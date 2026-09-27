# The finding: a bought part cannot be held by mate

Recorded 2026-09-27 at the planning of `hold-by-mate`, base `6f11aba`
(the implementation commit of `slide-by-mate`, ADR-151) plus the records
commits `4504471` and `ed1b8f0` on `workflow/warts.md`. Everything below
is quoted or re-derived read-only from committed records and source; the
probe of §6 ran the framework at that HEAD from a scratch directory
outside the worktree (with a throwaway `pyproject.toml` declaring
`[tool.machinome]`), changed nothing and is not a test. No project was
touched.

## 1. The wart (`workflow/warts.md`, last-but-one section, "A bought part cannot be held by mate: no rigid mate (2026-09-26, AlbertPro)")

> - **A mate must have a freedom; a part that is simply held has none.**
>   The `mates` spec refuses a mate with no freedom ("the rigid mate is
>   not provided", place-parts-by-mate, because Thor's root chain needed
>   only revolutes). A servo's ears onto the trunk's bores, a horn's seat
>   onto the thigh's hole, a knee servo's ears onto the shin's pattern are
>   connector onto connector with nothing free between them: the
>   statement `servo.ears.on(trunk.bay_fl)` with no freedom, placing the
>   child from the two frames and giving it no joint and no coordinate.
>   With it, each bought part is declared in the class of the printed
>   part that holds it and rides with it, the parallel tree, its eight
>   relations and the ordering wrapper go, and Thor's recorded question
>   ("whether a fixed end on a moving sibling should follow it, or
>   whether a part's fasteners belong in its own class") gets its answer
>   from this project: the fasteners belong in the class of the part they
>   fasten, held by a rigid mate, and a fixed end on a moving sibling is
>   not needed. **Cycle cut: `hold-by-mate`.**

And the Thor question it answers (`workflow/warts.md`, "Findings from the
Thor project's fastener holders (2026-09-26)", second bullet):

> - **A screw cannot be mated to the moving sibling it fastens.** A
>   fastener follows a part only as that part's child, so a turning leaf
>   (a pinion) has to be wrapped in an assembly to carry its grub screw,
>   and a jaw's pins are carried by hand in `simulate()`. The rigid mate
>   the mates design defers would not change that while a mate's fixed end
>   must be still (a sibling does not carry a sibling, `mates` spec).
>   Whether a fixed end on a moving sibling should follow it, or whether a
>   part's fasteners belong in its own class, is a design question for the
>   next project that fastens a moving part. **Recorded.**

The refusal's origin: `openspec/changes/archive/2026-09-26-place-parts-by-mate/proposal.md`,
scope question 2, "The rigid mate now": Thor's 142 in-assembly
attachments were each transcribed once by `emit_layout.py` and checked
by `test_layout.py`, so a rigid mate "would replace a working,
single-statement mechanism rather than fix a finding"; *Recommendation:
defer*, ratified. Its `design.md` §9 lists what a rigid mate would add:
(a) `on()` with no freedom, compiled as the rest placement and no joint,
no coordinate; (b) the fixed-end-on-a-moving-child refusal relaxed for a
child placed by a rigid mate, bringing a dependency order and a cycle
refusal among sibling mates; (c) a document decision (it should not
differ from a hand placement). ADR-147: "`Prismatic`, `Orbit`, `Free`
and no freedom at all (the rigid mate) are refused naming this version's
scope"; Consequences: "Deferred, each needing its own evidence: the
rigid mate (which brings the dependency order and a loop refusal among
sibling mates back)". ADR-151 kept it refused. This finding is that
evidence for (a), and -- §5 -- not for (b).

## 2. The originating project today

`/mnt/data/machinome-projects/Robots/AlbertPro` (`projects/Robots/AlbertPro`),
`main` at `d4384fd`, MIT upstream, read-only.

**The printed chain** (`simulation/leg.py`, `printed.py`, `trunk.py`)
nests as `RL/dog.xml` does (`dog.xml:141-151`: `FL_upper_leg` at
`pos="0.055 0.055 0"` with hinge `FL_hip`, `FL_lower_leg` at
`pos="0 0.008 -0.03"` with hinge `FL_knee`, both about `0 1 0`):
`PrintedRobot` (`printed.py`) holds `trunk = Trunk()` (an
`AssemblyNode` of two shells, `trunk.py:12-30`) and four `Leg`s placed
by `leg.translate(layout.HIP_POS[name])` in `render()`; `UpperLeg`
(`leg.py:39-48`) declares `hip = Revolute(axis=(0, 1, 0), unit='deg')`
and places `self.lower.translate(layout.KNEE_POS[self.LEG])`;
`LowerLeg` (`leg.py:27-36`) declares `knee = Revolute(axis=(0, 1, 0))`.
Per corner, `UpperLegFL` etc. declare `near`, `far` (the two thigh
plates) and `lower`; `LowerLegFL` etc. `near` and `far` (the shin
plates). These migrate as revolute mates read from `dog.xml`, as
SO-ARM100's did from its URDF; nothing here needs this cycle.

**The bought parts** (`simulation/sourced.py`) are a second tree that
"mirrors `leg.py`'s nesting exactly" (`sourced.py:5-16`):

- `SourcedRobot` (`:241-273`) holds four `HipServo`s and four
  `SourcedLeg`s; its `render()` places each servo by its ears on the
  trunk's bay, `servo.rotate(180.0, [0, 0, 1])` on the right side and
  `servo.translate([x, bore_y + outboard_sign(name) * inset, z])`
  ("Placed by its ears, not by the rail face: the bores are the
  interface with no freedom in it"), and each leg by
  `leg.translate(layout.HIP_POS[name])` -- the printed tree's placement,
  restated.
- `SourcedUpper` (`:120-145`) restates `hip = Revolute(axis=(0, 1, 0))`
  and places the two horns in the thigh's horn holes,
  `horn.rotate(0.0 if face > 0 else 180.0, [0, 0, 1])` then
  `horn.translate([x, 2.0 if face > 0 else -2.6, z])`, and
  `self.lower.translate(layout.KNEE_POS[self.LEG])` -- restated again.
- `SourcedLower` (`:108-117`) restates `knee = Revolute(axis=(0, 1, 0))`.
- `KneeServoMount` (`:78-105`) exists only for ordering: "A node's
  `simulate()` operations compose INSIDE its `render()` ones, so
  orienting and turning the same node would apply the joint angle first
  and the quarter turn afterwards -- which builds, runs, and puts the
  servo about 19 degrees out. A child's operations apply before its
  parent's, so a wrapper gets the order right." Its `render()` does
  `self.servo.rotate(90.0, [0, 1, 0])`, on the left side also
  `self.servo.rotate(180.0, [1, 0, 0])`, then
  `self.servo.translate([x, plate - outboard * inset, z])` with
  `x, _, z = hl.knee_bore_midpoint()`, `plate = -4.0 if outboard > 0
  else 2.0`.
- `BoltedServo` (`:44-64`) is a servo with its two M2 screws and nuts,
  placed in its own `render()` at `(±span/2, SCREW_STANDOFF, 0)` and
  `(±span/2, SCREW_STANDOFF - length, 0)`.
- Eight per-corner `KneeServoMount`/`SourcedLower`/`SourcedUpper`/
  `SourcedLeg` subclasses (`:157-238`) carry `LEG` and the children.

`simulation/albert.py:241-255` ties the two trees together:
`printed = PrintedRobot()`, `sourced = SourcedRobot()` and eight
relations `printed.fl.upper.hip.drives(sourced.fl.upper.hip)` ...
`printed.rr.upper.lower.knee.drives(sourced.rr.upper.lower.knee)`,
"Eight sentences tie the bought parts to the printed ones, joint for
joint, so the hardware moves with the parts that hold it".

**The seats** are project measurements, `simulation/hardware_layout.py`
("Every number here was read off `hardware/albert_pro.stl` with
`simulation/tools/probe.py features`, never off a datasheet"): the hip
bores `HIP_SERVO_BORE_X`, `HIP_SERVO_BORE_Z = 2.910`, `HIP_RAIL_Y`
(`:53-67`); the knee bores `KNEE_SERVO_BORE_X = -0.980`,
`KNEE_SERVO_BORE_Z = (7.000, -21.000)` (`:76-79`); the horn holes
`THIGH_HORN_HOLE = {'hip': (1.990, 0.660), 'knee': (2.000, -32.660)}`
and `THIGH_HORN_FACE` (`:84-93`). Its docstring: "A BOLTED interface is
unambiguous. A bore has a diameter, an axis and a position, and the part
that bolts there has no freedom. All eight servo mounts are of this
kind."

**The parts** (`simulation/hardware.py`): `MicroServo`, origin "at the
output shaft axis, on the output face", ears `ear_inset` 5.5 behind it
(`ear_positions()`); `ServoHorn`, origin "on the shaft axis at the face
the horn seats against"; `M2Screw` "Origin under the head"; `M2Nut`
"Origin on the face the nut is drawn up against". Each is a
`CadQueryNode` leaf.

Count: 16 bought parts are placed by hand in a PRINTED part's frame --
4 hip servos (bolted servo assemblies), 8 horns, 4 knee servos -- and
32 screws and nuts inside `BoltedServo` in the servo's frame; 48 in all
(66 published parts less the 18 printed bodies).

**Why the parallel tree exists** (`openspec/changes/archive/2026-09-07-model-the-sourced-parts/design.md`):

> **D12. Two parallel assemblies, one binding.** `Albert.printed` and
> `Albert.sourced` mirror each other joint for joint, and the root binds
> both from the same clamped joint angle. Two trees can silently
> disagree; one binding site makes that impossible, and a contract
> checks it anyway. The alternative -- one tree with the hardware hung
> off the printed parts -- would have made "show me only what I print"
> impossible, which is a thing a builder wants.

> **D15. Orientation and placement live one level below the joint.**
> ... `KneeServoMount` exists to hold the orientation and placement one
> level below the knee rotation, which is the same reason `leg.UpperLeg`
> exists.

**What the project measures** (`simulation/test_albert.py:640-813`,
`SourcedTest`): every hip and knee servo's ear bores on the printed
bores; every screw crossing its plate; `test_the_shaft_never_reaches_the_horn_hole`
(design F14: the hip servo's shaft and the thigh's horn hole never come
closer than 2.518 mm front, 2.665 mm rear, across the posture range);
and `test_both_assemblies_share_every_joint_angle`, which exists only
because there are two trees. The suites count 35 tests in
`test_albert.py`, 8 in `test_leg.py`, 4 in `test_trunk.py`.

## 3. What a rigid mate would state, row by row

| today (hand) | a mate with no freedom |
|---|---|
| `KneeServoMount.render`: `rotate(90, y)`, left `rotate(180, x)`, `translate(-0.98, plate - outboard*inset, -7)` | a seat frame on the shin at the bore midpoint on the plate face, `Frame(at=(-0.98, -4, -7), z=(1, 0, 0), x=(0, 0, 1))` on the left; a frame at the ears on the servo, `Frame(at=(0, -5.5, 0))`; `servo.ears.on(servo_seat)` |
| `SourcedUpper.render`: `rotate(0 or 180, z)`, `translate(x, 2.0 or -2.6, z)` | a seat frame on the thigh at each horn hole, its triad turned on the far face; `Frame()` on the horn; `hip_horn.seat.on(hip_horn_hole)` |
| `SourcedRobot.render`: right side `rotate(180, z)`, `translate(x, bore_y ± inset, z)` | a bay frame on the trunk at each bore midpoint; the bolted servo's ear frame; `hip_servo_fl.ears.on(bay_fl)` |
| `BoltedServo.render`: screws and nuts at `(±span/2, ...)` | a frame per ear on the servo (it reads its own `ear_span`, `ear_inset`); `near_screw.head.on(servo.ear_near)` -- a fixed end on a still sibling, allowed today |

Each placement is then stated once, as the printed chain's will be:
connector onto connector, the measured seat a frame on the printed part
that holds the bought one. Every rest attitude is a whole number of
quarter turns about principal axes, and the left knee servo's is a half
turn about `(1, 0, 1)/√2` (§6) -- a non-principal attitude that exercises
the axis-angle decomposition's half-turn branch.

## 4. What the framework does today

- `machinome/motion/mates.py:482-490`, `_check_freedom`: `if freedom is
  None: raise TypeError(... "The rigid mate -- a child placed by two
  frames with no freedom at all -- is not provided in this version
  (deferred, OpenSpec change place-parts-by-mate) ...")`.
- `mates.py:416-420`, `declare_mates`: an unassigned mate is refused
  because "A mate with a freedom owns a coordinate, and the coordinate is
  named after the mate". `declared_mates` (`:365-370`) is keyed by
  `mate.name`.
- `mates.py:293-303`, `Mate.__init__`: every mate builds a coordinate
  (`_coordinate_kind(freedom)(unit=...)`, `RotationalPort` for a
  freedom it cannot read) and `coordinates = {None: coordinate}`;
  `__set_name__` names it; `__get__`/`__set__` read and bind it.
  `declared_ports` (`ports.py:497-560`) reports a value whose
  `coordinates` is a non-empty mapping of ports, or whose `coordinate`
  is a port -- an empty mapping and a `None` coordinate report nothing.
- `mates.py:818-875`, `_install`: specializes the moving child's
  declaration with the joint and adds `wiring[mate.name] = mate`. It is
  the only place the child's class changes; `ChildDeclaration.realize`
  (`declarative.py:~490-530`) calls `call_freedom_functions` and
  `_record_wiring` only when the declaration has a wiring.
- `mates.py:1122-1165`, `apply_mates`: the rest placement is composed
  from the two resolved frames (and a fixed child's rest operations)
  alone; it never reads the freedom or the joint.
- `mates.py:727-769`, `_check_fixed`: a fixed end is refused on a child
  another mate places (`placed`, every mate of the class) or whose class
  declares a joint, worded "can move within ... -- the mate '<name>'
  moves it".
- `mates.py:693-724`, `_check_moving`: a subclass's mate on a child a
  base declares is refused because "A mate gives the child it moves a
  joint of its own, on the declaration <base> shares".
- `mates.py:772-794`, `_check_child_name`: the mate's name must be free
  on the moving child's class, "the mate gives '<child>' a joint named
  '<mate>'".
- Relations: `couplings.py:2312`, `coordinate_ref`, already refuses a
  frame named as a relation end; `OwnRef.check_declared_on`
  (`couplings.py:380-397`) admits every declared mate; the wiring check
  (`declarative.py:~360-400`) admits every mate of the class as a wiring
  source.

## 5. What AlbertPro does NOT need

- **A fixed end on a moving sibling** (Thor's question). Each bought
  part is declared in the class of the printed part that holds it: the
  horns in the thigh class (`UpperLeg*`, an assembly), the knee servo in
  the shin class (`LowerLeg*`), the hip servos in the trunk class
  (`Trunk`, an assembly) or in the root beside a still `trunk`. Every
  fixed end is then the holding class's own frame or a frame of a still
  sibling (a thigh or shin plate, a shell). The part rides because it
  is the moving part's descendant, not because it follows a sibling.
- **A fixed end on a rigidly held sibling** (place-parts-by-mate §9 (b)).
  The screws and nuts are held by the servo inside `BoltedServo`, whose
  `servo` child is placed by nothing; no bought part is held by another
  bought part that is itself held by a mate in the same assembly.
- **A rigid mate on an inherited child.** The project declares each
  corner's children in its per-corner subclass (`UpperLegFL` holds
  `near`, `far`, `lower`; `SourcedUpperFL` holds `hip_horn`,
  `knee_horn`), so a mate is stated where its child is declared.
- **A bare (unassigned) mate.** Naming each of 16 + 32 statements costs
  a word each; nothing in the project reads a mate by anything but its
  name.
- **A new document field or version.** `hardware_layout.py`'s seats
  reach the document today as ordinary operations.

## 6. The probe (framework at `ed1b8f0`, scratch directory, not a test)

A `Block` leaf declaring `ears = Frame(at=(0, -5.5, 0))`, mated onto
`seat = Frame(at=(-0.98, -4.0, -7.0), z=(1, 0, 0), x=(0, 0, 1))` -- the
left knee servo's seat of §3 -- first with no freedom, then with
`Revolute()` (a mate's rest placement never reads its freedom, so this
is the rest placement a rigid mate would make), against a twin placing
the block as `KneeServoMount` does:

    1. today, on() with no freedom:
       TypeError: Rigid.held states no freedom. The rigid mate -- a child
       placed by two frames with no freedom at all -- is not provided in
       this version (deferred, OpenSpec change place-parts-by-mate); ...
    2. the same frames under a Revolute mate: the rest placement
       [['r', '180', [0.7071067811865476, 0, 0.7071067811865476]],
        ['t', ['-0.98', '-9.5', '-7.0']]]
       twin [['r', '90.0', [0, 1, 0]], ['r', '180.0', [1, 0, 0]],
             ['t', ['-0.98', '-9.5', '-7.0']]]
       max |mate - twin| = 2.83e-16   (composed world matrices)
    3. a fixed end on a sibling another mate places:
       TypeError: Chain.second: its fixed end a.ears is on 'a', which can
       move within Chain -- the mate 'first' moves it. ...
    4. declared_ports of the revolute version: ['held'];
       type(block) is Block: False (a specialization named Block)

The seat `(-0.98, -4.0, -7.0)` is the bore midpoint on the plate face
`y = -4` (`plate = -4.0` for a left leg); with the ears 5.5 behind the
shaft it reproduces the project's translation `(-0.98, -9.5, -7.0)`. So the rest placement a rigid mate needs exists and
reproduces the project's hand placement within `3e-16` -- the half turn
about `(1, 0, 1)/√2` as one rotation where the project writes two, and
the angle `'180'` where the project writes `'180.0'`: the operations'
form differs, the matrices do not. What a rigid mate must NOT carry is
item 4: a coordinate on the assembly and a specialization of the child.

## 7. What the rigid mate buys, and what it does not

Stated plainly, so the pilot weighs the evidence and not the wart's
summary of it:

- **The parallel tree could go without this cycle.** Declaring each
  bought part in the printed class that holds it and placing it by
  `rotate`/`translate` in that class's `render()` would already delete
  `sourced.py`'s mirror, the eight relations and `KneeServoMount` (a
  child's rest operations compose outside a joint its PARENT carries, so
  D15's trap does not arise one level down). What the rigid mate adds is
  that the placement is stated once, as two connectors -- the measured
  seat as a frame on the printed part, the bought part's own interface
  as a frame on it -- instead of rotate/translate arithmetic derived by
  hand from them (`bore_y + outboard * inset`, `plate - outboard *
  inset`, `0.0 if face > 0 else 180.0`), which is ADR-147's own reason
  for a mate. After the printed chain migrates onto revolute mates, the
  bought parts would otherwise be the only hand placements left in the
  machine, 16 of them in printed frames and 32 in the servo's.
- **D12's other reason is not answered by any framework change.** "One
  tree with the hardware hung off the printed parts would have made 'show
  me only what I print' impossible." A rigid mate hangs the hardware off
  the printed parts; the migration therefore gives up the `printed`
  subtree as a view of the printed parts alone. That is the project's
  decision to take in its own record (tasks §6), not this cycle's.
- **Thor's question is answered by the project's shape**, not by a rule:
  the fastener is declared in the class of the part it fastens, and a
  fixed end stays still (§5).
