# Evidence: declare-controls-on-parts

Implemented in the framework worktree `solid-node/WTs/controls-on-parts`
(branch `controls-on-parts`, base `33d8bf5`, planning commit `25db9a2`)
on the workspace venv, `PYTHONPATH="$PWD"`, run from inside the worktree.

```
$ git rev-parse --show-toplevel
/home/asa/devel/libresolid-studio/solid-node/WTs/controls-on-parts
$ python -c "import solid_node; print(solid_node.__file__)"
/home/asa/devel/libresolid-studio/solid-node/WTs/controls-on-parts/solid_node/__init__.py
```

## 0.2 The base suite

Recorded on the planning commit `25db9a2` (the unchanged tree), before
any test or production change of this cycle:

```
$ python -m pytest -x -q
2513 passed, 5 skipped, 50 warnings, 1411 subtests passed in 338.35s (0:05:38)
```

Exit status 0. The 50 warnings are the pre-existing `FutureWarning`s of
the legacy `render()` fixtures; nothing fails at the base, so any failure
at task 8.4 is this cycle's.

## 0.3 The base per-tick cost

Task 4 moves `_values` and `_deltas` off `Run`. This is the number that
move is answerable to, from the run-owns-the-coordinates cycle's own
probe, on this worktree at the base:

```
$ python openspec/changes/archive/2026-09-13-run-owns-the-coordinates/evidence/probe_cost.py
running  Train   (record=None): 11.092 s for 10000 ticks = 1.109 ms/tick, tracemalloc peak 14.0 KiB, trajectory 0 entries
running  Train   (record=64) : 11.770 s for 10000 ticks = 1.177 ms/tick, tracemalloc peak 42.8 KiB, trajectory 64 entries
untimed  TrainBody           : 3.651 s for 10000 ticks = 0.365 ms/tick, tracemalloc peak 2739.5 KiB, trajectory 10010 entries
ratio running/untimed per tick: 3.04x
```

## 0.4 The base RUNNING document

`tests/base_documents/running_train.json` is the document
`tests.running_project.machine:Train` publishes at the base, written by
`tests/test_running_document.py`'s own `document()` helper with `mtime`
normalized exactly as `ByteIdentityTest.normalized` does. A version 5
document with no controls must come back byte-identical at task 7.2, and
a capture taken after the change would prove nothing.

```
captured at    25db9a2 (the planning commit, unchanged tree)
bytes          5550
sha256         ff71878ae84d3e04107d1d9b70e8a16adab13c025a6fa6db6e7210f0ac7b60ec
version        5
top-level keys format, version, animation, drivers, instructions, program, root
```

It is left UNTRACKED in the working tree: nothing is committed before the
reviewer's commit 2, and it is base evidence for the test that reads it.

## 0.5 The base corpus

```
$ sha256sum tests/running-corpus.json
8d5c450beaa574ac8bb798e516de2fd01a09193e5271f53b1dd7058041dbc86b  tests/running-corpus.json
```

The `program.identity` each committed corpus entry reports:

```
  Train              dt=0.05   steps=30   identity=2e6bc694e025b77c3a80210d59e399a6ce1ca033ea7bb998fc32945524eb1d1f
  Train              dt=0.1    steps=20   identity=2e6bc694e025b77c3a80210d59e399a6ce1ca033ea7bb998fc32945524eb1d1f
  Window             dt=0.05   steps=24   identity=9d98bb8bdb0d21782a7a6290d9aaa06056ae6647ee6969fb84bab83b33772292
  Remainder          dt=0.05   steps=24   identity=45df705c03fdbe69ab834e182321eda90a9575133f5cd9b1a3645900b1546d2a
  Wrapped            dt=0.05   steps=20   identity=b95215b439b27b59d3aa29cf487e3802dda50854e06c78fee6a4d50b2a3ec436
  Throwing           dt=0.05   steps=20   identity=d38ce5557cb163c53ff3f990ae3ab3223daae61e897496ff855f48caac35d040
  Clutch             dt=0.05   steps=24   identity=d5a6f9e866aacdf7dd392a81a128995016430bfac022023d28aceabd6ee17ea7
  CarryLead          dt=0.05   steps=24   identity=3836f48342eeaf1dec8132f9a143d359f0016f2c28784d2546b59f97fa8ff410
  CarryLead          dt=0.1    steps=14   identity=3836f48342eeaf1dec8132f9a143d359f0016f2c28784d2546b59f97fa8ff410
  Ratchet            dt=0.05   steps=20   identity=63e1af4025158eec39076b695d25df8a79636d8262979231bd98e7f3cac876a8
  Swept              dt=0.01   steps=16   identity=77f8ac022704ac73278f2783bec4207c2ce60323f6050e0f56b25b9171a84b46
  TwoStops           dt=0.05   steps=12   identity=81f06486452bb5b59031a905e8aa8edb292a7f99f72fd7f1f778ef00f3b2965c
  StopAndJump        dt=0.05   steps=12   identity=7699b735971ee59f55408cff21d86e1edc4b4f84cf49a8abf204482935110e4a
```

## 0.6 The design's load-bearing facts, probed

Two probes, kept beside this file with the manifest a fixture project
needs (`evidence/pyproject.toml`).

### (a) and (b): `evidence/probe_paths.py`

