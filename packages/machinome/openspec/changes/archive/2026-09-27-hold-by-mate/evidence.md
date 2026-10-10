# Evidence: hold-by-mate

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/hold-by-mate` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once. Probes ran from the session scratchpad and are not tests.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/hold-by-mate/machinome/__init__.py

Branch `hold-by-mate`: base `6f11aba` (the implementation commit of
`slide-by-mate`, ADR-151), the records commits `4504471` ("Record that a
bought part cannot be held by mate for want of the rigid mate") and
`ed1b8f0` ("Record OpenMANIPULATOR-X's validation of ADR-151 and its
findings"), and the ratified planning commit `45e5fe1` at `HEAD`. The
worktree was clean when this work began, and `git diff --quiet --
machinome` held.

## 0.2 Full suite at the base (planning commit 45e5fe1)

    python -m pytest -q -p no:cacheprovider -rsf

    11 failed, 3981 passed, 4 skipped, 53 warnings, 2783 subtests passed in 397.08s (0:06:37)

The 4 skips are the base's usual four: browser snapshot e2e not
enabled, jscad CLI absent, the two Internal-Cycloidal-Actuator
vendor-STEP cases.

**The 11 failures are pre-existing and not this change's**: the
`machinome vet` tests over fixture projects whose `sim/parts/` modules
`main` never committed (`.gitignore`'s `parts/`), recorded in the same
words by `slide-by-mate`'s evidence (0.2):

    tests/test_vet_assertions.py::KernelIoTest::test_the_pure_apis_raise_nothing
    tests/test_vet_assertions.py::SourcesTest::test_a_literal_under_the_root_passes_without_the_file
    tests/test_vet_closure.py::ThePureProjectTest::test_the_pure_project_is_pure
    tests/test_vet_closure.py::ThePureProjectTest::test_the_vetted_files_are_the_model_closure
    tests/test_vet_closure.py::ResolutionScenarioTest::test_a_package_init_on_the_path_is_vetted
    tests/test_vet_closure.py::ResolutionScenarioTest::test_a_star_import_vets_every_module_in_the_package
    tests/test_vet_command.py::TextReportTest::test_the_pure_project_exits_zero_with_the_preamble
    tests/test_vet_command.py::JsonReportTest::test_one_object_with_the_specified_keys
    tests/test_vet_isolation.py::CostTest::test_vetting_a_cadquery_model_loads_no_kernel_and_no_node
    tests/test_vet_isolation.py::EnvironmentTest::test_a_dotenv_file_does_not_matter
    tests/test_vet_isolation.py::EnvironmentTest::test_the_build_directory_does_not_matter

Nothing in this change touches `machinome vet`, its fixtures or
`.gitignore`; the same 11 are expected, and found, at the end (3.4).

Four modules at the base: `tests/test_mates.py tests/test_frames.py
tests/test_joints.py tests/test_declarative_nodes.py` -> `422 passed,
740 subtests passed`; `tests/test_mates.py` alone -> `115 passed, 359
subtests passed`.

## 0.3 Scope

The four scope questions of `proposal.md` are answered as ratified by
the orchestrator (2026-09-27, under the review gate the pilot delegated
on 2026-09-07), as the briefing for this apply states them:

1. The spelling is the freedom left out, `moving.on(fixed)`; there is no
   `Rigid` class. `on(fixed, None)` is the same statement.
2. Every mate is named; a bare rigid mate is refused.
3. A rigid mate read on an instance yields its declaration; assigning to
   it, or naming it as a relation's end or a wiring source, is refused
   naming the mate. It installs no joint, specializes nothing and owns
   no coordinate. A fixed end on any mated child stays refused.
4. A new ADR-152 (NODE) amends ADR-147 and ADR-151, written after
   implementation confirms the design.

Each answer is the recommendation the artifacts were written to, so
nothing was updated before the tests were written. (`proposal.md`
carries its "Scope questions for the pilot" and no separate "Ratified
scope" section; it was left as committed.)

The orchestrator's review findings, also binding here: a mate with a
freedom takes exactly today's path (same objects, same messages in the
same order, base documents byte-identical); a mate with no freedom
compiles to the rest placement only (no joint on the child, no
coordinate on the assembly, nothing in `declared_ports`, nothing new in
the document); a fixed end on a moving child, a second mate on one child
and a `render()` placing the held child stay refused, the last naming
the mate.

## 0.4 Base documents, hashed before any code change

    sha256sum tests/base_documents/*.json

    a8291af0ae42595dfe1ba6f9ba55e76860220d863537ca7084d72b89c94ce4e3  tests/base_documents/clearing.json
    91f85b264d0bd0127795a01d9d753548e43fb668eb63db47d1c4527573c85e7b  tests/base_documents/driverless.json
    1dc9157bef5b1398619d3228f5a217550d813e410fb44e7e13debd43082ce161  tests/base_documents/drivers.json
    5d0b7ee84fe38a395a28da62a8f208a9dcfa713702afd1fa0f5fc4d789be2447  tests/base_documents/flexible.json
    b0e715a7fe7d973575e0d60c2742643a2a14b9e38ea7a036e64ed88893df7c33  tests/base_documents/looping.json
    5e8c4c9a836a6e5c01c87140453c4e9cfc0dba18a8c603a86e1633379f0f2b8d  tests/base_documents/mate_free_arm.json
    746c1e44a6402c4c33b0265bf67754af46dc97b7c164b7f47f784b90cc5f9ff2  tests/base_documents/mated_elbow_machine.json
    440ca6f85cbd371371f11a0a0058c0448a0f3d99a7fc227ac847cac601c4dedf  tests/base_documents/mated_shoulder_machine.json
    ce86901d3d8805732fdcf44fc94e46c2e8b69442b6a13f77b5fb4efdc171b584  tests/base_documents/running_train.json
    4f38e51d27109972fc1f8f21b6d5f49062789986f9706ea3d79e2d3f01db9872  tests/base_documents/sharing.json
    b37128b937f02d082ec8748d552e8bcdd97aa4e0bbfd516391e9a44397bcf897  tests/base_documents/touched_columns.json
    433dc47bba5170c5a035f01be24e4f061adca52a61f92d496c8e37d61b919abe  tests/base_documents/untimed_train.json

(Identical, line for line, to `slide-by-mate`'s 0.4.)

## 1.1 Planning record

    openspec validate hold-by-mate --strict
    Change 'hold-by-mate' is valid

(Run again at the end of this work, with `evidence.md` and the ticked
`tasks.md` in place: still valid.)

## Section 2: red first (`tests/test_mates.py`, fixtures in `tests/mate_project/hold.py`)

**Fixtures** (`tests/mate_project/hold.py`, a new module, no framework
source), with the left knee servo's numbers of `evidence/finding.md`
§3 and §6: `Servo` (`ears`, `ear_near`), `OutputServo` (adds `output =
Revolute(axis=(0, 1, 0))`), `Screw` (`head`), `Plate` (`bores` at the
seat), `Shin`, `PlateShin` (the plate translated `(0, 0, 3)` in
`render()`), `OutputShin`, `BoltedServo` (`screwed =
screw.head.on(servo.ear_near)`) and `BoltedShin`, `Leg` (the revolute
knee mate), `Robot` (`angle.drives(leg.knee)`); the hand-placed twin
`TwinShin` (class-body `knee`, `render()` `rotate(90.0, [0, 1, 0])`,
`rotate(180.0, [1, 0, 0])`, `translate([-0.98, -9.5, -7.0])`),
`TwinPlateShin` (the same onto the translated plate, to
`(-0.98, -9.5, -4.0)`), `TwinBoltedServo`, `TwinBoltedShin`, `TwinLeg`,
`TwinRobot` (`angle.drives(leg.shin.knee)`). The seat is one module
constant, `SEAT`.

The class-creation refusals of 2.2, 2.6 and 2.7 build their assemblies
in the test's own body over two parts declared in `tests/test_mates.py`
beside `Pin` -- `HeldServo` (`ears`, `ear_near`) and `HeldScrew`
(`head`) -- because `hold.py` cannot be imported at the base (its
`Shin` is refused), and a refusal test importing it would be red for
the import, not for its fragments.

**Red** (no framework source edited, `git diff --quiet -- machinome`):

    python -m pytest -q -p no:cacheprovider -rA tests/test_mates.py \
        -k "freedom_out or rigid_mate_has_a_name or other_freedoms or not_a_relations_end or held_once or held_sibling or inherited_child_is_refused or HeldPartTest or HeldTwinTest"
    29 failed, 6 passed, 112 deselected, 25 subtests passed in 1.71s

Each new test red for the reason its task names:

- **2.1** `RefusalTest::test_a_mate_may_leave_its_freedom_out` (replaces
  `test_the_rigid_mate_is_deferred` and
  `test_the_rigid_mate_names_both_freedoms`): red, `TypeError:
  Shin.bolted states no freedom. The rigid mate -- a child placed by two
  frames with no freedom at all -- is not provided in this version
  (deferred, OpenSpec change place-parts-by-mate); ...` importing
  `hold.py`. `test_other_freedoms_are_refused`, its one added fragment
  `no freedom`: both subtests (`Orbit`, `Free`) red on that fragment
  alone.
- **2.2** `RefusalTest::test_a_rigid_mate_has_a_name`: red on `'by its
  name'`, the base message being "Bare: the unnamed mate
  servo.ears.on(servo_seat, ...) states no freedom. ..." (its `Bare` and
  `servo.ears` fragments already passing).
  `test_a_bare_mate_with_a_freedom` green, unedited.
