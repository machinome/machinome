# The finding: a handed design cannot state its mates per instance

Recorded 2026-09-26 at the planning of `state-the-freedom-per-instance`,
base `61f2335` (framework `main`, `vet-the-project` integrated) plus the
records commit `9e228fa` on `workflow/warts.md`. Everything below is
quoted or re-derived read-only from committed records and source; no
framework code was run at a new commit, and no project was touched.

## 1. The wart (`workflow/warts.md`, last section, "A handed design cannot state its mates per instance (2026-09-26, openarm)")

> - **A mate's freedom cannot state its line or its range as a function of
>   the node.** A frame already may: `Frame` takes three numbers, tokens or
>   formulas, or one callable of the realized declarer, so a handed fixed
>   frame (`at=lambda node: ...`) needs nothing new. The freedom may not:
>   `_check_stated` (ADR-148) refuses a callable `axis` or `at`, and
>   ADR-147 restricts `range` to numbers, both because the installed joint
>   resolves against the moving child while the freedom is written in the
>   assembly. ADR-148 rejected "the whole joint argument rule" with
>   "No project needs one; one that does gets a resolver-side resolution
>   then, together with the range." OpenArm is that project: without it,
>   its migration onto mates would have to split every joint class in two
>   by side and give up the per-instance handedness its design already
>   settled on. **Cycle cut: `state-the-freedom-per-instance`.**

The section's preamble states the project's settled reading: "handedness
is a fact of the realized node, not of the class", as the ADR-097
migration decided.

## 2. The originating project today

`/mnt/data/machinome-projects/Robotic-Arms/openarm` (`projects/Robotic-Arms/openarm`),
`main` at `48a2ac9`, read-only.

Two mirrored seven-joint arms, each ending in a pinch gripper. One class
per joint, instantiated once per side, a `left = Flag(False)` handed down
every declaration (`simulation/arm.py:41`, `:102`; `gripper.py:34`,
`:56`). Every joint is one factory reading the side off the realized node
(`simulation/arm.py:26-37`):

```python
def _revolute(row):
    return Revolute(
        axis=lambda node: ARM_JOINTS[_side(node.left)][row].axis,
        range=lambda node: ARM_JOINTS[_side(node.left)][row].limits,
        unit="deg",
    )
```

and the fingers the same shape (`simulation/gripper.py:19-30`,
`_finger_revolute`, over `FINGER_JOINTS`). No `at` is written: "every one
of these joints turns about its own placed origin", which the ADR-097
migration (`openspec/changes/archive/2026-09-10-joint-frame-follows-declarer/proposal.md`)
established by deleting the old parent-frame `at=`.

The placement is written a second time, by hand, per side, in each
parent's `render()`:

- `_Joint.render` (`simulation/arm.py:44-48`) translates the downstream
  joint by `ARM_JOINTS[_side(self.left)][self.joint_index].origin`;
- `Arm.render` (`simulation/arm.py:107-108`) translates `joint1` by
  `ARM_JOINTS[_side(self.left)][0].origin`;
- `PinchGripper.render` (`simulation/gripper.py:66-69`) translates each
  finger by `seated_finger_origin(self.left, index)`.

The mounts (`ArmsAtRest.render`, `arm.py:117-119`; `OpenArm.render`,
`openarm.py:65-67`) and the gripper base (`gripper.py:67`) are rigid
translations; nothing here asks to mate them.

The gripper's mimic reads the side off the realized finger too:
`grip.drives(finger1.turn, law=handed)` (`gripper.py:63`), where
`handed(gripper, finger)` returns `Affine(ratio=1.0 if finger.left else
-1.0)` (`gripper.py:47-51`).

## 3. What differs by side, and where each lands on a mate

From `simulation/layout.py:51-88` (transcribed from the pinned URDF
`.vendor/openarm_description/assets/robot/openarm_v2.0/urdf/example/v2.urdf`
and held to it by `simulation/test_arm.py::test_arm_layout_has_not_drifted_from_generated_urdf`):

