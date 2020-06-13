from machine import Pin, SPI
from uasyncio import get_event_loop, sleep_ms, sleep
from max7219 import Matrix8x8
from gc import mem_free, collect
from NtpTime import NtpTime
from SmallClock import SmallClock
from LargeClock import LargeClock
import settings

class Gpio:
    CS = 15


class ClockManager:
    brightness = 0

    def __init__(self, wifiManager, mqttManager, webServer):
        self.wifiManager = wifiManager
        self.mqttManager = mqttManager
        self.webServer = webServer

        self.spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
        self.board = Matrix8x8(self.spi, Pin(Gpio.CS), 4)
        self.board.brightness(self.brightness)
        self.board.fill(0)
        self.board.show()

        self.time = NtpTime(self.wifiManager)

        self.smallClock = SmallClock(self.board, self.time)
        self.smallClock.start()

        self.largeClock = None

        self.loop = get_event_loop()
        # self.loop.create_task(self._checkMqtt())
        self.loop.create_task(self._pollWebServer())
        # self.loop.create_task(self._sendState())
        # self.loop.create_task(self._checkState())

    async def _checkMqtt(self):
        while True:
            while self.mqttManager.isConnected():
                collect()
                self._checkForMqttMessage()
                await sleep_ms(500)

            while not self.mqttManager.isConnected():
                await sleep(1)

            self._sendMqttState()

    async def _pollWebServer(self):
        while True:
            try:
                (emptyRequest, client, path, queryStringsArray) = self.webServer.poll()

                if not emptyRequest:
                    if path == "/" or path == "/index.html":
                        self._index(client)
                    elif path == "/action/clock/small":
                        self.loop.create_task(self._setClock(client, "SMALL"))
                    elif path == "/action/clock/large":
                        self.loop.create_task(self._setClock(client, "LARGE"))
                    elif path == "/action/brightness/more":
                        self._setBrightness(client, 1)
                    elif path == "/action/brightness/less":
                        self._setBrightness(client, -1)
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

    def _checkForMqttMessage(self):
        try:
            message = self.mqttManager.checkMessage()

            if not message == None:
                pass
        except Exception as e:
            print("> ClockManager._checkForMqttMessage exception: {}".format(e))

    async def _sendState(self):
        while True:
            self._sendMqttState()

            await sleep(30)

    def _sendMqttState(self):
        try:
            group = settings.readGroup()

            state = "{" + '"group": "{}", "state": "{}"'.format(group, "TO DO") + "}"

            self.mqttManager.publishState(state)
        except Exception as e:
            print("> ClockManager._sendMqttState exception: {}".format(e))

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

    async def _setClock(self, client, type):
        if type == "SMALL":
            if self.largeClock != None:
                self.largeClock.stop()
                self.largeClock = None

            self.board.fill(0)
            self.board.show()
            await sleep_ms(250)
            
            if self.smallClock == None:
                collect()
                self.smallClock = SmallClock(self.board, self.time)
                self.smallClock.start()
        else:
            if self.smallClock != None:
                self.smallClock.stop()
                self.smallClock = None

            self.board.fill(0)
            self.board.show()
            await sleep_ms(250)

            if self.largeClock == None:
                collect()
                self.largeClock = LargeClock(self.board, self.time)
                self.largeClock.start()

        self.webServer.ok(client)

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

    async def _checkState(self):
        while True:
            # if self.task == None:
            #     self.board.fill(0)
            #     self.board.show()

            # if self.state == SignState.SHOW:
            #     if self.task == None:
            #         self.task = self._stateShow()
            #         self.loop.create_task(self.task)
            # elif self.state == SignState.HOTEL:
            #     if self.task == None:
            #         self.task = self._stateHotel()
            #         self.loop.create_task(self.task)
            # elif self.state == SignState.ON:
            #     if self.task == None:
            #         self.task = self._stateOnOff(1)
            #         self.loop.create_task(self.task)
            # elif self.state == SignState.OFF:
            #     if self.task == None:
            #         self.task = self._stateOnOff(0)
            #         self.loop.create_task(self.task)

            await sleep_ms(500)

