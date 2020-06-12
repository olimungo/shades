from select import select
from usocket import socket, AF_INET, SOCK_DGRAM
import uasyncio as asyncio
from gc import collect

_MAX_PACKET_SIZE = const(896)
_UDPS_PORT = const(53)
_IDLE_TIME_BETWEEN_CHECKS = const(500)

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


class UdpsServer:
    loop = asyncio.get_event_loop()
    connected = False

    def __init__(self, wifiManager):
        self.wifiManager = wifiManager

        self.udps = socket(AF_INET, SOCK_DGRAM)
        self.udps.setblocking(False)
        self.udps.bind(("", _UDPS_PORT))

        self.loop.create_task(self._checkUdps())

    async def _checkUdps(self):
        while True:
            try:
                readers, _, _ = select([self.udps], [], [], None)

                if readers:
                    collect()

                    data, address = self.udps.recvfrom(_MAX_PACKET_SIZE)
                    self.udps.sendto(DNSQuery(data).response(self.wifiManager.getIp()), address)
            except Exception as e:
                print("> UdpsServer._checkUdps error: {}".format(e))

            await asyncio.sleep_ms(_IDLE_TIME_BETWEEN_CHECKS)
