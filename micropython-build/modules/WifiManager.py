from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep
from UdpsServer import UdpsServer
from Blink import Blink

_WAIT_FOR_FLASHING_LED = const(2)
_IDLE_TIME_BEFORE_CHECKING = const(6)
_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS = const(30)
_IDLE_TIME_BETWEEN_CONNECTED_CHECKS = const(5)


class WifiManager:
    station = WLAN(STA_IF)
    ap = WLAN(AP_IF)
    loop = get_event_loop()
    apStarted = False
    connectedToStation = False

    def __init__(self, essidAp):
        self.essidAp = essidAp
        self.station.active(True)
        self.ap.active(False)
        self.udpsServer = UdpsServer(self)

        self.loop.create_task(self._checkConnection())

    async def _checkConnection(self):
        # Leave some time to try to connect to the station
        await sleep(_IDLE_TIME_BEFORE_CHECKING)

        if not self.station.isconnected():
            self._startAp()

        while True:
            while not self.station.isconnected():
                await sleep(_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS)

            if self.apStarted:
                self._stopAp()

            Blink().flash3TimesFast()

            await sleep(_WAIT_FOR_FLASHING_LED)

            self.connectedToStation = True

            print("> IP: {}".format(self.getIp()))

            while self.station.isconnected():
                await sleep(_IDLE_TIME_BETWEEN_CONNECTED_CHECKS)

            self.connectedToStation = False

            self._startAp()

    def _startAp(self):
        print("> No AP found... starting own AP: {}".format(self.essidAp))

        self.ap.active(True)
        self.apStarted = True
        self.ap.config(essid=self.essidAp, authmode=AUTH_OPEN)

    def _stopAp(self):
        print("> AP available, shutting down own AP")

        self.apStarted = False
        self.ap.active(False)

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if self.station.isconnected():
            ip = self.station.ifconfig()[0]

        return ip

    def connect(self, essid, password):
        print("> Trying to connect to {}...".format(essid))
        self.station.connect(essid, password)

    def isConnectedToStation(self):
        return self.connectedToStation
