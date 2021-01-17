from machine import Pin, deepsleep, reset_cause
from time import sleep

print(">>>> MAIN <<<<")
print("<<< RESET CAUSE: {}".format(reset_cause()))

pin = Pin(2, Pin.OUT)
pin.off()

sleep(2)

deepsleep(10000)