- **2.3** `HeldPartTest::test_the_servo_is_held_at_its_measured_seat`,
  `HeldTwinTest::test_the_held_servo_reproduces_its_twin` and
  `::test_a_held_servo_is_held_on_a_still_siblings_frame`: red importing
  `hold.py` (the rigid mate refused for having no freedom).
- **2.4** `HeldPartTest::test_the_held_servo_is_its_declared_class`,
  `::test_a_rigid_mate_installs_no_joint_and_no_wiring`,
  `::test_a_rigid_mate_is_not_a_port`,
  `::test_a_rigid_mate_may_share_a_name_with_the_childs_attribute`:
  red importing `hold.py`.
- **2.5** `HeldTwinTest::test_a_held_part_rides_with_the_part_that_holds_it`,
  `::test_a_held_assembly_keeps_its_own_mates`,
  `HeldPartTest::test_a_held_part_keeps_its_own_joints_inside_the_placement`:
  red importing `hold.py`.
- **2.6** `HeldPartTest::test_a_rigid_mate_is_read_not_bound`: red
  importing `hold.py`. `RefusalTest::test_a_rigid_mate_is_not_a_relations_end`,
  four routes -- `bolted.drives(travel)` in the body, `(bolted +
  1).drives(travel)` (the design's arithmetic route), `wheel =
  JointedPin(spin=bolted)` (`JointedPin` declares the joint `spin`), and
  a root stating `angle.drives(shin.bolted)` -- each subtest red on
  `'owns no coordinate'`, every base message being "<Class>.bolted
  states no freedom. ...".
- **2.7** `RefusalTest::test_a_held_part_is_held_once` (two rigid mates;
  one rigid and one `Revolute`): red on `again`/`swing` and `loop`;
  `::test_a_fixed_end_on_a_held_sibling_is_refused`: red on `screwed`
  and `'servo'` (its `assertNotIn('moves it')` passing at the base,
  where the rigid mate is refused first); 
  `::test_a_rigid_mate_on_an_inherited_child_is_refused`: red on
  `'servo'` and `Base`. Every base message: "<Class>.bolted states no
  freedom. ...". `HeldPartTest::test_a_held_part_is_not_placed_by_hand`:
  red importing `hold.py`.
- **2.8** `HeldTwinTest::test_a_held_machine_needs_no_newer_consumer`:
  red importing `hold.py`. The guards are the existing tests, run
  unedited: `DocumentTest::test_a_machine_without_mates_is_unchanged_in_every_byte`,
  `StatedLineDocumentTest::test_a_mate_that_states_no_line_is_unchanged_in_every_byte`,
  `SlidingTwinTest::test_a_revolute_mate_still_installs_a_revolute`,
  green at the base and after.

Tally of the recorded run (pytest's "29 failed" counts failed subtests
too): 14 tests FAILED outright (2.1 and every `HeldPartTest` and
`HeldTwinTest` test), 6 tests PASSED at the test level with 15 subtests
SUBFAILED (the narrowed `Orbit`/`Free` test, 2.2, 2.6's four routes,
2.7's three class-creation refusals).

## Section 3: the implementation

- **3.1** `machinome/motion/mates.py`: `_check_freedom` returns early
  for no freedom, and its refusal of another kind names the three forms
  ("a Revolute or a Prismatic in this version, or no freedom at all for
  a part that is held ... or ...on(<fixed>) to hold it"). `declare_mates`
  refuses a bare rigid mate with its own reason ("A mate is known by its
  name: declared_mates reports it under that name, and every refusal
  names it by its name ..."); the bare mate with a freedom keeps its
  message. `Mate.__init__` builds no coordinate for no freedom
  (`coordinate = None`, `coordinates = {}`); `__set_name__` names none;
  `__get__` returns the mate; `__set__` raises `AttributeError`
  ("cannot bind Shin.bolted: 'bolted' is a rigid mate: it states no
  freedom and owns no coordinate. ..."). `described()` reads
  `servo.ears.on(servo_seat)` for a rigid mate (no `, ...`). `_install`
  returns before building a joint. `_check_child_name` is skipped for a
  rigid mate. `_check_fixed`: a fixed end on a child a rigid mate
  places, whose class declares no joint, is refused naming the mate
  that places it and saying this version orders no mate before another;
  a child a rigid mate places whose class declares joints keeps the
  existing "can move ... its class declares the joint(s)" message, and a
  mate with a freedom keeps "the mate '<name>' moves it".
  `_check_moving`'s refusal of a rigid mate on an inherited child says
  "a mate is stated in the class that declares the child it moves, a
  rigid mate included".
- **3.2** The one message, `mates._owns_no_coordinate(written)`, used at
  three seams and by `Mate.__set__`: `coordinate_ref`
  (`machinome/motion/couplings.py`), for a rigid mate named bare (a
  relation's end or a term) and for a `PathRef` whose terminal is a rigid
  mate; `read_through` passes a rigid mate as a place (it previously
  fell through to the sideways-read refusal of a sibling's parameter);
  and `ChildDeclaration.__init__` (`machinome/node/declarative.py`) for a
  rigid mate handed to a child as a keyword. See deviations 2 and 3.
- **3.3** Docstrings: the `mates` module docstring (a held-part example,
  the compile list "a rigid mate to the first alone", `freedom` `None`),
  `Mate` (the rigid mate, its reads, no coordinate), `_check_freedom`,
  `_install`, `apply_mates`, and the new `_is_rigid` and
  `_owns_no_coordinate`.

**Messages, read once** (`probe_hold_messages.py`, scratchpad):

    bare | TypeError | Bare: the unnamed mate servo.ears.on(servo_seat) is never assigned. A mate is known by its name: declared_mates reports it under that name, and every refusal names it by its name, so a mate that holds a part is named as one that frees it: write <name> = servo.ears.on(servo_seat).
    body | TypeError | 'bolted' is a rigid mate: it states no freedom and owns no coordinate. It holds its child where two frames meet and gives nothing to drive, bind or read as a value, so it is not an end of a relation, a term of a derived coordinate or a wiring source. A mate owns a coordinate when it states a freedom: ...on(<fixed>, Revolute(...)) or ...on(<fixed>, Prismatic(...)).
    wiring | TypeError | wiring.<locals>.Wired: JointedPin(spin=bolted) hands a mate to a child as a wiring, and 'bolted' is a rigid mate: ... (as above)
    path | TypeError | 'shin.bolted' is a rigid mate: ... (as above)
    assign | AttributeError | cannot bind Shin.bolted: 'bolted' is a rigid mate: ... (as above)
    loop | TypeError | Twice: the mates 'bolted' and 'again' both move 'servo'. A child is placed by one mate; a second mate on a placed child closes a loop, which this version does not solve.
    fixed on held sibling | TypeError | Screwed.screwed: its fixed end servo.ear_near is on 'servo', which the rigid mate 'bolted' places within Screwed. A mated child is placed against the fixed child's REST placement, and this version orders no mate before another, so 'screw' would not be placed against where 'bolted' puts 'servo'. Mate onto a frame of Screwed itself, or of a child no mate places; a part that holds its own fasteners declares them in its own class.
    fixed on held sibling with joints | TypeError | Screwed.screwed: its fixed end servo.ear_near is on 'servo', which can move within Screwed -- its class declares the joint(s) output. ...
    inherited | TypeError | Mating.bolted: its moving end servo.ears is a child Base declares, and Mating inherits it. In this version a mate is stated in the class that declares the child it moves, a rigid mate included; state the mate in Base, or redeclare 'servo' in Mating.
    orbit | TypeError | A.swing has the freedom Orbit, which is neither a Revolute nor a Prismatic: a mate accepts a Revolute or a Prismatic in this version, or no freedom at all for a part that is held, and Orbit and Free are not mate freedoms. Write Revolute(range=(lo, hi), unit='deg') to turn the part about a line, Prismatic(axis=(x, y, z), range=(lo, hi), unit='mm') to slide it along one, or ...on(<fixed>) to hold it.
    render | ValueError | Handed.render() places 'servo' (['t', ['0', '0', '1']]), and the mate 'bolted' places it: a placement is stated once. Drop the placement from render(), or the mate.

(`wiring.<locals>.Wired` is the probe function's class body, named by
its qualified name.) Every refusal of a mate WITH a freedom takes the code path it
took at the base: the new branches test `freedom is None` (or the
placing mate's) before anything else and fall through otherwise; the
only reworded message a freedom-stating statement can meet is the
`Orbit`/`Free` refusal, which tasks 2.1 and 3.1 ask for.

**Green:** `tests/test_mates.py` -> `132 passed, 403 subtests passed`
(115 at the base, less the two replaced, plus nineteen of section 2);
with the manual test of 4.1, `133 passed`. `tests/test_mates.py
tests/test_frames.py tests/test_joints.py tests/test_declarative_nodes.py`
-> `439 passed, 784 subtests passed` (422 less two plus nineteen), none
of the last three edited, and in `tests/test_mates.py` no existing test
edited but the two replaced and the fragment added to
`test_other_freedoms_are_refused`.

**Mutation runs** (`mates.py` copied, mutated, the suite run, restored
from the copy and checked with `cmp`):

- **M1, the rest placement:** `apply_mates` skips a rigid mate
  (`if mate.freedom is None: continue`): `15 failed, 125 passed` --
  2.3's seat and twin tests (`Shin`, `PlateShin`), the still-sibling
  test, 2.5's ride at every angle, the output joint and the bolted
  assembly, 2.4's shared-name test, 2.8's document and 2.7's hand
  placement (nothing left to clash with). The rest-placement tests
  discriminate.
- **M2, the joint:** `_install` treats a rigid mate as a fresh
  `Revolute()`: `17 failed, 123 passed` -- among them
  `test_a_rigid_mate_installs_no_joint_and_no_wiring` (`<Revolute bolted
  axis=(0, 0, 1) at=(0, -5.5, 0)> is not None`),
  `test_the_held_servo_is_its_declared_class` (`<class ...hold.Servo'>
  is not <class ...hold.Servo'>`, the specialization) and 2.1; the
  placement tests crash, the wiring handing a coordinate-less mate
  (`'Mate' object has no attribute '_value'`).
- **M3, the coordinate:** `Mate.__init__` gives a rigid mate a
  `RotationalPort` it never wires (the rejected alternative of design
  decision 4): `2 failed, 130 passed` --
  `test_a_rigid_mate_is_not_a_port` (`declared_ports(Shin)` non-empty)
  and `test_a_rigid_mate_is_read_not_bound`. Every placement test stays
  green under it, which is the design's warning made concrete: only
  the port and read tests catch a silent, unwired coordinate, and they
  do.

## 3.4 Full suite after the implementation

One run, with every section 0 to 4 edit in place (the implementation,
the tests, the manual, reference, changelog, ADR, architecture, note
and warts):

    python -m pytest -q -p no:cacheprovider -rsf
    11 failed, 3999 passed, 4 skipped, 53 warnings, 2834 subtests passed in 388.82s (0:06:28)

3981 passed at the base, less the two replaced rigid-refusal tests,
plus twenty new: `RefusalTest` 6 (2.1, 2.2, 2.6's routes, 2.7 x3),
`HeldPartTest` 8, `HeldTwinTest` 5, `ManualTest` 1 (4.1). The 11
failures are exactly the base's 11 `machinome vet` tests (0.2), the same
node ids; the 4 skips are the base's four, the same reasons.

**2.8, bytes:** `sha256sum tests/base_documents/*.json` at the end is
identical, line for line, to 0.4 (`diff` empty; `git diff --quiet --
tests/base_documents` holds), and the unedited byte-identity tests pass.
`HeldTwinTest::test_a_held_machine_needs_no_newer_consumer`: `Robot`'s
document and `TwinRobot`'s have the same top-level keys (`animation`,
`drivers`, `format`, `instructions`, `root`, `version`), each equal
between the two but `root`; no node entry of the mated document has a
key set the twin's lacks; the servo's operation kinds are `['r', 't']`
against the twin's `['r', 'r', 't']`, the rotation
`['r', '180', [0.7071067811865476, 0, 0.7071067811865476]]`, the composed
matrices equal within `1e-9`.

## 4.1 The manual

Under `skills/write-the-manual`:

- **Red first:** `ManualTest::test_the_joints_page_states_a_held_part`
  ran red on the unedited page, `IndexError: list index out of range`
  (the section had five code blocks). It execs the sixth block
  (`_code_blocks(section)[5]`), renders the shin and checks the servo's
  two operations (the half turn about `(1, 0, 1)/sqrt(2)`, the
  translation `(-0.98, -9.5, -7)`), `declared_ports(Shin)` empty,
  `type(shin.servo)` the block's `Servo` and `freedom` `None`; asserts
  the paragraph's fragments and the refusal paragraph's "a fixed end on
  a child that can move or that another mate places", and that "a mate
  with no freedom at all" is gone; and asserts the reference sentence
  names ``<child>.<frame>.on(<frame>)``. With the page written and the
  reference not yet edited, it failed on that last assertion alone.
- **Written**, folded into `docs/concepts/joints.rst`, *Frames and
  mates*: the compile paragraph (a mate that holds a part compiles to
  the first of the three alone); the fixed-end and freedom paragraph
  (the fixed child must not be placed by another mate; the freedom may
  be left out for a part that is held); the refusal paragraph (a fixed
  end on a child that can move or that another mate places; the child
  name clash for a mate with a freedom; a mate with no freedom named
  where a coordinate is named; "a mate with no freedom at all" dropped;
  "its coordinate, if it has one, as a binding"); the reads paragraph
  (`name` is the coordinate's when the mate states a freedom; `freedom`
  `None` for a mate that holds a part); and, appended after the gripper
  so the first five blocks keep their indices, a sixth block -- a shin
  holding a servo by `bolted = servo.ears.on(servo_seat)`, the fixture's
  numbers -- with one paragraph: the part is placed connector onto
  connector and given no joint and no coordinate; it is a `Servo`
  itself, `declared_ports(Shin)` is empty, `shin.bolted` reads the mate
  whose `freedom` is `None`, and binding or naming it as a coordinate is
  refused; it moves only as its declaring assembly does, so a held part
  is declared in the class of the part that holds it (and a servo's
  screws beside it in an assembly of servo and screws); the fixed end
  still does not move; a held part may carry its own joints, children
  and mates; the operations may take another form, one rotation where a
  hand writes two. No project is named, no ADR number appears.
- **Build:** `python -m sphinx -E -b html -n -W --keep-going docs <out>`
  at the base (a `git archive HEAD` tree in the scratchpad) and on this
  worktree both report the same 5 warnings -- `api.rst:23/35/76` and
  the `Sim.initial`, `Sim.state` docstrings -- none on a page or
  docstring this change touched (`diff` of the two warning lists
  empty). The built `concepts/joints.html` (the held-part passage) and
  `reference/api.html` (the *Frames and mates* sentence and the `Mate`
  entry with its new docstring) were read as a reader.

## 4.2 Reference

`docs/reference/api.rst`, *Frames and mates*: "``<child>.<frame>.on(<frame>,
Revolute(...))`` or ``<child>.<frame>.on(<frame>, Prismatic(...))``, or
``<child>.<frame>.on(<frame>)`` for a part that is held". No entry
changes; `Mate` renders from its docstring (3.3).
`ManualTest::test_the_reference_lists_frames_and_mates` and
`ManualReadTest` stay green unedited.

