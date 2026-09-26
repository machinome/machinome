# The finding: a project that guards its frames must restate the framework to read them

Recorded 2026-09-26 at the planning of `read-frames-and-mates`, base
`0b0eae5` (the implementation record of `state-the-mate-line`, stacked
on it). Sections 1 to 3 are quoted from committed records; section 4 was
measured at planning time by running the base framework read-only
against Thor's modules, with the build directory in a scratch location
and bytecode writing off, so nothing was written in Thor.

## 1. The wart (`workflow/warts.md`, "Findings from the framework cycle `place-parts-by-mate` (2026-09-26)", sixth bullet)

> - **No documented way to read a declared frame's numbers, or a mate's
>   ends and freedom, off the class.** Thor's `test_frames.py`, which guards
>   the emitted frames against the design documents, had to restate the
>   default-`x` rule and read `Mate.described()` and `Mate.freedom.range`
>   — undocumented surfaces — because `declared_frames` yields the
>   declarations with their raw arguments and the resolved triad lives in
>   the instance's private `_frame_arguments`. The design chose no
>   instance-level read for this cycle. **Deferred:** a project has now
>   needed one; the smallest change is a documented resolved-frame read on
>   the instance and documented `moving`/`fixed`/`freedom` on `Mate`.

The design choice it names is `place-parts-by-mate` design decision 1,
kept in ADR-147's rejected alternatives: "**As a descriptor returning
resolved numbers**: nothing reads a frame on an instance in this
version." A project now does.

## 2. What Thor's guard reaches for

`/home/asa/devel/machinome/projects/Robotic-Arms/Thor/simulation/test_frames.py`,
as it stands on Thor's branch `state-the-mate-line` (head `87a5ddb`),
read with `git show state-the-mate-line:simulation/test_frames.py`
(read-only). The guard re-reads the design's FreeCAD connectors through
the emitter and compares them with what the modules declare.

**(a) The resolved triad, re-derived from the declaration.** Lines 27,
30–33 and 58–74:

```python
from machinome.node.frames import declared_frames

from simulation.tools.emit_frames import (DOCUMENTS, MODULES, ROOT_CHAIN,
                                          Numbers, default_x,
                                          mate_placement, read_frames,
                                          same_placement)
...
def unit(vector):
    length = math.sqrt(sum(v * v for v in vector))
    return tuple(v / length for v in vector)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def declared(class_name, frame_name):
    """A declared frame's numbers, `x` defaulted by the documented rule."""
    frame = declared_frames(node_class(class_name))[frame_name]
    z = unit(tuple(float(v) for v in frame.z))
    x = unit(tuple(float(v) for v in frame.x)) if frame.x else default_x(z)
    return Numbers(tuple(float(v) for v in frame.at), x, cross(z, x), z)
```

