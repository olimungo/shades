from machine import reset
import esp
import webrepl

print("")
print("> Booting...")
print("")

esp.sleep_type(esp.SLEEP_NONE)
esp.osdebug(None)

webrepl.start()


def rst():
    reset()
