Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`;
every project command as
`env -C <project> PYTHONPATH=<bench>:<project> /home/asa/devel/machinome/.venv/bin/<tool> ...`
with `<Clocks>` = `/home/asa/devel/machinome/projects/3DPrintedClocks` and
`<Thor>` = `/home/asa/devel/machinome/projects/Robotic-Arms/Thor`. Both
projects are read and run, never edited; nothing is created under them.
`<scratch>` is the campaign scratchpad's `cycle6/` directory. It holds
`probe/` (`pyproject.toml`, `two_arbors.py`, `test_two_arbors.py`,
`measure_paths.py`, `time_walk.py`), run from `<scratch>/probe` with
`PYTHONPATH=<bench>:<scratch>/probe`; `fixture_paths.py`, run from
`<bench>` with the bench path as its one argument; `provoke_mantel34.py`,
run from `<Clocks>`; and `thor_paths.py`, run from `<Thor>`. One test run
of ours at a time (the meta suite and the full suite share
`tests/_build`). Every test marked RED in section 2 is run and seen red,
for the reason it names, before the code that turns it green. Record every
command and its result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`, and
copy the scratch scripts' sources into it (the scratchpad is not
durable).

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Run `pytest -q -p no:cacheprovider tests/test_assertions.py
  tests/test_connectivity.py tests/test_assembly_integrity.py
  tests/test_assembly_supported.py tests/test_broad_phase_culling.py
  tests/test_mesh_cache.py tests/test_driver_ids.py
  tests/test_brep_geometry.py`, then, alone, `pytest -q -p
  no:cacheprovider tests/test_meta.py`; record counts and wall times
  (Stage P: 269 passed, 53 subtests passed, 5.75 s; 61 passed, 94.23 s).
- [ ] 1.3 Run the scratch probes and record their output: `machinome test
  two_arbors.py` in `<scratch>/probe` (Stage P: `wheel should not
  interfere with wheel (intersection volume 32.0)` and `wheel should not
  intersect wheel (intersection volume 32.0)`, 0 passed, 2 failed);
  `measure_paths.py` (the document's leaf paths and `instance_path` both
  `centre.wheel`, `centre.rod`, `third.wheel`, `third.rod`);
  `time_walk.py` (Stage P: 0.38 µs at depth 2, 1.23 µs at depth 12);
  `fixture_paths.py` (design.md, Decision 6).
- [ ] 1.4 In `<Clocks>`: `git -C <Clocks> status --short` (expect only
  ` M screenshots/wall_clock_03.png` and `?? WTs/`, neither ours); then
  `machinome test mantel_clock_34_steampunk --mesh --volume-epsilon 0.001`,
  recording the count, wall time and every `AssertionError` line (Stage P:
  20 tests, 15 passed, 5 failed, 194.29 s; `shell should not interfere with
  lid_screw_right (...)` three times); then `python
  <scratch>/provoke_mantel34.py` (Stage P: `wheel should not intersect
  wheel (intersection volume 809.3194719841327)`, `wheel should not
  interfere with wheel (intersection volume 0.8092617098037365)`).
- [ ] 1.5 In `<Thor>`: `git -C <Thor> status --short` (expect clean), then
  `python <scratch>/thor_paths.py` (Stage P: 438 printed solids, 438 named
  by hand, 0 differ; 67 leaf names repeat). Do not run Thor's suites: its
  contracts run on the B-rep engine only and take hours, and no focused
  model test under a minute exists.

## 2. Red tests

- [ ] 2.1 RED `tests/test_driver_ids.py`, a class `PathNameTest` beside
  `QualifiedIdTest`, on `tests/meta_project/machine.py`'s fixtures, each
  linked by `drive_tree` as `QualifiedIdTest` does:
  - for every node below `Machine()` (`x_axis`, `x_axis.carriage`,
    `y_axis.cover`, ...), `path_name(node, machine)` equals
    `'.'.join(instance_path(node, machine))`, and two instances' children
    differ (`x_axis.carriage`, `y_axis.carriage`);
  - `path_name(machine, machine)` is `machine.name`;
  - a node of an UNLINKED `Machine()` (never walked) is named by its bare
    name (`path_name(fresh.x_axis, fresh) == fresh.x_axis.name`) and
    nothing raises, where `instance_path` raises `DriverIdError`;
  - a node of ANOTHER linked `Machine()` is named below that tree's top
    (`path_name(other.x_axis.carriage, machine) == 'x_axis.carriage'`), and
    `path_name(node)` with no root gives the same;
  - below `ListMachine()`, `path_name(machine.axes[0].carriage, machine)`
    is `'axes-0.carriage'`, and nothing raises.
  Red today: `path_name` does not exist (ImportError).
