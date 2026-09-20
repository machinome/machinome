"""Write digits.svg: the ten digits of a counter drum, as seven-segment
glyphs laid along the drum's unwrapped circumference.

Artwork X is arc length on the drum, so the sheet is exactly one
circumference wide; artwork Y is height along the drum's axis. Digits
are laid out in DECREASING order so that turning the drum forward
(right-handed about its axis) brings the next digit to the reading
post.
"""
import math

RADIUS = 20.0          # the drum's outer radius, mm
HEIGHT = 10.0          # the drum's height, mm
CELL = 2 * math.pi * RADIUS / 10
GLYPH_W, GLYPH_H = 5.0, 7.0
STROKE = 1.1
GAP = 0.25

# Segments of a seven-segment glyph as (x, y, w, h) boxes, y down, in a
# GLYPH_W x GLYPH_H box.
def segments():
    s, g = STROKE, GAP
    half = GLYPH_H / 2
    return {
        'a': (s, 0, GLYPH_W - 2 * s, s),
        'b': (GLYPH_W - s, s + g, s, half - s - 2 * g + s / 2),
        'c': (GLYPH_W - s, half + g + s / 2, s, half - s - 2 * g + s / 2),
        'd': (s, GLYPH_H - s, GLYPH_W - 2 * s, s),
        'e': (0, half + g + s / 2, s, half - s - 2 * g + s / 2),
        'f': (0, s + g, s, half - s - 2 * g + s / 2),
        'g': (s, half - s / 2, GLYPH_W - 2 * s, s),
    }

DIGITS = {
    0: 'abcdef', 1: 'bc', 2: 'abged', 3: 'abgcd', 4: 'fgbc',
    5: 'afgcd', 6: 'afgedc', 7: 'abc', 8: 'abcdefg', 9: 'abcdfg',
}


def rect_path(x, y, w, h):
    return f'M{x:.3f},{y:.3f} h{w:.3f} v{h:.3f} h{-w:.3f} Z'


def svg():
    boxes = segments()
    paths = []
    for digit, lit in DIGITS.items():
        cell = 9 - digit                       # decreasing order
        x0 = cell * CELL + (CELL - GLYPH_W) / 2
        y0 = (HEIGHT - GLYPH_H) / 2
        for name in lit:
            x, y, w, h = boxes[name]
            paths.append(f'  <path d="{rect_path(x0 + x, y0 + y, w, h)}"/>')
    width = 10 * CELL
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width:.3f}mm" height="{HEIGHT:.3f}mm" '
            f'viewBox="0 0 {width:.3f} {HEIGHT:.3f}">\n'
            + '\n'.join(paths) + '\n</svg>\n')


if __name__ == '__main__':
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'digits.svg'), 'w') as f:
        f.write(svg())
    print('wrote digits.svg')
