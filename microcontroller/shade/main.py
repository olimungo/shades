import uasyncio as asyncio
from WifiManager import WifiManager

from DnsServer import DnsServer

from MqttManager import MqttManager
from ShadeManager import ShadeManager
from WebServer import WebServer
import settings


PUBLIC_NAME = "shade"
MQTT_BROKER_NAME = "nestor.local"
BROKER_TOPIC_NAME = "shades"
netId = settings.readNetId()

wifiManager = WifiManager("{}-{}".format(PUBLIC_NAME, netId))
dnsServer = DnsServer(wifiManager, "{}-{}".format(PUBLIC_NAME, netId))
mqttManager = MqttManager(dnsServer, MQTT_BROKER_NAME, netId, BROKER_TOPIC_NAME)
webServer = WebServer()

shadeManager = ShadeManager(wifiManager, dnsServer, mqttManager, webServer)

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()
