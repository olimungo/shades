from uselect import poll, POLLIN, POLLHUP
from usocket import socket, getaddrinfo, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from uasyncio import get_event_loop, sleep_ms
from gc import collect

from WifiManager import AP_IP

MAX_PACKET_SIZE = const(768)
UDPS_PORT = const(53)
IDLE_TIME_BETWEEN_CHECKS = const(30)

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ""

        m = data[2]
        tipo = (m >> 3) & 15

        if tipo == 0:
            ini = 12
            lon = data[ini]

            while lon != 0:
                self.domain += data[ini + 1 : ini + lon + 1].decode("utf-8") + "."
                ini += lon + 1
                lon = data[ini]

    def response(self, ip):
        packet = b""

        if self.domain:
            packet += self.data[:2] + b"\x81\x80"
            packet += self.data[4:6] + self.data[4:6] + b"\x00\x00\x00\x00"
            packet += self.data[12:]
            packet += b"\xc0\x0c"
            packet += b"\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"
            packet += bytes(map(int, ip.split(".")))

        return packet

class UdpServer:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        addr = getaddrinfo("0.0.0.0", UDPS_PORT)[0][-1]
        self.sock.bind(addr)
        # self.sock.bind(("", UDPS_PORT))

        self.poller = poll()
        self.poller.register(self.sock, POLLIN)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_requests())

    async def check_requests(self):
        while True:
            # try:
            #     request = self.poller.poll(1)


            #     if request:
            #         obj, event = request

            #         print("obj: {} | event: {}".format(obj, event))

            #         # if event != POLLHUP:
            #         data, address = self.sock.recvfrom(MAX_PACKET_SIZE)

            #         request = DNSQuery(data)

            #         print("> DNS reply: {:s} -> {:s}".format(request.domain, AP_IP))

            #         self.sock.sendto(request.response(AP_IP), address)

            #         del data
            #         collect()
            # except Exception as e:
            #     pass
            #     # print("> ERROR in UdpServer.check_requests: {}".format(e))

            await sleep_ms(IDLE_TIME_BETWEEN_CHECKS)