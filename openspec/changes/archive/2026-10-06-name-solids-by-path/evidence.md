# Evidence — `name-solids-by-path`

Cycle 6 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`350febd73db292c01750676485611b271ca78a64` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...`, every project command as
`env -C <project> PYTHONPATH=<bench>:<project> .venv/bin/<tool> ...`, with
Python 3.12.3. `env -C <bench> PYTHONPATH=<bench> .venv/bin/python -c
'import machinome; print(machinome.__file__)'` printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
One test run of ours at a time; before each long run `ps -eo pid,args | grep
'[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
listed nothing of ours.

`<Clocks>` is `/home/asa/devel/machinome/projects/3DPrintedClocks` (at
`ec2a05d`), `<Thor>` is `/home/asa/devel/machinome/projects/Robotic-Arms/Thor`
(at `47ba67f`), `<scratch>` the campaign scratchpad's `cycle6/` directory.
The scratch scripts' sources are copied at the end of this file.

## 1. Baseline on the unmodified tree (350febd)

### 1.2 Focused files and the meta suite

```
pytest -q -p no:cacheprovider tests/test_assertions.py tests/test_connectivity.py \
  tests/test_assembly_integrity.py tests/test_assembly_supported.py \
  tests/test_broad_phase_culling.py tests/test_mesh_cache.py \
  tests/test_driver_ids.py tests/test_brep_geometry.py
269 passed, 2 warnings, 53 subtests passed in 5.64s   (wall 7 s)

pytest -q -p no:cacheprovider tests/test_meta.py      (alone)
61 passed in 95.83s (0:01:35)                         (wall 97 s)
```

### 1.3 The scratch probes

`env -C <scratch>/probe PYTHONPATH=<bench>:<scratch>/probe .venv/bin/machinome
test two_arbors.py` (exit 1):

```
AssertionError: wheel should not interfere with wheel (intersection volume 32.0)
AssertionError: wheel should not intersect wheel (intersection volume 32.0)
Ran 2 tests in 0.11 seconds: 0 passed, 2 failed
```

`python measure_paths.py` (same directory and path):

```
document leaf paths below the root:
    centre.wheel
    centre.rod
    third.wheel
    third.rod
instance_path below the root:
    centre.wheel
    centre.rod
    third.wheel
    third.rod
leaf .name (what the assertion prints today):
    wheel
    rod
    wheel
    rod
list-held children: ['beads-0', 'beads-1']
root itself: ()
unlinked node: DriverIdError: cannot qualify Block 'Block': it is not linked under TwoArbors 'TwoArbors', so i ...
node of another tree: DriverIdError: cannot qualify Block 'wheel': it is not linked under TwoArbors 'TwoArbors', so i ...
```

`python time_walk.py`: `depth 2: third.wheel`, 0.38 µs per call;
`depth 12: n0.n1.n2.n3.n4.n5.n6.n7.n8.n9.n10.n11`, 1.25 µs per call.

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python <scratch>/fixture_paths.py
<bench>`: identical on stdout to Stage P's survey (design.md, Decision 6);
the nodes with a path of more than one segment include `group.c`
(`separated_overlap`), `chain.floater`, `chain.rider`, `leaning.left`,
`leaning.right` (`assembly_supported_floating`), `cantilever.bar`,
`tippy.tippy`, `tippy.neighbour` (`assembly_supported_unbalanced`) and
`carriage.moving` (`assembly_integrity_animated`).

### 1.4 Mantel clock 34

`git -C <Clocks> status --short`: ` M screenshots/wall_clock_03.png` and
`?? WTs/`, neither ours.

`env -C <Clocks> PYTHONPATH=<bench>:<Clocks> .venv/bin/machinome test
mantel_clock_34_steampunk --mesh --volume-epsilon 0.001` (exit 1, wall 28 s;
the verdict store, ADR-156, serves the verdicts Stage P's 199 s run kept —
it stores volumes, not message text, so every message below is built by
the code under test):

```
Running MantelClock34SteampunkTest.test_assembly_integrity........FAIL!
AssertionError: shell should not interfere with lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_movement_runs_free_through_a_swing....FAIL!
AssertionError: shell should not interfere with lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_solid_integrity.FAIL!
AssertionError: edging should be one connected body, but its STL contains 6 connected bodies
Running MantelClock34SteampunkTest.test_source_body_inventory.FAIL!
AssertionError: ['root.case.plates.edging: edging should be one connected body, but its STL contains 6 connected bodies', 'root.case.pillars.printed: printed should be one connected body, but its STL contains 4 connected bodies', 'root.case.pillars.behind: behind should be one connected body, but its STL contains 2 connected bodies', 'root.dial.numerals: numerals should be one connected body, but its STL contains 76 connected bodies', 'root.dial.supports: supports should be one connected body, but its STL contains 4 connected bodies', 'root.movement.power.arbor.ratchet_gear / root.movement.power.arbor.pawl: ratchet_gear should not intersect pawl (intersection volume 12.614036176992302)', 'root.movement.power.arbor.pawl / root.movement.power.arbor.click: pawl should not intersect click (intersection volume 107.94825470251449)', 'root.movement.pendulum.holder.collet / root.movement.pendulum.holder.hinge_screw: collet should not intersect hinge_screw (intersection volume 14.572911630649433)', 'root.movement.pendulum.holder.body / root.movement.pendulum.holder.beat_crinkle_washer: body should not intersect beat_crinkle_washer (intersection volume 1.5772444289067555)', 'root.movement.pendulum.holder.beat_screw / root.movement.pendulum.holder.beat_nut: beat_screw should not intersect beat_nut (intersection volume 0.002538083596905625)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_left: shell should not intersect lid_screw_left (intersection volume 1.7215580128599834)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_right: shell should not intersect lid_screw_right (intersection volume 1.7215580128600183)'] is not false :
Running MantelClock34SteampunkTest.test_the_train_meshes_all_the_way_round....FAIL!
AssertionError: shell should not interfere with lid_screw_right (intersection volume 1.7215580128600183)
Ran 20 tests in 23.73 seconds: 15 passed, 5 failed (mesh engine, volume epsilon 0.001 mm³)
```

`env -C <Clocks> PYTHONPATH=<bench>:<Clocks> .venv/bin/python
<scratch>/provoke_mantel34.py` (exit 0, wall 12 s):

```
'shell' is at 'movement.pendulum.bob.shell'
'lid_screw_right' is at 'movement.pendulum.bob.lid_screw_right'
'wheel' is at 'movement.train.third.wheel'
'wheel' is at 'movement.train.fourth.wheel'
pulled fourth onto third by [18.489, 18.415, -16.282]
centres now [40.673 -3.775 66.78 ] [40.673 -3.775 66.78 ]
fourth.wheel is Arbor rigid True parent TrainArbor
assertNotIntersecting(third.wheel, fourth.wheel):
    AssertionError: wheel should not intersect wheel (intersection volume 809.3194719841327)