- [ ] 2.2 RED `tests/test_assertions.py`, a class `NamedByPathTest`, on
  `FakeNode` doubles linked by setting `_parent` by hand (a root `Root`
  holding two `FakeNode`s named `centre` and `third`, each holding a
  `FakeNode` named `wheel`; all overlap at the origin; every parent's
  `operations` empty) and a `machinome.test.TestCase` instance bound with
  `set_node(root)`:
  - `assertNotIntersecting(centre_wheel, third_wheel)` fails with a message
    starting `centre.wheel should not intersect third.wheel (intersection
    volume`;
  - `assertFreeWithin(centre_wheel, 1, third_wheel)` fails with a message
    starting `centre.wheel should be free at 1deg against third.wheel`;
  - a direct child (`lever`, parent `root`) against `centre_wheel` reads
    `lever should not intersect centre.wheel (...)`;
  - the root itself against `centre_wheel` reads `Root should not
    intersect centre.wheel (...)`;
  - two unlinked doubles read exactly as today (`Node should not intersect
    Node (...)`);
  - the same linked pair on an unbound `TestCase()` (no `set_node`), and on
    one whose `node` is a class, still reads `centre.wheel ... third.wheel`
    and raises nothing else.
  Red today: every message names `wheel` twice; the direct-child, root and
  unlinked cases are green before and after (they pin "unchanged").
- [ ] 2.3 RED the reproduction end to end: `tests/meta_project/two_arbors.py`
  (`TwoArbors` holding `centre` and `third`, two `TrainArbor`s, each with
  `wheel = Cube(4.0)` and `rod = Cube(1.0)` placed 10 mm above it, `third`
  translated 2 mm along x; no `name=`; the `Cube` of `.parts`) and
  `tests/meta_project/test_two_arbors.py` (`node = TwoArbors`;
  `test_no_interference` calling `assertNoSolidInterference(self.node)`;
  `test_wheels_apart` calling `assertNotIntersecting(self.node.centre.wheel,
  self.node.third.wheel)`), and in `tests/test_meta.py` a class
  `NamedByPathMetaTest` asserting both tests fail and the run prints the
  full pair, `centre.wheel should not intersect third.wheel (intersection
  volume` and the interference message naming `centre.wheel` and
  `third.wheel` in the order the sweep emits them (record the order the
  green run prints, and pin that exact string). Red today: `wheel should
  not interfere with wheel`.
- [ ] 2.4 RED the moved expectations: edit the seven lines of design.md,
  Decision 6, in `tests/test_meta.py` to the strings its table gives (415,
  472, 475, 536, 539, 597, 617), and nothing else; line 542 stays. Run
  the affected classes (`PairwiseAdjacencyMetaTest`,
  `AssemblySupportMetaTest`, `ExactGeometryMetaTest`): 415, 472, 475, 597 and 617 red; 536 and 539
  red as well, since `cantilever.bar` and `tippy.tippy` are not printed
  today.

## 3. The helper

