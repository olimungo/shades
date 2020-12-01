from machine import Pin
import uasyncio as asyncio

_ESP_LED = const(2) # D4

class Blink:
    loop = asyncio.get_event_loop()
    pin = Pin(_ESP_LED, Pin.OUT)
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

    async def _flashOnceSlow(self):
        await self._flash(500, 0)

    def flash3TimesFast(self):
        self.loop.create_task(self._flash3TimesFast())

    def flashOnceSlow(self):
        self.loop.create_task(self._flashOnceSlow())
