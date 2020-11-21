from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset
from time import sleep

from WifiManager import WifiManager
from HttpServer import HttpServer, HEADER_OK
from Settings import Settings
from Credentials import Credentials

PUBLIC_NAME = b"Clock-%s"

class Main:
    def __init__(self):
        self.settings = Settings()
        self.credentials = Credentials()

        self.wifi = WifiManager(PUBLIC_NAME % self.settings.net_id)

        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/.favico": self.favico,
            b"/settings/values": self.settings_values,
            b"/action/brightness/more": self.brightness_more
        }

        self.http = HttpServer(routes)
        print("HTTP server up and running")
        
        # ClockManager(self.wifi, self.http)

        self.loop = get_event_loop()
        self.loop.create_task(self.handle())
        self.loop.run_forever()
        self.loop.close()

    async def handle(self):
        while True:
            self.http.handle()
            await sleep_ms(500)

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = ""

        result = b'{"ip": "' + self.wifi.ip + '", "netId": "' + self.settings.net_id + '", "group": "' + \
            self.settings.group + '", "essid": "' + essid + '"}'

        return result, b"HTTP/1.1 200 OK\r\n"

    def brightness_more(self, params):
        print("brightness more")
        # self.display_clock()
        # self.clock.set_brighter()
        # self.settings.color = b"" + self.clock.hex
        # self.settings.write()

        return b"", HEADER_OK

    def favico(self, params):
        print("> NOT sending the favico :-)")
        return b"", HEADER_OK

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()