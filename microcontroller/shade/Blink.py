from machine import Pin, Timer


class Blink:
    PIN = 2  # D4
    pin = Pin(PIN, Pin.OUT)
    pin.on()
    timer = Timer(-1)

    def flash(self):
        self.pin.off()

        self.timer.init(
            period=1000, mode=Timer.ONE_SHOT, callback=lambda t: self.pin.on()
        )