assertNoSolidInterference(root.movement.train):
    AssertionError: wheel should not interfere with wheel (intersection volume 0.8092617098037365)
```

`git -C <Clocks> status --short` afterwards: unchanged.

### 1.5 Thor

`git -C <Thor> status --short`: clean. `env -C <Thor> PYTHONPATH=<bench>:<Thor>
.venv/bin/python <scratch>/thor_paths.py` (exit 0, wall 5 s):

```
loaded and rendered in 3.1 s
438 printed solids; 438 named by hand; 0 differ from instance_path
67 leaf names repeat, e.g. ['art23_optodisk', 'bearing_625zz_1', 'bearing_625zz_2', 'body', 'common_bearing_fix_through', 'fan_40x40']
    shoulder.art2.art3.art4.art56.gt2x40_pulley_1 == by hand: True
```

Thor's suites were not run: its contracts run on the B-rep engine only and
take hours (`README.md`, "Running it"), and no focused model test under a
minute exists.

## 2. Red tests, on the unmodified code

### 2.1 `tests/test_driver_ids.py`, `PathNameTest`

Five tests: the path equals `'.'.join(instance_path(...))` for every node
below a linked `Machine()` and tells `x_axis.carriage` from
`y_axis.carriage`; the root is its bare name; a node of an unlinked
`Machine()` is its bare name where `instance_path` raises; a node of
another linked `Machine()` is named below that tree's top, with `root`
given or omitted; `ListMachine()`'s `axes-0.carriage` and `axes-1` are
printed as derived. `drive_tree` refuses `ListMachine`'s `axes-0` segment
before it links the axes' own children, so that test links the tree with
`_link_children`, one sibling batch per parent, as a render does (tasks.md
2.1 says so).

`pytest -q -p no:cacheprovider tests/test_driver_ids.py` (exit 2):

```
E   ImportError: cannot import name 'path_name' from 'machinome.node.qualified' (.../WTs/fix-warts-3/machinome/node/qualified.py)
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.18s
```

### 2.2 `tests/test_assertions.py`, `NamedByPathTest`

`FakeNode` doubles linked by `_parent` (`Root` holding `centre`, `third`
and `lever`; `centre` and `third` each holding a `wheel`; all unit boxes at
the origin), a `machinome.test.TestCase` bound with `set_node(root)`.
`pytest -q -p no:cacheprovider tests/test_assertions.py -k NamedByPathTest`
(exit 1):

```
E       AssertionError: False is not true : lever should not intersect wheel (intersection volume 1.0)
E           AssertionError: False is not true : wheel should not intersect wheel (intersection volume 1.0)
E       AssertionError: False is not true : Root should not intersect wheel (intersection volume 1.0)
E       AssertionError: False is not true : wheel should be free at 1deg against wheel (intersection volume 0.9914241312243224)
E       AssertionError: False is not true : wheel should not intersect wheel (intersection volume 1.0)
FAILED tests/test_assertions.py::NamedByPathTest::test_a_direct_child_keeps_its_bare_name
FAILED tests/test_assertions.py::NamedByPathTest::test_no_bound_node_names_below_the_tree_top
FAILED tests/test_assertions.py::NamedByPathTest::test_the_node_under_test_keeps_its_bare_name
FAILED tests/test_assertions.py::NamedByPathTest::test_the_perturbation_pair_reads_apart
FAILED tests/test_assertions.py::NamedByPathTest::test_two_instances_of_one_class_read_apart
5 failed, 1 passed, 40 deselected in 1.14s
```

The direct-child and root cases are red as well, not green as tasks.md
first said: their own node keeps its bare name, but the second node they
name is `centre.wheel`, which reads `wheel` today. `test_unlinked_nodes_read_as_before`
is the one green before and after. tasks.md 2.2 is corrected to say so.

### 2.3 and 2.4 The reproduction fixture and the moved expectations

`tests/meta_project/two_arbors.py` and `tests/meta_project/test_two_arbors.py`
(the fixture of tasks.md 2.3), `NamedByPathMetaTest` in `tests/test_meta.py`,
and the seven expectation lines of design.md, Decision 6, edited to their
new strings (line 542, `assertNotIn('neighbour cannot rest', ...)`, left
as it is). `pytest -q -p no:cacheprovider tests/test_meta.py -k
'NamedByPathMetaTest or PairwiseAdjacencyMetaTest or AssemblySupportMetaTest
or ExactGeometryMetaTest'` (exit 1, wall 31 s):

