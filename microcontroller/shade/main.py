import uasyncio as asyncio
from WifiManager import WifiManager
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from ShadeManager import ShadeManager
from WebServer import WebServer
import settings


PUBLIC_NAME = "shade"
MQTT_BROKER_NAME = "nestor.local"
BROKER_TOPIC_NAME = "shades"

netId = settings.readNetId()

wifiManager = WifiManager(PUBLIC_NAME, netId)
mdnsServer = mDnsServer(wifiManager, PUBLIC_NAME, netId)
webServer = WebServer(wifiManager)
mqttManager = MqttManager(mdnsServer, MQTT_BROKER_NAME, netId, BROKER_TOPIC_NAME)
shadeManager = ShadeManager(wifiManager, mdnsServer, mqttManager, webServer)

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()