## 4.3 Changelog

`docs/project/changelog.rst`, *Unreleased*: a sixth bullet, "A bought
part is held by one statement" -- a mate may leave its freedom out,
`bolted = servo.ears.on(servo_seat)`, placing the part at its seat,
connector onto connector, with no joint and no coordinate, so a servo,
a horn or a screw is declared in the class of the part that holds it and
rides with it; read with `freedom` `None`, not a port, publishing only
operations (ADR-152). `ManualTest::test_the_changelog_names_the_mate_above_the_release`
stays green unedited.

## 4.4 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain the rigid mate: a mate may leave its freedom out,
`<name> = <child>.<frame>.on(<frame>)`, for a part that is held; it
places the moving child at rest from the two frames exactly as any mate
does and gives it nothing else -- no joint (the child stays its declared
class), no coordinate on the assembly (`declared_ports` reports nothing
for it), no wiring; it is always assigned to a name; read on an instance
it yields the mate, and assigning to it, naming it in a relation, a
derived coordinate, a wiring or by path is refused ("owns no
coordinate"); `declared_mates(cls)[name].freedom` is `None`; a held
part is declared in the class of the part that holds it and rides with
it, a fastener in the class of the part it fastens; the fixed end still
does not move, and a fixed end on a sibling any mate places (a rigid one
included) is refused; a held child may carry its own joints, children
and mates; a hand-placed twin compares composed placements, since the
mate writes one rotation where a hand may write two. The refusal of
`Orbit` and `Free` now names the three accepted forms. That is a
separate change in that repository, made by someone else; nothing of it
is made here.

## 4.5 ADR and architecture

`docs/adrs/NODE/ADR-152-a-mate-may-leave-its-freedom-out.md`,
**Accepted**, written after the section-3 runs confirmed the design; it
amends ADR-147 and ADR-151, cites ADR-088 and ADR-098, records the five
rejected alternatives of decisions 1, 3 and 4, and that the dependency
order among sibling mates stays deferred. ADR-147 and ADR-151 gain an
*Amended by* line; `docs/adrs/README.md` indexes ADR-152 under NODE
(after ADR-151) and marks ADR-147 "amended by 148, 150, 151, 152" and
ADR-151 "amended by 152". `docs/architecture.md`: the mate paragraph
(ADR-152 in its citation; the fixed child placed by no mate; the freedom
left out for the rigid mate; "a mate compiles to a rest placement and,
when it states a freedom, a joint and a coordinate"; what a rigid mate
compiles to and where it is refused), and the Map rows *Node model* and
*Motion* gain 152.

## 4.6 The working note

`workflow/ongoing/mates-and-sketches.md`, the paragraph listing what
place-parts-by-mate left out: an *(amended 2026-09-27, hold-by-mate,
ADR-152)* passage -- the rigid mate was cut into `hold-by-mate` from
AlbertPro's bought parts, `moving.on(fixed)` with no `Rigid` class,
compiling to the rest placement alone; the note's "document kind
`fixed`" and "a rigid mate would bring [the dependency order] back" do
not hold for it: the fixed end still does not move, and the dependency
order among sibling mates still reads as proposal. `Free` still reads as
proposal.

## 4.7 Warts

`workflow/warts.md`: "A mate must have a freedom; a part that is simply
held has none." -- **Fixed, 2026-09-27, by `hold-by-mate` (ADR-152)**,
noting that every mate is named, so the statement is assigned rather
than bare as the bullet wrote it; pending AlbertPro's follow-up (tasks
§6). Thor's "A screw cannot be mated to the moving sibling it fastens."
-- **Answered by AlbertPro's shape (hold-by-mate, ADR-152)**: the
fastener is declared in the class of the part it fastens, held there by
a rigid mate; no rule change, a fixed end on a moving sibling stays
refused.

