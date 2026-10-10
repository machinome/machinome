# Evidence — `snap-keeps-the-triad-unit`

Cycle 1 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`f46b61314a6c3c251fb838d199c73f79d1272ade` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`. Every SO-ARM100 command ran as
`env -C <SO-ARM100> PYTHONPATH=<bench>:<SO-ARM100> .venv/bin/<tool> ...`,
`<SO-ARM100>` = `projects/Robotic-Arms/SO-ARM100`, branch
`frames-and-mates` at `4438106`, clean tree; both probes printed the
bench's `machinome/__init__.py`. `<scratch>` is the campaign scratchpad's
`cycle1/` directory. One test run of ours at a time throughout.

## 1. Baseline on the unmodified tree (f46b613)

### 1.2 Focused tests

`pytest -q -p no:cacheprovider tests/test_frames.py tests/test_joints.py
tests/test_mates.py tests/test_frame_precision.py
tests/test_frame_precision_review.py tests/test_frame_precision_docs.py`:

```
370 passed, 1 warning, 766 subtests passed in 4.74s   (wall 5.27 s)
```

### 1.3 `tests/base_documents/`

```
a8291af0ae42595dfe1ba6f9ba55e76860220d863537ca7084d72b89c94ce4e3  clearing.json
91f85b264d0bd0127795a01d9d753548e43fb668eb63db47d1c4527573c85e7b  driverless.json
1dc9157bef5b1398619d3228f5a217550d813e410fb44e7e13debd43082ce161  drivers.json
5d0b7ee84fe38a395a28da62a8f208a9dcfa713702afd1fa0f5fc4d789be2447  flexible.json
b0e715a7fe7d973575e0d60c2742643a2a14b9e38ea7a036e64ed88893df7c33  looping.json
5e8c4c9a836a6e5c01c87140453c4e9cfc0dba18a8c603a86e1633379f0f2b8d  mate_free_arm.json
746c1e44a6402c4c33b0265bf67754af46dc97b7c164b7f47f784b90cc5f9ff2  mated_elbow_machine.json
440ca6f85cbd371371f11a0a0058c0448a0f3d99a7fc227ac847cac601c4dedf  mated_shoulder_machine.json
ce86901d3d8805732fdcf44fc94e46c2e8b69442b6a13f77b5fb4efdc171b584  running_train.json
4f38e51d27109972fc1f8f21b6d5f49062789986f9706ea3d79e2d3f01db9872  sharing.json
b37128b937f02d082ec8748d552e8bcdd97aa4e0bbfd516391e9a44397bcf897  touched_columns.json
433dc47bba5170c5a035f01be24e4f061adca52a61f92d496c8e37d61b919abe  untimed_train.json
```

(`sha256sum` of the twelve files; the digest of this listing is
`54a3cd88…162f3`.)

### 1.4 The probes

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python <scratch>/probe.py`
(exit 0) printed, byte for byte, what Stage P recorded (`diff` against its
`probe-base.txt`: no difference). The rows that matter:

```
z omitted, x off -x by rpy 1.57079 about z: Frame({'x': (-0.9999999999799858, 6.326794896668469e-06, 0)})
    .x = (-1, 6.32679489666847e-06, 0)      |len-1| = 2e-11  types=['int', 'float', 'int']
    .y = (-6.32679489666847e-06, -1, 0)     |len-1| = 2e-11  types=['float', 'int', 'int']
z omitted, x off by 3.14158: Frame({'x': (-0.9999999999199434, 1.2653589793083688e-05, 0)})
    .x = (-1, 1.2653589793083688e-05, 0)    |len-1| = 8.01e-11
    .y = (-1.2653589793083688e-05, -1, 0)   |len-1| = 8.01e-11
z omitted, x of rpy 0 0 -1.57079: Frame({'x': (6.326794896668469e-06, -0.9999999999799858, 0)})
    .x = (6.32679489666847e-06, -1, 0)      |len-1| = 2e-11
    .y = (1, 6.32679489666847e-06, 0)       |len-1| = 2e-11
elbow z, x omitted: refused: Holder.pin: frame argument x -- z=(0, -0.9999999999799858, 6.326794896668469e-06) lies along no principal axis, so x must be stated ...
residue z, x omitted / z omitted, x residue: (1, 0, 0), (0, 1, 0), (0, 0, 1), every component int
both z and x stated (elbow, gripper, z=(0,0,1) stated): floats, |len-1| = 0

== Joint axes
  axis=(0, -0.9999999999799858, 6.326794896668469e-06): resolved (0, -1, 6.32679489666847e-06) |len-1| = 2e-11
  axis=(1.2653589793083688e-05, 0, -0.9999999999199434): resolved (1.2653589793083688e-05, 0, -1) |len-1| = 8.01e-11
  axis=(0, 0, 3): resolved (0, 0, 1) types=['int', 'int', 'int']
  axis=(1e-12, 1, 0): resolved (0, 1, 0) types=['int', 'int', 'int']

== A mate stating no axis: joint axis vs moving frame z
  z and x stated: joint axis (0, -1, 6.32679489666847e-06) (|len-1| 2e-11); frame z (0.0, -0.9999999999799859, 6.32679489666847e-06); equal: False
  z omitted, x stated: joint axis (0, 0, 1) (|len-1| 0); frame z (0, 0, 1); equal: True
```

