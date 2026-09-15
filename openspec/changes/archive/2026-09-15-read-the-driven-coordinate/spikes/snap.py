"""Spike 3b (WITHDRAWN -- see evidence.md section 3): at a self-read cut,
does the gate READ DISENGAGED after it?

Kept for the record. Its rule B takes the slope of the level from two
evaluations one unit apart and then divides by it, which loses about a
thousand ulps to cancellation, so what its table measures is that
formulation and not "snapping": it decides nothing. The rule the design
adopts -- the coordinate placed at the nearest representable value on the
FAR side of the surface, and the run committing that float -- is measured
in `landing2.py` through the framework's own classes.

Two candidate commit rules, over the window gate the design proposes:

    engaged = modulo(own, period) >= gap        (floor modulo)

    A. SEGMENT: own* = own0 + skeleton(t*) - skeleton(0), t* solved from
       the affine level.
    B. SOLVED: own* = the value that puts the crossing node's level
       exactly on its surface, the level solved for the coordinate.

What matters is not bit-exactness but the BRANCH the next piece reads at
own*: `engaged` must read False, or the wheel takes a whole extra tooth.
"""

import json
import math
import random


def modulo(value, period):
    return value - period * math.floor(value / period)


def engaged(own, period, gap):
    return modulo(own, period) >= gap


def trial(own0, rate, period, q):
    """One crossing: the wheel starts at own0, the tick would carry it to
    own0 + rate, and it meets the surface `q` of the level `own / period`.
    """
    surface = float(q)
    # A: solve t*, evaluate the segment.
    t = (surface * period - own0) / rate
    a = own0 + rate * t
    # B: solve the level for the coordinate. k, m from two evaluations,
    # the way a framework implementation would have to.
    m = 0.0 / period                    # L(0)
    k = 1.0 / period - m                # L(1) - L(0)
    b = (surface - m) / k
    return t, a, b


def sweep(count, seed, gap_ratio):
    random.seed(seed)
    bad_a = bad_b = 0
    total = 0
    worst_a = worst_b = 0.0
    for _ in range(count):
        period = random.choice((360.0, 10.0, 36.0, 11.25, 100.0, 1.0,
                                random.uniform(0.1, 1000.0)))
        gap = period * gap_ratio
        q = random.randint(-30, 30)
        surface = q * period
        own0 = surface - random.uniform(0.001, period * 0.9)
        rate = random.uniform(0.001, 1000.0)
        if own0 + rate < surface:
            continue
        total += 1
        t, a, b = trial(own0, rate, period, q)
        if engaged(a, period, gap):
            bad_a += 1
            worst_a = max(worst_a, abs(a - surface))
        if engaged(b, period, gap):
            bad_b += 1
            worst_b = max(worst_b, abs(b - surface))
    return {'trials': total,
            'A segment still engaged': bad_a,
            'B solved still engaged': bad_b,
            'A worst |own* - surface|': worst_a,
            'B worst |own* - surface|': worst_b}


def knife_edge(count, seed):
    """The same, with the DEGENERATE gate `modulo(own, period) > 0`,
    whose disengaged set is a single point."""
    random.seed(seed)
    bad = 0
    total = 0
    for _ in range(count):
        period = random.choice((360.0, 10.0, 36.0, 11.25))
        q = random.randint(-30, 30)
        surface = q * period
        own0 = surface - random.uniform(0.001, period * 0.9)
        rate = random.uniform(0.001, 1000.0)
        if own0 + rate < surface:
            continue
        total += 1
        t, a, b = trial(own0, rate, period, q)
        if modulo(a, period) > 0:
            bad += 1
    return {'trials': total, 'knife-edge gate still engaged': bad}


if __name__ == '__main__':
    print(json.dumps({
        'window gap = one tenth of the period': sweep(200000, 3, 0.1),
        'window gap = one hundredth of the period': sweep(200000, 5, 0.01),
        'window gap = 1e-9 of the period': sweep(200000, 7, 1e-9),
        'degenerate gate': knife_edge(200000, 9),
    }, indent=2))
