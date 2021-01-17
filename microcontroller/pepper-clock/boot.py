from machine import reset, freq, reset_cause
from esp import sleep_type, SLEEP_NONE, osdebug
import webrepl

osdebug(None)

print("\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...\n")

# freq(160000000)
sleep_type(SLEEP_NONE)

print("Reset cause: {}".format(reset_cause()))

webrepl.start()

def rst():
    reset()
