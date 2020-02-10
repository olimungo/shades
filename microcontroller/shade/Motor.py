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
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1


class MotorState:
    RUNNING_UP = 0
    RUNNING_DOWN = 1
    STOPPED = 2

    STATE_TEXT = ["RUNNING UP", "RUNNING DOWN", "STOPPED"]


class ShadeState:
    TOP = 0
    BOTTOM = 1
    IN_BETWEEN = 2
    UNKNOWN = 3

    STATE_TEXT = ["TOP", "BOTTOM", "IN BETWEEN", "UNKNOWN"]


class MotorManager:
    motorState = MotorState().STOPPED
    shadeState = ShadeState().UNKNOWN
    ctl1 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
    ctl2 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
    irSensor = ADC(Gpio().IR_SENSOR)
    irPower = Pin(Gpio().IR_POWER, Pin.OUT)
    stdbPmwPower = Pin(Gpio().STDBY_PWM_POWER, Pin.OUT)
    irCheckTimer = Timer(-1)
    disableTimer = Timer(-1)
    motorCheckTimer = Timer(-1)
    forceMoving = 0

    def __init__(self):
        motorReversed = settings.readMotorReversed()

        if motorReversed == "0":
            self.ctl1 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)

        self.ctl1.off()
        self.ctl2.off()
        self.stdbPmwPower.off()
        self.irPower.off()

    def _disable(self, timer):
        self.stdbPmwPower.off()
        self.irPower.off()

    def _stop(self):
        self.irCheckTimer.deinit()

        self.motorState = MotorState().STOPPED
        self.ctl1.on()
        self.ctl2.on()

        # Allow the motor to physically stop before cutting the power
        self.disableTimer.init(period=300, mode=Timer.ONE_SHOT, callback=self._disable)

    def _irCheck(self, timer):
        value = self.irSensor.read()

        if value > Gpio().IR_SENSOR_THRESHOLD_HIGH:
            if self.motorState == MotorState().RUNNING_UP:
                self.shadeState = ShadeState().TOP
            else:
                self.shadeState = ShadeState().BOTTOM

            self._stop()

    def _motorCheck(self, timer=0):
        self.irCheckTimer.init(period=50, mode=Timer.PERIODIC, callback=self._irCheck)

    def _moveMotor(self, direction):
        if direction == MotorDirection().CLOCKWISE:
            self.ctl1.on()
            self.ctl2.off()
        else:
            self.ctl1.off()
            self.ctl2.on()

        self.stdbPmwPower.on()
        self.irPower.on()

        if self.shadeState == ShadeState().IN_BETWEEN:
            self._motorCheck()
        else:
            # If shade was on top or on bottom, delay the IR check
            # to give a bit of time to leave the reflective marker
            self.motorCheckTimer.init(
                period=2000, mode=Timer.ONE_SHOT, callback=self._motorCheck
            )

    def reverseMotor(self):
        motorReversed = settings.readMotorReversed()

        if motorReversed == "0":
            self.ctl1 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
        else:
            self.ctl1 = Pin(Gpio().MOTOR_CTL1, Pin.OUT)
            self.ctl2 = Pin(Gpio().MOTOR_CTL2, Pin.OUT)

    def goUp(self):
        if self.shadeState == ShadeState().TOP:
            self.forceMoving = self.forceMoving + 1

            if self.forceMoving == 3:
                self.shadeState = ShadeState().IN_BETWEEN

        if self.shadeState != ShadeState().TOP:
            self.forceMoving = 0
            self._moveMotor(MotorDirection().CLOCKWISE)
            self.motorState = MotorState().RUNNING_UP

    def goDown(self):
        if self.shadeState == ShadeState().BOTTOM:
            self.forceMoving = self.forceMoving + 1

            if self.forceMoving == 3:
                self.shadeState = ShadeState().IN_BETWEEN

        if self.shadeState != ShadeState().BOTTOM:
            self.forceMoving = 0
            self._moveMotor(MotorDirection().COUNTERCLOCKWISE)
            self.motorState = MotorState().RUNNING_DOWN

    def stop(self):
        if self.motorState != MotorState().STOPPED:
            self.forceMoving = 0
            self.shadeState = ShadeState().IN_BETWEEN
            self._stop()

    def getState(self):
        if self.motorState != MotorState().STOPPED:
            state = MotorState().STATE_TEXT[self.motorState]
        else:
            state = ShadeState().STATE_TEXT[self.shadeState]

        return state