`env -C <SO-ARM100> PYTHONPATH=<bench>:<SO-ARM100> .venv/bin/python
<scratch>/so100_probe.py <scratch>/so100-before.json` (exit 0):

```
  joint shoulder.shoulder_pan_joint: axis (0, 1, 0) |len-1| = 0
  joint upper_arm.shoulder_lift: axis (1, 0, 0) |len-1| = 0
  joint lower_arm.elbow_flex: axis (1, 0, 0) |len-1| = 0
  wrist.wrist_roll_origin.y = (-0.0, 1.0000000000000002, 0.0) |len-1| = 2.22e-16
  joint wrist.wrist_flex: axis (1, 0, 0) |len-1| = 0
  joint gripper.wrist_roll: axis (0, 1, 0) |len-1| = 0
  joint jaw.gripper: axis (0, 0, 1) |len-1| = 0
poses recorded: Rest, Stand, Reach, Look, Grip
frames read: 12; joint axes read: 6
largest |length - 1| over every frame direction and joint axis: 2.22e-16
largest deviation of a fixed frame x or z from the URDF: 1.11e-16
```

`so100-before.json` is byte-identical (`cmp`) to Stage P's
`so100-base.json`.

The probes' sources, since the scratchpad is not durable. `probe.py`, beside
a `pyproject.toml` holding only `[tool.machinome]` / `model =
"probe:Nothing"`:

