from ubinascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from network import WLAN, STA_IF

WAIT_FOR_MDNS = const(5000)
WAIT_FOR_MESSAGE = const(500)
WAIT_BEFORE_RETRY = const(5000)

class MqttManager:
    def __init__(self, mdns, broker_name, net_id, topic_name):
        self.sta_if = WLAN(STA_IF)
        self.mdns = mdns
        self.broker_name = broker_name
        self.net_id = net_id
        self.commands_topic = "commands/{}".format(topic_name)
        self.states_topic = "states/{}".format(topic_name)
        self.logs_topic = "logs/{}".format(topic_name)

        self.loop = get_event_loop()
        self.connected = False
        self.messages = []

        self.loop.create_task(self.check_mdns())

    async def check_mdns(self):
        while True:
            while not self.mdns.connected:
                await sleep_ms(WAIT_FOR_MDNS)

            self.connect()

            if self.mdns.connected and self.connected:
                print("> MQTT server up and running")

            while self.mdns.connected and self.connected:
                self.check_msg()
                await sleep_ms(WAIT_FOR_MESSAGE)

            print("> MQTT server down")
            self.connected = False

            await sleep_ms(WAIT_BEFORE_RETRY)

    def connect(self):
        try:
            client_id = hexlify(unique_id())

            brokerIp = self.mdns.resolve_mdns_address(self.broker_name)

            if brokerIp != None:
                brokerIp = "{}.{}.{}.{}".format(*brokerIp)

                self.mqtt = MQTTClient(client_id, brokerIp)
                self.mqtt.set_callback(self.message_received)
                self.mqtt.connect()
                self.mqtt.subscribe("{}/{}".format(self.commands_topic, self.net_id))

                self.connected = True

                self.log("IP assigned: {}".format(self.sta_if.ifconfig()[0]))
        except Exception as e:
            print("> MQTT broker connect error: {}".format(e))

    def check_msg(self):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            print("> MQTT broker check_msg error: {}".format(e))
            self.connected = False

    def message_received(self, topic, message):
        self.messages.append(message.decode("utf-8"))

    def publish_state(self, message):
        if self.connected:
            try:
                self.mqtt.publish("{}/{}".format(self.states_topic, self.net_id), message)
            except Exception as e:
                print("> MQTT broker publish_state error: {}".format(e))

    def log(self, message):
        if self.connected:
            try:
                self.mqtt.publish("{}/{}".format(self.logs_topic, self.net_id), message)
            except Exception as e:
                print("> MQTT broker log error: {}".format(e))

    def check_messages(self):
        if len(self.messages) > 0:
            # Return first elem of the array
            return self.messages.pop(-len(self.messages))

        return None
