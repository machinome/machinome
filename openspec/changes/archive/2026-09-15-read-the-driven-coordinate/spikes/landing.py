"""Spike 3: does `start + rate * t*` land exactly on the surface?

`t* = (surface - start) / rate` is the solved crossing of an affine
level quantity; the segment then commits `start + rate * t*` -- the same
arithmetic `Edge.increments` performs with every delta scaled by `t*`.
If that is not bit-exact the gate re-engages on the next tick and the
wheel takes a whole extra tooth, so the design needs a snap rule.
"""

import json
import math
import random


def landed(start, rate, surface):
    t = (surface - start) / rate
    return start + rate * t, t


def sweep(count, seed):
    random.seed(seed)
    misses = []
    for _ in range(count):
        start = random.uniform(-1000.0, 1000.0)
        rate = random.uniform(-1000.0, 1000.0)
        if rate == 0.0:
            continue
        surface = 360.0 * random.randint(-5, 5)
        value, t = landed(start, rate, surface)
        if not (0.0 <= t <= 1.0):
            continue
        if value != surface:
            misses.append({'start': start, 'rate': rate, 'surface': surface,
                           't': t, 'landed': value,
                           'ulps': round((value - surface)
                                         / math.ulp(surface or 1.0))})
    return misses


def scaled_sweep(count, seed):
    """The same, but with the increment recomputed the way a SEGMENT
    recomputes it: every input's admission multiplied by `t*` and the
    law re-evaluated, rather than the rate multiplied by `t*`.

    `rack_start + rack_delta * t` minus `rack_start`, times the gate's
    ratio -- one multiplication more than the line above, which is where
    a last-bit difference would come from.
    """
    random.seed(seed)
    misses = []
    for _ in range(count):
        start = random.uniform(-1000.0, 1000.0)
        rack = random.uniform(-1000.0, 1000.0)
        delta = random.uniform(-1000.0, 1000.0)
        ratio = random.choice((1.0, -1.0, 0.5, 2.0, 0.1, 3.0))
        if delta == 0.0:
            continue
        rate = ratio * ((rack + delta) - rack)
        if rate == 0.0:
            continue
        surface = 360.0 * random.randint(-5, 5)
        t = (surface - start) / rate
        if not (0.0 <= t <= 1.0):
            continue
        # the segment: scale the admission, re-evaluate the law
        value = start + ratio * ((rack + delta * t) - rack)
        if value != surface:
            misses.append({'start': start, 'rack': rack, 'delta': delta,
                           'ratio': ratio, 'surface': surface, 't': t,
                           'landed': value,
                           'ulps': round((value - surface)
                                         / math.ulp(surface or 1.0))})
    return misses


def re_engages(misses, period=360.0):
    """Of the misses, how many leave the gate `value % period > 0` TRUE
    -- the wheel taking a whole extra tooth."""
    live = 0
    for entry in misses:
        remainder = math.fmod(entry['landed'], period)
        if remainder != 0.0:
            live += 1
    return live


if __name__ == '__main__':
    direct = sweep(200000, 11)
    scaled = scaled_sweep(200000, 13)
    print(json.dumps({
        'direct': {'misses': len(direct),
                   'sample': direct[:5],
                   're_engaging': re_engages(direct)},
        'segment_scaled': {'misses': len(scaled),
                           'sample': scaled[:5],
                           're_engaging': re_engages(scaled)},
    }, indent=2))
