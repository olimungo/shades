from math import fabs

def rgb_to_hsl(rgb):
    # Make r, g, and b fractions of 1
    r = rgb[0] / 255
    g = rgb[1] / 255
    b = rgb[2] / 255

    # Find greatest and smallest channel values
    cmin = min(r, g, b)
    cmax = max(r, g, b)
    delta = cmax - cmin
    h = 0
    s = 0
    l = 0

    # Calculate hue
    # No difference
    if delta == 0:
        h = 0
    # Red is max
    elif cmax == r:
        h = ((g - b) / delta) % 6
    # Green is max
    elif cmax == g:
        h = (b - r) / delta + 2
    # Blue is max
    else:
        h = (r - g) / delta + 4

    h = round(h * 60)

    # Make negative hues positive behind 360°
    if h < 0:
        h += 360

    # Calculate lightness
    l = (cmax + cmin) / 2

    # Calculate saturation
    if delta == 0:
        s= 0
    else :
        s = delta / (1 - fabs(2 * l - 1))

    # Multiply l and s by 100
    s = round(+(s * 100), 2)
    l = round(+(l * 100), 2)

    return (h, s , l)

def hsl_to_rgb(hsl):
    # Must be fractions of 1
    h = hsl[0]
    s = hsl[1] / 100
    l = hsl[2] / 100

    c = (1 - fabs(2 * l - 1)) * s
    x = c * (1 - fabs((h / 60) % 2 - 1))
    m = l - c / 2
    r = 0
    g = 0
    b = 0

    if 0 <= h and h < 60:
        r = c
        g = x
        b = 0
    elif 60 <= h and h < 120:
        r = x; g = c; b = 0
    elif 120 <= h and h < 180:
        r = 0
        g = c
        b = x
    elif 180 <= h and h < 240:
        r = 0
        g = x
        b = c
    elif 240 <= h and h < 300:
        r = x
        g = 0
        b = c
    elif 300 <= h and h < 360:
        r = c
        g = 0
        b = x

    r = round((r + m) * 255)
    g = round((g + m) * 255)
    b = round((b + m) * 255)

    return (r, g, b)

def hex_to_rgb(hex):
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def darker(rgb):
    h, s, l = rgb_to_hsl(rgb)
    l = round(l - 5) if l - 5 > 1 else 1

    print("darker: {}".format((h, s, l)))

    return hsl_to_rgb((h, s, l))

def brighter(rgb):
    h, s, l = rgb_to_hsl(rgb)
    l = round(l + 5) if l + 5 < 99 else 99

    print("brighter: {}".format((h, s, l)))

    return hsl_to_rgb((h, s, l))
