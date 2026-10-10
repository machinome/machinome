Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/hold-by-mate`
with `PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow `tests/test_mates.py`'s style: `BaseNodeTest` classes, one
behaviour per test, fixtures in `tests/mate_project/`. Every test in
section 2 is run and seen RED, for the reason it names, before the code
that turns it green; record each red run in `evidence.md`.

## 0. Opening evidence

- [x] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base (`6f11aba`, plus the
  records commits `4504471` and `ed1b8f0`).
- [x] 0.2 Run the full suite at the base and record the counts in
  `evidence.md`.
- [x] 0.3 Record the answers to the four scope questions of
  `proposal.md` as ratified. If any answer differs from what the
  artifacts say, STOP and update the planning artifacts before writing a
  test.
- [x] 0.4 Record `sha256sum` of every file in `tests/base_documents/` at
  the base in `evidence.md` (the byte-identity guard of 2.8).

## 1. Planning record

- [x] 1.1 `openspec validate hold-by-mate --strict` passes; the planning
  commit holds the change folder and its `evidence/`, nothing else. No
  ADR here (task 4.5).

## 2. Red first (`tests/test_mates.py`; fixtures in `tests/mate_project/hold.py`)

Fixtures (a new module; adding it is not implementation), with
AlbertPro's left knee servo numbers (`evidence/finding.md` §3, §6), in
the shortest form that discriminates:

- `Servo(Solid2Node)`: `ears = Frame(at=(0, -5.5, 0))`,
  `ear_near = Frame(at=(-14, -5.5, 0))`, a small cube.
  `OutputServo(Servo)`: adds `output = Revolute(axis=(0, 1, 0))`.
- `Screw(Solid2Node)`: `head = Frame()`, a small cube.
  `Plate(Solid2Node)`: `bores = Frame(at=(-0.98, -4, -7), z=(1, 0, 0),
  x=(0, 0, 1))`, a small cube.
- `Shin(AssemblyNode)`: `servo_seat = Frame(at=(-0.98, -4, -7),
  z=(1, 0, 0), x=(0, 0, 1))`, `knee_bore = Frame(z=(0, 1, 0))`,
  `servo = Servo()`, `bolted = servo.ears.on(servo_seat)`.
- `PlateShin(AssemblyNode)`: `plate = Plate()` placed by `render()` with
  `translate(0, 0, 3)`, `servo = Servo()`,
  `bolted = servo.ears.on(plate.bores)` -- a fixed end on a still
  sibling.
- `OutputShin(AssemblyNode)`: `Shin`'s seat, `servo = OutputServo()`,
  `bolted = servo.ears.on(servo_seat)`.
- `BoltedServo(AssemblyNode)`: `ears = Frame(at=(0, -5.5, 0))`,
  `servo = Servo()`, `screw = Screw()`,
  `screwed = screw.head.on(servo.ear_near)`; `BoltedShin(AssemblyNode)`:
  `Shin`'s seat, `servo = BoltedServo()`,
  `bolted = servo.ears.on(servo_seat)` -- a held child carrying a mate.
- `Leg(AssemblyNode)`: `knee_pin = Frame(at=(0, 8, -30), z=(0, 1, 0))`,
  `shin = Shin()`, `knee = shin.knee_bore.on(knee_pin,
  Revolute(range=(-90, 90), unit='deg'))`; `Robot(AssemblyNode)`:
  `angle = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')`,
  `leg = Leg()`, `angle.drives(leg.knee)`.
