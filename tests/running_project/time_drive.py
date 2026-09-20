# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Astrarium's two diagnostic cubes, not historical clock geometry.

Factories delay declarations so the original clock-source refusal fails a
test rather than preventing collection of the commanded/posed controls.
"""

import cadquery as cq

from machinome.motion.joints import Bound, Prismatic, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode, CadQueryNode
from machinome.simulation import Driver


class Shaft(CadQueryNode):
    turn = Revolute(axis=(0, 0, 1))

    def render(self):
        return cq.Workplane('XY').box(1, 1, 1)


class Weight(CadQueryNode):
    drop = Prismatic(axis=(0, 0, -1), range=(0, 10))

    def render(self):
        return cq.Workplane('XY').box(1, 1, 1)


def affine():
    class AffineClock(AssemblyNode):
        time = Time.running()
        shaft = Shaft()
        time.drives(shaft.turn, ratio=6)
    return AffineClock()


def gated(square=False):
    def gate(owners, target):
        if square:
            return lambda t, enabled: t*t*(enabled > 0.5)
        return lambda t, enabled: 6*t*(enabled > 0.5)

    class GatedClock(AssemblyNode):
        time = Time.running()
        enabled = Driver(default=1, range=(0, 1))
        shaft = Shaft()
        (time & enabled).drives(shaft.turn, law=gate)
    return GatedClock()


def astrarium():
    def power(owners, target):
        return lambda t, enabled, wind, angle: (
            t * (enabled > 0.5) * (angle - wind < 10))

    class AstrariumClock(AssemblyNode):
        time = Time.running()
        enabled = Driver(default=1, range=(0, 1))
        wind = Driver(default=0, unit='mm')
        shaft = Shaft()
        weight = Weight()
        (time & enabled & wind & shaft.turn).drives(shaft.turn, law=power)
        (shaft.turn & wind).drives(
            weight.drop, law=lambda owners, target: lambda angle, wind: angle-wind)

        def render(self):
            self.weight.translate((3, 0, 0))

        def simulate(self):
            if self.shaft.turn.value is None:
                self.shaft.turn = 0
    return AstrariumClock()


def stopped():
    class LimitedWeight(CadQueryNode):
        drop = Prismatic(axis=(0, 0, -1), range=(0, 2.5))

        def render(self):
            return cq.Workplane('XY').box(1, 1, 1)

    class IndependentClocks(AssemblyNode):
        time = Time.running()
        shaft = Shaft()
        weight = LimitedWeight()
        other = Shaft()
        time.drives(shaft.turn)
        shaft.turn.drives(weight.drop)
        time.drives(other.turn, ratio=2)
    return IndependentClocks()


def releasable():
    class AdjustableShaft(CadQueryNode):
        limit = Revolute(axis=(0, 0, 1))
        turn = Revolute(axis=(0, 0, 1), range=(0, Bound(
            lambda angle, limit: limit, reads=(limit,))))

        def render(self):
            return cq.Workplane('XY').box(1, 1, 1)

    class ReleasableClock(AssemblyNode):
        time = Time.running()
        release = Driver(default=2.5)
        shaft = AdjustableShaft()
        release.drives(shaft.limit)
        time.drives(shaft.turn)
    return ReleasableClock()


def mixed():
    class MixedClock(AssemblyNode):
        time = Time.running()
        assist = Driver(default=0)
        shaft = Shaft(turn=Revolute(axis=(0, 0, 1), range=(0, 2.5)))
        (time & assist).drives(
            shaft.turn, law=lambda owners, target: lambda t, assist: t+assist)
    return MixedClock()


def curved_stop():
    class CurvedClock(AssemblyNode):
        time = Time.running()
        shaft = Shaft()
        follower = Shaft(turn=Revolute(axis=(0, 0, 1), range=(0, 2)))
        time.drives(shaft.turn, law=lambda owner, target: lambda t: t*t)
        shaft.turn.drives(follower.turn)
    return CurvedClock()