`declared_frames` yields the DECLARATION, its arguments raw, so the
guard normalizes `z`, re-implements the default-`x` rule (through the
emitter's `default_x`), builds `y`, and — because it reads the class —
can only work while every argument is a literal: `float(v)` of a
parameter token or a callable fails. It never squares a stated `x` up
against `z`, which the framework does. The resolved `ResolvedFrame` it
reconstructs exists on every realized declarer, under the private
`_frame_arguments`.

The emitter's copy of the rule,
`git show state-the-mate-line:simulation/tools/emit_frames.py`,
lines 115–128:

```python
def default_x(z):
    """The `x` a frame takes when it states none: the next principal axis
    after a principal `z`, carrying its sign (`+X` for `+Z`, `+Y` for
    `+X`, `+Z` for `+Y`), or None for a `z` along no principal axis, which
    must state its `x`. The framework's documented rule, restated here
    only to decide which emitted frames need to write theirs: it chooses
    nothing about the frames themselves."""
```

It has a second caller, `frame_literal` (line 252: `if frame.x !=
default_x(frame.z):`), which decides what an emitted `Frame(...)` must
WRITE. That use is not a read of a declared frame (section 5).

**(b) The mate's ends, through its diagnostic string.** Lines 124–135:

```python
    def test_every_link_is_one_mate_between_its_two_frames(self):
        for entry in ROOT_CHAIN:
            mates = declared_mates(node_class(entry.holder))
            self.assertIn(entry.mate, mates, entry.holder)
            mate = mates[entry.mate]
            fixed = ('%s.%s' % (entry.fixed_on, entry.fixed)
                     if entry.fixed_on else entry.fixed)
            self.assertEqual(mate.described(), '%s.%s.on(%s, ...)'
                             % (entry.child, entry.moving, fixed))
            self.assertEqual(tuple(mate.freedom.range),
                             getattr(module_of(entry.holder), entry.travel),
                             '%s.%s' % (entry.holder, entry.mate))
```

`declared_mates` is documented; `described()` (the string refusals and
`repr` use) and `freedom` are not.

**(c) The freedom's line, through undocumented attributes and a
sentinel.** Lines 77–79 and 137–150:

```python
def freedom_of(entry):
    """The freedom of the mate that places `entry`'s link."""
    return declared_mates(node_class(entry.holder))[entry.mate].freedom
...
            if read['axis'] is None:
                self.assertIsNone(freedom.axis, where)
            else:
                self.assertIsNotNone(freedom.axis, where + ' states no axis')
                self.assertEqual(floats(freedom.axis), read['axis'], where)
            self.assertEqual(freedom.anchor_written, read['at'] is not None,
                             where)
            if read['at'] is not None:
                self.assertEqual(floats(freedom.at), read['at'], where)
```

After `state-the-mate-line` the guard reads the freedom's `axis`, `at`,
`anchor_written` and `range`. None is documented. `at` read alone is
misleading: left out, it reads `(0, 0, 0)` — `joints._DEFAULT_ANCHOR`, a
tuple subclass told apart only by identity — while the mate's anchor is
then the moving FRAME's origin, not the child's; only `anchor_written`
says which (section 4 shows four of Thor's five freedoms in that state).

**(d) The mate's line default, restated over (a) and (c).** Lines
167–178:

```python
    def test_each_mate_turns_its_link_about_the_line_its_joint_did(self):
        # The line the installed joint turns about: the freedom's where it
        # states one, else the moving frame's z through its origin.
        for entry in ROOT_CHAIN:
            freedom = freedom_of(entry)
            moving = declared(entry.child_class, entry.moving)
            axis = (unit(floats(freedom.axis)) if freedom.axis is not None
                    else moving.z)
            at = floats(freedom.at) if freedom.anchor_written else moving.at
```

This one is a choice between two values both of which the documented
reads of this change return, by the mate's own documented rule ("each
it leaves out, the frame supplies"); see design decision 6.

## 3. What the framework already computes

- `machinome/node/frames.py`: `Frame.resolve(node)` builds a
  `ResolvedFrame(at, x, y, z)` — `at` three floats, `z` normalized, `x`
  squared up against `z` or defaulted by `_principal_next`, `y = z × x`,
  directions snapped to exact `0`, `1`, `-1` within `1e-9` —
  and `resolve_declared_frames(node)` caches every declared frame's under
  `node.__dict__['_frame_arguments']` (`RESOLVED_KEY`) in declaration
  order, in the constructor right after the joints. A class declaring no
  frame gets no entry at all.
- `machinome/motion/mates.py`: `_placement` reads exactly that cache for
  both ends of every mate; `Mate.__init__` keeps `moving`, `fixed` and
  `freedom` as written; `FrameRef.written` is `'<child>.<frame>'`; the
  fixed end of a mate onto the assembly's own frame IS that `Frame`,
  whose `name` is its attribute; `Mate.name` is the assignment.
- `machinome/motion/joints.py`: `Revolute.axis`, `.at`, `.range`, `.unit`
  as written (`unit` defaulting to `'deg'`), and
  `Revolute.anchor_written`.

Nothing a documented read needs is missing; only the documentation and
one public function reading the cache are.

## 4. Measured at planning: the instance read is what Thor re-derives

`evidence/thor_read_probe.py`, run from a scratch directory with
`SOLID_BUILD_DIR` in the scratchpad and `PYTHONDONTWRITEBYTECODE=1`
against this worktree's framework and Thor's checkout on
`state-the-mate-line` (clean); a `find -newer` over Thor afterwards
listed nothing. For each of the ten frames of Thor's five root-chain
mates, it constructs the declaring class on its own and compares the
cached `ResolvedFrame` with the guard's `declared(...)`:

| Frame                | construct | max deviation | resolved `x`, `y`, `z`                  |
|----------------------|-----------|---------------|-----------------------------------------|
| `Base.yaw_pin`       | 0.250 s   | 0             | `(0,1,0)`, `(-1,0,0)`, `(0,0,1)`        |
| `Art1.yaw_bore`      | 0.569 s   | 0             | `(0,1,0)`, `(-1,0,0)`, `(0,0,1)`        |
| `Art1.shoulder_pin`  | 0.458 s   | 0             | `(1,0,0)`, `(0,1,0)`, `(0,0,1)`         |
| `Art2.shoulder_bore` | 0.369 s   | 0             | `(-1,0,0)`, `(0,0,1)`, `(0,1,0)`        |
| `Art2.elbow_pin`     | 0.353 s   | 0             | `(1,0,0)`, `(0,1,0)`, `(0,0,1)`         |
| `Art3.elbow_bore`    | 0.279 s   | 0             | `(1,0,0)`, `(0,0,-1)`, `(0,1,0)`        |
| `Art3.yaw_pin`       | 0.262 s   | 0             | `(1,0,0)`, `(0,1,0)`, `(0,0,1)`         |
| `Art4.yaw_bore`      | 0.163 s   | 0             | `(-1,0,0)`, `(0,1,0)`, `(0,0,-1)`       |
| `Art4.wrist_pin`     | 0.172 s   | 0             | `(1,0,0)`, `(0,1,0)`, `(0,0,1)`         |
| `Art56.wrist_bore`   | 0.053 s   | 0             | `(0,-1,0)`, `(1,0,0)`, `(0,0,1)`        |

The direction components come back as Python `int`s (the snap), `at`
as `float`s. The five mates, read off `declared_mates(holder)`:

| Mate              | `moving.written`    | `fixed`                       | `axis`            | `at` / `anchor_written`   | `range`            |
|-------------------|---------------------|-------------------------------|-------------------|---------------------------|--------------------|
| `Thor.yaw`        | `shoulder.yaw_bore` | ref, `written` `base.yaw_pin` | `None`            | `(0, 0, 0)` / `False`     | `(-180.0, 180.0)`  |
| `Art1.shoulder`   | `art2.shoulder_bore`| `Frame`, `name` `shoulder_pin`| `(0.0, 0.0, 1.0)` | `(0.0, 0.0, 0.0)` / `True`| `(-90.0, 90.0)`    |
| `Art2.elbow`      | `art3.elbow_bore`   | `Frame`, `name` `elbow_pin`   | `None`            | `(0, 0, 0)` / `False`     | `(-135.0, 135.0)`  |
| `Art3.yaw`        | `art4.yaw_bore`     | `Frame`, `name` `yaw_pin`     | `(0.0, 0.0, 1.0)` | `(0, 0, 0)` / `False`     | `(-180.0, 180.0)`  |
| `Art4.wrist`      | `art56.wrist_bore`  | `Frame`, `name` `wrist_pin`   | `(1.0, 0.0, 0.0)` | `(0, 0, 0)` / `False`     | `(-105.0, 105.0)`  |

Every unit is `'deg'`. Four freedoms read `at == (0, 0, 0)` with
`anchor_written` false: read alone, `at` would claim the child's origin
for the base yaw, the elbow (whose anchor is `(0, 0, 81.5)`) and the
forearm and wrist yaws. `Art1.shoulder` is the one whose `(0, 0, 0)` is
written and means the child's origin.

A second probe, `evidence/upper_arm_probe.py`, on the manual's `UpperArm` (`reach = Length(160)`,
`elbow_pin = Frame(at=(0, reach, 68), ...)`), realized with `reach=150`:
the class-level declaration reads `at=(0, <Length reach = 160>, 68)`, the
instance's cache `(0.0, 150.0, 68.0)`; the rendered forearm's rest
operations are `['r', '90', [1, 0, 0]]` then `['t', ['0.0', '231.5',
'68.0']]`, which `F_fixed · F_moving⁻¹` of the two cached frames gives.
A class-body child read off the class (`UpperArm.forearm`) is a
`ChildDeclaration`, not a node; a leaf declaring no frame has no
`_frame_arguments` entry.

## 5. What Thor does with the result

Thor's guard, rewritten later in Thor's own repository (tasks §7):

- `declared(...)` becomes the documented read of a constructed declarer,
  `resolved_frames(<class>())[<frame>]`: no normalizing, no `default_x`,
  no `cross`, and no dependence on every argument being a literal. The
  emitter's `mate_placement` already reads `.at`, `.x`, `.y`, `.z`, so a
  `ResolvedFrame` feeds it unchanged.
- `mate.described()` gives way to the documented ends,
  `mate.moving.written` and `mate.fixed.written` or `mate.fixed.name`.
- `freedom.axis`, `.at`, `.anchor_written`, `.range` are the same reads,
  now documented, `at` together with `anchor_written`.
- The emitter's `default_x` STAYS: `frame_literal` needs it to decide
  which emitted frames may leave `x` out — a question about what to
  write, which no read of a declared frame answers. The guard stops
  importing it.
- Nothing in any module changes, so no pose can move; Thor's suite and
  `capture_poses.py compare` confirm it.
