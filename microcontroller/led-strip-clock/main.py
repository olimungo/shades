from uasyncio import get_event_loop
from mDnsServer import mDnsServer
from WifiManager import WifiManager
from WebServer import WebServer
from ClockManager import ClockManager
from settings import readNetId

PUBLIC_NAME = "clock"

netId = readNetId()

wifiManager = WifiManager(PUBLIC_NAME, netId)
mdnsServer = mDnsServer(wifiManager, PUBLIC_NAME, netId)
webServer = WebServer(wifiManager)
clockManager = ClockManager(wifiManager, webServer)

loop = get_event_loop()
loop.run_forever()
loop.close()