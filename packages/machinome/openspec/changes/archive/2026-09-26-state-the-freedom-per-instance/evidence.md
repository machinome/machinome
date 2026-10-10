# Evidence: state-the-freedom-per-instance

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/state-the-freedom-per-instance`
with `PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/state-the-freedom-per-instance/machinome/__init__.py

Branch `state-the-freedom-per-instance`: base `61f2335` (framework
`main`, "Implement vet-the-project ... (ADR-149)"), the records commit
`9e228fa` ("Record the SO-ARM100 migration's findings and openarm's
per-instance need"), and the ratified planning commit `5a336b7` at
`HEAD`. The worktree was clean when this work began, and
`git diff --quiet -- machinome` held.

## 0.2 Full suite at the base (planning commit 5a336b7)

    python -m pytest -q -p no:cacheprovider -rs

    11 failed, 3946 passed, 4 skipped, 53 warnings, 2664 subtests passed in 402.67s (0:06:42)

The 4 skips: browser snapshot e2e not enabled, jscad CLI absent, the two
Internal-Cycloidal-Actuator vendor-STEP cases.

**The 11 failures are pre-existing and not this change's.** All are
`machinome vet` tests over fixture projects whose `sim/parts/` modules
were never committed: the repository's `.gitignore` line 20, `parts/`,
ignores `tests/vet_projects/pure_project/sim/parts/` (and the
`star_import` fixture's), so `vet-the-project`'s commit `61f2335` holds
`sim/model.py` importing `sim.parts.gear` without the package
(`git check-ignore -v --no-index tests/vet_projects/pure_project/sim/parts/gear.py`
-> `.gitignore:20:parts/`; `git ls-tree -r main` holds no
`vet_projects/*/sim/parts` path). Reproduced alone,
`pytest tests/test_vet_*.py` -> `11 failed, 62 passed`:

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
`.gitignore`; the same 11 are expected, and found, at the end (3.6).
Repairing them (force-adding the fixtures, or an exception in
`.gitignore`) is a separate fix on `main`, not made here.

## 0.3 Scope

The four scope questions of `proposal.md` were ratified at every
recommendation (the orchestrator's briefing of 2026-09-26, under the
review gate the pilot delegated on 2026-09-07), and are recorded there
under a new "Ratified scope":

1. The function receives the ASSEMBLY that states the mate (design
   decision 1).
2. `at` stays numbers; a function `at` is refused with its own reason.
3. No read of the resolved values is added.
4. A new ADR-150 (NODE) amends ADR-147 and ADR-148, written after
   implementation confirms the design.

None differs from the recommendation, so the planning artifacts stand
as ratified.

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

## 1.1 Planning record

    openspec validate state-the-freedom-per-instance --strict
    Change 'state-the-freedom-per-instance' is valid

(Run again at the end of this work: still valid.)

## Section 2: red first (`tests/test_mates.py`, fixtures in `tests/mate_project/handed.py`)

**Fixtures** (`tests/mate_project/handed.py`, a new module, no framework
source): `HandedLink` (`origin = Frame()`, no `left`); `HandedMount`
(`left = Flag(False)`, `pin = Frame(at=side_origin)`, `link =
HandedLink()`, `turn = link.origin.on(pin, Revolute(axis=side_axis,
range=side_range, unit='deg'))`); `ContraryLink` (its own `left =
Flag(True)`) and `ContraryMount` (as `HandedMount` over it, `left` not
passed, its axis function `contrary_axis` recording every node it is
called with in `CONTRARY_CALLS`); `HandedPair` (a driver `angle`,
default 30, onto `left.turn` and `right.turn`); the hand-placed twins
`TwinLink` (`left`, `turn = Revolute(axis=side_axis, range=side_range)`
over its own `left`), `TwinMount` (`render()` translating the link to
its side's origin) and `TwinPair`. The side's origin, axis and range
are module functions (`side_origin`, `side_axis`, `side_range`) rather
than the tasks' lambdas, so 2.8 can assert identity with what was
written; OpenArm's joint 1 numbers.

**Red** (no framework source edited, `git diff --quiet -- machinome`):

    python -m pytest -q -p no:cacheprovider -rA tests/test_mates.py \
        -k "may_be_a_function or anchor_is_not_a_function or HandedFreedom or HandedTwin or stated_line_is_numbers or depends_on_a_declarer"

Every new test red, each for the reason its task names:

- **2.1** `RefusalTest::test_a_freedom_axis_or_range_may_be_a_function`:
  both subtests (`axis`, `range`) red on the removed refusals,
  `TypeError: Handed.swing: its freedom's axis <function ...> is a
  callable of the node, which would be called with the moving child.`
  and `... its freedom's range <function ...> is a callable of the node,
  which would be resolved against the moving child.` The two narrowed
  tests, `test_a_stated_line_is_numbers` (its `callable_axis` case moved
  out) and `test_a_freedom_range_that_depends_on_a_declarer` (its `whole`
  case moved out), passed with their remaining cases.
- **2.2** `RefusalTest::test_a_stated_anchor_is_not_a_function`: red on
  the fragment, `'a stated anchor is three numbers in this version' not
  found in "Anchored.swing: its freedom's at <function ...> is a
  callable of the node, which would be called with the moving child..."`
  (and on `'called with the moving child' unexpectedly found`).
- **2.3** `HandedFreedomTest::test_the_handed_joint_resolves_per_side`
  and `::test_the_handed_range_belongs_to_each_side`: red importing
  `handed.py`, `TypeError: HandedMount.turn: its freedom's axis
  <function side_axis ...> is a callable of the node, which would be
  called with the moving child.`
- **2.4** `HandedFreedomTest::test_the_function_receives_the_assembly_not_the_child`
  (the child without `left`) and `::test_the_childs_own_flag_is_not_read`
  (`ContraryMount`, the child's own contrary `left`): red on the same
  class refusal. Because that red says nothing about WHICH node is
  handed the function, both were shown to discriminate by mutation after
  the implementation (below). (2.4 is two tests rather than one so each
  case is seen red on its own under the mutation.)
- **2.5** `::test_the_function_is_called_once_per_realized_assembly`,
  **2.6** `::test_the_function_sees_the_assembly_as_a_sites_function_does`,
  **2.8** `::test_a_function_is_read_as_written`: red on the class
  refusal (`Counted.swing`, `Based.swing`, `Counted.swing` resp.).
- **2.7** `::test_a_functions_result_is_taken_as_the_numbers_are`: all
  ten subtests red (axis `(0, 1)`, `(0, 0, 0)`, `(0, 0, True)`,
  `'xyz'`, a function, raising `KeyError`; range `(0,)`, `(True, 90)`, a
  pair holding a `Bound` that reads a declared port, raising) on the
  class refusal of the mount, a `TypeError` at class creation where the
  test needs the class created and a `ParameterError` at realization;
  `::test_a_returned_axis_is_normalized_as_a_written_one` red the same
  way.
- **3.4, pinned** (a test the tasks do not list, added for the review
  finding that the lazy path refuses a marked joint by the mate's name
  and its assembly and never calls the function with the child):
  `::test_a_handed_link_built_outside_its_mount_is_refused`, red on the
  class refusal.
- **2.9** `HandedTwinTest::test_the_handed_pair_reproduces_its_twin` and
  `::test_each_unbound_side_rests_as_its_twin`, **2.10**
  `::test_a_handed_machine_needs_no_newer_consumer`: red importing
  `handed.py` (its `HandedMount` is refused), the only failure they can
  have at the base; they are guards of the implementation's geometry
  and bytes, shown to discriminate by the mutation below.
  `::test_each_unbound_side_rests_as_its_twin` was split out of the pair
  test after the first green run showed a pair whose driver is unbound
  does not render (`AttributeError: driver 'angle' of HandedPair is not
  bound`), so "unbound" is each side's mount on its own; it was then
  run red at the base source separately (the three source files
  replaced by `git show HEAD:<file>`, the test run, the files restored
  from copies and checked with `cmp`): `TypeError: HandedMount.turn:
  its freedom's axis <function side_axis ...> is a callable of the
  node, which would be called with the moving child.`

Tally of that run: 11 tests FAILED outright, 2 tests (2.1, 2.7) PASSED
at the test level with every subtest failed (13 SUBFAILED), and the two
narrowed tests passed.

## Section 3: the implementation

- **3.1** `machinome/motion/mates.py`, class creation. `_check_freedom`
  admits a function `axis` and a whole-range function (`_is_function`:
  callable, no `dimension`, not a `Bound`) and passes every other value
  through the rules it had. The rules are factored so both moments word
  them once: `_stated_reason(value)` (three real numbers),
  `_has_no_length(axis)` (the joint's `1e-9`) and `_range_reason(range)`
  (the pair rule). `_check_stated` refuses a function `at` first, with
  its own reason: "is a function, and a stated anchor is three numbers
  in this version: at=(x, y, z), in the moving child's own frame. A
  freedom's axis and range may each be one function of the assembly
  that states the mate, its at may not; leave at out to turn about the
  moving frame's origin." Every class-creation refusal of a non-function
  value -- tokens, formulas, `bool`s, lengths, a zero axis, a range
  token, a `Bound` with reads -- keeps its message byte for byte.
- **3.2** `_install`: construction unchanged (the function passed
  through as the joint's `axis` or `range`); `joint._resolved_by_mate =
  True` when the freedom states a function. `Joint` carries the class
  default `_resolved_by_mate = False`, so every other joint, a numbers
  mate's included, is untouched.
- **3.3** `call_freedom_functions(declaration, assembly)` calls each
  function once with the realized assembly and checks its result
  (`_result_reason`: a function result refused as such, then
  `_range_reason` or `_stated_reason` plus `_has_no_length`), raising
  `ParameterError` "`<Assembly>.<mate>`: its freedom's `<argument>`
  function returned `<repr>` for this `<Assembly>`, which `<reason>`."
  or "... raised `<Type>: <message>` when called with this
  `<Assembly>`.", then the rule the result is taken by.
  `resolve_freedom_functions(child, called)` copies the installed joint
  (`copy.copy`), puts each result in its function's place and runs
  `Joint.resolve(child, <child's parameters>)`, caching under
  `_joint_arguments[<mate>]`. `ChildDeclaration.realize` calls the first
  BEFORE constructing the child (only when the declaration has a
  wiring, where a mate lives) and the second right after, before the
  wiring is recorded and site joints resolved.
- **3.4** `machinome/motion/joints.py`: `resolve_declared_joints` skips
  a joint with `_resolved_by_mate`, as it skips a site-declared one;
  `Joint.arguments`' lazy path refuses one by `_unreached_by_mate`,
  a `ParameterError` naming the child's class and joint, the mate
  `<Assembly>.<mate>` and the assembly, and never calls the function.
- **3.5** Docstrings: the `mates` module docstring (the handed example,
  item 2 of the compile list), `Mate` (the reads may be the function),
  `_check_freedom`, `_check_stated`, `_install`, the new functions;
  `joints.py` `Revolute`, `Joint.arguments`, `resolve_declared_joints`;
  `declarative.py` `ChildDeclaration.realize`.

**Green:** `tests/test_mates.py` -> `96 passed, 309 subtests passed`
(with the 4.1 manual test); `tests/test_mates.py tests/test_frames.py
tests/test_joints.py tests/test_declarative_nodes.py` -> `402 passed,
685 subtests passed`, none of the last three edited.

**Messages, read once** (a scratch project with a `[tool.machinome]`
manifest, `probe_messages.py`):

    ParameterError | Refusing.turn: its freedom's axis function returned (0, 1) for this Refusing, which has 2 components, not three. The function is called with the Refusing that states the mate, as it builds 'link', and what it returns is taken as the axis written in numbers is: three real numbers with a direction, read in the moving child's own frame.
    ParameterError | Refusing.turn: its freedom's axis function raised AttributeError: 'Refusing' object has no attribute 'nope' when called with this Refusing. ...
    ParameterError | HandedLink.turn: range -- (90, 0) is reversed: a range is (lo, hi)
    ParameterError | HandedLink.turn: this is the joint the mate HandedMount.turn gives 'link', and its freedom states a function of HandedMount, called with the realized HandedMount as it builds 'link'. This HandedLink was built outside HandedMount, so there is no HandedMount to call it with; the function is never called with the moving part itself. Build it as the child 'link' of a HandedMount.

A range function returning a reversed `(90, 0)` is refused by the
joint's own resolution with exactly the message `range=(90, 0)` written
in the freedom gets (design decision 4's last sentence).

**Mutation run for 2.4** (the joint resolved against the child instead
of the assembly: `_install`'s `joint._resolved_by_mate = True` replaced
by `pass`, so the child's constructor resolves the installed class
joint and calls the function with the child -- design decision 1's
rejected option (b); `mates.py` restored from a copy afterwards and
checked with `cmp`):

    FAILED ...::test_the_function_receives_the_assembly_not_the_child
        ParameterError: HandedLink.turn: axis -- the callable raised AttributeError: 'HandedLink' object has no attribute 'left'
    FAILED ...::test_the_childs_own_flag_is_not_read
        AssertionError: <...ContraryLink object> is not <...ContraryMount object>

and a probe of `ContraryMount(left=False)`: implemented, `axis (0, -1,
0) called with ContraryMount`; mutated, `axis (0, 1, 0) called with
ContraryLink` -- the silent wrong side the design's risk names. Under
the same mutation every other section-2 test that builds a
`HandedMount` goes red (2.3, 2.9, 2.10, the lazy-path test), 2.6 red
(`Pin.swing: axis -- the callable raised AttributeError: 'Pin' object
has no attribute 'base'`), and 2.7 red on every subtest (the refusal
names `HandedLink.turn`, the CHILD's class, not `Refusing.turn`, and
the `Bound`-with-reads result is not refused at all); 2.5, 2.8 and
`test_a_returned_axis_is_normalized_as_a_written_one` stay green, as
they must (the count, the reads and the normalization do not depend on
which node is handed the function).

## 3.6 Full suite after the implementation

One run (`full-1`), with every section 0 to 4 edit in place (the
implementation, the tests, the manual, changelog, ADR, architecture,
note and warts):

    python -m pytest -q -p no:cacheprovider -rs -rf
    11 failed, 3962 passed, 4 skipped, 53 warnings, 2733 subtests passed in 403.43s (0:06:43)

3946 passed at the base plus sixteen new tests: `RefusalTest` 2 (2.1,
2.2), `HandedFreedomTest` 10 (2.3 x2, 2.4 x2, 2.5, 2.6, 2.7 x2, 2.8, the
3.4 lazy-path test), `HandedTwinTest` 3 (2.9 x2, 2.10), `ManualTest` 1
(4.1). The 11 failures are exactly the base's 11 `machinome vet` tests
(0.2), the same node ids; the 4 skips are the base's count. No existing
test was edited but the two narrowed in 2.1; `tests/test_frames.py`,
`tests/test_joints.py` and `tests/test_declarative_nodes.py` are
unedited and green.

**2.10, bytes:** `sha256sum tests/base_documents/*.json` at the end is
identical, line for line, to 0.4 (`diff` empty; `git diff --quiet --
tests/base_documents` holds), and the unedited byte-identity tests
`DocumentTest::test_a_machine_without_mates_is_unchanged_in_every_byte`
and `StatedLineDocumentTest::test_a_mate_that_states_no_line_is_unchanged_in_every_byte`
pass. `test_a_freedom_stating_no_line_takes_the_frames` (the installed
joint of a mate stating no function holds the moving frame's declared
`z` and `at` as the same objects) passes unedited.
`HandedTwinTest::test_a_handed_machine_needs_no_newer_consumer`:
`HandedPair`'s document declares the version `TwinPair`'s (a machine
without mates) declares, the same top-level keys and drivers, each
link's operations equal the twin's (rotation angles as the same token,
components within `1e-9`), and no node entry has a field set the twin's
document lacks.

## 4.1 The manual

Under `skills/write-the-manual`:

- **Red first:** `ManualTest::test_the_joints_page_states_a_handed_freedom`
  ran red on the unedited page, `IndexError: list index out of range`.
  The *Frames and mates* section already had THREE code blocks (the
  upper arm, the shoulder across its connector, and the reads block
  `ManualReadTest.test_the_joints_page_reads_frames_and_mates` addresses
  as index 2), so the handed example is the FOURTH block, placed after
  the reads paragraph at the section's end, and the test reads
  `_code_blocks(section)[3]`; every existing index is kept.
- **Written**, folded into `docs/concepts/joints.rst`, *Frames and
  mates*: the stated-line paragraph (a stated line holds no parameter
  or formula; its `axis` may be a function, its `at` is three numbers);
  the freedom paragraph (axis three numbers or one function of the
  assembly, at three numbers, the range a pair or one function); the
  refusal list (loses "a function axis" and "a range that reads the
  node", gains "a function `at`", and a clause for the realization
  refusal); the reads paragraph (`axis` and `range` may read a function,
  not called; what it returned is not a read); and a new passage with
  the fourth example -- a handed `Mount` whose frame, axis and range are
  functions of its `left` flag, over a `Link` with no `left` -- saying
  every `node` is the mount, the function is called with the assembly
  that states the mate, once, as it builds the moving part, in the
  state described, its result taken as the numbers are and read in the
  part's own frame, each side's numbers, and that a stated `at` stays
  three numbers. No project is named. The test EXECUTES the example,
  realizes both sides, and checks each installed joint's axis and range
  and each link's rest.
- **Build:** `python -m sphinx -E -b html -n -W --keep-going docs <out>`
  at the base (a `git archive HEAD` tree in the scratchpad) and on this
  worktree both report the same 5 warnings, `api.rst:23/35/76` and the
  two `Sim` docstrings; none on a page or docstring this change touched.
  The built `concepts/joints.html` was read as a reader; one sentence
  was reworded after (`` ``at=`` stays three numbers`` -> ``A stated
  ``at`` stays three numbers``) and the build re-run (4.7).

## 4.2 Changelog

`docs/project/changelog.rst`, *Unreleased*: a fourth bullet, "A handed
design mates per instance" -- a freedom's `axis` and `range` each one
function of the assembly that states the mate, called once as it builds
the moving part; the result taken as numbers are; `at` stays three
numbers (ADR-150).

## 4.3 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain the handed freedom: as a mate's freedom,
`Revolute(axis=<function>, range=<function>, ...)`, each one function
of the ASSEMBLY that states the mate (the node the class body belongs
to, as a frame's function of that assembly is), called once as the
assembly realizes the moving child, never with the child; its result
taken as numbers written there are (an axis three numbers with a
direction in the moving child's frame, a range pair); a result that is
not, or a function that raises, refused at realization naming the
assembly, the mate and the argument; a function `at` refused at class
creation (a stated anchor is three numbers); `declared_mates(...)`
`freedom.axis`/`range` read the function as written, and no read gives
what it returned. The refusal of a function axis or range it may still
list goes. That is a separate change in that repository, made by
someone else; nothing of it is made here.

## 4.4 ADR and architecture

`docs/adrs/NODE/ADR-150-a-mates-freedom-may-be-a-function-of-the-assembly-that-states-it.md`,
**Accepted**, written after the section-3 run confirmed the design;
ADR-147 and ADR-148 gain *Amended by* lines; `docs/adrs/README.md`
indexes ADR-150 under NODE (after ADR-148; ADR-149 is BUILD) and marks
ADR-147 "amended by 148, 150" and ADR-148 "amended by 150".
`docs/architecture.md`: the Kinematics mate paragraph (the freedom's
`axis` and `range` may be a function of the assembly, called by
`ChildDeclaration.realize` before the child is constructed, checked,
resolved against the child by `Joint.resolve`; the `_resolved_by_mate`
mark, skipped by `resolve_declared_joints`, refused by the lazy path),
its ADR citation, and the Map rows *Node model* and *Motion* gain 150.

## 4.5 The working note

`workflow/ongoing/mates-and-sketches.md`, §5.2's "*Range and `Bound`*":
an *(amended 2026-09-26, state-the-freedom-per-instance, ADR-150)*
sentence -- a whole-range function of the assembly and a function
`axis` are admitted, called once with the realized assembly; tokens,
formulas, a `Bound` with reads and a function `at` stay refused.

## 4.6 Warts

`workflow/warts.md`, "A handed design cannot state its mates per
instance", first bullet: **Fixed, 2026-09-26, by
`state-the-freedom-per-instance` (ADR-150), for `axis` and `range`**;
`at` stays three numbers; pending openarm's follow-up (tasks §6).

## 4.7 Reference

`docs/reference/api.rst`: no entry changes (no new read). The `Mate`
entry is rendered from its docstring, which carries 3.5's wording
("the function itself, the same object" appears in the built
`reference/api.html`), and `Revolute`'s docstring says its axis and
range may each be one function of the assembly as a mate's freedom.
`ManualTest::test_the_reference_lists_frames_and_mates` and
`ManualReadTest` stay green unedited.

**Sphinx, final** (after the one-sentence rewording in 4.1):
`python -m sphinx -E -b html -n -W --keep-going docs <out>` -> the same
5 pre-existing warnings (`api.rst:23/35/76`, `Sim.initial`,
`Sim.state`), none on `concepts/joints.rst`, `project/changelog.rst` or
a docstring this change touched. `openspec validate
state-the-freedom-per-instance --strict` -> valid.

Not done here (the orchestrator's, after review): 5.1 (spec sync,
archive, commit) and section 6 (openarm, in its own repository).

## Where the implementation departs from, or clarifies, `design.md`

None contradicts a ratified behaviour.

1. **The substitution is a shallow copy of the installed joint**
   (`copy.copy(mate.joint)`, the result set on the copy's `axis` or
   `range`, `resolve` run on the copy), not a change to `Joint.resolve`'s
   signature: the joint's rules run unchanged, in one place, and the
   installed joint is never mutated.
2. **The mark is `Joint._resolved_by_mate`**, a class-level default
   `False` on `Joint`, set `True` only by `_install`.
3. **The realization call is guarded by the declaration's `wiring`**
   (a mate is recorded there by `_install`), so a declaration with no
   wiring does no extra work at all; one with a wiring and no marked
   mate finds an empty list and takes today's path.
4. **Class-creation messages for non-function values are unchanged
   byte for byte**, including `_check_freedom`'s range refusal, whose
   closing advice still names numbers, `None` and functions of the
   coordinate: the review finding's "same refusal messages" was read
   strictly. The admission of a function is taught by the manual, the
   docstrings and the new function-`at` refusal.
5. **2.4 and 2.9 are each split in two** (the child without `left` /
   the contrary child; the bound pair / each unbound mount on its own),
   because a pair whose driver is unbound refuses to render and each
   2.4 case must be seen red on its own under the mutation.
6. **A lazy-path test** (`test_a_handed_link_built_outside_its_mount_is_refused`)
   pins 3.4, which the tasks implement but do not test.
7. **The fixtures' functions are module-level** (`side_origin`,
   `side_axis`, `side_range`, `contrary_axis`) rather than lambdas, so
   2.8 asserts identity with what was written.
8. **The manual's handed example is the section's fourth block**, not
   its third (the reads block already holds index 2).

## 5.1 Orchestrator's review (2026-09-26)

Reviewed on the worktree before archive, independently of the applier:
the handed fixtures resolve `((0, 1, 0), (0, 0, 0), (-200, 80))` on the
left and `((0, -1, 0), (0, 0, 0), (-80, 200))` on the right; the
contrary child's own `left=True` is not read; a subclass inheriting the
mate is realized as the subclass instance; a function is called once
across two bindings and a render; a numbers-only mate is unmarked and
its class default is `False`; a function returning two components, a
zero axis, a `bool` bound, or raising, is refused as `ParameterError`
naming the assembly's class, the mate and the argument; a reversed
returned range is refused by the joint's own message as for numbers; a
mated child built outside its assembly is refused by the lazy path
naming the mate and its assembly; `tests/test_mates.py` 96 passed and
`test_frames`/`test_joints`/`test_declarative_nodes` 307 passed. The
delta spec is as ratified. Sync: `openspec archive` refuses a MODIFIED
block that drops a baseline scenario ("A stated line is numbers", which
this change deliberately narrows to "A stated line holds no
parameter"), so the three MODIFIED blocks were applied by
`evidence/sync_modified.py` and the ADDED requirement appended by hand,
`openspec validate --all --strict` passing, and the change archived with
`--skip-specs`. The 11 `vet` failures at the base are `main`'s: commit
`61f2335` lacks `tests/vet_projects/*/sim/parts/`, kept out by
`.gitignore`'s `parts/`; reported to the pilot, not touched here.
