from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep
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

    def __init__(self, essidAp, netId):
        self.essidAp = essidAp
        
        self.setNetId(netId)
        self.station.active(True)
        self.ap.active(False)

        self.loop.create_task(self._checkConnection())

    async def _checkConnection(self):
        # Leave some time to try to connect to the station
        await sleep(_IDLE_TIME_BEFORE_CHECKING)

        if not self.station.isconnected():
            print("> No Access Point found...")
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

            print("> Connection to Access Point broken...")
            self._startAp()

    def _startAp(self):
        print("> Starting own Access Point: {}".format(self.publicName))

        self.ap.active(True)
        self.apStarted = True
        self.ap.config(essid=self.publicName, authmode=AUTH_OPEN)

    def _stopAp(self):
        print("> Shutting down own Access Point")

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

    def setNetId(self, netId):
        self.netId = netId
        self.publicName = "{}-{}".format(self.essidAp, self.netId)