```
$ python openspec/changes/declare-controls-on-parts/evidence/probe_paths.py
(a) the part reference
    Columns.units.dial       -> <path units.dial>  type=PathRef
    isinstance PathRef       -> True
    .segments                -> ('dial',)
    .terminal                -> <declared Dial dial> (ChildDeclaration: True)
    _walk(instance)          -> <__main__.Dial object at 0x7c731463dd30>  type=Dial
    instance_path(leaf, root)-> ('units', 'dial')

(b) the point the joint turns about
    DialArbor.turn at=(0, 0, 0)
      arguments(node)[1]     -> (0.0, 0.0, 0.0)
      axes(node)             -> ((1, 0, 0),)
      carried_points(node,.) -> ((0.0, 0.0, 0.0),)
      placed operations      -> [['r', '-0.0', [1, 0, 0]]]
    OffCentreArbor.turn at=(0, 3, 0)
      arguments(node)[1]     -> (0.0, 3.0, 0.0)
      axes(node)             -> ((1, 0, 0),)
      carried_points(node,.) -> ((0.0, 3.0, 0.0),)
      placed operations      -> [['t', ['-0.0', '-3.0', '-0.0']], ['r', '-0.0', [1, 0, 0]], ['t', ['0.0', '3.0', '0.0']], ['t', ['50.0', '0.0', '0.0']]]

(b, published) the same two nodes as the document publishes them
    units  -> [['r', <ExpressionNode name 'units.turn'>, [1, 0, 0]]]
    off    -> [['t', ['-0.0', '-3.0', '-0.0']], ['r', <ExpressionNode name 'off.turn'>, [1, 0, 0]], ['t', ['0.0', '3.0', '0.0']], ['t', ['50.0', '0.0', '0.0']]]
```

(a) is design §2: a control's part is named in a class body exactly the
way a relation's path ends already are, resolves to the realized leaf,
and its instance path is the node-name path the document's tree
publishes.

(b) is design §8: the centred joint publishes `['r', <id>, [1, 0, 0]]`
and NOTHING else, so a consumer holding only `axis` would turn the drag
about the node's own origin — which is right here and wrong for the
off-centre joint, whose anchor reaches the document only as two
translations a consumer would have to recognize and subtract. `origin`
is therefore carried, and `arguments(node)[1]`/`carried_points` are
exactly the values `Joint.place` built the placement from.

### (c) and (d): `evidence/probe_response.py`

```
$ python openspec/changes/declare-controls-on-parts/evidence/probe_response.py
(c) response(rest, input, eps) vs move(input, by=eps, duration=0)
    Columns    tens_entry   ok both directions, 4 bank entries
    Columns    units_entry  ok both directions, 4 bank entries
    Carry      column       ok both directions, 4 bank entries
    Carry      tens_entry   ok both directions, 4 bank entries
    CarryLead  column       ok both directions, 4 bank entries
    CarryLead  tens_entry   ok both directions, 4 bank entries
    Ranged     crank        ok both directions, 2 bank entries
    Train      crank        ok both directions, 6 bank entries
    Train      lever        ok both directions, 6 bank entries
    VERDICT: bit-for-bit agreement = True

(c, continued) the reading the Pascaline shape earns
    units_entry: units.turn -3.4332275390625e-05  tens.turn 0.0
    tens_entry: units.turn 0.0  tens.turn 3.4332275390625e-05

(d) the displacement, on the affine chain units_entry -> units.turn
    eps=9.5367431640625e-07      raw=-3.4332275390625e-05     forward=-36.0                  backward=-36.0                  exact=True
    eps=0.001                    raw=-0.036000000000000004    forward=-36.0                  backward=-36.0                  exact=True
    eps=1e-06                    raw=-3.6e-05                 forward=-36.0                  backward=-36.0                  exact=True
    eps=9.313225746154785e-10    raw=-3.3527612686157227e-08  forward=-36.0                  backward=-36.0                  exact=True

    The RAW response at 1e-3 is -0.036000000000000004, exactly as
    design.md section 6 says; the DIVISION recovers -36.0 anyway on a
    chain of ONE edge. The power of two earns its keep on a chain of
    TWO, where the intermediate is rounded before the second factor
    multiplies it:
      -36.0 then -36.0, eps=0.001                  -> 1296.0000000000002     (exact product 1296.0)
      -36.0 then -36.0, eps=9.5367431640625e-07    -> 1296.0                 (exact product 1296.0)
      -36.0 then -1.5, eps=0.001                  -> 54.00000000000001      (exact product 54.0)
      -36.0 then -1.5, eps=9.5367431640625e-07    -> 54.0                   (exact product 54.0)
      -36.0 then 0.3, eps=0.001                  -> -10.8                  (exact product -10.799999999999999)
      -36.0 then 0.3, eps=9.5367431640625e-07    -> -10.799999999999999    (exact product -10.799999999999999)
```

(c) is design §6's whole claim and it holds bit for bit, on the
Pascaline-shaped fixture and on four committed running fixtures, over
every declared input and in both directions: the pure pass over
`edge.increments`, seeded with one input's displacement, commits exactly
what a fresh `Sim.move(input, by=eps, duration=0)` commits. The
measurement therefore never has to build a `Sim`, which is what keeps
`program_of`'s "publication leaves a live run's ownership intact"
promise.

(c, continued) is the fact the reviewer verified against the originating
project, reproduced here: under `carried_column`, `units_entry`'s
partial in `tens.turn` is exactly `0.0` at rest, so
`Turn(tens.dial, units_entry)` is §6's zero-at-rest refusal and NOT the
reaching refusal — `units_entry` genuinely reaches `tens.turn`.

**(d) does not reproduce as task 0.6(d) words it, and the deviation is
recorded under "Deviations" below.** The RAW response at `1e-3` reads
`-0.036000000000000004` as design §6 says, but the RATIO recovers
exactly `-36.0` at every displacement tried, because a one-edge chain
divides by the same number it multiplied by. The property design §6
actually relies on — that a power-of-two displacement makes the division
exact, so a COMPOSED ratio is the exact product rather than a rounded one
— is reproduced above on a two-edge chain, and is the reason `2**-20`
is kept.

## 0.7 `controls` is free to reserve

Design §2 makes `controls` a reserved class-body name. Nothing in the
workspace pays for the reservation:

