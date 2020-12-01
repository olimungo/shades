from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset
from time import sleep
from network import WLAN, STA_IF

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from Motor import Motor
from Settings import Settings
from Credentials import Credentials

PUBLIC_NAME = b"Shade"
BROKER_NAME = b"nestor.local"

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings().load()
        self.credentials = Credentials().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, self.settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), self.settings.net_id)
        self.mqtt = MqttManager(self.mdns, BROKER_NAME, self.settings.net_id, PUBLIC_NAME.lower())

        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/scripts.js": b"./scripts.js",
            b"/style.css": b"./style.css",
            b"/favicon.ico": self.favicon,
            b"/connect": self.connect,
            b"/action/go-up": self.go_up,
            b"/action/go-down": self.go_down,
            b"/action/stop": self.stop,
            b"/settings/values": self.settings_values,
            b"/settings/net": self.settings_net,
            b"/settings/group": self.settings_group,
            b"/settings/reverse-motor": self.reverse_motor
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.motor = Motor()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_wifi(self):
        while True:
            await sleep_ms(2000)

            while not self.sta_if.isconnected():
                await sleep_ms(1000)

            while self.sta_if.isconnected():
                await sleep_ms(1000)

    async def check_mqtt(self):
        while True:
            # message = self.mqtt.check_messages()

            # if not message == None:
            #     if message == "up":
            #         self.motor.goUp()
            #     elif message == "down":
            #         self.motor.goDown()
            #     elif message == "stop":
            #         self.motor.stop()

            await sleep_ms(500)

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        result = b'{"ip": "%s", "netId": "%s", "group": "%s", "motorReversed": "%s", "essid": "%s"}' % (self.wifi.ip, self.settings.net_id,
            self.settings.motor_reversed, self.settings.group, essid)

        return result

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.loop.create_task(self.wifi.connect())

    def go_up(self, params=None):
        self.motor.go_up()
        self.send_state()

    def go_down(self, params=None):
        self.motor.go_down()
        self.send_state()

    def stop(self, params):
        self.motor.stop()
        self.send_state()

    def settings_net(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

    def settings_group(self, params):
        name = params.get(b"name", None)

        if name:
            self.settings.group = name
            self.settings.write()

    def reverse_motor(self, params):
        motor_reversed = self.settings.motor_reversed

        if motor_reversed == b"0":
            motor_reversed = b"1"
        else:
            motor_reversed = b"0"

        self.settings.write()
        self.motor.reverse_direction()

    def send_state(self):
        try:
            group = self.settings.group
            motor_state = self.motor.get_state()

            state = b'{"group": "%s", "state": "%s"}' % (group, motor_state)

            self.mqtt.publish_state(state)
        except Exception as e:
            print("> Main.send_state exception: {}".format(e))

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()