import epaper2in9
from machine import SPI, Pin
import framebuf

DIGITS = [
    [0xFF, 0x81, 0xFF, 0xFF],  # 0
    [0x04, 0x02, 0xFF, 0xFF],  # 1
    [0xF1, 0xF9, 0x8F, 0x86],  # 2
    [0x89, 0x89, 0xFF, 0xFF],  # 3
    [0x0F, 0x08, 0xF8, 0xFC],  # 4
    [0x8F, 0x8F, 0xF9, 0xF9],  # 5
    [0xFF, 0x88, 0xF8, 0xF8],  # 6
    [0x01, 0x01, 0xFF, 0xFF],  # 7
    [0xFF, 0x89, 0xFF, 0xFF],  # 8
    [0x0F, 0x09, 0xFF, 0xFF],  # 9
]

WIDTH = const(128)
HEIGHT = const(296)
CUBE_SIZE = const(12)
CUBE_BORDER = const(2)
COL_DIGITS = [1, 6, 13, 18]
COL_BAR = const(23)
COL_DOTS = const(11)
ROW_DOTS = [3, 5]
WHITE = const(1)
BLACK = const(0)
CS_PIN = const(15)  # D8 - Orange
DC_PIN = const(0)  # D3 - Green
RST_PIN = const(4)  # D2 - White
BUSY_PIN = const(5)  # D1 - Purple

# D5 - Yellow (CLK)
# D7 - Blue (DIN)
# BROWN (GND)
# Grey (VCC)
# D0 to RST
# RST to push-button


class Display:
    def __init__(self):
        self.set_eco_mode(False)

        self.buf = bytearray(WIDTH * HEIGHT // 8)
        self.fb = framebuf.FrameBuffer(self.buf, WIDTH, HEIGHT, framebuf.MONO_HLSB)

        spi = SPI(1, baudrate=80000000, polarity=0, phase=0)

        self.cs = Pin(CS_PIN)
        self.dc = Pin(DC_PIN)
        self.rst = Pin(RST_PIN, Pin.OUT)
        self.busy = Pin(BUSY_PIN, Pin.OUT)

        self.epd = epaper2in9.EPD(spi, self.cs, self.dc, self.rst, self.busy)
        self.epd.init()

        self.fb.fill(WHITE)
        self.epd.set_frame_memory(self.buf, 0, 0, WIDTH, HEIGHT)
        self.epd.display_frame()

        # Partial updates
        self.epd.set_lut(self.epd.LUT_PARTIAL_UPDATE)

    def draw_cube(self, x, y, color):
        cube_border = CUBE_BORDER

        if color == WHITE:
            cube_border = 0

        self.fb.fill_rect(
            x + CUBE_BORDER,
            y + CUBE_BORDER,
            CUBE_SIZE - cube_border,
            CUBE_SIZE - cube_border,
            color,
        )

    def draw_col(self, col, value):
        bits = bin(int(hex(value), 16))[2:]
        row = 0

        # Padding
        bits = "{:08d}".format(int(bits))

        for bit_str in bits:
            bit = int(bit_str)

            if bit:
                color = BLACK
            else:
                color = WHITE

            self.draw_cube((row + 1) * CUBE_SIZE, col * CUBE_SIZE, color)

            row += 1

    def draw_dots(self, second2, previous_second2):
        if self.eco_mode:
            if not self.dots_drawn:
                self.dots_drawn = True
                self.draw_cube(ROW_DOTS[0] * CUBE_SIZE, COL_DOTS * CUBE_SIZE, BLACK)
                self.draw_cube(ROW_DOTS[1] * CUBE_SIZE, COL_DOTS * CUBE_SIZE, BLACK)

                return True
        else:
            if second2 != previous_second2:
                if second2 % 2:
                    color = WHITE
                else:
                    color = BLACK

                self.draw_cube(ROW_DOTS[0] * CUBE_SIZE, COL_DOTS * CUBE_SIZE, color)
                self.draw_cube(ROW_DOTS[1] * CUBE_SIZE, COL_DOTS * CUBE_SIZE, color)

                return True

        return False

    def draw_bar(self, count, previous_count):
        if self.eco_mode:
            return False

        column = 0

        if count != previous_count:
            for _ in range(count):
                column = (column << 1) + 1

            for _ in range(0, 8 - count):
                column <<= 1

            bits = "{0:08b}".format(column)
            row = 0

            for bit_str in bits:
                bit = int(bit_str)

                if bit:
                    color = BLACK
                else:
                    color = WHITE

                self.draw_cube((row + 1) * CUBE_SIZE, COL_BAR * CUBE_SIZE, color)

                row += 1

            return True

        return False

    def draw_digit(self, start_col, current, previous):
        if current != previous:
            col = 0
            values = DIGITS[current]

            for value in values:
                self.draw_col(start_col + col, value)
                col += 1

            return True

        return False

    def update(self):
        self.epd.reset()

        self.epd.set_frame_memory(self.buf, 0, 0, WIDTH, HEIGHT)
        self.epd.display_frame()

        self.epd.sleep()

    def set_eco_mode(self, value):
        self.eco_mode = bool(value)
        self.dots_drawn = False

    def display_image(self, buf, width, height):
        x = round((WIDTH - width) / 2)
        y = round((HEIGHT - height) / 2)

        # self.epd.clear_frame_memory(b"\xFF")
        # self.epd.display_frame()

        self.epd.reset()

        self.fb.fill(WHITE)
        self.epd.set_frame_memory(self.buf, 0, 0, WIDTH, HEIGHT)
        self.epd.display_frame()

        self.epd.clear_frame_memory(b"\xFF")
        self.epd.set_frame_memory(buf, x, y, width, height)
        self.epd.display_frame()

        self.epd.sleep()