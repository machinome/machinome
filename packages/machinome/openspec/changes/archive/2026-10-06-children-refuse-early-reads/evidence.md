# Evidence — `children-refuse-early-reads`

Cycle 3 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`52062bbc03e871ef89eab488a491e16472a61730` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`, and so did every probe and project run
(each records `machinome.__file__` in its output). Every project command
ran as `env -C <project> PYTHONPATH=<bench>:<project>
/home/asa/devel/machinome/.venv/bin/<tool> ...`, with `<Albert>` =
`projects/Robots/AlbertPro` (branch `frames-and-mates`, `2c34ebf`, clean
tree) and `<Clocks>` = `projects/3DPrintedClocks` (branch
`solid-node-simulation`, `ec2a05d`, ` M screenshots/wall_clock_03.png`
pre-existing and not ours). `<scratch>` is the campaign scratchpad's
`cycle3/` directory; this cycle's outputs are in its `apply-baseline/`,
`apply-after/` and `apply-branch/` subdirectories (Stage P's are at its
top level and were left in place). Tools: `flake8` 7.3.0 (the pyenv shim;
the venv has none), `black` 26.5.1, `openspec` 1.6.0. One test run of ours
at a time throughout.

## 1. Baseline on the unmodified tree (52062bb)

### 1.2 Focused tests

`pytest -q -p no:cacheprovider tests/test_declarative_render.py
tests/test_animator_tag.py tests/test_node_naming.py
tests/test_traversal_naming.py`:

```
43 passed, 3 warnings, 10 subtests passed in 1.73s   (wall 2.16 s)
```

### 1.3 The probes

`env -C <scratch>/repro_project PYTHONPATH=<bench>:<scratch> .venv/bin/python
repro.py` (exit 0; the build's INFO lines omitted):

```
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
children loop, first enumeration: simulate saw 0 children; near rotations [] ; far rotations []
addressed loop, first enumeration: near rotations [['r', '30.0', [1, 0, 0]]] ; far rotations [['r', '30.0', [1, 0, 0]]]
children loop, second enumeration before assemble(): simulate saw 0 children; near rotations []
children loop, enumeration after assemble(): simulate saw 2 children; near rotations [['r', '60.0', [1, 0, 0]]]
```

design.md's Context table: 0, 0, then 2 children seen; no rotation until
after `assemble()`; nothing raised.

`env -C <Clocks> PYTHONPATH=<bench>:<Clocks> .venv/bin/python
<scratch>/probe_children.py <scratch>/apply-baseline
simulation.wall_clock_40.clock:WallClock40` followed by clocks 12, 17, 25,
28, 32, 36, 37 and 39 in one process (wall 143.97 s), then
`summarize.py <scratch>/apply-baseline`. The summary is identical to Stage
P's (`summarize.py <scratch>` over its outputs, `diff` with the per-clock
seconds masked: no difference). Every read is in a `render()` phase, on the
first pass, and sees 0 children:

```
== simulation.wall_clock_12.clock:WallClock12 2.3 s
   {'site': '3DPrintedClocks/simulation/wall_clock_12/clock.py:104', 'phase': 'render', 'own_phase': False, 'second_pass': False, 'reads': 1, 'seen': [0], 'intended': 'DIAL_DETAIL', 'children_after': 60, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_17.clock:WallClock17 2.5 s
== simulation.wall_clock_25.clock:WallClock25 13.3 s
   {'site': '.../wall_clock_25/clock.py:121', 'phase': 'render', 'own_phase': True, ..., 'seen': [0], 'intended': None, 'children_after': 4, 'reach': 4, 'class_level': 4}
   {'site': '.../wall_clock_25/clock.py:135', ..., 'seen': [0], 'intended': 'DIAL_SUPPORTS', 'children_after': 4, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_25/clock.py:291', ..., 'seen': [0], 'intended': 'KEY', 'children_after': 2, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_25/clock.py:282', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_28.clock:WallClock28 9.2 s
   {'site': '.../wall_clock_28/clock.py:242', ..., 'seen': [0], 'intended': 'KEY', 'children_after': 1, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_28/clock.py:232', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_32.clock:WallClock32 7.8 s
   {'site': '.../wall_clock_32/clock.py:120', ..., 'seen': [0], 'intended': 'DIAL_SUPPORTS', 'children_after': 4, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_36.clock:WallClock36 4.6 s
   {'site': '.../wall_clock_36/clock.py:81', ..., 'seen': [0], 'intended': 'STANDOFFS', 'children_after': 2, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_36/clock.py:234', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_37.clock:WallClock37 9.6 s
   {'site': '.../wall_clock_37/clock.py:115', ..., 'seen': [0], 'intended': 'DIAL_SUPPORTS', 'children_after': 4, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_37/clock.py:276', ..., 'seen': [0], 'intended': 'KEY', 'children_after': 2, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_37/clock.py:267', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_39.clock:WallClock39 10.8 s
   {'site': '.../wall_clock_39/clock.py:232', ..., 'seen': [0], 'intended': 'KEY', 'children_after': 2, 'reach': 0, 'class_level': 0}
   {'site': '.../wall_clock_39/clock.py:224', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 0, 'class_level': 0}
== simulation.wall_clock_40.clock:WallClock40 3.2 s
   {'site': '.../wall_clock_40/clock.py:99', ..., 'seen': [0], 'intended': 'DIAL_SUPPORTS', 'children_after': 4, 'reach': 4, 'class_level': 4}
   {'site': '.../wall_clock_40/clock.py:281', ..., 'seen': [0], 'intended': 'KEY', 'children_after': 2, 'reach': 2, 'class_level': 2}
   {'site': '.../wall_clock_40/clock.py:272', ..., 'seen': [0], 'intended': 'PULLEY', 'children_after': 3, 'reach': 3, 'class_level': 3}
```

(The `reach 4` of clock 25's line 121 is the probe's artefact: its colour
is named in `render()`, two lines below the `parts` property the read is
in, so `intended` is `None` and the probe compares `None` with `None`. The
serialized document below shows those four parts uncoloured.)

`probe_document.py <scratch>/apply-baseline/document-wall_clock_25.json
simulation.wall_clock_25.clock:WallClock25`, and the same for clock 40
(both exit 0; `parts` lists byte-identical to Stage P's):

| Parts | Clock 25 | Clock 40 |
|---|---|---|
| `standoffs/*` (6) | `#b08d2d` | `#4a4d50` |
| `raised_detail/detail_0..3` | `None` | `#111111` |
| `dial/supports/support_0..3` | `None` | `#4a4d50` |
| `winding_knob/{body,handle}` | `None` | `#9be300` |
| `movement/pulley/{wheel,holder_back,holder_front}` | `None` | `#9be300` |
| `dial/numerals/piece-0..59` | `None` | `None` |

### 1.4 The originating project, unmodified bench

- `env -C <Albert> ... machinome test --mesh simulation/albert.py` (exit 0):
  `Ran 35 tests in 10.93 seconds: 35 passed, 0 failed (mesh engine, volume
  epsilon 0 mm³)`, wall 13.76 s.
- `env -C <Albert> ... python -m pytest -q -p no:cacheprovider
  simulation/test_frames.py`: `12 passed in 3.42s`, wall 4.55 s.
- `git -C <Albert> status --short`: empty before and after.
  `git -C <Clocks> status --short`: ` M screenshots/wall_clock_03.png`
  before and after.

## 2. Red tests, on the unmodified source (52062bb)

New file `tests/test_children_reads.py` (a `BaseNodeTest`; fixtures in the
module, `tests.meta_project.parts.Cube` as the part,
`machinome.simulation.Driver` for the knee). `pytest -q -p no:cacheprovider
-rA tests/test_children_reads.py`:

```
5 failed, 6 passed in 1.09s   (wall 1.54 s)
```

| Test | Task | Before the change |
|---|---|---|
| `SimulatePhaseReadTest.test_set_state_refuses_the_read` | 2.1 | RED: `AssertionError: StructureError not raised` |
| `SimulatePhaseReadTest.test_render_refuses_the_read` | 2.1 | RED: `AssertionError: StructureError not raised` |
| `SimulatePhaseReadTest.test_assemble_refuses_the_read` | 2.1 | RED: `AssertionError: StructureError not raised` |
| `RenderPhaseReadTest.test_own_children_in_render_are_refused` | 2.2 | RED: `AssertionError: StructureError not raised` |
| `RenderPhaseReadTest.test_a_childs_children_in_render_are_refused` | 2.3 | RED: `AssertionError: StructureError not raised` |
| `AddressedLoopTest.test_the_declared_attributes_rotate` | 2.4 | green |
| `UnchangedReadsTest.test_outside_any_phase_before_linking_is_empty` | 2.5 (a) | green |
| `UnchangedReadsTest.test_after_assemble_lists_the_linked_children` | 2.5 (b) | green |
| `UnchangedReadsTest.test_a_later_phase_reads_the_linked_children` | 2.5 (c) | green |
| `UnchangedReadsTest.test_a_leaf_inside_a_phase_is_empty` | 2.5 (d) | green |
| `UnchangedReadsTest.test_brep_before_linking_keeps_its_refusal` | 2.5 (e) | green |

Two details differ from the letter of tasks §2 and are recorded here: 2.5
(b) binds the knee (`set_state(knee=30.0)`) before `assemble()`, because
the first run without it failed on the unmodified tree with
`AttributeError: driver 'knee' of AddressedLowerLeg is not bound; bind it
with set_state(knee=...)` (the addressed loop reads the driver); and the
flags of 2.5 (c) and the records of (c) and (d) are kept in the instance
dictionary (`node.__dict__['_peek']`, `'_seen'`), which the node's naming
pass skips, rather than as plain attributes.

## 3. The change

`machinome/node/internal.py`: `from . import phase as _phase`; a module
function `_early_read(node, phase)` building the `StructureError` of
design.md, Decision 3; `InternalNode.children`, a property answering the
instance dictionary's `children` when assigned, `()` outside any phase,
and raising `_early_read(self, current)` inside one, with a setter storing
into the instance dictionary as before. `AbstractBaseNode.children =
tuple()` is unchanged; `present()`, `materialize()` and `model.py`'s
assignment are unchanged.

### 3.2 Green

`pytest -q -p no:cacheprovider -rA tests/test_children_reads.py`:

```
11 passed in 1.12s   (wall 1.56 s)
```

1.2's files: `43 passed, 3 warnings, 10 subtests passed in 1.82s` (wall
2.33 s), as before.

### 3.3 The reproduction

`repro.py` without `--refuse` now stops at its first step:

```
  File ".../cycle3/repro_project/repro.py", line 33, in simulate
    SEEN.append(len(self.children))
                    ^^^^^^^^^^^^^
  File "/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/node/internal.py", line 159, in children
    raise _early_read(self, current)
machinome.node.declarative.StructureError: LowerLeg 'LowerLeg' read self.children in simulate(): the framework links an assembly's children after the tree's render() and simulate() have run, so here the list is not there yet and a loop over it does nothing. Address the children by the attributes that declare them: self.near, self.far.
```

## 4. Validation in the projects

### 4.1 AlbertPro, after the change

- `machinome test --mesh simulation/albert.py` (exit 0): `Ran 35 tests in
  10.90 seconds: 35 passed, 0 failed (mesh engine, volume epsilon 0 mm³)`,
  wall 13.82 s.
- `python -m pytest -q -p no:cacheprovider simulation/test_frames.py`:
  `12 passed in 3.42s`, wall 4.38 s.
- `git -C <Albert> status --short`: empty. Counts equal to §1.4.

### 4.2 The clocks on the unchanged project checkout, after the change

`probe_document.py <scratch>/apply-after/document-wall_clock_NN.json
simulation.wall_clock_NN.clock:WallClockNN` in `<Clocks>`, for each clock.
Clock 17 serializes (exit 0) and its watched parts are those Stage P
recorded (`movement/pulley/{wheel,holder_back,holder_front}`, `None`;
`parts` identical to Stage P's `document-probe-17.json`). Each of the
other eight exits 1 at load, refused inside `render()`, as design.md's
Open Question 1 expects of the unchanged project; this is the expected
outcome, not a regression. Each message's site and first line:

| Clock | Site | Message |
|---|---|---|
| 12 | `clock.py:104` in `render` | `Dial 'dial' read numerals.children in render(): ... DialDetail declares no children: they are the list its own render() returns, and it is there that they are addressed.` |
| 25 | `clock.py:121` in `parts` | `RaisedDetail 'raised_detail' read self.children in render(): ... self.detail_0, self.detail_1, self.detail_2, self.detail_3.` |
| 28 | `clock.py:242` in `render` | `WindingKey 'winding_knob' read self.children in render(): ... self.body.` |
| 32 | `clock.py:120` in `render` | `DialSupports 'supports' read self.children in render(): ... self.support_0, self.support_1, self.support_2, self.support_3.` |
| 36 | `clock.py:81` in `render` | `Standoffs 'standoffs' read self.children in render(): ... self.top, self.bottom.` |
| 37 | `clock.py:115` in `render` | `DialSupports 'supports' read self.children in render(): ... self.support_0, self.support_1, self.support_2, self.support_3.` |
| 39 | `clock.py:232` in `render` | `WindingKey 'winding_knob' read self.children in render(): ... self.body, self.handle.` |
| 40 | `clock.py:99` in `render` | `DialSupports 'supports' read self.children in render(): ... self.support_0, self.support_1, self.support_2, self.support_3.` |

(`...` stands for the fixed middle sentence shown in §3.3.) `git -C
<Clocks> status --short`: ` M screenshots/wall_clock_03.png`, unchanged.

### 4.3 The companion change in 3DPrintedClocks

**Partly done: three of the eight clocks.** Direct project work in
`projects/3DPrintedClocks`, as design.md's Open Question 1 was answered.
`git -C <Clocks> worktree add WTs/children-reads -b children-reads` from
`ec2a05d` on `solid-node-simulation` (output: `Preparing worktree (new
branch 'children-reads')`, `HEAD is now at ec2a05d`). Worktree
`projects/3DPrintedClocks/WTs/children-reads`, branch `children-reads`;
`git -C <worktree> rev-parse --show-toplevel` names the project's
worktree. The project's `.gitignore` does not ignore `WTs/`, so its main
checkout's `git status --short` now also lists `?? WTs/` beside the
pre-existing ` M screenshots/wall_clock_03.png`; nothing else in that
checkout changed and its HEAD is still `ec2a05d`.

Rewritten, with the Edit tool, inside the worktree:

- clock 12 (`clock.py`): `DialDetail.render()` sets
  `colours.DIAL_DETAIL` on each island as it builds them, and
  `Dial.render()` no longer loops over `self.numerals.children`;
- clock 25: `RaisedDetail.parts` returns `[self.detail_0, ...,
  self.detail_3]`; `DialSupports`, `Pulley` and `WindingKey` loop over
  `[self.support_0, ..., self.support_3]`, `[self.wheel,
  self.holder_back, self.holder_front]` and `[self.body, self.handle]`;
- clock 28: `Pulley` loops over `[self.wheel, self.holder_back,
  self.holder_front]`; `WindingKey`, which declares only `body`, sets
  `self.body.color`.

**Not rewritten: clocks 32, 36, 37, 39 and 40.** The first Edit of clock
32's `clock.py` (in one batch with three of clock 36's) and a second,
lone Edit of clock 32 were each refused by the harness with: `Permission
for this tool use was denied. The tool use was rejected (eg. if it was a
file edit, the new_string was NOT written to the file). Try a different
approach or report the limitation to complete your task.` On the
orchestrator's instruction those edits were not tried another way, and
the five clocks were left as they are. For clock 40 the intended choice
was to make the three dead loops equivalent (address the attributes),
which leaves its document unchanged since the class-level colours are
the same values; it is not made. Clock 36's unreached `WindingKey` read
(`clock.py:243`) is in the same state.

Against the bench, from the worktree, `probe_document.py
<scratch>/apply-branch/document-wall_clock_NN.json
simulation.wall_clock_NN.clock:WallClockNN` serializes each of the three
(exit 0, no refusal), and the parts the loops meant now carry their
colours (each value is the clock's `colours.py` constant the loop names):

| Clock | Parts | Colour |
|---|---|---|
| 12 | `dial/numerals/island-*` (60) | `#ffc0cb` (`DIAL_DETAIL`) |
| 25 | `raised_detail/detail_0..3` | `#b08d2d` (`FRAME_DETAIL`) |
| 25 | `dial/supports/support_0..3` | `#b08d2d` (`DIAL_SUPPORTS`) |
| 25 | `movement/pulley/{wheel,holder_back,holder_front}` | `#b08d2d` (`PULLEY`) |
| 25 | `winding_knob/{body,handle}` | `#003b73` (`KEY`) |
| 28 | `movement/pulley/{wheel,holder_back,holder_front}` | `#d4af37` (`PULLEY`) |
| 28 | `winding_knob/body` | `#d4af37` (`KEY`) |

That is 77 of the 100 parts the refusal left uncoloured. Clock 12's other
watched parts are unchanged (its `movement/pulley` and `winding_knob` were
already coloured through attributes; `dial/supports`, set on the assembly,
stays `None` as before).

Each clock's documented test command (`simulation/README.md`: `machinome
test wall_clock_NN --mesh --volume-epsilon 0.001 --set facing=0`), run once
on the project's checkout (`solid-node-simulation`, `ec2a05d`) and once on
the branch, one at a time. The checkout's run is refused at load by this
change, so it ran with the pre-change behaviour of `children` restored
from outside (`<scratch>/prechange.py`, in the appendix: `env -C <Clocks>
PYTHONPATH=<bench>:<Clocks>:<scratch> .venv/bin/python
<scratch>/prechange.py test wall_clock_NN ...`); the branch's ran against
the changed bench as is (`env -C <worktree> PYTHONPATH=<bench>:<worktree>
.venv/bin/machinome test wall_clock_NN ...`). Both exit 1 for each clock,
on the same tests, with the same verdict for every test (`diff` of the
`Running ...` lines: none):

| Clock | `solid-node-simulation`, pre-change behaviour | `children-reads`, this change |
|---|---|---|
| 28 | 26 tests: 20 passed, 6 failed, 69.64 s (wall 73.16 s) | 26 tests: 20 passed, 6 failed, 69.07 s (wall 72.55 s) |
| 25 | 24 tests: 18 passed, 6 failed, 141.19 s (wall 144.68 s) | 24 tests: 18 passed, 6 failed, 141.30 s (wall 144.64 s) |
| 12 | 24 tests: 16 passed, 8 failed, 179.43 s (wall 182.93 s) | 24 tests: 16 passed, 8 failed, 180.09 s (wall 183.68 s) |

The failures are the clocks' own and the same on both sides:
`test_assembly_integrity`, `test_movement_runs_free_through_a_swing`,
`test_solid_integrity`, `test_source_body_inventory` and
`test_the_train_runs_free_over_twelve_hours` in all three;
`test_the_weight_hangs_clear_below_the_rigid_structure` (28, 12) or
`..._below_the_complete_rigid_structure` (25); and in clock 12
`test_the_key_goes_onto_the_barrel_arbor_one_way` and
`test_the_powered_wheel_turns_once_in_its_time` (`simulation/README.md`
records the clocks as not mechanically certified).

`machinome snapshot wall_clock_25 --renderer web --time 0 --imgsize
1280x960 --autocenter --viewall -o <scratch>/apply-branch/wall_clock_25.png`
from the worktree against the bench (exit 0, wall 31.54 s), looked at: the
pulley under the movement and the raised detail on the frame are brass
(`#b08d2d`), and the parked winding key beside the clock is navy
(`#003b73`), where the published `viewer.json` gave them no colour. No
"before" snapshot was taken: a snapshot's build runs in a fresh
interpreter, which the outside restore does not reach.

Committed on the branch, in the project repository only, in one attempt
(`git -C <worktree> add` of the three files, then `git -C <worktree>
commit`, exit 0): **`58ff90e5a8b4e274ef90147d87a6d937b5e7411b`**,
"Colour loops address the declared parts: wall clocks 12, 25, 28", whose
body says that clocks 32, 36, 37, 39 and 40 are not rewritten and refuse
to load until they are, and ends with the trailer `Co-Authored-By: Claude
Opus 5.5 (1M context) <noreply@anthropic.com>` (the model that made it,
in place of the one tasks §4.3 named). Nothing merged; the worktree is
left in place; the project's checkout is still on `solid-node-simulation`
at `ec2a05d`.

## 5. Manual and changelog

- `docs/concepts/rest-and-motion.rst`: after the `simulate()` paragraph,
  before the code block, the two sentences of design.md, Decision 6.
- `docs/architecture.md`: one sentence in the declarative-internal-node
  paragraph, after the one ending "raises on a later render whose set
  differs."
- `docs/project/changelog.rst`: one bullet under the existing `Unreleased`
  section, ending `(children-refuse-early-reads)`.
- 5.4: `grep -rn "\.children" docs` (outside `docs/adrs/`) finds only
  `docs/architecture.md`'s test-runner paragraph ("Only `node.children` are
  checkpointed and re-placed this way"), which is about a test's
  checkpoints, not a read in `render()` or `simulate()`; the `children`
  lines mentioning `render()` or `simulate()` (`rest-and-motion.rst:93`,
  `howto/fusion.rst:21`, `project/upgrading.rst:338`) tell no reader to
  read `children` there.

## 6. Checks

### 6.1 Lint

`flake8 --max-line-length=89 machinome/node/internal.py
tests/test_children_reads.py`: no finding (exit 0); `HEAD`'s
`internal.py` (`git show HEAD:machinome/node/internal.py`, into the
scratchpad): no finding either. `black --check` on the same two files
reports both would be reformatted, as it does for `HEAD`'s `internal.py`
and for every test file the campaign's earlier cycles added
(`test_clocked_bounds.py`, `test_couplings.py`, `test_joints.py`,
`test_mates.py`, `test_retained_builder_generation.py`); `black --check
machinome tests` reports 516 files would be reformatted on the bench. The
repository is not black-formatted and the CI step is `continue-on-error`;
the new code follows the surrounding style.

### 6.2 Full suite

`pytest -q -p no:cacheprovider` at the bench root, alone, after the
archive (exit 0):

```
4634 passed, 4 skipped, 55 warnings, 6619 subtests passed in 654.42s (0:10:54)   (wall 656.97 s)
```

Stage P's run of the unmodified bench with the refusal installed from
outside counted 4623 passed, 4 skipped, 6611 subtests; the eleven new
tests account for the passed count. The eight further subtests were not
traced to a test; every subtest passed. No framework read inside a phase
was refused, as the outside probe had found.

## 7. Warts

- 7.1: the AlbertPro entry moved verbatim from `workflow/warts.md` to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under
  `children-refuse-early-reads`, with a "What shipped" paragraph; the
  standing triage's "Planned, never done" bullet naming this cycle
  deleted.
- 7.2: `workflow/warts.md`, new section "Findings from the framework cycle
  `children-refuse-early-reads` (2026-10-06)": the eight clocks (the
  companion change has not landed: its branch is unmerged and five of the
  eight are not rewritten) and Open Question 2. Each **Recorded.**
- `workflow/ongoing/fix-warts-3.md`: a Progress line for this cycle beside
  the orchestrator's "Deferred to the pilot" entry, which is kept.

## 8. Sync and archive

- 8.1: the delta's one ADDED requirement, "An internal node's children
  are refused before they are linked", with its four scenarios, copied
  into `openspec/specs/node-model/spec.md` after "Tree naming from parent
  attributes"; no existing requirement edited. `openspec validate
  node-model`: valid.
- `openspec validate children-refuse-early-reads` before archiving: valid.
- `openspec archive children-refuse-early-reads --yes --skip-specs` (the
  specs were synced by hand in 8.1, so the CLI's own sync, which would add
  the requirement a second time, was skipped): archived as
  `openspec/changes/archive/2026-10-06-children-refuse-early-reads/`. Its
  warnings: the Why section's length, and 26 of 27 tasks complete (4.3,
  left unticked with its note).
- `openspec validate --specs`: `Totals: 45 passed, 0 failed (45 items)`.
- 8.3: `pytest -q -p no:cacheprovider tests/test_children_reads.py
  tests/test_declarative_render.py tests/test_animator_tag.py
  tests/test_node_naming.py tests/test_traversal_naming.py`: `54 passed, 3
  warnings, 10 subtests passed in 1.86s` (wall 2.36 s); 11 + 43, as in §3.2.
- Nothing committed on the bench.

## Appendix: the probes' sources

The scratchpad is not durable; these are the sources of every probe this
cycle ran, as they stood.

### `repro_project/pyproject.toml`

```toml
[project]
name = "children-repro"
version = "0"

[tool.machinome]
model = "leg:LowerLeg"
```

### `repro_project/repro.py`

```python
"""Reproduce AlbertPro's finding on the bench: a declared child rotated
through `self.children` in `simulate()` is never rotated, and nothing
raises; the same loop over the declared attributes rotates it.

Then show the read's answer depends on whether something has already
assembled the node: after `assemble()`, a later enumeration sees the
children.
"""

import sys

BENCH = '/home/asa/devel/machinome/machinome/WTs/fix-warts-3'
sys.path.insert(0, BENCH)

import machinome  # noqa: E402
from machinome.node.assembly import AssemblyNode  # noqa: E402
from machinome.simulation import Driver  # noqa: E402
from tests.meta_project.parts import Cube  # noqa: E402

if len(sys.argv) > 1 and sys.argv[1] == '--refuse':
    import refuse_probe  # noqa: F401,E402  the proposed refusal, from outside

AXIS = [1, 0, 0]
SEEN = []


class LowerLeg(AssemblyNode):
    knee = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')
    near = Cube()
    far = Cube()

    def simulate(self):
        SEEN.append(len(self.children))
        for piece in self.children:
            piece.rotate(self.knee, AXIS)


class AddressedLowerLeg(AssemblyNode):
    knee = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')
    near = Cube()
    far = Cube()

    def simulate(self):
        for piece in (self.near, self.far):
            piece.rotate(self.knee, AXIS)


def rotations(node):
    return [op.serialized for op in node.operations if op.serialized[0] == 'r']


print('machinome from', machinome.__file__)

leg = LowerLeg()
leg.set_state(knee=30.0)
print('children loop, first enumeration: simulate saw', SEEN[-1],
      'children; near rotations', rotations(leg.near),
      '; far rotations', rotations(leg.far))

addressed = AddressedLowerLeg()
addressed.set_state(knee=30.0)
print('addressed loop, first enumeration: near rotations',
      rotations(addressed.near), '; far rotations', rotations(addressed.far))

leg.set_state(knee=45.0)
print('children loop, second enumeration before assemble(): simulate saw',
      SEEN[-1], 'children; near rotations', rotations(leg.near))

leg.assemble()
leg.set_state(knee=60.0)
print('children loop, enumeration after assemble(): simulate saw',
      SEEN[-1], 'children; near rotations', rotations(leg.near))
```

### `probe_children.py`

```python
"""Measure what `self.children` reads during the lifecycle of a model.

Replaces AbstractBaseNode.children by a logging data descriptor (getter
returns exactly what the plain attribute would: the instance's assigned
value or the class's empty tuple), runs one enumeration of the root
(`root.render()`), and reports every read made from project code, and
every read made from anywhere while a lifecycle phase is running.

Usage: probe_children.py OUTDIR module:Class [module:Class ...]
"""

import collections
import importlib
import json
import re
import sys
import time

import machinome
from machinome.node import base, phase

PROJECTS = ('/mnt/data/machinome-projects/',
            '/home/asa/devel/machinome/projects/')
LOG = []


def _get(self):
    value = self.__dict__.get('children', ())
    current = phase.current()
    frame = sys._getframe(1)
    filename = frame.f_code.co_filename
    if filename.startswith(PROJECTS) or current is not None:
        LOG.append(dict(
            node=self, cls=type(self).__name__,
            phase=current.kind if current else None,
            phase_owner=type(current.assembly).__name__ if current else None,
            own_phase=current is not None and current.assembly is self,
            seen=len(value), file=filename, line=frame.f_lineno))
    return value


def _set(self, value):
    self.__dict__['children'] = value


base.AbstractBaseNode.children = property(_get, _set)


def intended(file, line):
    with open(file) as fh:
        lines = fh.read().splitlines()
    for text in lines[line - 1:line + 2]:
        found = re.search(r'colours\.(\w+)', text)
        if found:
            return found.group(1)
    return None


def leaves_below(node):
    rest = node.__dict__.get('_rest')
    if rest is None:
        return [node]
    return list(rest)


def probe(target):
    module_name, class_name = target.split(':')
    module = importlib.import_module(module_name)
    root = getattr(module, class_name)()
    del LOG[:]
    started = time.monotonic()
    # The loader's default binding: every driver at its declared
    # default, the rest-only walk, then one enumeration of the root.
    from machinome.simulation.enumeration import qualified_drivers
    qualified_drivers(root)
    elapsed = time.monotonic() - started
    # A second enumeration, as a test's set_state or a second tick would
    # run it, to see whether a later read differs from the first.
    first = len(LOG)
    root.render()
    for entry in LOG[first:]:
        entry['second_pass'] = True
    sites = collections.OrderedDict()
    for entry in LOG:
        key = (entry['file'], entry['line'], entry['phase'],
               entry['own_phase'], entry.get('second_pass', False))
        sites.setdefault(key, []).append(entry)
    report = []
    for (file, line, kind, own, second), entries in sites.items():
        row = dict(site=f'{file.replace(PROJECTS[1], "")}:{line}',
                   phase=kind, own_phase=own, second_pass=second,
                   reads=len(entries),
                   seen=sorted({e['seen'] for e in entries}))
        if file.startswith(PROJECTS):
            colour_name = intended(file, line)
            colour_module = sys.modules[module_name.rsplit('.', 1)[0]
                                        + '.colours']
            target_colour = (getattr(colour_module, colour_name, None)
                             if colour_name else None)
            reached = []
            for entry in entries:
                owner = entry['node']
                linked = owner.__dict__.get('_rest') or ()
                for child in linked:
                    reached.append((type(owner).__name__, child.name,
                                    type(child).__name__, child.color,
                                    child.color == target_colour,
                                    getattr(type(child), 'color', None)
                                    == target_colour))
            row.update(intended=colour_name, intended_value=target_colour,
                       children_after=len(reached),
                       reach=sum(1 for r in reached if r[4]),
                       class_level=sum(1 for r in reached if r[5]),
                       detail=reached[:12])
        report.append(row)
    return dict(target=target, render_seconds=round(elapsed, 1),
                sites=report)


if __name__ == '__main__':
    print('machinome from', machinome.__file__, file=sys.stderr)
    out = sys.argv[1]
    for target in sys.argv[2:]:
        try:
            result = probe(target)
        except Exception as error:  # report and carry on
            import traceback
            result = dict(target=target, error=repr(error),
                          trace=traceback.format_exc()[-3000:])
        name = target.split(':')[0].split('.')[-2]
        with open(f'{out}/probe-{name}.json', 'w') as fh:
            json.dump(result, fh, indent=1, default=str)
```

### `probe_document.py`

```python
"""Serialize a model's tree against the bench, as a build publishes it,
and print the colour each part of the colour loops' assemblies carries.

The tree walk is `machinome.core.serializer.serialize_node`, the walk the
build's viewer document is made of, after the loader's default binding;
the rigid model references are replaced by the node name, so nothing is
built and nothing is written to the project.

Usage: probe_document.py OUT.json module:Class
"""

import importlib
import json
import sys

import machinome
from machinome.core.serializer import serialize_node
from machinome.simulation.enumeration import qualified_drivers

WATCHED = ('/winding_key/', '/winding_knob/', '/pulley/', '/supports/',
           '/raised_detail/', '/standoffs/', '/numerals/')


def main(out, target):
    module_name, class_name = target.split(':')
    root = getattr(importlib.import_module(module_name), class_name)()
    qualified_drivers(root)
    document = serialize_node(root, lambda node: node.name)
    rows = []

    def walk(node, path):
        path = f'{path}/{node["name"]}'
        if any(w in path + '/' for w in WATCHED) and 'children' not in node:
            rows.append((path, node['color']))
        for child in node.get('children', ()):
            walk(child, path)

    walk(document, '')
    with open(out, 'w') as fh:
        json.dump(dict(target=target, machinome=machinome.__file__,
                       parts=rows), fh, indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
```

### `summarize.py`

```python
import glob
import json
import sys

for path in sorted(glob.glob(sys.argv[1] + '/probe-*.json')):
    data = json.load(open(path))
    print('==', data['target'], data.get('render_seconds'), 's',
          data.get('error', ''))
    if 'trace' in data:
        print(data['trace'])
    for site in data.get('sites', []):
        print('  ', {k: v for k, v in site.items()
                     if k not in ('detail', 'intended_value')})
        if '-v' in sys.argv:
            for row in site.get('detail', []):
                print('      ', row)
```

### `refuse_probe.py` (Stage P's outside install of the refusal)

```python
"""Design probe, never committed: install the proposed refusal on
InternalNode.children from outside the bench, so a suite run shows which
code reads `children` inside a lifecycle phase before anything has
assigned them.

Loaded as a pytest plugin (`-p refuse_probe`) or imported first by a
script. Every refusal is appended to REFUSALS_LOG, then raised.
"""

import os
import sys

from machinome.node import phase
from machinome.node.declarative import StructureError
from machinome.node.internal import InternalNode

LOG = os.environ.get(
    'REFUSALS_LOG',
    '/tmp/claude-1000/-home-asa-devel-machinome/'
    'ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle3/refusals.log')


def _children(self):
    linked = self.__dict__.get('children')
    if linked is not None:
        return linked
    current = phase.current()
    if current is None:
        return ()
    frame = sys._getframe(1)
    with open(LOG, 'a') as fh:
        fh.write(f'{os.environ.get("PYTEST_CURRENT_TEST", "-")}\t'
                 f'{current.kind}\t{type(current.assembly).__name__}\t'
                 f'{type(self).__name__}\t{frame.f_code.co_filename}:'
                 f'{frame.f_lineno}\n')
    raise StructureError(
        f"{type(self).__name__} '{self.name}': children read during "
        f"{current.kind}() of {type(current.assembly).__name__} "
        f"'{current.assembly.name}' before they are linked")


def _set_children(self, value):
    self.__dict__['children'] = value


InternalNode.children = property(_children, _set_children)
```

### `prechange.py` (this cycle: the pre-change behaviour, for §4.3's "before")

```python
"""Run `machinome` against the bench with the pre-change `children`
behaviour restored from outside: a read answers the assigned list or the
empty tuple, in every phase, exactly as the plain class attribute did
before children-refuse-early-reads. Never committed.

Usage: python prechange.py <machinome arguments...>
"""

import sys

from machinome.node.internal import InternalNode


def _children(self):
    return self.__dict__.get('children', ())


def _set_children(self, value):
    self.__dict__['children'] = value


InternalNode.children = property(_children, _set_children)

if __name__ == '__main__':
    from machinome.cli import manage
    sys.argv[0] = 'machinome'
    sys.exit(manage())
```
