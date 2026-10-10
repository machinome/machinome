"""The companion the `solid test` runner binds to the bench.

Two scenarios step the run on the node the RUNNER built and handed over
(`ScenarioTest.scenario_node()` adopts it), and the geometry cases that
follow ask one question: does the leaf's placement state the coordinate the
leaf holds?
"""
from solid_node.motion.ports import get_coordinate
from solid_node.simulation import ScenarioTest
from solid_node.test import TestCase

from machine import Bench


def placement(node):
    """The travel every motion operation on `node` states, added up."""
    total = 0.0
    for operation in node.operations:
        if not getattr(operation, '_motion', False):
            continue
        total += float(operation.serialized[1][0])
    return total


def report(label, node):
    print(f"\n   {label}: slide.travel={get_coordinate(node.slide, 'travel')._value!r}, "
          f"placed={placement(node.slide)!r}, "
          f"operations={[o.serialized for o in node.slide.operations]}")


class BenchScenario(ScenarioTest):
    node = Bench
    dt = 0.1

    def test_a_push(self):
        sim = self.simulation()
        sim.move('push', to=12.0, duration=0.2)
        sim.run(0.2)
        report('scenario 1', self.node)

    def test_b_push_again(self):
        sim = self.simulation()
        sim.move('push', to=8.0, duration=0.2)
        sim.run(0.2)
        report('scenario 2', self.node)


class BenchGeometry(TestCase):
    node = Bench

    def _agrees(self, label):
        report(label, self.node)
        self.assertAlmostEqual(
            placement(self.node.slide),
            get_coordinate(self.node.slide, 'travel')._value,
            msg='the leaf stands where its coordinate does not say')

    def test_a(self):
        self._agrees('geometry A')

    def test_b(self):
        self._agrees('geometry B')


# The runner hands its node to a test INSTANCE, so a class whose setUpClass
# wants it has to be handed it too. Stashing it here is the shortest path to
# the second face of the same defect: a checkpoint TAKEN while a run's own
# placement stands.
_HANDED = []


class BenchHandOver(ScenarioTest):
    node = Bench
    dt = 0.1

    def test_a_hand_the_node_over(self):
        _HANDED.append(self.node)


class BenchAfterSetUpClass(TestCase):
    """Every checkpoint of this class is taken while the run's own,
    UNTAGGED placement stands, because setUpClass stepped the run before
    the first test saved one."""

    node = Bench

    @classmethod
    def setUpClass(cls):
        from solid_node.simulation import Sim

        sim = Sim(_HANDED[0], 0.1)
        sim.move('push', to=12.0, duration=0.2)
        sim.run(0.2)

    def _step(self, label):
        from solid_node.simulation import Sim

        Sim(self.node, 0.1)
        report(label, self.node)
        self.assertAlmostEqual(
            placement(self.node.slide),
            get_coordinate(self.node.slide, 'travel')._value,
            msg='the leaf stands where its coordinate does not say')

    def test_a(self):
        self._step('after setUpClass A')

    def test_b(self):
        self._step('after setUpClass B')

    def test_c(self):
        self._step('after setUpClass C')
