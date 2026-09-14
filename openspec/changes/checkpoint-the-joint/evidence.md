# Evidence: the runner's checkpoint against a joint's placement

Everything below was measured on this worktree (`fix-warts`, at `9181f23`)
with the workspace venv, before any implementation. No framework file was
changed to produce it.

## The fixture

`evidence/bench/` is a real Solid project (`pyproject.toml` declaring
`model = "machine:Bench"`), and it is the smallest tree that carries the
finding:

- `Bench` — a root declaring `time = Time.running()`, two drivers;
- `slide` — a ROOT-LEVEL LEAF (`Solid2Node`) owning a `Prismatic`, driven by
  the `push` driver, and placed by the root's `render()`;
- `arm.slide` — the identical leaf one level down, inside the `Arm`
  sub-assembly;
- `floater` — a root-level leaf owning a `Free`, whose one binding places
  SEVERAL operations;
- `BenchBody` — the identical tree with NO time base: the untimed control,
  which `Bench` subclasses.

Revision 1 adds three more untimed machines beside it in
`evidence/bench/conditional.py`; they are described in the Revision 1
section below.

Two probes read it:

- `evidence/probe_checkpoint.py` — the checkpoint sequence step by step. It
  takes `save_children_checkpoints` and `restore_children_checkpoints`
  UNCHANGED off `solid_node.manager.test.Test`; everything else is public
  API. Sections 1-6 below are its output.
- `evidence/probe_lock.py` — the wart's own reproduction, verbatim, on the
  originating project. Section 8.

Section 7 is a real `solid test` run over the fixture and its companion
(`evidence/bench/test_machine.py`).

How each was run:

```
cd openspec/changes/checkpoint-the-joint/evidence/bench
PYTHONPATH="<worktree>:$PWD" <venv>/bin/python ../probe_checkpoint.py
PYTHONPATH="<worktree>:$PWD" <venv>/bin/solid test machine.py

cd <projects>/Locks/Pin_tumbler_lock
PYTHONPATH="<worktree>" <venv>/bin/python <change>/evidence/probe_lock.py
```

(`<worktree>` is `/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts`,
`<venv>/bin` is `/home/asa/devel/libresolid-studio/.venv/bin`. Running the
probe or `solid test` creates `evidence/bench/_build/` and
`evidence/bench/_build.lock` beside the fixture's `pyproject.toml`; they are
build output, not part of the change.)

Each line reads: the step, the number of operations the leaf carries, the
value its coordinate holds, and every MOTION operation as
`(serialized, _joint_slot, tagged|untagged)` — `tagged` meaning the operation
carries an `_animator`, which is what `_sweep` removes by.

## 1. A running root: the checkpoint DOUBLES a root-level leaf's placement

```
=== 1. A running root: the checkpoint doubles a root-level leaf's joint displacement
    built: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    a scenario has stepped the run: 2 operations, coordinate travel=12.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged')]
    test 1: a second scenario binds the bank: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
    test 1: the runner restores: 2 operations, coordinate travel=0.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged')]
    test 2: a third scenario binds the bank: 3 operations, coordinate travel=0.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged'), (['t', ['0.0', '0', '0']], 0, 'untagged')]
    test 2: the runner restores: 2 operations, coordinate travel=0.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged')]
    test 3: a fourth scenario binds the bank: 3 operations, coordinate travel=0.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged'), (['t', ['0.0', '0', '0']], 0, 'untagged')]
```

Step by step, with the operation objects named:

1. The build places `B` through the root's simulate phase: motion, slot 0,
   TAGGED with the root assembly, and recorded in
   `slide.__dict__['_joint_motion']['travel']`.
2. A scenario's `Sim` binds the bank through `set_state`, so
   `CoordinateDelivery` → `set_coordinate` → `Joint.place` runs with NO
   phase current: `clear` drops `B` (it is still the recorded object) and
   `apply_joint_motion` inserts `O1` — motion, slot 0, UNTAGGED. Record:
   `[O1]`.
