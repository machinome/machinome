# Evidence — `name-what-is-refused`

Cycle 2a of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`1ba1d3626eaeddeb6e543fd44baa6d32d81063e3` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`, and so did every probe. Every project
command ran as `env -C <project> PYTHONPATH=<bench>:<project>
/home/asa/devel/machinome/.venv/bin/<tool> ...`, with `<OMX>` =
`projects/Robotic-Arms/open_manipulator` (branch `frames-and-mates`,
`04f1188`, clean tree) and `<OpenArm>` = `projects/Robotic-Arms/openarm`
(branch `frames-and-mates`, `a59c006`, clean tree). `<scratch>` is the
campaign scratchpad's `cycle2a/` directory. Tools: `flake8` 7.3.0 (the
pyenv shim; the venv has none), `black` 26.5.1, `openspec` from the
workspace's Node install. One test run of ours at a time throughout.

## 1. Baseline on the unmodified tree (1ba1d36)

### 1.2 Focused tests

`pytest -q -p no:cacheprovider tests/test_joints.py tests/test_mates.py
tests/test_couplings.py tests/test_clocked_bounds.py
tests/test_running_reads.py tests/test_mate_existing_joint.py`:

```
603 passed, 1 warning, 954 subtests passed in 11.66s   (wall 12.76 s)
```

### 1.3 The probes

`env -C <scratch> PYTHONPATH=<bench> .venv/bin/python probe.py` and
`env -C <scratch> PYTHONPATH=<bench> .venv/bin/python clocked_probe.py`
(both exit 0) printed, byte for byte, what Stage P recorded (`diff` against
its `probe-base.txt` and `clocked-probe-base.txt`: no difference).
`env -C <OMX> PYTHONPATH=<bench>:<OMX> .venv/bin/python
<scratch>/omx_probe.py` (exit 0) likewise matched `omx-probe-base.txt`.
The rows that matter (`raised at` lines kept where they name the site):

```
=== 1. axis-less refusal
--- class body: slide = Prismatic(axis=None)
TypeError: Loose.slide is a Revolute without an axis. An axis may be left out only in a mate's freedom -- moving.on(fixed, Revolute(...)) -- where the moving frame supplies it; everywhere else a joint states the line it turns about: Revolute(axis=(x, y, z), ...).
    raised at machinome/motion/joints.py:392 in __set_name__
--- mate freedom: finger.origin.on(seat, Prismatic(axis=None))
TypeError: Finger.grip is a Revolute without an axis. [...]
--- declaration site: Slider(travel=Prismatic(axis=None))
TypeError: Slider.travel is a Revolute without an axis. [...]
--- class body: turn = Revolute() (control)
TypeError: Loose.turn is a Revolute without an axis. [...]
--- declaration site: Finger(turn=Revolute()) (control)
TypeError: site_revolute.<locals>.Axle: the joint 'turn' passed where Finger is declared is a Revolute without an axis. [...]
    raised at machinome/node/declarative.py:328 in __init__
--- Prismatic() with no argument (control)
TypeError: _MateFreedom.__init__() missing 1 required positional argument: 'axis'

=== 2. JointRangeError names the installed joint
--- Gripper().set_state(grip=21)
JointRangeError: wrist.palm.finger: joint 'grip' declares the range -11 to 20 mm, and 21 is outside it. A range refuses the binding rather than clamping it, because a pose outside the joint's travel is a mistake in what drives it.
    raised at machinome/motion/joints.py:696 in _refuse_out_of_range
--- Palm().grip = 21; render()
JointRangeError: finger: joint 'grip' declares the range -11 to 20 mm, and 21 is outside it. [...]
--- GatedPalm().set_state(gate=3, push=5)  (Bound reading a driver)
JointRangeError: finger: joint 'grip' -- the coordinate finger.grip -- declares the range 0 to 3 mm, and 5 is outside it. The bound reads other coordinates and is judged when the enumeration closes, over the values they hold there: GatedPalm (GatedPalm).gate = 3. [...]
    raised at machinome/motion/couplings.py:2862 in refuse_bounds
--- HeldGate().set_state(gate=3, push=5)  (the palm one level down)
JointRangeError: palm.finger: joint 'grip' -- the coordinate palm.finger.grip -- declares the range 0 to 3 mm, and 5 is outside it. [...] palm.gate = 3. [...]
--- tests.mate_project.slide.Palm(); left_grip = 25; render()
    root name: 'Palm'
JointRangeError: left_finger: joint 'left_grip' declares the range -11 to 20 mm, and 25 is outside it. [...]
--- SitePalm().finger.grip = 21 (site joint, control)
JointRangeError: finger (Finger): joint 'grip' declares the range -11 to 20 mm, and 21 is outside it. [...]

=== 3. a.drives(a), one to one
--- class definition of wheel.turn.drives(wheel.turn)
accepted: <class '__main__.declare_self_relation.<locals>.Selfish'>
--- render at rest, nothing bound
UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either end. wheel.turn and wheel.turn are both unbound when nothing changes any more, so the relation has no side to be read from. Bind one of them in simulate(), or state a relation that reaches one.
    raised at machinome/motion/couplings.py:3242 in _refuse
