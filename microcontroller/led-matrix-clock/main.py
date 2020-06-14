from uasyncio import get_event_loop
from mDnsServer import mDnsServer
from WifiManager import WifiManager
from WebServer import WebServer
from ClockManager import ClockManager
from settings import readNetId

PUBLIC_NAME = "clock"

netId = readNetId()
publicName = "{}-{}".format(PUBLIC_NAME, netId)

wifiManager = WifiManager(publicName)
mdnsServer = mDnsServer(wifiManager, publicName)
webServer = WebServer(wifiManager)
clockManager = ClockManager(wifiManager, webServer)

loop = get_event_loop()
loop.run_forever()
loop.close()