3. The runner saves the checkpoint HERE, so the snapshot holds `O1`.
4. The next scenario's `Sim` places again: `clear` drops `O1` (recorded and
   present), inserts `O2`. Record: `[O2]`. One operation, still right.
5. The runner restores BY CONTENT: `O1` is back in the list. The record
   still says `[O2]` — the record is now stale, and nothing else can reach
   `O1`: it is untagged, so `_sweep` does not see it.
6. The next `Sim` places again: `clear` looks for `O2`, which is not in the
   list, and removes NOTHING; `apply_joint_motion` inserts `O3` beside `O1`.
   **Two translations, 12.0 and 0.0, for one coordinate reading 0.0.** The
   leaf stands 12 mm from where the machine is.

From step 6 on the state is fixed: every later restore/place pair reproduces
it (tests 2 and 3 above are identical).

## 2. The same tree's SUB-ASSEMBLY leaf, unaffected

```
=== 2. The same tree's SUB-ASSEMBLY leaf, through the same steps
    arm.slide: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
```

`arm.slide` owns the same joint, driven by the same driver, and went through
the same six steps — one operation, agreeing with its coordinate. The runner
checkpoints `node.children`, the ROOT's own children
(`save_children_checkpoints`, `solid_node/manager/test.py:385`), and
`arm.slide` is not one of them, so nothing ever replaced its list.

## 3. A `Free`: several operations for one placement, doubled as a unit

```
=== 3. A Free joint on a root-level leaf: several operations, one placement
    a scenario has stepped the run: 5 operations, motion=[(['r', '12.0', [1, 0, 0]], 0, 'untagged'), (['r', '-6.0', [0, 1, 0]], 0, 'untagged'), (['r', '18.0', [0, 0, 1]], 0, 'untagged'), (['t', ['3.0', '1.5', '6.0']], 0, 'untagged')]
    test 1: a second scenario binds the bank: 5 operations, motion=[(['r', '0.0', [1, 0, 0]], 0, 'untagged'), (['r', '-0.0', [0, 1, 0]], 0, 'untagged'), (['r', '0.0', [0, 0, 1]], 0, 'untagged'), (['t', ['0.0', '0.0', '0.0']], 0, 'untagged')]
    test 2: a third scenario binds the bank: 9 operations, motion=[(['r', '12.0', [1, 0, 0]], 0, 'untagged'), (['r', '-6.0', [0, 1, 0]], 0, 'untagged'), (['r', '18.0', [0, 0, 1]], 0, 'untagged'), (['t', ['3.0', '1.5', '6.0']], 0, 'untagged'), (['r', '0.0', [1, 0, 0]], 0, 'untagged'), (['r', '-0.0', [0, 1, 0]], 0, 'untagged'), (['r', '0.0', [0, 0, 1]], 0, 'untagged'), (['t', ['0.0', '0.0', '0.0']], 0, 'untagged')]
```

A `Free` places FOUR operations for one binding (three rotations and one
translation), and every one of them carries the SAME `_joint_slot` (`0`
above). The defect therefore duplicates the whole run: four operations become
eight, an entire spurious attitude and translation composed onto the body.
A fix that removes a placement by its mark removes all four as a unit; one
that removes operations one recorded object at a time has four chances to be
wrong instead of one.

## 4. The UNTIMED control: unaffected under a keyframe-only test

```
=== 4. The UNTIMED control: the same steps, no run to bind the bank
    built: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 1: after set_keyframe(0): 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 1: the runner restores: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 2: after set_keyframe(0): 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 2: the runner restores: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 3: after set_keyframe(0): 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    test 3: the runner restores: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
```

WHY it is unaffected: under `BenchBody` every joint coordinate is bound by
the relation the enumeration solves, INSIDE the root's simulate phase, so
every placement is TAGGED. `_sweep` (`solid_node/node/assembly.py:16`)
removes by animator identity, "regardless of which operation OBJECT currently
sits in the list", so a wholesale restore cannot strand one: the next render
drops whatever the restore put back and places afresh. The stale record in
`_joint_motion` is harmless because it is not the only handle.