```
$ grep -rn "controls *=" --include=*.py .        # the worktree, minus this change's own dir
(no matches)

$ grep -rn "controls *=" --include=*.py /home/asa/devel/libresolid-studio/projects/
projects/3DPrintedClocks/simulation/shared/test_ring_inventory.py:64:    controls = dict(defaults, rod_turns=0.25, upper_ring_nut_turns=0.5,
projects/3DPrintedClocks/cq_warehouse/drafting.py:359:            line_controls = [
projects/3DPrintedClocks/cq_warehouse/drafting.py:360:            line_controls = [
projects/Calculators/Curta-Type-I-3x/WTs/open-run-simulation/simulation/tools/open_run_selector.py:120:                negative_controls=negative)
```

Exactly one `controls =`, a LOCAL VARIABLE inside a clock test method;
the other three are different names (`line_controls`,
`negative_controls=`). No node class in the workspace declares
`controls`, exactly as design §2 claims.

## 2.0 The names do not exist yet

Probed on the unchanged tree, before any fixture was written (the names
are absent either way, and probing first keeps `machine.py` importable
so the probe fails for the RIGHT name):

```
from solid_node.simulation import Button
    AttributeError: module 'solid_node.simulation' has no attribute 'Button'
from solid_node.simulation import Turn
    AttributeError: module 'solid_node.simulation' has no attribute 'Turn'
import solid_node.simulation.control
    ModuleNotFoundError: No module named 'solid_node.simulation.control'
enumeration.qualified_controls
    AttributeError: module 'solid_node.simulation.enumeration' has no attribute 'qualified_controls'
enumeration.qualified_declarations
    AttributeError: module 'solid_node.simulation.enumeration' has no attribute 'qualified_declarations'
Program.controls
    AttributeError: 'Program' object has no attribute 'controls'
Program.response
    AttributeError: 'Program' object has no attribute 'response'
Program.values_of
    AttributeError: 'Program' object has no attribute 'values_of'
Program.deltas_of
    AttributeError: 'Program' object has no attribute 'deltas_of'
Program.published_controls
    AttributeError: 'Program' object has no attribute 'published_controls'
Sim.controls
    AttributeError: 'Sim' object has no attribute 'controls'
```

`Sim.controls` is probed for completeness. It becomes the enumeration
`Run.__init__` hands to `compile_program` (task 5.5) and nothing more:
reviewer decision 4 of 2026-09-14 is that this cycle adds no control API
to `Sim`, and every test reads `program.controls` and the published
table instead.

## 1. The fixtures

`tests/running_project/parts.py` gains `Dial`, a leaf with geometry and
no coordinate. `tests/running_project/machine.py` gains, under one
section header:

| Fixture | What it is for |
| --- | --- |
| `DialArbor` | the Pascaline's own shape: the joint at depth, the touchable leaf beneath it (1.2) |
| `Columns` | the acceptance vehicle (1.3): two drivers in `'digit'`, two `DialArbor`s, a leaf `frame` nothing moves, `units_entry.drives(units.turn, ratio=-36.0)`, `(tens_entry & units.turn).drives(tens.turn, law=carried_column)`, two `by=` instructions and the four controls |
| `ColumnsBare` | `Columns` minus the controls: the identity twin (2.5, 5.4) |
| `OffCentre` / `OffCentreArbor` | `Revolute(axis=(1,0,0), at=(0,3,0))`, the `origin` case (1.4, 5.2) |
| `SiteTurned` / `PlainDial` | the joint declared at the SITE, for the carry (5.3) |
| `DeepColumn` / `DeepArbor` / `DialHolder` | three deep, the middle assembly declaring nothing (2.3) |
| `ColumnStack` / `Column` | a child declaring its own driver, instruction and controls (2.2) |
| `Unposed`, `Sliding` / `SlideDial`, `Unreached`, `Unnamed`, `TwoJoints` / `TwoJointed`, `FreePosed` / `FreeDial`, `NotRunning`, `LoopingControls` | one per compile- or construction-time refusal (1.5) |
| `OmittedControl` / `OmittableArbor` | a `Flag` whose render omits the controlled part (1.6) |
| `Stepping` | an integer input with a scale, for the raised displacement (6.2) |
| `KinkedControl`, `SmoothControl` | a kink exactly at the rest value, and a smooth non-affine law, for the two-sided window (6.4) |

Every refusal that fires at CLASS DEFINITION is built inside the test
with a `class` statement under `assertRaises`, as the couplings suite
does: such a fixture cannot be a module-level class.

`OmittedControl` departed from the task's literal shape; see
"Deviations".

## 2. Red first — the declaration

The names did not exist (§2.0 above), so `tests/running_project/machine.py`
could not be imported at all:

```
$ python -c "import tests.running_project.machine"
ImportError: cannot import name 'Button' from 'solid_node.simulation'
```

That is a missing NAME, not a wrong ANSWER, so a SKELETON went in first
— `Button`/`Turn` accepting anything and checking nothing,
`qualified_controls` returning `{}`, `Program.controls = ()` — and every
case of `tests/test_controls.py` was run against it. **29 failed, 9
passed**, every failure a wrong answer:

```
E       AssertionError: Lists differ: [] != ['tens dial', 'turn tens', 'turn units', 'units dial']
E       AssertionError: Lists differ: [] != ['column.dial', 'column.turn']
E       KeyError: 'units dial'
E       KeyError: 'turn tens'
E       KeyError: 'turn units'
E       KeyError: 'column.dial'
E       KeyError: 'column.turn'
E       KeyError: 'turn deep'
E       AssertionError: TypeError not raised          (x 11: every class-definition refusal)
E       AssertionError: ValueError not raised         (x 6: every compile-time refusal)
```

