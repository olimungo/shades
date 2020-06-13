from uasyncio import get_event_loop
# from mDnsServer import mDnsServer
# from MqttManager import MqttManager
from WifiManager import WifiManager
from WebServer import WebServer
from ClockManager import ClockManager
from settings import readNetId

PUBLIC_NAME = "clock"
MQTT_BROKER_NAME = "nestor.local"
MQTT_BROKER_TOPIC_NAME = "clock"

netId = readNetId()
publicName = "{}-{}".format(PUBLIC_NAME, netId)

wifiManager = WifiManager(publicName)
# mdnsServer = mDnsServer(wifiManager, publicName)
# mqttManager = MqttManager(mdnsServer, MQTT_BROKER_NAME, netId, MQTT_BROKER_TOPIC_NAME)
webServer = WebServer(wifiManager)

# clockManager = ClockManager(wifiManager, mqttManager, webServer)
clockManager = ClockManager(wifiManager, None, webServer)

loop = get_event_loop()
loop.run_forever()
loop.close()
