from time import ticks_ms, ticks_diff
from select import select
from ustruct import pack_into, unpack_from
from usocket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, IPPROTO_IP, IP_ADD_MEMBERSHIP
from uasyncio import get_event_loop, sleep_ms, sleep
from gc import collect

_MAX_PACKET_SIZE = const(512)
_MAX_NAME_SEARCH = const(20)

_MDNS_ADDR = "224.0.0.251"
_MDNS_PORT = const(5353)
_DNS_TTL = const(2 * 60)  # two minute default TTL

_FLAGS_QR_MASK = const(0x8000)  # query response mask
_FLAGS_QR_QUERY = const(0x0000)  # query
_FLAGS_QR_RESPONSE = const(0x8000)  # response

_FLAGS_AA = const(0x0400)  # Authorative answer

_CLASS_IN = const(1)
_CLASS_ANY = const(255)
_CLASS_MASK = const(0x7FFF)
_CLASS_UNIQUE = const(0x8000)

_TYPE_A = const(1)
_TYPE_PTR = const(12)
_TYPE_TXT = const(16)
_TYPE_AAAA = const(28)
_TYPE_SRV = const(33)
_TYPE_ANY = const(255)

_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS = const(5)
_IDLE_TIME_BETWEEN_PACKETS_CHEKS = const(500)

# Convert a dotted IPv4 address string into four bytes, with some
# sanity checks
def dotted_ip_to_bytes(ip):
    l = [int(i) for i in ip.split(".")]
    if len(l) != 4 or any(i < 0 or i > 255 for i in l):
        raise ValueError
    return bytes(l)


# Convert four bytes into a dotted IPv4 address string, without any
# sanity checks
def bytes_to_dotted_ip(a):
    return ".".join(str(i) for i in a)


# Ensure that a name is in the form of a list of encoded blocks of
# bytes, typically starting as a qualified domain name
def check_name(n):
    if isinstance(n, str):
        n = n.split(".")
        if n[-1] == "":
            n = n[:-1]
    n = [i.encode("UTF8") if isinstance(i, str) else i for i in n]
    return n


# Move the offset past the name to which it currently points
def skip_name_at(buf, o):
    while True:
        l = buf[o]
        if l == 0:
            o += 1
            break
        elif (l & 0xC0) == 0xC0:
            o += 2
            break
        else:
            o += l + 1
    return o


# Test if two possibly compressed names are equal
def compare_packed_names(buf, o, packed_name, po=0):
    while packed_name[po] != 0:
        while buf[o] & 0xC0:
            (o,) = unpack_from("!H", buf, o)
            o &= 0x3FFF
        while packed_name[po] & 0xC0:
            (po,) = unpack_from("!H", packed_name, po)
            po &= 0x3FFF
        l1 = buf[o] + 1
        l2 = packed_name[po] + 1
        if l1 != l2 or buf[o : o + l1] != packed_name[po : po + l2]:
            return False
        o += l1
        po += l2
    return buf[o] == 0


# Find the memory size needed to pack a name without compression
def name_packed_len(name):
    return sum(len(i) + 1 for i in name) + 1


# Pack a name into the start of the buffer
def pack_name(buf, name):
    # We don't support writing with name compression, BIWIOMS
    o = 0
    for part in name:
        pl = len(part)
        buf[o] = pl
        buf[o + 1 : o + pl + 1] = part
        o += pl + 1
    buf[o] = 0


# Pack a question into a new array and return it as a memoryview
def pack_question(name, qtype, qclass):
    # Return a pre-packed question as a memoryview
    name = check_name(name)
    name_len = name_packed_len(name)
    buf = bytearray(name_len + 4)
    pack_name(buf, name)
    pack_into("!HH", buf, name_len, qtype, qclass)
    return memoryview(buf)


# Pack an answer into a new array and return it as a memoryview
def pack_answer(name, rtype, rclass, ttl, rdata):
    # Return a pre-packed answer as a memoryview
    name = check_name(name)
    name_len = name_packed_len(name)
    buf = bytearray(name_len + 10 + len(rdata))
    pack_name(buf, name)
    pack_into("!HHIH", buf, name_len, rtype, rclass, ttl, len(rdata))
    buf[name_len + 10 :] = rdata
    return memoryview(buf)


# Advance the offset past the question to which it points
def skip_question(buf, o):
    o = skip_name_at(buf, o)
    return o + 4


# Advance the offset past the answer to which it points
def skip_answer(buf, o):
    o = skip_name_at(buf, o)
    (rdlen,) = unpack_from("!H", buf, o + 8)
    return o + 10 + rdlen


# Test if a questing an answer. Note that this also works for
# comparing a "known answer" in a packet to a local answer. The code
# is asymetric to the extent that the questions my have a type or
# class of ANY
def compare_q_and_a(q_buf, q_offset, a_buf, a_offset=0):
    if not compare_packed_names(q_buf, q_offset, a_buf, a_offset):
        return False
    (q_type, q_class) = unpack_from("!HH", q_buf, skip_name_at(q_buf, q_offset))
    (r_type, r_class) = unpack_from("!HH", a_buf, skip_name_at(a_buf, a_offset))
    if not (q_type == r_type or q_type == _TYPE_ANY):
        return False
    q_class &= _CLASS_MASK
    r_class &= _CLASS_MASK
    return q_class == r_class or q_class == _TYPE_ANY


