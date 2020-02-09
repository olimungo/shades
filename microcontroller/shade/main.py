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

isStartupDelayEllapsed = False
isStationConnected = False
isMqttBrokerFound = False

startupDelayEllapsedTimer = Timer(-1)
checkWifiConnectionTimer = Timer(-1)
heartbeatTimer = Timer(-1)
sendMqttStateTimer = Timer(-1)


def handleWeb():
    try:
        emptyRequest, client, path, queryStringsArray = webServer.handleRequest()

        if not emptyRequest:
            if path == "/":
                ip = wifiManager.getIp()
                netId, essid, motorReversed, group = settings.readSettings()

                webServer.index(client, ip, netId, essid, motorReversed, group)
            elif path == "/action/go-up":
                print(path)
                motorManager.goUp()
                webServer.ok(client)
                sendMqttState()

                netId = settings.readNetId()
            elif path == "/action/go-down":
                print(path)
                motorManager.goDown()
                webServer.ok(client)
                sendMqttState()
            elif path == "/action/stop":
                print(path)
                motorManager.stop()
                webServer.ok(client)
                sendMqttState()
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

                    wifiManager.connect(
                        queryStringsArray["essid"], queryStringsArray["pwd"]
                    )

                webServer.ok(client)
            else:
                print(path)
                webServer.notFound(client)
    except Exception as e:
        print("> handleWeb exception: {}".format(e))


def checkForMqttMessage():
    try:
        message = mqttManager.checkMessage()

        if message == "up":
            motorManager.goUp()
        elif message == "down":
            motorManager.goDown()
        elif message == "stop":
            motorManager.stop()

        if message in ["up", "down", "stop"]:
            sendMqttState()
    except Exception as e:
        print("> checkForMqttMessage exception: {}".format(e))


def sendMqttState(timer=None):
    try:
        if isMqttBrokerFound:
            group = settings.readGroup()
            motorState = motorManager.getState()

            state = "{" + '"group": "{}", "state": "{}"'.format(group, motorState) + "}"

            mqttManager.sendState(state)
    except Exception as e:
        print("> sendMqttState exception: {}".format(e))


def heartbeat(timer):
    if isStartupDelayEllapsed:
        wifiManager.checkConnection()

    handleWeb()

    if isStationConnected:
        dnsServer.processPackets()

    if isMqttBrokerFound:
        checkForMqttMessage()


def startupDelayEllapsed(timer):
    global isStartupDelayEllapsed
    isStartupDelayEllapsed = True


def checkWifiConnection(timer):
    global isStationConnected
    global isMqttBrokerFound

    try:
        if station.isconnected():
            if not isStationConnected:
                isStationConnected = True

                localIp = station.ifconfig()[0]

                print("ip: " + localIp)

                dnsServer.connect(localIp, "{}-{}".format(PUBLIC_NAME, netId))

                nestorIp = dnsServer.resolve_mdns_address(MQTT_BROKER_NAME)

                if nestorIp != None:
                    isMqttBrokerFound = True
                    nestorIp = "{}.{}.{}.{}".format(*nestorIp)
                    mqttManager.connect(nestorIp, netId)
                    mqttManager.sendLog("IP assigned: {}".format(localIp))
                    sendMqttState()
                else:
                    isMqttBrokerFound = False

                Blink().fast()
        else:
            isStationConnected = False
            isMqttBrokerFound = False
    except Exception as e:
        print("> checkWifiConnection exception: {}".format(e))


startupDelayEllapsedTimer.init(
    period=6000, mode=Timer.ONE_SHOT, callback=startupDelayEllapsed
)

heartbeatTimer.init(period=250, mode=Timer.PERIODIC, callback=heartbeat)

checkWifiConnectionTimer.init(
    period=1000, mode=Timer.PERIODIC, callback=checkWifiConnection
)

sendMqttStateTimer.init(period=30000, mode=Timer.PERIODIC, callback=sendMqttState)
