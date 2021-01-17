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
from NtpTime import NtpTime
from Display import Display, COL_DIGITS

PUBLIC_NAME = b"Clock"


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
            b"/settings/values": self.settings_values,
            b"/settings/net": self.settings_net,
            b"/settings/group": self.settings_group,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.display = Display()
        self.ntp = NtpTime()

        self.previous_hour1 = self.previous_hour2 = -1
        self.previous_minute1 = self.previous_minute2 = -1
        self.previous_second2 = self.previous_count = -1

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.create_task(self.update_time())
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

    async def update_time(self):
        # self.display.set_eco_mode(True)

        while True:
            hour1, hour2, minute1, minute2, second1, second2 = self.ntp.get_time()
            seconds = second1 * 10 + second2
            count = int(seconds / (60 / 9))  # 9 states = 8 lights + no light

            updated = self.display.draw_digit(COL_DIGITS[0], hour1, self.previous_hour1)
            updated = (
                self.display.draw_digit(COL_DIGITS[1], hour2, self.previous_hour2)
                or updated
            )
            updated = (
                self.display.draw_digit(COL_DIGITS[2], minute1, self.previous_minute1)
                or updated
            )
            updated = (
                self.display.draw_digit(COL_DIGITS[3], minute2, self.previous_minute2)
                or updated
            )
            updated = self.display.draw_dots(second2, self.previous_second2) or updated
            updated = self.display.draw_bar(count, self.previous_count) or updated

            if updated:
                self.display.update()

            self.previous_hour1 = hour1
            self.previous_hour2 = hour2
            self.previous_minute1 = minute1
            self.previous_minute2 = minute2
            self.previous_second2 = second2
            self.previous_count = count

            await sleep_ms(100)


try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()