--- bind wheel.turn = 30, render
DoublyBound: wheel.turn would be bound by the relation wheel.turn drives wheel.turn and by the author's simulate(). [...]
--- DrivenSelf().set_state(crank=10)
DoublyBound: wheel.turn would be bound by the relation wheel.turn drives wheel.turn and by the relation crank drives wheel.turn. [...]
--- LawSelf().render() at rest / Sim(Spun(), 0.1).run(0.1)
UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either end. [...]
--- Mounted().render() at rest
UnreachedCoordinate: mount drives body.turn: nothing bound either end. body.turn and body.turn are both unbound [...]
--- crank.drives(crank) on a Driver
TypeError: driver 'crank' cannot be the driven end of a relation: [...]
--- Ported().render() at rest
UnreachedCoordinate: turn drives turn: nothing bound either end. Ported (Ported).turn and Ported (Ported).turn are both unbound [...]
--- wheels.turn.drives(wheels.turn) over a repeat
TypeError: 'wheels.turn' passes through the repeated declaration 'wheels' of Wheel (count=3), so it cannot be the SOURCE of a relation: [...]
--- Inferred().render() at rest
UnreachedCoordinate: wheel drives wheel.turn: nothing bound either end. [...]
--- (crank & wheel.turn).drives(wheel.turn) (several ends, control)
accepted: <class '__main__.declare_several.<locals>.Pair'>
```

Every class definition in section 3 of the probe was accepted, save the
`Driver` and the repeat controls.

`clocked_probe.py`:

```
--- Sim(MatedShut(), record=8).move("crank", by=400.0)
bounds: [('shutter.travel', 'low'), ('shutter.travel', 'high')]
JointRangeError: shutter: joint 'travel' -- the coordinate 'shutter.travel' -- declares a high bound of 0.0 mm, and the request move('crank', by=400.0) ends with it at 3.0, which is outside it. The clip read that bound over the bank the request STARTED from; an event inside the request committed a state that moved it. The request committed nothing: the bank, the tree and the record stand as they were. Split the request at that event.
--- a root Palm: name 'Palm' parent of finger is palm: False
```

(The last line: an unrendered root `Palm`'s child is not linked yet; it is
linked by the render that binds it, which is when the refusal is raised.)

`omx_probe.py` (each refusal raised at `machinome/motion/joints.py:696` in
`_refuse_out_of_range`, reached from `couplings.py:2577` `apply`):

```
--- OpenManipulatorX.set_state(grip=21)
machinome.motion.joints.JointRangeError: arm.link2.link3.link4.link5.left_finger: joint 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. A range refuses the binding rather than clamping it, because a pose outside the joint's travel is a mistake in what drives it.
--- OpenManipulatorX.set_state(grip=-12)
machinome.motion.joints.JointRangeError: arm.link2.link3.link4.link5.left_finger: joint 'left_travel' declares the range -11.0 to 20.0 mm, and -12 is outside it. [...]
--- Link5Assembly().left_travel = 21; render()
machinome.motion.joints.JointRangeError: left_finger: joint 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. [...]
--- Link5Assembly().right_travel = 21; render()
machinome.motion.joints.JointRangeError: left_finger: joint 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. [...]
```

(The fourth case names `left_travel` before and after the change: the
project's mimic reaches the left finger's range first. Not this change's.)

The probes' sources, since the scratchpad is not durable. `probe.py` and
`clocked_probe.py` sit beside a `pyproject.toml` holding only:

```toml
# A manifest so the probe's nodes find a project root; nothing is built.
[tool.machinome]
model = "probe:Nothing"
```

`probe.py`:

```python
"""Reproduce name-what-is-refused on the bench: the three messages.

Run as:
  env -C <scratch> PYTHONPATH=<bench> .venv/bin/python probe.py
"""

import traceback

from solid2 import cube

import machinome
from machinome.motion.joints import Bound, Prismatic, Revolute
from machinome.node.assembly import AssemblyNode
from machinome.node.frames import Frame
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver, Sim, State

print('machinome:', machinome.__file__)


def attempt(label, action):
    print(f'--- {label}')
    try:
        result = action()
    except Exception as failure:  # noqa: BLE001 - a probe prints any refusal
        print(f'{type(failure).__name__}: {failure}')
        frame = traceback.extract_tb(failure.__traceback__)[-1]
        print(f'    raised at {frame.filename.split("WTs/fix-warts-3/")[-1]}'
              f':{frame.lineno} in {frame.name}')
        return None
    print('accepted' + ('' if result is None else f': {result}'))
    return result


class Finger(Solid2Node):
    origin = Frame()

    def render(self):
        return cube(2, center=True)


class Wheel(Solid2Node):
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cube(2, center=True)


##############################################
# 1. The axis-less refusal

print('\n=== 1. axis-less refusal')


def class_body_prismatic():
    class Loose(Solid2Node):
        slide = Prismatic(axis=None, unit='mm')

        def render(self):
            return cube(1, center=True)


def mate_freedom_prismatic():
    class Palm(AssemblyNode):
        seat = Frame(at=(10, 0, 0))
        finger = Finger()
        grip = finger.origin.on(seat, Prismatic(axis=None, range=(0, 5),
                                                unit='mm'))


def site_prismatic():
    class Slider(Solid2Node):
        def render(self):
            return cube(1, center=True)

    class Rail(AssemblyNode):
        car = Slider(travel=Prismatic(axis=None, unit='mm'))

    return Rail().car


def class_body_revolute():
    class Loose(Solid2Node):
        turn = Revolute(unit='deg')

        def render(self):
            return cube(1, center=True)


def site_revolute():
    class Axle(AssemblyNode):
        wheel = Finger(turn=Revolute())


def prismatic_without_axis():
    Prismatic()


attempt('class body: slide = Prismatic(axis=None)', class_body_prismatic)
attempt('mate freedom: finger.origin.on(seat, Prismatic(axis=None))',
        mate_freedom_prismatic)
