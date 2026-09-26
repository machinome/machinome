# The finding: a gripper's fingers cannot be mated

Recorded 2026-09-26 at the planning of `slide-by-mate`, base `b7cc651`
(the implementation commit of `state-the-freedom-per-instance`, ADR-150)
plus the records commits `eec8689` and `60834c9` on `workflow/warts.md`
and ADR-150. Everything below is quoted or re-derived read-only from
committed records and source; the two probes of §6 ran the framework at
that HEAD from a scratch directory outside the worktree, changed nothing
and are not tests. No project was touched.

## 1. The wart (`workflow/warts.md`, last section, "A gripper's fingers cannot be mated: no prismatic freedom (2026-09-26, open_manipulator)")

> - **A mate's freedom must be a `Revolute`.** The `mates` spec refuses a
>   `Prismatic` freedom by name (place-parts-by-mate: "a freedom that is
>   not a `Revolute` -- a `Prismatic`, an `Orbit` or a `Free` -- ... is
>   refused", ADR-147, because Thor exercised only revolutes). The four
>   links migrate as SO-ARM100's did, but the two fingers cannot: they are
>   placed and freed by a slide, and would stay on the old form -- a
>   `translate` in `render()` and a class-body `Prismatic` -- beside four
>   mates, leaving the migration split down the middle. The URDF's
>   prismatic joint is the same statement as its revolute one (parent,
>   child, origin, axis, limits), and a mate should be able to give the
>   moving child a `Prismatic` with the same rules: the line stated in the
>   child's frame or taken from the moving frame's `z`, the range in
>   millimetres, the rest placement from the frames as today.
>   **Cycle cut: `slide-by-mate`.**

The refusal's origin, `openspec/changes/archive/2026-09-26-place-parts-by-mate/`
and ADR-147 ("`Prismatic`, `Orbit`, `Free` and no freedom at all (the
rigid mate) are refused naming this version's scope"; Consequences:
"Deferred, each needing its own evidence: ... `Prismatic` and `Free`
freedoms"): Thor exercised only revolutes. This finding is that
evidence for `Prismatic`, and for nothing else.

## 2. The originating project today

`/mnt/data/machinome-projects/Robotic-Arms/open_manipulator`
(`projects/Robotic-Arms/open_manipulator`), `main` at `eb170c1`,
read-only.

The URDF (`open_manipulator_description/urdf/open_manipulator_x/open_manipulator_x.urdf`)
states the fingers exactly as it states the four revolutes, every
`rpy` zero:

```xml
<joint name="gripper_left_joint" type="prismatic">          <!-- :155 -->
  <parent link="link5"/>
  <child link="gripper_left_link"/>
  <origin rpy="0 0 0" xyz="0.0817 0.021 0.0"/>
  <axis xyz="0 1 0"/>
  <limit effort="1000" lower="-0.011" upper="0.02" velocity="4.8"/>
</joint>
<joint name="gripper_right_joint" type="prismatic">         <!-- :185 -->
  <parent link="link5"/>
  <child link="gripper_right_link"/>
  <origin rpy="0 0 0" xyz="0.0817 -0.021 0"/>
  <axis xyz="0 -1 0"/>
  <limit effort="1000" lower="-0.011" upper="0.02" velocity="4.8"/>
  <mimic joint="gripper_left_joint" multiplier="1"/>
</joint>
```

beside, for example, `joint4` (`:125`): parent `link4`, child `link5`,
origin `0.124 0.0 0.0`, axis `0 1 0`, limits `-1.7..1.97`.

`simulation/layout.py:56-57` transcribes them in millimetres:

```python
"gripper_left_joint": Joint((81.7, 21.0, 0.0), (0.0, 1.0, 0.0), -0.011, 0.02),
"gripper_right_joint": Joint((81.7, -21.0, 0.0), (0.0, -1.0, 0.0), -0.011, 0.02, "gripper_left_joint", 1.0),
```

with `Joint.millimetres` giving `(-11.0, 20.0)`.

`simulation/open_manipulator_x.py` states each finger twice, as the four
links are stated today (ADR-097's class form):

- the freedom on the child's class, `:31-44`:
  `class LeftFinger(VisualPack): travel = Prismatic(axis=JOINTS["gripper_left_joint"].axis, range=JOINTS["gripper_left_joint"].millimetres, unit="mm")`,
  and `RightFinger` the same over `gripper_right_joint`;
- the placement in the parent's `render()`, `:55-57`:
  `self.left_finger.translate(JOINTS["gripper_left_joint"].origin_mm)`,
  `self.right_finger.translate(JOINTS["gripper_right_joint"].origin_mm)`;
- the URDF's `mimic`, `:53`: `left_finger.travel.drives(right_finger.travel)`
  in `Link5Assembly` (identity law; the mirrored axes make equal travel
  opposite motion, the URDF's `multiplier="1"`);
- the root driver, `:105` and `:111`:
  `grip = Driver(default=0.0, range=(-11.0, 20.0), unit="mm")`,
  `grip.drives(arm.link2.link3.link4.link5.left_finger.travel)`.

The four revolutes follow the same split: `wrist = Revolute(...)` on
`Link5Assembly` (`:51`) with `self.link5.translate(JOINTS["joint4"].origin_mm)`
in `Link4Assembly.render` (`:65-66`), and so on down the chain.

The behaviour the migration must keep, `simulation/test_open_manipulator_x.py:41-51`,
`test_gripper_fingers_move_equally_and_oppositely`: at `grip=10.0` the
left finger's centroid moves `+10.0` in `y` and the right one's `-10.0`,
within `0.01`. The project's tests are four in
`test_open_manipulator_x.py` and one in `test_layout.py`; its own
OpenSpec records are under `openspec/` (spec `open-manipulator-x-poses`).

## 3. What a mate would state, row by row

In SO-ARM100's shape (§5), each URDF joint becomes a fixed frame on the
parent link at the joint's origin, a moving `Frame()` at the child's own
origin, and a freedom. For the fingers:

| URDF | mate |
|---|---|
| `<origin xyz>` | the fixed frame, `Frame(at=(81.7, ±21.0, 0.0))` on `Link5Assembly` |
| child link's own frame | `Frame()` on the finger class |
| `<axis xyz>` | the freedom's `axis`, `(0, ±1, 0)`, in the finger's own frame |
| `<limit>` | the freedom's `range`, `(-11.0, 20.0)` mm |
| `type="prismatic"` | the freedom's kind: `Prismatic(axis=..., range=..., unit="mm")` |
| `<mimic multiplier="1">` | a relation between the two mates' coordinates on `Link5Assembly` |

No anchor: the URDF's axis runs through the child's origin, which the
moving `Frame()`'s origin is. Every `rpy` is zero, so every rest
placement is one translation.

## 4. What the framework does today

- `machinome/motion/mates.py:452-457`, `_check_freedom`:
  `if not isinstance(freedom, Revolute): raise TypeError(... "accepts a Revolute only in this version: Prismatic, Orbit and Free are not mate freedoms yet" ...)`.
- `mates.py:278`, `Mate.__init__`: the mate's coordinate is always
  `RotationalPort(unit=unit)`, `unit` defaulting to `'deg'`.
- `mates.py:795-798`, `_install`: the installed joint is always
  `Revolute(axis=..., at=freedom.at if freedom.anchor_written else frame.at, range=..., unit=...)`.
- `machinome/motion/joints.py:302`, `Joint.__init__(self, axis, at=(0, 0, 0), ...)`:
  `axis` is positional and required. `Revolute` alone overrides it
  (`:843`, `axis=None, at=_DEFAULT_ANCHOR`) and alone has
  `anchor_written` (`:848-854`). So today `Prismatic(range=(-11, 20), unit='mm')`
  raises `TypeError: Joint.__init__() missing 1 required positional argument: 'axis'`
  at construction (§6), before any mate sees it, and a `Prismatic`'s
  default `at` is a plain `(0, 0, 0)`, not the sentinel a mate tells
  "left out" by.
- `joints.py:870-898`, `Prismatic`: "Bound, it places one translation of
  `value` along the carried unit axis. `at` does not affect the placement
  -- a translation along a line is the same wherever the line is taken to
  pass -- and is carried as the declared position of the slide, for a
  reader and for a later exporter." Its coordinate is a
  `TranslationalPort`, default unit `'mm'`.
- `machinome/node/declarative.py:305`: the site-joint refusal of an
  axis-less joint tests `isinstance(value, Revolute)` only;
  `joints.py:1380`, `axisless_refusal`, words it "is a Revolute without
  an axis".

## 5. Where `at` goes for a `Prismatic`

The placement ignores it (§4). It is still read: the control compiler's
`_placed_geometry` (`machinome/simulation/program.py:3886-3903`) reads
`joint.arguments(node)[1]` for every joint a control poses and
publishes it as the control's `origin` (ADR-112 decision 3: "`axis` and
`origin` are the values the joint's own placement used"), so a `Slide`
control on a prismatic joint publishes the slide's anchor as its
gesture origin. A class-body `Prismatic` accepts `at` in every form the
joint argument rule takes.

## 6. Two probes (scratch directory, framework at `60834c9`, nothing changed)

- **The mimic between two mates' coordinates.** Two fingers mated onto
  one palm by `Revolute` freedoms with mirrored axes `(0, 1, 0)` and
  `(0, -1, 0)`, range `(-11, 20)`, the palm stating
  `left_turn.drives(right_turn)`, the palm two levels under a root whose
  driver drives `wrist.palm.left_turn` by path. Bound at 10: the left
  finger's operations `[['r', '10', [0, 1, 0]], ['t', ['81.7', '21.0', '0.0']]]`,
  the right one's `[['r', '10', [0, -1, 0]], ['t', ['81.7', '-21.0', '0.0']]]`;
  bound at 25: `JointRangeError ... joint 'left_turn' declares the range -11 to 20`.
  A relation between two mate coordinates of one assembly, driven from
  above by path, works today; OpenArm's validated
  `finger1_turn.drives(finger2_turn, ratio=1.0)` (branch
  `frames-and-mates`, `simulation/gripper.py`) is the same shape.
- **The hand-placed twin's document.** open_manipulator's pre-mate
  gripper (class-body `Prismatic` per finger, `render()` translates,
  identity mimic, root `grip` driver in mm), exported with and without an
  `Instruction`: version `2`, keys `animation, drivers, format,
  instructions, root, version`, no program; the left finger's operations
  `[['t', ['0', 'grip', '0']], ['t', ['81.7', '21.0', '0.0']]]`, the right
  one's `[['t', ['0', '(grip * -1)', '0']], ['t', ['81.7', '-21.0', '0.0']]]`.
  An `Instruction` alone publishes no program, so the coordinate table
  that carries a coordinate's `domain` (`program.py:3228-3246`) is not
  in open_manipulator's document.

## 7. The contrast: SO-ARM100's revolute mates

`/mnt/data/machinome-projects/Robotic-Arms/SO-ARM100`, branch
`frames-and-mates` (`ce8b3b1`), `simulation/so_arm100.py`: each URDF link
one class with `link_frame = Frame()`, each URDF joint one mate in the
parent link's class, `<joint>_origin = Frame(at=..., z=..., x=...)` and
`<child>.link_frame.on(<joint>_origin, Revolute(axis=<URDF axis>, range=<TRAVEL>, unit="deg"))`.
open_manipulator's four revolutes take that shape as they are; its two
prismatics would take it with `Prismatic` for `Revolute`.
