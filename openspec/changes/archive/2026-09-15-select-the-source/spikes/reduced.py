"""The note's reduced fixture, copied verbatim from the Curta project's
simulation/tools/shifted_carry_probe.py (read-only), so the spikes here
run it on THIS worktree."""

from solid_node.node import AssemblyNode
from solid_node.motion.joints import Revolute, Prismatic
from solid_node.motion.ports import Time
from solid_node.simulation import Driver, Sim, UnsupportedLaw


class Shaft(AssemblyNode):
    turn = Revolute(axis=(0, 0, 1))

    def simulate(self):
        if self.turn.value is None:
            self.turn = 0


class Latch(AssemblyNode):
    travel = Prismatic(axis=(0, 0, 1))

    def simulate(self):
        if self.travel.value is None:
            self.travel = 0


class ShiftedCarry(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0)
    shift = Driver(default=0)
    clearing = Driver(default=0)
    lower = Shaft()
    higher = Shaft()
    carry = Latch()
    (crank & shift & clearing & lower.turn).drives(lower.turn,
        law=lambda sources, target: lambda c, s, r, own:
        c * (s < .5) + r * (own > .5))
    (crank & shift & clearing & carry.travel & higher.turn).drives(higher.turn,
        law=lambda sources, target: lambda c, s, r, latch, own:
        c * (s >= .5) + c * (s < .5) * (latch >= .5) + r * (own > .5))
    (lower.turn & higher.turn & shift & carry.travel).drives(carry.travel,
        law=lambda sources, target: lambda lo, hi, s, own:
        (lo * (s < .5) + hi * (s >= .5)) * (own < 1))


class NoSelfRead(AssemblyNode):
    """The SAME union cycle with NO self-read in any relation, and rest
    defaults on every driven end (spike 2)."""
    time = Time.running()
    crank = Driver(default=0)
    shift = Driver(default=0)
    lower = Shaft()
    higher = Shaft()
    carry = Latch()
    (crank & shift).drives(lower.turn,
        law=lambda sources, target: lambda c, s: c * (s < .5))
    (crank & shift & carry.travel).drives(higher.turn,
        law=lambda sources, target: lambda c, s, latch:
        c * (s >= .5) + c * (s < .5) * (latch >= .5))
    (lower.turn & higher.turn & shift).drives(carry.travel,
        law=lambda sources, target: lambda lo, hi, s:
        lo * (s < .5) + hi * (s >= .5))


class Unguarded(AssemblyNode):
    """Same as NoSelfRead but the driven ends declare no rest default."""
    time = Time.running()
    crank = Driver(default=0)
    shift = Driver(default=0)

    class Bare(AssemblyNode):
        turn = Revolute(axis=(0, 0, 1))

    class BareLatch(AssemblyNode):
        travel = Prismatic(axis=(0, 0, 1))

    lower = Bare()
    higher = Bare()
    carry = BareLatch()
    (crank & shift).drives(lower.turn,
        law=lambda sources, target: lambda c, s: c * (s < .5))
    (crank & shift & carry.travel).drives(higher.turn,
        law=lambda sources, target: lambda c, s, latch:
        c * (s >= .5) + c * (s < .5) * (latch >= .5))
    (lower.turn & higher.turn & shift).drives(carry.travel,
        law=lambda sources, target: lambda lo, hi, s:
        lo * (s < .5) + hi * (s >= .5))


class FixedZero(AssemblyNode):
    """The GROUND TRUTH: the same three laws with `shift` frozen at the
    literal 0, which the framework orders correctly today."""
    time = Time.running()
    crank = Driver(default=0)
    clearing = Driver(default=0)
    lower = Shaft()
    higher = Shaft()
    carry = Latch()
    (crank & clearing & lower.turn).drives(lower.turn,
        law=lambda sources, target: lambda c, r, own: c + r * (own > .5))
    (crank & clearing & carry.travel & higher.turn).drives(higher.turn,
        law=lambda sources, target: lambda c, r, latch, own:
        c * (latch >= .5) + r * (own > .5))
    (lower.turn & carry.travel).drives(carry.travel,
        law=lambda sources, target: lambda lo, own: lo * (own < 1))


def probe():
    """Spike 1 and spike 2 in one run."""
    for label, klass in (('self-read cycle (the note\'s fixture)', ShiftedCarry),
                         ('the same cycle, no self-read, rest guards', NoSelfRead),
                         ('the same cycle, no self-read, no guards', Unguarded),
                         ('the ground truth, shift frozen at 0', FixedZero)):
        try:
            Sim(klass(), dt=.02)
            print(f'{label}: CONSTRUCTED')
        except Exception as error:
            print(f'{label}: {type(error).__name__}: {error}')
        print('---')


if __name__ == '__main__':
    probe()