```
E       AssertionError: 'centre.wheel should not interfere with third.wheel (intersection volume' not found in 'Running TwoArborsTest.test_no_interference.FAIL!...
E       AssertionError: 'a should not intersect group.c' not found in 'Running SeparatedOverlapTest.test_no_pairwise_intersections.FAIL!...
E       AssertionError: 'chain.floater, chain.rider should be supported against gravity' not found in 'Running AssemblySupportedFloatingTest...
E       AssertionError: 'cantilever.bar cannot rest in frictionless static equilibrium' not found in 'Running AssemblySupportedUnbalancedTest...
E       AssertionError: 'fixed should not interfere with carriage.moving' not found in 'Running AssemblyIntegrityAnimatedTest.test_assembly_integrity...FAIL!...
E       AssertionError: 'fixed should not interfere with carriage.moving' not found in 'Running AssemblyIntegrityAnimatedTest.test_assembly_integrity..FAIL!...
FAILED tests/test_meta.py::NamedByPathMetaTest::test_two_instances_of_one_class_are_named_apart
FAILED tests/test_meta.py::PairwiseAdjacencyMetaTest::test_nonadjacent_overlap_is_reported_naming_both_leaves
FAILED tests/test_meta.py::AssemblySupportMetaTest::test_floating_chain_and_ungrounded_lean_are_reported
FAILED tests/test_meta.py::AssemblySupportMetaTest::test_unbalanced_assemblies_are_reported
FAILED tests/test_meta.py::ExactGeometryMetaTest::test_animated_world_placement_reports_positive_interference
FAILED tests/test_meta.py::ExactGeometryMetaTest::test_failfast_stops_the_animated_instant_loop
6 failed, 9 passed, 47 deselected in 30.55s
```

