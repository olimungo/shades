import uasyncio as asyncio
import time
from ledsConfig import leds, letters, anglesRight, anglesLeft
import math
import random


class EffectsLibrary:
    def __init__(self, board):
        self.board = board
        self.loop = asyncio.get_event_loop()

    async def glow(self, times):
        for i in range(times):
            self.board.fill(1)

            for i in range(6):
                self.board.brightness(i)
                self.board.show()

                await asyncio.sleep_ms(40)

            time.sleep_ms(500)

            for i in range(3, -1, -1):
                self.board.brightness(i)
                self.board.show()

                await asyncio.sleep_ms(40)

            self.board.fill(0)
            self.board.show()

            await asyncio.sleep_ms(500)

    async def oneByone(self):
        for led in leds:
            self.board.fill(0)
            self.board.pixel(led[0], led[1], 1)
            self.board.show()

            await asyncio.sleep_ms(100)

        await asyncio.sleep_ms(25)

        for i in range(len(leds) - 2, -1, -1):
            led = leds[i]

            self.board.fill(0)
            self.board.pixel(led[0], led[1], 1)
            self.board.show()

            await asyncio.sleep_ms(100)

        self.board.fill(0)
        self.board.show()

    async def inSerie(self):
        for led in leds:
            self.board.pixel(led[0], led[1], 1)
            self.board.show()
            await asyncio.sleep_ms(100)

        await asyncio.sleep_ms(25)

        for i in range(len(leds) - 1, -1, -1):
            led = leds[i]

            self.board.pixel(led[0], led[1], 0)
            self.board.show()
            await asyncio.sleep_ms(100)

    async def byLetter(self):
        for letter in letters:
            for led in letter:
                self.board.pixel(leds[led][0], leds[led][1], 1)

            self.board.show()
            await asyncio.sleep_ms(600)

        await asyncio.sleep_ms(500)

        for i in range(len(letters) - 1, -1, -1):
            letter = letters[i]

            for led in letter:
                self.board.pixel(leds[led][0], leds[led][1], 0)

            self.board.show()
            await asyncio.sleep_ms(600)

    def byAngleRight(self):
        for angle in anglesRight:
            led = leds[angle]
            self.board.pixel(led[0], led[1], 1)

        self.board.show()

    def byAngleLeft(self):
        for angle in anglesLeft:
            led = leds[angle]
            self.board.pixel(led[0], led[1], 1)

        self.board.show()

    async def byAngle(self):
        self.board.fill(0)

        self.byAngleRight()

        await asyncio.sleep(1)

        self.board.fill(0)

        self.byAngleLeft()

        await asyncio.sleep(1)

        for wait in range(5):
            self.board.fill(0)

            self.byAngleRight()

            await asyncio.sleep_ms(300)

            self.board.fill(0)

            self.byAngleLeft()

            await asyncio.sleep_ms(300)

        await asyncio.sleep_ms(300)

        self.board.fill(0)
        self.board.show()

    async def strobe(self):
        self.board.fill(0)
        self.board.show()

        for wait in range(50):
            self.board.fill(0)

            self.byAngleRight()

            await asyncio.sleep_ms(20)

            self.board.fill(0)

            self.byAngleLeft()

            await asyncio.sleep_ms(20)

        self.board.fill(0)
        self.board.show()

    async def turnOn(self, led, duration):
        await asyncio.sleep(duration)

        self.board.pixel(led[0], led[1], 1)
        self.board.show()

    async def blinkLed(self, led, frequency, durationMs):
        start = time.ticks_ms()
        end = start
        state = False

        while time.ticks_add(end, -start) < durationMs:
            self.board.pixel(led[0], led[1], state)
            self.board.show()

            await asyncio.sleep_ms(frequency)
            state = not state
            end = time.ticks_ms()

    async def blink(self, led):
        await self.blinkLed(led, 500, 500)

        await asyncio.sleep(1)

        await self.blinkLed(led, 250, 500)

        await asyncio.sleep(3)

        await self.blinkLed(led, 500, 2000)

        await asyncio.sleep(1)

        await self.blinkLed(led, 30, 300)

        await self.blinkLed(led, 200, 500)

        await asyncio.sleep(1)

        await asyncio.sleep(1)

        await self.blinkLed(led, 30, 300)

        await self.blinkLed(led, 200, 500)

        await asyncio.sleep(1)

        self.board.pixel(led[0], led[1], 0)
        self.board.show()

        duration = math.floor(random.getrandbits(4) / 16 * 30) + 10
        self.loop.create_task(self.turnOn(led, duration))