attempt('declaration site: Slider(travel=Prismatic(axis=None))',
        site_prismatic)
attempt('class body: turn = Revolute() (control)', class_body_revolute)
attempt('declaration site: Finger(turn=Revolute()) (control)', site_revolute)
attempt('Prismatic() with no argument (control)', prismatic_without_axis)


##############################################
# 2. JointRangeError on a mate's coordinate

print('\n=== 2. JointRangeError names the installed joint')


class Palm(AssemblyNode):
    seat = Frame(at=(81.7, 21.0, 0.0))
    finger = Finger()
    grip = finger.origin.on(seat, Prismatic(axis=(0, 1, 0), range=(-11, 20),
                                            unit='mm'))


class Wrist(AssemblyNode):
    palm = Palm()


class Gripper(AssemblyNode):
    grip = Driver(default=0.0, unit='mm')
    wrist = Wrist()
    grip.drives(wrist.palm.grip)


def gripper(value):
    def run():
        Gripper().set_state(grip=value)
    return run


def palm_alone(value):
    def run():
        palm = Palm()
        palm.grip = value
        palm.render()
    return run


attempt('Gripper().set_state(grip=21)', gripper(21))
attempt('Palm().grip = 21; render()', palm_alone(21))


class GatedPalm(AssemblyNode):
    """A mate's range whose upper bound READS another coordinate: judged
    when the enumeration closes (couplings.refuse_bounds)."""

    gate = Driver(default=0.0, unit='mm')
    push = Driver(default=0.0, unit='mm')
    seat = Frame(at=(10, 0, 0))
    finger = Finger()
    grip = finger.origin.on(seat, Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(0, Bound(lambda own, gate: gate, reads=(gate,)))))
    push.drives(grip)


class GatedRoot(AssemblyNode):
    gate = Driver(default=0.0, unit='mm')
    push = Driver(default=0.0, unit='mm')
    palm = GatedPalm()


def gated(value, gate):
    def run():
        GatedPalm().set_state(gate=gate, push=value)
    return run


attempt('GatedPalm().set_state(gate=3, push=5)  (Bound reading a driver)',
        gated(5, 3))


class PortGatedPalm(AssemblyNode):
    """`GatedPalm` reading a PORT, so it can be held under a root."""

    from machinome.motion.ports import TranslationalPort

    gate = TranslationalPort(unit='mm')
    seat = Frame(at=(10, 0, 0))
    finger = Finger()
    grip = finger.origin.on(seat, Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(0, Bound(lambda own, gate: gate, reads=(gate,)))))


class HeldGate(AssemblyNode):
    gate = Driver(default=0.0, unit='mm')
    push = Driver(default=0.0, unit='mm')
    palm = PortGatedPalm()
    gate.drives(palm.gate)
    push.drives(palm.grip)


attempt('HeldGate().set_state(gate=3, push=5)  (the palm one level down)',
        lambda: HeldGate().set_state(gate=3, push=5))


def root_slide_palm():
    import sys
    sys.path.insert(0, '/home/asa/devel/machinome/machinome/WTs/fix-warts-3')
    from tests.mate_project.slide import Palm as SlidePalm

    palm = SlidePalm()
    print('    root name:', repr(palm.name))
    palm.left_grip = 25
    palm.render()


attempt('tests.mate_project.slide.Palm(); left_grip = 25; render()',
        root_slide_palm)


class SitePalm(AssemblyNode):
    """The same finger with a SITE-declared joint, for comparison."""

    finger = Finger(grip=Prismatic(axis=(0, 1, 0), range=(-11, 20),
                                   unit='mm'))


def site_palm(value):
    def run():
        palm = SitePalm()
        palm.finger.grip = value
        palm.render()
    return run


attempt('SitePalm().finger.grip = 21 (site joint, control)', site_palm(21))


##############################################
# 3. a.drives(a), one to one

print('\n=== 3. a.drives(a), one to one')


def declare_self_relation():
    class Selfish(AssemblyNode):
        wheel = Wheel()
        wheel.turn.drives(wheel.turn)

    return Selfish


Selfish = attempt('class definition of wheel.turn.drives(wheel.turn)',
                  declare_self_relation)

if Selfish is not None:
    def realize():
        Selfish()

    def render_rest():
        node = Selfish()
        node.render()

    def bound():
        node = Selfish()
        node.wheel.turn = 30
        node.render()
        return node.wheel.turn.value

    attempt('realize Selfish()', realize)
    attempt('render at rest, nothing bound', render_rest)
    attempt('bind wheel.turn = 30, render', bound)


def declare_driven_root():
    class DrivenSelf(AssemblyNode):
        crank = Driver(default=0.0, unit='deg')
        wheel = Wheel()
        crank.drives(wheel.turn)
        wheel.turn.drives(wheel.turn, ratio=1)

    return DrivenSelf


DrivenSelf = attempt('class definition with a driver also driving the end',
                     declare_driven_root)
if DrivenSelf is not None:
    attempt('DrivenSelf().set_state(crank=10)',
            lambda: DrivenSelf().set_state(crank=10))


def declare_law_self():
    def law(driver, driven):
        return lambda turn: turn + 1

    class LawSelf(AssemblyNode):
        wheel = Wheel()
        wheel.turn.drives(wheel.turn, law=law)

    return LawSelf


LawSelf = attempt('class definition of a law= self relation',
                  declare_law_self)
if LawSelf is not None:
    attempt('LawSelf().render() at rest', lambda: LawSelf().render())


