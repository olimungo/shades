import time
from machine import Timer, reset
from Web import WebServer
from Wifi import WifiManager
from Motor import MotorManager
import settings

webServer = WebServer()
wifiManager = WifiManager()
motorManager = MotorManager()


def rst():
    reset()


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
        # print("> motor: " + str(motorManager.motorState))
        # print("> shade: " + str(motorManager.shadeState))
    except Exception as e:
        print("> Web exception: {}".format(e))


def handleWifi(timer):
    try:
        wifiManager.checkWifi()
    except Exception as e:
        print("> Wifi exception: {}".format(e))


timerWeb = Timer(-1)
timerWeb.init(period=1000, mode=Timer.PERIODIC, callback=handleWeb)

timerWifi = Timer(-1)
timerWifi.init(period=5000, mode=Timer.PERIODIC, callback=handleWifi)
