from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop
from time import sleep_ms

from Credentials import Credentials, FILE

WAIT_FOR_AP = const(250)
PUBLIC_NAME = b"Pepper-clock"
AP_IP = "192.168.4.1"


class NetworkManager:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)

        self.sta_if.active(False)
        self.sta_if.active(False)

        self.credentials = Credentials()

        self.loop = get_event_loop()

    def start_access_point(self):
        self.ap_if.active(True)

        while not self.ap_if.active():
            sleep_ms(WAIT_FOR_AP)

        self.ap_if.ifconfig((AP_IP, "255.255.255.0", AP_IP, AP_IP))
        self.ap_if.config(essid=PUBLIC_NAME, authmode=AUTH_OPEN)

        print(
            "> AP mode configured: {} ".format(PUBLIC_NAME.decode("utf-8")),
            self.ap_if.ifconfig(),
        )
