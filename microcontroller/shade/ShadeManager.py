import uasyncio as asyncio
from MotorManager import MotorManager
import settings


class ShadeManager:
    def __init__(self, wifiManager, mDnsServer, mqttManager, webServer):
        self.wifiManager = wifiManager
        self.mDnsServer = mDnsServer
        self.mqttManager = mqttManager

        self.webServer = webServer
        self.motorManager = MotorManager()

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._checkMqtt())
        self.loop.create_task(self._pollWebServer())
        self.loop.create_task(self._sendState())

    async def _checkMqtt(self):
        while True:
            while self.mqttManager.isConnected():
                self._checkForMqttMessage()

                if self.motorManager.checkStoppedByIrSensor():
                    self._sendMqttState()

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
                    elif path == "/action/go-up":
                        self._goUp(client)
                    elif path == "/action/go-down":
                        self._goDown(client)
                    elif path == "/action/stop":
                        self._stop(client)
                    elif path == "/settings/set-net":
                        self._setNet(client, queryStringsArray)
                    elif path == "/settings/reverse-motor":
                        self._reverseMotor(client)
                    elif path == "/settings/group":
                        self._group(client, queryStringsArray)
                    elif path == "/settings/connect":
                        self._connect(client, queryStringsArray)
                    elif path == "/favicon.ico":
                        self.webServer.ok(client)
                    else:
                        # Probably a request from Android or IOS for the Custom Portal.
                        # Anyways, return a redirect to the index and do not close the client connection.
                        self.webServer.redirectToIndex(client)
            except Exception as e:
                print("> ShadeManager._pollWebServer exception: {}".format(e))

            await asyncio.sleep_ms(300)

    def _checkForMqttMessage(self):
        try:
            message = self.mqttManager.checkMessage()

            if not message == None:
                if message == "up":
                    self.motorManager.goUp()
                elif message == "down":
                    self.motorManager.goDown()
                elif message == "stop":
                    self.motorManager.stop()
        except Exception as e:
            print("> ShadeManager._checkForMqttMessage exception: {}".format(e))

    async def _sendState(self):
        while True:
            self._sendMqttState()

            await asyncio.sleep(30)

    def _sendMqttState(self):
        try:
            group = settings.readGroup()
            motorState = self.motorManager.getState()

            state = "{" + '"group": "{}", "state": "{}"'.format(group, motorState) + "}"

            self.mqttManager.publishState(state)
        except Exception as e:
            print("> ShadeManager._sendMqttState exception: {}".format(e))

    def _index(self, client):
        ip = self.wifiManager.getIp()
        netId, essid, motorReversed, group = settings.readSettings()

        if motorReversed == "1":
            motorReversed = "CHECKED"
        else:
            motorReversed = ""

        interpolate = {
            "IP": ip,
            "NET_ID": netId,
            "ESSID": essid,
            "MOTOR_REVERSED": motorReversed,
            "GROUP": group,
        }

        self.webServer.index(client, interpolate)

    def _goUp(self, client):
        self.motorManager.goUp()
        self.webServer.ok(client)
        self._sendMqttState()

    def _goDown(self, client):
        self.motorManager.goDown()
        self.webServer.ok(client)
        self._sendMqttState()

    def _stop(self, client):
        self.motorManager.stop()
        self.webServer.ok(client)
        self._sendMqttState()

    def _setNet(self, client, queryStringsArray):
        if "id" in queryStringsArray and not queryStringsArray["id"] == "":
            netId = queryStringsArray["id"]
            settings.writeNetId(netId)

            self.wifiManager.setNetId(netId)
            self.mDnsServer.setNetId(netId)

        self.webServer.ok(client)

    def _reverseMotor(self, client):
        settings.writeMotorReversed()
        self.motorManager.reverseDefaultDirection()
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