- The hand-placed twin, AlbertPro's pre-mate form: `TwinShin(AssemblyNode)`
  declaring `knee = Revolute(axis=(0, 1, 0), range=(-90, 90), unit='deg')`
  and `servo = Servo()`, its `render()` placing the servo with
  `rotate(90.0, [0, 1, 0])`, `rotate(180.0, [1, 0, 0])`,
  `translate([-0.98, -9.5, -7.0])` (`KneeServoMount`'s form);
  `TwinPlateShin` the same over a translated `plate`; `TwinBoltedShin`
  holding a `TwinBoltedServo` whose `render()` translates the screw to
  `(-14, -5.5, 0)`; `TwinLeg` translating `shin` to `(0, 8, -30)` in
  `render()`; `TwinRobot` with `angle.drives(leg.shin.knee)`.

- [x] 2.1 **A mate may leave its freedom out.** Replace
  `RefusalTest.test_the_rigid_mate_is_deferred` and
  `test_the_rigid_mate_names_both_freedoms` with
  `test_a_mate_may_leave_its_freedom_out`: `Shin` is created, and
  `declared_mates(Shin)['bolted']` has `name` `bolted`,
  `moving.written` `'servo.ears'`, `fixed` `Shin.servo_seat` and
  `freedom` `None`; `servo.ears.on(servo_seat, None)` is the same
  statement. `test_other_freedoms_are_refused` stays, unedited but for
  one added fragment, `no freedom` (the message still says
  `a Revolute or a Prismatic`). Red at the base (refused).
- [x] 2.2 **Every mate is named.** A bare `servo.ears.on(servo_seat)` is
  refused at class creation naming `servo.ears` and `by its name`;
  `test_a_bare_mate_with_a_freedom` stays green unedited. Red at the
  base (refused for having no freedom, without the fragment).
- [x] 2.3 **The rest placement.** `Shin()` rendered: the servo's
  operations are `['r', '180', [0.7071067811865476, 0,
  0.7071067811865476]]` then a translation within `1e-9` of
  `(-0.98, -9.5, -7.0)`; its composed placement (`leaves_of`) equals
  `TwinShin`'s within `1e-9`. `PlateShin` against `TwinPlateShin`: the
  same, the plate's `translate(0, 0, 3)` carried. Red at the base.
- [x] 2.4 **Nothing on the child, nothing on the assembly.**
  `type(Shin().servo) is Servo`; `declared_joints(type(shin.servo))`
  equals `declared_joints(Servo)`; the held servo has the identity of a
  bare `Servo()`; `declared_ports(Shin)` is empty and
  `declared_ports(Leg)` holds `knee` alone; the mate's `joint` is
  `None` and `Shin.servo` (the declaration) carries no wiring. A rigid
  mate named like an attribute of the child's class
  (`ears = servo.ears.on(servo_seat)`) is accepted. Red at the base.
- [x] 2.5 **The held part rides, and keeps what it carries.** `Robot` and
  `TwinRobot` under `set_state(angle=v)` for `v` in
  `(-90, -30, 0, 30, 90)` and under the default: every leaf's composed
  placement equal within `1e-9`. `OutputShin` with the servo's `output`
  bound to 20: operations `['r', '20', [0, 1, 0]]` innermost, then the
  rest rotation and translation. `BoltedShin` against `TwinBoltedShin`:
  every leaf (the servo and the screw) equal within `1e-9`. Red at the
  base.
- [x] 2.6 **A rigid mate is not a coordinate.** On a realized `Shin`,
  `shin.bolted` is the mate `declared_mates` reports; `shin.bolted = 10`
  raises `AttributeError` naming `Shin`, `bolted` and
  `owns no coordinate`. Refused at class creation, each naming `bolted`
  and `owns no coordinate`: `bolted.drives(travel)` in a body declaring
  the port `travel`; `wheel = Wheel(spin=bolted)` with `Wheel`
  declaring the joint `spin`; a root declaring `angle = Driver(...)` and
  `shin = Shin()` stating `angle.drives(shin.bolted)`. Red at the base.
- [x] 2.7 **What stays refused.** Two mates on the held servo -- two rigid,
  and one rigid with one `Revolute` -- refused naming both and `loop`;
  a `render()` translating a held servo refused naming the shin,
  `servo` and `bolted`; `screwed = screw.head.on(servo.ear_near)` beside
  `bolted` in one class refused naming `screwed`, `servo` and `bolted`,
  and the message does NOT contain `moves it`; a subclass's rigid mate
  on an inherited child refused, its message not containing
  `joint of its own`. Red at the base (the rigid mates are refused for
  having no freedom, without the fragments).
- [x] 2.8 **Nothing else moves.** Every file in `tests/base_documents/`
  is byte-identical to its hash in 0.4 (the existing byte-identity tests,
  run unedited). `Robot`'s and `TwinRobot`'s exported documents
  (`published`) declare the same version and top-level keys, equal
  `drivers`, no node entry of the mated document with a key set the
  twin's lacks, and the servo's operation kinds `['r', 't']` against the
  twin's `['r', 'r', 't']` (decision 7), the composed placements equal
  as 2.5 says. Every existing test in `tests/test_mates.py`,
  `tests/test_frames.py`, `tests/test_joints.py` and
  `tests/test_declarative_nodes.py` stays green unedited except the two
  replaced in 2.1 and the fragment added there;
  `test_a_revolute_mate_still_installs_a_revolute` stays green.

## 3. Implementation

- [x] 3.1 `machinome/motion/mates.py`: `_check_freedom` returns early for
  no freedom, and its refusal of another kind names the three accepted
  forms, keeping `a Revolute or a Prismatic`; `declare_mates`' bare-mate
  refusal gives a mate with no freedom its own true reason (design
  decision 3); `Mate.__init__` builds no coordinate for no freedom
  (`coordinate = None`, `coordinates = {}`), `__set_name__` names none,
  `__get__` returns the mate and `__set__` raises `AttributeError`
  (decision 4); `_install` installs nothing for it (decision 2);
  `_check_child_name` is skipped for it; `_check_fixed`'s message for a
  fixed child a rigid mate places and `_check_moving`'s for an inherited
  child say what is true (decision 5).
- [x] 3.2 The coordinate refusal (decision 4): in
  `machinome/motion/couplings.py` `coordinate_ref`, beside the frame
  refusal, for a rigid mate and for a path reference ending on one; in
  `machinome/node/declarative.py`'s wiring source check. One message,
  worded once in `mates.py`.
- [x] 3.3 Docstrings: the `mates.py` module docstring (the compile list,
  "A mate compiles ... to three things"), `Mate` (the reads: `freedom`
  `None` for a rigid mate; `name` names a coordinate only with a
  freedom), `_check_freedom`, `_install`, `apply_mates`.
- [x] 3.4 Every test of section 2 green; the full suite green with the
  counts of 0.2 plus the new ones, nothing skipped that was not skipped
  at the base. Record in `evidence.md`.

## 4. Documentation, records (the second commit)

- [x] 4.1 `docs/concepts/joints.rst`, "Frames and mates", under
  `skills/write-the-manual`: a SIXTH code block, appended after the
  gripper so the first five keep their indices -- a shin holding a
  servo by `bolted = servo.ears.on(servo_seat)`, the numbers of the
  fixtures -- with one paragraph: a mate may leave its freedom out for a
  part that is held; it places the part, connector onto connector, and
  gives it nothing else, no joint and no coordinate; the part rides with
  the assembly that declares it, so a held part is declared in the class
  of the part that holds it (the fixed end still does not move); it is
  read with `freedom` `None`, is not a port, and its operations may take
  another form than a hand placement's (one rotation for two) with the
  same placement. The paragraph that says the mate "compiles ... to three
  things", the refusal paragraph (drop "a mate with no freedom at all";
  a fixed end on a child another mate places), and "A mate's ``name`` is
  its coordinate's" say what holds for a rigid mate. Pinned by a
  `ManualTest` test that execs `_code_blocks(section)[5]`, renders the
  shin and checks the servo's two operations, `declared_ports` empty and
  `freedom` `None`, and asserts the paragraph's fragments.
