from uasyncio import get_event_loop, sleep_ms
from WifiManager import WifiManager
from HttpServer import HttpServer, HEADER_OK
from ClockManager import ClockManager
from gc import collect, mem_free
from machine import reset

from time import sleep

PUBLIC_NAME = "clock"

class Main():
    def __init__(self):
        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/.favico": self.favico,
            b"/toto": self.toto
        }

        self.wifi = WifiManager(PUBLIC_NAME, "0")
        self.http = HttpServer("192.168.4.1", routes)
        
        # ClockManager(self.wifi, self.http)

        self.loop = get_event_loop()
        self.loop.create_task(self.handle())
        self.loop.run_forever()
        self.loop.close()

    async def handle(self):
        while True:
            self.http.handle()
            await sleep_ms(50)

    def toto(self,params):
        print("toto: {}".format(params))

        return b'{"toto": 3, "titi": "tata"}', HEADER_OK

    def favico(self, params):
        print("favico")

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