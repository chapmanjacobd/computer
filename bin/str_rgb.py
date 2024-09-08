#!/usr/bin/python3
import hashlib
import sys

def string_to_rgb(input_string):
    hash_object = hashlib.md5(input_string.encode())
    hash_hex = hash_object.hexdigest()
    hash_int = int(hash_hex, 16)

    hue = hash_int % 360  # Hue is between 0 and 359
    saturation = 50 + (hash_int // 360) % 50  # Saturation is between 50 and 99
    lightness = 50 + (hash_int // (360 * 50)) % 50  # Lightness is between 50 and 99

    r, g, b = hsl_to_rgb(hue, saturation, lightness)

    return r, g, b

def hsl_to_rgb(h, s, l):
    # Normalize HSL values
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0

    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1/3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1/3)

    # Convert RGB values to integers in the range 0-255
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)

    return r, g, b

rgb_color = string_to_rgb(sys.argv[1])
print('%02x%02x%02x' % rgb_color)
