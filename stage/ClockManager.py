from uasyncio import get_event_loop, sleep_ms
from uselect import poll
from gc import mem_free, collect, threshold, mem_alloc
import network

from clock import Clock

from httpServer import HTTPServer
from captivePortal import CaptivePortal
from credentials import Creds
from settings import Settings

PUBLIC_NAME = b"clock"
ORANGE = (255, 98, 0)
SPINNER_RATE = const(120)

class Player:
    GREEN = 0
    RED = 1

class Mode:
    CLOCK = 0
    SCOREBOARD = 1

class ClockManager:
    def __init__(self):
        self.brightness = 0
        self.mode = Mode.CLOCK
        self.sta_if = network.WLAN(network.STA_IF)

        self.credentials = Creds().load()
        self.settings = Settings().load()

        routes = {
            b"/": b"./index.html",
            b"/connect": self.connect,
            b"/action/color": self.set_color,
            b"/action/clock/display": self.display_clock,
            b"/action/brightness/more": self.brightness_more,
            b"/action/brightness/less": self.brightness_less,
            b"/action/scoreboard/display": self.display_scoreboard,
            b"/action/scoreboard/green/more": self.scoreboard_green_more,
            b"/action/scoreboard/green/less": self.scoreboard_green_less,
            b"/action/scoreboard/red/more": self.scoreboard_red_more,
            b"/action/scoreboard/red/less": self.scoreboard_red_less,
            b"/action/scoreboard/reset": self.scoreboard_reset,
            b"/settings/values": self.settings_values,
            b"/settings/net": self.settings_net,
            b"/settings/group": self.settings_group
        }

        self.poller = poll()
        self.http = HTTPServer(self.poller, CaptivePortal.AP_IP, routes)
        print("> HTTP server started")

        self.clock = Clock(self.settings.color)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.create_task(self.poll_web_server())

    async def check_wifi(self):
        while True:
            collect()
            threshold(mem_free() // 4 + mem_alloc())
            print("> Free memory: {}".format(mem_free()))

            # self.clock.play_spinner(SPINNER_RATE, ORANGE)

            self.portal = CaptivePortal(PUBLIC_NAME + b"-%s" % self.settings.net_id)
            self.portal.start()

            while not self.sta_if.isconnected():
                await sleep_ms(1000)
            
            ip = self.sta_if.ifconfig()[0]
            self.http.set_ip(ip)

            print("> Connected to {:s} ({:s})".format(self.credentials.essid, ip))

            self.portal = None
            
            collect()
            print("> Free memory: {}".format(mem_free()))

            self.clock.stop_clock()
            self.clock.stop_effect_init = True
            self.clock.display()

            while  self.sta_if.isconnected():
                await sleep_ms(1000)

    async def poll_web_server(self):
        while True:
            for response in self.poller.ipoll(1000):
                sock, event, *others = response
                self.http.handle(sock, event, others)

            await sleep_ms(50)

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = ""

        result = b'{"ip": "' + self.http.local_ip + '", "netId": "' + self.settings.net_id + '", "group": "' + \
            self.settings.group + '", "essid": "' + essid + '"}'

        return result, b"HTTP/1.1 200 OK\r\n"

    def connect(self, params):
        if self.portal:
            # Write out credentials
            self.credentials.essid = params.get(b"essid", None)
            self.credentials.password = params.get(b"password", None)
            self.credentials.write()

            self.loop.create_task(self.portal.connect_to_wifi())

        return b"", b"HTTP/1.1 200 OK\r\n"

    def display_clock(self, params=None):
        if self.mode == Mode.SCOREBOARD:
            self.mode = Mode.CLOCK
            self.clock.display()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def display_scoreboard(self, params=None):
        if self.mode == Mode.CLOCK:
            self.clock.stop_clock()
            self.mode = Mode.SCOREBOARD
            self.clock.display_scoreboard()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def set_color(self, params):
        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.clock.set_color(color)

            # Comment the following lines in order to NOT save the selected color for the next boot
            self.settings.color = color
            self.settings.write()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def scoreboard_green_more(self, params):
        return self.scoreboard_update(Player.GREEN, 1)

    def scoreboard_green_less(self, params):
        return self.scoreboard_update(Player.GREEN, -1)

    def scoreboard_red_more(self, params):
        return self.scoreboard_update(Player.RED, 1)

    def scoreboard_red_less(self, params):
        return self.scoreboard_update(Player.RED, -1)

    def scoreboard_update(self, player, increment):
        if player == Player.GREEN:
            self.clock.update_scoreboard_green(increment)
        else:
            self.clock.update_scoreboard_red(increment)

        return self.display_scoreboard()

    def brightness_more(self, params):
        self.display_clock()
        self.clock.set_brighter()
        self.settings.color = b"" + self.clock.hex
        self.settings.write()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def brightness_less(self, params):
        self.display_clock()
        self.clock.set_darker()
        self.settings.color = b"" + self.clock.hex
        self.settings.write()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def scoreboard_reset(self, params):
        self.display_scoreboard()
        self.clock.reset_scoreboard()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def settings_net(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()

        return b"", b"HTTP/1.1 200 OK\r\n"

    def settings_group(self, params):
        name = params.get(b"name", None)

        if name:
            self.settings.group = name
            self.settings.write()

        return b"", b"HTTP/1.1 200 OK\r\n"

