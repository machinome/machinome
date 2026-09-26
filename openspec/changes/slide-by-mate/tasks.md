Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/slide-by-mate`
with `PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow `tests/test_mates.py`'s style: `BaseNodeTest` classes, one
behaviour per test, fixtures in `tests/mate_project/`. Every test in
section 2 is run and seen RED, for the reason it names, before the code
that turns it green; record each red run in `evidence.md`.

## 0. Opening evidence

- [ ] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base (`b7cc651`, plus the
  records commits `eec8689` and `60834c9`).
- [ ] 0.2 Run the full suite at the base and record the counts in
  `evidence.md`.
- [ ] 0.3 Record the answers to the four scope questions, ratified in
  `proposal.md` ("Ratified scope": the three recommendations accepted,
  the axis-less `Prismatic` struck and already folded into these
  artifacts). If any answer differs from what the artifacts say, STOP
  and update the planning artifacts before writing a test.
- [ ] 0.4 Record `sha256sum` of every file in `tests/base_documents/` at
  the base in `evidence.md` (the byte-identity guard of 2.9).

## 1. Planning record

- [ ] 1.1 `openspec validate slide-by-mate --strict` passes; the planning
  commit holds the change folder and its `evidence/`, nothing else. No
  ADR here (task 4.5).

## 2. Red first (`tests/test_mates.py`; fixtures in `tests/mate_project/slide.py`)

Fixtures (a new module; adding it is not implementation), with
open_manipulator's finger numbers (`evidence/finding.md` §2-3), in the
shortest form that discriminates:

- `Finger(Solid2Node)`: `origin = Frame()`, a small cube.
- `Palm(AssemblyNode)`: `left_seat = Frame(at=(81.7, 21.0, 0.0))`,
  `right_seat = Frame(at=(81.7, -21.0, 0.0))`, `left_finger = Finger()`,
  `right_finger = Finger()`, `left_grip = left_finger.origin.on(left_seat,
  Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))`, `right_grip`
  the same over `right_seat` with `axis=(0, -1, 0)`, and
  `left_grip.drives(right_grip)`.
- `Wrist(AssemblyNode)`: `palm = Palm()`. `Gripper(AssemblyNode)`:
  `grip = Driver(default=0.0, range=(-11.0, 20.0), unit='mm')`,
  `wrist = Wrist()`, `grip.drives(wrist.palm.left_grip)` -- the
  mimic's source driven by path from two levels up, as
  open_manipulator's root drives `...link5.left_finger.travel`.
- `SidePalm(AssemblyNode)`: `left = Flag(True)`,
  `seat = Frame(at=lambda node: (81.7, 21.0 if node.left else -21.0, 0.0))`,
  `finger = Finger()`, `grip = finger.origin.on(seat, Prismatic(axis=lambda
  node: (0, 1, 0) if node.left else (0, -1, 0), range=(-11, 20),
  unit='mm'))`.
- `SlotPart(Solid2Node)`: `slot = Frame(z=(0, 1, 0), x=(1, 0, 0))`;
  `SlotMount(AssemblyNode)`: `seat = Frame(at=(0, 0, 5), z=(0, 1, 0),
  x=(1, 0, 0))`, `part = SlotPart()`, `slide = part.slot.on(seat,
  Prismatic(axis=(1, 0, 0), range=(0, 10)))` -- an axis across the
  moving frame's `z`, no unit.
- `AnchoredPalm(AssemblyNode)`: `Palm`'s left half with
  `Prismatic(axis=(0, 1, 0), at=(0, 0, 5), range=(-11, 20), unit='mm')`.
- The hand-placed twin, open_manipulator's pre-mate form:
  `TwinLeftFinger(Solid2Node)` and `TwinRightFinger(Solid2Node)` each
  declaring `travel = Prismatic(axis=(0, ±1, 0), range=(-11, 20),
  unit='mm')`; `TwinPalm(AssemblyNode)` declaring both,
  `left_finger.travel.drives(right_finger.travel)` and a `render()`
  translating each to `(81.7, ±21.0, 0.0)`; `TwinWrist` and
  `TwinGripper` as above, `grip.drives(wrist.palm.left_finger.travel)`.

