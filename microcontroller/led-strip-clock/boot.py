from machine import reset, freq
import esp
# import webrepl

print("")
print("> Booting...")
print("")

esp.sleep_type(esp.SLEEP_NONE)
esp.osdebug(None)

freq(160000000)

# webrepl.start()


def rst():
    reset()