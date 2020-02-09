import ubinascii
from umqtt.simple import MQTTClient
from machine import unique_id,


class MqttManager:
    lastMessage = ""

    def __init__(self, commandsTopic, statesTopic, logsTopic):
        self.commandsTopic = commandsTopic
        self.statesTopic = statesTopic
        self.logsTopic = logsTopic

    def checkMessage(self):
        try:
            self.mqtt.check_msg()

            message = self.lastMessage
            self.lastMessage = ""

            return message
        except Exception as e:
            print("> MQTT broker checkMessage error: {}".format(e))

    def _messageReceived(self, topic, message):
        self.lastMessage = message.decode("utf-8")

    def connect(self, brokerIp,netId):
        try:
            self.netId = netId
            clientId = ubinascii.hexlify(unique_id())

            self.mqtt = MQTTClient(clientId, brokerIp)
            self.mqtt.set_callback(self._messageReceived)
            self.mqtt.connect()
            self.mqtt.subscribe("{}/{}".format(self.commandsTopic, self.netId))
        except Exception as e:
            print("> MQTT broker connect error: {}".format(e))

    def sendState(self, message):
        self.mqtt.publish("{}/{}".format(self.statesTopic, self.netId), message)

    def sendLog(self, message):
        self.mqtt.publish("{}/{}".format(self.logsTopic, self.netId), message)

