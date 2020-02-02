from machine import Timer
import network

from Web import WebServer
from Wifi import WifiManager
from Motor import MotorManager
import settings
from Blink import Blink
from Mqtt import MqttManager
from slimDNS import SlimDNSServer

PUBLIC_NAME = "shade"
BROKER_TOPIC_NAME = "shades"
MQTT_BROKER_NAME = "nestor.local"

netId = settings.readNetId()
station = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

webServer = WebServer()
wifiManager = WifiManager("{}-{}".format(PUBLIC_NAME, netId))
motorManager = MotorManager()
mqttManager = MqttManager(
    "{}/commands".format(BROKER_TOPIC_NAME),
    "{}/states".format(BROKER_TOPIC_NAME),
    "logs/{}".format(BROKER_TOPIC_NAME),
)
dnsServer = SlimDNSServer()

checkWifiConnectionTimer = Timer(-1)
processTimer = Timer(-1)
sendStateTimer = Timer(-1)


def handleWebRequest(client, path, queryStringsArray):
    if path == "/":
        ip = wifiManager.getIp()
        netId, essid, motorReversed, group = settings.readSettings()

        webServer.index(client, ip, netId, essid, motorReversed, group)
    elif path == "/action/go-up":
        print(path)
        motorManager.goUp()
        webServer.ok(client)
        sendState()

        netId = settings.readNetId()
    elif path == "/action/go-down":
        print(path)
        motorManager.goDown()
        webServer.ok(client)
        sendState()
    elif path == "/action/stop":
        print(path)
        motorManager.stop()
        webServer.ok(client)
        sendState()
    elif path == "/settings/set-net":
        if len(queryStringsArray) > 0 and not queryStringsArray["id"] == "":
            settings.writeNetId(queryStringsArray["id"])

        webServer.ok(client)
    elif path == "/settings/reverse-motor":
        settings.writeMotorReversed()
        motorManager.reverseMotor()
        webServer.ok(client)
    elif path == "/settings/group":
        if len(queryStringsArray) > 0:
            settings.writeGroup(queryStringsArray["name"])

        webServer.ok(client)
    elif path == "/settings/connect":
        if (
            len(queryStringsArray) > 0
            and not queryStringsArray["essid"] == ""
            and not queryStringsArray["pwd"] == ""
        ):
            settings.writeEssid(queryStringsArray["essid"])

            wifiManager.connect(queryStringsArray["essid"], queryStringsArray["pwd"])

        webServer.ok(client)
    else:
        print(path)
        webServer.notFound(client)


def handleWeb():
    try:
        emptyRequest, client, path, queryStringsArray = webServer.handleRequest()

        if not emptyRequest:
            handleWebRequest(client, path, queryStringsArray)
    except Exception as e:
        print("> handleWeb exception: {}".format(e))


def handleMqtt():
    try:
        message = mqttManager.checkMessage()

        if message == "up":
            print("up")
            motorManager.goUp()
            sendState()
        elif message == "down":
            motorManager.goDown()
            sendState()
        elif message == "stop":
            print("stop")
            motorManager.stop()
            sendState()
    except Exception as e:
        print("> handleMqtt exception: {}".format(e))


def sendState(timer=None):
    try:
        if wifiManager.stationReady:
            group = settings.readGroup()
            motorStatus = motorManager.getStatus()

            status = "{" + '"group": {}, "state": {}'.format(group, motorStatus) + "}"

            mqttManager.sendState(status)
    except Exception as e:
        print("> sendState exception: {}".format(e))


def process(timer):
    if station.isconnected() or ap.isconnected():
        handleWeb()

    if wifiManager.stationReady:
        handleMqtt()
        dnsServer.processPackets()


def checkWifiConnection(timer):
    try:
        if station.isconnected():
            if not wifiManager.stationReady:
                localIp = station.ifconfig()[0]

                dnsServer.connect(localIp, "{}-{}".format(PUBLIC_NAME, netId))

                nestorIp = dnsServer.resolve_mdns_address("nestor.local")
                nestorIp = "{}.{}.{}.{}".format(*nestorIp)
                mqttManager.connect(nestorIp, netId)

                wifiManager.stationReady = True

                mqttManager.sendLog("IP assigned: {}".format(localIp))

                Blink().fast()
    except Exception as e:
        print("> checkWifiConnection exception: {}".format(e))


processTimer.init(period=500, mode=Timer.PERIODIC, callback=process)

checkWifiConnectionTimer.init(
    period=1000, mode=Timer.PERIODIC, callback=checkWifiConnection
)

sendStateTimer.init(period=1000, mode=Timer.PERIODIC, callback=sendState)
