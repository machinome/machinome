from machinome.simulation import Sim
from machinome.test import TestCase

from .c08_running import Counter


class RunningCounterTest(TestCase):

    node = Counter

    def test_ten_turns_advance_the_tens_drum_one_digit(self):
        sim = Sim(Counter(), dt=0.05)
        for _ in range(10):
            sim.trigger('Turn once')
            sim.run(2.0)
        self.assertAlmostEqual(sim.state['units_drum.turn'], 360.0)
        self.assertAlmostEqual(sim.state['tens_drum.turn'], 36.0)

    def test_the_ratchet_holds_the_crank(self):
        sim = Sim(Counter(), dt=0.05)
        sim.trigger('Turn once')
        sim.run(2.0)

        back, = sim.trigger('Back a bit')
        sim.run(0.5)
        self.assertEqual(back.status, 'blocked')
        self.assertEqual(back.admitted, 0.0)

        # One tooth of backlash, and no more.
        sim.move('crank', by=30.0, duration=0.5)
        sim.run(0.5)
        back = sim.move('crank', by=-100.0, duration=0.5)
        sim.run(0.5)
        self.assertEqual(back.status, 'blocked')
        self.assertAlmostEqual(back.admitted, -30.0)
        self.assertAlmostEqual(sim.state['crank'], 360.0)