```
FAILED DeclarationTest::test_the_trees_qualified_controls_are_the_four_declared
FAILED DeclarationTest::test_one_walk_returns_both_tables
FAILED DeclarationTest::test_each_compiled_control_names_its_part_and_its_gesture
FAILED DeclarationTest::test_a_button_names_a_declared_instruction
FAILED DeclarationTest::test_a_turn_names_the_input_the_author_declared
FAILED DeclarationTest::test_a_dial_two_inputs_reach_is_bound_to_the_one_named
FAILED QualificationTest::test_a_childs_control_takes_the_childs_path
FAILED QualificationTest::test_the_instruction_reference_qualifies_through_the_same_path
FAILED QualificationTest::test_the_input_qualifies_through_the_same_path
FAILED NearestJointTest::test_the_arbor_wins_over_the_root_and_the_dial
FAILED NearestJointTest::test_the_walk_passes_through_an_assembly_declaring_nothing
FAILED RefusalTest::test_a_controls_attribute_that_is_not_a_table_is_refused
FAILED RefusalTest::test_a_controls_attribute_that_is_not_a_mapping_is_refused
FAILED RefusalTest::test_a_part_that_is_not_a_node_is_refused_where_it_is_written
FAILED RefusalTest::test_a_coordinate_is_not_a_part
FAILED RefusalTest::test_a_joint_of_the_declaring_class_is_not_a_part
FAILED RefusalTest::test_a_driver_is_not_a_part
FAILED RefusalTest::test_a_repeated_child_names_one_part_per_copy
FAILED RefusalTest::test_a_misspelt_part_is_refused_where_it_is_written
FAILED RefusalTest::test_a_part_of_another_class_is_refused_at_class_definition
FAILED RefusalTest::test_an_input_of_another_class_is_refused
FAILED RefusalTest::test_an_input_named_by_a_string_is_refused
FAILED RefusalTest::test_a_button_naming_no_declared_instruction_is_refused
FAILED RefusalTest::test_a_part_nothing_run_owned_moves_is_refused
FAILED RefusalTest::test_a_turn_on_a_coordinate_that_does_not_turn_is_refused
FAILED RefusalTest::test_a_turn_whose_input_does_not_reach_the_part_is_refused
FAILED RefusalTest::test_a_node_declaring_two_joints_is_refused
FAILED RefusalTest::test_a_joint_owning_several_coordinates_is_refused
SUBFAILED(root='NotRunning')       RefusalTest::test_a_control_without_a_running_root_is_refused_at_construction
SUBFAILED(root='LoopingControls')  RefusalTest::test_a_control_without_a_running_root_is_refused_at_construction
29 failed, 9 passed in 1.62s
```

The nine that passed at the skeleton are the cases about what a control
must NOT change — the bank, the edges, the sources, the trajectory — and
they are the ones that would have gone red if the implementation had
touched the run.

## 3. The declaration, green

`solid_node/simulation/control.py` (new), `NodeMeta._validate_controls`,
`enumeration.qualified_declarations` with its two thin faces, the two
lazy exports, and `Sim.__init__`'s one walk plus its non-running
refusal.

Tasks 2.1–2.5 go green together with task 5, because 2.1, 2.3 and 2.4
assert on the COMPILED control, which task 5 creates: the declaration
alone cannot answer "its coordinate is `units.turn`". Recorded here
rather than pretended away; see "Deviations".

## 4. The arithmetic the ratio is measured with

Red first, the names absent:

```
E   AttributeError: 'Program' object has no attribute 'values_of'
E   AttributeError: 'Program' object has no attribute 'deltas_of'
E   AttributeError: 'Program' object has no attribute 'response'
21 failed, 3 passed, 36 deselected in 1.35s
```

`Run._values` and `Run._deltas` then moved to `Program.values_of` and
`Program.deltas_of` with `Run` delegating; `Run._pass` stayed on `Run`,
because it owns conflict detection and the messages a failed tick needs.

```
$ python -m pytest tests/test_controls.py -q -k ProgramArithmetic
4 passed, 36 deselected, 20 subtests passed in 1.25s
```

`test_response_reproduces_the_run_bit_for_bit` is 0.6(c) as a test, over
`Columns`, `Carry`, `CarryLead` and `Ranged`, every declared input, both
directions; `test_response_seeds_the_banks_own_units` pins the same
agreement for `Stepping`, whose bank is NATIVE, through
`Driver.native`.

### 4.3 The corpus and the cost after the move

```
$ python -m pytest tests/test_running_corpus.py -q
6 passed, 39 subtests passed in 1.23s

$ python openspec/changes/archive/2026-09-13-run-owns-the-coordinates/evidence/probe_cost.py
running  Train   (record=None): 11.282 s for 10000 ticks = 1.128 ms/tick, tracemalloc peak 14.0 KiB, trajectory 0 entries
running  Train   (record=64) : 11.950 s for 10000 ticks = 1.195 ms/tick, tracemalloc peak 43.0 KiB, trajectory 64 entries
untimed  TrainBody           : 3.841 s for 10000 ticks = 0.384 ms/tick, tracemalloc peak 2739.7 KiB, trajectory 10010 entries
ratio running/untimed per tick: 2.94x
```

Against the base (1.109 / 1.177 / 0.365 ms per tick): the running tick
rose 1.7% and the UNTIMED control — which this cycle does not touch at
all — rose 5.2% on the same machine in the same session, so the move is
inside the bench's own noise. The ratio fell, 3.04x to 2.94x.

## 5. Compiling a control

Red first against the declaration-only tree (the compiled record absent):

```
E       KeyError: 'turn units'
E       KeyError: 'turn tens'
E       KeyError: 'turn deep'
E       KeyError: 'column.dial'
SUBFAILED(control='turn units') GestureGeometryTest::test_a_centred_joint_turns_about_its_own_origin
SUBFAILED(control='units dial') GestureGeometryTest::test_an_off_centre_joint_publishes_the_point_it_turns_about
FAILED GestureGeometryTest::test_a_site_declared_joint_publishes_the_carried_values
20 failed, 23 passed, 4 deselected, 2 subtests passed in 1.49s
```