- [ ] 2.1 **The `Prismatic` refusal is gone; `Orbit` and `Free` stay.**
  In `RefusalTest.test_other_freedoms_are_refused` move the `Prismatic`
  case out into `test_a_freedom_may_be_a_prismatic` (`Palm` is created
  and `declared_mates(Palm)` lists `left_grip` then `right_grip`, each
  moving `<finger>.origin` onto its seat). Red at the base (refused).
  The `Orbit` and `Free` cases stay refused, now also asserting the
  fragments `Revolute` and `Prismatic` as the accepted kinds (red at the
  base: the message says Prismatic is "not a mate freedom").
2.2 struck at ratification (the axis-less `Prismatic`, design decision 8).
- [ ] 2.3 **The installed joint and the coordinate.** Realized `Palm`:
  `declared_joints(type(palm.left_finger))['left_grip']` is a
  `Prismatic`, its `arguments(palm.left_finger)` is
  `((0, 1, 0), (0.0, 0.0, 0.0), (-11, 20))` (the right finger's
  `(0, -1, 0)`), unit `'mm'`; `declared_ports(Palm)['left_grip']` is a
  `TranslationalPort` in `'mm'`. Red at the base (class refused).
- [ ] 2.4 **The finger rests and slides as the twin's.** Unbound, each
  finger's operations are one translation `(81.7, ±21, 0)`; `Gripper`
  and `TwinGripper` under `set_state(grip=v)` for `v` in
  `(-11, 0, 10, 20)` and under the declared default: each finger's
  operations equal the twin's in kind, order and value (translations
  within `1e-9`), `['t', ...]` along the axis then the rest translation;
  the composed world matrices of every leaf equal within `1e-9`
  (`leaves_of`). Red at the base.
- [ ] 2.5 **The mimic and the range.** `Gripper` at `grip=10`: the left
  finger's first operation is a translation `(0, 10, 0)` and the right's
  `(0, -10, 0)`; at `grip=25` and at `grip=-12`, `JointRangeError`
  naming `left_grip`. Red at the base.
