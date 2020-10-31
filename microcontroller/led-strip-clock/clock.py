from machine import Pin, Timer
from math import floor
import neopixel
import colors

LEDS = 59

class Gpio:
    DATA = 4 # D2

class Clock:
    _digits = [1, 15, 31, 45]
    _dots = 29
    _hour1 = _hour2 = _minute1 = _minute2 = _second = -1
    _rgb = None
    _hsv = None
    _tickTimer = Timer(-1)
    _digits = [1, 15, 31, 45]
    _effectInit = [(0, 1), (2, 3), (4, 5), (12, 13), (10 ,11), (8 ,9)]
    _effectToPlay = None
    _effectOriginal = None
    stopEffectInit = None
    scoreGreen = 0
    scoreRed = 0

    def __init__(self, time, color="0000ff"):
        self._time = time
        self._ledsStrip = neopixel.NeoPixel(Pin(Gpio.DATA), LEDS)
        self.clearAll()
        self.setColor(color)

    def clearAll(self):
        for i in range(self._ledsStrip.n):
            self._ledsStrip[i] = (0, 0, 0)

        self._ledsStrip.write()

    def _tick(self, timer=None):
        hour1, hour2, minute1, minute2, second1, second2 = self._time.getTime()
        updated = False

        updated |= self._checkUpdate(1, self._hour1, hour1)
        updated |= self._checkUpdate(2, self._hour2, hour2)
        updated |= self._checkUpdate(3, self._minute1, minute1)
        updated |= self._checkUpdate(4, self._minute2, minute2)
        updated |= self._checkUpdateSeconds(self._second, second2)

        if updated:
            self._ledsStrip.write()

        self._hour1 = hour1
        self._hour2 = hour2
        self._minute1 = minute1
        self._minute2 = minute2
        self._second = second2

    def _checkUpdate(self, position, prevValue, newValue):
        if prevValue != newValue:
            self._update(position, newValue, self._rgb)
            return True

        return False

    def _update(self, position, value, rgb):
        start = self._digits[position - 1]

        for i in range (start, start + 7 * 2):
            self._ledsStrip[i] = (0, 0, 0)

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
            self._ledsStrip[led + start] = rgb
            

    def _checkUpdateSeconds(self, prevValue, newValue):
        if prevValue != newValue:
            if newValue % 2:
                value = self._rgb
            else:
                value = (0, 0, 0)

            self._ledsStrip[self._dots] = self._ledsStrip[self._dots + 1] = value

            return True

        return False

    def _forceRefresh(self):
        self._hour1 = self._hour2 = self._minute1 = self._minute2 = self._second = -1
        self._tick()

    def startClock(self):
        self._hour1 = self._hour2 = self._minute1 = self._minute2 = self._second = -1
        self.clearAll()
        self._tick()
        self._tickTimer.init(period=250, mode=Timer.PERIODIC, callback=self._tick)

    def stopClock(self):
        self._tickTimer.deinit()

    def displayScoreboard(self):
        self._update(1, floor(self.scoreGreen / 10), (0, 255, 0))
        self._update(2, self.scoreGreen % 10, (0, 255, 0))
        self._update(3, floor(self.scoreRed / 10), (255, 0, 0))
        self._update(4, self.scoreRed % 10, (255, 0, 0))

        self._ledsStrip[self._dots] = self._ledsStrip[self._dots + 1] = (255, 255, 255)

        self._ledsStrip.write()

    def updateScoreboardGreen(self, increment):
        if self.scoreGreen + increment >= 0 and self.scoreGreen + increment <= 99:
            self.scoreGreen += increment
            self.displayScoreboard()

    def updateScoreboardRed(self, increment):
        if self.scoreRed + increment >= 0 and self.scoreRed + increment <= 99:
            self.scoreRed += increment
            self.displayScoreboard()

    def resetScoreboard(self):
        self.scoreGreen = self.scoreRed = 0
        self.displayScoreboard()

    def setColor(self, h):
        self._rgb = colors.hexToRgb(h)
        r, g, b = self._rgb
        h, s, v = colors.rgbToHsv(r, g, b)
        self._hsv = (h, s, v)

        self._forceRefresh()

    def setBrighter(self):
        self._rgb = colors.brighter(self._rgb, self._hsv)
        self._forceRefresh()

    def setDarker(self):
        self._rgb = colors.darker(self._rgb, self._hsv)
        self._forceRefresh()

    def playEffectInit(self, period):
        self._effectOriginal = self._effectInit.copy()
        self._effectToPlay = []
        self.stopEffectInit = False

        self.clearAll()

        timer = Timer(-1)
        timer.init(period=period, mode=Timer.PERIODIC, callback=self._tickEffectInit)

    def _tickEffectInit(self, timer):
        if self.stopEffectInit:
            timer.deinit()
        else:
            if len(self._effectToPlay) == 0:
                self._effectToPlay = self._effectOriginal.copy()

            currentStep = self._effectToPlay.pop(0)

            for start in self._digits:
                for i in range (start, start + 7 * 2):
                    self._ledsStrip[i] = (0, 0, 0)
                    
                self._ledsStrip[start + currentStep[0]] = (0, 255, 0)
                self._ledsStrip[start + currentStep[1]] = (0, 255, 0)

            self._ledsStrip.write()