def declare_running():
    from machinome.motion.ports import Time

    class Spun(AssemblyNode):
        time = Time.running()
        wheel = Wheel()
        wheel.turn.drives(wheel.turn)

    return Spun


Spun = attempt('class definition under a running root', declare_running)
if Spun is not None:
    attempt('Sim(Spun(), 0.1).run(0.1)',
            lambda: Sim(Spun(), 0.1).run(0.1))


class Axled(Solid2Node):
    axle = Frame()
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cube(2, center=True)


def declare_alias():
    class Mounted(AssemblyNode):
        seat = Frame(at=(5, 0, 0))
        body = Axled()
        mount = body.axle.on(seat, body.turn)
        mount.drives(body.turn)

    return Mounted


Mounted = attempt('mount = body.axle.on(seat, body.turn); '
                  'mount.drives(body.turn) (an alias of one coordinate)',
                  declare_alias)
if Mounted is not None:
    attempt('Mounted().render() at rest', lambda: Mounted().render())


def declare_driver_self():
    class Cranked(AssemblyNode):
        crank = Driver(default=0.0, unit='deg')
        crank.drives(crank)


def declare_port_self():
    from machinome.motion.ports import RotationalPort

    class Ported(AssemblyNode):
        turn = RotationalPort(unit='deg')
        turn.drives(turn)

    return Ported


def declare_broadcast_self():
    class Wheels(AssemblyNode):
        wheels = Wheel().repeat(3)
        wheels.turn.drives(wheels.turn)

    return Wheels


attempt('crank.drives(crank) on a Driver', declare_driver_self)
Ported = attempt('turn.drives(turn) on a port of the class', declare_port_self)
if Ported is not None:
    attempt('Ported().render() at rest', lambda: Ported().render())
Wheels = attempt('wheels.turn.drives(wheels.turn) over a repeat',
                 declare_broadcast_self)
if Wheels is not None:
    attempt('Wheels().render() at rest', lambda: Wheels().render())


def declare_inferred():
    class Inferred(AssemblyNode):
        wheel = Wheel()
        wheel.drives(wheel.turn)

    return Inferred


Inferred = attempt('wheel.drives(wheel.turn) (the node standing for its one '
                   'joint)', declare_inferred)
if Inferred is not None:
    attempt('Inferred().render() at rest', lambda: Inferred().render())


def declare_several():
    class Pair(AssemblyNode):
        crank = Driver(default=0.0, unit='deg')
        wheel = Wheel()

        def law(sources, targets):
            return lambda crank, turn: crank

        (crank & wheel.turn).drives(wheel.turn, law=law)

    return Pair


attempt('(crank & wheel.turn).drives(wheel.turn) (several ends, control)',
        declare_several)
```

`clocked_probe.py`:

```python
"""Finding 2's sibling paths: a mate's ranged coordinate under a CLOCKED
root (clocked.py) and the name a root palm is given.

Run as:
  env -C <scratch> PYTHONPATH=<bench>:<bench>/tests/.. .venv/bin/python clocked_probe.py
"""

from solid2 import cube

from machinome.motion.joints import Bound, Prismatic
from machinome.node.assembly import AssemblyNode
from machinome.node.frames import Frame
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver, Sim, State

from tests.clocked_project.gate import hundredth, reaches, shuts


class Carriage(Solid2Node):
    origin = Frame()

    def render(self):
        return cube([20, 6, 6], center=True)


class MatedShut(AssemblyNode):
    """`tests/clocked_project/gate.py`'s `Shut`, its shutter placed by a
    mate whose freedom carries the range."""

    crank = Driver(default=0.0, unit='deg')
    shutting = State(default=0, dtype=int)

    seat = Frame()
    shutter = Carriage()
    travel = shutter.origin.on(seat, Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(0, Bound(lambda travel, shut: 3 - 3 * shut,
                        reads=(shutting,)))))

    (crank & shutting).commits(shutting, at=reaches, law=shuts)

    crank.drives(travel, law=hundredth)


print('--- Sim(MatedShut(), record=8).move("crank", by=400.0)')
try:
    sim = Sim(MatedShut(), record=8)
    print('bounds:', [(entry.coordinate, entry.side)
                      for entry in sim._clocked.bounds])
    sim.move('crank', by=400.0)
    print('accepted')
except Exception as failure:  # noqa: BLE001
    print(f'{type(failure).__name__}: {failure}')


class Palm(AssemblyNode):
    seat = Frame(at=(81.7, 21.0, 0.0))
    finger = Carriage()
    grip = finger.origin.on(seat, Prismatic(axis=(0, 1, 0), range=(-11, 20),
                                            unit='mm'))


palm = Palm()
print('--- a root Palm: name', repr(palm.name), 'parent of finger is palm:',
      palm.finger._parent is palm)
```

`omx_probe.py`, run from `<OMX>`:

```python
"""Finding 2 probe: the message OpenMANIPULATOR-X's out-of-range grip and
finger bindings are refused with. Run from the project root with
PYTHONPATH=<bench>:<project>."""

import traceback

import machinome
from machinome.motion.joints import JointRangeError

from simulation.open_manipulator_x import Link5Assembly, OpenManipulatorX

print("machinome:", machinome.__file__)


def attempt(label, action):
    print(f"--- {label}")
    try:
        action()
    except Exception as failure:  # noqa: BLE001 - a probe prints any refusal
        print(f"{type(failure).__module__}.{type(failure).__name__}: {failure}")
        frames = traceback.extract_tb(failure.__traceback__)
        for frame in frames[-4:]:
            print(f"    at {frame.filename}:{frame.lineno} in {frame.name}")
        return
    print("accepted")


