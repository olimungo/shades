import network
from machine import Timer


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    stationReady = False

    waitForAutoConnectionTimer = Timer(-1)
    checkStationConnectionTimer = Timer(-1)

    def __init__(self, essid):
        self.essid = essid
        self.station.active(True)
        self.ap.active(False)

        self.waitForAutoConnectionTimer.init(
            period=5000, mode=Timer.ONE_SHOT, callback=self._waitForAutoConnection
        )

    def _waitForAutoConnection(self, timer):
        if not self.station.isconnected():
            self._startAp()

        self.checkStationConnectionTimer.init(
            period=1000, mode=Timer.PERIODIC, callback=self._checkStationConnection
        )

    def _checkStationConnection(self, timer):
        if not self.station.isconnected():
            if not self.ap.isconnected():
                self._startAp()
                self.stationReady = False
        else:
            if self.ap.isconnected():
                self._stopAp()

        self.checkStationConnectionTimer.init(
            period=5000, mode=Timer.PERIODIC, callback=self._checkStationConnection
        )

    def _startAp(self):
        print("> No AP found... starting own AP: " + self.essid)
        self.ap.active(True)
        self.ap.config(essid=self.essid, authmode=network.AUTH_OPEN)

    def _stopAp(self):
        print("> AP available, shutting down own AP")
        self.ap.active(False)

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if self.station.isconnected():
            ip = self.station.ifconfig()[0]

        return ip

    def connect(self, essid, pwd):
        print("> Trying to connect to " + essid)
        self.station.connect(essid, pwd)
