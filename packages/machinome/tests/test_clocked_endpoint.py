# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Enigma I's measured release endpoint, through public declarations only."""
import math
import unittest
from machinome.simulation import Sim

from .clocked_project.endpoint import THRESHOLD, machine


def events(request):
    return [(c.value, c.targets) for c in request.commits]


def check_exact_endpoint_and_partition(form, direction):
    model = machine(form, direction=direction)
    threshold = -direction * THRESHOLD
    direct = Sim(model())
    uninterrupted = direct.move('press', to=0)
    assert direct.state['count'] == 1
    split = Sim(model())
    endpoint = split.move('press', to=threshold)
    assert split.state['press'] == threshold
    assert split.state['count'] == 1
    assert len(endpoint.commits) == 1
    assert endpoint.commits[0].value == threshold
    assert split.move('press', to=threshold).commits == ()
    continuation = split.move('press', to=0)
    assert events(endpoint) + events(continuation) == events(uninterrupted)
    assert dict(split.state) == dict(direct.state)


def check_strict_endpoint(direction):
    model = machine(strict=True, direction=direction)
    threshold = -direction * THRESHOLD
    sim = Sim(model())
    assert sim.move('press', to=threshold).commits == ()
    landing = math.nextafter(threshold, direction * math.inf)
    request = sim.move('press', to=landing)
    assert [c.value for c in request.commits] == [landing]
    assert sim.state['count'] == 1
    assert sim.move('press', to=0).commits == ()


class EndpointTest(unittest.TestCase):
    def test_exact_endpoint_and_partition(self):
        for form in range(5):
            for direction in (-1, 1):
                with self.subTest(form=form, direction=direction):
                    check_exact_endpoint_and_partition(form, direction)

    def test_strict_endpoint(self):
        for direction in (-1, 1):
            with self.subTest(direction=direction):
                check_strict_endpoint(direction)

    def test_partition_bank_and_order_independently(self):
        direct, split = Sim(machine()()), Sim(machine()())
        uninterrupted = direct.move('press', to=0)
        endpoint = split.move('press', to=THRESHOLD)
        continuation = split.move('press', to=0)
        self.assertEqual(dict(split.state), dict(direct.state))
        self.assertEqual(events(endpoint) + events(continuation),
                         events(uninterrupted))

    def test_reconstructable_endpoint_control(self):
        sim = Sim(machine()(), state={'press': 2 * THRESHOLD})
        request = sim.move('press', to=THRESHOLD)
        self.assertEqual([c.value for c in request.commits], [THRESHOLD])