```python
"""Reproduce snap-keeps-the-triad-unit on the bench.

Run as:
  env -C <bench> PYTHONPATH=<bench> .venv/bin/python <this file>
"""

import math

from solid2 import cube

import machinome
from machinome.motion.joints import Revolute, declared_joints
from machinome.motion.mates import declared_mates
from machinome.node.assembly import AssemblyNode
from machinome.node.frames import Frame, resolved_frames
from machinome.node.solid2 import Solid2Node
from machinome.parameters import ParameterError

print('machinome:', machinome.__file__)

C = 6.326794896668469e-06            # sin of the 1.57079 shortfall
S = 0.9999999999799858               # cos-side, -sin(1.57079) = -S
C2 = 1.2653589793083688e-05          # from 3.14158
S2 = 0.9999999999199434


def length(v):
    return math.sqrt(sum(c * c for c in v))


def show(label, frame):
    for axis in 'xyz':
        v = getattr(frame, axis)
        print(f'  {label}.{axis} = {v!r:70} |len-1| = '
              f'{abs(length(v) - 1):.3g}  types={[type(c).__name__ for c in v]}')


def frame(**arguments):
    class Holder(AssemblyNode):
        pin = Frame(**arguments)
    return resolved_frames(Holder())['pin']


cases = {
    # Both z and x stated: the precise path since fabfc3d.
    'elbow, z and x stated': dict(z=(0, -S, C), x=(1, 0, 0)),
    'gripper, z and x stated': dict(z=(C2, 0, -S2), x=(-S2, 0, -C2)),
    # x omitted: z must lie along a principal axis after the snap.
    'elbow z, x omitted': dict(z=(0, -S, C)),
    'residue z, x omitted': dict(z=(0, 1e-12, 1)),
    # z omitted (defaulted), x stated: the snapped path.
    'z omitted, x off -x by rpy 1.57079 about z': dict(x=(-S, C, 0)),
    'z omitted, x off by 3.14158': dict(x=(-S2, C2, 0)),
    'z omitted, x residue': dict(x=(1, 1e-12, 0)),
    'z omitted, x of rpy 0 0 -1.57079': dict(x=(C, -S, 0)),
    # explicit default z with x: precise.
    'z=(0,0,1) stated, x off': dict(z=(0, 0, 1), x=(-S, C, 0)),
}
print('\n== Frames')
for label, arguments in cases.items():
    print(f'{label}: Frame({arguments})')
    try:
        show('  ', frame(**arguments))
    except ParameterError as error:
        print('  refused:', error)


print('\n== Joint axes')
for axis in ((0, -S, C), (C2, 0, -S2), (0, 0, 3), (1e-12, 1, 0)):
    class Tilted(Solid2Node):
        turn = Revolute(axis=axis, unit='deg')

        def render(self):
            return cube(2, center=True)
    node = Tilted()
    resolved = declared_joints(Tilted)['turn'].arguments(node)[0]
    print(f'  axis={axis!r}: resolved {resolved!r} |len-1| = '
          f'{abs(length(resolved) - 1):.3g} '
          f'types={[type(c).__name__ for c in resolved]}')


print('\n== A mate stating no axis: joint axis vs moving frame z')
for label, hinge in (
        ('z and x stated', dict(z=(0, -S, C), x=(1, 0, 0))),
        ('z omitted, x stated', dict(x=(-S, C, 0))),
):
    class Link(Solid2Node):
        hinge_frame = Frame(**hinge)

        def render(self):
            return cube(2, center=True)

    class Stand(AssemblyNode):
        pin = Frame(at=(0, 0, 10))
        link = Link()
        turn = link.hinge_frame.on(pin, Revolute())

    stand = Stand()
    axis = declared_joints(type(stand.link))['turn'].arguments(stand.link)[0]
    z = resolved_frames(stand.link)['hinge_frame'].z
    print(f'  {label}: joint axis {axis!r} (|len-1| '
          f'{abs(length(axis) - 1):.3g}); frame z {z!r}; equal: {axis == z}')


def whole(components, snap=1e-9):
    """The proposed rule, restated here only to predict its numbers."""
    components = tuple(components)
    nearest = []
    for c in components:
        for exact in (0, 1, -1):
            if abs(c - exact) <= snap:
                nearest.append(exact)
                break
        else:
            return tuple(0 if abs(c) <= snap else c for c in components)
    return tuple(nearest)


print('\n== Prediction under the whole-direction rule')
declared = (0, -S, C)
norm = math.sqrt(sum(c ** 2 for c in declared))
predicted = whole(c / norm for c in declared)
frame_z = frame(z=declared, x=(1, 0, 0)).z
print(f'  joint axis {predicted!r} |len-1| {abs(length(predicted) - 1):.3g}; '
      f'precise frame z {frame_z!r}; equal {predicted == frame_z}; '
      f'max diff {max(abs(a - b) for a, b in zip(predicted, frame_z)):.3g}')
for x in ((C, -S, 0), (-S, C, 0), (-S2, C2, 0)):
    size = math.sqrt(sum(c * c for c in x))
    px = whole(c / size for c in x)
    py = whole((-px[1], px[0], 0))
    print(f'  Frame(x={x!r}): x {px!r} |len-1| {abs(length(px) - 1):.3g}; '
          f'y {py!r} |len-1| {abs(length(py) - 1):.3g}')
for axis in ((0, 0, 3), (1e-12, 1, 0), (1 / 3 * 3, 0, 0), (3e-10, 0, 1),
             (2e-9, 0, 1), (0.6, 0.8, 0), (1, 1, 1)):
    n = math.sqrt(sum(c * c for c in axis))
    print(f'  {axis!r} -> {whole(c / n for c in axis)!r}')
```

`so100_probe.py`:

```python
"""The SO-100's resolved frames, mate joint axes and rest operations.

Run from the project root:
  env -C <SO-ARM100> PYTHONPATH=<bench>:<SO-ARM100> .venv/bin/python <this> [out.json]
Writes the record as JSON when given a path, so a run before and a run
after a change can be compared.
"""

import json
import math
import sys

import machinome
from machinome.motion.joints import declared_joints
from machinome.node.frames import resolved_frames

from simulation.so_arm100 import SOArm100
from simulation.tools.emit_frames import CHILD_ATTRIBUTES, read_joints

print('machinome:', machinome.__file__)


def length(v):
    return math.sqrt(sum(c * c for c in v))


from simulation.test_so_arm100 import EXPECTED_POSES  # noqa: E402

arm = SOArm100()
links = {'base': arm}
node = arm
for link, attribute in CHILD_ATTRIBUTES.items():
    node = getattr(node, attribute)
    links[link] = node

record = {'frames': {}, 'axes': {}, 'operations': {}}
worst = 0.0
for link, node in links.items():
    for name, frame in resolved_frames(node).items():
        for axis in 'xyz':
            v = getattr(frame, axis)
            off = abs(length(v) - 1)
            worst = max(worst, off)
            record['frames'][f'{link}.{name}.{axis}'] = [float(c) for c in v]
            if off:
                print(f'  {link}.{name}.{axis} = {v!r} |len-1| = {off:.3g}')
    for name, joint in declared_joints(type(node)).items():
        axis = joint.arguments(node)[0]
        off = abs(length(axis) - 1)
        worst = max(worst, off)
        record['axes'][f'{link}.{name}'] = [float(c) for c in axis]
        print(f'  joint {link}.{name}: axis {axis!r} |len-1| = {off:.3g}')

# Every documented pose: each link's operations after the arm renders it
# (a mate's rest placement and its joint's motion are composed then).
for pose, state in EXPECTED_POSES.items():
    arm.set_state(**state)
    arm.render()
    record['operations'][pose] = {
        link: [repr(op.serialized) for op in node.operations]
        for link, node in links.items()}
print(f'poses recorded: {", ".join(EXPECTED_POSES)}')

# The URDF's directions, re-read, against the resolved fixed frames at 1e-12.
deviation = 0.0
from simulation.tools.emit_frames import fixed_frame_name  # noqa: E402
for joint in read_joints():
    frame = resolved_frames(links[joint.parent])[fixed_frame_name(joint)]
    for axis, want in (('x', joint.x), ('z', joint.z)):
        for got, expected in zip(getattr(frame, axis), want):
            deviation = max(deviation, abs(got - expected))

print(f'frames read: {len(record["frames"]) // 3}; joint axes read: '
      f'{len(record["axes"])}')
print(f'largest |length - 1| over every frame direction and joint axis: '
      f'{worst:.3g}')
print(f'largest deviation of a fixed frame x or z from the URDF: '
      f'{deviation:.3g}')
if len(sys.argv) > 1:
    with open(sys.argv[1], 'w') as out:
        json.dump(record, out, indent=1, sort_keys=True)
    print('written', sys.argv[1])
```

### 1.5 SO-ARM100's documented suites, unmodified bench

