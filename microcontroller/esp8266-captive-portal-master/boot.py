# This file is executed on every boot (including wake-boot from deepsleep)

from esp import osdebug
from uos import dupterm
from machine import reset
from gc import collect
# import webrepl

osdebug(None)

# uos.dupterm(None, 1) # disable REPL on UART(0)
# webrepl.start()
collect()

print("\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...")

def rst():
    reset()
