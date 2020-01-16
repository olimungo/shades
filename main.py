import time
from machine import Timer, reset, unique_id
from Web import WebServer
from Wifi import WifiManager
from Motor import MotorManager
import settings
from Mqtt import MqttManager

import ubinascii
from umqtt.simple import MQTTClient


MQTT_BROKER = "192.168.0.167"

webServer = WebServer()
wifiManager = WifiManager()
motorManager = MotorManager()
mqttManager = MqttManager(MQTT_BROKER, 2)


def handleWebRequest(emptyRequest, client, path, queryStringsArray):
    if not emptyRequest:
        if path == "/":
            ip = wifiManager.getIp()
            netId, essid, motorReversed = settings.readSettings()

            webServer.index(client, ip, netId, essid, motorReversed)
        elif path == "/action/go-up":
            print(path)
            motorManager.goUp()
            webServer.ok(client)

            netId = settings.readNetId()
        elif path == "/action/go-down":
            print(path)
            motorManager.goDown()
            webServer.ok(client)
        elif path == "/action/stop":
            print(path)
            motorManager.stop()
            webServer.ok(client)
        elif path == "/settings/set-net":
            if len(queryStringsArray) > 0 and not queryStringsArray["id"] == "":
                settings.writeNetId(queryStringsArray["id"])

            webServer.ok(client)
        elif path == "/settings/reverse-motor":
            settings.writeMotorReversed()
            motorManager.reverseMotor()
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


def handleWeb(timer):
    try:
        emptyRequest, client, path, queryStringsArray = webServer.handleRequest()
        handleWebRequest(emptyRequest, client, path, queryStringsArray)
    except Exception as e:
        print("> Web exception: {}".format(e))


def handleMqtt(timer):
    try:
        message = mqttManager.checkMessage()

        if message == "up":
            motorManager.goUp()
        elif message == "down":
            motorManager.goDown()
        elif message == "stop":
            motorManager.stop()
    except Exception as e:
        print("> Mqtt exception: {}".format(e))


timerWeb = Timer(-1)
timerWeb.init(period=50, mode=Timer.PERIODIC, callback=handleWeb)

timerMqtt = Timer(-1)
timerMqtt.init(period=500, mode=Timer.PERIODIC, callback=handleMqtt)
