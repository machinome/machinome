"""Baseline for the path-evaluation cycle: for each running fixture,
ticks/s, `GraphValue.evaluate` calls per tick (cycle 1's probe) and the
NODE VISITS per tick that those evaluations actually pay for.

A node visit is one iteration of `GraphValue.evaluate`'s postorder walk:
the unit the interpreter charges by, and the one this cycle reduces
where the evaluation count does not move.

    WT="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
        python <this file> [ROUNDS]
"""
import os
import sys
import time

ROOT = os.environ['WT']
sys.path.insert(0, ROOT)

from solid_node.expression_graph import postorder          # noqa: E402
from solid_node.scad_expression import GraphValue          # noqa: E402
from solid_node.simulation import Sim                      # noqa: E402
from tests.running_project.machine import Clearing, Train   # noqa: E402
from tests.clearing_project.machine import CurtaInterface   # noqa: E402

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SIZES = {}


def counted(run):
    original = GraphValue.evaluate
    tally = [0, 0]

    def counting(self, values):
        node = self._expression_node
        size = SIZES.get(id(node))
        if size is None:
            size = sum(1 for _ in postorder([node]))
            SIZES[id(node)] = size
        tally[0] += 1
        tally[1] += size
        return original(self, values)

    GraphValue.evaluate = counting
    try:
        run()
    finally:
        GraphValue.evaluate = original
    return tally


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
    calls, visits = counted(run)
    times = []
    for _round in range(ROUNDS):
        run, ticks = build()
        began = time.perf_counter()
        run()
        times.append(time.perf_counter() - began)
    best = min(times)
    print(f'{name:16s} ticks {ticks:4d}  best {best * 1000:9.2f} ms  '
          f'{ticks / best:8.1f} ticks/s  '
          f'{calls / ticks:8.1f} evaluations/tick  '
          f'{visits / ticks:10.1f} node visits/tick')


for name, build in (('Train', train), ('Clearing', clearing),
                    ('CurtaInterface', curta)):
    measure(name, build)