- [ ] 3.1 Add `path_name(node, root=None)` to `machinome/node/qualified.py`
  after `instance_path`, with the contract of design.md, Decisions 2 and
  3: walk `_parent` upward from `node`, stopping at `root` or at a node
  with no parent, join the collected names with `.`, return `node.name`
  when there are none, never raise. Its docstring says it names a node in
  a message, why it is not a relaxed `instance_path` (the module
  docstring's rule) and why it applies no segment rule.
- [ ] 3.2 Leave `instance_path`, `driver_id` and `_LEGAL_SEGMENT`
  untouched; `QualifiedIdTest` stays green unchanged.

## 4. Every message site

- [ ] 4.1 Import `path_name` in `machinome/test.py` and add
  `TestCase._named(self, node)` returning `path_name(node, getattr(self,
  'node', None))`.
- [ ] 4.2 Replace `X.name` with `self._named(X)` at every in-scope site of
  design.md, Decision 4 (first table): 2046, 2055, 2062, 2071-2072,
  2081-2082, 2091, 2101, 2265-2266, 2268-2269, 2273-2274, 2305, 2356, 2487,
  2516 and 2519 (the `_statics_body` labels, read back at 2543), 2573-2575,
  2599, 2605, 2651.
- [ ] 4.3 Leave the out-of-scope sites of Decision 4's second table as
  they are: 420, 442, 1105, 1967, 2587. Thread no root into a module-level
  helper.
- [ ] 4.4 `grep -n '\.name\b' machinome/test.py` after the edit lists only
  the out-of-scope sites and `_VirtualFloor.name`; no in-scope site
  computes a name outside its `raise` except 2516 and 2519.

## 5. Green

- [ ] 5.1 2.1 to 2.4 pass.
- [ ] 5.2 Re-run the files of 1.2 (each run alone): the focused files at
  the baseline count plus the tests added in 2.1 and 2.2, every other
  expectation untouched; `tests/test_meta.py` at 61 plus the test of 2.3,
  all passed.
- [ ] 5.3 Re-run `machinome test two_arbors.py` in `<scratch>/probe` and
  record the new messages beside 1.3's.
- [ ] 5.4 `black --check` and `flake8 --max-line-length=89` on
  `machinome/node/qualified.py`, `machinome/test.py` and every touched
  test file.

## 6. Project validation, after

- [ ] 6.1 In `<Clocks>`, the documented run of 1.4 again: 20 tests, 15
  passed, 5 failed, the same tests; the interference failures now read
  `movement.pendulum.bob.shell should not interfere with
  movement.pendulum.bob.lid_screw_right (intersection volume ...)` (or the
  pair in the order the sweep emits it) and the connectivity failure
  `case.plates.edging should be one connected body, ...`. Record every
  `AssertionError` line, the count and the wall time beside 1.4's.
- [ ] 6.2 `python <scratch>/provoke_mantel34.py` again: both messages name
  `movement.train.third.wheel` and `movement.train.fourth.wheel` (or, for
  the whole-train assertion, whichever pair the sweep emits first, by its
  paths). Record both.
- [ ] 6.3 Add to `<scratch>/thor_paths.py` a comparison of
  `machinome.node.qualified.path_name(solid, root)` with
  `seats.qualified_names(root)` for every printed solid, run it, and
  record: every one of the solids the same string, so the name the
  framework now prints for a Thor solid is the one the project builds by
  hand.
- [ ] 6.4 `git -C <Clocks> status --short` and `git -C <Thor> status
  --short` as in 1.4 and 1.5: nothing changed in either project.

## 7. Documentation, changelog, records

- [ ] 7.1 `docs/reference/assertions.rst`: in the opening paragraph, after
  the sentence on how the runner hands the node over, one or two sentences
  saying that a failure names a part by its path below the node under
  test, as `movement.train.third.wheel`, the path the viewer's tree shows
  and a qualified driver id is built from, and that a direct child reads
  as its bare name. Confirm the tutorial's quoted messages
  (`docs/tutorial/06-fit.rst:38`, `:72`, `07-scenario.rst:57`) name direct
  children and stay.
- [ ] 7.2 `docs/project/changelog.rst`: one bullet under the existing
  `Unreleased` section, naming the change (`name-solids-by-path`) as the
  bullets there do: a failing assertion names a part by its path below the
  node under test, so two instances of one class read apart
  (`centre.wheel should not interfere with third.wheel`); a direct child
  reads as before.
- [ ] 7.3 `workflow/warts.md`: move the "3DPrintedClocks (2026-09-07,
  shared simulation package)" entry, verbatim, to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under a heading
  `## \`name-solids-by-path\``, and delete it with its now empty heading;
  move the "Related:" paragraph of the second "Robots/Thor (2026-09-07,
  full simulation with fasteners)" entry there too, verbatim, saying where
  it came from, and delete it from that entry, whose inventory finding
  stays open; follow both with a "What shipped" paragraph (the rule, the
  helper, the mantel clock and Thor results of section 6). Remove the
  "Interference failures name the leaf, not its path" bullet of "Standing
  triage", "Planned, never done". File one new entry, "Findings from the
  framework cycle `name-solids-by-path` (2026-10-06)": the engine labels of
  design.md, Decision 4's second table still print a bare name beside an
  assertion message that prints a path.
- [ ] 7.4 `workflow/ongoing/fix-warts-3.md`: one "Progress" entry for this
  cycle, in the shape of the earlier ones.

## 8. Sync, archive, close

- [ ] 8.1 Sync the `test-framework` delta into
  `openspec/specs/test-framework/spec.md` (the ADDED requirement and the
  MODIFIED "Mesh assertions", its three scenarios carried).
- [ ] 8.2 Finish `evidence.md`; archive the change to
  `openspec/changes/archive/2026-10-06-name-solids-by-path/`; `openspec
  validate --specs` (or `openspec validate test-framework`) passes.
- [ ] 8.3 The focused files of 1.2 once more, then the full suite once,
  alone (`pytest -q -p no:cacheprovider` at the bench root); record counts
  and wall times. Leave everything uncommitted.
