"""End-to-end: three Curta ticks with `_Walk`'s two evaluation sites
replaced by a PATH EVALUATION (constants once per piece, moving cone per
sample), everything else untouched. Prints the tick times and the whole
committed snapshot so it can be diffed against the unpatched run.

    python endtoend_curta.py [patched|plain] [ticks]
"""
import json
import math
import operator
import sys
from time import perf_counter

from solid_node import math as degree_math
from solid_node.expression_graph import postorder
from solid_node.scad_expression import as_node
import solid_node.simulation.program as P
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

MODE = sys.argv[1] if len(sys.argv) > 1 else 'patched'
PORTS_CACHED = 'ports' in MODE
import os as _os
NOSTRUCT = bool(_os.environ.get('NOSTRUCT'))
TICKS = int(sys.argv[2]) if len(sys.argv) > 2 else 3

OPERATORS = {'+': operator.add, '-': operator.sub, '*': operator.mul,
             '/': operator.truediv, '%': math.fmod, '^': operator.pow,
             '<': operator.lt, '<=': operator.le, '>': operator.gt,
             '>=': operator.ge, '==': operator.eq, '!=': operator.ne}

STRUCTURE = {}      # (id(root), frozenset(moving)) -> (order, varies)
BUILDS = [0]
SAMPLES = [0]


def _apply(node, args, inputs):
    if node.kind == 'num':
        return float(node.text)
    if node.kind == 'name':
        return float(inputs[node.text])
    if node.kind == 'binop':
        return OPERATORS[node.op](*args)
    if node.kind == 'unary':
        return -args[0] if node.op == '-' else +args[0]
    return getattr(degree_math, node.op)(*args)


class PathEvaluation:
    __slots__ = ('root', 'order', 'constant')

    def __init__(self, root, fixed, moving):
        BUILDS[0] += 1
        self.root = root
        key = (id(root), frozenset(moving))
        found = None if NOSTRUCT else STRUCTURE.get(key)
        if found is None:
            order = list(postorder([root]))
            varies = {}
            for node in order:
                if node.kind == 'name':
                    varies[node] = node.text in moving
                elif not node.children:
                    varies[node] = False
                else:
                    varies[node] = any(varies[c] for c in node.children)
            found = (order, varies, [n for n in order if varies[n]])
            if not NOSTRUCT:
                STRUCTURE[key] = found
        order, varies, self.order = found
        constant = {}
        for node in order:
            if varies[node]:
                continue
            constant[node] = _apply(
                node, [constant[c] for c in node.children], fixed)
        self.constant = constant

    def at(self, inputs):
        SAMPLES[0] += 1
        if not self.order:
            return self.constant[self.root]
        values = dict(self.constant)
        for node in self.order:
            values[node] = _apply(
                node, [values[c] for c in node.children], inputs)
        return values[self.root]


def _moving(walk):
    names = {name for name, value in walk.delta.items() if value}
    names.discard(walk.own)
    return names


def _key(branches):
    return tuple(sorted(branches.items()))


def patched_skeleton(self, t, branches):
    cache = _SK.setdefault(self, {})
    key = _key(branches)
    path = cache.get(key)
    values = P._along(self.start, self.delta, t)
    values.update(branches)
    if path is None:
        path = PathEvaluation(as_node(self.plan.skeleton), values,
                              _moving(self))
        cache[key] = path
    return path.at(values)


def patched_level(self, jump, t, own_value, branches):
    cache = _LV.setdefault(self, {})
    key = (id(jump), _key(branches))
    path = cache.get(key)
    if path is None:
        values = P._along(self.start, self.delta, t)
        values[self.own] = own_value
        values.update(branches)
        path = PathEvaluation(as_node(jump.argument), values,
                              _moving(self) | {self.own})
        cache[key] = path
    values = P._along(self.start, self.delta, t)
    values[self.own] = own_value
    values.update(branches)
    try:
        level = path.at(values)
    except ZeroDivisionError:
        raise P._no_level(jump, self.described, self.coordinate) from None
    if jump.primitive in ('floor', 'ceil', '%') and not math.isfinite(level):
        raise P._no_level(jump, self.described, self.coordinate,
                          'a level quantity that is not a finite number')
    return level