def grip(value):
    def run():
        root = OpenManipulatorX()
        root.set_state(base_yaw=0.0, shoulder=0.0, elbow=0.0, wrist=0.0,
                       grip=value)
        root.assemble()
    return run


def palm(value):
    def run():
        node = Link5Assembly()
        node.left_travel = value
        node.render()
    return run


def palm_right(value):
    def run():
        node = Link5Assembly()
        node.right_travel = value
        node.render()
    return run


attempt("OpenManipulatorX.set_state(grip=21)", grip(21))
attempt("OpenManipulatorX.set_state(grip=-12)", grip(-12))
attempt("Link5Assembly().left_travel = 21; render()", palm(21))
attempt("Link5Assembly().right_travel = 21; render()", palm_right(21))
```

### 1.4 The originating projects' suites, unmodified bench

Each alone. The pytest commands add `-p no:cacheprovider` to the README's
`python -m pytest simulation/test_frames.py` so nothing is written into the
project.

| project | command | result | wall |
|---|---|---|---|
| OpenMANIPULATOR-X | `python -m pytest -q -p no:cacheprovider simulation/test_frames.py` | 11 passed in 1.70s | 2.14 s |
| OpenMANIPULATOR-X | `machinome test --mesh simulation/open_manipulator_x.py:OpenManipulatorX` | exit 0, `Ran 4 tests in 1.51 seconds: 4 passed, 0 failed (mesh engine, volume epsilon 0 mm³)` | 2.50 s |
| OpenArm | `python -m pytest -q -p no:cacheprovider simulation/test_frames.py` | 10 passed in 5.25s | 5.70 s |

`git -C <OMX> status --short` and `git -C <OpenArm> status --short` before:
empty, both.

## 2. Red tests, on the unmodified source (1ba1d36)

New tests, no existing test edited (the only removed lines in `git diff
tests` are two import lines of `tests/test_clocked_bounds.py`, widened):

- 2.1 `tests/test_joints.py::AxislessKindTest` (new class after
  `AxislessRevoluteTest`):
  `test_a_class_body_prismatic_without_an_axis_names_its_kind`,
  `test_a_site_prismatic_without_an_axis_names_the_declaring_class`,
  `test_an_orbit_without_an_axis_names_its_kind`;
- 2.2 `tests/test_mates.py::SlidingMateTest::test_a_prismatic_freedom_written_axis_none_names_the_mate`;
- 2.3 `tests/test_mates.py::SlidingMateTest::test_a_range_refusal_on_a_mates_joint_names_the_mate`
  (the slide fixture's `Gripper` posed at `grip=25`, and its `Palm` alone,
  `left_grip = 25` and `render()` inside one `assertRaises`);
- 2.4 `tests/test_mates.py::SlidingMateTest::test_a_bound_judged_at_the_close_names_the_mate`
  (the probe's `PortGatedPalm` held by `HeldGate`, defined in the test);
- 2.5 `tests/test_clocked_bounds.py::RefusalTest::test_a_commit_out_of_a_mates_range_names_the_mate`,
  with `MatedCarriage` and `MatedShut` defined in the module (the probe's
  `MatedShut`, importing `hundredth`, `reaches`, `shuts` from
  `tests/clocked_project/gate.py`);
- 2.6 `tests/test_couplings.py::SelfReadTest::test_a_relation_whose_one_source_is_its_driven_end_is_refused`
  (five subtests: `written`, `with_a_law`, `own_port`, `inferred`,
  `reused_joint_mate`), with a module-level fixture `OneTurn`;
- 2.7 GUARD `tests/test_couplings.py::SelfReadTest::test_the_end_checks_and_the_read_stand_beside_it`.

One pytest process with all nine (log `<scratch>/red.txt`):

```
24 failed, 2 passed, 6 subtests passed in 2.65s
```

(pytest-subtests counts every failing subtest, and counts a test whose only
failures are subtests as passed; the two "passed" are 2.7 and the 2.6 test
body, whose five subtests all failed.) The reasons, verbatim:

- 2.1 class body (`tests/test_joints.py:4850`/`:4861`): `'Prismatic' not
  found in "Loose.slide is a Revolute without an axis. An axis may be left
  out only in a mate's freedom -- moving.on(fixed, Revolute(...)) -- where
  the moving frame supplies it; ..."`, likewise `"a mate's freedom
  included"` and `'required everywhere'`, and `'is a Revolute' unexpectedly
  found`.
- 2.1 site: `'Rail' not found in "Slider.travel is a Revolute without an
  axis. ..."`, likewise `'Prismatic'`, `'required everywhere'`, and `'is a
  Revolute' unexpectedly found`.
- 2.1 orbit: `'an Orbit' not found in "Loose.orbit is a Revolute without an
  axis. ..."`, `'required everywhere'` likewise, `'is a Revolute'
  unexpectedly found`.
- 2.2 (`tests/test_mates.py:2448`/`:2449`): `'Palm.grip' not found in
  "Finger.grip is a Revolute without an axis. ..."`, likewise `"the mate's
  freedom"`, `'Prismatic'`, `'required everywhere'`; `'is a Revolute'
  unexpectedly found`.
- 2.3 (`tests/test_mates.py:2458`): `False is not true : wrist.palm.left_finger:
  joint 'left_grip' declares the range -11 to 20 mm, and 25 is outside it.
  ...`