`compile_program` gained `controls` and `instructions`, and
`Program.controls` is the ordered tuple of `_Control` records. The
geometry is asserted against `joint.axes(node)` and
`joint.carried_points(node, anchor)` with the site carry applied, never
against the published operations, so an entry cannot drift from the
placement it describes.

## 6. The ratio

Red first, the name absent:

```
E   AttributeError: 'Program' object has no attribute 'published_controls'. Did you mean: 'published_names'?
7 failed, 9 passed, 34 deselected, 4 subtests passed in 1.22s
```

Green after `Program.published_controls` and `_per_unit`:

- `turn units` reads exactly `-36.0` and `turn tens` exactly `36.0` on
  `Columns` — asserted with `assertEqual`, not `assertAlmostEqual`, so
  the power-of-two displacement is pinned by the test;
- `Stepping` (`Driver(default=0, dtype=int, scale=0.0125, unit='mm')`)
  reads exactly `-2880.0`, and the test first shows that the naive
  displacement moves the part not at all;
- `Unmoved` is refused, and the test first shows that `units_entry` DOES
  reach `tens.turn` — reaching is necessary and not sufficient;
- `KinkedControl` is refused naming `5.0` and `-5.0`, while
  `SmoothControl`'s two readings differ by more than the program's
  `1e-9` agreement and less than the control window's `1e-3`, which is
  what pins the choice of window.

## 7. The document

Red first (the table absent, the key absent, the refusal absent):

```
FAILED ControlsTableTest::test_the_table_sits_beside_the_instructions
FAILED ControlsTableTest::test_each_entrys_fields_are_in_the_specs_order
FAILED ControlsTableTest::test_a_button_names_a_key_of_its_own_instructions_table
FAILED ControlsTableTest::test_a_turn_names_a_key_of_its_own_drivers_table
FAILED ControlsTableTest::test_every_coordinate_is_a_key_of_the_program
FAILED ControlsTableTest::test_the_part_and_joint_paths_resolve_by_walking_the_tree
FAILED ControlsTableTest::test_the_geometry_is_the_joints_own
FAILED ControlsTableTest::test_an_off_centre_joint_publishes_the_point_it_turns_about
FAILED ControlsTableTest::test_a_control_under_a_non_running_root_is_refused_at_publication
FAILED ControlsTableTest::test_an_omitted_part_drops_its_control
FAILED ControlsTableTest::test_no_control_expression_enters_the_binding_pass
SUBFAILED(producer='built')    ControlsTableTest::test_both_producers_publish_the_table
SUBFAILED(producer='exported') ControlsTableTest::test_both_producers_publish_the_table
SUBFAILED(key='edges')         ControlsTableTest::test_the_program_is_unchanged_by_the_presence_of_a_control
14 failed, 7 passed, 43 deselected, 2 warnings, 15 subtests passed in 3.95s
```

`ByteIdentityTest` was among the seven that passed, `running_train`
included: at that point nothing had been published, which is exactly the
"absent when empty" half being true before the table existed. It stays
green after `document_body` learns the argument, which is the half that
matters.

Green after `serializer.document_body` gained its keyword-only
`controls`, `serializer.compiled_controls` was added beside
`compiled_program`, `symbolic_document`'s `collect` learned the
non-running refusal, and `core/builder.py` and `core/export.py` passed
the table:

```
$ python -m pytest tests/test_running_document.py tests/test_controls.py -q
113 passed, 2 warnings, 111 subtests passed in 7.80s
```

### 7.1 The table `Columns` publishes

The Pascaline module's own tree shape, published:

```json
{
  "controls": {
    "tens dial": {
      "kind": "button",
      "part": [
        "tens",
        "dial"
      ],
      "instruction": "Add ten",
      "joint": [
        "tens"
      ],
      "coordinate": "tens.turn",
      "axis": [
        1.0,
        0.0,
        0.0
      ],
      "origin": [
        0.0,
        0.0,
        0.0
      ]
    },
    "turn tens": {
      "kind": "turn",
      "part": [
        "tens",
        "dial"
      ],
      "input": "tens_entry",
      "per_unit": 36.0,
      "joint": [
        "tens"
      ],
      "coordinate": "tens.turn",
      "axis": [
        1.0,
        0.0,
        0.0
      ],
      "origin": [
        0.0,
        0.0,
        0.0
      ]
    },
    "turn units": {
      "kind": "turn",
      "part": [
        "units",
        "dial"
      ],
      "input": "units_entry",
      "per_unit": -36.0,
      "joint": [
        "units"
      ],
      "coordinate": "units.turn",
      "axis": [
        1.0,
        0.0,
        0.0
      ],
      "origin": [
        0.0,
        0.0,
        0.0
      ]
    },
    "units dial": {
      "kind": "button",
      "part": [
        "units",
        "dial"
      ],
      "instruction": "Add one",
      "joint": [
        "units"
      ],
      "coordinate": "units.turn",
      "axis": [
        1.0,
        0.0,
        0.0
      ],
      "origin": [
        0.0,
        0.0,
        0.0
      ]
    }
  }
}
```

`OffCentre`'s `turn units` publishes `"origin": [0.0, 3.0, 0.0]` with
the same `[1.0, 0.0, 0.0]` axis — the point the placement turns the part
about, which no consumer could recover from the node's world matrix.

`SiteTurned`'s `turn holder` is the carry: the SITE wrote
`Revolute(axis=(0, 0, 1), at=(0, 6, 0))` in the parent's frame, and the
child is placed `rotate(90, [1, 0, 0])` then `translate([0, 20, 0])`.
The entry publishes `"axis": [0.0, 1.0, 0.0]` and
`"origin": [0.0, 0.0, 14.0]` — exactly what `_carry` gave `place`, and
neither of the numbers the site wrote.

