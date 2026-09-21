# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A faster threshold overtakes a moving follower (Curta carry reduction)."""

from machinome.motion.joints import Bound
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver
from .running_project.parts import Arbor


class OvertakenFollower(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    follower = Arbor()
    (crank & follower.turn).drives(follower.turn, law=lambda sources, target:
        lambda crank, own: crank*(.5+.5*(own > 2*crank+1)))

    def simulate(self):
        if self.follower.turn.value is None:
            self.follower.turn = 2


class ObservedFollower(OvertakenFollower):
    bell = Arbor()
    OvertakenFollower.crank.drives(bell.turn)
    bell.turn.constrain(range=(None, Bound(lambda own, follower: follower+10,
        reads=(OvertakenFollower.follower.turn,))))


class NegativeFollower(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    follower = Arbor()
    (crank & follower.turn).drives(follower.turn, law=lambda sources, target:
        lambda crank, own: crank*(.5+.5*(own < 2*crank-1)))

    def simulate(self):
        if self.follower.turn.value is None:
            self.follower.turn = -2


class StationaryFollower(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    follower = Arbor()
    (crank & follower.turn).drives(follower.turn, law=lambda sources, target:
        lambda crank, own: crank*(own < 2*crank+1))

    def simulate(self):
        if self.follower.turn.value is None:
            self.follower.turn = 2


class FollowingContact(AssemblyNode):
    """Diagnostic: a carried lever follows a rising pin on one affine piece.

    The inactive reset leaves the contact level constant; turning reset on
    would move the follower below the pin. This is not two opposing rates.
    """
    time = Time.running()
    crank = Driver(default=0)
    follower = Arbor()
    (crank & follower.turn).drives(follower.turn, law=lambda sources, target:
        lambda x, q: 32+(1+x/7) - .1*x*(q+4.2-(1+x/7) > 0))

    def simulate(self):
        if self.follower.turn.value is None:
            self.follower.turn = -3.2
