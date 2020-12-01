from time import ticks_ms, ticks_diff
from uselect import select
from ustruct import pack_into, unpack_from
from usocket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, IPPROTO_IP, IP_ADD_MEMBERSHIP
from uasyncio import get_event_loop, sleep_ms
from network import WLAN, STA_IF
from gc import collect

from mDnsServerHelpers import dotted_ip_to_bytes, check_name, pack_answer, compare_q_and_a, skip_question, skip_answer, pack_question, skip_name_at

MAX_PACKET_SIZE = const(512)
MAX_NAME_SEARCH = const(20)
MDNS_ADDR = b"224.0.0.251"
MDNS_PORT = const(5353)
DNS_TTL = const(2 * 60)
FLAGS_QR_RESPONSE = const(0x8000) 
FLAGS_AA = const(0x0400)
CLASS_IN = const(1)
TYPE_A = const(1)

WAIT_FOR_CONNECT = const(1000)
WAIT_MORE_FOR_CONNECT = const(8000)
WAIT_FOR_REQUEST = const(500)

class mDnsServer:
    def __init__(self, hostname, net_id):
        self.sta_if = WLAN(STA_IF)
        self.hostname = hostname
        self.connected = False

        self.set_net_id(net_id)

        self.sock = self.make_socket()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_request())

    async def check_request(self):
        while True:
            self.connected = False

            while not self.sta_if.isconnected():
                await sleep_ms(WAIT_FOR_CONNECT)
            
            # Wait a bit more so other services have the time to start up
            await sleep_ms(WAIT_MORE_FOR_CONNECT)

            self.connect()
            
            self.connected = True

            print("> mDNS server up and running")

            while self.sta_if.isconnected():
                self.process_waiting_packets()
                await sleep_ms(WAIT_FOR_REQUEST)

            print("> mDNS server down")

    def connect(self):
        try:
            print("> mDNS start or restart")
            self.make_socket()
            self.advertise_hostname()
        except Exception as e:
            print("> mDnsServer.connect error: {}".format(e))

    def make_socket(self):
        collect()

        self.ip = self.sta_if.ifconfig()[0]

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        member_info = dotted_ip_to_bytes(MDNS_ADDR.decode('ascii')) + dotted_ip_to_bytes(self.ip)

        self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, member_info)
        self.sock.bind(("", MDNS_PORT))

        self.adverts = []
        self._reply_buffer = None
        self._pending_question = None
        self.answered = False

    def advertise_hostname(self, find_vacant=True):
        collect()

        hostname = check_name(self.public_name.decode('ascii'))
        n = len(hostname)

        if n == 1:
            hostname.append(b"local")
        elif n == 0 or n > 2 or hostname[1] != b"local":
            raise ValueError("> Hostname should be a single name component")

        ip_bytes = dotted_ip_to_bytes(self.ip)

        basename = hostname[0]

        for i in range(MAX_NAME_SEARCH):
            if i != 0:
                hostname[0] = basename + b"-" + str(i)

            addr = self.resolve_mdns_address(hostname, True)

            if not addr or addr == ip_bytes:
                break

            if not find_vacant or i == MAX_NAME_SEARCH - 1:
                raise ValueError("Name in use")

        A_record = pack_answer(hostname, TYPE_A, CLASS_IN, DNS_TTL, ip_bytes)
        
        self.adverts.append(A_record)

        mdns = []
        for _, key in enumerate(hostname):
            mdns.append(key.decode('utf-8'))
        
        print("> mDNS hostname: {}".format('.'.join(mdns)))

        collect()

    def process_packet(self, buf, addr):
        collect()

        (pkt_id, flags, qst_count, ans_count, _, _) = unpack_from("!HHHHHH", buf, 0)

        o = 12
        matches = []
        reply_len = 12

        for i in range(qst_count):
            for a in self.adverts:
                if compare_q_and_a(buf, o, a):
                    matches.append(a)
                    reply_len += len(a)
            o = skip_question(buf, o)

        if self._pending_question:
            for i in range(ans_count):
                if compare_q_and_a(self._pending_question, 0, buf, o):
                    if self._answer_callback(buf[o : skip_answer(buf, o)]):
                        self.answered = True
                o = skip_answer(buf, o)

        if not matches:
            return

        if not self._reply_buffer or len(self._reply_buffer) < reply_len:
            self._reply_buffer = memoryview(bytearray(reply_len))

        buf = self._reply_buffer

        pack_into("!HHHHHH", buf, 0, pkt_id, FLAGS_QR_RESPONSE | FLAGS_AA, 0, len(matches), 0, 0,)

        o = 12

        for a in matches:
            l = len(a)
            buf[o : o + l] = a
            o += l

        self.sock.sendto(buf[:o], (MDNS_ADDR, MDNS_PORT) if addr[0] == MDNS_PORT else addr)

    def process_waiting_packets(self):
        while True:
            try:
                readers, _, _ = select([self.sock], [], [], 0)
            except Exception as e:
                print("> mDnsServer.process_waiting_packets error: {}".format(e))

            if not readers:
                break

            buf, addr = self.sock.recvfrom(MAX_PACKET_SIZE)

            if buf and addr[0] != self.ip:
                try:
                    self.process_packet(memoryview(buf), addr)

                    del buf
                except IndexError as e:
                    print("> Index error processing packet; probably malformed data: {}".format(e))
                except Exception as e:
                    print("> Error processing packet: {}".format(e))

    def handle_question(self, q, answer_callback, fast=False, retry_count=3):
        collect()

        p = bytearray(len(q) + 12)
        pack_into("!HHHHHH", p, 0, 1, 0, 1, 0, 0, 0, 0)
        p[12:] = q

        self._pending_question = q
        self._answer_callback = answer_callback
        self.answered = False

        try:
            for i in range(retry_count):
                if self.answered:
                    break

                self.sock.sendto(p, (MDNS_ADDR, MDNS_PORT))
                timeout = ticks_ms() + (250 if fast else 1000)

                while not self.answered:
                    sel_time = ticks_diff(timeout, ticks_ms())

                    if sel_time <= 0:
                        break

                    (rr, _, _) = select([self.sock], [], [], sel_time / 1000.0)

                    if rr:
                        self.process_waiting_packets()
        finally:
            self._pending_question = None
            self._answer_callback = None

    def resolve_mdns_address(self, hostname, fast=False):
        collect()

        if self.sta_if.isconnected():
            q = pack_question(hostname, TYPE_A, CLASS_IN)
            answer = []
        
            def _answer_handler(a):
                addr_offset = skip_name_at(a, 0) + 10
                answer.append(a[addr_offset : addr_offset + 4])

                return True

            self.handle_question(q, _answer_handler, fast)

            return bytes(answer[0]) if answer else None

    def set_net_id(self, net_id):
        self.net_id = net_id
        self.public_name = b"%s-%s" % (self.hostname, self.net_id)

        if (self.sta_if.isconnected()):
            self.connect()