- 2.4 (`tests/test_mates.py:2497`): `"palm: mate 'grip' -- the coordinate
  palm.grip --" not found in "palm.finger: joint 'grip' -- the coordinate
  palm.finger.grip -- declares the range 0 to 3 mm, and 5 is outside it.
  ..."`
- 2.5 (`tests/test_clocked_bounds.py:145`): `"mate 'travel' -- the
  coordinate 'shutter.travel' --" not found in "shutter: joint 'travel' --
  the coordinate 'shutter.travel' -- declares a high bound of 0.0 mm, ..."`
- 2.6, each of the five subtests (`tests/test_couplings.py:3847` via
  `_class_body`, `:3693`): `AssertionError: TypeError not raised` — every
  class was created.

2.7 alone on the unmodified source:

```
PASSED tests/test_couplings.py::SelfReadTest::test_the_end_checks_and_the_read_stand_beside_it
1 passed, 2 subtests passed in 0.27s
```

## 3. The change

- `machinome/motion/joints.py`:
  - `axisless_refusal(kind, where)` in place of `(owner, name, site=None)`:
    the `Revolute` text unchanged after `where`; any other kind "`{where}`
    is a/an `{kind}` without an axis. A/An `{kind}`'s axis is required
    everywhere[, a mate's freedom included]: `{kind}(axis=(x, y, z), ...)`.
    Only a Revolute may leave its axis out, and only as a mate's freedom,
    where the moving frame supplies it.", the bracketed clause for a
    `Prismatic` only.
  - `Joint.__set_name__` names `{mate.owner.__name__}.{mate.name}: the mate's
    freedom` when `installed_by` is set, else `{owner}.{name}` as before,
    and passes `type(self)`; the kind is told by `issubclass` and shown by
    its `__name__` (see §4.3 for why: the first implementation compared
    the name with strings).
  - `_binding_site(node, joint)` beside `_where`, as design.md Decision 2
    states it; `_refuse_out_of_range`'s two messages and `_bound_at`'s two
    take their head from it. It is called only on the refusal branches, so
    an accepted binding pays nothing for it.
- `machinome/node/declarative.py`: the site check in
  `ChildDeclaration.__init__` covers `Revolute`, `Prismatic` and `Orbit`
  with `axis is None`, building `where` as before and passing the kind,
  `type(value)`.
- `machinome/motion/couplings.py`: `refuse_bounds`'s two messages and
  `_bound_side`'s one take their head from `_binding_site` (its second
  value is held as `coordinate` there, `named` being the read values'
  name in `refuse_bounds`); `_names_one_coordinate(driver_ref, driven_ref)`
  and `_refuse_one_source_driving_itself(driver_ref, driven_ref)` beside
  `_self_read_index`; `relate` raises the latter after the end checks when
  the relation does not name several ends and the former holds.
- `machinome/simulation/clocked.py`: `_constrained`'s `refuse` and
  `_commit_out_of_range` take their head from `_binding_site`, the bank id
  quoted as before.

Green, step by step:

- after 3.1: `AxislessKindTest`, `AxislessRevoluteTest` and 2.2 — `8
  passed, 27 subtests passed in 1.12s`;
- after 3.2: 2.3 — `1 passed in 1.00s`;
- after 3.3: 2.4 — `1 passed in 1.06s`;
- after 3.4: 2.5 and its guard
  `AuthorityTest::test_a_commit_out_of_range_refuses_the_request_by_name`
  (a site joint, `"joint 'travel'"`) — `2 passed in 1.12s`;
- after 3.5: all of `SelfReadTest` (2.6, 2.7 and the five existing) — `7
  passed, 15 subtests passed in 1.22s`. Every spelling of 2.6 is caught by
  the comparison; none needed widening.

3.6, `grep -n "_where(node)}: joint '\|_where(bounded.node)}: joint '"
machinome/` (recursive):

```
machinome/motion/joints.py:514:                    f"{_where(node)}: joint '{self.name}' is generated by "
machinome/motion/joints.py:519:                f"{_where(node)}: joint '{self.name}' is declared at the "
machinome/motion/joints.py:846:                    f"{_where(node)}: joint '{self.name}' cannot be placed, "
machinome/motion/joints.py:1126:                f"{_where(node)}: joint '{self.name}' carries a point "
```

`declarer_of`'s two, the site-only placement refusal and the `Orbit` one:
no range refusal that can judge a mate's joint.

3.7, the focused set of 1.2, no existing test edited:

```
612 passed, 1 warning, 977 subtests passed in 12.34s   (wall 13.52 s)
```

(603 + the nine new tests.)

## 4. Framework validation

### 4.1 Lint

`flake8 --max-line-length=89` on the eight touched Python files, compared
file by file with the same command on their `HEAD` text (`git show
HEAD:<file> | flake8 --max-line-length=89 -`), counts now / at `HEAD`:
`couplings.py` 23/23, `joints.py` 5/5, `declarative.py` 2/3,
`clocked.py` 2/2, `test_clocked_bounds.py` 0/0, `test_couplings.py` 18/18,
`test_joints.py` 38/38, `test_mates.py` 3/3. No new finding: the widened
import in `declarative.py` first added one E127 (over-indented
continuation), which was fixed by breaking the import after its
parenthesis, which also removed the E127 that line had at `HEAD`.

`black --check --target-version py312` exits 1 for each of the eight files
and for each file's `HEAD` text alike: the repository is not
black-formatted. (Without `--target-version`, black 26.5.1 warns that
Python 3.12 cannot parse code formatted for 3.15.) The new code follows
the surrounding style.

