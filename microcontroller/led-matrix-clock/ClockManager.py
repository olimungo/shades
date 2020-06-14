from machine import Pin, SPI
from uasyncio import get_event_loop, sleep_ms, sleep
from max7219 import Matrix8x8
from gc import mem_free, collect
from NtpTime import NtpTime
from SmallClock import SmallClock
import settings

class Gpio:
    CS = 15


class ClockManager:
    brightness = 0

    def __init__(self, wifiManager, webServer):
        self.wifiManager = wifiManager
        self.webServer = webServer

        self.spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
        self.board = Matrix8x8(self.spi, Pin(Gpio.CS), 4)
        self.board.brightness(self.brightness)
        self.board.fill(0)
        self.board.show()

        self.time = NtpTime(self.wifiManager)
        self.smallClock = SmallClock(self.board, self.time)
        self.smallClock.start()

        self.loop = get_event_loop()
        self.loop.create_task(self._pollWebServer())

    async def _pollWebServer(self):
        while True:
            try:
                (emptyRequest, client, path, queryStringsArray) = self.webServer.poll()

                if not emptyRequest:
                    if path == "/" or path == "/index.html":
                        self._index(client)
                    elif path == "/action/brightness/more":
                        self._setBrightness(client, 1)
                    elif path == "/action/brightness/less":
                        self._setBrightness(client, -1)
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
        netId, essid, group = settings.readSettings()

        interpolate = {
            "IP": ip,
            "NET_ID": netId,
            "ESSID": essid,
            "GROUP": group
        }

        self.webServer.index(client, interpolate)

    def _setBrightness(self, client, increment):
        if self.brightness + increment > 0 and self.brightness + increment < 10:
            self.brightness += increment
            self.board.brightness(self.brightness)

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

