## 0. Before anything

- [ ] 0.1 Work only in `solid-node/WTs/controls-on-parts` (branch
  `controls-on-parts`, base `33d8bf5`), with `PYTHONPATH="$PWD"` and the
  workspace venv `/home/asa/devel/libresolid-studio/.venv/bin/python`,
  run from inside the worktree so its `.env` is read. Confirm
  `git rev-parse --show-toplevel` prints that worktree and
  `python -c "import solid_node; print(solid_node.__file__)"` prints the
  WORKTREE path. Never write inside
  `/home/asa/devel/libresolid-studio/projects/`, never write in the
  pilot's primary `solid-node/` checkout, and never run npm.
- [ ] 0.2 Record the FULL SUITE at the base (`python -m pytest -x -q`),
  exact counts, into `evidence.md`. Any failure here is pre-existing and
  must be shown to be so before task 9.
- [ ] 0.3 Record the BASE per-tick cost by running
  `openspec/changes/archive/2026-09-13-run-owns-the-coordinates/evidence/probe_cost.py`
  on this worktree and pasting the output into `evidence.md`. Task 4
  moves two methods off `Run`; this is the number that move is
  answerable to.
- [ ] 0.4 **Capture the base documents this cycle must not change.**
  Before touching any source, extend `tests/base_documents/` with a
  RUNNING root's document — `tests.running_project.machine:Train`, as
  `running_train.json`, written by `tests/test_running_document.py`'s own
  `document()` helper with `mtime` normalized exactly as
  `ByteIdentityTest.normalized` does. Do NOT commit it (nothing is
  committed before the reviewer's commit 2); keep it in the working tree
  as base evidence beside the test that reads it: a version 5 document
  with no controls must come back byte-identical, and a capture taken
  AFTER the change would prove nothing. Record the byte count and the
  base commit it was captured at in `evidence.md`.
- [ ] 0.5 Record the base `tests/running-corpus.json` digest
  (`sha256sum tests/running-corpus.json`) in `evidence.md`, and the
  `program.identity` of each corpus machine as the committed fixture
  reports it. Task 8.3 must reproduce both.
- [ ] 0.6 Probe and paste, so the design's load-bearing facts are
  evidence rather than claims: (a) that `Columns.units.dial`, written in
  a class body, is a `PathRef` whose terminal is a `ChildDeclaration`,
  that `PathRef._walk(instance)` returns the realized leaf, and that
  `qualified.instance_path(leaf, root)` is `('units', 'dial')`; (b) that
  `Revolute(axis=(1,0,0), at=(0,3,0))` places
  `[['t', [-0,-3,-0]], ['r', <id>, [1,0,0]], ['t', [0,3,0]]]` on its
  node while `Revolute(axis=(1,0,0))` places the rotation alone, so
  `origin` is needed (design §8); (c) that a pure pass over
  `edge.increments` seeded with one input's displacement reproduces, to
  the last bit, what `sim.move(input, by=eps, duration=0)` commits on a
  fresh simulation (design §6); (d) that `2**-20` as the displacement
  makes an affine chain read exactly `-36.0` in BOTH directions while
  `1e-3` reads `-36.000000000000004`.
- [ ] 0.7 Grep the worktree and every project under
  `/home/asa/devel/libresolid-studio/projects/` for `controls =` on a
  node class and paste the result into `evidence.md`. Design §2 reserves
  the name; this is the evidence that nothing in the workspace pays for
  the reservation.

## 1. The fixtures

Project-style code, no meshes, added beside the existing running
fixtures. Nothing here changes an existing fixture's meaning.

- [ ] 1.1 `tests/running_project/parts.py`: `Dial`, a leaf with geometry
  and NO coordinate — the part a hand touches. (`Block` is the existing
  nothing-moves leaf; a separate name makes the fixtures read.)
- [ ] 1.2 `tests/running_project/machine.py`: `DialArbor`, an ASSEMBLY
  declaring `turn = Revolute(axis=(1, 0, 0), unit='deg')` and holding
  `dial = Dial()`. This is the Pascaline's own shape — the joint at
  depth, the touchable leaf beneath it — which no existing fixture has,
  because `Arbor` is a leaf and can hold nothing.
- [ ] 1.3 `tests/running_project/machine.py`: `Columns`, the fixture
  shaped like the Pascaline module's tree. A running root with two
  drivers `units_entry` and `tens_entry` in `'digit'`; `units` and
  `tens` as `DialArbor`s; a leaf `frame` nothing moves;
  `units_entry.drives(units.turn, ratio=-36.0)` and
  `(tens_entry & units.turn).drives(tens.turn, law=carried_column)`, so
  `tens.turn` is reached by BOTH inputs and `units.turn` by one;
  instructions `'Add one'` and `'Add ten'` stating `by=`; and
  ```python
  controls = {
      'units dial': Button(units.dial, 'Add one'),
      'tens dial':  Button(tens.dial, 'Add ten'),
      'turn units': Turn(units.dial, units_entry),
      'turn tens':  Turn(tens.dial, tens_entry),
  }
  ```
  Declare `time`, the children and the controls on ONE class: a control
  names a class-body declaration, and splitting it over a body/base pair
  the way the law fixtures do would only make the reference read
  `ColumnsBody.units.dial`.
- [ ] 1.4 `tests/running_project/machine.py`: `OffCentre`, a running root
  whose posing joint is `Revolute(axis=(1, 0, 0), at=(0, 3, 0))`, for the
  `origin` case of design §8.
- [ ] 1.5 `tests/running_project/machine.py`: one fixture per refusal, each
  a running root except where the refusal is about not being one —
  `Unposed` (a control on a leaf no joint poses), `Sliding` (a `Turn`
  over a `Prismatic`), `Unreached` (a `Turn` naming an input that does
  not reach the coordinate), `Unnamed` (a `Button` naming an undeclared
  instruction), `TwoJoints` (a posing node declaring two joints),
  `FreePosed` (a posing node declaring a `Free`), and `NotRunning` (the
  same controls under no time base). Fixtures whose refusal fires at
  CLASS DEFINITION cannot be module-level classes: build them inside the
  test with a `class` statement under `assertRaises`, as the couplings
  suite already does for its class-definition refusals.
- [ ] 1.6 `tests/running_project/machine.py`: `OmittedControl`, a running
  root with a `Flag` whose `render()` calls `omit()` on the controlled
  part, for design §10.

## 2. Red first — the declaration

Write every case below and SEE IT RED before task 3. Paste the exact red
text of each into `evidence.md`. A case red for the wrong reason (an
import error where a wrong answer was expected) is not evidence: record
the missing-name failure first, then rewrite the case so the eventual red
is a wrong ANSWER.

- [ ] 2.0 The names do not exist yet: `solid_node.simulation.Button`,
  `Turn`, `enumeration.qualified_controls`,
  `enumeration.qualified_declarations`, `Program.controls`,
  `Program.response`, `Program.values_of`, `Program.deltas_of`,
  `Program.published_controls`. Record the `ImportError`/`AttributeError`
  for each in `evidence.md`.
- [ ] 2.1 **A control is declared and discovered.** New
  `tests/test_controls.py`: `Sim(Columns(), 0.1)` constructs; the tree's
  qualified controls are exactly `'units dial'`, `'tens dial'`,
  `'turn units'`, `'turn tens'`; each compiled control names its part
  path, its coordinate, its joint path, its axis and its origin; the
  button entries name `'Add one'`/`'Add ten'`, which are keys of
  `sim.instructions`.
- [ ] 2.2 **A control on a child qualifies through its path.** A root
  holding one assembly that declares both the instruction and the
  control: the control is `column.dial` and its instruction reference is
  `column.Add one`.
- [ ] 2.3 **The nearest posing joint wins.** On `Columns`, the control's
  coordinate is `units.turn` and its joint path is `('units',)`, not the
  root and not the dial. Add a three-deep fixture where an intermediate
  assembly between the part and the joint declares nothing, and assert
  the walk passes through it.
- [ ] 2.4 **Every refusal of the `simulation` delta**, one test each,
  each asserting the MESSAGE carries the facts the spec names: the
  non-mapping `controls`, the non-node part, the part of another class,
  a coordinate passed as a part, an input of another class, the
  undeclared instruction, the unposed part, the non-rotational `Turn`,
  the unreached input (naming the inputs that DO reach), the two-joint
  node, the `Free` node, and the control under a non-running root
  (refused both at `Sim` construction and at publication).
- [ ] 2.5 **A control changes nothing about the run.** `Columns` and a
  twin declaring no controls produce the same bank, the same
  `program.edges`, the same `program.sources` and the same
  `program.identity`; stepping both through the same script gives
  identical trajectories. This is the test that would go red if
  `described()` ever learned about controls.

## 3. The declaration

- [ ] 3.1 `solid_node/simulation/control.py` (new): `Button` and `Turn`,
  each carrying `control_kind` (`'button'`/`'turn'`), the normalized part
  reference, and `check_declared_on(owner, name)` with its own message.
  Normalize a `ChildDeclaration` to `PathRef(value, (), value)` exactly as
  `couplings.coordinate_ref` does, and refuse everything else in the
  constructor, naming what was written.
- [ ] 3.2 `solid_node/node/declarative.py`: `NodeMeta.__new__` validates
  `namespace.get('controls')` right after `super().__new__`, duck-typed
  on `control_kind` — no import from `solid_node/simulation/` — refusing
  a non-mapping table and a non-control entry, calling
  `check_declared_on(cls, name)` on each, and setting
  `cls._declares_controls` from the class's OWN table — `True` iff the
  namespace's `controls` is non-empty, so a subclass that assigns
  `controls = {}` reads `False` and is not refused under a non-running
  root for a table it emptied. Keep the existing relation validation
  and its local-import comment untouched, and mirror its shape.
- [ ] 3.3 `solid_node/simulation/enumeration.py`:
  `qualified_declarations(root)` returning `(instructions, controls)`
  from ONE `drive_tree` walk, with `qualified_instructions` and a new
  `qualified_controls` as thin faces over it. `qualified_instructions`
  keeps its exact present signature and return shape;
  `tests/test_simulation_enumeration.py` must pass unchanged.
- [ ] 3.4 `solid_node/simulation/__init__.py`: `Button` and `Turn` in
  `_EXPORTS`, mapped to `control`, lazily like every other name.
  `tests/test_lazy_test_framework.py` and `tests/test_node_lazy_exports.py`
  are the guards that nothing became eager.
- [ ] 3.5 `solid_node/simulation/sim.py`: one walk for both tables;
  refuse a control under a non-running root at construction, naming the
  declaring class, the control and `Time.running()`.
- [ ] 3.6 Green for 2.1–2.5. Paste the counts.

## 4. Red first — the arithmetic the ratio is measured with

- [ ] 4.1 **`Program.values_of` and `Program.deltas_of` are the run's
  own.** Write the case that `Run._values(bank)` and
  `Run._deltas(admissions)` return exactly what the new `Program`
  methods do, on `Train`, `Carry` and `Columns`, at the rest bank and at
  a mid-move bank. See it red (the names do not exist), then move the
  two methods to `Program` and make `Run` delegate. `Run._pass` STAYS on
  `Run`: it owns conflict detection and the messages a failed tick
  needs.
- [ ] 4.2 **`Program.response` reproduces the run.** Red first: for each
  of `Columns`, `Carry`, `CarryLead` and `Ranged`, and for each declared
  input, `program.response(rest_bank, input_id, eps)` equals, bit for
  bit, the bank difference a fresh `Sim` shows after
  `move(input_id, by=eps, duration=0)` — with `eps` both positive and
  negative. This is the test that keeps the measurement and the tick in
  step now that they are two call sites.
- [ ] 4.3 **The corpus still replays.** `python -m pytest
  tests/test_running_corpus.py -q` green after the move, and the cost
  probe of 0.3 re-run with its output pasted beside the base number.

## 5. Red first — compiling a control

- [ ] 5.1 **The compiled control.** `compile_program` gains the controls
  and the instructions it must check against; `Program.controls` is the
  ordered tuple of compiled records, each carrying kind, qualified name,
  part path, joint path, coordinate id, axis, origin and the reference
  its kind needs. Red first on `Columns`: assert every field, including
  that `tens dial`'s coordinate is `tens.turn` and that `turn tens`'s
  input is `tens_entry` although `units_entry` also reaches it.
- [ ] 5.2 **`origin` on an off-centre joint.** On `OffCentre`, `origin`
  is `[0, 3, 0]` and `axis` is `[1, 0, 0]`; on `Columns` both dials read
  `origin == [0, 0, 0]`. Assert against `joint.axes(node)` and
  `joint.carried_points(...)` rather than against the published
  operations, so the entry cannot drift from the placement.
- [ ] 5.3 **A site-declared joint carries.** A fixture whose joint is
  declared at the SITE rather than on the class: `axis` and `origin` are
  the CARRIED values `place` used, not the ones the site wrote. Red
  first, because this is the case a naive implementation gets wrong.
- [ ] 5.4 **The identity is untouched.** `Program.described()` is
  unchanged: assert the digest of `Columns` equals the digest of its
  control-free twin, and that no line of `described()` mentions a
  control. 2.5's assertion, restated where the compiler is edited.
- [ ] 5.5 `solid_node/simulation/run.py`: `Run.__init__` hands
  `sim.controls` and `sim.instructions` to `compile_program`. Green for
  5.1–5.4.

## 6. Red first — the ratio

- [ ] 6.1 **`per_unit` is the measured ratio.** Red first: on `Columns`,
  `turn units` reads exactly `-36.0` and `turn tens` exactly `36.0`;
  assert the EXACT float, not an `assertAlmostEqual`, so the
  power-of-two displacement of design §6 is pinned by the test.
- [ ] 6.2 **An integer input measures over one native unit.** A fixture
  with `Driver(default=0, dtype=int, scale=0.0125, unit='mm')` driving a
  revolute: the measurement displaces by one native unit rather than by
  `2**-20`, and `per_unit` is the ratio in design units. Red first, with
  the naive displacement showing zero.
- [ ] 6.3 **Zero is refused.** A `Turn` whose input reaches the
  coordinate only through a law that is disengaged at rest: publication
  is refused naming the part, the input and the coordinate. Build it
  from `carried_column`'s own shape, where `units_entry`'s partial in
  `tens.turn` is zero at rest — a fact 0.6(c)'s probe already shows.
- [ ] 6.4 **A two-sided disagreement is refused.** A `Turn` over a law
  with a kink exactly at the rest value (`abs`, or `clamp01` at its
  boundary): the forward and backward readings differ beyond the stated
  window and publication is refused naming both readings. Assert that a
  SMOOTH non-affine law (`sin`) is ADMITTED at the same window, so the
  test pins the choice of `1e-3` over the program's `1e-9` agreement.
- [ ] 6.5 `Program.published_controls(initial)` implementing 6.1–6.4.
  Green.

## 7. Red first — the document

- [ ] 7.1 **The table is published.** In
  `tests/test_running_document.py`, a `ControlsTableTest` red first: the
  built and the exported document of `Columns` each carry a `controls`
  object with the four keys, each entry's fields in the spec's order,
  `instruction` a key of the same document's `instructions` table and
  `input` a key of its `drivers` table, `coordinate` a key of
  `program.coordinates`, and `part`/`joint` node-name paths that
  RESOLVE by walking the document's own `root` tree. **This is the task
  that publishes the table for the Pascaline module's own tree shape**:
  `Columns` is that shape, and the walk-the-tree assertion is what
  proves the path a viewer will follow.
- [ ] 7.2 **Absent when empty, and byte-identical.** `Train`,
  `LoopingTrain`, `TrainBody` and the four other `ByteIdentityTest`
  trees publish no `controls` key, and every one of them — the running
  `running_train.json` captured in 0.4 included — is byte-identical to
  its base capture. Add `running_train` to `ByteIdentityTest.trees`.
- [ ] 7.3 **The version does not move.** `Columns` declares
  `version: 5`; nothing anywhere declares 6; an untimed root carrying a
  `controls` table is refused rather than published (7.5's other half).
- [ ] 7.4 **Republishing is byte-identical**, key order and field order
  included, and the `bindings` table of `Columns` is the same whether or
  not the controls are declared — the proof that no control expression
  enters the binding pass.
- [ ] 7.5 **An omitted part drops its control.** On `OmittedControl`
  built with the flag off: the document's tree has no such node, the
  `controls` table has no entry for it, the other entries are unchanged,
  and the build succeeds. With the flag on, the entry is present.
- [ ] 7.6 **A baked capture publishes none.**
  `tests/test_browser_renderer.py` (or the web-snapshot fixture beside
  it): capturing `Columns` produces a document with no `controls` key,
  otherwise unchanged.
- [ ] 7.7 `solid_node/core/serializer.py`: `document_body` gains a
  `controls` argument and writes the key only when it is non-empty,
  immediately after `instructions` and before `bindings`;
  `symbolic_document`'s `collect` refuses a class carrying
  `_declares_controls` when the walk is not running.
  `solid_node/core/builder.py` and `solid_node/core/export.py` pass the
  table; `solid_node/viewers/browser.py` passes none. Green for 7.1–7.6.

## 8. The things that must not move

- [ ] 8.1 `python -m pytest tests/test_running_document.py
  tests/test_running_simulation.py tests/test_running_jumps.py
  tests/test_running_stops.py tests/test_export.py
  tests/test_build_publication.py tests/test_couplings.py
  tests/test_joints.py tests/test_declarative_nodes.py -q` green. Paste
  counts.
- [ ] 8.2 `python -m pytest tests/test_cli_lazy_imports.py
  tests/test_node_lazy_exports.py tests/test_lazy_test_framework.py -q`
  green: a model that declares no running time still loads none of the
  simulation layer, and the node layer still imports nothing from it.
  Add the direct assertion that `solid_node.node.declarative` names no
  `solid_node.simulation` import.
- [ ] 8.3 **Regenerate the corpus and prove `identity` is unchanged.**
  `PYTHONPATH="$PWD" python tools/generate_running_corpus.py` writes
  `tests/running-corpus.json`; `git diff --stat` on it must be EMPTY and
  its sha256 must equal 0.5's. Paste both. Then
  `python -m pytest tests/test_running_corpus.py -q` green. No corpus
  machine gains a control and the coverage guard is not touched.
- [ ] 8.4 Full suite (`python -m pytest -x -q`), counts pasted beside
  0.2's, every difference accounted for by a test this cycle added or
  rewrote.

## 9. Documentation and the record

- [ ] 9.1 `docs/driving.rst`: a "Controls: pressing and turning the part
  itself" section immediately after "Instructions", stating both
  spellings, that the part is named the way a relation's path ends are,
  that the ratio is derived and measured at rest, and that a control is
  refused where it cannot be resolved. Say plainly that the viewer
  behaviour is the viewer's own release.
- [ ] 9.2 `docs/scenarios.rst`: one cross-reference from the running
  section. `docs/api-reference.rst`: `Button` and `Turn` beside
  `Instruction`. `docs/changelog.rst`: the entry.
  `docs/architecture.md`: one sentence each in the Simulation and Export
  sections.
- [ ] 9.3 `python -m pytest tests/test_docs_exports.py -q` green, and
  the docs build if the suite does not already cover it.
- [ ] 9.4 `evidence.md` complete: the base and final suite counts, the
  base and final corpus digests, every red text, the probes of 0.6, the
  grep of 0.7, and the cost probe before and after task 4.
- [ ] 9.5 Update `workflow/docs/controls-on-parts.md` to point at this
  change for the framework half and to record the three deviations
  (design §8 `origin`, §9 the capture, §10 the omitted part), so the
  plan note does not read as the ratified record.
- [ ] 9.6 Report to the reviewer, do NOT commit, and do NOT extract the
  ADR: ADR-112 is written after implementation, under the pilot's
  direction, from design.md's last section.