- [ ] 2.6 **A function axis on a slide (ADR-150's path, the new kind).**
  `SidePalm(left=True)` and `SidePalm(left=False)`: the joint resolves
  with axis `(0, 1, 0)` and `(0, -1, 0)`; bound to 10, each finger's
  operations are a translation of 10 along its side's axis then its
  side's rest translation. Red at the base.
- [ ] 2.7 **The stated axis, the unit default and `at`.** `SlotMount`:
  the joint's axis is `(1, 0, 0)` (the stated axis, not the moving
  frame's `z`), its unit `'mm'`, the mate's port a `TranslationalPort`
  in `'mm'`; bound to 4 its operations are `(4, 0, 0)` then
  `(0, 0, 5)`. `Prismatic(range=(0, 10))` raises `TypeError` at
  construction, before any mate is stated (green at the base; stays
  green: the mate adds no refusal of its own). `AnchoredPalm`: the
  joint's anchor is `(0.0, 0.0, 5.0)`, and bound to 10 its operations
  equal `Palm`'s left finger's at 10. `Prismatic(axis=(0, 1, 0),
  at=lambda node: (0, 0, 0))` and `at=(0, 0, lift)` over a `Length` are
  refused at class creation with today's `Revolute` fragments ("three
  numbers in this version"; "resolve against the moving child"). All
  red at the base (class refused, for the refusals by fragment).
- [ ] 2.8 **The class reads.** `declared_mates(Palm)['left_grip'].freedom`
  is a `Prismatic` whose `axis` is `(0, 1, 0)`, `anchor_written` false,
  `range` `(-11, 20)`, `unit` `'mm'`; `SlotMount`'s `slide` reads `axis`
  `(1, 0, 0)` and `unit` `'mm'`. Red at the base.
- [ ] 2.9 **Nothing else moves.** Every file in `tests/base_documents/`
  is byte-identical to its hash in 0.4 (the existing `DocumentTest`,
  `StatedLineDocumentTest` byte-identity tests, run unedited).
  `Gripper`'s and `TwinGripper`'s exported documents (`published`)
  declare the same version and top-level keys, their `drivers` are
  equal, no node entry of the mated document has a key set the twin's
  lacks, and each finger's operations equal the twin's -- the symbolic
  components as the same strings (`'grip'`, `'(grip * -1)'`,
  `evidence/finding.md` §6), the numeric within `1e-9`. Every existing
  test in `tests/test_mates.py`, `tests/test_frames.py`,
  `tests/test_joints.py` and `tests/test_declarative_nodes.py` stays
  green unedited except the one narrowed in 2.1; a `Revolute` mate's
  installed joint is still a `Revolute` holding the moving frame's
  declared `z` and `at` as the same objects. `Prismatic((0, 1, 0),
  range=(-11, 20), unit='mm')` on a class, bound to 10, places exactly
  the operations it placed at the base (green at the base; stays green;
  kept from the struck 2.2 as the guard of 3.1's anchor default).

## 3. Implementation

- [ ] 3.1 `machinome/motion/joints.py`: `Prismatic` takes
  `(axis, at=_DEFAULT_ANCHOR, range=None, unit=None)` -- `axis` still
  the first, required, positional-or-keyword argument -- and
  `anchor_written`, one definition shared with `Revolute` (design
  decision 3). Nothing else in `joints.py` changes behaviour.

3.2 struck at ratification (`declarative.py`'s site refusal stays `Revolute`'s alone).
- [ ] 3.3 `machinome/motion/mates.py`: `_check_freedom` accepts a
  `Revolute` or a `Prismatic`, the refusal of anything else naming both;
  the rigid-mate refusal's hint names both; `Mate.__init__` builds the
  coordinate as the freedom's `coordinate_kind` with its unit, falling
  back to `RotationalPort` for a freedom `_check_freedom` will refuse;
  `_install` builds `type(freedom)(...)` from today's four expressions;
  the zero-length refusals in `_check_stated` and `_result_reason` say
  "states no line", not "no line to turn about".
- [ ] 3.4 Docstrings and messages: `mates.py` module docstring ("The
  freedom is a `Revolute`"; "a revolute JOINT"; "a rotational
  COORDINATE"), `Mate` (the reads: `freedom` a `Revolute` or `Prismatic`,
  `unit` `'deg'` or `'mm'`), `_check_freedom`, `_install`;
  `joints.py` `_DefaultAnchor`, `Revolute`, `Prismatic`.
- [ ] 3.5 Every test of section 2 green; the full suite green with the
  counts of 0.2 plus the new ones, nothing skipped that was not skipped
  at the base. Record in `evidence.md`.

## 4. Documentation, records (the second commit)

- [ ] 4.1 `docs/concepts/joints.rst`, "Frames and mates", under
  `skills/write-the-manual`: a FIFTH code block, appended after the
  handed example so the first four keep their indices -- a palm whose
  two fingers are mated by `Prismatic` freedoms on mirrored axes and
  related by `left_grip.drives(right_grip)` -- with one paragraph: the
  freedom may be a `Prismatic`, the part then slides along the line
  instead of turning about it, by the same rules (frames fix the rest
  and the zero; `at` and `range` as for a `Revolute`; the `axis` always
  stated; `at` moves nothing on a slide); the coordinate on the assembly is a length, in
  `'mm'` unless the freedom states a unit. The paragraph naming the
  freedom ("The **freedom** is a ``Revolute``, the one place a
  ``Revolute`` may leave out its axis") and the refusal list ("a
  freedom that is not a fresh ``Revolute``") name both kinds, the
  ``Revolute`` still the one place an axis may be left out. Pinned by
  a `ManualTest` test that execs `_code_blocks(section)[4]`, binds one
  finger's mate and checks both fingers' first operations, and asserts
  the paragraph's fragments.
- [ ] 4.2 `docs/reference/api.rst`, "Frames and mates": the sentence
  "``<child>.<frame>.on(<frame>, Revolute(...))``, and needs no import
  beyond ``Revolute``" names ``Prismatic`` too. No entry changes; the
  `Prismatic` and `Mate` entries render from their docstrings (3.4), and
  `test_the_reference_lists_frames_and_mates` stays green.
- [ ] 4.3 `docs/project/changelog.rst`, Unreleased: a bullet saying a
  mate's freedom may be a `Prismatic`, so a gripper's fingers are mated
  like its links, the mate's coordinate then a length (ADR-151).
- [ ] 4.4 Record for the studio (a separate change in
  `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the sliding freedom.
- [ ] 4.5 Write ADR-151 (NODE) as **Accepted** (design §9); add an
  *Amended by* line to ADR-147; ADR-151 and ADR-147's updated entry in
  `docs/adrs/README.md`'s index; amend `docs/architecture.md`'s mate
  paragraph ("the freedom a fresh `Revolute`", "(2) a `Revolute` of the
  child's class", "(3) a rotational COORDINATE": a `Revolute` or a
  `Prismatic`, a joint of the freedom's kind, a coordinate of its port
  kind).
- [ ] 4.6 `workflow/ongoing/mates-and-sketches.md`: the paragraph that
  lists "the rigid mate, `Prismatic` and `Free` freedoms" as left out
  says `Prismatic` was cut into `slide-by-mate` (ADR-151).
- [ ] 4.7 `workflow/warts.md`: the bullet "A mate's freedom must be a
  `Revolute`." gains its disposition (fixed by `slide-by-mate`; pending
  the open_manipulator follow-up of §6).

## 5. Sync and archive

- [ ] 5.1 Sync the `mates` delta spec into `openspec/specs/mates/spec.md`
  (there is no `joints` delta: struck at ratification). It deliberately
  REPLACES one scenario of "An assembly mates a child's frame onto
  another frame": "A mate needs a revolute freedom" becomes "A mate
  needs a revolute or prismatic freedom" (its `Prismatic()` case is now
  accepted). Sync it with the orchestrator's script (the previous
  cycle's `evidence/sync_modified.py`,
  `openspec/changes/archive/2026-09-26-state-the-freedom-per-instance/evidence/sync_modified.py`)
  if `openspec archive` refuses the dropped scenario; every other
  scenario of every modified requirement is kept verbatim. Then
  `openspec validate --strict`, archive the change, final full suite,
  and commit the implementation record.

## 6. Originating project: open_manipulator (later, by a separate agent, in its own repository -- NOT in this worktree)

- [ ] 6.1 On a branch `frames-and-mates` of
  `projects/Robotic-Arms/open_manipulator` from `main` (`eb170c1`),
  capture base poses of `OpenManipulatorX` over its five instructions and
  limit poses of every driver with the workspace's
  `docs/motion-general-refactor/capture_poses.py capture`, against the
  framework at this change's content commit.
- [ ] 6.2 Each of the six URDF joints becomes a mate stated in its
  parent link's class, in SO-ARM100's shape and read verbatim from the
  URDF (`simulation/layout.py`'s `JOINTS`): a moving `Frame()` on each
  child link class and on each finger class; a fixed frame
  `<joint>_origin = Frame(at=JOINTS[<joint>].origin_mm)` on the parent;
  the four revolutes `Revolute(axis=..., range=JOINTS[...].degrees,
  unit="deg")`, the two fingers `Prismatic(axis=..., range=JOINTS[...]
  .millimetres, unit="mm")`. The class-body joints (`base_yaw`,
  `shoulder`, `elbow`, `wrist`, both `travel`s) and every `render()`
  translate of a moving link or finger go; `Link2Assembly.render`'s
  visual offset of its `body` stays.
- [ ] 6.3 The mimic becomes a relation between the two finger mates on
  `Link5Assembly`, and the root's five `drives` are re-pathed to the
  mates' coordinates (the installed joint is bound only through the
  mate). Mate names must be free on the child and on the root's
  drivers' classes; each rename is recorded.
- [ ] 6.4 `capture_poses.py compare` at its default tolerance:
  **maximum deviation 0** on every pose. A non-zero deviation stops the
  migration and is reported.
- [ ] 6.5 open_manipulator's tests pass with the same counts as `main`
  (four in `test_open_manipulator_x.py`, one in `test_layout.py`),
  `test_gripper_fingers_move_equally_and_oppositely` unedited; its
  documented snapshots re-rendered and identical to `main`'s; its own
  OpenSpec record of the migration under `openspec/`.
