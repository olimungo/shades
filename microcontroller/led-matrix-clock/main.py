import uasyncio as asyncio
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from WifiManager import WifiManager
from UdpsServer import UdpsServer
from WebServer import WebServer
from ClockManager import ClockManager
import settings

PUBLIC_NAME = "clock"
MQTT_BROKER_NAME = "nestor.local"
MQTT_BROKER_TOPIC_NAME = "clock"

netId = settings.readNetId()
publicName = "{}-{}".format(PUBLIC_NAME, netId)

wifiManager = WifiManager(publicName)
updsServer = UdpsServer(wifiManager)
mdnsServer = mDnsServer(wifiManager, publicName)
mqttManager = MqttManager(mdnsServer, MQTT_BROKER_NAME, netId, MQTT_BROKER_TOPIC_NAME)
webServer = WebServer(wifiManager)

clockManager = ClockManager(wifiManager, mqttManager, webServer)

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()
