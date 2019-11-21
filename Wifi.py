import network
import settings


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)

    def __init__(self):
        self.station.active(True)

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if not self.station.ifconfig()[0] == "0.0.0.0":
            ip = self.station.ifconfig()[0]

        return ip

    def checkWifi(self):
        if self.station.ifconfig()[0] == "0.0.0.0":
            if self.ap.ifconfig()[0] == "0.0.0.0":
                self.__startAp()
        else:
            if not self.ap.ifconfig()[0] == "0.0.0.0":
                self.__stopAp()

    def __startAp(self):
        self.ap.active(True)
        netId = settings.readNetId()
        essid = "Shade-" + str(netId)

        print("> No AP found... starting own AP: " + essid)

        self.ap.config(essid=essid, authmode=network.AUTH_OPEN)

    def __stopAp(self):
        print("> AP available, shutting down own AP")
        self.ap.active(False)

    def connect(self, essid, pwd):
        print("> Trying to connect to " + essid)
        self.station.connect(essid, pwd)
