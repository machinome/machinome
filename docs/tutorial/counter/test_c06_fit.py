from machinome.test import TestCase

from .c06_fit import Counter


class CounterFitTest(TestCase):

    node = Counter

    def test_the_parts_do_not_interfere(self):
        self.assertNoSolidInterference(self.node)

    def test_every_piece_is_one_body(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_the_drums_run_on_the_arbor(self):
        # Free within the clearance, held beyond it: the arbor locates the
        # drum, and the drum still turns.
        for drum in (self.node.units_drum, self.node.tens_drum):
            self.assertFreeWithin(drum, 0.05, self.node.handle,
                                  along=(1, 0, 0))
            self.assertBlockedBeyond(drum, 0.5, self.node.handle,
                                     along=(1, 0, 0))
