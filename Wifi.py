import network
import settings
import Blink
from machine import Timer


class WifiManager:
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    stationIpAssigned = False
    blink = Blink.Blink()
    checkConnectivityTimer = Timer(-1)

    def __init__(self):
        self.station.active(True)
        self.checkConnectivityTimer.init(
            period=5000, mode=Timer.PERIODIC, callback=self._checkConnectivity
        )

    def _checkConnectivity(self, timer):
        if self.station.ifconfig()[0] == "0.0.0.0":
            if self.ap.ifconfig()[0] == "0.0.0.0":
                self.stationIpAssigned = False
                self.__startAp()
        else:
            if not self.stationIpAssigned:
                self.stationIpAssigned = True
                self.blink.fast()
                print(self.getIp())

            if not self.ap.ifconfig()[0] == "0.0.0.0":
                self.__stopAp()

    def getIp(self):
        ip = self.ap.ifconfig()[0]

        if not self.station.ifconfig()[0] == "0.0.0.0":
            ip = self.station.ifconfig()[0]

        return ip

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
