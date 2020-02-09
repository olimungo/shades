from machine import Pin, Timer


class Blink:
    PIN = 2  # D4
    pin = Pin(PIN, Pin.OUT)
    pin.on()

    def __init__(self):
        self.pin.on()

    def __blink(self, period, state):
        timer = Timer(-1)
        timer.init(
            period=period, mode=Timer.ONE_SHOT, callback=lambda t: self.pin.value(state)
        )

    def fast(self):
        self.pin.value(0)

        self.__blink(100, 1)
        self.__blink(300, 0)
        self.__blink(400, 1)
        self.__blink(600, 0)
        self.__blink(700, 1)

    def slow(self):
        self.pin.value(0)

        self.__blink(300, 1)
        self.__blink(600, 0)
        self.__blink(900, 1)
        self.__blink(1200, 0)
        self.__blink(1500, 1)

