# Evidence: slide-by-mate

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/slide-by-mate` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once. Probes ran from the session scratchpad and are not tests.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/slide-by-mate/machinome/__init__.py

Branch `slide-by-mate`: base `b7cc651` (the implementation commit of
`state-the-freedom-per-instance`, ADR-150), the records commits
`eec8689` ("Record that a gripper's fingers cannot be mated for want of
a prismatic freedom") and `60834c9` ("Record OpenArm's validation of
ADR-150 and its four findings"), and the ratified planning commit
`028edf8` at `HEAD`. The worktree was clean when this work began, and
`git diff --quiet -- machinome` held.

## 0.2 Full suite at the base (planning commit 028edf8)

    python -m pytest -q -p no:cacheprovider -rs -rf

    11 failed, 3962 passed, 4 skipped, 53 warnings, 2733 subtests passed in 405.07s (0:06:45)

The 4 skips are the base's usual four: browser snapshot e2e not
enabled, jscad CLI absent, the two Internal-Cycloidal-Actuator
vendor-STEP cases.

**The 11 failures are pre-existing and not this change's**: the
`machinome vet` tests over fixture projects whose `sim/parts/` modules
`main` never committed (`.gitignore`'s `parts/`), recorded in the same
words by `state-the-freedom-per-instance`'s evidence (0.2):

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
`.gitignore`; the same 11 are expected, and found, at the end (3.5).

Four modules at the base (a `git archive HEAD` tree in the
scratchpad): `tests/test_mates.py tests/test_frames.py
tests/test_joints.py tests/test_declarative_nodes.py` -> `403 passed,
690 subtests passed`; `tests/test_mates.py` alone -> `96 passed`.

## 0.3 Scope

The four scope questions of `proposal.md` are answered under its
"Ratified scope" (the orchestrator, 2026-09-26, under the review gate
the pilot delegated on 2026-09-07):

1. `at` on a `Prismatic` freedom is taken as the `Revolute` freedom's:
   three numbers, left out taking the moving frame's origin, a written
   `(0, 0, 0)` the child's own; `Prismatic` gains the default anchor
   and `anchor_written`.
2. Functions of the assembly in a `Prismatic` freedom are admitted by
   ADR-150's rules unchanged, at no code.
3. A new ADR-151 (NODE) amends ADR-147 and extends ADR-148 and ADR-150,
   written after implementation confirms the design.
4. The axis-less `Prismatic` is struck: a `Prismatic` freedom states its
   axis; the constructor keeps requiring it; the `joints` spec, the site
   refusal and `axisless_refusal` are untouched.

The planning artifacts (`design.md` decision 8, tasks 2.2 and 3.2
struck) already carry these answers, so nothing was updated before the
tests were written.

The orchestrator's review findings, also binding here: a `Revolute`
freedom takes exactly today's path (same objects, same messages in the
same order, base documents byte-identical); a `Prismatic` without an
axis is refused by its constructor and the mate adds no refusal of its
own; `Prismatic`'s `at` default and `anchor_written` share one
definition with `Revolute`, and `Orbit`/`Free` do not gain them; the
mate's coordinate for a `Prismatic` is a `TranslationalPort` in the
freedom's unit, `RotationalPort` only for a freedom `_check_freedom`
refuses.

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

(Identical, line for line, to `state-the-freedom-per-instance`'s 0.4.)

## 1.1 Planning record

    openspec validate slide-by-mate --strict
    Change 'slide-by-mate' is valid

(Run again at the end of this work, with `evidence.md` and the ticked
`tasks.md` in place: still valid.)

## Section 2: red first (`tests/test_mates.py`, fixtures in `tests/mate_project/slide.py`)

**Fixtures** (`tests/mate_project/slide.py`, a new module, no framework
source), with the finger numbers of `evidence/finding.md` §2-3:
`Finger` (`origin = Frame()`); `Palm` (the two seats, the two fingers,
`left_grip` and `right_grip` by `Prismatic(axis=(0, +-1, 0),
range=(-11, 20), unit='mm')`, `left_grip.drives(right_grip)`); `Wrist`;
`Gripper` (`grip = Driver(default=0.0, range=(-11.0, 20.0),
unit='mm')`, `grip.drives(wrist.palm.left_grip)`); `SidePalm` (`left =
Flag(True)`, a seat and an axis that are functions of the side);
`SlotPart` and `SlotMount` (an axis `(1, 0, 0)` across the moving
frame's `z`, no unit); `AnchoredPalm` (`at=(0, 0, 5)`); the hand-placed
twin `TwinLeftFinger`, `TwinRightFinger`, `TwinPalm` (render
translates, the mimic between the fingers' own `travel`), `TwinWrist`,
`TwinGripper`. The side's seat and axis are module functions
(`side_seat`, `side_axis`) rather than lambdas, as `handed.py`'s are.

**Red** (no framework source edited, `git diff --quiet -- machinome`):

    python -m pytest -q -p no:cacheprovider -rA tests/test_mates.py \
        -k "other_freedoms or may_be_a_prismatic or rigid_mate_names_both or slides_stated_anchor_is_three or SlidingMateTest or SlidingTwinTest"
    20 failed, 7 passed, 95 deselected, 17 subtests passed in 2.21s

Each new test red for the reason its task names:

- **2.1** `RefusalTest::test_a_freedom_may_be_a_prismatic`: red, `TypeError:
  Palm.left_grip has the freedom Prismatic, and a mate accepts a
  Revolute only in this version: Prismatic, Orbit and Free are not mate
  freedoms yet. Write Revolute(range=(lo, hi), unit='deg').` The
  narrowed `RefusalTest::test_other_freedoms_are_refused` (its
  `Prismatic` case moved out; `Orbit` and `Free` stay): both subtests
  red on the fragment `'a Revolute or a Prismatic'` (the base message
  names Prismatic only as "not mate freedoms yet"), its other fragments
  passing.
- **3.3, pinned** (the rigid mate's hint names both kinds; the spec
  scenario "A mate needs a revolute or prismatic freedom" lists the
  rigid mate): `RefusalTest::test_the_rigid_mate_names_both_freedoms`,
  red on `'a Revolute or a Prismatic'`.
- **2.3** `SlidingMateTest::test_the_installed_joint_is_a_prismatic` and
  `::test_the_mates_coordinate_is_a_translational_port`: red importing
  `slide.py` (the class refused, the message above).
- **2.4** `SlidingTwinTest::test_the_gripper_reproduces_its_twin` and
  `::test_each_unbound_finger_rests_on_its_seat`: red importing
  `slide.py`. The unbound case was first written on `Palm` and, once the
  implementation existed, found to raise `UnreachedCoordinate: left_grip
  drives right_grip: nothing bound either end` -- as `TwinPalm` does,
  `left_finger.travel drives right_finger.travel: nothing bound either
  end` -- so "unbound" is each side's finger on its own (`SidePalm`),
  and the parity of the refusal is its own test,
  `::test_an_unbound_mimic_is_refused_as_the_twins_is`. Both were then
  run red at the base source (the two source files replaced by `git show
  HEAD:<file>`, the tests run, the files restored from copies and
  checked with `cmp`): `2 failed`, each on the `Palm.left_grip ... accepts a
  Revolute only` refusal at import.
- **2.5** `SlidingMateTest::test_the_mimic_moves_the_fingers_equally_and_oppositely`:
  red importing `slide.py`; `::test_the_range_belongs_to_the_freedom`:
  passed at the test level with both subtests (`grip=25`, `grip=-12`)
  failed, `TypeError` where `JointRangeError` is expected.
- **2.6** `SlidingMateTest::test_a_slides_axis_may_be_a_function_of_the_assembly`:
  red importing `slide.py`.
- **2.7** `SlidingMateTest::test_a_slide_takes_its_stated_axis_not_the_frames_z`
  and `::test_a_slides_stated_anchor_moves_nothing`: red importing
  `slide.py`. `RefusalTest::test_a_slides_stated_anchor_is_three_numbers`
  (a function `at`, and `at=(0, 0, lift)` over a `Length`): both cases
  red on their fragments (`"freedom's at"`, `'a stated anchor is three
  numbers in this version'`, `'resolve against the moving child'`), the
  base message being the kind refusal.
  `SlidingMateTest::test_a_prismatic_without_an_axis_is_refused_by_its_constructor`
  is a GUARD: green at the base (`TypeError: Joint.__init__() missing 1
  required positional argument: 'axis'`) and after.
