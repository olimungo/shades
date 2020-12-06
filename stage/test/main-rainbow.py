# from uasyncio import get_event_loop
# from mDnsServer import mDnsServer
# from WifiManager import WifiManager
# from WebServer import WebServer
# from ClockManager import ClockManager
# from settings import readNetId

###################
import machine, neopixel
import random
import time
###################

PUBLIC_NAME = "clock"

#netId = readNetId()

#wifiManager = WifiManager(PUBLIC_NAME, netId)
#mdnsServer = mDnsServer(wifiManager, PUBLIC_NAME, netId)
#webServer = WebServer(wifiManager)
#clockManager = ClockManager(wifiManager, webServer)

##########
LEDS = 123
ledsStrip = None
heat = []

def setLedsStrip(ledsCount):
    global ledsStrip, heat

    ledsStrip = neopixel.NeoPixel(machine.Pin(4), ledsCount)
    heat = [0 for _ in range(ledsCount)]

def clearAll():
    for i in range(ledsStrip.n):
        ledsStrip[i] = (0, 0, 0)

    ledsStrip.write()

def fillAll(r, g, b):
    for i in range(ledsStrip.n):
        ledsStrip[i] = (r, g, b)
        
    ledsStrip.write()

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

def showStrip():
    ledsStrip.write()

def setPixel(pixel, red, green, blue):
    ledsStrip[pixel]= (red, green, blue)

def setAll(red, green, blue):
    for i in range(ledsStrip.n):
        setPixel(i, red, green, blue)

    showStrip()

def RGBLoop():
    for j in range(3):
        # Fade IN
        for k in range(0, 50, 3):
            if j == 0: fillAll(k, 0, 0)
            elif j == 1: fillAll(0, k, 0)
            else: fillAll(0, 0, k)

        time.sleep_ms(300)

        # Fade OUT
        for k in range(50, -1, -3):
            if j == 0: fillAll(k, 0, 0)
            elif j == 1: fillAll(0, k, 0)
            else: fillAll(0, 0, k)

        clearAll()
        time.sleep_ms(300)

def snowSparkle(red, green, blue, sparkleDelay, speedDelay):
  setAll(red,green,blue)
 
  pixel = int(random.getrandbits(8)/256 * LEDS)
  setPixel(pixel, 0xff, 0xff, 0xff)
  showStrip()
  time.sleep_ms(sparkleDelay)
  setPixel(pixel, red, green, blue)
  showStrip()
  time.sleep_ms(speedDelay)

def rainbowCycle(speedDelay):
  for j in range(0, 256 * 5, 3): # 5 cycles of all colors on wheel
    for i in range(ledsStrip.n):
      r, g, b = wheel(int((i * 256 / ledsStrip.n) + j) & 255)
      ledsStrip[i] = (r, g, b)

    ledsStrip.write()

    time.sleep_ms(speedDelay)

def wheel(wheelPos):
    if wheelPos < 85:
        return wheelPos * 3, 255 - wheelPos * 3, 0
    elif wheelPos < 170:
        wheelPos -= 85
        return 255 - wheelPos * 3, 0, wheelPos * 3
    else:
        wheelPos -= 170
        return 0, wheelPos * 3, 255 - wheelPos * 3

def fire(cooling, sparking):
    global heat

    # Step 1.  Cool down every cell a little
    for i in range(ledsStrip.n):
        maxRandom = (cooling * 10 / ledsStrip.n) + 2
        cooldown = int(random.getrandbits(8) / 256 * maxRandom)
   
        if cooldown > heat[i]:
            heat[i] = 0
        else:
            heat[i] = heat[i] - cooldown
 
    # Step 2.  Heat from each cell drifts 'up' and diffuses a little
    for k in range(ledsStrip.n - 1, 1, -1):
        heat[k] = int((heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3)

    # Step 3.  Randomly ignite new 'sparks' near the bottom
    if random.getrandbits(8) < sparking:
        y = random.getrandbits(3)
        rnd = int(random.getrandbits(7) / 128 * 95) + 100
        heat[y] = (heat[y] + rnd) & 255

    # Step 4.  Convert heat to LED colors
    for j in range(ledsStrip.n):
        setPixelHeatColor(j, heat[j])

    showStrip()

def setPixelHeatColor(pixel, temperature):
    # Scale 'heat' down from 0-255 to 0-191
    t192 = round((temperature / 255) * 191)

    #print(t192)

    # calculate ramp up from
    heatramp = t192 & 0x3F # 0..63
    heatramp <<= 2 # scale up to 0..252


    # figure out which third of the spectrum we're in:
    if t192 > 0x80: # hottest
        setPixel(pixel, 255, 255, heatramp)
    elif t192 > 0x40: # middle
        setPixel(pixel, 255, heatramp, 0)
    else: # coolest
        setPixel(pixel, heatramp, 0, 0)

def shoot():
    while True:
        fire(35, 60)

machine.freq(160000000)
setLedsStrip(LEDS)
clearAll()

#######

# loop = get_event_loop()
# loop.run_forever()
# loop.close()