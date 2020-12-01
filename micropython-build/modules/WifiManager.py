from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from ubinascii import hexlify
from uasyncio import get_event_loop, sleep
from Blink import Blink

from Credentials import Credentials, FILE
    
AP_IP = "192.168.4.1"
WAIT_FOR_CONNECT = const(6)
WAIT_FOR_RECONNECT = const(10)

class WifiManager:
    ip = "0.0.0.0"

    def __init__(self, ap_essid=None):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)

        if ap_essid is None:
            ap_essid = b"ESP8266-%s" % hexlify(self.ap_if.config("mac")[-3:])

        self.ap_essid = ap_essid
        self.credentials = Credentials()

        # Turn off station and AP interface to force a reconnect
        self.sta_if.active(True)
        self.ap_if.active(False)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())

    async def start_access_point(self):
        while not self.ap_if.active():
            self.ap_if.active(True)
            await sleep(1)

        self.ip = AP_IP

        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.ip, "255.255.255.0", self.ip, self.ip)
        )

        self.ap_if.config(essid=self.ap_essid, authmode=AUTH_OPEN)
        print("> AP mode configured: {} ".format(self.ap_essid.decode("utf-8")), self.ap_if.ifconfig())
            
    async def check_wifi(self):
        while True:
            self.loop.create_task(self.connect(True))

            if self.credentials.load().is_valid():
                await sleep(WAIT_FOR_CONNECT)

            if not self.sta_if.isconnected():
                self.loop.create_task(self.start_access_point())

            while not self.sta_if.isconnected():
                await sleep(2)

            self.ip = self.sta_if.ifconfig()[0]

            Blink().flash3TimesFast()
            
            print("> Connected to {} with IP: {}".format(self.credentials.essid.decode('ascii'), self.ip))

            if self.ap_if.active():
                # Leave a bit of time so the client can retrieve the Wifi IP address
                await sleep(10)

                print("> Shuting down AP")
                self.ap_if.active(False)

            while self.sta_if.isconnected():
                await sleep(1)

    async def connect(self, autoLoop=False):
        if not self.sta_if.isconnected() or not autoLoop:
            if self.credentials.load().is_valid():
                print("> Connecting to {:s}/{:s}".format(self.credentials.essid, self.credentials.password))

                self.sta_if.connect(self.credentials.essid, self.credentials.password)

                await sleep(WAIT_FOR_CONNECT)

                if not self.sta_if.isconnected():
                    if autoLoop:
                        await sleep(WAIT_FOR_RECONNECT)
                        self.loop.create_task(self.connect(True))
            else:
                print("> No valid credentials file: {}".format(FILE))