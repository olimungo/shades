from machine import Pin, SPI
import max7219
import math
import random
import uasyncio as asyncio
from effects import EffectsLibrary
from ledsConfig import leds

MODE_SHOW = 0
MODE_HOTEL = 1
MODE_ON = 2
MODE_OFF = 3

mode = MODE_SHOW
task = None

spi = SPI(1, baudrate=10000000)
board = max7219.Matrix8x8(spi, Pin(15), 1)
effectsLibrary = EffectsLibrary(board)


async def modeHotel():
    global board

    board.fill(1)
    board.brightness(3)
    board.show()

    while True:
        led = math.floor(random.getrandbits(5) / 32 * 20)
        duration = math.floor(random.getrandbits(4) / 16 * 5) + 1

        await effectsLibrary.blink(leds[led])
        await asyncio.sleep(duration)


async def modeShow():
    global board

    while True:
        board.brightness(2)

        await effectsLibrary.oneByone()
        await asyncio.sleep_ms(500)

        await effectsLibrary.inSerie()
        await asyncio.sleep_ms(500)

        await effectsLibrary.byAngle()
        await asyncio.sleep_ms(500)

        await effectsLibrary.byLetter()
        await asyncio.sleep_ms(500)

        await effectsLibrary.glow(3)
        await asyncio.sleep_ms(500)

        board.brightness(3)

        await effectsLibrary.strobe()
        await asyncio.sleep_ms(500)


async def modeOnOff(state):
    global board

    board.fill(state)
    board.show()

    while True:
        await asyncio.sleep_ms(10)


async def mainLoop():
    global loop
    global mode
    global task
    global board

    while True:
        if task == None:
            board.fill(0)
            board.show()

        if mode == MODE_SHOW:
            if task == None:
                task = modeShow()
                loop.create_task(task)
        elif mode == MODE_HOTEL:
            if task == None:
                task = modeHotel()
                loop.create_task(task)
        elif mode == MODE_ON:
            if task == None:
                task = modeOnOff(1)
                loop.create_task(task)
        elif mode == MODE_OFF:
            if task == None:
                task = modeOnOff(0)
                loop.create_task(task)

        await asyncio.sleep_ms(500)

        await asyncio.sleep(1)


async def changeMode():
    global mode
    global task

    while True:
        await asyncio.sleep(2)

        if task != None:
            asyncio.cancel(task)
            task = None

        mode = MODE_ON

        await asyncio.sleep(2)

        if task != None:
            asyncio.cancel(task)
            task = None

        mode = MODE_OFF

loop = asyncio.get_event_loop()
loop.create_task(mainLoop())
loop.run_forever()
loop.close()