### 7.6 The baked capture

`solid_node/viewers/browser.py` is **unchanged**: it already passes no
controls, which is what design §9 asks for. The test is therefore green
on arrival, exactly as the neighbouring
`test_the_staged_document_carries_no_bindings_key` is. It was
MUTATION-CHECKED to prove it discriminates — make the capture pass
`compiled_controls(program, initial)` and it fails:

```
FAILED tests/test_browser_renderer.py::UnreadableDocumentRefusalTest::test_a_baked_capture_publishes_no_controls
1 failed, 22 deselected in 1.61s
```

and with `browser.py` put back (byte-identical, `git diff` empty):

```
1 passed, 22 deselected in 1.53s
```

## 8. The things that must not move

```
$ python -m pytest tests/test_running_document.py tests/test_running_simulation.py \
    tests/test_running_jumps.py tests/test_running_stops.py tests/test_export.py \
    tests/test_build_publication.py tests/test_couplings.py tests/test_joints.py \
    tests/test_declarative_nodes.py -q
645 passed, 1 skipped, 8 warnings, 896 subtests passed in 39.13s

$ python -m pytest tests/test_cli_lazy_imports.py tests/test_node_lazy_exports.py \
    tests/test_lazy_test_framework.py -q
79 passed, 170 subtests passed in 66.94s
```

The lazy-export guard's `EXPECTED_EXPORTS` table gained `Button` and
`Turn` (mapped to `solid_node.simulation.control`) and its
"importing the package imports no submodule" list gained `control` —
that table is written out by hand on purpose, so adding a name to it is
the guard working. `NodeLayerImportsNothingOfTheSimulationTest` is task
8.2's direct assertion: an `ast` walk over
`solid_node/node/declarative.py` finds no `solid_node.simulation` import,
and a probe importing that module in a fresh interpreter loads none of
`control`, `driver`, `program`, `run` or `sim`.

### 8.3 The corpus

```
$ PYTHONPATH="$PWD" python tools/generate_running_corpus.py
tests/running-corpus.json: 13 scenarios over 11 machines (CarryLead, Clutch, Ratchet,
Remainder, StopAndJump, Swept, Throwing, Train, TwoStops, Window, Wrapped),
260 ticks, 170449 bytes

$ git diff --stat tests/running-corpus.json
(no output)

$ sha256sum tests/running-corpus.json
8d5c450beaa574ac8bb798e516de2fd01a09193e5271f53b1dd7058041dbc86b  tests/running-corpus.json

$ python -m pytest tests/test_running_corpus.py -q
6 passed, 39 subtests passed in 1.39s
```

Byte-identical to the committed file, and the digest is 0.5's exactly. No
corpus machine gained a control and the coverage guard is untouched.

### 8.4 The full suite

```
$ python -m pytest -x -q
2593 passed, 5 skipped, 50 warnings, 1481 subtests passed in 310.87s (0:05:10)
```

Exit status 0, beside the base's
`2513 passed, 5 skipped, 50 warnings, 1411 subtests passed`.

**+80 tests**, every one added by this cycle:

| Where | Tests |
| --- | --- |
| `tests/test_controls.py` (new) | 57 |
| `tests/test_running_document.py` — `ControlsTableTest` (new) | 20 |
| `tests/test_lazy_test_framework.py` — `NodeLayerImportsNothingOfTheSimulationTest` (new) | 2 |
| `tests/test_browser_renderer.py` — `test_a_baked_capture_publishes_no_controls` | 1 |

**+70 subtests**, all in those tests or in the guards this cycle had to
extend:

| Where | Subtests |
| --- | --- |
| `tests/test_controls.py` | 33 |
| `ControlsTableTest` | 24 |
| `NodeLayerImportsNothingOfTheSimulationTest` | 5 |
| `ByteIdentityTest` — the `running_train` tree | +1 |
| `test_importing_the_package_imports_no_submodule` — `control` | +1 |
| `SimulationPackageExports`' three table-driven tests — `Button` and `Turn` in `EXPECTED_EXPORTS` | +6 |

**Skips unchanged at 5** and **warnings unchanged at 50**: no test was
removed, disabled or renamed out of the run, and this cycle introduced
no new deprecation. One test was RENAMED in place —
`ByteIdentityTest.test_every_untimed_document_is_unchanged_in_every_byte`
to `..._every_document_with_no_control_...` — which is why the count of
that class is unchanged while its subtests rose by one.

## 9. Documentation

- `docs/driving.rst`: a "Controls: pressing and turning the part itself"
  section immediately after "Instructions", with a `controls-on-parts`
  label — both spellings, the part named the way a relation's path ends
  are, the ratio derived and measured at rest with its caveat, every
  refusal and where it fires, the additive table, and the plain
  statement that the viewer behaviour is the viewer's own release.
- `docs/scenarios.rst`: one cross-reference from "What a running root
  publishes".
- `docs/api-reference.rst`: `Button` and `Turn` beside `Instruction`.
- `docs/changelog.rst`: the Unreleased entry, first.
- `docs/architecture.md`: one paragraph in Simulation (the declaration,
  where it is validated, that the node layer still imports nothing of
  the simulation layer, and that `described()` never learns of a
  control) and one in Export (the table, its fields, additivity, and
  which producers publish it).

```
$ python -m pytest tests/test_docs_exports.py -q
8 passed, 26 subtests passed in 0.38s

$ python -m sphinx -b html -q docs <tmp>
```

The Sphinx build emits the same six pre-existing warnings it emits at
the base — two short title underlines (`docs/animation.rst:255`,
`docs/api-reference.rst:405`), one title overline mismatch
(`docs/api-reference.rst:471`), one docstring markup warning in
`joints.py`'s `Orbit`, and two missing example export directories — and
none in anything this cycle wrote. Both pre-existing `api-reference.rst`
warnings were confirmed present at `HEAD` before the edit.