- **2.8** `SlidingMateTest::test_a_sliding_freedom_is_read_as_written`:
  red importing `slide.py`.
- **2.9** `SlidingTwinTest::test_a_sliding_machine_needs_no_newer_consumer`:
  red importing `slide.py`. Two GUARDS, green at the base and after:
  `::test_a_class_body_prismatic_places_what_it_placed` (a class-body
  `Prismatic((0, 1, 0), range=(-11, 20), unit='mm')` resolves to
  `((0, 1, 0), (0.0, 0.0, 0.0), (-11, 20))` and bound to 10 places
  `[['t', ['0', '10', '0']]]`, the literal read off the base run -- the
  guard of 3.1's anchor default) and
  `::test_a_revolute_mate_still_installs_a_revolute` (the elbow mate's
  joint is exactly a `Revolute` holding the moving frame's declared `z`
  and `at` as the same objects, its coordinate exactly a
  `RotationalPort` in `'deg'`).

Tally of the recorded run (pytest's "20 failed" counts failed subtests
too): 11 tests FAILED outright, 4 tests PASSED at the test level with
every new fragment or case SUBFAILED (9 subtests: 2.1's narrowed test,
the rigid-mate test, 2.5's range test, 2.7's anchor refusals), 3 guards
green.

## Section 3: the implementation

- **3.1** `machinome/motion/joints.py`: a private base
  `_MateFreedom(Joint)` holds the one `__init__(self, axis,
  at=_DEFAULT_ANCHOR, range=None, unit=None)` and the one
  `anchor_written` property; `Revolute` and `Prismatic` derive from it,
  `Revolute` keeping its own `__init__` that makes `axis` optional (the
  only one that does). `Orbit` and `Free` are untouched. `Prismatic`'s
  `axis` stays the first, required argument.
- **3.3** `machinome/motion/mates.py`: `_check_freedom` accepts a
  `Revolute` or a `Prismatic` and applies every check to both in the
  same order; the refusal of anything else says it is "neither a
  Revolute nor a Prismatic" and names both as accepted; the rigid
  mate's hint names both. `Mate.__init__` builds its coordinate as
  `_coordinate_kind(freedom)(unit=...)`: the freedom's own
  `coordinate_kind` for a `Revolute` or `Prismatic`, `RotationalPort`
  otherwise. `_install` builds a `Prismatic` for a `Prismatic` freedom
  and a `Revolute` otherwise, from today's expressions, except that a
  `Prismatic`'s `axis` is passed straight through and never replaced by
  the moving frame's `z` (see deviations). A `Prismatic` freedom's own
  refusals speak of a line to slide along (`_check_stated(...,
  slides=True)`, `_result_reason(..., slides=True)`, `_slides(freedom)`);
  every `Revolute` freedom message is unchanged byte for byte.
- **3.4** Docstrings: the `mates` module docstring (a sliding example,
  items 2 and 3 of the compile list), `Mate` (the coordinate's kind; the
  reads: `freedom` a `Revolute` or `Prismatic`, `unit` `'deg'` or
  `'mm'`), `_check_freedom`, `_check_stated`, `_result_reason`,
  `_install`, the new `_coordinate_kind` and `_slides`; `joints.py`
  `_DefaultAnchor`, `_MateFreedom`, `Revolute`, `Prismatic`.

**Green:** `tests/test_mates.py` -> `115 passed, 359 subtests passed`
(96 at the base plus the nineteen of this change, the manual test
included); `tests/test_mates.py tests/test_frames.py
tests/test_joints.py tests/test_declarative_nodes.py` -> `422 passed,
740 subtests passed` (403 at the base plus nineteen), none of the last
three edited, and in `tests/test_mates.py` no existing test edited but
`test_other_freedoms_are_refused` (plus `TranslationalPort` added to an
import line).

**Messages, read once** (`probe_slide_messages.py` in a scratch project
with a `[tool.machinome]` manifest). Five `Revolute` freedom refusals --
a zero axis, a function `at`, a token `at`, a freedom already declared,
a function returning a zero axis -- were read with the base source and
with the implementation and are identical after normalizing object
addresses (`diff` empty). The new or kind-specific ones:

    orbit | TypeError | A.swing has the freedom Orbit, which is neither a Revolute nor a Prismatic: a mate accepts a Revolute or a Prismatic in this version, and Orbit and Free are not mate freedoms. Write Revolute(range=(lo, hi), unit='deg') to turn the part about a line, or Prismatic(axis=(x, y, z), range=(lo, hi), unit='mm') to slide it along one.
    rigid | TypeError | A.swing states no freedom. The rigid mate -- a child placed by two frames with no freedom at all -- is not provided in this version (deferred, OpenSpec change place-parts-by-mate); a mate's freedom is a Revolute or a Prismatic: ...on(<fixed>, Revolute(range=(lo, hi))) to turn the part, ...on(<fixed>, Prismatic(axis=(x, y, z), range=(lo, hi))) to slide it.
    prismatic zero axis | TypeError | A.slide: its freedom's axis (0, 0, 0) has zero length, and an axis of zero length states no line to slide along. State the direction of the line.
    prismatic function at | TypeError | A.slide: its freedom's at <function ...> is a function, and a stated anchor is three numbers in this version: at=(x, y, z), in the moving child's own frame. A freedom's axis and range may each be one function of the assembly that states the mate, its at may not; leave at out to take the moving frame's origin.
    prismatic already declared | TypeError | A.slide: its freedom is already declared on A. A mate's freedom becomes a joint of the child it moves, so it is written fresh in the statement: ...on(<fixed>, Prismatic(axis=(x, y, z), range=(lo, hi))).
    prismatic zero result | ParameterError | A.slide: its freedom's axis function returned (0, 0, 0) for this A, which has zero length, and an axis of zero length states no line to slide along. The function is called with the A that states the mate, as it builds 'part', and what it returns is taken as the axis written in numbers is: three real numbers with a direction, read in the moving child's own frame.
    prismatic no axis | TypeError | _MateFreedom.__init__() missing 1 required positional argument: 'axis'
    prismatic axis=None | TypeError | Part.slide is a Revolute without an axis. An axis may be left out only in a mate's freedom -- moving.on(fixed, Revolute(...)) -- where the moving frame supplies it; everywhere else a joint states the line it turns about: Revolute(axis=(x, y, z), ...).
    class-body Prismatic(None) | TypeError | B.travel is a Revolute without an axis. An axis may be left out only in a mate's freedom -- ...

The last two are the base's own behaviour for an explicit
`Prismatic(None)` anywhere: `Joint.__set_name__`'s axis-less refusal,
whose wording names a `Revolute` (unchanged; the ratified scope leaves
`axisless_refusal` alone). As a mate's freedom it fires on the installed
joint, naming the child's class, because `_install` passes a
`Prismatic`'s axis straight through.

**Mutation run for the port kind** (`_coordinate_kind` made to return
`RotationalPort` for every freedom; `mates.py` restored from a copy and
checked with `cmp`):

    FAILED ...SlidingMateTest::test_a_slide_takes_its_stated_axis_not_the_frames_z
        AssertionError: <rotational port declaration slide> is not an instance of <class 'machinome.motion.ports.TranslationalPort'>
    SUBFAILED(mate='left_grip') ...::test_the_mates_coordinate_is_a_translational_port
    SUBFAILED(mate='right_grip') ...::test_the_mates_coordinate_is_a_translational_port
    3 failed, 113 passed, 348 subtests passed

Every other test stays green under it -- the placements, the twin
comparison and the exported document included -- which is design
decision 5's warning made concrete: a rotational coordinate in
millimetres passes a document that publishes no program. Only the
port-kind tests catch it, and they do.

**Mutation run for the joint kind** (`_install`'s `kind` forced to
`Revolute`, restored and checked with `cmp`): `16 failed, 111 passed`
-- 2.3's joint test, 2.5's mimic, 2.6, 2.7's axis and anchor tests, 2.4's
twin comparison at every grip and 2.9's document, the fingers turning
where the twin slides.

## 3.5 Full suite after the implementation

One run, with every section 0 to 4 edit in place (the implementation,
the tests, the manual, changelog, ADR, architecture, note and warts):

    python -m pytest -q -p no:cacheprovider -rsf
    11 failed, 3981 passed, 4 skipped, 53 warnings, 2783 subtests passed in 408.42s (0:06:48)

3962 passed at the base plus nineteen new tests: `RefusalTest` 3 (2.1,
the rigid mate, 2.7's anchor refusals), `SlidingMateTest` 9 (2.3 x2,
2.5 x2, 2.6, 2.7 x3, 2.8), `SlidingTwinTest` 6 (2.4 x3, 2.9 and its two
guards), `ManualTest` 1 (4.1). The 11 failures are exactly the base's
11 `machinome vet` tests (0.2), the same node ids; the 4 skips are the
base's four, the same reasons.

**2.9, bytes:** `sha256sum tests/base_documents/*.json` at the end is
identical, line for line, to 0.4 (`diff` empty; `git diff --quiet --
tests/base_documents` holds), and the unedited byte-identity tests
`DocumentTest::test_a_machine_without_mates_is_unchanged_in_every_byte`
and `StatedLineDocumentTest::test_a_mate_that_states_no_line_is_unchanged_in_every_byte`
pass. `test_a_freedom_stating_no_line_takes_the_frames` passes
unedited. `SlidingTwinTest::test_a_sliding_machine_needs_no_newer_consumer`:
`Gripper`'s document declares the version `TwinGripper`'s declares, the
same top-level keys and drivers, each finger's operations equal the
twin's (the driven slide as the same strings, `grip` on the left and
`(grip * -1)` on the right; the rest translation within `1e-9`), and no
node entry has a field set the twin's document lacks.

