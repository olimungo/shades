import network
import uasyncio as asyncio
from Blink import Blink


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    isApStarted = False
    justConnectedToStation = False

    def __init__(self, loop, essidAp):
        self.loop = loop
        self.essidAp = essidAp
        self.station.active(True)
        self.ap.active(False)

        self.loop.create_task(self._waitForStation())

    def _startAp(self):
        print("> No AP found... starting own AP: {}".format(self.essidAp))
        self.isApStarted = True
        self.ap.active(True)
        self.ap.config(essid=self.essidAp, authmode=network.AUTH_OPEN)

    def _stopAp(self):
        print("> AP available, shutting down own AP")
        self.isApStarted = False
        self.ap.active(False)

    async def _waitForStation(self):
        await asyncio.sleep(4)
        self.loop.create_task(self._checkConnection())

    async def _checkConnection(self):
        while True:
            if not self.station.isconnected():
                if not self.isApStarted:
                    self.justConnectedToStation = False
                    self._startAp()
            else:
                if not self.justConnectedToStation:
                    self.justConnectedToStation = True
                    Blink(self.loop).flash3TimesFast()

                if self.isApStarted:
                    self._stopAp()

            await asyncio.sleep(2)

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if self.station.isconnected():
            ip = self.station.ifconfig()[0]

        return ip

    def connect(self, essid, pwd):
        print("> Trying to connect to {}".format(essid))
        self.station.connect(essid, pwd)

    def isConnectedToStation(self):
        return self.station.isconnected()
