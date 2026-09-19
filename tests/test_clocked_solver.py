# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The event solver: where a request's events are, and which of them
fire.

Every crossing on a request's path is SOLVED by the tools ADR-107 and
ADR-123 already own -- one division on an affine level, one division per
sub-interval on a kinked one -- and never searched; a curved level is
refused at construction instead. Only a RISING step fires, because the
project spike measured the requirement note's assumption false: dragging
the crank backwards through `floor(crank / 360)` with an additive law
commits a SECOND addition (9 to 18).

Two relations are ONE event exactly when their far-side landings are the
SAME float. No tolerance decides it, and these tests are what that claim
means: a pair one ulp apart is two events whether the crossing happens
inside one long request or inside the shorter requests that reach past
it, which is the assertion a travel-scaled tolerance would fail.

Task 5 of the change `declare-the-state`. The originating project is
`projects/Calculators/Curta-Type-I-3x`.
"""

import math

from machinome.simulation import Sim
from machinome.simulation.clocked import TooManyEvents
from machinome.math import floor, min as sym_min
from machinome.node import AssemblyNode
from machinome.simulation import Driver, State

from .base import BaseNodeTest
from .clocked_project.counter import Counter, KinkedCounter, Reverse
from .clocked_project.parts import Dial
from .clocked_project.ties import (NonStrict, SamePair, Strict, SwappedPair,
                                   T, UP, UlpPair)


def fractions(request):
    return [commit.fraction for commit in request.commits]


def values(request):
    return [commit.value for commit in request.commits]


class CrossingTest(BaseNodeTest):
    """Task 5.1: where the crossings are, and which of them fire."""

    def test_one_rising_crossing_at_the_hand_computed_fraction(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=540.0)
        # The level crosses 1 where crank reaches 360, which is
        # 360 / 540 = two thirds of the way along the request.
        self.assertEqual(len(request.commits), 1)
        self.assertAlmostEqual(request.commits[0].fraction, 360.0 / 540.0)
        self.assertEqual(request.commits[0].value, 360.0)

    def test_a_falling_crossing_is_located_and_not_fired(self):
        """The spike's 9 to 18: dragging the crank backwards crosses the
        same surfaces and commits nothing."""
        sim = Sim(Counter(), state={'crank': 3600.0, 'units': 9, 'tens': 0})
        request = sim.move('crank', by=-3600.0)
        self.assertEqual(request.commits, ())
        self.assertEqual(sim.state['units'], 9)
        self.assertEqual(sim.state['tens'], 0)
        self.assertEqual(sim.state['crank'], 0.0)

    def test_three_crossings_in_one_path_arrive_in_order(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=1080.0)
        self.assertEqual(values(request), [360.0, 720.0, 1080.0])
        self.assertEqual(fractions(request), [1 / 3, 2 / 3, 1.0])
        self.assertEqual(sim.state['units'], 3)

    def test_the_other_edge_is_written_by_negating_the_level(self):
        """Rising-only is fully expressive: a mechanism committing on the
        falling edge negates its own level."""
        sim = Sim(Reverse())
        forward = sim.move('crank', by=720.0)
        self.assertEqual(forward.commits, ())
        backward = sim.move('crank', by=-720.0)
        self.assertEqual(len(backward.commits), 2)
        self.assertEqual(sim.state['units'], 2)


class LandingTest(BaseNodeTest):
    """Task 5.3: the far-side landing, asserted as an exact float."""

    def test_a_floor_crossing_lands_on_the_surface_itself(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=720.0)
        self.assertEqual(values(request), [360.0, 720.0])

    def test_resuming_from_the_landing_does_not_refire(self):
        sim = Sim(Counter())
        sim.move('crank', by=360.0)
        self.assertEqual(sim.state['crank'], 360.0)
        self.assertEqual(sim.state['units'], 1)
        # A second request that moves nowhere fires nothing, and one
        # that moves on fires only the NEXT surface.
        self.assertEqual(sim.move('crank', by=0.0).commits, ())
        following = sim.move('crank', by=360.0)
        self.assertEqual(values(following), [720.0])
        self.assertEqual(sim.state['units'], 2)

    def test_a_strict_comparison_lands_on_the_next_float(self):
        sim = Sim(Strict())
        request = sim.move('crank', by=200.0)
        self.assertEqual(len(request.commits), 1)
        self.assertEqual(request.commits[0].value, math.nextafter(T, math.inf))
        self.assertEqual(request.commits[0].value, UP)

    def test_a_non_strict_comparison_lands_on_the_threshold(self):
        sim = Sim(NonStrict())
        request = sim.move('crank', by=200.0)
        self.assertEqual(len(request.commits), 1)
        self.assertEqual(request.commits[0].value, T)


class KinkedLevelTest(BaseNodeTest):
    """Task 5.5: a kinked level is SOLVED at its breakpoint."""

    def test_a_kinked_level_is_solved_and_its_breakpoint_is_not_an_event(self):
        sim = Sim(KinkedCounter(), state={'crank': -720.0})
        request = sim.move('crank', by=1800.0)
        # max(crank, 0) kinks at crank == 0, which is t = 720 / 1800.
        # That breakpoint is not a crossing: the quantity is continuous
        # there. The three crossings are at crank 360, 720 and 1080.
        self.assertEqual(values(request), [360.0, 720.0, 1080.0])
        self.assertEqual(fractions(request),
                         [1080.0 / 1800.0, 1440.0 / 1800.0, 1.0])
        self.assertEqual(sim.state['units'], 3)

    def test_the_flat_side_of_a_kink_fires_nothing(self):
        sim = Sim(KinkedCounter(), state={'crank': -720.0})
        request = sim.move('crank', by=360.0)
        self.assertEqual(request.commits, ())


class SimultaneityTest(BaseNodeTest):
    """Task 5.7: ties are decided by IDENTITY of the landing."""

    def test_surfaces_one_ulp_apart_are_two_events_in_path_order(self):
        sim = Sim(UlpPair())
        request = sim.move('crank', by=200.0)
        self.assertEqual(len(request.commits), 2)
        self.assertEqual(values(request), [T, UP])
        # The second law read what the first committed: a * 10 + 1 with
        # a == 1 is 11, where a synchronous read would give 1.
        self.assertEqual(sim.state['a'], 1)
        self.assertEqual(sim.state['b'], 11)

    def test_the_ulp_pair_reads_the_same_split_into_short_requests(self):
        """The assertion a travel-scaled tolerance would fail."""
        one = Sim(UlpPair())
        one.move('crank', by=200.0)

        several = Sim(UlpPair())
        first = several.move('crank', by=100.0)
        second = several.move('crank', by=100.0)
        self.assertEqual(values(first), [T])
        self.assertEqual(values(second), [UP])
        self.assertEqual(one.state, several.state)

    def test_surfaces_landing_on_one_float_are_one_event(self):
        sim = Sim(SamePair())
        request = sim.move('crank', by=200.0)
        self.assertEqual(len(request.commits), 1)
        self.assertEqual(request.commits[0].value, T)
        # Both laws read the bank as it stood BEFORE the event: a was 0,
        # so b is 0 * 10 + 1.
        self.assertEqual(sim.state['a'], 1)
        self.assertEqual(sim.state['b'], 1)

    def test_swapping_the_two_lines_changes_nothing_observable(self):
        straight = Sim(SamePair())
        straight.move('crank', by=200.0)
        swapped = Sim(SwappedPair())
        swapped.move('crank', by=200.0)
        self.assertEqual(straight.state, swapped.state)


class MovingSurfaceTest(BaseNodeTest):
    """Task 5.9: an event surface that reads its own state moves with
    it."""

    def test_a_cleared_dial_is_not_reached_again(self):
        from .clocked_project.clearing import Clearer, threshold

        sim = Sim(Clearer(), state={'dial.digit': 7})
        # The rack reaches a dial standing at 7 after 10 + 4 * 3 == 22
        # ring degrees.
        self.assertEqual(threshold(7), 22.0)
        first = sim.move('ring', by=40.0)
        self.assertEqual(values(first), [22.0])
        self.assertEqual(sim.state['dial.digit'], 0)
        # Cleared, the same dial is reached only at 10 + 4 * 10 == 50,
        # which this sweep never gets to.
        self.assertEqual(threshold(0), 50.0)
        sim.move('ring', to=0.0)
        second = sim.move('ring', by=40.0)
        self.assertEqual(second.commits, ())
        self.assertEqual(sim.state['dial.digit'], 0)

    def test_a_reversed_sweep_fires_nothing(self):
        from .clocked_project.clearing import Clearer

        sim = Sim(Clearer(), state={'dial.digit': 7, 'ring': 40.0})
        request = sim.move('ring', by=-40.0)
        self.assertEqual(request.commits, ())
        self.assertEqual(sim.state['dial.digit'], 7)


def far_level(sources, targets):
    return lambda crank, value: floor(crank / 360)


def stopping_level(sources, targets):
    """A level that would cross far more than the maximum if it kept
    crossing, and stops partway through the path."""
    return lambda crank, value: floor(sym_min(crank, 3600.0) / 360)


def bump(sources, targets):
    return lambda crank, value: value + 1


class Endless(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=far_level, law=bump)
    value.drives(face.turn, ratio=1.0)


class Stopping(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stopping_level, law=bump)
    value.drives(face.turn, ratio=1.0)


class CrossingMaximumTest(BaseNodeTest):
    """Task 5.11: the bound is over the events ACTUALLY LOCATED."""

    def test_more_events_than_the_maximum_are_refused(self):
        sim = Sim(Endless())
        with self.assertRaises(TooManyEvents) as caught:
            sim.move('crank', by=360.0 * 1001)
        message = str(caught.exception)
        self.assertIn('crank', message)
        self.assertIn('1000', message)
        self.assertIn('Split it into shorter requests', message)
        # Nothing was committed.
        self.assertEqual(sim.state['value'], 0)
        self.assertEqual(sim.state['crank'], 0.0)

    def test_a_level_that_stops_crossing_is_admitted(self):
        sim = Sim(Stopping())
        request = sim.move('crank', by=360.0 * 5000)
        self.assertEqual(len(request.commits), 10)
        self.assertEqual(sim.state['value'], 10)


class LandingContainmentTest(BaseNodeTest):
    """Closure 1(a) of the change `publish-the-clocked-machine`: a
    crossing belongs to the request whose path CONTAINS its landing.

    ADR-125 stated the containment by FRACTION -- right end inclusive,
    left end exclusive -- and that reading loses an event. A request
    that ends exactly ON a STRICT comparison's surface solves its
    crossing at fraction 1.0, but the landing is the first representable
    value BEYOND the endpoint, which this request's path does not
    contain; and the next request, resuming from that endpoint, excluded
    its own left end by fraction and so never saw the surface at all.

    The corpus of this cycle is what found it. The rule is stated by
    LANDING in both directions: a landing beyond the endpoint is the
    next request's, and a crossing solved at fraction 0 whose far side
    lies inside the path IS this request's event.
    """

    def test_a_request_ending_on_a_strict_surface_fires_nothing(self):
        sim = Sim(Strict())
        request = sim.move('crank', to=T)
        self.assertEqual(request.commits, ())
        self.assertEqual(sim.state['crank'], T)
        self.assertEqual(sim.state['a'], 0)

    def test_the_next_request_fires_the_strict_surface_it_stands_on(self):
        sim = Sim(Strict())
        sim.move('crank', to=T)
        following = sim.move('crank', by=1.0)
        self.assertEqual(values(following), [UP])
        self.assertEqual(sim.state['a'], 1)
        # And only once: the surface is behind the bank now.
        self.assertEqual(sim.move('crank', by=1.0).commits, ())
        self.assertEqual(sim.state['a'], 1)

    def test_the_non_strict_twin_fires_on_the_first_request(self):
        sim = Sim(NonStrict())
        request = sim.move('crank', to=T)
        self.assertEqual(values(request), [T])
        self.assertEqual(sim.state['a'], 1)
        # Its landing IS the endpoint, so the next request resuming from
        # it fires nothing: the surface was taken by the request whose
        # path contained the landing.
        self.assertEqual(sim.move('crank', by=1.0).commits, ())
        self.assertEqual(sim.state['a'], 1)

    def test_a_floor_surface_reached_exactly_still_fires_on_arrival(self):
        # The non-strict reading of `floor`: `move('crank', by=360)` with
        # `at = floor(crank / 360)` IS one stroke, and the request that
        # resumes from that landing fires nothing.
        sim = Sim(Counter())
        self.assertEqual(values(sim.move('crank', to=360.0)), [360.0])
        self.assertEqual(sim.move('crank', by=0.0).commits, ())
        self.assertEqual(sim.state['units'], 1)
