from urequests import get
from machine import RTC
from ntptime import settime
from uasyncio import get_event_loop, sleep
from network import WLAN, STA_IF


class NtpTime:
    offset_hour = 0
    offset_minute = 0

    def __init__(self):
        self.sta_if = WLAN(STA_IF)

        self.loop = get_event_loop()
        self.loop.create_task(self.wait_for_station())

    async def wait_for_station(self):
        await sleep(5)

        while not self.sta_if.isconnected():
            await sleep(2)

        self.loop.create_task(self.get_offset())
        self.loop.create_task(self.update_time())

    async def get_offset(self):
        while True:
            while not self.sta_if.isconnected():
                await sleep(1)

            while self.sta_if.isconnected():
                try:
                    worldtime = get("http://worldtimeapi.org/api/ip")
                    worldtime_json = worldtime.json()
                    offset = worldtime_json["utc_offset"]

                    self.offset_hour = int(offset[1:3])
                    self.offset_minute = int(offset[4:6])

                    if offset[:1] == "-":
                        self.offset_hour = -self.offset_hour

                    # Wait an hour before updating again
                    await sleep(3600)
                except Exception as e:
                    print("> NtpTime.get_offset error: {}".format(e))
                    await sleep(15)

    async def update_time(self):
        while True:
            try:
                settime()
                print("> NTP time updated at {}".format(RTC().datetime()))

                # Wait 5 minutes before updating again
                await sleep(300)
            except Exception as e:
                print("> NtpTime.update_time error: {}".format(e))
                await sleep(15)

    def get_time(self):
        _, _, _, _, hour, minute, second, _ = RTC().datetime()

        hour += self.offset_hour
        minute += self.offset_minute

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
