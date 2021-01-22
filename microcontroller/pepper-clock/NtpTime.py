from urequests import get
from machine import RTC
from ntptime import settime
from Settings import Settings


class NtpTime:
    def __init__(self):
        self.settings = Settings().load()

    def get_offset(self):
        try:
            worldtime = get("http://worldtimeapi.org/api/ip")
            # worldtime = get("https://timezoneapi.io/api/ip/?token=aWrIAGYXyzAbKptqjmKU")

            worldtime_json = worldtime.json()
            offset = worldtime_json["utc_offset"]
            # offset = worldtime_json["data"]["datetime"]["offset_gmt"]

            offset_hour = int(offset[1:3])
            offset_minute = int(offset[4:6])

            if offset[:1] == "-":
                offset_hour = -offset_hour

            self.settings.offset_hour = b"%s" % offset_hour
            self.settings.offset_minute = b"%s" % offset_minute
            self.settings.write()

            print(
                "> Timezone offset: {}h{}m".format(offset_hour, offset_minute)
            )

            return True
        except Exception as e:
            print("> NtpTime.get_offset error: {}".format(e))

            return False

    def update_time(self):
        try:
            settime()
            print("> NTP time updated at {}".format(RTC().datetime()))

            return True
        except Exception as e:
            print("> NtpTime.update_time error: {}".format(e))
            return False

    def get_time(self):
        _, _, _, _, hour, minute, second, _ = RTC().datetime()

        hour += int(self.settings.offset_hour.decode("ascii"))
        minute += int(self.settings.offset_minute.decode("ascii"))

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
