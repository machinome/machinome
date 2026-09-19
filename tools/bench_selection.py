# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What a BLOCK costs per tick, against the machine that has none.

OpenSpec change ``select-the-source``, design.md section 10. Four
measurements, plus the honest baseline:

- ``Train``, the CONTROL: a program with no block at all, whose measured
  ``1.05 ms/tick`` in ``docs/architecture.md`` this change must leave
  alone.
- ``FixedZero``, the reduced fixture's members run as three SEPARATE
  edges with the carriage frozen -- the machine the originating project
  can build today, and therefore what a block has to be compared to.
- ``ShiftedCarry``, the same three laws with the carriage LIVE: one
  block of two members, ordered once per piece.
- ``RangedBlock``, the ONE tick that drives a block coordinate into its
  declared range, which pays the searched localization: a block's give is
  never affine, so `Run._locate` samples and bisects the whole block.
- ``ShiftedCarry`` again over the tick in which the carriage crosses a
  detent, which is the one tick with two pieces.

Run from the framework worktree root, ONE job at a time:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
      PYTHONPATH="$PWD" python tools/bench_selection.py [ROUNDS]
"""

import os
import sys
import time

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, ROOT)

from machinome.simulation import Sim  # noqa: E402

from tests.carriage_project.machine import (  # noqa: E402
    CurtaCarriage, FixedZero, RangedBlock, ShiftedCarry,
)
from tests.running_project.machine import Train  # noqa: E402


DT = 0.02
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def train():
    sim = Sim(Train(), DT)
    sim.move('crank', by=360.0, duration=1.0)
    return sim, 50


def frozen():
    sim = Sim(FixedZero(), DT)
    sim.move('crank', by=360.0, duration=1.0)
    return sim, 50


def selected():
    sim = Sim(ShiftedCarry(), DT)
    sim.move('crank', by=360.0, duration=1.0)
    return sim, 50


def ranged():
    """The one tick that drives a block coordinate INTO its declared
    range: `Run._locate` takes the SEARCHED path, because a block's give
    is never affine, and every sample re-locates the whole block."""
    sim = Sim(RangedBlock(), DT, state={'shift': 1.0})
    sim.move('crank', by=2.0, duration=DT)
    return sim, 1


def detent():
    """The one tick in which the carriage crosses its detent: the
    selector cuts the stretch and the block runs TWICE."""
    sim = Sim(ShiftedCarry(), DT)
    sim.move('crank', by=360.0, duration=1.0)
    sim.move('shift', by=1.0, duration=DT)
    return sim, 1


def carriage():
    """The Curta-shaped fixture: ONE block of seven members, four dials
    and three levers, every association a pair of comparisons on the
    carriage's own joint coordinate."""
    sim = Sim(CurtaCarriage(), DT)
    sim.move('crank', by=360.0, duration=1.0)
    return sim, 20


BENCHES = (
    ('Train (the control, no block)', train),
    ('FixedZero (the frozen twin: three separate edges)', frozen),
    ('ShiftedCarry (one block of two, no crossing)', selected),
    ('RangedBlock (a range on a block coordinate)', ranged),
    ('ShiftedCarry, the tick that crosses the detent', detent),
    ('CurtaCarriage (one block of seven)', carriage),
)


def measure(build):
    best = None
    for _round in range(ROUNDS):
        sim, ticks = build()
        start = time.perf_counter()
        for _tick in range(ticks):
            sim.run(DT)
        elapsed = (time.perf_counter() - start) / ticks * 1000.0
        best = elapsed if best is None else min(best, elapsed)
    return best


def main():
    print(f'dt = {DT}, best of {ROUNDS}')
    for label, build in BENCHES:
        print(f'  {label}: {measure(build):.3f} ms/tick')


if __name__ == '__main__':
    main()
