import network


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    isApStarted = False

    def __init__(self, essid):
        self.essid = essid
        self.station.active(True)
        self.ap.active(False)

    def _startAp(self):
        print("> No AP found... starting own AP: " + self.essid)
        self.isApStarted = True
        self.ap.active(True)
        self.ap.config(essid=self.essid, authmode=network.AUTH_OPEN)

    def _stopAp(self):
        print("> AP available, shutting down own AP")
        self.isApStarted = False
        self.ap.active(False)

    def checkConnection(self):
        if not self.station.isconnected():
            if not self.isApStarted:
                self._startAp()
        else:
            if self.isApStarted:
                self._stopAp()

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if self.station.isconnected():
            ip = self.station.ifconfig()[0]

        return ip

    def connect(self, essid, pwd):
        print("> Trying to connect to " + essid)
        self.station.connect(essid, pwd)
