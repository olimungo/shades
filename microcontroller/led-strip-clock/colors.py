from math import floor

def rgbToHsv(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = high, high, high

    d = high - low
    s = 0 if high == 0 else d/high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, v

def hsvToRgb(h, s, v):
    i = floor(h*6)
    f = h*6 - i
    p = v * (1-s)
    q = v * (1-f*s)
    t = v * (1-(1-f)*s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i%6)]

    return int(r), int(g), int(b)

def hexToRgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def brighter(rgb, hsv):
    r, g, b = rgb
    hOrig, sOrig, vOrig = hsv
    h, s, v = rgbToHsv(r, g, b)

    if v < vOrig:
        if h != hOrig:
            s = sOrig
            h = hOrig

        if v > 120:
            step = 50
        elif v > 70:
            step = 30
        elif v > 25:
            step = 10
        else:
            step = 5

        if v + step < vOrig:
            v += step
        else:
            v = vOrig
    else:
        if s - 0.2 > 0:
            s -= 0.2
        else:
            s = 0
            v = 255

    return hsvToRgb(h, s, v)

def darker(rgb, hsv):
    r, g, b = rgb
    hOrig, sOrig, vOrig = hsv
    h, s, v = rgbToHsv(r, g, b)

    if s < sOrig:
        if h != hOrig:
            h = hOrig

        if s + 0.2 < sOrig:
            s += 0.2
        else:
            s = sOrig
    else:
        if v > 120:
            step = 50
        elif v > 70:
            step = 30
        elif v > 25:
            step = 10
        else:
            step = 5

        if v - step > 0:
            v -= step
        else:
            v = 0

    return hsvToRgb(h, s, v)

def rgb_to_hsl(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = ((high + low) / 2,)*3

    if high == low:
        h = 0.0
        s = 0.0
    else:
        d = high - low
        # l = (high + low) / 2
        s = d / (2 - high - low) if l > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, v

def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return r, g, b