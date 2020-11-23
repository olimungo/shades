import gc
import network
import ubinascii as binascii
import uselect as select
import uasyncio as asyncio

from dns import DNSServer
from credentials import Creds
    

class CaptivePortal:
    AP_IP = "192.168.4.1"
    AP_OFF_DELAY = const(10 * 1000)
    MAX_CONN_ATTEMPTS = 10

    def __init__(self, essid=None):
        self.connected = False
        self.local_ip = self.AP_IP
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)

        if essid is None:
            essid = b"ESP8266-%s" % binascii.hexlify(self.ap_if.config("mac")[-3:])

        self.essid = essid
        self.creds = Creds()
        self.poller = select.poll()
        self.dns_server = None
        self.conn_time_start = None

        self.loop = asyncio.get_event_loop()

    async def start_access_point(self):
        while not self.ap_if.active():
            print("Waiting for access point to turn on")

            self.ap_if.active(True)
            await asyncio.sleep(1)

        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.local_ip, "255.255.255.0", self.local_ip, self.local_ip)
        )

        self.ap_if.config(essid=self.essid, authmode=network.AUTH_OPEN)
        print("AP mode configured: {} ".format(self.essid), self.ap_if.ifconfig())

        self.loop.create_task(self.captive_portal())

    async def connect_to_wifi(self, autoLoop=False):
        if not self.sta_if.isconnected():
            if self.creds.load().is_valid():
                print(
                    "Trying to connect to SSID '{:s}' with password {:s}".format(
                        self.creds.ssid, self.creds.password
                    )
                )

                # Initiate the connection
                self.sta_if.connect(self.creds.ssid, self.creds.password)

                await asyncio.sleep(8)

            if not self.sta_if.isconnected():
                if not self.ap_if.active():
                    if self.creds.load().is_valid():
                        print(
                            "Failed to connect to {:s} with {:s}. WLAN status={:d}".format(
                                self.creds.ssid, self.creds.password, self.sta_if.status()
                            )
                        )
                    else:
                        print("No valid credentials file: {}".format(Creds.CRED_FILE))

                    self.loop.create_task(self.start_access_point())
                    
                # Retry in 30 secs
                if autoLoop and self.creds.load().is_valid():
                    await asyncio.sleep(30)
                    self.loop.create_task(self.connect_to_wifi(True))
            else:
                self.connected = True
                self.local_ip = self.sta_if.ifconfig()[0]

                print("Connected to {:s} ({:s})".format(self.creds.ssid, self.local_ip))

                # Wait a bit, then stop AP
                await asyncio.sleep(5)
                self.ap_if.active(False)

    async def captive_portal(self):
        print("Starting captive portal")

        if self.dns_server is None:
            self.dns_server = DNSServer(self.poller, self.local_ip)
            print("Configured DNS server")

        try:
            while not self.sta_if.isconnected():
                gc.collect()

                # check for socket events and handle them
                for response in self.poller.ipoll(1000):
                    sock, event, *others = response
                    is_handled = self.handle_dns(sock, event, others)
                    
                    # if not is_handled:
                    #     self.http_server.handle(sock, event, others)

                await asyncio.sleep_ms(50)
        except KeyboardInterrupt:
            print("Captive portal stopped")

        self.cleanup()

    def handle_dns(self, sock, event, others):
        if sock is self.dns_server.sock:
            # ignore UDP socket hangups
            if event == select.POLLHUP:
                return True
                
            self.dns_server.handle(sock, event, others)

            return True

        return False

    def cleanup(self):
        print("Cleaning up")

        if self.dns_server:
            self.dns_server.stop(self.poller)
            self.dns_server = None

        gc.collect()

    def start(self):
        # Turn off station and AP interface to force a reconnect
        self.sta_if.active(False)
        self.ap_if.active(False)
        self.connected = False

        self.sta_if.active(True)

        self.loop.create_task(self.connect_to_wifi())

