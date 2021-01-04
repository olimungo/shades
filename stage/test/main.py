import time
import machine, neopixel
import random

LEDS = 2
# LEDS = 59
ledsStrip = None


def set(n, b, g, r):
    ledsStrip[n] = (b, g, r)
    ledsStrip.write()

def clear(n):
        set(n, 0, 0, 0)

def fill(n):
        set(n, 255, 255, 255)

def clearAll():
    for i in range(ledsStrip.n):
        clear(i)

def fillAll():
    for i in range(ledsStrip.n):
        fill(i)

def demo():
    n = ledsStrip.n

    for i in range(1, n, 1):
        r = random.getrandbits(8)
        g = random.getrandbits(8)
        b = random.getrandbits(8)
        ledsStrip[i] = (r, g, b)

        ledsStrip.write()

        time.sleep_ms(20)

    for i in range(n-1, -1, -1):
        ledsStrip[i] = (0, 0, 0)

        ledsStrip.write()

        time.sleep_ms(20)

def setLedsStrip(ledsCount):
    global ledsStrip
    ledsStrip = neopixel.NeoPixel(machine.Pin(4), ledsCount)

def setNumber(position, r, g, b, number):
    digits = [1, 15, 31, 45]
    start = digits[position - 1]

    for i in range (start, start + 7 * 2):
        ledsStrip[i] = (0, 0, 0)

    if number == 0:
        leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
    elif number == 1:
        leds = [4, 5, 12, 13]
    elif number == 2:
        leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    elif number == 3:
        leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
    elif number == 4:
        leds = [0, 1, 4, 5, 6, 7, 12, 13]
    elif number == 5:
        leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
    elif number == 6:
        leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
    elif number == 7:
        leds = [2, 3, 4, 5, 12, 13]
    elif number == 8:
        leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    elif number == 9:
        leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

    for led in leds:
        ledsStrip[led + start] = (r, g, b)

    ledsStrip.write()

def setSeconds():
    dots = 29

    if time.time() % 2:
        value = 255
    else:
        value = 0

    ledsStrip[dots] = (value, value, value)
    ledsStrip[dots + 1] = (value, value, value)

def scrollNumber():
    for number in range(10):
        r = random.getrandbits(8)
        g = random.getrandbits(8)
        b = random.getrandbits(8)
        setNumber(1, r, g, b, number)

        r = random.getrandbits(8)
        g = random.getrandbits(8)
        b = random.getrandbits(8)
        setNumber(2, r, g, b, number)

        r = random.getrandbits(8)
        g = random.getrandbits(8)
        b = random.getrandbits(8)
        setNumber(3, r, g, b, number)

        r = random.getrandbits(8)
        g = random.getrandbits(8)
        b = random.getrandbits(8)
        setNumber(4, r, g, b, number)

        setSeconds()

        time.sleep(1)


setLedsStrip(LEDS)
clearAll()
# fillAll()
# setNumber(1, 255, 0, 0, 1)
# setNumber(2, 0, 255, 0, 2)
# setNumber(3, 0, 0, 255, 3)
# setNumber(4, 255, 255, 0, 4)

#while True:
#    demo(ledsStrip)