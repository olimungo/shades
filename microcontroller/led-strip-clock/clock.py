from machine import Pin, Timer
import neopixel
from math import floor

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

    def __init__(self, time, color="0000ff"):
        self._time = time
        self._ledsStrip = neopixel.NeoPixel(Pin(Gpio.DATA), LEDS)
        self._clearAll()
        self.setColor(color)

    def _clearAll(self):
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
        updated |= self._setSeconds(self._second, second2)

        if updated:
            self._ledsStrip.write()

        self._hour1 = hour1
        self._hour2 = hour2
        self._minute1 = minute1
        self._minute2 = minute2
        self._second = second2

    def _checkUpdate(self, position, prevVal, newVal):
        if prevVal != newVal:
            start = self._digits[position - 1]

            for i in range (start, start + 7 * 2):
                self._ledsStrip[i] = (0, 0, 0)

            if newVal == 0:
                leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
            elif newVal == 1:
                leds = [4, 5, 12, 13]
            elif newVal == 2:
                leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            elif newVal == 3:
                leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
            elif newVal == 4:
                leds = [0, 1, 4, 5, 6, 7, 12, 13]
            elif newVal == 5:
                leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
            elif newVal == 6:
                leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
            elif newVal == 7:
                leds = [2, 3, 4, 5, 12, 13]
            elif newVal == 8:
                leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            elif newVal == 9:
                leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

            for led in leds:
                self._ledsStrip[led + start] = self._rgb
            
            return True

        return False

    def _setSeconds(self, prevVal, newVal):
        if prevVal != newVal:
            if newVal % 2:
                value = self._rgb
            else:
                value = (0, 0, 0)

            self._ledsStrip[self._dots] = self._ledsStrip[self._dots + 1] = value

            return True

        return False

    def _forceRefresh(self):
        self._hour1 = self._hour2 = self._minute1 = self._minute2 = self._second = -1
        self._tick()

    def _rgbToHsv(self, r, g, b):
        r = float(r)
        g = float(g)
        b = float(b)
        high = max(r, g, b)
        low = min(r, g, b)
        h, s, v = high, high, high

        d = high - low
        s = 0 if high == 0 else d/high

        if high == low:
            h = 0.0
        else:
            h = {
                r: (g - b) / d + (6 if g < b else 0),
                g: (b - r) / d + 2,
                b: (r - g) / d + 4,
            }[high]
            h /= 6

        return h, s, v

    def _hsvToRgb(self, h, s, v):
        i = floor(h*6)
        f = h*6 - i
        p = v * (1-s)
        q = v * (1-f*s)
        t = v * (1-(1-f)*s)

        r, g, b = [
            (v, t, p),
            (q, v, p),
            (p, v, t),
            (p, q, v),
            (t, p, v),
            (v, p, q),
        ][int(i%6)]

        return int(r), int(g), int(b)

    def _hexToRgb(self, h):
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def start(self):
        self._tick()
        self._tickTimer.init(period=250, mode=Timer.PERIODIC, callback=self._tick)

    def stop(self):
        self._tickTimer.deinit()

    def setColor(self, h):
        self._rgb = self._hexToRgb(h)
        r, g, b = self._rgb
        h, s, v = self._rgbToHsv(r, g, b)
        self._hsv = (h, s, v)

        self._forceRefresh()

    def setBrighter(self):
        r, g, b = self._rgb
        hOrig, sOrig, vOrig = self._hsv
        h, s, v = self._rgbToHsv(r, g, b)

        if v < vOrig:
            if h != hOrig:
                s = sOrig
                h = hOrig

            if v > 120:
                step = 50
            elif v > 70:
                step = 30
            elif v > 25:
                step = 10
            else:
                step = 5

            if v + step < vOrig:
                v += step
            else:
                v = vOrig
        else:
            if s - 0.2 > 0:
                s -= 0.2
            else:
                s = 0
                v = 255

        r, g, b = self._hsvToRgb(h, s, v)

        self._rgb = (r, g, b)

        self._forceRefresh()

    def setDarker(self):
        r, g, b = self._rgb
        hOrig, sOrig, vOrig = self._hsv
        h, s, v = self._rgbToHsv(r, g, b)

        if s < sOrig:
            if h != hOrig:
                h = hOrig

            if s + 0.2 < sOrig:
                s += 0.2
            else:
                s = sOrig
        else:
            if v > 120:
                step = 50
            elif v > 70:
                step = 30
            elif v > 25:
                step = 10
            else:
                step = 5

            if v - step > 0:
                v -= step
            else:
                v = 0

        r, g, b = self._hsvToRgb(h, s, v)

        self._rgb = (r, g, b)

        self._forceRefresh()