## 4.1 The manual

Under `skills/write-the-manual`:

- **Red first:** `ManualTest::test_the_joints_page_states_a_sliding_freedom`
  ran red on the unedited page, `IndexError: list index out of range`
  (the section had four code blocks). It execs the fifth block
  (`_code_blocks(section)[4]`), checks `declared_ports(Palm)['left_grip']`
  is a `TranslationalPort` in `'mm'`, binds `palm.left_grip = 10` and
  checks both fingers' first operations, `(0, 10, 0)` and `(0, -10, 0)`;
  asserts the paragraph's fragments on the whitespace-normalized
  section; and asserts the reference sentence names `Prismatic(...))`.
- **Written**, folded into `docs/concepts/joints.rst`, *Frames and
  mates*: the freedom paragraph (a `Revolute`, the one place a
  `Revolute` may leave out its axis, or a `Prismatic`, which states its
  axis here as it does anywhere); the refusal list ("a freedom that is
  neither a fresh `Revolute` nor a fresh `Prismatic`"); the reads
  paragraph (`freedom` is the `Revolute` or `Prismatic` as written; the
  line a mate turns its child about, or slides it along); and, appended
  after the handed example so the first four blocks keep their indices,
  a fifth block -- a palm whose two fingers are mated by `Prismatic`
  freedoms on mirrored axes and related by
  `left_grip.drives(right_grip)` -- with one paragraph: the part slides
  along the line instead of turning about it, by the same rules (the
  frames fix the rest and the zero; `at` and `range` as a `Revolute`
  freedom's; an `axis` or `range` may be a function of the assembly);
  a `Prismatic` always states its `axis`, only a `Revolute` freedom
  leaving it to the moving frame; a stated `at` moves nothing on a
  slide and is carried as the joint's anchor; the finger gets a
  `Prismatic` joint and the palm's coordinate is a length, in `'mm'`
  unless the freedom states a unit; binding `palm.left_grip = 10` moves
  the fingers 10 along `(0, 1, 0)` and `(0, -1, 0)`. The three edited
  paragraphs were rewrapped. No project is named, no ADR number appears.
- **Build:** `python -m sphinx -E -b html -n -W --keep-going docs <out>`
  at the base (a `git archive HEAD` tree in the scratchpad) and on this
  worktree both report the same 5 warnings -- `api.rst:23/35/76` and
  the `Sim.initial`, `Sim.state` docstrings -- none on a page or
  docstring this change touched. The built `concepts/joints.html` (the
  sliding passage) and `reference/api.html` (the `Prismatic` entry,
  rendered `Prismatic(axis, at=(0, 0, 0), range=None, unit=None)` with
  its new docstring, and the *Frames and mates* sentence) were read as a
  reader.

## 4.2 Reference

`docs/reference/api.rst`, *Frames and mates*: "``<child>.<frame>.on(<frame>,
Revolute(...))`` or ``<child>.<frame>.on(<frame>, Prismatic(...))``, and
needs no import beyond ``Revolute`` or ``Prismatic``". No entry changes;
`Prismatic` and `Mate` render from their docstrings (3.4).
`ManualTest::test_the_reference_lists_frames_and_mates` and
`ManualReadTest` stay green unedited (`Revolute.anchor_written.__doc__`,
now `_MateFreedom`'s, still carries "moving frame's origin").

## 4.3 Changelog

`docs/project/changelog.rst`, *Unreleased*: a fifth bullet, "A
gripper's fingers are mated like its links" -- a mate's freedom may be
a `Prismatic`, sliding the part along the line it states by the
`Revolute` freedom's rules; it states its `axis`; the part gets a
`Prismatic` joint, the mate's coordinate is a length in `'mm'` unless a
unit is stated, and the slide is published as a class-declared
`Prismatic`'s translation (ADR-151). The first bullet's "Revolute mates
only;" was dropped, since the same *Unreleased* section now provides a
sliding mate ("Documents are unchanged (ADR-147)." stays).
`ManualTest::test_the_changelog_names_the_mate_above_the_release` stays
green unedited.

## 4.4 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain the sliding freedom: a mate's freedom may be a
`Prismatic`, `<child>.<frame>.on(<frame>, Prismatic(axis=(x, y, z),
range=(lo, hi), unit='mm'))`, which slides the moving child along the
stated line in its own rest frame by the `Revolute` freedom's rules --
the frames fix the rest placement and the zero; `at` is three numbers,
left out the moving frame's origin, a written `(0, 0, 0)` the child's
own, and moves nothing on a slide; `axis` and `range` may each be one
function of the assembly -- save that a `Prismatic` always states its
`axis` (only a `Revolute` freedom may leave it to the moving frame's
`z`); the child gets a `Prismatic` joint under the mate's name and the
assembly a translational coordinate in `'mm'` unless a unit is stated;
a URDF mimic is a relation between the two mates' coordinates,
`left_grip.drives(right_grip)`; `declared_mates(...)[name].freedom` is
the `Prismatic` as written, `anchor_written` included; the refusal of a
non-`Revolute` freedom it may list now names `Orbit` and `Free` only.
That is a separate change in that repository, made by someone else;
nothing of it is made here.

## 4.5 ADR and architecture

`docs/adrs/NODE/ADR-151-a-mates-freedom-may-be-a-prismatic.md`,
**Accepted**, written after the section-3 runs confirmed the design;
it amends ADR-147, extends ADR-148 and ADR-150, cites ADR-112 and
records the four rejected alternatives. ADR-147 gains an *Amended by*
line; `docs/adrs/README.md` indexes ADR-151 under NODE (after ADR-150)
and marks ADR-147 "amended by 148, 150, 151". `docs/architecture.md`:
the Kinematics mate paragraph (the freedom a fresh `Revolute` or a fresh
`Prismatic`, the shared `_MateFreedom`; (2) a joint of the freedom's
kind, the moving frame's `z` a `Revolute` freedom's only, a slide's
anchor carried for a control's origin; (3) a coordinate of the
freedom's port kind in its unit, chosen by `_coordinate_kind`), its ADR
citation, and the Map rows *Node model* and *Motion* gain 151.

## 4.6 The working note

`workflow/ongoing/mates-and-sketches.md`, the paragraph listing "the
rigid mate, `Prismatic` and `Free` freedoms" as left out: an *(amended
2026-09-26, slide-by-mate, ADR-151)* sentence -- the `Prismatic` freedom
was cut into `slide-by-mate` from open_manipulator's gripper fingers;
the rigid mate and `Free` still read as proposal.

## 4.7 Warts

`workflow/warts.md`, "A gripper's fingers cannot be mated", the bullet
"A mate's freedom must be a `Revolute`.": **Fixed, 2026-09-26, by
`slide-by-mate` (ADR-151)**, noting that the axis-less `Prismatic` the
bullet anticipated ("taken from the moving frame's `z`") was struck at
ratification; pending open_manipulator's follow-up (tasks §6).

Not done here (the orchestrator's, after review): 5.1 (spec sync,
archive, commit) and section 6 (open_manipulator, in its own
repository).

## Where the implementation departs from, or clarifies, `design.md`

None contradicts a ratified behaviour.

1. **A `Revolute` freedom's zero-length and function-`at` messages are
   unchanged, not reworded.** Tasks 3.3 and design decision 4 ask the
   zero-length refusals to say "states no line", not "no line to turn
   about"; the review finding requires a `Revolute` freedom to take
   exactly today's path with the same messages. Both are kept by making
   the wording kind-aware: a `Revolute` freedom's messages are byte for
   byte the base's (probed, `diff` empty), and a `Prismatic` freedom's
   say "states no line to slide along. State the direction of the line."
   (no "leave axis out" advice, which a `Prismatic` cannot take) and
   "leave at out to take the moving frame's origin". The existing
   fragment test `'an axis of zero length states no line'` holds for
   both.
2. **`_install` passes a `Prismatic` freedom's `axis` straight through**
   rather than reusing today's `freedom.axis if freedom.axis is not None
   else frame.z`: with that expression an explicit `Prismatic(axis=None)`
   would be admitted with the moving frame's `z`, the struck axis-less
   `Prismatic` by the back door. As written it is refused, as a
   class-body `Prismatic(None)` is, by `Joint.__set_name__`'s existing
   axis-less refusal (probe above). The joint kind is chosen by
   `isinstance(freedom, Prismatic)`, not `type(freedom)(...)`, so a
   project's subclass of `Revolute` still installs exactly a `Revolute`,
   as today.
3. **The shared definition is a private base, `_MateFreedom`**, holding
   the `__init__` with the `_DEFAULT_ANCHOR` default and
   `anchor_written`. Python's refusal of an axis-less `Prismatic` now
   names `_MateFreedom.__init__()` where the base named
   `Joint.__init__()`; the words that matter, "missing 1 required
   positional argument: 'axis'", are the same.
4. **The unbound case of 2.4 is `SidePalm`, one finger per side**, not
   `Palm`: a palm whose mimic has nothing bound at either end refuses to
   render (`UnreachedCoordinate`), exactly as its twin does, and that
   parity is pinned by its own test.
5. **Three tests the tasks do not list**: the rigid mate's hint naming
   both kinds (3.3; the spec scenario lists the rigid mate), the unbound
   mimic's parity with the twin (above), and the `Revolute` mate guard
   (the review finding: same objects, `RotationalPort` in `'deg'`). 2.3
   and 2.7 are split into one test per behaviour, and 2.7's two anchor
   refusals sit in `RefusalTest` with the other class-creation
   refusals.
6. **The changelog's first bullet loses "Revolute mates only;"**, which
   the new bullet in the same *Unreleased* section contradicts.
7. **The reference sentence names both spellings**,
   `...on(<frame>, Revolute(...))` or `...on(<frame>, Prismatic(...))`,
   and the manual test pins it.

## 5.1 Orchestrator's review (2026-09-26)

Reviewed on the worktree before archive, independently of the applier:
a palm with two fingers mated by `Prismatic` freedoms (one axis a
function of the palm's flag, one with a written anchor `(0, 0, 3)`),
mimicked by `left_grip.drives(right_grip)` and driven from a root's mm
driver, installs two `Prismatic` joints with the stated lines and
anchors, reports both coordinates as `TranslationalPort` in `'mm'`,
reads the freedom's `axis`, `at`, `anchor_written`, `range` and `unit`
as written, binds both at 12.0 and refuses 25.0 by `JointRangeError`
naming the mate; a mate with no freedom is still refused with the
rigid-mate hint naming both kinds; `test_mates`, `test_frames`,
`test_joints` and `test_declarative_nodes` together 422 passed. One
finding, recorded in `workflow/warts.md`: a `Prismatic(axis=None)`
written as a freedom (or in a class body) is refused by the joint's
pre-existing axis-less refusal, whose wording says "is a Revolute
without an axis" for any kind. Sync: the six MODIFIED blocks were
applied by `evidence/sync_modified.py` because `openspec archive`
refuses the scenario this change deliberately replaces ("A mate needs a
revolute freedom" → "A mate needs a revolute or prismatic freedom");
`openspec validate --all --strict` passes; archived with `--skip-specs`.
