"""Spike 4: the REST story and the Kahn order, with the two refusals
monkeypatched out.

`_refuse_shared_coordinate` is made a no-op and `_step_relation` is
wrapped so a relation naming its own driven end among its sources binds
NOTHING and records itself solved forward -- the design's rest rule.
Nothing in the worktree is edited. The question is what the NEXT failure
downstream is: the rest render, the compile, or the Kahn order.
"""

import json

from solid_node.motion import couplings

couplings._refuse_shared_coordinate = lambda driver_ref, driven_ref: None

_step = couplings._step_relation


def _self_read(record):
    driven = {id(end.slot) for end in record.driven_ends
              if end.slot is not None}
    return any(end.slot is not None and id(end.slot) in driven
               for end in record.driver_ends)


def _patched(record, claimed, bound):
    if _self_read(record):
        if record.direction is None:
            record.direction = 'forward'
            return True
        return False
    return _step(record, claimed, bound)


couplings._step_relation = _patched

from solid_node.math import floor                  # noqa: E402
from solid_node.motion.joints import Revolute      # noqa: E402
from solid_node.motion.ports import Time           # noqa: E402
from solid_node.node import AssemblyNode           # noqa: E402
from solid_node.simulation import Driver, Sim      # noqa: E402


def modulo(value, period):
    return value - period * floor(value / period)


GAP = 36.0


def gated(sources, target):
    """The window gate: engaged while the gap is not facing the rack."""
    return lambda rack, wheel: rack * (modulo(wheel, 360.0) >= GAP)


class ClearingWheel(AssemblyNode):
    rotation = Revolute(axis=(0, 0, 1), unit='deg')

    def simulate(self):
        if self.rotation.value is None:
            self.rotation = 108.0

    def render(self):
        pass


class Clearing(AssemblyNode):
    time = Time.running()
    rack = Driver(default=0.0, unit='deg')
    wheel = ClearingWheel()
    (rack & wheel.rotation).drives(wheel.rotation, law=gated)

    def render(self):
        pass


class Untimed(AssemblyNode):
    rack = Driver(default=0.0, unit='deg')
    wheel = ClearingWheel()
    (rack & wheel.rotation).drives(wheel.rotation, law=gated)

    def render(self):
        pass


def case(name, fn):
    try:
        return {'case': name, 'result': fn()}
    except Exception as failure:          # noqa: BLE001
        return {'case': name, 'error': type(failure).__name__,
                'message': str(failure)[:1000]}


def rest_pose():
    node = Untimed()
    node.set_state(rack=10.0)
    return {'rotation': node.wheel.rotation.value}


def construct():
    sim = Sim(Clearing(), dt=0.1, record=16)
    program = sim.run_engine.program if hasattr(sim, 'run_engine') else None
    return {'state': dict(sim.state)}


def compiled():
    from solid_node.simulation.program import program_of

    node = Clearing()
    Sim(node, dt=0.1)
    program = program_of(node)
    return {'described': program.described(),
            'edges': [{'kind': e.kind,
                       'needs': [program.nodes[k].name for k in e.needs],
                       'gives': [program.nodes[k].name for k in e.gives],
                       'graphs': [str(g) for g in e.graphs],
                       'skeleton': (str(e.plans[0].skeleton)
                                    if e.plans and e.plans[0] else None),
                       'affine': e.affine}
                      for e in program.edges]}


if __name__ == '__main__':
    for name, fn in (('untimed rest pose', rest_pose),
                     ('Sim construction', construct),
                     ('the compiled program', compiled)):
        print(json.dumps(case(name, fn), indent=2, default=repr))
        print()