Not done here (the orchestrator's, after review): 5.1 (spec sync,
archive, commit) and section 6 (AlbertPro, in its own repository).

## Where the implementation departs from, or clarifies, `design.md`

None contradicts a ratified behaviour.

1. **The class-creation refusal tests use two parts declared in
   `tests/test_mates.py`** (`HeldServo`, `HeldScrew`, beside `Pin`), not
   `hold.py`'s, so each runs red at the base for its fragments rather
   than for `hold.py`'s import. Their names match the tasks' (`servo`,
   `screw`, `ears`, `ear_near`, `head`, `bolted`, `screwed`).
2. **The wiring refusal is in `ChildDeclaration.__init__`, not in
   `_check_wiring`.** A rigid mate owns no coordinate, so
   `_is_coordinate` never classes it as a wiring: without a refusal it
   would reach the child's constructor as a parameter keyword. It is
   refused where the keyword is read, naming the executing class body's
   qualified name, the child class, the keyword and the mate -- which
   also catches a declaration held in a list, which `_check_wiring`
   never sees.
3. **The path route needed `read_through` too.** `shin.bolted` read in a
   class body fell through `read_through` to the sideways-read refusal
   of a sibling's parameter ("a sibling's parameter is not a value in a
   class body"), which is false. `read_through` now passes a rigid mate
   as a place, as it does a frame, and `coordinate_ref` refuses the
   `PathRef` naming the mate -- the design's seam. Three seams in all
   (`coordinate_ref`, `read_through`, `ChildDeclaration.__init__`), one
   message.
