import time
from machine import Timer, reset, unique_id

from Web import WebServer
from Wifi import WifiManager
from Motor import MotorManager
import settings

from Mqtt import MqttManager

webServer = WebServer()
wifiManager = WifiManager()
motorManager = MotorManager()
mqttManager = MqttManager(settings.readNetId())


def handleWebRequest(client, path, queryStringsArray):
    if path == "/":
        ip = wifiManager.getIp()
        netId, essid, motorReversed, group = settings.readSettings()

        webServer.index(client, ip, netId, essid, motorReversed, group)
    elif path == "/action/go-up":
        print(path)
        motorManager.goUp()
        webServer.ok(client)
        sendStatus()

        netId = settings.readNetId()
    elif path == "/action/go-down":
        print(path)
        motorManager.goDown()
        webServer.ok(client)
        sendStatus()
    elif path == "/action/stop":
        print(path)
        motorManager.stop()
        webServer.ok(client)
        sendStatus()
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


def handleWeb(timer):
    try:
        emptyRequest, client, path, queryStringsArray = webServer.handleRequest()

        if not emptyRequest:
            handleWebRequest(client, path, queryStringsArray)
    except Exception as e:
        print("> Web exception: {}".format(e))


def handleMqtt(timer):
    try:
        message = mqttManager.checkMessage()

        if message == "up":
            motorManager.goUp()
            sendStatus()
        elif message == "down":
            motorManager.goDown()
            sendStatus()
        elif message == "stop":
            motorManager.stop()
            sendStatus()
    except Exception as e:
        print("> Mqtt exception: {}".format(e))


def sendStatus(timer=None):
    try:
        group = settings.readGroup()
        motorStatus = motorManager.getStatus()

        status = "{" + '"group": "' + group + '", "state": "' + motorStatus + '"' + "}"
        mqttManager.sendStatus(status)
    except Exception as e:
        print("> Mqtt send status exception: {}".format(e))


timerWeb = Timer(-1)
timerWeb.init(period=100, mode=Timer.PERIODIC, callback=handleWeb)

timerMqtt = Timer(-1)
timerMqtt.init(period=100, mode=Timer.PERIODIC, callback=handleMqtt)

timerStatus = Timer(-1)
timerStatus.init(period=3000, mode=Timer.PERIODIC, callback=sendStatus)
