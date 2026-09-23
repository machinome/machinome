# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A running law's numeric failure refuses its tick and retires its command."""

import cadquery as cq
import pytest

from machinome import math as machinome_math
from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time, get_coordinate
from machinome.node import AssemblyNode, CadQueryNode
from machinome.simulation import Driver, Sim, UnsupportedLaw


class Shaft(CadQueryNode):
    turn = Revolute(axis=(0, 0, 1))

    def render(self):
        return cq.Workplane('XY').box(1, 1, 1)


class SquareRootMachine(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0)
    shaft = Shaft()
    feed.drives(shaft.turn, law=lambda owners, target:
                lambda feed: machinome_math.sqrt(0.1 - feed))


class SquareMachine(AssemblyNode):
    time = Time.running()
    feed = Driver(default=1)
    shaft = Shaft()
    feed.drives(shaft.turn, law=lambda owners, target:
                lambda feed: feed * feed)


class ArchedMachine(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0)
    slide = Shaft()
    guard = Shaft(turn=Revolute(axis=(0, 0, 1), range=(
        None, Bound(lambda own, slide: slide + 1,
                    reads=(slide.turn,)))))
    feed.drives(slide.turn, law=lambda owners, target:
                lambda feed: machinome_math.sqrt(
                    (feed - 0.1) * (feed - 0.1) - 0.0025))
    feed.drives(guard.turn, ratio=1)


def test_immediate_domain_error_refuses_and_frees_the_input():
    node = SquareRootMachine()
    sim = Sim(node, 0.1, meshes=False, record=8)
    before = sim.snapshot()
    posed = get_coordinate(node.shaft, 'turn')._value

    with pytest.raises(UnsupportedLaw, match=r'(?s)feed drives shaft\.turn.*SquareRootMachine.*shaft\.turn'):
        sim.move('feed', to=0.2)

    assert sim.snapshot() == before
    assert sim.tick == 0
    assert sim.trajectory == []
    assert sim.crossings == []
    assert sim.stops == []
    assert sim.commands == ()
    assert get_coordinate(node.shaft, 'turn')._value == posed


def test_finite_source_overflow_refuses_instead_of_banking_infinity():
    sim = Sim(SquareMachine(), 0.1, meshes=False, record=8)
    before = sim.snapshot()

    with pytest.raises(UnsupportedLaw, match=r'(?s)feed drives shaft\.turn.*SquareMachine.*shaft\.turn'):
        sim.move('feed', to=1e308)

    assert sim.snapshot() == before
    assert sim.trajectory == []
    assert sim.commands == ()


def test_later_domain_error_keeps_first_committed_tick():
    sim = Sim(SquareRootMachine(), 0.1, meshes=False, record=8)
    command = sim.move('feed', to=0.2, duration=0.2)
    sim.run(0.1)
    before = sim.snapshot()
    assert sim.tick == 1
    assert sim.state['feed'] == 0.1
    assert command.admitted == 0.1

    with pytest.raises(UnsupportedLaw, match='shaft.turn'):
        sim.run(0.1)

    assert sim.tick == 1
    assert sim.state == dict(before.bank)
    assert len(sim.trajectory) == 1
    assert command.status == 'refused'
    assert command.admitted == 0.1
    assert sim.commands == ()


def test_finite_square_root_boundary_and_unrelated_request_refusal():
    sim = Sim(SquareRootMachine(), 0.1, meshes=False, record=8)
    command = sim.move('feed', to=0.1)
    assert command.status == 'completed'
    assert sim.state == {'feed': 0.1, 'shaft.turn': 0}

    with pytest.raises(ValueError, match='not a declared') as caught:
        sim.move('undeclared', to=1)
    assert not isinstance(caught.value, UnsupportedLaw)


def test_existing_bound_path_sample_refuses_nonfinite_law_interior():
    sim = Sim(ArchedMachine(), 0.1, meshes=False, record=8)
    before = sim.snapshot()
    with pytest.raises(UnsupportedLaw, match='feed drives slide.turn'):
        sim.move('feed', to=0.3)
    assert sim.snapshot() == before
    assert sim.commands == ()


def test_exact_terminal_target_outside_law_domain_refuses():
    # The ordinary delta lands on 0.1, but the authored terminal target is
    # the next representable float, outside sqrt(0.1 - feed)'s domain.
    start = -0.234
    target = 0.10000000000000002
    assert start + (target - start) == 0.1
    sim = Sim(SquareRootMachine(), 0.1, state={'feed': start},
              meshes=False, record=8)
    before = sim.snapshot()

    with pytest.raises(UnsupportedLaw, match='feed drives shaft.turn'):
        sim.move('feed', to=target)

    assert sim.snapshot() == before
    assert sim.commands == ()
