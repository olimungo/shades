from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
import ubinascii as binascii
import uselect as select
import uasyncio as asyncio

from credentials import Creds
    
AP_IP = "192.168.4.1"
WAIT_FOR_CONNECT = const(8)

class WifiManager:
    def __init__(self, essid=None):
        self.local_ip = AP_IP
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)

        if essid is None:
            essid = b"ESP8266-%s" % binascii.hexlify(self.ap_if.config("mac")[-3:])

        self.essid = essid
        self.creds = Creds()

        # Turn off station and AP interface to force a reconnect
        self.sta_if.active(True)
        self.ap_if.active(False)

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.check_wifi())

    async def start_access_point(self):
        while not self.ap_if.active():
            self.ap_if.active(True)
            await asyncio.sleep(1)

        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.local_ip, "255.255.255.0", self.local_ip, self.local_ip)
        )

        self.ap_if.config(essid=self.essid, authmode=AUTH_OPEN)
        print("> AP mode configured: {} ".format(self.essid.decode("utf-8")), self.ap_if.ifconfig())
            

    async def check_wifi(self):
        while True:
            self.loop.create_task(self.connect(True))

            if self.creds.load().is_valid():
                await asyncio.sleep(WAIT_FOR_CONNECT)

            if not self.sta_if.isconnected():
                self.loop.create_task(self.start_access_point())

                while not self.sta_if.isconnected():
                    await asyncio.sleep(1)

                self.ap_if.active(False)

                while self.sta_if.isconnected():
                    await asyncio.sleep(1)

    async def connect(self, autoLoop=False):
        if not self.sta_if.isconnected():
            if self.creds.load().is_valid():
                print("> Connecting to {:s}/{:s}".format(self.creds.essid, self.creds.password))

                self.sta_if.connect(self.creds.essid, self.creds.password)

                await asyncio.sleep(WAIT_FOR_CONNECT)

                if not self.sta_if.isconnected():
                    print("> Connection failed. WLAN status={:d}".format(self.sta_if.status()))

                    if autoLoop:
                        self.loop.create_task(self.connect(True))
            else:
                print("> No valid credentials file: {}".format(Creds.CRED_FILE))