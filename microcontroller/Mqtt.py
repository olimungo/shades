import ubinascii
from umqtt.simple import MQTTClient
from machine import unique_id, Timer
import network


class MqttManager:
    mqtt = None
    clientId = ubinascii.hexlify(unique_id())
    station = network.WLAN(network.STA_IF)
    checkMessageTimer = Timer(-1)
    checkConnectivityTimer = Timer(-1)
    lastMessage = ""
    wifiConnected = False
    mqttConnected = False
    firstConnection = False

    def __init__(self, netId):
        self.netId = netId
        brokerIp = self._getBrokerIp()

        self.mqtt = MQTTClient(self.clientId, brokerIp)
        self.mqtt.set_callback(self._messageReceived)

        self.checkConnectivityTimer.init(
            period=1000, mode=Timer.PERIODIC, callback=self._checkConnectivity
        )

    def _getBrokerIp(self):
        file = open("broker.txt", "r")
        return file.read()

    def _checkConnectivity(self, timer):
        if self.station.isconnected():
            if not self.wifiConnected:
                self.wifiConnected = True

            if not self.mqttConnected:
                self._connectToBroker()
        else:
            if self.wifiConnected:
                self.wifiConnected = False
                self.mqttConnected = False
                self.checkMessageTimer.deinit()

    def _connectToBroker(self):
        try:
            self.mqtt.connect()

            if not self.firstConnection:
                self.firstConnection = True
                self.sendLog("REBOOT")

            self.mqtt.subscribe("shades/commands/{}".format(self.netId))

            self.checkMessageTimer.init(
                period=100, mode=Timer.PERIODIC, callback=self._checkMessage
            )

            self.mqttConnected = True
        except Exception as e:
            print("> MQTT broker error: {}".format(e))

    def _checkMessage(self, timer):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            timer.deinit()
            self.mqttConnected = False
            print("> MQTT broker error: {}".format(e))

    def _messageReceived(self, topic, message):
        self.lastMessage = message.decode("utf-8")

    def checkMessage(self):
        message = self.lastMessage
        self.lastMessage = ""

        return message

    def sendStatus(self, message):
        self.mqtt.publish("shades/states/{}".format(self.netId), message)

    def sendLog(self, message):
        self.mqtt.publish("logs/shades/{}".format(self.netId), message)

