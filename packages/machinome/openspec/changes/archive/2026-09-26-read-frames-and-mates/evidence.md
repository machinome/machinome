# Evidence: read-frames-and-mates

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/read-frames-and-mates` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once. Nothing outside this worktree was read for writing; Thor was
not touched.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/read-frames-and-mates/machinome/__init__.py

Branch `read-frames-and-mates`, base commit `0b0eae5` ("Record Thor's
validation of state-the-mate-line and the note's cut status"), planning
commit `7ace70f` at `HEAD` ("Propose read-frames-and-mates: a
documented read of resolved frames and of a mate's ends and freedom").
The worktree was clean when this work began.

## 0.2 Full suite at the planning commit (7ace70f)

    python -m pytest -q -p no:cacheprovider -rs

    3826 passed, 4 skipped, 53 warnings, 2536 subtests passed in 433.59s (0:07:13)

The 4 skips: browser snapshot e2e not enabled
(`MACHINOME_WEB_SNAPSHOT_E2E`), jscad CLI absent, the two
Internal-Cycloidal-Actuator vendor-STEP cases.

## 0.3 Scope

The three scope questions of `proposal.md` were taken at their
recommendations, ratified on 2026-09-26 by the orchestrator's
adversarial review under the review gate the pilot delegated on
2026-09-07, on the pilot's instruction of 2026-09-26 to work the
`place-parts-by-mate` findings with Thor as the validator
(`proposal.md`, "Ratified scope"):

1. `described()` stays undocumented and unchanged; Thor reads the
   attributes.
2. A class, a declaration or a read before resolution is refused by
   name.
3. No ADR.

The review's note for the implementer -- task 2.3 may pin the identity
of the read's objects with the cache through `frames.RESOLVED_KEY` in a
test, and the public read must not depend on anything the test reads
privately -- is followed: `test_the_read_holds_the_objects_the_mate_composes`
reads `RESOLVED_KEY`; `resolved_frames` reads the cache through the same
module constant it owns. None differs from the recommendation, so the
planning artifacts stand as ratified.

## 1.1 Planning record

    openspec validate read-frames-and-mates --strict
    Change 'read-frames-and-mates' is valid

(run at the start and again after section 4). No ADR.

## Section 2: red first

New classes only. `tests/test_frames.py`: `ResolvedReadTest`,
`ResolvedReadRefusalTest`, and module helpers `resolved_frames` (the
function imported where a test calls it), `_rest_matrix` (Rodrigues, so
the file needs no geometry library) and `_upper_arm` (the spec
scenario's arm: `reach` token, child `art3` whose class `Art3` declares
`hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`, mate
`elbow`). `tests/test_mates.py`: `MateReadTest`, `ManualReadTest`
(reusing `_section`, `_code_blocks`, `DOCS`), the helper
`resolved_frames`, and the fixture classes `Swung`/`Swinging` (2.10's
`Revolute(axis=(0, 0, 2))` on a part whose `hinge = Frame(at=(0, 0, 5))`).
The existing `resolved()` helper, `ManualTest` and every fixture file are
unedited: `git diff --numstat tests/` is `373 0 tests/test_frames.py`,
`192 0 tests/test_mates.py`.

**Red** (no framework source or documentation edited,
`git diff --quiet -- machinome docs` held):

    python -m pytest -p no:cacheprovider tests/test_frames.py tests/test_mates.py \
        -k "ResolvedRead or MateReadTest or ManualReadTest" -rA --tb=line
    42 failed, 7 passed, 102 deselected   (failures counted per subtest)

Per task:

- **2.1** `ResolvedReadTest::test_the_numbers_are_read_off_the_instance`,
  `::test_frames_are_read_in_declaration_order`: red, `ImportError:
  cannot import name 'resolved_frames' from 'machinome.node.frames'`.
- **2.2** `::test_the_default_x_is_read_on_each_principal_z` (six
  frames, expected triads written out), `::test_a_stated_x_is_read_squared_up`,
  `::test_the_rotations_columns_are_the_read_triad`: red, the same
  `ImportError`.
- **2.3** `::test_the_read_is_what_the_mate_composes`,
  `::test_the_read_holds_the_objects_the_mate_composes` (identity through
  `RESOLVED_KEY`), `::test_a_mated_child_reads_as_its_declared_class`:
  red, the same `ImportError`.
- **2.4** `::test_a_function_is_not_called_by_the_read`: red, `ImportError`.
- **2.5** `::test_each_read_is_a_fresh_mapping`: red, `ImportError`.
- **2.6** `::test_a_node_declaring_no_frame_reads_nothing`,
  `::test_a_dropped_frame_is_not_read`: red, `ImportError`.
- **2.7** `ResolvedReadRefusalTest::test_a_class_is_refused`,
  `::test_a_child_declaration_is_refused`, `::test_a_frame_is_refused`,
  `::test_a_number_is_refused`, `::test_a_read_from_check_is_refused`:
  red, `ImportError` (for the `check()` case raised from inside
  `check()` during construction). One further refusal test, beyond the
  task list, pins the spec's "from a function given as one of its frame
  arguments": `::test_a_read_from_a_frame_argument_is_refused` -- red on
  its fragments `'TypeError'` and `'check()'`, because at the base the
  callable raised `ImportError`, which the argument rule wrapped as
  `ParameterError` (see "Clarifications" below).
- **2.8** `DeclarationTest::test_importing_frames_adds_nothing_outside_the_framework`:
  existing, unedited; green before and after (the new function imports
  `AbstractBaseNode` inside itself; `frames.py` keeps `math` as its only
  module-scope import).
- **2.9** `MateReadTest::test_the_ends_and_freedom_of_a_mate_stating_no_line`
  (`MatedArm.elbow`), `::test_a_fixed_end_on_a_child_is_read_as_written`
  (`Pedestal.yaw`): **GREEN GUARDS** at the base, as the task names them
  -- the attributes exist; this change documents them.
- **2.10** `::test_a_stated_line_is_read_as_written` (`VerbatimShoulder`,
  `AnchoredHousing`, `VerbatimWrist`), `::test_a_left_out_anchor_is_read_as_not_written`
  (`Swinging.swing`: `axis == (0, 0, 2)` as written, `anchor_written is
  False`): **GREEN GUARDS** at the base. The `resolved_frames`
  comparison is its own test,
  `::test_a_left_out_anchor_is_the_moving_frames_resolved_origin`
  (installed anchor `(0.0, 0.0, 5.0)` equals `resolved_frames(part)['hinge'].at`
  and differs from `freedom.at`): red, `ImportError`.
- **2.11** `::test_the_mates_line_from_the_documented_reads_alone`: red
  in all six subtests (`MatedArm.elbow`, `Pedestal.yaw`,
  `VerbatimShoulder.shoulder`, `AnchoredHousing.shoulder`,
  `VerbatimWrist.wrist`, `Swinging.swing`), `ImportError`.
- **2.12** `ManualReadTest::test_the_reference_lists_the_reads`: red,
  `'.. autofunction:: machinome.node.frames.resolved_frames' not found`
  (and the `ResolvedFrame` and `Mate` entries, and `:members: rotation`).
  `::test_the_docstrings_state_the_reads`: red on eleven subtests --
  `ResolvedFrame` lacks `columns`, `int`, `float`, `rotation()`; `Mate`
  lacks `declared_mates`, `name`, `anchor_written`, `moving frame's
  origin`; `FrameRef.written` has no docstring (`"'<child>.<frame>'" not
  found in ''`); `Frame.name` lacks `mate.fixed.name`;
  `Revolute.anchor_written` lacks `moving frame's origin`.
