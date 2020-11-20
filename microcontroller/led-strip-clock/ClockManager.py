from uasyncio import get_event_loop, sleep_ms, sleep
from gc import mem_free, collect
from NtpTime import NtpTime
from clock import Clock
import settings

class Player:
    GREEN = 0
    RED = 1

class Mode:
    CLOCK = 0
    SCOREBOARD = 1

class ClockManager:
    brightness = 0
    mode = Mode.CLOCK

    def __init__(self, wifiManager, webServer):
        color = settings.readColor()

        self.wifiManager = wifiManager
        self.webServer = webServer
        self.time = NtpTime(self.wifiManager)
        self.clock = Clock(self.time, color)
        self.clock.playEffectInit(120)

        self.loop = get_event_loop()
        self.loop.create_task(self._pollWebServer())
        self.loop.create_task(self._waitForStation())

    async def _waitForStation(self):
        await sleep(5)

        while not self.wifiManager.isConnectedToStation():
            await sleep(2)

        await sleep(2)

        self.clock.stopEffectInit = True

        await sleep_ms(70)

        self.clock.clearAll()

        await sleep_ms(200)

        self.clock.startClock()

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
                    elif path == "/action/color":
                        self._setColor(client, queryStringsArray)
                    elif path == "/action/scoreboard/green/more":
                        self._scoreboardUpdate(client, Player.GREEN, 1)
                    elif path == "/action/scoreboard/green/less":
                        self._scoreboardUpdate(client, Player.GREEN, -1)
                    elif path == "/action/scoreboard/red/more":
                        self._scoreboardUpdate(client, Player.RED, 1)
                    elif path == "/action/scoreboard/red/less":
                        self._scoreboardUpdate(client, Player.RED, -1)
                    elif path == "/action/scoreboard/reset":
                        self._scoreboardReset(client)
                    elif path == "/action/clock/show":
                        self._showClock(client)
                    elif path == "/action/scoreboard/show":
                        self._displayScoreboard(client)
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

            await sleep_ms(50)

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

    def _setBrightness(self, client, increment):
        self._showClock()

        if increment > 0:
            self.clock.setBrighter()
        else:
            self.clock.setDarker()

        self.webServer.ok(client)

    def _setColor(self, client, queryStringsArray):
        self._showClock()

        if "hex" in queryStringsArray and not queryStringsArray["hex"] == "":
            color = queryStringsArray["hex"]
            self.clock.setColor(color)

            # Comment the following line in order to NOT record the selected color for the next boot
            settings.writeColor(color)

        self.webServer.ok(client)
    
    def _displayScoreboard(self, client):
        if self.mode == Mode.CLOCK:
            self.clock.stopClock()
            self.mode = Mode.SCOREBOARD
            self.clock.displayScoreboard()

        self.webServer.ok(client)

    def _scoreboardUpdate(self, client, player, increment):
        self._displayScoreboard(client)

        if player == Player.GREEN:
            self.clock.updateScoreboardGreen(increment)
        else:
            self.clock.updateScoreboardRed(increment)

    def _scoreboardReset(self, client):
        self._displayScoreboard(client)
        self.clock.resetScoreboard()

    def _showClock(self, client=None):
        if self.mode == Mode.SCOREBOARD:
            self.mode = Mode.CLOCK
            self.clock.startClock()

        if client != None:
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