Each alone, in the order of its README. The pytest command adds `-p
no:cacheprovider` to the README's `python -m pytest
simulation/test_frames.py` so nothing is written into the project.

| command | result | wall |
|---|---|---|
| `python -m pytest -p no:cacheprovider simulation/test_frames.py` | 9 passed in 2.85s | 3.78 s |
| `machinome test --mesh simulation/parts.py` | 4 passed, 0 failed (0.69 s) | 1.66 s |
| `machinome test --mesh simulation/hardware.py` | 5 passed, 0 failed (0.30 s) | 3.16 s |
| `machinome test --mesh simulation/so_arm100.py` | 12 passed, 0 failed (35.43 s) | 38.46 s |
| `machinome test --brep simulation/parts.py` | 4 passed, 0 failed (0.31 s) | 1.30 s |
| `machinome test --brep simulation/hardware.py` | 5 passed, 0 failed (0.13 s) | 3.02 s |
| `machinome test --brep simulation/so_arm100.py` | 12 passed, 0 failed (35.14 s) | 38.12 s |

`git -C <SO-ARM100> status --short`, before and after: empty.

## 2. Red tests, on the unmodified source (f46b613)

New tests:

- 2.1 `tests/test_joints.py::NumericHygieneTest::test_an_axis_within_the_snap_of_a_principal_axis_is_integers`
  (joints scenario "An axis within the snap of a principal axis resolves to
  exact integers"), a guard;
- 2.2 `tests/test_joints.py::NumericHygieneTest::test_an_axis_a_few_millionths_off_a_principal_axis_is_unit`
  ("An axis a few millionths off a principal axis resolves unit");
- 2.3 `tests/test_mates.py::InstalledJointTest::test_the_joint_turns_about_a_moving_z_a_few_millionths_off`
  ("A mate's joint turns about its moving frame's z a few millionths off an
  axis"), reading the installed joint's axis with
  `declared_joints(type(stand.link))['turn'].arguments(stand.link)[0]`;
- 2.4 `tests/test_frames.py::TriadTest::test_an_x_a_few_millionths_off_an_axis_reads_a_unit_triad`
  (mates scenario "A frame with z omitted and x a few millionths off an axis
  reads a unit triad"), both frames declared on one holder and read through
  `resolved_frames`.

One pytest process with the four:

```
8 failed, 2 passed, 10 subtests passed in 0.69s
```

- 2.1 passed (green before, as planned).
- 2.2 `tests/test_joints.py:658: AssertionError: 2.0014212509522622e-11
  not less than or equal to 1e-12` (the axis's length − 1).
- 2.3 `tests/test_mates.py:1064: AssertionError: 2.0014212509522622e-11
  not less than or equal to 1e-12` (the installed joint's axis length − 1).
- 2.4 six failing subtests: `pin` `x` and `y` length − 1
  `2.0014212509522622e-11`, `jaw` `x` and `y` `8.005662799348556e-11`
  (`test_frames.py:474`), and `x` against the declared `x`
  `2.0014212509522622e-11` / `8.005662799348556e-11` beyond `1e-15`
  (`test_frames.py:486`).

## 3. The change

- `machinome/motion/joints.py`: `_snapped_direction(components)` beside
  `_snapped` — every component within `_SNAP` of `0`, `1` or `-1` gives
  exactly that principal axis in integers; otherwise only components within
  `_SNAP` of `0` become the integer `0`. `Joint.resolve` normalizes the
  axis through it. `_snapped` stays, used by the site-joint carry. The
  `_SNAP` comment and `Joint.resolve`'s docstring state the rule.
- `machinome/node/frames.py`: `Frame.resolve` imports `_snapped_direction`
  with `resolved_vector` and applies one function per direction —
  `tuple` on the precise path, `_snapped_direction` on the snapped path —
  to `z`, to a stated `x` and to `y = _cross(z, x)`; `frames._snapped` is
  removed (nothing else read it). The `_SNAP` comment and the `Frame` and
  `ResolvedFrame` docstrings state the whole-direction rule and keep every
  phrase `tests/test_frame_precision_docs.py` pins.

After 3.1 (joints only): 2.1, 2.2, 2.3 `3 passed, 5 subtests passed in
0.47s`. After 3.2: 2.4 `1 passed, 14 subtests passed in 0.24s`.

3.4, the focused set of 1.2 with no existing test edited:

```
374 passed, 1 warning, 785 subtests passed in 5.00s   (wall 5.51 s)
```

## 4. Framework validation

### 4.1 Lint

`flake8 --max-line-length=89` (flake8 7.3.0) on the five touched Python
files, compared file by file with the same command on their `HEAD` text
(`git show HEAD:<file> | flake8 -`): no new finding. One was introduced and
fixed (an over-indented continuation of the new import in `frames.py`); the
remaining findings (`joints.py` 5, `frames.py` 1, `test_joints.py` 38,
`test_mates.py` 3, `test_frames.py` 0) are all present at `HEAD`.

`black --check` (black 26.5.1) reports all five files would be reformatted,
and so it does for each file's `HEAD` text: the repository is not
black-formatted (the CI step is `continue-on-error`). The new code follows
the surrounding style.

### 4.2 The probe after the change

`<scratch>/probe.py` again (exit 0). Every row of design.md's Context table
reads unit; the integer rows are unchanged; the mate's joint axis equals the
frame's `z`; the numbers are the ones design.md predicted:

```
z omitted, x off -x by rpy 1.57079 about z:
    .x = (-0.9999999999799859, 6.32679489666847e-06, 0)   |len-1| = 0  types=['float', 'float', 'int']
    .y = (-6.32679489666847e-06, -0.9999999999799859, 0)  |len-1| = 0  types=['float', 'float', 'int']
    .z = (0, 0, 1)                                        |len-1| = 0  types=['int', 'int', 'int']
z omitted, x off by 3.14158:
    .x = (-0.9999999999199434, 1.2653589793083688e-05, 0) |len-1| = 0
    .y = (-1.2653589793083688e-05, -0.9999999999199434, 0) |len-1| = 0
