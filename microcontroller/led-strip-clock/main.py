from uasyncio import get_event_loop
from mDnsServer import mDnsServer
from WifiManager import WifiManager
from HttpServer import HttpServer
from ClockManager import ClockManager
from settings import readNetId

PUBLIC_NAME = "clock"
netId = readNetId()

routes = {}

wifiManager = WifiManager(PUBLIC_NAME, netId)
mdnsServer = mDnsServer(wifiManager, PUBLIC_NAME, netId)
httpServer = HttpServer("192.168.4.1", routes)
clockManager = ClockManager(wifiManager, httpServer)

loop = get_event_loop()
loop.run_forever()
loop.close()