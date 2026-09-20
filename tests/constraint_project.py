# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Curta-shaped scope fixtures: real joints with stationary siblings."""

from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver
from .running_project.parts import Arbor, Block


class Drive(AssemblyNode):
    fixed = Block()
    disc = Arbor()


class ShaftBank(AssemblyNode):
    fixed = Block()
    ones = Arbor()


class Machine(AssemblyNode):
    crank = Driver(default=0)
    phase = Driver(default=4)
    drive = Drive()
    bank = ShaftBank()
    crank.drives(drive.disc.turn)
    phase.drives(bank.ones.turn)


class Flat(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    phase = Driver(default=4)
    shaft = Arbor()
    disc = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, Bound(
        lambda own, phase: 120 + phase, reads=(shaft.turn,)))))
    crank.drives(disc.turn)
    phase.drives(shaft.turn)


def nested_machine():
    class Nested(Machine):
        time = Time.running()
        Machine.drive.disc.turn.constrain(range=(None, Bound(
            lambda own, phase: 120 + phase, reads=(Machine.bank.ones.turn,))))
    return Nested


def limited_machine(high=90, running=True, clocked=False):
    from machinome.simulation import State

    class Limited(Machine):
        Machine.drive.disc.turn.constrain(range=(0, high))
    if running:
        class Running(Limited):
            time = Time.running()
        return Running
    if clocked:
        class Clocked(Limited):
            retained = State(default=0)
            Machine.crank.commits(
                retained,
                at=lambda source, target: lambda crank: crank >= 45,
                law=lambda source, target: lambda crank: 1)
        return Clocked
    return Limited


class NativeDrive(AssemblyNode):
    fixed = Block()
    disc = Arbor(turn=Revolute(axis=(0, 0, 1), range=(0, 90), unit='deg'))


class ScopedDrive(AssemblyNode):
    phase = Driver(default=5)
    request = Driver(default=0)
    fixed = Block()
    disc = Arbor(turn=Revolute(axis=(0, 0, 1), range=(0, 90), unit='deg'))
    request.drives(disc.turn)
    disc.turn.constrain(range=(None, Bound(
        lambda own, limit: 10+limit, reads=(phase,))))


class TwoCopies(AssemblyNode):
    time = Time.running()
    left = ScopedDrive()
    right = ScopedDrive()
    left.disc.turn.constrain(range=(None, 12))


class LocalDrive(AssemblyNode):
    setting = Revolute(axis=(0, 0, 1), unit='deg')
    fixed = Block()
    disc = Arbor(turn=Revolute(axis=(0, 0, 1), range=(0, Bound(
        lambda own, phase: 80+phase, reads=(setting,))), unit='deg'))


class SeveralScopes(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    local = Driver(default=20)
    outer = Driver(default=4)
    drive = LocalDrive()
    bank = ShaftBank()
    crank.drives(drive.disc.turn)
    local.drives(drive.setting)
    outer.drives(bank.ones.turn)
    drive.disc.turn.constrain(range=(None, Bound(
        lambda own, phase: 120+phase, reads=(bank.ones.turn,))))


class TwoTimeDrives(AssemblyNode):
    time = Time.running()
    release = Driver(default=2.5)
    drive = Drive()
    other = Arbor()
    time.drives(drive.disc.turn)
    time.drives(other.turn, ratio=2)
    drive.disc.turn.constrain(range=(None, Bound(
        lambda own, limit: limit, reads=(release,))))
