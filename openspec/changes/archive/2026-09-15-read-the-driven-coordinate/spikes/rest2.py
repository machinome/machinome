"""Spike 4b: with the Kahn order patched too, what does a tick DO?"""
import json
from solid_node.motion import couplings
couplings._refuse_shared_coordinate = lambda a, b: None
_step = couplings._step_relation
def _self_read(record):
    driven = {id(e.slot) for e in record.driven_ends if e.slot is not None}
    return any(e.slot is not None and id(e.slot) in driven
               for e in record.driver_ends)
def _patched(record, claimed, bound):
    if _self_read(record):
        if record.direction is None:
            record.direction = 'forward'
            return True
        return False
    return _step(record, claimed, bound)
couplings._step_relation = _patched

from solid_node.simulation import program as P
_ordered = P._ordered
def _ordered_patched(kept, nodes):
    class _Shim:
        def __init__(self, edge):
            self.edge = edge
            self.needs = tuple(k for k in edge.needs if k not in edge.gives)
            self.gives = edge.gives
            self.description = edge.description
            self.kind = edge.kind
    shims = [_Shim(e) for e in kept]
    order = _ordered(shims, nodes)
    return [s.edge for s in order]
P._ordered = _ordered_patched

from solid_node.math import floor
from solid_node.motion.joints import Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Sim

def modulo(v, p):
    return v - p * floor(v / p)

def gated(sources, target):
    return lambda rack, wheel: rack * (modulo(wheel, 360.0) >= 36.0)

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

out = {}
try:
    node = Clearing()
    sim = Sim(node, dt=0.1, record=32)
    
    program = sim.program
    out['described'] = program.described()
    out['edge'] = [{'kind': e.kind,
                    'needs': [program.nodes[k].name for k in e.needs],
                    'gives': [program.nodes[k].name for k in e.gives],
                    'graph': [str(g) for g in e.graphs],
                    'skeleton': str(e.plans[0].skeleton) if e.plans and e.plans[0] else None,
                    'jumps': [(j.primitive, j.placeholder, str(j.argument), j.affine)
                              for j in e.plans[0].jumps] if e.plans and e.plans[0] else None,
                    'affine': e.affine} for e in program.edges]
    out['initial'] = dict(sim.state)
    h = sim.move('rack', by=500.0, duration=1.0)
    sim.run(1.0)
    out['after_500'] = dict(sim.state)
    out['status'] = h.status
    out['crossings'] = [(c.primitive, c.level, c.t) for c in sim.crossings]
    # second sweep over an already-cleared wheel
    h2 = sim.move('rack', by=500.0, duration=1.0)
    sim.run(1.0)
    out['after_second_500'] = dict(sim.state)
except Exception as failure:
    out['error'] = type(failure).__name__
    out['message'] = str(failure)[:900]
print(json.dumps(out, indent=2, default=repr))
