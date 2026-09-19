"""Task 0.6 (c) and (d): the measurement design.md section 6 publishes
`per_unit` from, probed before `Program.response` exists.

(c) A PURE pass over the compiled program's `edge.increments`, seeded
    with one input's displacement and nothing else, reproduces BIT FOR
    BIT what `sim.move(input, by=eps, duration=0)` commits on a fresh
    simulation. The bodies below are what `Run._values` and
    `Run._deltas` do today, written out here so the probe measures the
    design's arithmetic rather than an implementation of it.

(d) `2**-20` as the displacement makes an affine chain read exactly
    `-36.0` in BOTH directions, while `1e-3` reads
    `-36.000000000000004`.
"""

from solid2 import cylinder

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, Sim

from tests.running_project.machine import (Carry, CarryLead, Ranged, Train,
                                           carried_column)


class Dial(Solid2Node):
    def render(self):
        return cylinder(r=20, h=3)


class DialArbor(AssemblyNode):
    turn = Revolute(axis=(1, 0, 0), unit='deg')

    dial = Dial()

    def render(self):
        pass


class Columns(AssemblyNode):
    """The Pascaline module's own tree shape."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    tens = DialArbor()

    units_entry.drives(units.turn, ratio=-36.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    def render(self):
        self.tens.translate([60.0, 0.0, 0.0])


##############################################
# The pure arithmetic, written out


def values_of(run, bank):
    values = {run.keys[identifier]: value
              for identifier, value in bank.items()}
    for edge in run.program.edges:
        if all(key in run.bank_keys for key in edge.gives):
            continue
        for key, value in edge.values(values):
            if key not in run.bank_keys:
                values[key] = value
    return values


def deltas_of(run, admissions):
    deltas = {key: 0.0 for key in run.program.nodes}
    for input_id, delta in admissions.items():
        if delta:
            deltas[run.keys[input_id]] = delta
    return deltas


def response(run, bank, input_id, eps):
    """One input displaced by `eps` at `bank`, propagated once."""
    values = values_of(run, bank)
    deltas = deltas_of(run, {input_id: eps})
    for edge in run.program.edges:
        if edge.kind == 'check':
            continue
        for key, delta in edge.increments(values, deltas):
            deltas[key] = delta
    return {identifier: deltas[key]
            for identifier, key in run.keys.items()}


##############################################
# (c) the pure pass reproduces the run


EPS = 2.0 ** -20

print('(c) response(rest, input, eps) vs move(input, by=eps, duration=0)')
agreed = True
for factory in (Columns, Carry, CarryLead, Ranged, Train):
    reference = Sim(factory(), 0.1)
    run = reference._run
    rest = dict(run.bank)
    for input_id, _declaration in run.program.inputs:
        for eps in (EPS, -EPS):
            measured = response(run, rest, input_id, eps)
            fresh = Sim(factory(), 0.1)
            fresh.move(input_id, by=eps, duration=0)
            committed = {identifier: fresh.state[identifier] - rest[identifier]
                         for identifier in rest}
            for identifier in sorted(rest):
                if measured[identifier] != committed[identifier]:
                    agreed = False
                    print(f'    MISMATCH {factory.__name__} {input_id} '
                          f'{eps:+} {identifier}: '
                          f'{measured[identifier]!r} != '
                          f'{committed[identifier]!r}')
        print(f'    {factory.__name__:10s} {input_id:12s} '
              f'ok both directions, {len(rest)} bank entries')
print(f'    VERDICT: bit-for-bit agreement = {agreed}')

print()
print('(c, continued) the reading the Pascaline shape earns')
reference = Sim(Columns(), 0.1)
run = reference._run
rest = dict(run.bank)
for input_id in ('units_entry', 'tens_entry'):
    forward = response(run, rest, input_id, EPS)
    print(f'    {input_id}: units.turn {forward["units.turn"]!r}  '
          f'tens.turn {forward["tens.turn"]!r}')

print()
print('(d) the displacement, on the affine chain units_entry -> units.turn')
for eps in (2.0 ** -20, 1e-3, 1e-6, 2.0 ** -30):
    raw = response(run, rest, 'units_entry', eps)['units.turn']
    forward = raw / eps
    backward = response(run, rest, 'units_entry', -eps)['units.turn'] / -eps
    print(f'    eps={eps!r:24s} raw={raw!r:24s} forward={forward!r:22s} '
          f'backward={backward!r:22s} exact={forward == backward == -36.0}')

print()
print('    The RAW response at 1e-3 is -0.036000000000000004, exactly as')
print('    design.md section 6 says; the DIVISION recovers -36.0 anyway on a')
print('    chain of ONE edge. The power of two earns its keep on a chain of')
print('    TWO, where the intermediate is rounded before the second factor')
print('    multiplies it:')
for first, second in ((-36.0, -36.0), (-36.0, -1.5), (-36.0, 0.3)):
    for eps in (1e-3, 2.0 ** -20):
        ratio = ((first * eps) * second) / eps
        print(f'      {first} then {second}, eps={eps!r:22s} -> {ratio!r:22s} '
              f'(exact product {first * second!r})')