| joint | origin, left / right | axis, left / right | limits (deg), left / right |
|---|---|---|---|
| arm 1 | `(0, 62.5, 0)` / `(0, -62.5, 0)` | `(0, 1, 0)` / `(0, -1, 0)` | `(-200.0, 80.0)` / `(-80.0, 200.0)` |
| arm 2 | `(0, 60, 0)` / `(0, -60, 0)` | `(-1, 0, 0)` both | `(-190.0, 10.0)` / `(-10.0, 190.0)` |
| arm 3-5 | same | same | same |
| arm 6 | same | `(0, -1, 0)` / `(0, 1, 0)` | same |
| arm 7 | same | same | same |
| finger 1 | `(-1.43, -18, -68)` / `(-1.43, 18, -68)` | `(-1, 0, 0)` both | `(0, 45)` / `(-45, 0)` |
| finger 2 | `(-1.43, 18, -68)` / `(-1.43, -18, -68)` | `(1, 0, 0)` both | `(0, 45)` / `(-45, 0)` |

(limits rounded here; the table holds the URDF's radians converted.)

On a mate, in the shape SO-ARM100 already uses (§6), each row becomes a
fixed frame on the parent at the joint's origin, a moving `Frame()` at
the child's own origin, and a freedom:

- **the origin** is the fixed frame's `at`, a frame of the PARENT, which
  holds `left`: `Frame(at=lambda node: ARM_JOINTS[side(node.left)][row].origin)`.
  **Served today** (spec `mates`, "A frame resolves against its declarer
  at realization", scenario "A frame may be computed from the realized
  node").
- **the axis** is the freedom's `axis`, per side for arm joints 1 and 6.
  **Refused today.**
- **the limits** are the freedom's `range`, per side for arm joints 1
  and 2 and both fingers. **Refused today.**
- **the anchor**: none. Every joint turns about the child's own origin,
  which is the moving `Frame()`'s origin, the default a freedom that
  leaves `at` out already takes. A function `at` is **not needed**.

## 4. What the framework does today

- `machinome/motion/mates.py:472`, `_check_stated`, refuses a stated
  line that "is a callable of the node, which would be called with the
  moving child"; `_check_freedom` (`mates.py:402`, the `callable(declared)`
  branch at `:439`) refuses a range that "is a callable of the node,
  which would be resolved against the moving child".
- Both refusals exist because `_install` (`mates.py:678`) passes the
  freedom's values into a class-form `Revolute` installed on the child's
  specialized class, which `resolve_declared_joints`
  (`machinome/motion/joints.py:1444`) resolves in the child's own
  constructor, calling any callable with the CHILD (`resolved_vector`,
  `joints.py:1382`; `Joint._span`).
- ADR-148, rejected alternative "The whole joint argument rule": "each
  would resolve against the node the line is not written in. No project
  needs one; one that does gets a resolver-side resolution then, together
  with the range."

## 5. What the migration would cost today

A mate is stated in the PARENT's class body, and a subclass may not
restate a mate on a child an ancestor declares (spec `mates`, the
inherited-mate refusals), so numbers that differ by side need a parent
class per side, and a left parent must declare a left child: the whole
chain splits. Counted from `simulation/arm.py` and `gripper.py`: `Arm`
and `Joint1`…`Joint7` (eight classes, each stating one handed mate or
declaring a class that does) become sixteen, and `PinchGripper` (stating
both finger mates) becomes two; `FingerJoint1`/`FingerJoint2` need not
split, because the moving child's class is not where the freedom is
written. The wart's "fourteen arm classes and four finger classes in
place of seven and two" counts the joint classes rather than the
stating ones; the order of magnitude and the conclusion are the same:
the per-instance handedness the ADR-097 migration settled on is given
up.

## 6. What the project could do today instead, and why not

- **The axis on both frames' `z`.** Declaring the fixed frame
  `Frame(at=..., z=lambda node: <axis>)` and the moving frame
  `Frame(z=lambda node: <axis>)` with the same derived `x` leaves the
  rest rotation the identity and makes the frames' `z` the joint line,
  per side, with no framework change. This is exactly the workaround
  ADR-148 retired for Thor: a connector made to double as a joint frame
  (ADR-148, "A design's connectors can be declared verbatim: the frames
  place the part, the freedom states the line"; rejected alternative
  "The line on the frame"). It also leaves the range unserved.
- **The limits as an ancestor's constraint.** `path.constrain(range=...)`
  from each root, numbers per arm. Not examined against a mate-installed
  joint; rejected regardless, because it moves each URDF joint's limit
  out of the joint into every root that holds an arm (`OpenArm`,
  `ArmsAtRest`, `GrippersAtThirtyDegrees`), and a constraint only
  intersects, so the freedom itself would carry no range.

## 7. The contrast: SO-ARM100, nothing handed

`/mnt/data/machinome-projects/Robotic-Arms/SO-ARM100`, branch
`frames-and-mates` (`ce8b3b1`), `simulation/so_arm100.py`, read-only:
each URDF link is one class, each URDF joint one mate stated in the
parent link's class, the joint origin a frame of the parent
(`<joint>_origin`), the child's `link_frame = Frame()`, and the freedom
`Revolute(axis=<URDF axis>, range=<TRAVEL>, unit="deg")` in numbers. That
is the shape OpenArm migrates into, with one difference: OpenArm's
numbers are a function of the side.

## 8. Source facts the node decision rests on

- A node's constructor (`machinome/node/base.py`, around `:660-790`)
  resolves its parameters, runs `check()`, resolves its class-declared
  joints (`resolve_declared_joints`), then its frames
  (`resolve_declared_frames`), and realizes its children LAST
  (`realize_children`), then resolves its relations.
- `realize_children` (`machinome/node/declarative.py:1371`) hands each
  `ChildDeclaration.realize(values, owner)` (`declarative.py:490`) the
  realized PARENT; `realize` constructs the child, records its wiring
  (the mate's included) and resolves every SITE-declared joint's
  arguments against that parent (`_resolve_site_joints`,
  `declarative.py:514`), a joint `resolve_declared_joints` skips on
  purpose (`joints.py:1468`). ADR-098, "Callables: one argument, the
  realized declaring parent": a function written at a declaration site
  is called with the parent, not the child.
- A frame's function is called with its declarer (spec `mates`, "A frame
  resolves against its declarer at realization"); a class-declared
  joint's with its declarer (ADR-097); a site joint's with the declaring
  parent (ADR-098). In every case: the realized node whose class body
  wrote the function.
- The rest placement is composed at the owner's RENDER, not its
  realization: `apply_mates` (`mates.py:849`) is called from
  `machinome.node.assembly._rest` after the author's `render()` returns,
  and again on every re-run of a legacy render. The joint's arguments,
  by contrast, are read from the instance's `_joint_arguments` by
  binding (`Joint.__set__` through `_refuse_out_of_range`), by the
  constraint and relation range checks (`constraints.py:166`,
  `couplings.py:2741`) and by the running and clocked compilers
  (`simulation/program.py:3896`, `:3997`).
- No documented read gives a joint's resolved axis or range on an
  instance: `docs/reference/api.rst` documents `Revolute` by its class
  docstring and `declared_joints` (class-level declarations).
  `Joint.arguments(node)` exists and the framework's own tests read it
  (`tests/test_mates.py`, e.g. `InstalledJointTest`, `StatedLineTest`,
  `MateReadTest`), but it is not in the reference. OpenArm's tests read
  no resolved joint argument: they hold `layout.py` to the URDF and read
  joint names and coordinate values (`simulation/test_arm.py:66`,
  `test_gripper.py:43-44`, `test_openarm.py:40`, `:116`).
