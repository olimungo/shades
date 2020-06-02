from machine import Pin, SPI
import max7219
from effects import EffectsLibrary
import uasyncio as asyncio
import math
import random
import settings
from ledsConfig import leds

class Gpio:
    CS = 15


class SignState:
    SHOW = 0
    HOTEL = 1
    ON = 2
    OFF = 3


class SignManager:
    def __init__(self, wifiManager, mDns, mqttManager, webServer):
        self.wifiManager = wifiManager
        self.mDns = mDns
        self.mqttManager = mqttManager

        self.state = SignState.SHOW
        self.task = None

        self.spi = SPI(1, baudrate=10000000)
        self.board = max7219.Matrix8x8(self.spi, Pin(Gpio.CS), 1)
        self.effectsLibrary = EffectsLibrary(self.board)

        self.webServer = webServer

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._checkMqtt())
        self.loop.create_task(self._pollWebServer())
        self.loop.create_task(self._sendState())
        self.loop.create_task(self._checkState())

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
                    self.wifiManager.webActivtityInProgress()
                    
                    if path == "/" or path == "/index.html":
                        self._index(client)
                    elif path == "/action/previous":
                        self._previous(client)
                    elif path == "/action/next":
                        self._next(client)
                    elif path == "/settings/set-net":
                        self._setNet(client, queryStringsArray)
                    elif path == "/settings/group":
                        self._group(client, queryStringsArray)
                    elif path == "/settings/connect":
                        self._connect(client, queryStringsArray)
                    elif path == "/favicon.ico":
                        self.webServer.ok(client)
                    else:
                        # Probably a request from Android or IOS for the Custom Portal.
                        # Return a redirect to the index.
                        self.webServer.redirectToIndex(client)
            except Exception as e:
                print("> SignManager._pollWebServer exception: {}".format(e))

            await asyncio.sleep_ms(500)

    def _checkForMqttMessage(self):
        try:
            message = self.mqttManager.checkMessage()

            if not message == None:
                if message == "previous":
                    self.state -= 1

                    if self.state < SignState.SHOW:
                        self.state = SignState.OFF
                elif message == "next":
                    self.state += 1

                    if self.state > SignState.OFF:
                        self.state = SignState.SHOW
        except Exception as e:
            print("> SignManager._checkForMqttMessage exception: {}".format(e))

    async def _sendState(self):
        while True:
            self._sendMqttState()

            await asyncio.sleep(30)

    def _sendMqttState(self):
        try:
            group = settings.readGroup()

            state = "{" + '"group": "{}", "state": "{}"'.format(group, self.state) + "}"

            self.mqttManager.publishState(state)
        except Exception as e:
            print("> SignManager._sendMqttState exception: {}".format(e))

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

    def _previous(self, client):
        self.state -= 1

        if self.state < SignState.SHOW:
            self.state = SignState.OFF

        self.webServer.ok(client)
        self._sendMqttState()

        if self.task != None:
            asyncio.cancel(self.task)
            self.task = None

    def _next(self, client):
        self.state += 1

        if self.state > SignState.OFF:
            self.state = SignState.SHOW

        self.webServer.ok(client)
        self._sendMqttState()

        if self.task != None:
            asyncio.cancel(self.task)
            self.task = None

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

    async def _stateHotel(self):
        self.board.fill(1)
        self.board.brightness(3)
        self.board.show()

        while True:
            led = math.floor(random.getrandbits(5) / 32 * 20)
            duration = math.floor(random.getrandbits(4) / 16 * 5) + 1

            await self.effectsLibrary.blink(leds[led])
            await asyncio.sleep(duration)


    async def _stateShow(self):
        while True:
            self.board.brightness(2)

            await self.effectsLibrary.oneByone()
            await asyncio.sleep_ms(500)

            await self.effectsLibrary.inSerie()
            await asyncio.sleep_ms(500)

            await self.effectsLibrary.byAngle()
            await asyncio.sleep_ms(500)

            await self.effectsLibrary.byLetter()
            await asyncio.sleep_ms(500)

            await self.effectsLibrary.glow(3)
            await asyncio.sleep_ms(500)

            self.board.brightness(3)

            await self.effectsLibrary.strobe()
            await asyncio.sleep_ms(500)


    async def _stateOnOff(self, state):
        self.board.fill(state)
        self.board.show()

        while True:
            await asyncio.sleep_ms(10)


    async def _checkState(self):
        while True:
            if self.task == None:
                self.board.fill(0)
                self.board.show()

            if self.state == SignState.SHOW:
                if self.task == None:
                    self.task = self._stateShow()
                    self.loop.create_task(self.task)
            elif self.state == SignState.HOTEL:
                if self.task == None:
                    self.task = self._stateHotel()
                    self.loop.create_task(self.task)
            elif self.state == SignState.ON:
                if self.task == None:
                    self.task = self._stateOnOff(1)
                    self.loop.create_task(self.task)
            elif self.state == SignState.OFF:
                if self.task == None:
                    self.task = self._stateOnOff(0)
                    self.loop.create_task(self.task)

            await asyncio.sleep_ms(200)

            # await asyncio.sleep(1)