z omitted, x of rpy 0 0 -1.57079:
    .x = (6.32679489666847e-06, -0.9999999999799859, 0)   |len-1| = 0
    .y = (0.9999999999799859, 6.32679489666847e-06, 0)    |len-1| = 0
elbow z, x omitted: refused (unchanged)
residue z / x residue: integers (unchanged)
both z and x stated: floats, unchanged

== Joint axes
  axis=(0, -0.9999999999799858, 6.326794896668469e-06): resolved (0, -0.9999999999799859, 6.32679489666847e-06) |len-1| = 0 types=['int', 'float', 'float']
  axis=(1.2653589793083688e-05, 0, -0.9999999999199434): resolved (1.2653589793083688e-05, 0, -0.9999999999199434) |len-1| = 0 types=['float', 'int', 'float']
  axis=(0, 0, 3): resolved (0, 0, 1) types=['int', 'int', 'int']
  axis=(1e-12, 1, 0): resolved (0, 1, 0) types=['int', 'int', 'int']

== A mate stating no axis: joint axis vs moving frame z
  z and x stated: joint axis (0, -0.9999999999799859, 6.32679489666847e-06) (|len-1| 0); frame z (0.0, -0.9999999999799859, 6.32679489666847e-06); equal: True
  z omitted, x stated: joint axis (0, 0, 1) (|len-1| 0); frame z (0, 0, 1); equal: True
