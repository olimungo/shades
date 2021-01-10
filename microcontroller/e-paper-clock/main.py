import epaper2in9
from machine import SPI, Pin
import framebuf
from NtpTime import NtpTime
from uasyncio import get_event_loop, sleep

WIDTH = const(128)
HEIGHT = const(296)
CUBE_SIZE = const(12)
CUBE_BORDER = const(2)
COL_DIGITS = [1, 6, 13, 18]
COL_BAR = const(23)
COL_DOTS = const(11)
ROW_DOTS = [3, 5]

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

spi = SPI(1, baudrate=80000000, polarity=0, phase=0)

cs = Pin(15)
dc = Pin(16)
rs = Pin(4, Pin.OUT)
busy = Pin(5, Pin.OUT)

e = epaper2in9.EPD(spi, cs, dc, rs, busy)
e.init()


buf = bytearray(WIDTH * HEIGHT // 8)
fb = framebuf.FrameBuffer(buf, WIDTH, HEIGHT, framebuf.MONO_HLSB)
black = 0
white = 1
fb.fill(white)

e.set_frame_memory(buf, 0, 0, WIDTH, HEIGHT)
e.display_frame()


def cubicbezier(fb, x0, y0, x1, y1, x2, y2, x3, y3, n=20):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1.0 - t) ** 3
        b = 3.0 * t * (1.0 - t) ** 2
        c = 3.0 * t ** 2 * (1.0 - t)
        d = t ** 3

        x = int(a * x0 + b * x1 + c * x2 + d * x3)
        y = int(a * y0 + b * y1 + c * y2 + d * y3)
        pts.append((x, y))

    for i in range(n):
        fb.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], black)


def draw_cube(fb, x, y):
    fb.fill_rect(
        x + CUBE_BORDER,
        y + CUBE_BORDER,
        CUBE_SIZE - CUBE_BORDER,
        CUBE_SIZE - CUBE_BORDER,
        black,
    )


def draw_col(fb, col, value):
    bits = bin(int(hex(value), 16))[2:]
    row = 0

    # Padding
    bits = "{:08d}".format(int(bits))

    for bit_str in bits:
        bit = int(bit_str)

        if bit:
            draw_cube(fb, (row + 1) * CUBE_SIZE, col * CUBE_SIZE)

        row += 1


def draw_digit(fb, start_col, digit):
    col = 0
    values = DIGITS[digit]

    for value in values:
        draw_col(fb, start_col + col, value)
        col += 1


def draw_dots(fb):
    draw_cube(fb, ROW_DOTS[0] * CUBE_SIZE, COL_DOTS * CUBE_SIZE)
    draw_cube(fb, ROW_DOTS[1] * CUBE_SIZE, COL_DOTS * CUBE_SIZE)


def draw_bar(fb, count):
    column = 0

    for i in range(count):
        column = (column << 1) + 1

    for i in range(0, 8 - count):
        column <<= 1

    bits = "{0:08b}".format(column)
    row = 0

    for bit_str in bits:
        bit = int(bit_str)

        if bit:
            draw_cube(fb, (row + 1) * CUBE_SIZE, COL_BAR * CUBE_SIZE)

        row += 1


def draw_time(fb):
    global previous_hour1, previous_hour2, previous_minute2

    hour1, hour2, minute1, minute2, _, _ = ntp_time.get_time()

    if previous_hour1 != hour1 or previous_hour2 != hour2 or previous_minute2 != minute2:
        previous_hour1 = hour1
        previous_hour2 = hour2
        previous_minute2 = minute2

        fb.fill(white)

        draw_digit(fb, COL_DIGITS[0], hour1)
        draw_digit(fb, COL_DIGITS[1], hour2)
        draw_digit(fb, COL_DIGITS[2], minute1)
        draw_digit(fb, COL_DIGITS[3], minute2)
        draw_dots(fb)

        e.set_frame_memory(buf, 0, 0, WIDTH, HEIGHT)
        e.display_frame()


async def main():
    while True:
        draw_time(fb)
        await sleep(1)


# cubicbezier(fb, 128, 0, 50, 50, 100, 100, 128, 296, 20)

previous_hour1 = previous_hour2 = previous_minute2 = -1

ntp_time = NtpTime()
loop = get_event_loop()
loop.create_task(main())
loop.run_forever()
loop.close()

# fb.fill(white)

# draw_digit(fb, COL_DIGITS[0], DIGITS[0])
# draw_digit(fb, COL_DIGITS[1], DIGITS[1])
# draw_digit(fb, COL_DIGITS[2], DIGITS[2])
# draw_digit(fb, COL_DIGITS[3], DIGITS[3])
# draw_dots(fb)

# draw_bar(fb, 8)

# e.set_frame_memory(buf, 0, 0, WIDTH, HEIGHT)
# e.display_frame()