A test stops at its first failing expectation, so the `leaning.left,
leaning.right` and `tippy.tippy` lines are not reached on the red run;
the fixture runs in 5.3 show both strings printed after the change, and
neither could be printed before, when a message printed the leaf names
`left`, `right` and `tippy` (1.3's survey).

## 3 and 4. The helper and the message sites

- `machinome/node/qualified.py`: `path_name(node, root=None)` after
  `instance_path`, walking `_parent` from `node` until `root` or a node
  with no parent, joining the collected names with `.`, else `node.name`.
  `instance_path`, `driver_id` and `_LEGAL_SEGMENT` untouched.
- `machinome/test.py`: `from machinome.node.qualified import path_name`;
  `TestCase._named(self, node)` returns `path_name(node, getattr(self,
  'node', None))`; every in-scope site of design.md, Decision 4, prints
  `self._named(X)`: the seven pair assertions, the three perturbation
  messages, `assertNoDisconnectedSolids`, `assertNoSolidInterference`, the
  reachability phase of `assertAssemblySupported` and the `_statics_body`
  labels of its equilibrium phase, the three messages of `assertJoined`,
  and `assertNoPairwiseIntersections`.
- `grep -n '\.name\b' machinome/test.py` afterwards lists 421 and 443
  (`_admitted` labels), 1106 (`intersect_shapes` labels), 1968
  (`_brep_verdict` labels), 2598 (`fuse_shapes` labels), the out-of-scope
  sites of Decision 4, and 2553, `bodies[index].name`, which reads back the
  `_Body` label the equilibrium phase now builds with `self._named`.
  `_VirtualFloor`'s `name` is a class attribute (`'the floor'`) and reads
  as its bare name through `path_name`.

## 5. Green

### 5.1 and 5.2

`pytest -q -p no:cacheprovider` on 1.2's eight files (exit 0, wall 7 s):

```
280 passed, 2 warnings, 53 subtests passed in 5.77s
```

269 at baseline plus `PathNameTest`'s 5 and `NamedByPathTest`'s 6.

`pytest -q -p no:cacheprovider tests/test_meta.py`, alone (exit 0, wall
87 s):

```
62 passed in 87.27s (0:01:27)
```

61 at baseline plus `NamedByPathMetaTest`. The interference sweep emits
the pair as `centre.wheel` then `third.wheel`, the order pinned.

### 5.3 The probe and the fixtures, after

`machinome test two_arbors.py` in `<scratch>/probe` (exit 1):

```
AssertionError: centre.wheel should not interfere with third.wheel (intersection volume 32.0)
AssertionError: centre.wheel should not intersect third.wheel (intersection volume 32.0)
Ran 2 tests in 0.10 seconds: 0 passed, 2 failed
```

Each moved fixture run directly, `env -C <bench> PYTHONPATH=<bench>
SOLID_BUILD_DIR=<bench>/tests/_build_meta .venv/bin/python -c 'from
machinome.cli import manage; manage()' test tests/meta_project/<fixture>.py`:

```
two_arbors:
AssertionError: centre.wheel should not interfere with third.wheel (intersection volume 32.0)
AssertionError: centre.wheel should not intersect third.wheel (intersection volume 32.0)
separated_overlap:
AssertionError: a should not intersect group.c (intersection volume 0.7)
assembly_supported_floating:
AssertionError: chain.floater, chain.rider should be supported against gravity, but no support path reaches a grounded solid (dropped 1mm along gravity (0, 0, -1))
AssertionError: leaning.left, leaning.right should be supported against gravity, but no support path reaches a grounded solid (dropped 1.5mm along gravity (0, 0, -1))
assembly_supported_unbalanced:
AssertionError: cantilever.bar cannot rest in frictionless static equilibrium on its detected contacts (unbalanced torque). Declare a hold that is real but outside frictionless statics in supports=[(supported, supporter)]
AssertionError: tippy.tippy cannot rest in frictionless static equilibrium on its detected contacts (unbalanced torque). Declare a hold that is real but outside frictionless statics in supports=[(supported, supporter)]
assembly_integrity_animated:
AssertionError: fixed should not interfere with carriage.moving (intersection volume 0.5)
```

### 5.4 Lint, compared against `HEAD`

`flake8 --max-line-length=89` (the pyenv shim, flake8 7.3.0) on each
touched file, and on the same file at `HEAD` (`git show HEAD:<file> |
flake8 --max-line-length=89 --stdin-display-name=<file> -`):

```
machinome/node/qualified.py   HEAD 0  after 0
machinome/test.py             HEAD 2  after 2   (E127 at the import block, lines 26-27)
tests/test_assertions.py      HEAD 4  after 4   (E127, older tests)
tests/test_driver_ids.py      HEAD 0  after 0
tests/test_meta.py            HEAD 3  after 3   (two E302 and one E127, older code)
tests/meta_project/two_arbors.py, test_two_arbors.py   (new)  0
```

`black --check` (the workspace's black 26.5.1): none of the five existing
files passes at `HEAD` either (each `git show HEAD:<file> | black --check
-` exits 1); black rewrites their single-quoted strings, which the new code
keeps to match each file. The two new fixture files pass (`black -q --diff`
empty) after one call in `test_two_arbors.py` was put on one line.

## 6. Project validation, after

### 6.1 Mantel clock 34

The documented run of 1.4 (exit 1, wall 46 s):

```
Running MantelClock34SteampunkTest.test_assembly_integrity....FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_movement_runs_free_through_a_swing....FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_solid_integrity.FAIL!
AssertionError: case.plates.edging should be one connected body, but its STL contains 6 connected bodies
Running MantelClock34SteampunkTest.test_source_body_inventory.FAIL!
AssertionError: ['root.case.plates.edging: case.plates.edging should be one connected body, but its STL contains 6 connected bodies', 'root.case.pillars.printed: case.pillars.printed should be one connected body, but its STL contains 4 connected bodies', 'root.case.pillars.behind: case.pillars.behind should be one connected body, but its STL contains 2 connected bodies', 'root.dial.numerals: dial.numerals should be one connected body, but its STL contains 76 connected bodies', 'root.dial.supports: dial.supports should be one connected body, but its STL contains 4 connected bodies', 'root.movement.power.arbor.ratchet_gear / root.movement.power.arbor.pawl: movement.power.arbor.ratchet_gear should not intersect movement.power.arbor.pawl (intersection volume 12.614036176992302)', 'root.movement.power.arbor.pawl / root.movement.power.arbor.click: movement.power.arbor.pawl should not intersect movement.power.arbor.click (intersection volume 107.94825470251449)', 'root.movement.pendulum.holder.collet / root.movement.pendulum.holder.hinge_screw: movement.pendulum.holder.collet should not intersect movement.pendulum.holder.hinge_screw (intersection volume 14.572911630649433)', 'root.movement.pendulum.holder.body / root.movement.pendulum.holder.beat_crinkle_washer: movement.pendulum.holder.body should not intersect movement.pendulum.holder.beat_crinkle_washer (intersection volume 1.5772444289067555)', 'root.movement.pendulum.holder.beat_screw / root.movement.pendulum.holder.beat_nut: movement.pendulum.holder.beat_screw should not intersect movement.pendulum.holder.beat_nut (intersection volume 0.002538083596905625)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_left: movement.pendulum.bob.shell should not intersect movement.pendulum.bob.lid_screw_left (intersection volume 1.7215580128599834)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_right: movement.pendulum.bob.shell should not intersect movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)'] is not false :
Running MantelClock34SteampunkTest.test_the_train_meshes_all_the_way_round....FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Ran 20 tests in 42.76 seconds: 15 passed, 5 failed (mesh engine, volume epsilon 0.001 mm³)
```

The same 20 tests with the same verdicts as 1.4 (the `Running` lines,
reduced to name and FAIL, compare equal with `diff`), every volume the
same. The project's `test_source_body_inventory` prefixes each framework
message with the path it walks by hand from `root`; that prefix now repeats
the path the framework prints, which is the project's to drop.

### 6.2 The provoked failure

`python <scratch>/provoke_mantel34.py` (exit 0, wall 11 s):

```
assertNotIntersecting(third.wheel, fourth.wheel):
    AssertionError: movement.train.third.wheel should not intersect movement.train.fourth.wheel (intersection volume 809.3194719841327)
assertNoSolidInterference(root.movement.train):
    AssertionError: movement.train.centre.wheel.wheel should not interfere with movement.train.fourth.wheel (intersection volume 0.8092617098037365)
```

The whole-train sweep's first pair is not third against fourth: it is the
centre arbor's wheel solid against the pulled fourth wheel. Before the
change the same pair read `wheel should not interfere with wheel`, which
a reader would have taken for the pair the script pulled together.
`<scratch>/centre_wheel.py` (load and render only) confirms the shape:

```
centre: LanternArbor; wheel is LanternGroup rigid=False; path 'movement.train.centre.wheel'
third: TrainArbor; wheel is Arbor rigid=True; path 'movement.train.third.wheel'
fourth: TrainArbor; wheel is Arbor rigid=True; path 'movement.train.fourth.wheel'
```

so the topmost rigid solid under the centre arbor's `wheel` group is
`movement.train.centre.wheel.wheel`. design.md's proof plan and tasks.md
6.2 record this.

### 6.3 Thor

`<scratch>/thor_paths.py` with the `path_name` comparison added (exit 0,
wall 4 s):

```
loaded and rendered in 2.9 s
438 printed solids; 438 named by hand; 0 differ from instance_path
67 leaf names repeat, e.g. ['art23_optodisk', 'bearing_625zz_1', 'bearing_625zz_2', 'body', 'common_bearing_fix_through', 'fan_40x40']
    shoulder.art2.art3.art4.art56.gt2x40_pulley_1 == by hand: True
path_name: 438 solids; 0 differ from qualified_names()
    path_name: shoulder.art2.art3.art4.art56.gt2x40_pulley_1 == by hand: True
```

### 6.4 Projects untouched

`git -C <Clocks> status --short` after every run: ` M
screenshots/wall_clock_03.png`, `?? WTs/`, as in 1.4. `git -C <Thor> status
--short` after both runs: clean.

## 7. Documentation, changelog, records

- `docs/reference/assertions.rst`, opening paragraph: a failure names a
  part by its path below the node under test (`movement.train.third.wheel`),
  the path the viewer's tree shows and a qualified driver id is built
  from; a direct child reads as its bare name. The tutorial's quoted
  messages (`docs/tutorial/06-fit.rst:38`, `:72`; `07-scenario.rst:57`) name
  `base`, `units_drum` and `handle`, declared directly on the tutorial's
  `Counter` (`docs/tutorial/counter/c04_relations.py`), and stay. No other
  page of `docs/` quotes an assertion message.
- `docs/project/changelog.rst`: one bullet at the end of `Unreleased`,
  "A failing assertion names a part by its path" (name-solids-by-path).
- `workflow/warts.md`: the "3DPrintedClocks (2026-09-07, shared simulation
  package)" entry and its heading, and the "Related:" paragraph of the
  second "Robots/Thor (2026-09-07, full simulation with fasteners)" entry,
  moved verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## \`name-solids-by-path\`` with a "What shipped" paragraph; the
  Thor inventory entry stays open. The "Planned, never done" bullet of
  "Standing triage" removed. New section "Findings from the framework
  cycle `name-solids-by-path` (2026-10-06)": the engines' bare-name labels.
- `workflow/ongoing/fix-warts-3.md`: a "Progress" entry for cycle 6.

## 8. Sync, archive, close

- 8.1: by hand. Into `openspec/specs/test-framework/spec.md`: "Mesh
  assertions" replaced by the delta's MODIFIED text (the path sentence and
  the first scenario's THEN), and the ADDED requirement "A failing
  assertion names a node by its path", with its six scenarios, after it.
  Each of the two requirements, cut from the spec and from the delta up to
  the next heading, compares equal (a short Python check, `True` for
  both). `git diff --stat -- openspec/specs`: test-framework +79 -3.
  `openspec validate test-framework`: "Specification 'test-framework' is
  valid". `openspec validate name-solids-by-path`: "Change
  'name-solids-by-path' is valid".
- 8.2: `openspec archive name-solids-by-path --yes --skip-specs` (the
  specs were synced by hand in 8.1, so the CLI's own sync was skipped):
  "Change 'name-solids-by-path' archived as
  '2026-10-06-name-solids-by-path'". Its warnings: the Why section's
  length, and 29 of 30 tasks complete (8.3, done after it and ticked in
  the archived copy). `openspec validate --specs`: `Totals: 45 passed, 0
  failed (45 items)`.
- 8.3: 1.2's eight focused files once more (exit 0, wall 6 s): `280
  passed, 2 warnings, 53 subtests passed in 5.21s`. Then the full suite,
  alone (`pytest -q -p no:cacheprovider` at the bench root; no other run
  of ours active): exit 0, wall 649 s, `4665 passed, 4 skipped, 55
  warnings, 6644 subtests passed in 647.11s (0:10:47)`.
- During that run one message site of `assertNoDisconnectedSolids` was
  re-wrapped (`f"but its " f"{source} "` joined into `f"but its {source} "`,
  the same string). The focused files after it: `280 passed, 2 warnings,
  53 subtests passed in 5.05s`; the meta fixture `solid_integrity_red`
  still reads `SolidIntegrityRed should be one connected body, but its STL
  contains 2 connected bodies` (its root is the rigid node under test, so
  the bare name); `flake8` on `machinome/test.py` still reports the 2
  findings it reports at `HEAD`.
- Nothing committed on the bench. Nothing written in 3DPrintedClocks or
  Thor (statuses in 6.4).

## Appendix: the scratch scripts

The scratchpad is not durable; these are the sources run above.

### `<scratch>/probe/pyproject.toml`

```toml
[project]
name = "probe"
version = "0"

[tool.machinome]
model = "two_arbors"

[tool.machinome.models]
two_arbors = "two_arbors:TwoArbors"
```

### `<scratch>/probe/two_arbors.py`

```python
"""Reproduction fixture: two instances of one class under one parent,
each holding a `wheel` and a `rod`, the two wheels overlapping."""

from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node
from solid2 import cube


class Block(Solid2Node):

    def __init__(self, size=1.0, name=None):
        self.size = size
        super().__init__(size=size, name=name)

    def render(self):
        return cube(self.size, center=True)


class TrainArbor(AssemblyNode):

    def __init__(self):
        self.wheel = Block(4)
        self.rod = Block(1)
        super().__init__()
        self.rod.translate([0, 0, 10])

    def render(self):
        return [self.wheel, self.rod]


class TwoArbors(AssemblyNode):

    def __init__(self):
        self.centre = TrainArbor()
        self.third = TrainArbor()
        super().__init__()
        self.third.translate([2, 0, 0])

    def render(self):
        return [self.centre, self.third]
```

### `<scratch>/probe/test_two_arbors.py`

```python
from machinome.test import TestCase

from two_arbors import TwoArbors


class TwoArborsTest(TestCase):
    node = TwoArbors

    def test_no_interference(self):
        self.assertNoSolidInterference(self.node)

    def test_wheels_apart(self):
        self.assertNotIntersecting(self.node.centre.wheel,
                                   self.node.third.wheel)
```

### `<scratch>/probe/measure_paths.py`

```python
"""Measurement: the document's tree path, instance_path, and what an
assertion prints today, for the same fixture. Writes nothing."""

import sys

from machinome.core.serializer import serialize_node
from machinome.node.assembly import AssemblyNode
from machinome.node.qualified import DriverIdError, instance_path

from two_arbors import Block, TwoArbors


def document_paths(data, path=()):
    here = path + (data['name'],)
    if 'children' not in data:
        yield here
    for child in data.get('children', ()):
        yield from document_paths(child, here)


root = TwoArbors()
document = serialize_node(root, model_path=lambda node: 'x.stl')
print('document leaf paths below the root:')
for path in document_paths(document):
    print('   ', '.'.join(path[1:]))

print('instance_path below the root:')
for arbor in (root.centre, root.third):
    for leaf in (arbor.wheel, arbor.rod):
        print('   ', '.'.join(instance_path(leaf, root)))

print('leaf .name (what the assertion prints today):')
for arbor in (root.centre, root.third):
    for leaf in (arbor.wheel, arbor.rod):
        print('   ', leaf.name)


class Beads(AssemblyNode):

    def __init__(self):
        self.beads = [Block(1), Block(1)]
        super().__init__()

    def render(self):
        return list(self.beads)


beads = Beads()
serialize_node(beads, model_path=lambda node: 'x.stl')
print('list-held children:',
      ['.'.join(instance_path(b, beads)) for b in beads.beads])

print('root itself:', repr(instance_path(root, root)))
loose = Block(1)
try:
    instance_path(loose, root)
except DriverIdError as error:
    print('unlinked node: DriverIdError:', str(error)[:80], '...')
other = TwoArbors()
serialize_node(other, model_path=lambda node: 'x.stl')
try:
    instance_path(other.centre.wheel, root)
except DriverIdError as error:
    print('node of another tree: DriverIdError:', str(error)[:80], '...')
sys.exit(0)
```

### `<scratch>/probe/time_walk.py`

```python
"""Cost of naming a node by its path: the proposed walk, written here as a
scratch copy, timed at depth 2 (the fixture) and depth 12 (a chain of
linked stand-ins). Writes nothing."""

import timeit
from types import SimpleNamespace

from machinome.core.serializer import serialize_node

from two_arbors import TwoArbors


def path_name(node, root=None):
    parts = []
    current = node
    while current is not root:
        parent = getattr(current, '_parent', None)
        if parent is None:
            break
        parts.append(current.name)
        current = parent
    return '.'.join(reversed(parts)) if parts else node.name


root = TwoArbors()
serialize_node(root, model_path=lambda node: 'x.stl')
wheel = root.third.wheel
print('depth 2:', path_name(wheel, root))
count = 100000
seconds = timeit.timeit(lambda: path_name(wheel, root), number=count)
print(f'    {seconds / count * 1e6:.2f} us per call')

top = SimpleNamespace(name='top', _parent=None)
node = top
for level in range(12):
    node = SimpleNamespace(name=f'n{level}', _parent=node)
print('depth 12:', path_name(node, top))
seconds = timeit.timeit(lambda: path_name(node, top), number=count)
print(f'    {seconds / count * 1e6:.2f} us per call')
```

### `<scratch>/fixture_paths.py`

```python
"""For every meta-project test case: the node it binds, and every node
below it whose path has more than one segment (the nodes whose name in a
failure message would change). Reads fixtures; writes nothing."""

import importlib
import inspect
import pathlib
import sys

from machinome.node.base import AbstractBaseNode
from machinome.node.qualified import instance_path
from machinome.test import TestCase

BENCH = pathlib.Path(sys.argv[1])
fixtures = sorted((BENCH / 'tests' / 'meta_project').glob('test_*.py'))


def walk(node):
    yield node
    if getattr(node, 'rigid', False):
        return
    children = node.render() if hasattr(node, 'render') else None
    if type(children) not in (list, tuple):
        return
    node._link_children(children)
    for child in children:
        yield from walk(child)


for path in fixtures:
    module = importlib.import_module(f'tests.meta_project.{path.stem}')
    for _, case in inspect.getmembers(module, inspect.isclass):
        if not (issubclass(case, TestCase) and case.__module__ == module.__name__):
            continue
        root_class = getattr(case, 'node', None)
        if root_class is None:
            node_module = importlib.import_module(
                f'tests.meta_project.{path.stem[len("test_"):]}')
            candidates = [
                klass for _, klass in inspect.getmembers(
                    node_module, inspect.isclass)
                if issubclass(klass, AbstractBaseNode)
                and klass.__module__ == node_module.__name__]
            if len(candidates) == 1:
                root_class = candidates[0]
        if not (isinstance(root_class, type)
                and issubclass(root_class, AbstractBaseNode)):
            print(f'{path.stem}: {case.__name__}: node={root_class!r}')
            continue
        try:
            root = root_class()
            if hasattr(root, 'set_keyframe'):
                root.set_keyframe(0)
            deep = []
            for node in walk(root):
                if node is root:
                    continue
                segments = instance_path(node, root)
                if len(segments) > 1:
                    deep.append(f"{node.name} -> {'.'.join(segments)}")
        except Exception as error:  # noqa: BLE001 -- a survey
            print(f'{path.stem}: {case.__name__}: could not walk: {error!r}')
            continue
        if deep:
            print(f'{path.stem}: {case.__name__} ({root_class.__name__}):')
            for line in deep:
                print('    ', line)
```

### `<scratch>/provoke_mantel34.py`

```python
"""Provoked failure on 3DPrintedClocks' mantel clock 34: pull the fourth
arbor onto the third so the two `wheel` children overlap, then ask the
framework's own assertions, with the clock's root bound as the node under
test exactly as `machinome test` binds it. Prints the messages.

Run from the project directory with PYTHONPATH=<bench>. The verdict store
is off, so nothing is kept in the project's build directory; the STLs the
runner would build are already current from the documented run.
"""

import numpy as np

from machinome.core.builder import project_build_lock
from machinome.core.loader import load_node
from machinome.node.base import _compose_world_matrix
from machinome.test import (TestCase, resolve_comparison_policy,
                             set_comparison_policy)


class Probe(TestCase):

    def runTest(self):
        pass


set_comparison_policy(resolve_comparison_policy('mesh', 0.001, None, False))

root = load_node('mantel_clock_34_steampunk')
with project_build_lock():
    root.set_keyframe(0)
    root._prepare()
    root.build_stls()

case = Probe()
case.set_node(root)

from machinome.node.qualified import instance_path  # noqa: E402

bob = root.movement.pendulum.bob
for node in (bob.shell, bob.lid_screw_right, root.movement.train.third.wheel,
             root.movement.train.fourth.wheel):
    print(f"{node.name!r} is at {'.'.join(instance_path(node, root))!r}")

train = root.movement.train
third, fourth = train.third, train.fourth


def centre(node):
    return np.asarray(node.mesh.bounds).mean(axis=0)


delta = centre(third.wheel) - centre(fourth.wheel)
# A translation appended to the arbor's operations is applied in the
# frame its ancestors then place: undo their rotation first.
rotation = _compose_world_matrix(train)[:3, :3]
local = np.linalg.solve(rotation, delta)
fourth.translate([float(value) for value in local])
print('pulled fourth onto third by', [round(float(v), 3) for v in delta])
print('centres now', centre(third.wheel).round(3),
      centre(fourth.wheel).round(3))
print('fourth.wheel is', type(fourth.wheel).__name__, 'rigid',
      fourth.wheel.rigid, 'parent', type(fourth.wheel._parent).__name__)

for label, call in (
        ('assertNotIntersecting(third.wheel, fourth.wheel)',
         lambda: case.assertNotIntersecting(third.wheel, fourth.wheel)),
        ('assertNoSolidInterference(root.movement.train)',
         lambda: case.assertNoSolidInterference(train))):
    try:
        call()
    except AssertionError as error:
        print(f'{label}:\n    AssertionError: {error}')
    else:
        print(f'{label}: passed')
```

### `<scratch>/centre_wheel.py`

```python
"""What is `movement.train.centre.wheel.wheel` in mantel clock 34? Loads
and renders the model at instant 0; builds nothing, writes nothing. Run
from the 3DPrintedClocks checkout with PYTHONPATH=<bench>:<project>."""

from machinome.core.loader import load_node
from machinome.node.qualified import path_name

root = load_node('mantel_clock_34_steampunk')
root.set_keyframe(0)
root._prepare()
train = root.movement.train
for arbor_name in ('centre', 'third', 'fourth'):
    arbor = getattr(train, arbor_name)
    wheel = arbor.wheel
    print(f'{arbor_name}: {type(arbor).__name__}; wheel is '
          f'{type(wheel).__name__} rigid={wheel.rigid}; '
          f'path {path_name(wheel, root)!r}')
    inner = getattr(wheel, 'wheel', None)
    if inner is not None:
        print(f'    inner wheel: {type(inner).__name__} rigid={inner.rigid}; '
              f'path {path_name(inner, root)!r}')
```

### `<scratch>/thor_paths.py` (with 6.3's comparison)

```python
"""Thor: does the path the framework derives (`instance_path` below the
root) equal the path `simulation/seats.qualified_names()` builds by hand,
for every printed solid? Loads and renders the tree; builds nothing,
compares nothing, writes nothing. Run from the Thor checkout."""

import time

from machinome.core.loader import load_node
from machinome.node.qualified import instance_path

from simulation import seats

start = time.time()
root = load_node()
root.set_keyframe(0)
root._prepare()
print(f'loaded and rendered in {time.time() - start:.1f} s')

by_hand = seats.qualified_names(root)


def rigid_nodes(node):
    for child in getattr(node, 'children', ()) or ():
        if child.rigid:
            yield child
        else:
            yield from rigid_nodes(child)


solids = list(rigid_nodes(root))
derived = {id(solid): '.'.join(instance_path(solid, root)) for solid in solids}
differ = [(by_hand[key], derived[key]) for key in derived
          if by_hand.get(key) != derived[key]]
leaf_names = [solid.name for solid in solids]
repeated = sorted({name for name in leaf_names if leaf_names.count(name) > 1})
print(f'{len(solids)} printed solids; {len(by_hand)} named by hand; '
      f'{len(differ)} differ from instance_path')
for pair in differ[:10]:
    print('   differ:', pair)
print(f'{len(repeated)} leaf names repeat, e.g. {repeated[:6]}')
for key, path in derived.items():
    if path.endswith('gt2x40_pulley_1'):
        print('   ', path, '== by hand:', by_hand[key] == path)

try:
    from machinome.node.qualified import path_name
except ImportError:
    print('path_name: not on this tree')
else:
    printed = {id(solid): path_name(solid, root) for solid in solids}
    printed_differ = [(by_hand.get(key), printed[key]) for key in printed
                      if by_hand.get(key) != printed[key]]
    print(f'path_name: {len(printed)} solids; {len(printed_differ)} differ '
          f'from qualified_names()')
    for pair in printed_differ[:10]:
        print('   differ:', pair)
    for solid in solids:
        if solid.name == 'gt2x40_pulley_1':
            print('    path_name:', path_name(solid, root), '== by hand:',
                  by_hand[id(solid)] == path_name(solid, root))
```
