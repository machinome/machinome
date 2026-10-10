# Running self-read gates do not express unilateral pickup/release at a contact surface

## Symptom

The complex Vault with Combination Lock needs retained wheel collection under
`Time.running()`: a peg pushes a wheel when a flank reaches it, releases on
reversal, and crosses the clearance before picking up the opposite flank.
The attempted position-gated self-read relation instead pulls the wheel back
with the dial, or refuses at contact. Separate host controllers would be a
workaround, but are not the requested running model.

This is a **capability/semantics finding**, not a proven regression against
the current self-read specification. Positional engagement alone does not
state unilateral contact on a surface where driver and follower move together.

The needed behavior is pickup only when pushing a flank, immediate release
on reversal, retained wheel positions across clearance, opposite-flank
pickup, and agreement across partial commands, cadence and snapshot replay.
Any change to published running semantics also needs independently validated
viewer parity. Please ratify a caller-facing shape before implementation;
filing this report authorizes neither design nor implementation.

## Evidence

Framework development HEAD `b9b64ddaf0bc1d51d715d3d971b77b6ee58880bf`;
Python 3.12.3, Linux x86_64. Originating project checkpoint `78d4ceb`.
These are local development commits, not a claim about a published release.
Save this mesh-free reproduction as a Python file and run it in a project:

```python
from machinome.node import AssemblyNode
from machinome.motion.ports import Time
from machinome.motion.joints import Revolute
from machinome.simulation import Driver, Sim

class Wheel(AssemblyNode):
    turn = Revolute(axis=(1, 0, 0))

def pickup(sources, target):
    return lambda dial, held: dial * ((dial-held >= 3) + (dial-held <= -329))

class Pair(AssemblyNode):
    time = Time.running()
    dial = Driver(default=0, unit="deg")
    wheel = Wheel()
    (dial & wheel.turn).drives(wheel.turn, law=pickup)

    def simulate(self):
        if self.wheel.turn.value is None:
            self.wheel.turn = 0

sim = Sim(Pair(), dt=0.02)
for target in (2, 360, 1590):
    sim.move("dial", to=target, duration=1)
    sim.run(1)
assert sim.state["wheel.turn"] == 1587
sim.move("dial", to=1580, duration=1)
sim.run(1)
assert sim.state["wheel.turn"] == 1587  # actual: 1577
```

The failure repeats at dt 0.02, 0.01, 0.001 and 0.0001 s. Strict comparisons
also fail on the extended path `2, 360, 1590, 1580, 672, 720, 1182, 1140`:
three cadences raise `UnsupportedLaw`; dt 0.01 wrongly moves a wheel to 1049
instead of retaining 1001. The Vault's measured offsets can additionally
raise `TooManyCrossings`. Smaller ticks are not a reliable workaround.

Source analysis: ADR-121 and `_Walk._decide/_probe` start from the operator's
branch and flip only if its candidate path leaves the surface. Under the
engaged branch, dial and wheel move together; their difference stays 3 even
on reversal. Thus the current rule retains engagement. Inferring unilateral
release here requires a semantic decision, not merely loosening a tolerance.

Controls: all 42 existing self-read tests and 62 subtests pass. The originating
project's four running contracts yield one pass, one failure and two errors.
Geometry, assembly orientation and the source combination are separate issues.

## Skill text this would delete

No new skill workaround has been added. This asks for a capability, rather
than removal of an existing skill paragraph. It would avoid teaching another
project-owned Python/browser pickup controller, the workaround already
recorded in the local wart log for the earlier Combination safe lock project.
The current requirement to keep self-reads inside switches is not proposed
for deletion by this report.

## Proposed interface
