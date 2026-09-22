"""A Bound-only consumer must demand its retained law's actual path."""

from unittest import TestCase
from unittest.mock import patch

from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Sim
from machinome.simulation.run import Run

from .running_project.parts import Arbor


def retained(_sources, _target):
    return lambda crank, own: crank / 10.0 * (own < 1.0)


class BoundOnlyRetained(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0.0, unit='deg')
    pawl = Arbor()
    wheel = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(None, Bound(lambda turn, pawl: 90.0 + pawl,
                           reads=(pawl.turn,)))))

    (crank & pawl.turn).drives(pawl.turn, law=retained)
    crank.drives(wheel.turn, ratio=1.0)

    def simulate(self):
        if self.pawl.turn.value is None:
            self.pawl.turn = 0.0


def interior_singularity(_source, _target):
    return lambda crank: crank * (crank - 10.0) / (crank - 5.0)


class InactiveBoundWithInteriorLaw(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0.0, unit='deg')
    pawl = Arbor()
    wheel = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(None, Bound(lambda turn, pawl: 90.0 + pawl,
                           reads=(pawl.turn,)))))

    crank.drives(pawl.turn, law=interior_singularity)

    def simulate(self):
        if self.wheel.turn.value is None:
            self.wheel.turn = 0.0


class BoundReadDemandTest(TestCase):
    def test_bound_only_retained_law_supplies_a_motion_path(self):
        sim = Sim(BoundOnlyRetained(), dt=0.1)
        pawl_key = sim._run.keys['pawl.turn']
        self.assertIn(pawl_key, sim._run.program.deltas_of({'crank': 1.0}).demanded)

        original = Run._constraint_level
        replays = []

        def counted(run, constraint, *args):
            replays.append(constraint.identifier)
            return original(run, constraint, *args)

        with patch.object(Run, '_constraint_level', counted):
            handle = sim.move('crank', by=9.0, duration=0.1)
            sim.run(0.1)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(sim.state['pawl.turn'], 0.9)
        self.assertEqual(replays, [])

    def test_inactive_bound_does_not_evaluate_an_unused_interior(self):
        idle = Sim(InactiveBoundWithInteriorLaw(), dt=0.1)
        idle.run(0.1)
        self.assertEqual(idle.state['pawl.turn'], 0.0)

        sim = Sim(InactiveBoundWithInteriorLaw(), dt=0.1)
        sim.move('crank', by=10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 0.0)
