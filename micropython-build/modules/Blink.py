from machine import Pin
import uasyncio as asyncio


class Blink:
    loop = asyncio.get_event_loop()
    PIN = 2  # D4
    pin = Pin(PIN, Pin.OUT)
    pin.on()

    async def _flash(self, onDelay, offDelay):
        self.pin.off()
        await asyncio.sleep_ms(onDelay)
        self.pin.on()
        await asyncio.sleep_ms(offDelay)

    async def _flash3TimesFast(self):
        await self._flash(100, 200)
        await self._flash(100, 200)
        await self._flash(100, 200)

    async def _flash3TimesSlow(self):
        await self._flash(800, 800)
        await self._flash(800, 800)
        await self._flash(800, 800)

    def flash3TimesFast(self):
        self.loop.create_task(self._flash3TimesFast())

    def flash3TimesSlow(self):
        self.loop.create_task(self._flash3TimesSlow())
