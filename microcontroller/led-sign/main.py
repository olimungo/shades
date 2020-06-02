import uasyncio as asyncio
from WifiManager import WifiManager
from DnsServer import DnsServer
from MqttManager import MqttManager
from WebServer import WebServer
from SignManager import SignManager
import settings

PUBLIC_NAME = "sign"
MQTT_BROKER_NAME = "nestor.local"
MQTT_BROKER_TOPIC_NAME = "signs"

netId = settings.readNetId()

wifiManager = WifiManager("{}-{}".format(PUBLIC_NAME, netId))
dnsServer = DnsServer(wifiManager, "{}-{}".format(PUBLIC_NAME, netId))
mqttManager = MqttManager(dnsServer, MQTT_BROKER_NAME, netId, MQTT_BROKER_TOPIC_NAME)
webServer = WebServer(wifiManager)

signManager = SignManager(wifiManager, dnsServer, mqttManager, webServer)

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()