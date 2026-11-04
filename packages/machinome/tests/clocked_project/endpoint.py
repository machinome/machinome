# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Enigma I's measured public release event, without CAD geometry."""
from machinome.node.assembly import AssemblyNode
from machinome.simulation import Driver, State

START = 6.442137473829186
THRESHOLD = 1.0571271006818843


def machine(form=0, strict=False, direction=-1):
    threshold = direction * -THRESHOLD
    def at(sources, targets):
        if strict:
            return lambda press, count: direction * press > direction * threshold
        return (
            lambda press, count: direction * press >= direction * threshold,
            lambda press, count: direction * threshold <= direction * press,
            lambda press, count: -direction * press <= -direction * threshold,
            lambda press, count: direction * (press - threshold) >= 0,
            lambda press, count: direction * press * 2 >= direction * threshold * 2,
        )[form]
    def law(sources, targets):
        return lambda press, count: count + 1
    class Release(AssemblyNode):
        press = Driver(default=-direction * START, unit='mm')
        count = State(default=0, dtype=int)
        (press & count).commits(count, at=at, law=law)
    return Release


EndpointRelease = machine()
