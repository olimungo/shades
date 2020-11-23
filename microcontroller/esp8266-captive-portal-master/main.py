import uasyncio as asyncio
import uselect as select

from http import HTTPServer
from captive_portal import CaptivePortal
from credentials import Creds


def login(params):
    ssid = params.get(b"ssid", None)
    password = params.get(b"password", None)

    # Write out credentials
    Creds(ssid=ssid, password=password).write()

    loop.create_task(portal.connect_to_wifi())

    headers = b"HTTP/1.1 200 OK\r\n"

    return b"", headers

async def toto():
    connected = False
    
    while True:
        for response in poller.ipoll(1000):
            sock, event, *others = response
            http_server.handle(sock, event, others)

        if portal.connected and not connected:
            connected = True
            http_server.set_ip(portal.local_ip, portal.creds.ssid)

        await asyncio.sleep_ms(50)

poller = select.poll()
portal = CaptivePortal("Clock-1")
http_server = HTTPServer(poller, portal.local_ip, {b"/": b"./index.html", b"/login": login})
print("Configured HTTP server")

loop = asyncio.get_event_loop()
portal.start()

loop.create_task(toto())


loop.run_forever()
loop.close()