## 5. A running root the runner NEVER checkpoints: unaffected

```
=== 5. A running root the runner NEVER checkpoints
    a scenario has stepped the run: 2 operations, coordinate travel=12.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged')]
    scenario 2: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
    scenario 3: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
    scenario 4: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
```

The same root, the same four `Sim` constructions, with the checkpoint pair
never called: one operation throughout, always agreeing with the coordinate.
The defect belongs to the checkpoint, not to the run.

## 6. An UNTIMED root IS affected when a test binds a coordinate BY HAND

```
=== 6. An UNTIMED root whose test binds a coordinate BY HAND (the one out-of-phase placement an untimed tree has)
    built: 2 operations, coordinate travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    a test binds the coordinate by hand: 2 operations, coordinate travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 1: bound by hand again: 2 operations, coordinate travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 2: bound by hand again: 3 operations, coordinate travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged'), (['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 2: after the next set_keyframe(0): 3 operations, coordinate travel=0.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged'), (['t', ['0.0', '0', '0']], 0, 'tagged')]
```

This CORRECTS the wart, which reports the untimed model as showing the defect
"not at all". What is actually untimed-specific is only the FREQUENCY of an
out-of-phase placement: a running root makes one on every tick
(`Run.bind`, `solid_node/simulation/run.py:348`), an untimed tree only when
something binds a coordinate outside a simulate phase — which a test doing
`node.slide.travel = 7.0` does. The same restore then strands the same
operation, the body carries 14 mm of travel for a coordinate reading 7.0, and
the last line shows the stranded operation SURVIVING the next
`set_keyframe(0)` (it is untagged, so the sweep cannot see it, and the record
no longer names it): 7.0 + 0.0, permanently, for a coordinate now reading 0.

## 7. `solid test` over the fixture: both faces, red

The companion (`evidence/bench/test_machine.py`) asserts one thing — that the
travel every motion operation on `slide` states adds up to the coordinate
`slide` holds. `BenchScenario` steps the run on the node the runner built and
handed over (`ScenarioTest.scenario_node`); `BenchGeometry` measures it
afterwards; `BenchAfterSetUpClass` is the shape of §1, reached through a
`setUpClass` that steps the run BEFORE the class's first checkpoint is taken.

```
Running BenchScenario.test_a_push
   scenario 1: slide.travel=12.0, placed=12.0, operations=[['t', ['12.0', '0', '0']], ['t', ['0.0', '0.0', '4.0']]]
. passed
Running BenchScenario.test_b_push_again
   scenario 2: slide.travel=8.0, placed=8.0, operations=[['t', ['8.0', '0', '0']], ['t', ['0.0', '0.0', '4.0']]]
. passed
Running BenchGeometry.test_a
   geometry A: slide.travel=8.0, placed=0.0, operations=[['t', ['0.0', '0.0', '4.0']]]
.FAIL!
AssertionError: 0.0 != 8.0 within 7 places (8.0 difference) : the leaf stands where its coordinate does not say

Running BenchGeometry.test_b
   geometry B: slide.travel=8.0, placed=0.0, operations=[['t', ['0.0', '0.0', '4.0']]]
.FAIL!
AssertionError: 0.0 != 8.0 within 7 places (8.0 difference) : the leaf stands where its coordinate does not say

Running BenchHandOver.test_a_hand_the_node_over. passed
Running BenchAfterSetUpClass.test_a
   after setUpClass A: slide.travel=0.0, placed=0.0, operations=[['t', ['0.0', '0', '0']], ['t', ['0.0', '0.0', '4.0']]]
. passed
Running BenchAfterSetUpClass.test_b
   after setUpClass B: slide.travel=0.0, placed=12.0, operations=[['t', ['12.0', '0', '0']], ['t', ['0.0', '0', '0']], ['t', ['0.0', '0.0', '4.0']]]
.FAIL!
AssertionError: 12.0 != 0.0 within 7 places (12.0 difference) : the leaf stands where its coordinate does not say

Running BenchAfterSetUpClass.test_c
   after setUpClass C: slide.travel=0.0, placed=12.0, operations=[['t', ['12.0', '0', '0']], ['t', ['0.0', '0', '0']], ['t', ['0.0', '0.0', '4.0']]]
.FAIL!
AssertionError: 12.0 != 0.0 within 7 places (12.0 difference) : the leaf stands where its coordinate does not say


Ran 8 tests in 0.09 seconds: 4 passed, 4 failed
```

