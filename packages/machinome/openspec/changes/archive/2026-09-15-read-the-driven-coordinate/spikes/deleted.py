"""Spike 1b: what deleting `_refuse_shared_coordinate` actually gives.

The refusal is monkeypatched OUT at runtime -- no worktree file is
touched -- so the next failure downstream is visible.
"""

import json

from solid_node.motion import couplings

couplings._refuse_shared_coordinate = lambda driver_ref, driven_ref: None

from solid_node.motion.joints import Revolute      # noqa: E402
from solid_node.motion.ports import Time           # noqa: E402
from solid_node.node import AssemblyNode           # noqa: E402
from solid_node.simulation import Driver, Sim      # noqa: E402


def missing_tooth(sources, target):
    return lambda rack, wheel: rack * (wheel % 360 < 359)


def case(name, build):
    try:
        value = build()
    except Exception as failure:          # noqa: BLE001
        return {'case': name, 'error': type(failure).__name__,
                'message': str(failure)[:1200]}
    return {'case': name, 'result': value}


def guarded():
    """The project's own shape: a rest-default guard in simulate()."""
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
        (rack & wheel.rotation).drives(wheel.rotation, law=missing_tooth)

        def render(self):
            pass

    sim = Sim(Clearing(), dt=0.1)
    return dict(sim.state)


def unguarded():
    """No rest default at all."""
    class ClearingWheel(AssemblyNode):
        rotation = Revolute(axis=(0, 0, 1), unit='deg')

        def render(self):
            pass

    class Clearing(AssemblyNode):
        time = Time.running()
        rack = Driver(default=0.0, unit='deg')
        wheel = ClearingWheel()
        (rack & wheel.rotation).drives(wheel.rotation, law=missing_tooth)

        def render(self):
            pass

    sim = Sim(Clearing(), dt=0.1)
    return dict(sim.state)


def untimed():
    """The same declaration with NO running time base."""
    class ClearingWheel(AssemblyNode):
        rotation = Revolute(axis=(0, 0, 1), unit='deg')

        def simulate(self):
            if self.rotation.value is None:
                self.rotation = 108.0

        def render(self):
            pass

    class Clearing(AssemblyNode):
        rack = Driver(default=0.0, unit='deg')
        wheel = ClearingWheel()
        (rack & wheel.rotation).drives(wheel.rotation, law=missing_tooth)

        def render(self):
            pass

    node = Clearing()
    node.set_state(rack=10.0)
    return {'rotation': node.wheel.rotation.value}


if __name__ == '__main__':
    for name, build in (('guarded rest default, running', guarded),
                        ('no rest default, running', unguarded),
                        ('guarded rest default, untimed', untimed)):
        print(json.dumps(case(name, build), indent=2, default=repr))
        print()
