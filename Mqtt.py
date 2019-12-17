import ubinascii
from umqtt.simple import MQTTClient
from machine import unique_id, Timer


class MqttManager:
    mqtt = None
    clientId = ubinascii.hexlify(unique_id())

    def __init__(self, mqttServerIp, netId):
        self.mqtt = MQTTClient(self.clientId, mqttServerIp)
        self.mqtt.set_callback(self.messageReceived)

        timer = Timer(-1)
        timer.init(period=5000, mode=Timer.ONE_SHOT, callback=self.__postInit)

    def __postInit(self, timer):
        self.mqtt.connect()
        subscribeTopic = "shade/{}/commands".format(7)
        self.mqtt.subscribe(subscribeTopic)

        timer = Timer(-1)
        timer.init(
            period=500, mode=Timer.PERIODIC, callback=lambda t: self.mqtt.check_msg()
        )

    def messageReceived(self, topic, msg):
        print((topic, msg))

        return topic, msg

    def sendMessage(self, netId, msg):
        self.mqtt.publish("shade/{}".format(netId), msg)