(Tracebacks elided to their last line; the full run is reproducible with the
command above. The build's OpenSCAD chatter is elided too.)

Two faces of one defect, both inside `solid test`:

- **LOST** (`BenchGeometry`): the checkpoint held the build's TAGGED
  operation; the restore put it back; the next test's `set_keyframe(0)`
  swept it as its animator's own, and nothing re-placed it, because under a
  running root the run owns the coordinate and the enumeration does not
  re-solve it. The leaf stands at rest while its coordinate reads 8.0 — a
  geometry assertion measures a machine that is not the machine.
- **DOUBLED** (`BenchAfterSetUpClass`, from its SECOND test on — the wart's
  own wording): the checkpoint held the run's UNTAGGED operation, so the
  sweep could not reach it and the stale record could not either. 12.0 + 0.0
  for a coordinate reading 0.0.

## 8. The wart's own reproduction, re-run verbatim on the lock

`evidence/probe_lock.py`, on
`/home/asa/devel/libresolid-studio/projects/Locks/Pin_tumbler_lock`:

```
-- after build
  d1: 4 operations
    [0] Translation ['t', ['0', '0', '0.10000020307669977']] motion=True slot=0 animator=PinTumblerLock id=124452509660512
    [1] Rotation ['r', '90', (0, 1, 0)] motion=False slot=None animator=NoneType id=124452509658064
    [2] Rotation ['r', '180', (0, 0, 1)] motion=False slot=None animator=NoneType id=124452509658112
    [3] Translation ['t', ['25', '0', '5.5']] motion=False slot=None animator=NoneType id=124452509658160
    _joint_motion: {lift: [124452509660512]}
-- after test 1
  d1: 4 operations
    [0] Translation ['t', ['0', '0', '0.10000020307669977']] ... id=124452509660512
    _joint_motion: {lift: [124452509660464]}
-- after test 2
  d1: 4 operations
    [0] Translation ['t', ['0', '0', '0.10000020307669977']] ... id=124452509660512
    _joint_motion: {lift: [124452509660416]}
-- final set_keyframe(0)
  d1: 4 operations
    [0] Translation ['t', ['0', '0', '0.10000020307669977']] ... id=124452509660224
    _joint_motion: {lift: [124452509660224]}
```

Honest reading: on this worktree that exact sequence reports FOUR operations,
not the five the wart records. It does show the STALE RECORD the defect rests
on — after test 1 the list holds `id=…660512` while `_joint_motion` names
`…660464`, an object the restore has already discarded — but nothing in the
sequence binds a coordinate outside the enumeration, so no untagged operation
is ever stranded: every placement here is the root's relation, tagged, and
the sweep cleans it. The lock's own tests stopped stepping the runner's node
when the wart was filed (`lock_under_test()` in `simulation/test_lock.py`
builds a private lock and says why), which is why the project's own suite no
longer reaches it either. Sections 1, 3 and 7 reproduce the doubling the wart
describes, on a framework fixture, with the binding path spelled out.

## What the fix has to satisfy

Measured facts a candidate fix is answerable to:

1. A restored child must end up placed at the coordinates it holds (§7,
   `BenchGeometry`).
2. Removing a joint's previous placement must not depend on the operation
   OBJECTS surviving (§1, §6).
3. A many-operation placement must go as one unit (§3).
4. A child with no joint, a sub-assembly's child, and an untimed tree whose
   bindings are all in-phase must be exactly as they are (§2, §4).
5. The run's placements must stay UNTAGGED: tagging them would have the next
   enumeration's sweep delete the run's own pose, since nothing re-places a
   run-owned coordinate (§5 shows the run keeping its pose today with no
   checkpoint in the way).

# Revision 1: does the restore's re-place outlive its coordinate's value?

Revision 1's Finding A asks whether decisions 2 and 3 introduce a
regression: the operation the restore re-places is UNTAGGED, so the sweep
cannot reach it, and if the NEXT enumeration does not re-bind that joint
nothing removes it. Measured below, on this worktree, before any
implementation.

## The fixture

`evidence/bench/conditional.py` adds three untimed machines to the bench
project:

- `Conditional` — a root with NO time base whose `simulate()` binds a
  ROOT-LEVEL LEAF's `Prismatic` only under a guard,
  `if self.time < 0.5: self.gate.travel = 10.0`. Instant 0 binds it;
  instant 1 leaves it UNBOUND, which ADR-099's clear semantics explicitly
  allow ("SHALL find the coordinate unbound on every run").
- `Wired` — a root wiring its own port into a leaf's joint coordinate.
- `Formula` — a root whose DERIVED coordinate (`span = left + right`)
  drives a leaf's joint.

`evidence/probe_conditional.py` reads them. It takes
`save_children_checkpoints` and `restore_children_checkpoints` unchanged
off `solid_node.manager.test.Test` and, where a section says so, applies
the PROPOSED design at its seams and nowhere else:

- `clear_by_mark` — decision 1, `Joint.clear` dropping by `_joint_slot`;
- `replace_from_coordinates` + `restore_with_seam` — decisions 2 and 3;
- `clear_solved_with_motion` — decision 5, the joint cleared with the value.

`evidence/proposed_design.py` is the same three seams packaged as a pytest
plugin, so the framework's OWN suites can be run against the design before
a framework file is changed.

How each was run:

```
cd openspec/changes/checkpoint-the-joint/evidence/bench
PYTHONPATH="<worktree>:$PWD" <venv>/bin/python ../probe_conditional.py

cd <worktree>
PYTHONPATH="$PWD:$PWD/openspec/changes/checkpoint-the-joint/evidence" \
    <venv>/bin/python -m pytest tests/<files> -q -p proposed_design
```

## A1. TODAY: the guarded binding is GREEN

```
=== A1. TODAY: an untimed guarded binding, two instants
    instant 0 (the guard binds): travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'tagged')]
    instant 0: the runner restores: travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'tagged')]
    instant 1 (the guard does NOT bind: rest): travel=None, motion=[]
    instant 1: the runner restores: travel=None, motion=[(['t', ['10.0', '0', '0']], 0, 'tagged')]
```

At instant 1 — the instant the test method measures — the leaf is at REST
and its coordinate is unbound. Correct. The restore does put the build's
operation back afterwards, but it is TAGGED, so the next `set_keyframe`'s
`_sweep` removes it: today's content restore cannot strand anything here.

## A2. UNDER DECISIONS 1-3 ALONE: the same case is RED

```
=== A2. UNDER THE PROPOSED DESIGN (decisions 1 + 2 + 3)
    instant 0 (the guard binds): travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'tagged')]
    instant 0: the runner restores: travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'untagged')]
    instant 1 (the guard does NOT bind: rest): travel=None, motion=[(['t', ['10.0', '0', '0']], 0, 'untagged')]
    instant 1: the runner restores: travel=None, motion=[]
```

Line 2 is the seam: the restore re-places from the value the coordinate
holds, and the new operation is UNTAGGED because no phase is current during
a restore. Line 3 is the regression: at instant 1 the coordinate is unbound
— `clear_solved` dropped it — while the body still carries 10 mm of travel.
`_sweep` cannot see the operation, and nothing calls `joint.clear`. The
test method measures a leaf standing at the previous instant's pose.

Finding A is confirmed exactly as predicted: **green today, red under
decisions 1-3 alone.**

## A3. What every binding path records

The discriminator direction (i) would need, measured. Each row is one
binding of a joint coordinate, read immediately after it.

```
=== A3. What `slot.binder` and `slot._bound_by` hold, by path
    author's simulate() assignment:
        value      = 10.0
        binder     = NoneType  None
        _bound_by  = Conditional
        run_owned  = False
    a relation (push.drives(slide.travel)):
        value      = 0.0
        binder     = RelationRecord  <relation push drives slide.travel solved forward>
        _bound_by  = BenchBody
        run_owned  = False
    a hand assignment outside any phase:
        value      = 7.0
        binder     = NoneType  None
        _bound_by  = BenchBody
        run_owned  = False
    a running simulation:
        value      = 12.0
        binder     = RunBinder  <the running simulation>
        _bound_by  = Bench
        run_owned  = True
    a publication (document producer):
        value      = <ExpressionNode name 'travel'>
        binder     = RunBinder  <the running simulation>
        _bound_by  = BenchBody
        run_owned  = True
    the same slot after the publication restores:
        value      = 0.0
        binder     = RelationRecord  <relation push drives slide.travel solved forward>
        _bound_by  = BenchBody
        run_owned  = False
    a wiring into a leaf's joint coordinate:
        value      = 4.0
        binder     = Wiring  <solid_node.motion.couplings.Wiring object at 0x...>
        _bound_by  = Wired
        run_owned  = False
    a derived formula driving a joint coordinate:
        value      = 9.0
        binder     = RelationRecord  <relation span drives gate.travel solved forward>
        _bound_by  = Formula
        run_owned  = False
    the guarded leaf at instant 1: travel=None, motion=[]
    the same slot, never bound in a phase:
        value      = None
        binder     = NoneType  None
        _bound_by  = Conditional
        run_owned  = False
    ...then bound BY HAND outside any phase:
        value      = 3.0
        binder     = NoneType  None
        _bound_by  = Conditional
        run_owned  = False
```

Read as a table:

| binding path | `slot.binder` | `slot._bound_by` | `run_owned` |
| --- | --- | --- | --- |
| the author's own `simulate()` assignment | `None` | the assembly whose phase ran | `False` |
| a relation | `RelationRecord` | the assembly | `False` |
| a derived formula driving a joint | `RelationRecord` of the formula's relation | the assembly | `False` |
| a wiring into a joint coordinate | `Wiring` | the assembly | `False` |
| a hand assignment outside any phase | `None` | STALE leftover | `False` |
| a running simulation | `RunBinder` | stale leftover | `True` |
| a document publication | `RunBinder` | stale leftover | `True` |
| a slot nothing ever bound | `None` | STALE leftover | `False` |

Two facts settle direction (i):

1. `binder` is `None` for BOTH the author's own `simulate()` assignment and
   a hand assignment outside any phase. The first WILL be re-placed by the
   next enumeration (unless its guard says otherwise — Finding A's case);
   the second will not. `binder` cannot tell them apart.
2. `_bound_by` is never `None` on a tree that has rendered once: nothing
   clears it (`clear_solved` resets `_value` and `binder` only;
   `phase.note_bound` only ever sets it), so it is a sticky leftover. The
   last two rows show it reading `Conditional` on a slot NO phase has ever
   bound, and on one bound by hand afterwards.

The only live discriminator is `_enum_marker`, which `bind` stamps on every
binding with `current_enumeration()` and which is `None` exactly when
nothing was enumerating — but it is `clear_solved`'s own freshness
bookkeeping, and reading it in the test runner would couple the runner to
the solver's internals to reach a narrower result than direction (ii).

`clear_solved` walks `assembly.__dict__['_solver_bound']`, whose entries are
SLOTS. A slot carries `.node` (the node owning the coordinate, a leaf
several levels below the solving assembly included) and `.name` — and
`slot.name` is exactly the key `joint.coordinates` reports, `pose.roll`
included, measured on the bench's `floater`. So direction (ii) needs nothing
new recorded.

## A4. UNDER DECISION 5: the guarded binding is GREEN again

```
=== A4. UNDER (ii): clear_solved clears the joint of every coordinate whose value it drops
    instant 0 (the guard binds): travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'tagged')]
    instant 0: the runner restores: travel=10.0, motion=[(['t', ['10.0', '0', '0']], 0, 'untagged')]
    instant 1 (the guard does NOT bind: rest): travel=None, motion=[]
    instant 1: the runner restores: travel=None, motion=[]
```

Line 3 is A1's line 3 again: at rest, coordinate unbound. `clear_solved`
dropped the value and, with it, the joint's placement — by slot, so the
untagged operation goes even though the sweep cannot see it.

## A5. UNDER DECISION 5: open question 2 closes

The untimed HAND binding of §6, which today ends at `7.0 + 0.0` for a
coordinate reading `0.0`, permanently:

```
=== A5. UNDER (ii): the untimed HAND binding of open question 2
    built: travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
    a test binds the coordinate by hand: travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 1: bound by hand again: travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 2: bound by hand again: travel=7.0, motion=[(['t', ['7.0', '0', '0']], 0, 'untagged')]
    test 2: after the next set_keyframe(0): travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'tagged')]
```

One operation throughout, always stating the value the coordinate holds; and
at the next enumeration the hand value and its operation go together and the
relation's value and operation take their place. Compare §6, where the same
sequence reaches two operations and then strands one for good.

## A6. UNDER DECISION 5: the running root is untouched by the new clear

```
=== A6. UNDER (ii): the running root of sections 1 and 7 is untouched by the new clear
    a scenario has stepped the run: travel=12.0, motion=[(['t', ['12.0', '0', '0']], 0, 'untagged')]
    test 1: the runner restores: travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
    test 2: a third scenario binds the bank: travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
    test 2: after the next set_keyframe(0): travel=0.0, motion=[(['t', ['0.0', '0', '0']], 0, 'untagged')]
```

The sequence of §1, which reaches two operations (12.0 and 0.0) on the
unchanged framework, now carries ONE that agrees with the coordinate at
every step — including across the `set_keyframe` that would sweep a tagged
one. `clear_solved`'s existing `run_owned` exemption is what keeps the new
clear away from the run's own pose; without it the loss face would become
every render's behaviour.

## A7. The framework's own suites, unchanged, against the proposed design

Fourteen suites — the joints, couplings, runner, running-mode, declarative
and control suites — run UNCHANGED with `-p proposed_design`, which applies
decisions 1, 2, 3 and 5 at their seams:

```
tests/test_joints.py tests/test_couplings.py tests/test_manager_test.py
tests/test_running_simulation.py tests/test_motion_package.py
tests/test_kinematics.py tests/test_mechanisms.py
    516 passed, 1 warning, 505 subtests passed in 27.65s

tests/test_running_stops.py tests/test_running_jumps.py
tests/test_running_document.py tests/test_declarative_nodes.py
tests/test_declarative_render.py tests/test_animator_tag.py
tests/test_controls.py
    330 passed, 9 warnings, 489 subtests passed in 14.44s
```

846 tests and 994 subtests, nothing failed. The warnings are the
pre-existing `FutureWarning`s those fixtures already raise for reading time
in `render()`.

## What revision 1 adds to what the fix has to satisfy

6. A placement the restore re-places must not outlive the coordinate value
   that states it: a joint the next enumeration leaves unbound must leave
   the body at rest (§A1 against §A2 and §A4).
7. The new clear must not reach a coordinate a running simulation owns
   (§A6), nor one another assembly has already re-bound in the current
   enumeration — both are exemptions `clear_solved` already makes.
