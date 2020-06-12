from machine import Pin, SPI
import uasyncio as asyncio
import max7219
from NtpTime import NtpTime
from SmallClock import SmallClock
import settings

class Gpio:
    CS = 15


class ClockManager:
    def __init__(self, wifiManager, mqttManager, webServer):
        self.wifiManager = wifiManager
        self.mqttManager = mqttManager
        self.webServer = webServer

        self.spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
        self.board = max7219.Matrix8x8(self.spi, Pin(Gpio.CS), 4)
        self.board.brightness(0)
        self.board.fill(0)
        self.board.show()

        self.time = NtpTime(self.wifiManager)
        self.smallClock = SmallClock(self.board, self.time)
        self.smallClock.start()

        self.loop = asyncio.get_event_loop()
        # self.loop.create_task(self._checkMqtt())
        self.loop.create_task(self._pollWebServer())
        # self.loop.create_task(self._sendState())
        # self.loop.create_task(self._checkState())

    async def _checkMqtt(self):
        while True:
            while self.mqttManager.isConnected():
                self._checkForMqttMessage()
                await asyncio.sleep_ms(500)

            while not self.mqttManager.isConnected():
                await asyncio.sleep(1)

            self._sendMqttState()

    async def _pollWebServer(self):
        while True:
            try:
                (emptyRequest, client, path, queryStringsArray) = self.webServer.poll()

                if not emptyRequest:
                    if path == "/" or path == "/index.html":
                        self._index(client)
                    elif path == "/action/xxx":
                        self._xxx(client)
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

            await asyncio.sleep_ms(250)

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

            await asyncio.sleep(30)

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

    def _xxx(self, client):
        self.webServer.ok(client)
        self._sendMqttState()


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

            await asyncio.sleep_ms(200)