class mDnsServer:
    loop = get_event_loop()
    connected = False

    def __init__(self, wifiManager, hostname, netId):
        self.wifiManager = wifiManager
        self.hostname = hostname
        self.setNetId(netId)

        self.loop.create_task(self._checkMdns())

    async def _checkMdns(self):
        while True:
            while not self.wifiManager.isConnectedToStation():
                await sleep(_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS)

            self._connect()

            if self.wifiManager.isConnectedToStation() and self.connected:
                print("> mDNS server up and running")

            while self.wifiManager.isConnectedToStation() and self.connected:
                self._process_waiting_packets()
                await sleep_ms(_IDLE_TIME_BETWEEN_PACKETS_CHEKS)

            print("> mDNS server down")

            self.connected = False

    def _connect(self):
        try:
            collect()

            self.sock = self._make_socket()
            self.connected = True
        except Exception as e:
            print("> mDnsServer._connect error: {}".format(e))

    def _make_socket(self):
        self.local_addr = self.wifiManager.getIp()

        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        member_info = dotted_ip_to_bytes(_MDNS_ADDR) + dotted_ip_to_bytes(
            self.local_addr
        )

        s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, member_info)

        s.bind(("", _MDNS_PORT))

        self.adverts = []
        self._reply_buffer = None
        self._pending_question = None
        self.answered = False
        self._advertise_hostname()

        return s

    def _advertise_hostname(self, find_vacant=True):
        hostname = check_name(self.publicName)
        n = len(hostname)

        if n == 1:
            hostname.append(b"local")
        elif n == 0 or n > 2 or hostname[1] != b"local":
            raise ValueError("hostname should be a single name component")

        ip_bytes = dotted_ip_to_bytes(self.local_addr)

        basename = hostname[0]

        for i in range(_MAX_NAME_SEARCH):
            if i != 0:
                hostname[0] = basename + b"-" + str(i)

            addr = self.resolve_mdns_address(hostname, True)

            if not addr or addr == ip_bytes:
                break

            if not find_vacant or i == _MAX_NAME_SEARCH - 1:
                raise ValueError("Name in use")

        A_record = pack_answer(hostname, _TYPE_A, _CLASS_IN, _DNS_TTL, ip_bytes)

        self.adverts.append(A_record)

        mdns = []
        for idx, key in enumerate(hostname):
            mdns.append(key.decode('utf-8'))
        
        print("> mDNS hostname: {}".format('.'.join(mdns)))

    def _process_packet(self, buf, addr):
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

        pack_into(
            "!HHHHHH",
            buf,
            0,
            pkt_id,
            _FLAGS_QR_RESPONSE | _FLAGS_AA,
            0,
            len(matches),
            0,
            0,
        )

        o = 12

        for a in matches:
            l = len(a)
            buf[o : o + l] = a
            o += l

        self.sock.sendto(
            buf[:o], (_MDNS_ADDR, _MDNS_PORT) if addr[0] == _MDNS_PORT else addr
        )

    def _process_waiting_packets(self):
        while True:
            try:
                readers, _, _ = select([self.sock], [], [], 0)
            except Exception as e:
                print("> mDnsServer._process_waiting_packets error: {}".format(e))

            if not readers:
                break

            collect()

            buf, addr = self.sock.recvfrom(_MAX_PACKET_SIZE)

            if buf and addr[0] != self.local_addr:
                try:
                    self._process_packet(memoryview(buf), addr)

                    del buf
                    collect()
                except IndexError:
                    print("Index error processing packet; probably malformed data")
                except Exception as e:
                    print("Error processing packet: {}".format(e))

    def _handle_question(self, q, answer_callback, fast=False, retry_count=3):
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

                self.sock.sendto(p, (_MDNS_ADDR, _MDNS_PORT))
                timeout = ticks_ms() + (250 if fast else 1000)

                while not self.answered:
                    sel_time = ticks_diff(timeout, ticks_ms())

                    if sel_time <= 0:
                        break

                    (rr, _, _) = select([self.sock], [], [], sel_time / 1000.0)

                    if rr:
                        self._process_waiting_packets()
        finally:
            self._pending_question = None
            self._answer_callback = None

    def resolve_mdns_address(self, hostname, fast=False):
        if self.connected:
            q = pack_question(hostname, _TYPE_A, _CLASS_IN)
            answer = []

            def _answer_handler(a):
                addr_offset = skip_name_at(a, 0) + 10
                answer.append(a[addr_offset : addr_offset + 4])

                return True

            self._handle_question(q, _answer_handler, fast)

            return bytes(answer[0]) if answer else None

    def isConnected(self):
        return self.connected

    def getIp(self):
        return self.wifiManager.getIp()

    def setNetId(self, netId):
        self.netId = netId
        self.publicName = "{}-{}".format(self.hostname, self.netId)

        if (self.connected):
            self._connect()