### 4.2 The probes after the change

Both exit 0. `diff` against the before outputs: every changed line is one
of the three findings; every control row reads as before but for the line
number it is raised at.

Finding 1:

```
TypeError: Loose.slide is a Prismatic without an axis. A Prismatic's axis is required everywhere, a mate's freedom included: Prismatic(axis=(x, y, z), ...). Only a Revolute may leave its axis out, and only as a mate's freedom, where the moving frame supplies it.
TypeError: Palm.grip: the mate's freedom is a Prismatic without an axis. A Prismatic's axis is required everywhere, a mate's freedom included: [...]
TypeError: site_prismatic.<locals>.Rail: the joint 'travel' passed where Slider is declared is a Prismatic without an axis. A Prismatic's axis is required everywhere, a mate's freedom included: [...]
    raised at machinome/node/declarative.py:333 in __init__
```

Controls unchanged: `Loose.turn is a Revolute without an axis. ...`,
`site_revolute.<locals>.Axle: the joint 'turn' passed where Finger is
declared is a Revolute without an axis. ...`, and `Prismatic()`'s
`_MateFreedom.__init__() missing 1 required positional argument: 'axis'`.

Finding 2:

```
JointRangeError: wrist.palm: mate 'grip' declares the range -11 to 20 mm, and 21 is outside it. [...]
JointRangeError: Palm (Palm): mate 'grip' declares the range -11 to 20 mm, and 21 is outside it. [...]
JointRangeError: GatedPalm (GatedPalm): mate 'grip' -- the coordinate GatedPalm (GatedPalm).grip -- declares the range 0 to 3 mm, and 5 is outside it. [...] GatedPalm (GatedPalm).gate = 3. [...]
JointRangeError: palm: mate 'grip' -- the coordinate palm.grip -- declares the range 0 to 3 mm, and 5 is outside it. [...] palm.gate = 3. [...]
JointRangeError: Palm (Palm): mate 'left_grip' declares the range -11 to 20 mm, and 25 is outside it. [...]
```

The control, a site joint, is unchanged: `finger (Finger): joint 'grip'
declares the range -11 to 20 mm, and 21 is outside it. ...`. Where the
assembly stating the mate is the root, `_where` names it by its name and
class, and design.md Decision 2's form for the enumeration's close then
reads `the coordinate GatedPalm (GatedPalm).grip`, as the read values of
the same message already read `GatedPalm (GatedPalm).gate`.

`clocked_probe.py`:

```
JointRangeError: MatedShut (MatedShut): mate 'travel' -- the coordinate 'shutter.travel' -- declares a high bound of 0.0 mm, and the request move('crank', by=400.0) ends with it at 3.0, which is outside it. [...]
```

Finding 3: every one-to-one spelling is refused at class definition,
`raised at machinome/motion/couplings.py:2426 in relate`, where each was
accepted and refused only at its first enumeration:

```
TypeError: wheel.turn drives wheel.turn: the relation's one source, wheel.turn, is its own driven end, wheel.turn. A relation naming one coordinate at each end computes the driven value from the source's, and here there is no other value to compute it from: bound at either end it is the same coordinate bound twice, and bound at neither nothing reaches it. Drive wheel.turn from another coordinate; a law that reads the coordinate it drives names another source beside it, (source & wheel.turn).drives(wheel.turn, law=...), under a root declaring time = Time.running().
TypeError: mount drives body.turn: the relation's one source, mount, is its own driven end, body.turn. [...]
TypeError: turn drives turn: the relation's one source, turn, is its own driven end, turn. [...]
TypeError: wheel drives wheel.turn: the relation's one source, wheel, is its own driven end, wheel.turn. [...]
```

