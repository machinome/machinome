from machinome.simulation import Sim
from machinome.test import TestCase

from .c09_clocked import Counter


class ClockedCounterTest(TestCase):

    node = Counter

    def test_twelve_strokes_count_to_twelve(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=12 * 360.0)
        self.assertEqual(len(request.commits), 12)
        self.assertEqual((sim.state['tens'], sim.state['units']), (1, 2))

    def test_ninety_nine_carries_to_zero(self):
        sim = Sim(Counter(), state={'units': 9, 'tens': 9})
        request = sim.move('crank', by=360.0)
        self.assertEqual([c.value for c in request.commits], [360.0])
        self.assertEqual((sim.state['tens'], sim.state['units']), (0, 0))

    def test_a_button_is_one_request(self):
        sim = Sim(Counter())
        request = sim.trigger('Turn once')
        self.assertEqual((request.origin, request.end), (0.0, 360.0))
        self.assertEqual([c.fraction for c in request.commits], [1.0])
        self.assertEqual(sim.state['units'], 1)

    def test_the_ratchet_stops_a_reverse_stroke(self):
        sim = Sim(Counter())
        sim.move('crank', by=360.0)
        request = sim.move('crank', by=-100.0)
        self.assertEqual(request.admitted, 0.0)
        self.assertEqual(request.stops[0].coordinate, 'handle.turn')
        self.assertEqual(sim.state['crank'], 360.0)