- [x] 4.2 `docs/reference/api.rst`, "Frames and mates": the sentence on
  the mate's spelling adds ``<child>.<frame>.on(<frame>)`` for a held
  part. The `Mate` entry renders from its docstring (3.3);
  `test_the_reference_lists_frames_and_mates` stays green.
- [x] 4.3 `docs/project/changelog.rst`, Unreleased: a bullet saying a
  mate may leave its freedom out, so a bought part is held at its seat
  by one statement in the class of the part that holds it, with no joint
  and no coordinate (ADR-152).
- [x] 4.4 Record for the studio (a separate change in
  `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the rigid mate.
- [x] 4.5 Write ADR-152 (NODE) as **Accepted** (design §9); add an
  *Amended by* line to ADR-147 and to ADR-151; ADR-152 and both updated
  entries in `docs/adrs/README.md`'s index; amend
  `docs/architecture.md`'s mate paragraph (a mate compiles to a rest
  placement and, when it states a freedom, a joint and a coordinate).
- [x] 4.6 `workflow/ongoing/mates-and-sketches.md`: the paragraphs that
  say the rigid mate "still read[s] here as proposal" say it was cut
  into `hold-by-mate` (ADR-152), the fixed end still still, and the
  dependency order among sibling mates still proposal.
- [x] 4.7 `workflow/warts.md`: the bullet "A mate must have a freedom; a
  part that is simply held has none." gains its disposition (fixed by
  `hold-by-mate`; pending the AlbertPro follow-up of §6), and Thor's
  "A screw cannot be mated to the moving sibling it fastens." gains
  "answered by AlbertPro's shape (hold-by-mate): the fastener is
  declared in the class of the part it fastens; no rule change".

## 5. Sync and archive

- [x] 5.1 Sync the `mates` delta spec into `openspec/specs/mates/spec.md`.
  It ADDS one requirement ("A mate with no freedom holds a child where
  two frames meet") and deliberately REPLACES one scenario of "An
  assembly mates a child's frame onto another frame": "A mate needs a
  revolute or prismatic freedom" becomes "A mate's freedom is a
  revolute, a prismatic or none" (its `art3.hinge.on(elbow_pin)` case is
  now accepted). If `openspec archive` refuses the dropped scenario, sync
  the MODIFIED blocks with the orchestrator's script
  (`openspec/changes/archive/2026-09-26-slide-by-mate/evidence/sync_modified.py`,
  which handles MODIFIED blocks only) and append the ADDED requirement
  after "A mate places the moving child at rest" by hand; every other
  scenario of every modified requirement is kept verbatim. Then
  `openspec validate --strict`, archive the change, final full suite,
  and commit the implementation record.

## 6. Originating project: AlbertPro (later, by a separate agent, in its own repository -- NOT in this worktree)

- [ ] 6.1 On a branch `frames-and-mates` of `projects/Robots/AlbertPro`
  from `main` (`d4384fd`), capture base poses of `Albert` over its seven
  instructions and the limit poses of every driver with the workspace's
  `docs/motion-general-refactor/capture_poses.py capture`, against the
  framework at this change's content commit.
- [ ] 6.2 The printed chain becomes revolute mates read from `RL/dog.xml`
  (`simulation/layout.py`'s `HIP_POS`, `KNEE_POS`, `MJCF_JOINT_AXIS` and
  ranges): a fixed frame on each parent at the body's `pos`, a moving
  frame on each link, `Revolute(range=..., unit='deg')`; the class-body
  `hip` and `knee` and every `render()` translate of a leg or a shin go.
  The root's bindings are re-pathed to the mates' coordinates; each
  rename is recorded.
- [ ] 6.3 Every bought part is declared in the class of the printed part
  that holds it and placed by a rigid mate at its measured seat
  (`simulation/hardware_layout.py`, unchanged numbers): the four hip
  servos in the trunk's class (or beside a still `trunk`), the eight
  horns in the thigh classes, the four knee servos in the shin classes;
  the screws and nuts inside the bolted servo, onto ear frames the servo
  declares from its own `ear_span` and `ear_inset`. Each seat is a frame
  on the holding class; each connector a frame on the bought class.
  Known traps: a frame of an ASSEMBLY resolves before its children, so a
  bolted servo's ear frame cannot read its child servo's `ear_inset`
  (restate it, or pass it down); a per-corner seat attitude reads the
  corner (`LEG`) through a frame function or a per-corner class; a mate
  on a child a base class declares is refused, so each mate is stated
  where its child is.
- [ ] 6.4 `simulation/sourced.py`, `SourcedRobot`'s tree, the eight
  relations of `albert.py` and `KneeServoMount` are deleted. The loss of
  the printed-only subtree (the project's D12, "show me only what I
  print") is recorded as a decision in the project's own OpenSpec
  change, for the pilot; it is not decided silently.
- [ ] 6.5 `capture_poses.py compare` at its default tolerance: **maximum
  deviation 0** on every pose, for every printed leaf and every bought
  leaf. The bought leaves move from `sourced.*` to paths under the
  printed parts, so the comparison maps each old path to its new one
  (the map recorded with the evidence); the tool as it is reports a
  moved leaf as missing and new. A non-zero deviation -- a hand
  placement's ordering trick that was hiding an error would show as one
  -- is reported, not fixed.
- [ ] 6.6 AlbertPro's tests pass at their `main` counts (35 in
  `test_albert.py`, 8 in `test_leg.py`, 4 in `test_trunk.py`), repointed
  at the new paths; `test_both_assemblies_share_every_joint_angle`,
  whose subject disappears, is replaced by one contract that every
  bought part rides with the printed part that holds it, and the
  replacement is recorded; F14's measurement
  (`test_the_shaft_never_reaches_the_horn_hole`, the servo shaft against
  the horn hole) is still taken, with its expected gaps unchanged; the
  project's own OpenSpec record of the migration under `openspec/`.
- [ ] 6.7 Findings from the migration are recorded in the framework's
  `workflow/warts.md` for the pilot's triage.
