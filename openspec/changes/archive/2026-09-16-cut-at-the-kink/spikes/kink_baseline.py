"""Baseline for the kinked-skeleton cycle: ticks/s and GraphValue
evaluations per tick for an AFFINE self-read skeleton against a KINKED
one, repeating the read-the-driven-coordinate evidence.md section 14
probe.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
        python <this file> [ROUNDS]
"""
import os
import sys
import time

ROOT = os.environ['WT']
sys.path.insert(0, ROOT)

from solid_node.scad_expression import GraphValue        # noqa: E402
from solid_node.simulation import Sim                    # noqa: E402
from tests.running_project.machine import Clearing, Train  # noqa: E402
from tests.clearing_project.machine import CurtaInterface  # noqa: E402

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def counted(run):
    original = GraphValue.evaluate
    tally = [0]

    def counting(self, values):
        tally[0] += 1
        return original(self, values)

    GraphValue.evaluate = counting
    try:
        run()
    finally:
        GraphValue.evaluate = original
    return tally[0]


def clearing():
    sim = Sim(Clearing(), 0.1)
    def run():
        sim.move('ring', by=600.0, duration=1.0)
        sim.run(1.0)
    return run, 10


def curta():
    sim = Sim(CurtaInterface(), 1.0 / 60.0)
    def run():
        sim.move('clearing', by=1.0, duration=1.0)
        sim.run(1.0)
    return run, 60


def train():
    sim = Sim(Train(), 0.1)
    sim.rate('crank', 90.0)
    def run():
        sim.run(1.0)
    return run, 10


def measure(name, build):
    run, ticks = build()
    evaluations = counted(run)
    times = []
    for _round in range(ROUNDS):
        run, ticks = build()
        began = time.perf_counter()
        run()
        times.append(time.perf_counter() - began)
    best = min(times)
    print(f'{name:16s} ticks {ticks:4d}  best {best * 1000:9.2f} ms  '
          f'median {sorted(times)[len(times) // 2] * 1000:9.2f} ms  '
          f'{ticks / best:8.1f} ticks/s  '
          f'{evaluations} evaluations = {evaluations / ticks:.1f}/tick')


for name, build in (('Train', train), ('Clearing', clearing),
                    ('CurtaInterface', curta)):
    measure(name, build)
