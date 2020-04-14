import ubinascii
from umqtt.simple import MQTTClient
from machine import unique_id
import uasyncio as asyncio


class MqttManager:
    loop = asyncio.get_event_loop()
    connected = False
    messages = []

    def __init__(self, dnsServer, brokerName, netId, topicName):
        self.dnsServer = dnsServer
        self.brokerName = brokerName
        self.netId = netId
        self.commandsTopic = "commands/{}".format(topicName)
        self.statesTopic = "states/{}".format(topicName)
        self.logsTopic = "logs/{}".format(topicName)

        self.loop.create_task(self._checkConnection())

    async def _checkConnection(self):
        while True:
            while not self.dnsServer.isConnected():
                await asyncio.sleep(1)

            self._connect()

            while self.dnsServer.isConnected() and self.connected:
                self._checkMessageReceived()

                await asyncio.sleep_ms(250)

            self.connected = False

            await asyncio.sleep(5)

    def _connect(self):
        try:
            clientId = ubinascii.hexlify(unique_id())

            brokerIp = self.dnsServer.resolve_mdns_address(self.brokerName)

            if brokerIp != None:
                brokerIp = "{}.{}.{}.{}".format(*brokerIp)

                self.mqtt = MQTTClient(clientId, brokerIp)
                self.mqtt.set_callback(self._messageReceived)
                self.mqtt.connect()
                self.mqtt.subscribe("{}/{}".format(self.commandsTopic, self.netId))

                self.log("IP assigned: {}".format(self.dnsServer.getIp()))

                self.connected = True
        except Exception as e:
            print("> MQTT broker connect error: {}".format(e))

    def _checkMessageReceived(self):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            print("> MQTT broker _checkMessageReceived error: {}".format(e))
            self.connected = False

    def _messageReceived(self, topic, message):
        self.messages.append(message.decode("utf-8"))

    def publishState(self, message):
        if self.connected:
            try:
                self.mqtt.publish("{}/{}".format(self.statesTopic, self.netId), message)
            except Exception as e:
                print("> MQTT broker publishState error: {}".format(e))

    def log(self, message):
        if self.connected:
            try:
                self.mqtt.publish("{}/{}".format(self.logsTopic, self.netId), message)
            except Exception as e:
                print("> MQTT broker log error: {}".format(e))

    def checkMessage(self):
        if len(self.messages) > 0:
            # Return first elem of the array
            return self.messages.pop(-len(self.messages))

        return None

    def isConnected(self):
        return self.connected
