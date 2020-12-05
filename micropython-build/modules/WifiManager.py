from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from ubinascii import hexlify
from uasyncio import get_event_loop, sleep_ms
from Blink import Blink

from Credentials import Credentials, FILE
    
AP_IP = "192.168.4.1"
WAIT_FOR_CONNECT = const(6000)
WAIT_BEFORE_RECONNECT = const(10000)
WAIT_BEFORE_AP_SHUTDOWN = const(10000)
CHECK_CONNECTED = const(250)

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
            
    async def check_wifi(self):
        while True:
            self.loop.create_task(self.connect(True))

            if self.credentials.load().is_valid():
                await sleep_ms(WAIT_FOR_CONNECT)

            if not self.sta_if.isconnected():
                self.loop.create_task(self.start_access_point())

            while not self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = self.sta_if.ifconfig()[0]

            Blink().flash3TimesFast()
            
            print("> Connected to {} with IP: {}".format(self.credentials.essid.decode('ascii'), self.ip))

            if self.ap_if.active():
                # Leave a bit of time so the client can retrieve the Wifi IP address
                await sleep_ms(WAIT_BEFORE_AP_SHUTDOWN)

                print("> Shuting down AP")
                self.ap_if.active(False)

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    async def start_access_point(self):
        self.ap_if.active(True)
        
        while not self.ap_if.active():
            await sleep_ms(CHECK_CONNECTED)

        self.ip = AP_IP

        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.ip, "255.255.255.0", self.ip, self.ip)
        )

        self.ap_if.config(essid=self.ap_essid, authmode=AUTH_OPEN)
        print("> AP mode configured: {} ".format(self.ap_essid.decode("utf-8")), self.ap_if.ifconfig())

    async def connect(self, autoLoop=False):
        if not self.sta_if.isconnected() or not autoLoop:
            if self.credentials.load().is_valid():
                print("> Connecting to {:s}/{:s}".format(self.credentials.essid, self.credentials.password))

                self.sta_if.active(False)
                self.sta_if.active(True)

                self.sta_if.connect(self.credentials.essid, self.credentials.password)

                await sleep_ms(WAIT_FOR_CONNECT)

                if not self.sta_if.isconnected():
                    if autoLoop:
                        await sleep_ms(WAIT_BEFORE_RECONNECT)
                        self.loop.create_task(self.connect(True))
            else:
                print("> No valid credentials file: {}".format(FILE))