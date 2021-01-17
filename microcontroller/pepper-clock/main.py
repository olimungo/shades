from uasyncio import get_event_loop, sleep_ms
from time import sleep
from gc import collect, mem_free
from machine import (
    reset,
    deepsleep,
    reset_cause,
    PWRON_RESET,
    HARD_RESET,
    DEEPSLEEP_RESET,
    SOFT_RESET,
)
from time import sleep
from network import WLAN, STA_IF

# from WifiManager import WifiManager
# from HttpServer import HttpServer
# from mDnsServer import mDnsServer
# from Settings import Settings
# from NtpTime import NtpTime
from Credentials import Credentials
from Display import Display, COL_DIGITS
from NetworkManager import NetworkManager


class Main:
    def __init__(self):
        # self.sta_if = WLAN(STA_IF)
        # self.settings = Settings().load()
        self.credentials = Credentials()

        # self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, self.settings.net_id))
        # self.mdns = mDnsServer(PUBLIC_NAME.lower(), self.settings.net_id)

        # routes = {
        #     b"/": b"./index.html",
        #     b"/index.html": b"./index.html",
        #     b"/scripts.js": b"./scripts.js",
        #     b"/style.css": b"./style.css",
        #     b"/favicon.ico": self.favicon,
        #     b"/connect": self.connect,
        #     b"/settings/values": self.settings_values,
        #     b"/settings/net": self.settings_net,
        #     b"/settings/group": self.settings_group,
        # }

        # self.http = HttpServer(routes)
        # print("> HTTP server up and running")

        self.display = Display()
        self.networkManager = NetworkManager()
        # self.ntp = NtpTime()

        # self.previous_hour1 = self.previous_hour2 = -1
        # self.previous_minute1 = self.previous_minute2 = -1
        # self.previous_second2 = self.previous_count = -1

        # self.loop = get_event_loop()
        # self.loop.create_task(self.check_wifi())
        # self.loop.create_task(self.update_time())
        # self.loop.run_forever()
        # self.loop.close()

        self.loop = get_event_loop()

        rst_cause = reset_cause()

        if rst_cause in [PWRON_RESET, SOFT_RESET]:
            self.power_on_reset_wkfl()
        elif rst_cause == HARD_RESET:
            self.hard_reset_wkfl()
        elif rst_cause == DEEPSLEEP_RESET:
            self.deepsleep_reset_wkfl()
        else:
            self.other_reset_wkfl(rst_cause)

        self.loop.run_forever()
        self.loop.close()

    # Power on
    def power_on_reset_wkfl(self):
        print("> SOFT reset or POWER ON reset")
        self.display_logo()

        sleep(2)

        self.check_credentials()

    # Reset button pressed
    def hard_reset_wkfl(self):
        print("> HARD reset")
        self.display_access_point_icon()
        self.networkManager.start_access_point()

    # Reset from deepsleep
    def deepsleep_reset_wkfl(self):
        print("> DEEPSLEEP reset")

    def other_reset_wkfl(self, rst_cause):
        print("> Other reset: {}".format(rst_cause))

    def display_logo(self):
        from images import pepper_clock_icon, pepper_clock_icon_size

        self.display.display_image(
            pepper_clock_icon, pepper_clock_icon_size[0], pepper_clock_icon_size[1]
        )

    def display_no_wifi_icon(self):
        from images import no_wifi_icon, no_wifi_icon_size

        self.display.display_image(
            no_wifi_icon, no_wifi_icon_size[0], no_wifi_icon_size[1]
        )

    def display_access_point_icon(self):
        from images import access_point_icon, access_point_icon_size

        self.display.display_image(
            access_point_icon, access_point_icon_size[0], access_point_icon_size[1]
        )

    def check_credentials(self):
        if self.credentials.load().is_valid():
            return True

        self.display_no_wifi_icon()
        print("> Going to deep sleep...")
        deepsleep()

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        result = b'{"ip": "%s", "essid": "%s"}' % (
            self.wifi.ip,
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
    print("Free mem: {}".format(mem_free()))

    sleep(10)
    reset()
