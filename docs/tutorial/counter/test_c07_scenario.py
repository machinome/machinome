from machinome.simulation import ScenarioTest, Sim

from .c07_scenario import Counter


class CounterScenarioTest(ScenarioTest):

    node = Counter
    dt = 0.02
    meshes = True

    def test_a_turn_stays_clear_of_the_post(self):
        sim = self.simulation()

        sim.at(0.0).trigger('Turn once')
        sim.every(0.1, self.assertNoSolidInterference, self.node)
        sim.run(2.0)

        self.assertEqual(sim.state['crank'], 360.0)
        self.assertEqual(sim.assertion_stats[0], 20)

    def test_a_low_arm_is_caught_at_the_tick_it_sweeps_the_post(self):
        low = Counter(arm_height=34.0)
        sim = Sim(low, dt=0.02, meshes=True)

        sim.at(0.0).trigger('Turn once')
        sim.every(0.1, self.assertNoSolidInterference, low)

        with self.assertRaises(AssertionError):
            sim.run(2.0)

        self.assertEqual(sim.tick, 70)
