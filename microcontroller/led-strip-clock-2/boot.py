from machine import reset, freq
from esp import sleep_type, SLEEP_NONE, osdebug
# import webrepl

osdebug(None)

print("\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...\n")

# freq(160000000)
sleep_type(SLEEP_NONE)

# webrepl.start()

def rst():
    reset()