_SK = {}
_LV = {}

if 'patched' in MODE:
    P._Walk._skeleton = patched_skeleton
    P._Walk._level = patched_level


def snapshot_of(sim):
    return json.dumps(sim.snapshot(), sort_keys=True, default=str)


import solid_node.motion.ports as _ports
if PORTS_CACHED:
    _raw = _ports.declared_ports
    _CACHE = {}
    def _cached(node_class):
        found = _CACHE.get(node_class)
        if found is None:
            found = _raw(node_class)
            _CACHE[node_class] = found
        return found
    _ports.declared_ports = _cached
    import solid_node.motion.couplings as _c
    for _mod in (_c,):
        try:
            if getattr(_mod, 'declared_ports', None) is _raw:
                _mod.declared_ports = _cached
        except Exception:
            pass
    import sys as _sys
    for _name, _mod in list(_sys.modules.items()):
        if _mod is None or not _name.startswith('solid_node'):
            continue
        try:
            if getattr(_mod, 'declared_ports', None) is _raw:
                _mod.declared_ports = _cached
        except Exception:
            pass
PORT = [0.0, 0]
DEPTH = [0]
_dp = _ports.declared_ports
def _timed(*a, **k):
    if DEPTH[0]:
        return _dp(*a, **k)
    DEPTH[0] = 1
    t0 = perf_counter()
    try:
        return _dp(*a, **k)
    finally:
        PORT[0] += perf_counter() - t0
        PORT[1] += 1
        DEPTH[0] = 0
_ports.declared_ports = _timed

from solid_node.scad_expression import GraphValue as _GV
EV = [0.0, 0]
_ev = _GV.evaluate
def _tev(self, inputs):
    t0 = perf_counter()
    try:
        return _ev(self, inputs)
    finally:
        EV[0] += perf_counter() - t0
        EV[1] += 1
_GV.evaluate = _tev

PATH = [0.0, 0]
_at = PathEvaluation.at
def _tat(self, inputs):
    t0 = perf_counter()
    try:
        return _at(self, inputs)
    finally:
        PATH[0] += perf_counter() - t0
        PATH[1] += 1
PathEvaluation.at = _tat
_bi = PathEvaluation.__init__
BLD = [0.0]
def _tbi(self, *a):
    t0 = perf_counter()
    try:
        return _bi(self, *a)
    finally:
        BLD[0] += perf_counter() - t0
PathEvaluation.__init__ = _tbi

began = perf_counter()
sim = Sim(OperatingCurta(), dt=.1)
print(f'constructed {perf_counter() - began:.3f} s', flush=True)
sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)
PORT[0] = 0.0; PORT[1] = 0; EV[0] = 0.0; EV[1] = 0
PATH[0] = 0.0; PATH[1] = 0; BLD[0] = 0.0

began = perf_counter()
for _ in range(TICKS):
    t0 = perf_counter()
    sim.run(.1)
    print(f'  tick {perf_counter() - t0:.3f} s', flush=True)
total = perf_counter() - began
print(f'{MODE}: {TICKS} ticks {total:.3f} s ({total / TICKS:.3f} s/tick)')
print(f'  GraphValue.evaluate {EV[0]:.3f} s in {EV[1]} calls')
print(f'  PathEvaluation.at  {PATH[0]:.3f} s in {PATH[1]} calls; '
      f'building {BLD[0]:.3f} s')
print(f'  declared_ports     {PORT[0]:.3f} s in {PORT[1]} top-level calls')
print(f'  everything else    {total - EV[0] - PATH[0] - BLD[0] - PORT[0]:.3f} s')
print(f'  path builds {BUILDS[0]}, structures {len(STRUCTURE)}, '
      f'samples {SAMPLES[0]}')
print('SNAPSHOT-SHA', __import__('hashlib').sha256(
    snapshot_of(sim).encode()).hexdigest())
import os
_out = os.environ.get('SNAPDIR')
if _out:
    with open(os.path.join(_out, f'snapshot-{MODE}.json'), 'w') as handle:
        handle.write(snapshot_of(sim))