(`Selfish`, `DrivenSelf` with `ratio=1`, `LawSelf` and `Spun` all read the
first message.) Controls unchanged: `crank.drives(crank)`'s driver
refusal, `wheels.turn.drives(wheels.turn)`'s repeat refusal, and `(crank &
wheel.turn).drives(wheel.turn, law=...)` accepted.

### 4.3 Full suite

Run alone, after section 8 (`pytest -q -p no:cacheprovider` at the bench
root). The first run:

```
FAILED tests/test_no_class_name_recognition.py::NoClassNameComparisonTest::test_no_core_module_compares_a_class_name_to_a_string
1 failed, 4622 passed, 4 skipped, 55 warnings, 6611 subtests passed in 650.67s (0:10:50)   (wall 653.2 s)
```

with `('machinome/motion/joints.py', 1507, "kind == 'Revolute'", 'compares
a string spelling the class Revolute')` and the same for `'Prismatic'`: the
first implementation passed `axisless_refusal` the joint's class NAME and
compared it with strings, which `node-model`'s "No node type is recognised
by its class name" (ADR-166) forbids in the core. The evidence decided: the
kind is now passed as its class, told by `issubclass(kind, Revolute)` and
`issubclass(kind, Prismatic)` and shown by `kind.__name__`; both callers
pass `type(...)`. design.md Decision 1 and tasks.md 3.1 are revised in
place to say so. After the fix, `tests/test_no_class_name_recognition.py`,
`AxislessKindTest`, `AxislessRevoluteTest` and `SlidingMateTest`: `24
passed, 4 warnings, 48 subtests passed in 4.54s`; `probe.py` printed
exactly what it printed before the fix (`diff`: none); `flake8` on
`joints.py` 5 and `declarative.py` 2, as in §4.1.

The second run, alone, on the final tree:

```
4623 passed, 4 skipped, 55 warnings, 6611 subtests passed in 652.16s (0:10:52)   (wall 654.6 s)
```

`git status` after it shows no change under `tests/base_documents/` or
anywhere outside the files this change touched.

## 5. Validation in OpenMANIPULATOR-X and OpenArm (read only)

### 5.1 The probe after the change

`env -C <OMX> PYTHONPATH=<bench>:<OMX> .venv/bin/python
<scratch>/omx_probe.py` (exit 0):

```
--- OpenManipulatorX.set_state(grip=21)
machinome.motion.joints.JointRangeError: arm.link2.link3.link4.link5: mate 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. A range refuses the binding rather than clamping it, because a pose outside the joint's travel is a mistake in what drives it.
--- OpenManipulatorX.set_state(grip=-12)
machinome.motion.joints.JointRangeError: arm.link2.link3.link4.link5: mate 'left_travel' declares the range -11.0 to 20.0 mm, and -12 is outside it. [...]
--- Link5Assembly().left_travel = 21; render()
machinome.motion.joints.JointRangeError: Link5Assembly (Link5Assembly): mate 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. [...]
--- Link5Assembly().right_travel = 21; render()
machinome.motion.joints.JointRangeError: Link5Assembly (Link5Assembly): mate 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it. [...]
```

### 5.2 Its documented suites, and OpenArm's, after the change

| project | command | before | after |
|---|---|---|---|
| OpenMANIPULATOR-X | `python -m pytest -q -p no:cacheprovider simulation/test_frames.py` | 11 passed, 2.14 s | 11 passed in 1.51s, 1.94 s |
| OpenMANIPULATOR-X | `machinome test --mesh simulation/open_manipulator_x.py:OpenManipulatorX` | 4 passed (1.51 s), 2.50 s | exit 0, 4 passed, 0 failed (1.72 s), 2.75 s |
| OpenArm | `python -m pytest -q -p no:cacheprovider simulation/test_frames.py` | 10 passed, 5.70 s | 10 passed in 5.32s, 5.76 s |

OpenMANIPULATOR-X's guard `test_a_finger_binding_past_the_urdf_limit_is_refused`
asserts `left_travel` in the message; OpenArm's two range guards assert the
mate's name and `r"finger[12]_turn"`: every new head carries the mate's
name. `git -C <OMX> status --short` and `git -C <OpenArm> status --short`
after: empty, both.

## 6. Words

- `grep -rn "without an axis\|declares the range\|nothing bound either end"
  docs/ --include=*.rst --include=*.md`, outside `docs/adrs/`: one hit,
  `docs/concepts/relations.rst:177`, the `UnreachedCoordinate` entry of the
  enumeration's refusal list ("nothing bound either end of a relation, and
  nothing reached it; ..."), still true of every relation that reaches it.
  `docs/concepts/joints.rst` already says a `Prismatic` "always states its
  ``axis``, here as anywhere". Nothing made wrong; nothing changed.
- `docs/project/changelog.rst`: one bullet under the existing `Unreleased`
  section, naming the change. `pytest -q -p no:cacheprovider
  tests/test_release_records.py`: `9 passed, 58 subtests passed in 0.13s`.

## 7. Findings record

- Moved verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## name-what-is-refused`, each with a "What shipped" paragraph,
  and deleted from `workflow/warts.md`: "The axis-less refusal names a
  `Revolute` for any kind." (its section's only entry; the section went
  too); "`JointRangeError` names the child's installed joint, not the
  mate's coordinate." — the section's last entry, its other findings having
  left it in the warts hygiene of 4 October 2026
  (`workflow/archive/warts-hygiene-2026-10-04/`), so the section went too,
  its introduction quoted beside the entry (tasks.md 7.1 revised in place
  to say so); "`a.drives(a)`, one to one, still deadlocks into
  `UnreachedCoordinate` instead of naming itself." (its section's other
  entries stay). A script compared each entry's text, saved from
  `warts.md` before the edit, with `resolved.md`: each present verbatim
  there and absent from `warts.md`; the introduction present verbatim as a
  quotation; neither removed heading left in `warts.md`.
- One new entry in `workflow/warts.md`, under a new section "Findings from
  the framework cycle `name-what-is-refused` (2026-10-06)" where the
  `slide-by-mate` section was: design.md's Open Questions 1 and 2,
  **Recorded.**
- `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this cycle.

## 8. Sync and archive

- `openspec validate name-what-is-refused` before archiving: valid.
- `openspec archive name-what-is-refused --yes`: `couplings: ~ 1
  modified`, `joints: ~ 2 modified`, `Totals: + 0, ~ 3, - 0, → 0`;
  archived as `openspec/changes/archive/2026-10-06-name-what-is-refused/`
  (its warnings: the Why section's length, and task 4.3, then unticked
  because the full suite runs after the archive).
- Each of the three synced requirements in `openspec/specs/` is identical,
  as text, to its delta block. Against `HEAD`: `joints` "Joint
  declarations" 8 scenarios → 9, "A declared range refuses a binding
  outside it" 11 → 12, `couplings` "A relation may name several
  coordinates at each end" 10 → 11; no scenario lost, each title once;
  requirement counts unchanged (18 and 17).
- `openspec validate --specs`: `Totals: 45 passed, 0 failed (45 items)`.
- The focused set of 1.2 once more, after both full-suite runs:
  `612 passed, 1 warning, 977 subtests passed in 11.93s` (wall 13.11 s).

Nothing is committed.