## Every refusal, verbatim

Collected by a probe over each fixture; one line of code produces each.
A name a class body has assigned is reported by that name even while the
body is still running (`couplings._named_in_body`), so a message says
`bank` rather than a list repr.

```
CLASS DEFINITION: controls is not a mapping [TypeError]
Listed.controls is ['units']. On a node class `controls` names the machine's CONTROLS -- a mapping of display name to Button(part, instruction) or Turn(part, input), beside `instructions` -- so the name is reserved; rename the attribute.

CLASS DEFINITION: an entry is not a control [TypeError]
Mistyped.controls['speed'] is 3, which is not a control. On a node class `controls` names the machine's CONTROLS -- Button(part, instruction) or Turn(part, input) -- so the name is reserved; rename the attribute.

CONSTRUCTOR: a plain value as a part [TypeError]
a Button names a PART: a child the declaring assembly holds, or a path of declared children through one (units.input.dial). 3.0 is none of those.

CONSTRUCTOR: a coordinate as a part [TypeError]
a Turn names a PART -- a node whose geometry a hand touches -- not a coordinate, and 'units.turn' names one. A control's gesture is about the coordinate the part RIDES, which the framework finds from the tree: name the body that moves.

CONSTRUCTOR: a driver as a part [TypeError]
a Turn names a PART -- a node whose geometry a hand touches -- and 'entry' is a Driver, which is an INPUT: a value the run advances, with no geometry to touch.

CONSTRUCTOR: a whole list of children as a part [TypeError]
a Button names ONE part, and 'bank' holds 2 children, each with its own arguments -- named 'bank-0', 'bank-1', and so on. Name one child by its own attribute.

CLASS DEFINITION: one entry of a list-held child as a part [TypeError]
the control 'press bank' of Listed names a part held in a LIST. A declaration held in a list is named <attribute>-<index> and names one child per entry, so it cannot be a control's part. Hold the DialArbor on its own attribute, or state the control inside it.

CONSTRUCTOR: a repeated child as a part [TypeError]
a Button names ONE part, and 'bank' is a repeated declaration of DialArbor (count=3): a repeated child names one part per copy. Name one copy's own attribute, or state the control inside DialArbor.

CONSTRUCTOR: an input named by a string [TypeError]
a Turn names its input by its DECLARATION -- the `Driver(...)` the class body assigns -- not by the string 'entry'. A driver is addressed by the qualified id its position in the tree gives it, and a second address for one value is what that qualification prevents.

read_through (unchanged, and reached by a control's path): a misspelt segment [SidewaysReadError]
'units.dail' names nothing: DialArbor declares no port, joint or child called 'dail'. A path reference is checked against the classes where it is written, so this is a misspelling, not a runtime surprise. DialArbor declares: dial, turn.

CLASS DEFINITION: a part of another class [TypeError]
Borrower: 'other', the first segment of other.dial in the control 'units dial', is not a child Borrower declares. A control's part is walked from the assembly that declares the control; Borrower declares: units.

CLASS DEFINITION: an input of another class [TypeError]
Foreign: the control 'turn units' turns units.dial with a Driver Foreign does not declare. A Turn's input is a driver of the class stating the control -- a child's driver is named by declaring the control on the child -- and Foreign declares: entry.

COMPILE: a button naming no declared instruction [ControlError]
the control 'units dial' is a button for the instruction 'Add two', which nothing in this tree declares. A button references an instruction and never repeats its definition; the declared instructions are: Add one.

COMPILE: a part nothing run-owned moves [ControlError]
the control 'press frame' is on Block 'frame' (frame), and nothing the run owns moves that part: no ancestor of it, and not the part itself, declares a joint whose coordinate the run banks. A control's gesture is a joint's motion -- a part posed by a plain port an author's own render() turns is not one.

COMPILE: a Turn over a translational coordinate [ControlError]
the control 'turn carriage' is a Turn on the coordinate 'carriage.travel', whose domain is 'translational' and not 'rotational'. A turn is a drag about a rotational coordinate; Slide, for a prismatic one, is not in this release.

COMPILE: a Turn whose input does not reach the coordinate [ControlError]
the control 'turn units' turns the coordinate 'units.turn' with the input 'tens_entry', which does not reach it through the compiled program. The inputs that DO reach 'units.turn' are: units_entry.

COMPILE: a posing node declaring two joints [ControlError]
the control 'turn stack' is on a part posed by TwoJointed 'stack', which declares 2 joints -- swing, lift -- that compose one motion between them. A control names ONE coordinate, and neither of those is it. Declare the control on a part posed by a single joint.

COMPILE: a joint owning several coordinates [ControlError]
the control 'turn floating' is on a part posed by the joint 'pose' of FreeDial 'floating', which owns 6 coordinates -- pose.roll, pose.pitch, pose.yaw, pose.x, pose.y, pose.z. A control names ONE coordinate, and a free body's six are not one gesture.

CONSTRUCTION and PUBLICATION: a control under a non-running root [TypeError]
NotRunning declares the control 'units dial', and NotRunning declares no running time base. A control is how a person issues a movement request, and only a running simulation takes one: declare time = Time.running() on the root, or drop the control.

CONSTRUCTION: the same, under a looping root [TypeError]
LoopingControls declares the control 'units dial', and LoopingControls declares no running time base. A control is how a person issues a movement request, and only a running simulation takes one: declare time = Time.running() on the root, or drop the control.

PUBLICATION: the part does not move with that input at rest [ControlError]
the control 'turn tens' turns tens.dial with the input 'units_entry', and at the rest bank that part does not move with that input at all: displacing 'units_entry' moves the coordinate 'tens.turn' by nothing in either direction. Reaching a coordinate through the program is necessary and not sufficient -- an input coupled only through a law that is disengaged at rest reaches it and moves it not at all -- so there is no scale for the gesture.

PUBLICATION: the two directions disagree [ControlError]
the control 'turn units' turns the coordinate 'units.turn' with the input 'crank', and the two directions do not agree at the rest bank: forward reads 5.0 and backward -5.0 coordinate units per design unit. A law whose response at rest is not one number gives the gesture no single scale, and a drag scaled by one of them would be wrong in the other direction. A law that merely CURVES agrees well inside the window of 0.001 relative; this is a kink, a jump or a one-way law at the value the part rests at.
```

