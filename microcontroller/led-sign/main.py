import uasyncio as asyncio
from WifiManager import WifiManager
from DnsServer import DnsServer
from MqttManager import MqttManager
from WebServer import WebServer
from SignManager import SignManager

PUBLIC_NAME = "mungo-sign"
MQTT_BROKER_NAME = "nestor.local"
BROKER_TOPIC_NAME = "signs"

wifiManager = WifiManager(PUBLIC_NAME)
dnsServer = DnsServer(wifiManager, PUBLIC_NAME)
mqttManager = MqttManager(dnsServer, MQTT_BROKER_NAME, 1, BROKER_TOPIC_NAME)
webServer = WebServer()

signManager = SignManager(wifiManager, dnsServer, mqttManager, webServer)

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()