4. **A fourth route is tested**: arithmetic, `(bolted + 1)`, which the
   design names beside the three routes of tasks 2.6.
5. **`_check_fixed` keeps the joint wording for a held child whose class
   declares joints.** The new message ("which the rigid mate '<name>'
   places ... this version orders no mate before another") is given only
   where the rigid mate is the sole reason; a held `OutputServo` as a
   fixed end still "can move -- its class declares the joint(s) output",
   which is true of it.
6. **`Mate.described()` omits `, ...` for a rigid mate**, so a message
   or `repr` shows the statement as written: `servo.ears.on(servo_seat)`.
7. **2.4's "the declaration carries no wiring"** is read as
   `Shin.servo.wiring == {}` and `Shin.servo.node_class is Servo`.
8. **2.8's document test compares the drivers, and every other
   top-level key happens to be equal too**; the spec scenario's "the
   same drivers and bindings" has no top-level `bindings` key in this
   document to compare, and the root's path to the knee differs by
   construction (`leg.knee` against `leg.shin.knee`).

## 5.1 Orchestrator's review (2026-09-27)

Reviewed on the worktree before archive, independently of the applier:
a horn with its own `Revolute` held by `horn.seat.on(hip_horn_hole)` in
a thigh assembly that a leg turns by a revolute mate lands with its seat
on the hole (world `(1.99, 34, 0.66)` for a hip pin at `(0, 30, 0)`, a
hole at `(1.99, 2, 0.66)` with `z=(0,-1,0)` and a seat at `(0, 0, 2)`)
and rides the thigh's turn (`(0.66, 34, -1.99)` at 90°); `declared_mates`
reports it with `freedom None` and `joint None`; the thigh assembly has
no port for it; the horn keeps its own joint and its declared class;
reading it on the instance yields the `Mate`; assigning to it, naming it
as a relation's end, a second mate on the held child and a fixed end on
a moving sibling are refused naming the mate; `test_mates`,
`test_frames`, `test_joints` and `test_declarative_nodes` together 440
passed. Sync: the five MODIFIED blocks were applied by
`evidence/sync_modified.py` (archive refuses the replaced scenario "A
mate needs a revolute or prismatic freedom") and the ADDED requirement
appended by hand; `openspec validate --all --strict` passes; archived
with `--skip-specs`. The proposal's scope questions are ratified at
every recommendation (recorded in 0.3).
