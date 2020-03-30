import urequests
from machine import RTC
import network
import ntptime
import uasyncio as asyncio


class Time:
    _offset_hour = 0
    _offset_minute = 0

    def __init__(self, loop, wifiManager):
        self.loop = loop
        self._wifiManager = wifiManager

        self.loop.create_task(self._waitForStation())

    async def _waitForStation(self):
        await asyncio.sleep(4)

        while not self._wifiManager.isConnectedToStation():
            await asyncio.sleep(2)

        self.loop.create_task(self._getOffset())
        self.loop.create_task(self._updateTime())

    async def _getOffset(self):
        while True:
            if self._wifiManager.isConnectedToStation():
                offset = urequests.get("http://worldtimeapi.org/api/ip").json()[
                    "utc_offset"
                ]

                self._offset_hour = int(offset[1:3])
                self._offset_minute = int(offset[4:6])

                if offset[:1] == "-":
                    self._offset_hour = -self._offset_hour

                await asyncio.sleep(3600)
            else:
                await asyncio.sleep(60)

    async def _updateTime(self):
        while True:
            try:
                ntptime.settime()
                await asyncio.sleep(300)
            except Exception as e:
                print("> Update time exception: {}".format(e))
                await asyncio.sleep(30)

    def getTime(self):
        _, _, _, _, hour, minute, second, _ = RTC().datetime()

        hour += self._offset_hour
        minute += self._offset_minute

        if minute > 60:
            hour += 1
            minute -= 60

        if hour > 23:
            hour -= 24

        if hour < 0:
            hour += 24

        hour1 = int(hour / 10)
        hour2 = hour % 10
        minute1 = int(minute / 10)
        minute2 = minute % 10
        second1 = int(second / 10)
        second2 = second % 10

        return hour1, hour2, minute1, minute2, second1, second2
