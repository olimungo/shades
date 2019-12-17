from machine import Pin, ADC, Timer
import settings


class Gpio:
    MOTOR_CTL1 = 13  # D7
    MOTOR_CTL2 = 15  # D8
    IR_SENSOR = 0  # A0 - ADC
    IR_POWER = 5  # D1
    STDBY_PWM_POWER = 4  # D2
    IR_SENSOR_THRESHOLD_HIGH = 150


class MotorDirection:
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 2


class MotorState:
    RUNNING_UP = 1
    RUNNING_DOWN = 2
    STOPPED = 3


class ShadeState:
    TOP = 1
    BOTTOM = 2
    IN_BETWEEN = 3
    UNKNOWN = 4


class MotorManager:
    motorState = MotorState().STOPPED
    shadeState = ShadeState().UNKNOWN
    ctl1 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
    ctl2 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
    irSensor = ADC(Gpio().IR_SENSOR)
    irPower = Pin(Gpio().IR_POWER, Pin.OUT)
    stdbPmwPower = Pin(Gpio().STDBY_PWM_POWER, Pin.OUT)
    irCheckTimer = Timer(-1)

    def __init__(self):
        motorReversed = settings.readMotorReversed()

        if motorReversed == "0":
            self.ctl1 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)

        self.ctl1.off()
        self.ctl2.off()
        self.stdbPmwPower.off()
        self.irPower.off()

    def __disable(self, timer):
        self.stdbPmwPower.off()
        self.irPower.off()

    def __stop(self):
        self.irCheckTimer.deinit()

        self.motorState = MotorState().STOPPED
        self.ctl1.on()
        self.ctl2.on()

        # Allow the motor to physically stop before cutting the power
        timer = Timer(-1)
        timer.init(period=300, mode=Timer.ONE_SHOT, callback=self.__disable)

    def __irCheck(self, timer):
        value = self.irSensor.read()

        if value > Gpio().IR_SENSOR_THRESHOLD_HIGH:
            if self.motorState == MotorState().RUNNING_UP:
                self.shadeState = ShadeState().TOP
            else:
                self.shadeState = ShadeState().BOTTOM

            self.__stop()

    def __motorCheck(self, timer=0):
        self.irCheckTimer.init(period=50, mode=Timer.PERIODIC, callback=self.__irCheck)

    def __moveMotor(self, direction):
        if direction == MotorDirection().CLOCKWISE:
            self.ctl1.on()
            self.ctl2.off()
        else:
            self.ctl1.off()
            self.ctl2.on()

        self.stdbPmwPower.on()
        self.irPower.on()

        if self.shadeState == ShadeState().IN_BETWEEN:
            self.__motorCheck()
        else:
            # If shade was on top or on bottom, delay the IR check
            # to give a bit of time to leave the reflective marker
            timer = Timer(-1)
            timer.init(period=500, mode=Timer.ONE_SHOT, callback=self.__motorCheck)

    def reverseMotor(self):
        motorReversed = settings.readMotorReversed()

        if motorReversed == "0":
            self.ctl1 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
        else:
            self.ctl1 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)

    def goUp(self):
        if self.shadeState != ShadeState().TOP:
            self.__moveMotor(MotorDirection().CLOCKWISE)
            self.motorState = MotorState().RUNNING_UP

    def goDown(self):
        if self.shadeState != ShadeState().BOTTOM:
            self.__moveMotor(MotorDirection().COUNTERCLOCKWISE)
            self.motorState = MotorState().RUNNING_DOWN

    def stop(self):
        if self.motorState != MotorState().STOPPED:
            self.shadeState = ShadeState().IN_BETWEEN
            self.__stop()

