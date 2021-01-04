from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset
from time import sleep
from network import WLAN, STA_IF

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from Settings import Settings
from Credentials import Credentials
from Sign import Sign

PUBLIC_NAME = b"Sign"


class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings().load()
        self.credentials = Credentials().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, self.settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), self.settings.net_id)

        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/scripts.js": b"./scripts.js",
            b"/style.css": b"./style.css",
            b"/favicon.ico": self.favicon,
            b"/connect": self.connect,
            b"/action/previous": self.previous,
            b"/action/next": self.next,
            b"/settings/values": self.settings_values,
            b"/settings/net": self.settings_net,
            b"/settings/group": self.settings_group,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.sign = Sign()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.run_forever()
        self.loop.close()

    async def check_wifi(self):
        while True:
            await sleep_ms(2000)

            while not self.sta_if.isconnected():
                await sleep_ms(1000)

            while self.sta_if.isconnected():
                await sleep_ms(1000)

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        result = b'{"ip": "%s", "netId": "%s", "group": "%s", "essid": "%s"}' % (
            self.wifi.ip,
            self.settings.net_id,
            self.settings.group,
            essid,
        )

        return result

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.loop.create_task(self.wifi.connect())

    def previous(self, params):
        self.sign.previous()

    def next(self, params):
        pass
        self.sign.next()

    def settings_net(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

            self.wifi.set_ap_essid(b"%s-%s" % (PUBLIC_NAME, id))
            self.mdns.set_net_id(id)

    def settings_group(self, params):
        name = params.get(b"name", None)

        if name:
            self.settings.group = name
            self.settings.write()


try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()