```

### 4.3 Full suite

Run at this point, alone (`pytest -q -p no:cacheprovider` at the bench
root), it stalled at 82% inside `tests/test_scad_presentation.py`, in a
`machinome build tests/scad_where_read_project/native.py:StlBench`
subprocess that spawned a fresh build generation about once a second; it was
stopped after 1,676 s (exit 143). The cause is the open wart "a `machinome
build` in a project whose sources were written moments earlier restarts
every second without end" (`workflow/warts.md`), and not this change:

- `timeout 60 machinome build tests/scad_where_read_project/native.py:StlBench`
  (bench as cwd, a scratch `SOLID_BUILD_DIR`) exits 124 after 18 `START`
  lines.
- One generation run in-process under a line tracer of `Builder._start`
  returns `SOURCE_CHANGED` at `builder.py:361`, the `self.node.mtime_ns !=
  loaded_source_mtime_ns` check after assembly, with no `SourceChanged`
  raised: the node's source mtime moves from `1791295831479951928` (the
  loaded closure, `native.py`) to `1791295831480951959`, the mtime of
  `tab.stl`, an `StlNode` input that joins the source union during
  assembly. The fixture's files were written by the worktree checkout at
  14:10:31 on 6 October, `tab.stl` one millisecond after `native.py`, so
  every generation sees the same "change". No framework file is in the
  union, and this change touched no fixture file.
- Of the fixture's roots, `native.py:StlBench` and `machine.py:Machine` move
  that way; `ExactBench`, `LegacyBench` and `Mixed` are steady.

The complete run, after section 8, alone, deselecting the seven tests that
run `machinome build` on `StlBench` or `Machine`
(`WithoutTheEngineTest::test_native_projects_build_without_each_module`,
`WrittenOnlyWhereReadTest::test_a_build_writes_only_the_scad_authored_leafs_scad`,
`SweepTest::test_presentation_scad_and_a_renamed_leafs_scad_are_swept`, and
`SnapshotOnDemandTest`'s four tests), all in
`tests/test_scad_presentation.py`:

```
4604 passed, 4 skipped, 7 deselected, 55 warnings, 6573 subtests passed in 565.94s (0:09:25)   (wall 568.3 s)
```

### 4.4 `tests/base_documents/`

Re-hashed after the full suite: the twelve digests are those of 1.3 (the
listing's digest `54a3cd88…162f3` again); `git status` shows no change
under `tests/base_documents/`.

## 5. Validation in SO-ARM100 (read only)

### 5.1 The probe after the change

`<scratch>/so100_probe.py <scratch>/so100-after.json` printed exactly 1.4's
lines (12 frames, 6 joint axes, largest |length − 1| `2.22e-16`, largest
deviation of a fixed frame's `x` or `z` from the URDF `1.11e-16`). The
comparison:

```
python -c "import json; a = json.load(open('<scratch>/so100-before.json')); b = json.load(open('<scratch>/so100-after.json')); print(a == b)"
True
```

and `cmp` finds the two files byte-identical: every frame direction, every
joint axis and every link's operations in `Rest`, `Stand`, `Reach`, `Look`
and `Grip` unchanged. The SO-100 reaches neither changed path (its
off-axis fixed frames state both directions, its moving frames are
`Frame()`, its joint axes are exact), so this is the "poses do not move"
half of the proof; the red-to-green tests above are the other.

### 5.2 Its documented suites after the change

| command | before | after |
|---|---|---|
| `python -m pytest -p no:cacheprovider simulation/test_frames.py` | 9 passed, 3.78 s | 9 passed in 3.04s, 4.14 s |
| `machinome test --mesh simulation/parts.py` | 4/4, 1.66 s | 4 passed (0.35 s), 1.34 s |
| `machinome test --mesh simulation/hardware.py` | 5/5, 3.16 s | 5 passed (0.15 s), 3.19 s |
| `machinome test --mesh simulation/so_arm100.py` | 12/12, 38.46 s | 12 passed (35.90 s), 38.91 s |
| `machinome test --brep simulation/parts.py` | 4/4, 1.30 s | 4 passed (0.34 s), 1.29 s |
| `machinome test --brep simulation/hardware.py` | 5/5, 3.02 s | 5 passed (0.13 s), 3.01 s |
| `machinome test --brep simulation/so_arm100.py` | 12/12, 38.12 s | 12 passed (35.62 s), 38.48 s |

`git -C <SO-ARM100> status --short`: empty.

## 6. Words

- `skills/write-the-manual/SKILL.md` (workspace) read before the manual
  edit.
- `docs/concepts/joints.rst`: the omitted-`x` sentence and the closing
  sentence on mate and joint snaps changed in place; nothing added.
- `docs/architecture.md`: the frame paragraph's snap sentences and the joint
  paragraph's axis-snap sentence state the whole-direction rule.
- `docs/project/changelog.rst`: an `Unreleased` section above `Machinome
  0.8.0` with one bullet naming the change.
  `pytest tests/test_release_records.py tests/test_frame_precision_docs.py`:
  `11 passed, 61 subtests passed in 0.18s`.
- `python -m sphinx -b html -n -q docs <scratch>/_build/html`: exit 0, five
  warnings, all in `docs/reference/api.rst` and `machinome/simulation/sim.py`
  docstrings, none on a page this change touched; the rebuilt
  `concepts/joints.html` carries the new sentences.
- `grep -rn "1e-9" docs/ machinome/node/frames.py machinome/motion/joints.py`:
  every hit on a frame direction or a joint axis states the whole-direction
  rule; the others are `_SNAP`, `_PARALLEL_TOLERANCE`, ADRs and unrelated
  tolerances.

## 7. Findings record

- The entry "A snapped triad component leaves the triad non-unit." with its
  **Remaining (2026-10-04)** note moved verbatim (`diff` of the two
  passages: identical) to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## snap-keeps-the-triad-unit` with a "What shipped" paragraph, and
  deleted from `workflow/warts.md`.
- In its place in the same section, one new entry: "Two direction snaps
  still work one component at a time" (a site-declared joint's carried
  axes; a mate's rest-rotation axis), **Recorded.**
- `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this cycle.

## 8. Sync and archive

- `openspec validate snap-keeps-the-triad-unit` before archiving: valid.
- `openspec archive snap-keeps-the-triad-unit --yes`: `joints: ~ 1
  modified`, `mates: ~ 2 modified`; archived as
  `openspec/changes/archive/2026-10-06-snap-keeps-the-triad-unit/` (its only
  warnings: the Why section's length, and the task boxes, then unticked).
- Each of the three synced requirements in `openspec/specs/` is identical,
  as text, to its delta block; against `HEAD`, the two baseline specs lose
  no scenario and gain four (one in `mates`, three in `joints`), each title
  once.
- `openspec validate --specs`: `Totals: 45 passed, 0 failed (45 items)`.
- The focused set of 1.2 once more, after the full suite:
  `374 passed, 1 warning, 785 subtests passed in 4.73s`; with
  `tests/test_release_records.py` added, `383 passed, 1 warning, 843
  subtests passed in 4.78s` (wall 5.26 s).

Nothing is committed.
