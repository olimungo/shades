import time
import d1motor
from machine import I2C, Pin
i2c = I2C(scl=Pin(5), sda=Pin(4))
i2c.scan()

m0 = d1motor.Motor(0, i2c)
m0.brake()

# while True:
#     m0.speed(10000)
#     time.sleep(2)
#     m0.brake()
#     time.sleep(1)
#     m0.speed(-10000)
#     time.sleep(2)
#     m0.brake()
#     time.sleep(1)