## Deviations

Each preserves the specs' observable behaviour; each is here because a
task or a design sentence says something slightly different.

1. **Task 0.6(d) is not reproducible as worded**, and §0.6 above says so
   with the reading that is. The RAW response at `1e-3` is
   `-0.036000000000000004` exactly as design §6 states, but the RATIO
   recovers `-36.0` at every displacement tried, because a chain of ONE
   edge divides by the same number it multiplied by. The property §6
   actually rests on — a power-of-two displacement makes the division
   exact, so a COMPOSED ratio is the exact product — is reproduced on a
   two-edge chain (`-36 then -36` reads `1296.0000000000002` at `1e-3`
   and `1296.0` at `2**-20`). `2**-20` is kept for that reason.

2. **Tasks 2.5 and 5.4 ask for "the same `program.identity`" against a
   control-free twin, and two classes cannot have one.**
   `Program.described()`'s FIRST LINE is
   `root <module>.<qualname>`, so `ColumnsBare` necessarily hashes
   differently from `Columns`. The test aligns that one line and asserts
   the digests are then equal, and asserts separately that every line
   after the first is identical, that `described()` mentions no control,
   and that the two step identically. The document-level test does the
   same for each published edge's `stated_by`, which is the same class
   name published per edge. Nothing weaker than the task intends is
   asserted; the class name is simply not a control.

3. **`Program.response` seeds the BANK's units, not design units.**
   Design §6 words the displacement as design units. The bank of a
   scaled or integer driver is NATIVE — `sim.move('feed', by=0.0125)`
   on `Stepping` moves the bank entry by `1` — so `response` takes a
   native displacement and `_per_unit` divides by what that displacement
   is worth in design units. The published behaviour is exactly what §6
   and the export spec state: `per_unit` is coordinate units per DESIGN
   unit, and an integer input is measured over one native unit. The
   units contract is pinned by `test_response_seeds_the_banks_own_units`,
   which converts through `Driver.native` and reproduces `move` bit for
   bit for `Stepping` too.

4. **Tasks 2.1–2.5 go green at task 5.5, not at 3.6.** 2.1, 2.3 and 2.4
   assert on the COMPILED control — its coordinate, its joint path, its
   axis, its origin, and the compile-time refusals — which task 5
   creates. The declaration alone cannot answer them. Task 3.6's own
   counts are therefore task 5.5's counts.

5. **`OmittedControl` omits the PART, not the node carrying the driven
   coordinate.** Written first as a `Flag` omitting a whole `DialArbor`,
   which the framework refuses to publish for a reason that has nothing
   to do with controls: the relation onto the omitted child is still
   compiled and its driven end takes the `<ClassName>.<name>` fallback,
   which `Program.published()` refuses. Recorded as a framework wart
   (`workflow/warts.md`, "declare-controls-on-parts") with a
   control-free reproduction. The fixture now gives the arbor a `Flag`
   and omits its DIAL — "the controlled part", which is what task 1.6
   says and what design §10's own picture (a control on a lid) is.

6. **`document_body`'s `controls` is a keyword parameter at the end of
   the signature.** The KEY is written immediately after `instructions`
   and before `bindings`, as task 7.7 requires. The PARAMETER is last
   because `viewers/browser.py` calls `document_body` positionally, and
   inserting a positional parameter beside `instructions` would have
   silently changed that call.

7. **`solid_node/viewers/browser.py` is unchanged.** The proposal's
   Impact lists it; design §9 says it passes no controls, which it
   already does, so there was nothing to edit. `git diff` on it is
   empty. Task 7.6's test is therefore green on arrival — exactly as the
   neighbouring `test_the_staged_document_carries_no_bindings_key` is,
   and for the reason that test states — and was mutation-checked
   instead (§7.6 above).

8. **`ControlError` is not exported from `solid_node.simulation`.** It
   is a `ValueError` subclass in `simulation/control.py`, importable
   from there. Neither delta spec names an error class, and
   `simulation/__init__.py`'s `_EXPORTS` is documented as "the whole
   public surface of the package", so adding a name to it would be a
   public-surface change this cycle was not asked for.

9. **`simulation/control.py` imports three private helpers from
   `motion/couplings.py`** — `_coordinate_of`, `_coordinates_of` and
   `_is_declaration_list`. `couplings` restates `_coordinate_of` rather
   than importing it only to avoid an import cycle, which does not exist
   here (the simulation layer imports the motion layer freely). One
   implementation of "is this a coordinate" is the point; a second would
   be a second thing to keep in step.

10. **Two refusals the `simulation` delta does not enumerate** are
    raised in the constructors, as narrowings of ones it does: a `Turn`
    whose `input` is a STRING (the delta says an input "SHALL be a
    `Driver` declared on the class"; the string case gets its own
    message naming the qualification rule it would reopen), and a
    `Button` whose instruction is not a string. Both are additions to
    the refusal set, not changes to any stated behaviour.

11. **`tests/test_running_document.py`'s `document()` helper gained the
    `controls` argument** so the shared helper matches the two
    producers, and `ByteIdentityTest`'s method was RENAMED from
    `test_every_untimed_document_is_unchanged_in_every_byte` to
    `test_every_document_with_no_control_is_unchanged_in_every_byte`,
    because its `trees` now includes a running one.
