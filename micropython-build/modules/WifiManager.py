import network
import uasyncio as asyncio
from Blink import Blink

_WAIT_FOR_FLASHING_LED = const(2)
_IDLE_TIME_BEFORE_CHECKING = const(6)
_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS = const(30)
_IDLE_TIME_BETWEEN_CONNECTED_CHECKS = const(5)
_IDLE_TIME_BETWEEN_CONNECTION_CHECKS = const(10)
_IDLE_TIME_WHEN_DELAY_RECONNECTION = const(60)


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    loop = asyncio.get_event_loop()
    apStarted = False
    connectedToStation = False
    delayAttemptReconnection = False

    def __init__(self, essidAp):
        self.essidAp = essidAp
        self.station.active(True)
        self.ap.active(False)

        self.loop.create_task(self._checkConnection())

    async def _checkStation(self):
        while not self.station.isconnected():
            if self.delayAttemptReconnection:
                while self.delayAttemptReconnection:
                    # delayAttemptReconnection could be set to True while waiting
                    self.delayAttemptReconnection = False
                    await asyncio.sleep(_IDLE_TIME_WHEN_DELAY_RECONNECTION)
            else:
                await asyncio.sleep(_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS)

            self.station.connect()

            await asyncio.sleep(_IDLE_TIME_BETWEEN_CONNECTION_CHECKS)

            if not self.station.isconnected():
                self.station.disconnect()

    async def _checkConnection(self):
        # Leave some time to try to connect to the station
        await asyncio.sleep(_IDLE_TIME_BEFORE_CHECKING)

        if not self.station.isconnected():
            self._startAp()

        while True:
            while not self.station.isconnected():
                await asyncio.sleep(_IDLE_TIME_BETWEEN_NOT_CONNECTED_CHECKS)

            if self.apStarted:
                self._stopAp()

            Blink().flash3TimesFast()

            await asyncio.sleep(_WAIT_FOR_FLASHING_LED)

            self.connectedToStation = True

            print("> IP: {}".format(self.getIp()))

            while self.station.isconnected():
                await asyncio.sleep(_IDLE_TIME_BETWEEN_CONNECTED_CHECKS)

            self.connectedToStation = False

            self._startAp()

    def _startAp(self):
        print("> No AP found... starting own AP: {}".format(self.essidAp))

        self.station.disconnect()
        self.ap.active(True)
        self.apStarted = True
        self.ap.config(essid=self.essidAp, authmode=network.AUTH_OPEN)

        self.loop.create_task(self._checkStation())

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

    def webActivtityInProgress(self):
        self.delayAttemptReconnection = True
