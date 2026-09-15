"""Spike 1: the three 'current model' routes the requirement note lists.

Run from the worktree with PYTHONPATH="$PWD".
"""

import json

from solid_node.math import clamp01, floor
from solid_node.motion.joints import Bound, Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, Sim

from solid2 import cylinder


class Wheel(Solid2Node):
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cylinder(r=10, h=4)


class Dummy(AssemblyNode):
    def render(self):
        pass


def report(name, fn):
    try:
        value = fn()
    except Exception as failure:          # noqa: BLE001
        return {'route': name, 'error': type(failure).__name__,
                'message': str(failure)[:900]}
    return {'route': name, 'result': value}


##############################################
# Route A1: a plain declared range on the wheel -- stops the RING.

def route_a1():
    class RackWheel(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Wheel(turn=Revolute(axis=(0, 0, 1), unit='deg',
                                    range=(None, 360.0)))
        ring.drives(wheel.turn, ratio=1.0)

        def render(self):
            pass

    sim = Sim(RackWheel(), dt=0.1, record=16)
    handle = sim.move('ring', by=500.0, duration=1.0)
    sim.run(1.0)
    return {'wheel': sim.state['wheel.turn'], 'ring': sim.state['ring'],
            'handle': handle.status, 'admitted': handle.admitted,
            'stops': [(s.coordinate, s.bound, s.value, s.t, s.inputs)
                      for s in sim.stops]}


##############################################
# Route A2: a Bound with reads on the wheel -- still stops the RING.

def route_a2():
    class RackWheel(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Wheel(turn=Revolute(
            axis=(0, 0, 1), unit='deg',
            range=(None, Bound(lambda turn, r: 360.0 * (r >= 0),
                               reads=(ring,)))))
        ring.drives(wheel.turn, ratio=1.0)

        def render(self):
            pass

    sim = Sim(RackWheel(), dt=0.1, record=16)
    handle = sim.move('ring', by=500.0, duration=1.0)
    sim.run(1.0)
    return {'wheel': sim.state['wheel.turn'], 'ring': sim.state['ring'],
            'handle': handle.status, 'admitted': handle.admitted,
            'stops': [(s.coordinate, s.bound, s.value, s.t, s.inputs)
                      for s in sim.stops]}


##############################################
# Route B: a source-only gate from TOTAL ring travel

def route_b():
    def clearing(sources, target):
        return lambda ring: 90.0 * clamp01((ring - 100.0) / 90.0)

    class RackWheel(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Wheel()
        ring.drives(wheel.turn, law=clearing)

        def render(self):
            pass

    sim = Sim(RackWheel(), dt=0.1)
    sim.move('ring', by=200.0, duration=1.0)
    sim.run(1.0)
    first = sim.state['wheel.turn']
    sim.move('ring', by=-200.0, duration=1.0)
    sim.run(1.0)
    back = sim.state['wheel.turn']
    sim.move('ring', by=200.0, duration=1.0)
    sim.run(1.0)
    return {'after_first_sweep': first, 'after_return': back,
            'after_second_sweep': sim.state['wheel.turn'],
            'wanted_after_second_sweep': first}


##############################################
# Route C: a duplicated wheel coordinate

def route_c():
    def gated(sources, target):
        return lambda ring, shadow: ring * (shadow < 350.0)

    class RackWheel(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Wheel()
        shadow = Wheel()
        wheel.turn.drives(shadow.turn, ratio=1.0)
        (ring & shadow.turn).drives(wheel.turn, law=gated)

        def render(self):
            self.shadow.translate([40.0, 0.0, 0.0])

    sim = Sim(RackWheel(), dt=0.1)
    return {'constructed': True, 'state': dict(sim.state)}


##############################################
# Route D: the diagnostic itself, as the project wrote it

def route_d():
    def missing_tooth(sources, target):
        return lambda rack, wheel: rack * (wheel % 360 < 359)

    class ClearingWheel(AssemblyNode):
        rotation = Revolute(axis=(0, 0, 1))

        def simulate(self):
            if self.rotation.value is None:
                self.rotation = 108

    class Clearing(AssemblyNode):
        time = Time.running()
        rack = Driver(default=0, unit='deg')
        wheel = ClearingWheel()
        (rack & wheel.rotation).drives(wheel.rotation, law=missing_tooth)

    return {'constructed': True}


##############################################
# Route E: a one-to-one self relation, which nothing refuses today

def route_e():
    def gated(sources, target):
        return lambda wheel: wheel * 2

    class RackWheel(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Wheel()
        wheel.turn.drives(wheel.turn, law=gated)

        def render(self):
            pass

    sim = Sim(RackWheel(), dt=0.1)
    return {'constructed': True}


if __name__ == '__main__':
    for name, fn in (('A1 plain range on the wheel', route_a1),
                     ('A2 Bound-with-reads on the wheel', route_a2),
                     ('B source-only gate from total travel', route_b),
                     ('C duplicated wheel coordinate', route_c),
                     ('D the diagnostic as written', route_d),
                     ('E a.drives(a)', route_e)):
        print(json.dumps(report(name, fn), indent=2, default=repr))
        print()
