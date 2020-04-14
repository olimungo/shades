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

"""
def _index(client):
    print("> _index")

    ip = wifiManager.getIp()
    netId, essid, motorReversed, group = settings.readSettings()

    if motorReversed == "1":
        motorReversed = "CHECKED"
    else:
        motorReversed = ""

    interpolate = {
        "IP": ip,
        "NET_ID": netId,
        "ESSID": essid,
        "MOTOR_REVERSED": motorReversed,
        "GROUP": group,
    }

    webServer.index(client, interpolate, False)


def _index2(client):
    print("> _index2")

    webServer.index2(client)


async def _pollWebServer():
    while True:
        try:
            (emptyRequest, client, path, queryStringsArray,) = webServer.poll()

            if not emptyRequest:
                print("path: {}".format(path))

                if path == "/index.html":
                    _index(client)
                else:
                    _index2(client)
        except Exception as e:
            print("> _pollWebServer exception: {}".format(e))

        await asyncio.sleep_ms(500)
"""

loop = asyncio.get_event_loop()
# loop.create_task(_pollWebServer())
loop.run_forever()
loop.close()
