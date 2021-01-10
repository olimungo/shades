from machine import Pin, ADC, Timer, I2C
import d1motor
from Settings import Settings

class Gpio:
    I2C_SCL = 5 # D1
    I2C_SDA = 4 # D2
    IR_SENSOR = 0  # A0 - ADC
    IR_POWER = 16  # D0
    STDBY_PWM_POWER = 4  # D2
    IR_SENSOR_THRESHOLD_HIGH = 100

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

class Motor:
    def __init__(self):
        self.settings = Settings().load()
        self.i2c = I2C(scl=Pin(Gpio().I2C_SCL), sda=Pin(Gpio().I2C_SDA))
        self.motor_state = MotorState().STOPPED
        self.shade_state = ShadeState().UNKNOWN
        self.ir_sensor = ADC(Gpio().IR_SENSOR)
        self.ir_power = Pin(Gpio().IR_POWER, Pin.OUT)
        self.motor = d1motor.Motor(0, self.i2c)
        self.ir_check_timer = Timer(-1)
        self.motor_check_timer = Timer(-1)
        self.force_moving = 0
        self.stopped_by_ir_sensor = False
        self.speed = 10000 

        if self.settings.motor_reversed == b"1":
            self.speed = -10000

        self.motor.brake()
        self.ir_power.off()

    def disable(self, timer):
        self.ir_power.off()

    def brake(self):
        self.ir_check_timer.deinit()
        self.motor_state = MotorState().STOPPED
        self.motor.brake()

    def ir_check(self, timer):
        value = self.ir_sensor.read()

        # print("IR SENSOR : {}".format(value))

        if value > Gpio().IR_SENSOR_THRESHOLD_HIGH:
            if self.motor_state == MotorState().RUNNING_UP:
                self.shade_state = ShadeState().TOP
            else:
                self.shade_state = ShadeState().BOTTOM

            self.stopped_by_ir_sensor = True

            self.brake()

    def motor_check(self, timer=0):
        self.ir_check_timer.init(period=50, mode=Timer.PERIODIC, callback=self.ir_check)

    def move_motor(self, direction):
        if direction == MotorDirection().CLOCKWISE:
            self.motor.speed(self.speed)
        else:
            self.motor.speed(-self.speed)

        self.ir_power.on()

        if self.shade_state == ShadeState().IN_BETWEEN:
            self.motor_check()
        else:
            # If shade was on top or on bottom, delay the IR check
            # to allow to leave the reflective marker
            self.motor_check_timer.init(
                period=2000, mode=Timer.ONE_SHOT, callback=self.motor_check
            )

    def reverse_direction(self):
        if self.settings.load().motor_reversed == b"1":
            self.speed = -10000
        else:
            self.speed = 10000

    def go_up(self):
        if self.shade_state == ShadeState().TOP:
            self.force_moving = self.force_moving + 1

            if self.force_moving == 3:
                self.shade_state = ShadeState().IN_BETWEEN

        if self.shade_state != ShadeState().TOP:
            self.force_moving = 0
            self.move_motor(MotorDirection().CLOCKWISE)
            self.motor_state = MotorState().RUNNING_UP

    def go_down(self):
        if self.shade_state == ShadeState().BOTTOM:
            self.force_moving = self.force_moving + 1

            if self.force_moving == 3:
                self.shade_state = ShadeState().IN_BETWEEN

        if self.shade_state != ShadeState().BOTTOM:
            self.force_moving = 0
            self.move_motor(MotorDirection().COUNTERCLOCKWISE)
            self.motor_state = MotorState().RUNNING_DOWN

    def stop(self):
        if self.motor_state != MotorState().STOPPED:
            self.force_moving = 0
            self.shade_state = ShadeState().IN_BETWEEN
            self.brake()

    def check_stopped_by_ir_sensor(self):
        if self.stopped_by_ir_sensor:
            self.stopped_by_ir_sensor = False
            return True

        return False

    def get_state(self):
        if self.motor_state != MotorState().STOPPED:
            state = MotorState().STATE_TEXT[self.motor_state]
        else:
            state = ShadeState().STATE_TEXT[self.shade_state]

        return state
