from uasyncio import get_event_loop, sleep_ms, sleep
from gc import mem_free, collect
from NtpTime import NtpTime
from clock import Clock
import settings



class ClockManager:
    brightness = 0

    def __init__(self, wifiManager, webServer):
        color = settings.readColor()

        self.wifiManager = wifiManager
        self.webServer = webServer

        self.time = NtpTime(self.wifiManager)
        self.clock = Clock(self.time, color)
        self.clock.start()

        self.loop = get_event_loop()
        self.loop.create_task(self._pollWebServer())

    async def _pollWebServer(self):
        while True:
            try:
                (emptyRequest, client, path, queryStringsArray) = self.webServer.poll()

                if not emptyRequest:
                    print("req: " + path)

                    if path == "/" or path == "/index.html":
                        self._index(client)
                    elif path == "/action/brightness/more":
                        self._setBrightness(client, 1)
                    elif path == "/action/brightness/less":
                        self._setBrightness(client, -1)
                    elif path == "/action/color":
                        self._setColor(client, queryStringsArray)
                    elif path == "/settings/set-net":
                        self._setNet(client, queryStringsArray)
                    elif path == "/settings/connect":
                        self._connect(client, queryStringsArray)
                    elif path == "/favicon.ico":
                        self.webServer.ok(client)
                    else:
                        # Probably a request from Android or IOS for the Custom Portal.
                        # Return a redirect to the index.
                        self.webServer.redirectToIndex(client)
            except Exception as e:
                print("> ClockManager._pollWebServer exception: {}".format(e))

            await sleep_ms(250)

    def _index(self, client):
        ip = self.wifiManager.getIp()
        _settings = settings.readSettings()

        interpolate = {
            "IP": ip,
            "NET_ID": _settings["netId"],
            "ESSID": _settings["essid"],
            "GROUP": _settings["group"]
        }



        self.webServer.index(client, interpolate)

        print("xxxx")

    def _setBrightness(self, client, increment):
        if increment > 0:
            self.clock.setBrighter()
        else:
            self.clock.setDarker()

        self.webServer.ok(client)

    def _setColor(self, client, queryStringsArray):
        if "hex" in queryStringsArray and not queryStringsArray["hex"] == "":
            color = queryStringsArray["hex"]
            self.clock.setColor(color)
            settings.writeColor(color)

        self.webServer.ok(client)

    def _setNet(self, client, queryStringsArray):
        if "id" in queryStringsArray and not queryStringsArray["id"] == "":
            settings.writeNetId(queryStringsArray["id"])

        self.webServer.ok(client)

    def _group(self, client, queryStringsArray):
        if "name" in queryStringsArray:
            settings.writeGroup(queryStringsArray["name"])

        self.webServer.ok(client)

    def _connect(self, client, queryStringsArray):
        if "essid" in queryStringsArray and "pwd" in queryStringsArray:
            essid = queryStringsArray["essid"]
            password = queryStringsArray["pwd"]

            if not essid == "" and not password == "":
                settings.writeEssid(essid)

                self.wifiManager.connect(essid, password)

        self.webServer.ok(client)

