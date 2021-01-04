# Useful URLs

-   Github: https://github.com/thomasfredericks/wemos_motor_shield/blob/master/README.md
-   motor-shield bin: https://cdn.hackaday.io/files/18439788894176/motor_shield.bin

:exclamation: Don't forget to bridge the STDBY pad to I2C :exclamation:

# Commands

### Check if shield is connected correctly

```
stm32flash /dev/tty.usbserial-1460
```

### Unlock the shield

```
stm32flash -k /dev/tty.usbserial-1460
```

### Flash the new firmware

```
stm32flash -f -v -w motor_shield.bin /dev/tty.usbserial-1460
```
