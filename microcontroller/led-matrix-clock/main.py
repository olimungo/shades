from machine import Pin, SPI
import uasyncio as asyncio
import max7219
from time import Time
from WifiManager import WifiManager
from smallClock import SmallClock

PUBLIC_NAME = "clock"


spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
board = max7219.Matrix8x8(spi, Pin(15), 4)
board.brightness(0)
board.fill(0)
board.show()

wifiManager = WifiManager(PUBLIC_NAME)
time = Time(wifiManager)
smallClock = SmallClock(board, time)
smallClock.start()

loop = asyncio.get_event_loop()
loop.run_forever()
loop.close()
