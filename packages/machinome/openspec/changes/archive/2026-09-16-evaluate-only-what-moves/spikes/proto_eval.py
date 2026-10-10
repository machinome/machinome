"""Prototype: evaluating a law ALONG A PATH.

Captures the real skeleton/level graphs and inputs of the Curta's searched
crossings, then compares, for the same 64 sample points:

  A  the evaluator as it stands (GraphValue.evaluate per sample)
  B  a path evaluation: the constant frontier computed once, only the
     moving cone walked per sample (same postorder, same operators)
  C  B plus a compiled Python closure for the moving cone

and asserts every sample's float is BIT-IDENTICAL across the three.
"""
import math
import operator
import struct
from time import perf_counter

from solid_node import math as degree_math
from solid_node.expression_graph import postorder
from solid_node.scad_expression import as_node
import solid_node.simulation.program as P
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

OPERATORS = {'+': operator.add, '-': operator.sub, '*': operator.mul,
             '/': operator.truediv, '%': math.fmod, '^': operator.pow,
             '<': operator.lt, '<=': operator.le, '>': operator.gt,
             '>=': operator.ge, '==': operator.eq, '!=': operator.ne}


def plain(root, inputs):
    values = {}
    for node in postorder([root]):
        args = [values[c] for c in node.children]
        if node.kind == 'num':
            value = float(node.text)
        elif node.kind == 'name':
            value = float(inputs[node.text])
        elif node.kind == 'binop':
            value = OPERATORS[node.op](*args)
        elif node.kind == 'unary':
            value = -args[0] if node.op == '-' else +args[0]
        else:
            value = getattr(degree_math, node.op)(*args)
        values[node] = value
    return values[root]


class PathEvaluation:
    """`root` evaluated repeatedly with only `moving` names changing."""

    def __init__(self, root, fixed, moving):
        self.root = root
        order = list(postorder([root]))
        varies = {}
        for node in order:
            if node.kind == 'name':
                varies[node] = node.text in moving
            elif not node.children:
                varies[node] = False
            else:
                varies[node] = any(varies[c] for c in node.children)
        self.constant = {}
        for node in order:
            if varies[node]:
                continue
            args = [self.constant[c] for c in node.children]
            self.constant[node] = self._apply(node, args, fixed)
        self.order = [node for node in order if varies[node]]
        self.total = len(order)

    @staticmethod
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

    def at(self, inputs):
        values = self.constant
        if not self.order:
            return values[self.root]
        values = dict(values)
        for node in self.order:
            values[node] = self._apply(
                node, [values[c] for c in node.children], inputs)
        return values[self.root]


class CompiledPath(PathEvaluation):
    """The moving cone as a Python closure, same operations, same order."""

    def __init__(self, root, fixed, moving):
        super().__init__(root, fixed, moving)
        lines = []
        names = {}
        env = {'_op': OPERATORS, '_m': degree_math, '_k': self.constant}

        def slot(node):
            if node in self.constant:
                key = f'_c{len(names)}'
                if node not in names:
                    names[node] = key
                    env[key] = self.constant[node]
                return names[node]
            return names[node]

        for index, node in enumerate(self.order):
            names[node] = f'_v{index}'
        for node in self.order:
            args = [slot(c) for c in node.children]
            if node.kind == 'name':
                lines.append(f'{names[node]} = float(inputs[{node.text!r}])')
            elif node.kind == 'binop':
                env[f'_f{id(node)}'] = OPERATORS[node.op]
                lines.append(f'{names[node]} = _f{id(node)}({args[0]}, {args[1]})')
            elif node.kind == 'unary':
                lines.append(f'{names[node]} = '
                             + (f'-{args[0]}' if node.op == '-' else f'+{args[0]}'))
            else:
                env[f'_g{id(node)}'] = getattr(degree_math, node.op)
                lines.append(f'{names[node]} = _g{id(node)}({", ".join(args)})')
        body = '\n    '.join(lines) if lines else 'pass'
        source = f'def _run(inputs):\n    {body}\n    return {slot(self.root)}\n'
        exec(compile(source, '<path>', 'exec'), env)
        self._run = env['_run']

    def at(self, inputs):
        return self._run(inputs)


def bits(value):
    return struct.pack('<d', float(value))


# ---- capture real cases -------------------------------------------------
CASES = []
_searched = P._Walk._searched
ARMED = [False]


def watched(self, jump, t, right, own_left, branches, own_at):
    if ARMED[0] and len(CASES) < 40:
        moving = {name for name, value in self.delta.items() if value}
        moving.discard(self.own)
        width = (right - t) / 64.0
        samples = [t + width * step for step in range(65)]
        sk_inputs = []
        for s in samples:
            values = P._along(self.start, self.delta, s)
            values.update(branches)
            sk_inputs.append(values)
        lv_inputs = []
        for s in samples:
            values = P._along(self.start, self.delta, s)
            values[self.own] = own_left
            values.update(branches)
            lv_inputs.append(values)
        CASES.append(('skeleton', as_node(self.plan.skeleton), moving, sk_inputs))
        CASES.append(('level', as_node(jump.argument), moving | {self.own}, lv_inputs))
    return _searched(self, jump, t, right, own_left, branches, own_at)


P._Walk._searched = watched

sim = Sim(OperatingCurta(), dt=.1)
sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)
ARMED[0] = True
sim.run(.1)
ARMED[0] = False
print(f'{len(CASES)} captured cases')

# ---- compare ------------------------------------------------------------
totals = {'A': 0.0, 'B': 0.0, 'Bbuild': 0.0, 'C': 0.0, 'Cbuild': 0.0}
mismatch = 0
nodes_total = nodes_moving = 0
for kind, root, moving, inputs in CASES:
    began = perf_counter()
    a = [plain(root, one) for one in inputs]
    totals['A'] += perf_counter() - began

    began = perf_counter()
    path = PathEvaluation(root, inputs[0], moving)
    totals['Bbuild'] += perf_counter() - began
    began = perf_counter()
    b = [path.at(one) for one in inputs]
    totals['B'] += perf_counter() - began

    began = perf_counter()
    comp = CompiledPath(root, inputs[0], moving)
    totals['Cbuild'] += perf_counter() - began
    began = perf_counter()
    c = [comp.at(one) for one in inputs]
    totals['C'] += perf_counter() - began

    nodes_total += path.total * len(inputs)
    nodes_moving += len(path.order) * len(inputs)
    for x, y, z in zip(a, b, c):
        if bits(x) != bits(y) or bits(x) != bits(z):
            mismatch += 1

samples = sum(len(one[3]) for one in CASES)
print(f'{samples} evaluations, {nodes_total} node visits today, '
      f'{nodes_moving} moving ({100 * nodes_moving / nodes_total:.1f}%)')
print(f'  A  current walk           {totals["A"] * 1000:8.2f} ms   '
      f'{1e6 * totals["A"] / samples:6.1f} us/evaluation')
print(f'  B  path evaluation        {totals["B"] * 1000:8.2f} ms   '
      f'{1e6 * totals["B"] / samples:6.1f} us/evaluation   '
      f'(+{totals["Bbuild"] * 1000:.2f} ms building, '
      f'{totals["A"] / totals["B"]:.1f}x)')
print(f'  C  compiled path          {totals["C"] * 1000:8.2f} ms   '
      f'{1e6 * totals["C"] / samples:6.1f} us/evaluation   '
      f'(+{totals["Cbuild"] * 1000:.2f} ms building, '
      f'{totals["A"] / totals["C"]:.1f}x)')
print(f'  bit mismatches: {mismatch} of {samples}')