- **2.13** `ManualReadTest::test_the_joints_page_reads_frames_and_mates`:
  red, `AssertionError: 2 not greater than or equal to 3` (no third
  block). The test execs block 0 then block 2 in one namespace (block 2
  builds on block 0's `UpperArm`, as its prose says) and checks the
  section states `(0.0, 150.0, 68.0)`, `resolved_frames`,
  `anchor_written` and `'forearm.hinge'`.

**After `resolved_frames` (3.1), before any docstring:**
`16 failed, 25 passed, 102 deselected, 39 subtests passed` -- every
code test green; only 2.12 and 2.13 (documentation) still red.
**After the docstrings (3.2):** only the two api.rst/manual tests red.
**After section 4:** `tests/test_frames.py tests/test_mates.py`
`129 passed, 321 subtests passed`.

### Mutation runs (2.1 to 2.5 discriminate)

Each mutation replaced `resolved_frames`'s last line in
`machinome/node/frames.py`; the section-2 code tests
(`-k "ResolvedRead or MateReadTest"`) ran; the file was restored from a
copy and compared with `cmp` (identical).

- **re-resolves** (`{name: frame.resolve(node) for ...}`): red
  `test_the_read_holds_the_objects_the_mate_composes` (2.3, identity) and
  `test_a_function_is_not_called_by_the_read` (2.4, the count moved).
  2.1's and 2.2's numbers are equal under a re-resolution, so they stay
  green: re-resolution is caught by 2.3 and 2.4, as designed.
- **returns the cache itself** (`return cached`): red
  `test_each_read_is_a_fresh_mapping` (2.5).
- **returns the declarations** (`dict(declared)`): red 2.1
  (`test_the_numbers_are_read_off_the_instance`), 2.2 (all six
  default-`x` subtests, the squared-up `x`, the rotation columns), 2.3
  (all three), 2.4 -- 13 failures.
- **declaration order lost** (`sorted(declared)`): red 2.1
  (`test_frames_are_read_in_declaration_order`) and 2.2's default-`x`
  test (which pins its order too).
- **re-derives from the declaration, Thor-style** (normalize `z`, take
  the stated `x` normalized without squaring it up or the principal
  default, `y = z x x`, no snapping, `float()` of each literal): red 2.2
  (six default-`x` subtests on the `int` components, the squared-up `x`),
  2.1, 2.3, 2.4, 2.5 (the `reach` token cannot be `float()`ed), and one
  2.11 subtest -- 13 failures.

## 3.1, 3.2 Implementation

`machinome/node/frames.py`: `resolved_frames(node)` added and put in
`__all__` -- `isinstance(node, type)` -> `TypeError` naming the class,
saying a frame resolves against the instance that declares it (its
arguments may read its parameters or be a function of it) and naming
`declared_frames(<Class>)` and `resolved_frames(<Class>(...))`; a local
`from machinome.node.base import AbstractBaseNode` and a non-node ->
`TypeError` naming its type and "reads a realized node"; then
`declared = declared_frames(type(node))`, `cached =
node.__dict__.get(RESOLVED_KEY, {})`, any declared name missing from
`cached` -> `TypeError` naming the class and the missing frames and
saying a node's frames resolve after its `check()` and its joints;
else `{name: cached[name] for name in declared}`. `_placement` is not
rewritten onto it. Nothing else in any module changed but docstrings:
the `frames` module docstring (the two reads, the attribute read giving
the declaration), `ResolvedFrame` (attributes, types, snapping,
`rotation()` columns, read not assigned, never constructed by a
project), `Frame.name` (a mate's fixed end on the assembly's own frame
reads as `mate.fixed.name`), `resolve_declared_frames` (the
constructor's hook, not a read); `mates` module docstring (a mate read
off the class), `FrameRef.written` (`'<child>.<frame>'`), `Mate` (`name`,
`moving`, `fixed`, `freedom` with `axis`, `at`/`anchor_written`,
`range`, `unit`, the line rule; read off the class because on an
instance it reads its coordinate); `joints.Revolute.anchor_written`
(false: `at` is the default and a mate's anchor is the moving frame's
origin). `described()` is neither documented nor changed.

### Clarifications (no ratified behaviour changed)

- **A read from a frame or joint argument's callable.** `resolved_frames`
  raises `TypeError` there as the spec says, but the constructor calls
  such a callable through the existing argument rule
  (`joints.resolved_vector`), which reports ANY exception a callable
  raises as `ParameterError` naming the class, the frame or joint and
  the argument, with "the callable raised TypeError: <the read's
  message>". The read's refusal therefore reaches the author wrapped,
  as every callable's failure does; the new test pins that the wrapped
  message names the class, the frame, `TypeError` and `check()`. From
  `check()` the `TypeError` arrives unwrapped. Changing the argument
  rule was out of scope and not done.
- **2.10 split.** The green guard and the `resolved_frames` comparison
  are two tests, so the guard's green and the comparison's red are each
  recorded honestly.

## 3.3 Full suite at the end

    python -m pytest -q -p no:cacheprovider -rs

    3853 passed, 4 skipped, 53 warnings, 2593 subtests passed in 453.04s (0:07:33)

3826 + 27 new tests (18 in `test_frames.py`, 9 in `test_mates.py`);
subtests 2536 + 57; the same four skips; no existing test edited.

## 4.1 to 4.5 Documentation and records

- **4.1** `docs/concepts/joints.rst`, "Frames and mates": after the
  refusal paragraph, a passage and the section's THIRD code block
  (blocks 0 and 1 unchanged): `resolved_frames` on `UpperArm(reach=150)`
  and its forearm, `declared_mates(UpperArm)['elbow']`'s
  `moving.written`, `fixed.name`, `freedom.range`,
  `freedom.anchor_written`; why a built node (a frame may read its
  parameters; `declared_frames` gives the declaration; the attribute
  read gives the declaration); the refusals; the resolved frame's types
  and `rotation()` columns, read not assigned; the mate's `name`, the
  two forms of `fixed`, `freedom`, `at` only with `anchor_written`, and
  the line rule in one sentence. No project is named (write-the-manual
  rule 3); only public reads are used (rule 5), and the block runs in
  `ManualReadTest`.
- **4.2** `docs/reference/api.rst`, "Frames and mates": the lead
  sentence names the read; after the existing three entries,
  `.. autofunction:: machinome.node.frames.resolved_frames`,
  `.. autoclass:: machinome.node.frames.ResolvedFrame` with
  `:members: rotation`, `.. autoclass:: machinome.motion.mates.Mate`.
- **4.3** `docs/project/changelog.rst`, Unreleased: a third bullet,
  "Frames and mates read back". `ManualTest::test_the_changelog_names_the_mate_above_the_release`
  stays green.
- **4.4** `docs/architecture.md`, the frame paragraph: after "cached as
  `_frame_arguments`", the clause -- read publicly on the instance by
  `resolved_frames` (those very objects, a fresh mapping, the three
  refusals), never off the class.
- **4.5** `workflow/warts.md`: the sixth `place-parts-by-mate` bullet
  gains **Fixed, 2026-09-26, by `read-frames-and-mates`**, the note that
  ADR-147's rejected alternative's reason is overtaken and its decision
  stands, and **Pending** the Thor follow-up of tasks §7.

## 4.6 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain: `from machinome.node.frames import
resolved_frames`; `resolved_frames(node)` on a realized node gives
`{name: ResolvedFrame}` in declaration order -- `at` three floats, unit
`x`, `y`, `z` with exact `0`/`1`/`-1` integers, `rotation()` rows whose
columns are `x`, `y`, `z` -- the numbers the mates compose, read not
assigned; refused (`TypeError`) on a class (use `declared_frames`), a
non-node, or before resolution (from `check()` or an argument's
callable); and a mate's documented reads off the class through
`declared_mates(cls)[name]`: `name`, `moving.written`
(`'<child>.<frame>'`), `fixed` (a reference with `written`, or the
assembly's own `Frame` with `name`), `freedom.axis` (as written or
`None`), `freedom.at` only when `freedom.anchor_written` (else the
anchor is the moving frame's origin), `freedom.range`, `freedom.unit`;
and the line rule. `described()` is not part of the contract. That is a
separate change in that repository, made by someone else; nothing of it
is made here.

## 4.7 Sphinx

    python -m sphinx -E -b html -n -W --keep-going docs <scratch>/html

The first build reported one NEW warning, on a touched docstring:
`frames.py:docstring of machinome.node.frames.ResolvedFrame:6: WARNING:
Inline interpreted text or phrase reference start-string without
end-string` (`` `float`s ``); reworded to "three `float` values". The
rebuild reports exactly the five pre-existing warnings
(`api.rst:23`, `api.rst:35`, `api.rst:76`, the `Sim.initial` and
`Sim.state` docstrings) and none on a page or docstring this change
touched. The built `reference/api.html` (the three new entries,
`ResolvedFrame.rotation` listed) and the new passage of
`concepts/joints.html` were read as text. `tests/test_docs_structure.py`
and `tests/test_profile_documentation.py` pass.

Section 5 (sync, archive, commit), 6 and 7 are not done here: the
orchestrator reviews first, and 7 is Thor's, in Thor's repository.

## 5.1 Sync and archive (the orchestrator, after review)

The reviewer re-ran the full suite from a clean shell (`3853 passed, 4
skipped, 2593 subtests`, the applier's counts), built the manual with
`-n -W` (the same five pre-existing warnings, none on a touched page),
validated the change `--strict`, read the source, test and documentation
diffs, and probed the read on the originating project's ten root-chain
frames against its guard's own re-derivation: maximum deviation 0, the
five mates' documented reads as expected, and a class refused by name.
Two review edits: the delta spec's third refusal says that from a frame
or joint argument's function the refusal reaches the author as the
argument rule reports any error a function raises, quoting it (the
applier's clarification, pinned by its extra test); and two over-long
lines in `docs/architecture.md` and `docs/concepts/joints.rst` were
re-wrapped. The delta adds requirements only, so `openspec archive`
synced the baseline spec itself.
