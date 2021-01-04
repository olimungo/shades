from machine import Pin, SPI
import max7219
from EffectsLibrary import Effects
import uasyncio as asyncio
import math
import random
from ledsConfig import leds


class Gpio:
    CS = 15


class SignState:
    DEMO = 0
    HOTEL = 1
    ON = 2
    OFF = 3


class Sign:
    def __init__(self):
        self.state = SignState.DEMO
        self.task = None

        self.spi = SPI(1, baudrate=10000000)
        self.board = max7219.Matrix8x8(self.spi, Pin(Gpio.CS), 1)
        self.effects = Effects(self.board)

        self.loop = asyncio.get_event_loop()

        self.setState()

    def previous(self):
        self.state -= 1

        if self.state < SignState.DEMO:
            self.state = SignState.OFF

        self.setState()

    def next(self):
        self.state += 1

        if self.state > SignState.OFF:
            self.state = SignState.DEMO

        self.setState()

    async def stateHotel(self):
        self.board.fill(1)
        self.board.brightness(3)
        self.board.show()

        while True:
            led = math.floor(random.getrandbits(5) / 32 * 20)
            duration = math.floor(random.getrandbits(4) / 16 * 5) + 1

            await self.effects.blink(leds[led])
            await asyncio.sleep(duration)

    async def stateDemo(self):
        while True:
            self.board.brightness(2)

            await self.effects.oneByone()
            await asyncio.sleep_ms(500)

            await self.effects.inSerie()
            await asyncio.sleep_ms(500)

            await self.effects.byAngle()
            await asyncio.sleep_ms(500)

            await self.effects.byLetter()
            await asyncio.sleep_ms(500)

            await self.effects.glow(3)
            await asyncio.sleep_ms(500)

            self.board.brightness(3)

            await self.effects.strobe()
            await asyncio.sleep_ms(500)

    async def stateOnOff(self, state):
        self.board.fill(state)
        self.board.show()

        while True:
            await asyncio.sleep_ms(10)

    def setState(self):
        if self.task != None:
            self.task.cancel()
            self.task = None

        if self.state == SignState.DEMO:
            self.task = self.loop.create_task(self.stateDemo())
        elif self.state == SignState.HOTEL:
            self.task = self.loop.create_task(self.stateHotel())
        elif self.state == SignState.ON:
            self.task = self.loop.create_task(self.stateOnOff(1))
        elif self.state == SignState.OFF:
            self.task = self.loop.create_task(self.stateOnOff(0))
