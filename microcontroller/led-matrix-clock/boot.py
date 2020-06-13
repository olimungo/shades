from machine import reset
from esp import sleep_type, osdebug, SLEEP_NONE
from webrepl import start

print("")
print("> Booting...")
print("")

sleep_type(SLEEP_NONE)
osdebug(None)

# webrepl.start()


def rst():
    reset()
