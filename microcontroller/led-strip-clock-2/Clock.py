from machine import Pin, Timer
from math import floor
from neopixel import NeoPixel
import colors
import gc

from NtpTime import NtpTime

LEDS = 59
DIGIT = [1, 15, 31, 45]
DOTS = 29
EFFECT_INIT = [(0, 1), (2, 3), (4, 5), (12, 13), (10 ,11), (8 ,9)]

class Gpio:
    DATA = 4 # D2

class Clock:
    hour1 = hour2 = minute1 = minute2 = second = -1
    rgb = None
    hex = None
    tick_timer = Timer(-1)
    play_spinner_timer = Timer(-1)
    effect_to_play = None
    effect_original = None
    stop_effect_init = None
    score_green = 0
    score_red = 0

    def __init__(self, color="0000ff"):
        self.leds_strip = NeoPixel(Pin(Gpio.DATA), LEDS)

        self.time = NtpTime()

        self.clear_all()
        self.set_color(color)

    def clear_all(self):
        for i in range(self.leds_strip.n):
            self.leds_strip[i] = (0, 0, 0)

        self.leds_strip.write()

    def tick(self, timer=None):
        hour1, hour2, minute1, minute2, second1, second2 = self.time.get_time()
        updated = False

        updated |= self.check_update(1, self.hour1, hour1)
        updated |= self.check_update(2, self.hour2, hour2)
        updated |= self.check_update(3, self.minute1, minute1)
        updated |= self.check_update(4, self.minute2, minute2)
        updated |= self.check_update_seconds(self.second, second2)

        if updated:
            self.leds_strip.write()

        self.hour1 = hour1
        self.hour2 = hour2
        self.minute1 = minute1
        self.minute2 = minute2
        self.second = second2

    def check_update(self, position, prevValue, newValue):
        if prevValue != newValue:
            self.update(position, newValue, self.rgb)
            return True

        return False

    def update(self, position, value, rgb):
        start = DIGIT[position - 1]

        for i in range (start, start + 7 * 2):
            self.leds_strip[i] = (0, 0, 0)

        if value == 0:
            leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
        elif value == 1:
            leds = [4, 5, 12, 13]
        elif value == 2:
            leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        elif value == 3:
            leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
        elif value == 4:
            leds = [0, 1, 4, 5, 6, 7, 12, 13]
        elif value == 5:
            leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
        elif value == 6:
            leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 7:
            leds = [2, 3, 4, 5, 12, 13]
        elif value == 8:
            leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 9:
            leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

        for led in leds:
            self.leds_strip[led + start] = rgb

    def check_update_seconds(self, prevValue, newValue):
        if prevValue != newValue:
            if newValue % 2:
                value = self.rgb
            else:
                value = (0, 0, 0)

            self.leds_strip[DOTS] = self.leds_strip[DOTS + 1] = value

            return True

        return False

    def force_refresh(self):
        self.hour1 = self.hour2 = self.minute1 = self.minute2 = self.second = -1
        self.tick()

    def display(self):
        print("> Clock started")
        self.hour1 = self.hour2 = self.minute1 = self.minute2 = self.second = -1
        self.clear_all()
        self.tick()
        self.tick_timer.init(period=250, mode=Timer.PERIODIC, callback=self.tick)

    def stop(self):
        self.tick_timer.deinit()

    def display_scoreboard(self):
        self.update(1, floor(self.score_green / 10), (0, 255, 0))
        self.update(2, self.score_green % 10, (0, 255, 0))
        self.update(3, floor(self.score_red / 10), (255, 0, 0))
        self.update(4, self.score_red % 10, (255, 0, 0))

        self.leds_strip[DOTS] = self.leds_strip[DOTS + 1] = (255, 255, 255)

        self.leds_strip.write()

    def update_scoreboard_green(self, increment):
        if self.score_green + increment >= 0 and self.score_green + increment <= 99:
            self.score_green += increment
            self.display_scoreboard()

    def update_scoreboard_red(self, increment):
        if self.score_red + increment >= 0 and self.score_red + increment <= 99:
            self.score_red += increment
            self.display_scoreboard()

    def reset_scoreboard(self):
        self.score_green = self.score_red = 0
        self.display_scoreboard()

    def set_color(self, hex):
        if isinstance(hex, bytes):
            hex = hex.decode('ascii')

        self.hex = hex
        self.rgb = colors.hex_to_rgb(hex)

        self.force_refresh()

    def set_brighter(self):
        self.rgb = colors.brighter(self.rgb)
        self.hex = colors.rgb_to_hex(self.rgb)
        self.force_refresh()

    def set_darker(self):
        self.rgb = colors.darker(self.rgb)
        self.hex = colors.rgb_to_hex(self.rgb)
        self.force_refresh()

    def play_spinner(self, period, color):
        gc.collect()

        self.effect_original = EFFECT_INIT.copy()
        self.effect_to_play = []
        self.stop_effect_init = False
        self.effect_color = color

        self.clear_all()

        self.play_spinner_timer.init(period=period, mode=Timer.PERIODIC, callback=self.play_spinner_tick)

    def play_spinner_tick(self, timer):
        if self.stop_effect_init:
        
            timer.deinit()
        else:
            if len(self.effect_to_play) == 0:
                self.effect_to_play = self.effect_original.copy()

            currentStep = self.effect_to_play.pop(0)

            for start in DIGIT:
                for i in range (start, start + 7 * 2):
                    self.leds_strip[i] = (0, 0, 0)
                    
                self.leds_strip[start + currentStep[0]] = self.effect_color
                self.leds_strip[start + currentStep[1]] = self.effect_color

            self.leds_strip.write()