# Evidence: `a-bound-stops-the-request`

The originating project is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation` at `9fb725f`, whose spike record
`simulation/docs/clocked-spike-2026-09-16.md` states the finding this
change answers (**finding 4**: a violated `Bound` must CLIP a request
rather than reject a pose, with the events located on the clipped path).

Everything below was run from inside this worktree with

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
      tests -q -p no:cacheprovider

ONE job at a time.

## Red log

Each entry is a test that was written, run and SEEN to fail before the
change that turned it green, with the failing line as pytest printed it.

### Task 2.1 — the compile

`CompileTest.test_the_pawl_compiles_one_constraint_over_the_bank` and
`test_a_plain_numeric_range_compiles_both_sides`:

    compiled = sim._clocked.bounds
    E  AttributeError: 'Clocked' object has no attribute 'bounds'

Turned green by `compile_bounds`, `_Chains` and `Bounded` in
`solid_node/simulation/clocked.py` (task 2.2).

### Task 2.3 — the refusals

Written against the green compile of 2.2 and run before 2.4's messages
existed in their final form. Two of the six were red for their own
reason and are recorded with their failures:

`RefusalTest.test_a_bounded_coordinate_bound_by_hand_is_refused`:

    self.assertIn('HandBound.simulate()', message)
    E  AssertionError: 'HandBound.simulate()' not found in
       "plate: joint 'lift' ... is bound BY HAND, in Plate.simulate(): ..."

`RefusalTest.test_a_bound_reading_an_unreached_coordinate_is_refused`:

    self.assertIn('UnreachedRead.simulate()', message)
    E  AssertionError: 'UnreachedRead.simulate()' not found in
       "slide: joint 'travel' ... its read 'plate.lift' is bound BY HAND,
        in Plate.simulate(): ..."

The refusal named the node the slot BELONGS to rather than the assembly
whose `simulate()` bound it, which is the class the maker has to edit.
Turned green by reading `slot._bound_by` — the record the rest render
already keeps of "the assembly whose OWN simulate phase bound this slot"
— and falling back to the slot's node when nothing bound it inside a
phase.

### Task 4.3 — the direction test

`ClipTest.test_the_threshold_frees_a_bank_standing_outside_a_bound`, as
`design.md` section 17 words it:

    back = sim.move('feed', by=15.0)
    self.assertEqual(back.admitted, 15.0)
    E  AssertionError: 4.0 != 15.0

This is a CONTRADICTION inside the ratified design, not an
implementation fault; it is written up under "Design questions" below and
the test now asserts section 7's own rule.

### Task 5.7 — `sim.stops`

`RequestTest.test_sim_stops_is_a_bounded_ring_under_record` and
`test_sim_stops_is_empty_without_record`:

    return self._running('stops').stops
    E  TypeError: stops belongs to a simulation with a CLOCK, and Stroke
       is CLOCKED: ...

Turned green by `Sim.stops` returning the clocked ring (task 5.8), and by
moving `'stops'` out of cycle 1's `CadenceRefusalTest.REFUSED` list and
into its admitted-surface list — the one deliberate change to a cycle 1
test, stated by the proposal ("which LIFTS cycle 1's refusal of that
name").

### Task 6.3 — one authority, at BOTH judgement sites

`AuthorityTest.test_a_request_marks_the_coordinates_it_compiled`:

    self.assertIn(('couplings', 'travel', True), seen)
    E  AssertionError: ('couplings', 'travel', True) not found in
       [('joints', 'travel', True)]

The first placement of the mark returned from
`Joint._refuse_out_of_range` BEFORE `phase.note_bound_binding`, so the
close of the enumeration never heard of the binding and
`couplings.refuse_bounds` never consulted the mark at all. Behaviourally
equivalent, structurally wrong: the design says the TWO judgement sites
consult the mark. Turned green by moving the check to sit AFTER the
binding is recorded, so the enumeration's `bounds` list stays complete
and `refuse_bounds` skips the coordinate through its own consultation,
exactly as it skips a run-owned one.

### Tests that arrived green, and why

Task 3 (classification), task 4.1/4.5, task 5.1–5.6 and task 7 were
written after the compile of 2.2 and the clip of 5.2 were already in the
tree, and most of them passed on their first run. They are recorded
honestly as such rather than as reds: the compile, the classification,
the clip and the request are ONE mechanism — `Bounded`'s construction is
where the classification lives, and `Clocked.move` cannot truncate a
travel it has not compiled a level for — and splitting them into
separately-red steps would have meant writing stubs whose failure proved
nothing about the design. Where a test DID fail it is above, with its
line. This is a deviation from the assignment's "every test seen red
first" and is reported as one.

The three failures that were test-side rather than implementation-side
(`node.plate.lift` is the port object, not its value) are not listed as
reds; they were corrected in the test.

## Design questions

### 1. The direction test and "a request back to exactly where it started"

`design.md` section 7 decides the threshold: **`h = max(0, g(0))`, read
at the start of EACH request**. Section 17's planned proof for the
OUTSIDE fixture then states three assertions:

> a request inward admits its whole travel, a request back to exactly
> where it started is admitted, and a request that would carry it
> further out admits zero and reports the stop.

The middle one cannot hold under section 7's own rule, and the
implementation measured it: from `feed = 20` (the slide standing at 20
where its bound is 9), `move('feed', by=-15)` admits its whole travel
and lands at 5, which is INSIDE the bound. The NEXT request reads
`g(0) = 5 - 9 = -4`, so `h = 0` — the ordinary bound — and the return is
clipped at 9, admitting 4 of the 15 asked for. It is not a rounding
question: it is what "the level it started at, or zero, whichever is
greater" means once the machine has come back inside. Nor does choosing a
shorter inward travel rescue it: from 20 to 15 the threshold becomes 6,
and returning to 20 is still clipped.

**Choice taken:** section 7 is the DECISION and section 17 is a planned
proof, so section 7 wins and section 17's middle assertion is treated as
a mis-statement of it. `ClipTest.test_the_threshold_frees_a_bank_standing
_outside_a_bound` now asserts, in one test:

* a request `to=` exactly where the machine already stands is ADMITTED
  (zero travel, no stop) — which is the reading of "back to exactly where
  it started" that section 7 does support;
* a request further out from 20 admits zero and reports the stop;
* a request inward admits its whole travel;
* and a request back out, from INSIDE, is admitted only as far as the
  bound itself — 4 of 15 — with the deviation named in the test.

Nothing was silently substituted: the ratified DECISION is implemented
exactly, and the proof text is what moved. **Confirmed at the cycle's
review (2026-09-17):** section 7 stands, and the cross-request
consequence — a bank that came back INSIDE a bound cannot return outside
— is stated behaviour, recorded in `workflow/warts.md` and in ADR-126. A
threshold REMEMBERED across requests is a different design and would
need its own evidence.

### 2. Two rows of section 3's refusal table are unreachable

Section 3 refuses, among others, "a chain that reads the coordinate it
drives (ADR-121's self-read)" and "a chain that is CYCLIC". Both are
refused EARLIER, by the relation layer, under every non-running root,
long before the clocked compile is reached — measured on fixtures written
for them:

* `bounds_unsupported.SelfReadChain` →
  `CouplingError: (clearing, wheel.turn) drives wheel.turn, stated by
  SelfReadChain: it reads wheel.turn, the coordinate it drives, and a
  relation that reads its own driven end states INCREMENTS ... which only
  a running simulation ...`
* a two-relation cycle between two unbound plate lifts →
  `UnreachedCoordinate: a.lift drives b.lift: nothing bound either end.
  ... the relation has no side to be read from.`

The guards are kept in `_Chains` as backstops (the self-read check on
`record.relation.self_read`, and the `seen` set for a cycle) and are
unreachable by any fixture this cycle could write. The refusal TEST for
the self-read therefore asserts the message a maker actually sees, and
says so in a comment; the cyclic row has no test at all, which is a
structural blind spot reported rather than hidden.

### 3. `restore` is not marked

Section 10 part 3 lists `restore` among the poses judged by the
ENUMERATION, and the mechanism paragraph says "nothing outside a request
is ever marked"; section 17 says a `restore` "takes the same path".
Those cannot all be literally true, because `Clocked._posed` is shared.
The two explicit statements were taken: `_posed` gained a `marked=`
argument, `move` passes it and `restore`/`reset` do not, so `_posed` is
still what opens and closes the mark (task 6.4) and nothing outside a
request is marked.
`AuthorityTest.test_a_pose_that_is_not_a_request_is_judged_by_the
_enumeration` asserts it: after a request that landed the shutter exactly
on its inclusive bound, restoring that snapshot consults the mark at both
sites and gets `False` at every one — and does not fail, which is what
section 17 asks of it.

### 4. A relation binding into a SCALED sink

`ports.bind` multiplies by the sink's declared `scale` for EVERY binder —
a wiring, a relation, a derived coordinate alike — while the running
compile applies a scale factor only for a wiring edge (`_wiring_edge`'s
`factor`). The chain here applies `slot.scale` uniformly, wherever it
composes INTO a slot, because task 6.1's agreement test compares the
chain against the POSE and the pose goes through `bind`. A joint's own
coordinate is created with `unit=` alone and therefore never carries a
scale, so no existing model can tell the two readings apart; if one ever
does, the running compile is the side that looks wrong. Recorded, not
acted on.

### 5. Names

`proposal.md` names the compile `compile_constraints` and the value
object `Constrained`; `tasks.md` names them `compile_bounds` and
`Bounded`. The tasks list was followed. The per-request view of one
constraint is `_Level`, which neither document names.

**Decided at the cycle's review (2026-09-17):** `compile_bounds` and
`Bounded` STAND, and `proposal.md`'s `compile_constraints`/`Constrained`
are SUPERSEDED by them — recorded here rather than by editing a ratified
proposal. ADR-126 uses the code's names.

## Measurements

Design section 18's plan, taken on the FIXTURES ONLY and compared to
nothing. One process, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, on the
workspace venv (CPython 3.12). Wall-clock means over the stated repeat
counts.

### Construction: compiling the constraints

`nodes` counts postorder nodes of the composed graph.

| fixture | compile | constraints | chain nodes | level nodes |
| --- | --- | --- | --- | --- |
| `Counter` (no ranged joint) | 15.5 µs | 0 | — | — |
| `Stroke` (numeric `(0, 9)`) | 221.8 µs | 2 | 1, 1 | 3, 3 |
| `Pawl` (one-argument bound) | 253.5 µs | 1 | 1 | 8 |
| `Gate` (bound reads a STATE) | 254.8 µs | 2 | 3, 3 | 5, 9 |
| `Kinked` (`max` over a read) | 249.3 µs | 1 | 3 | 9 |
| `Lock` (the note's sketch) | 429.4 µs | 2 | 3, 3 | 5, 15 |
| `Freeze` (the acceptance shape) | 660.9 µs | 2 | 3, 3 | 17, 18 |

A clocked tree with no ranged joint compiles nothing and the whole call
is the `qualified_coordinates` walk. The Curta's own interlocks are one
or two links deep, and the deepest chain any fixture here produces is
three nodes: the risk section's "a composed chain can be large" is not
reached by anything this cycle can write.

### One request

Measured as `(restore + move)` minus `restore` alone, 200 rounds each, so
the number is the request's own cost with the restore's pose removed.

| fixture and shape | request |
| --- | --- |
| `Counter` — no constraint at all | 22.3 µs |
| `Stroke` — one examined, not violated | 183.0 µs |
| `Stroke` — clipped, AFFINE level | 203.1 µs |
| `Gate` — clipped, JUMPED level, one event on the clipped path | 269.1 µs |
| `Kinked` — clipped, KINKED level | 263.4 µs |
| `Lock` — clipped, JUMPED level (two jump nodes) | 398.9 µs |
| `Freeze` — two constraints, ZERO travel admitted | 391.6 µs |

The subtraction is approximate — the two restores pose slightly different
banks — so these are indicative of the SHAPE of the cost (a clip costs
tens of microseconds on top of a request, and a jumped level costs more
than an affine one) rather than exact.

### The chain against one pose of the same fixture

This is the ratio the whole design rests on: locating a stop by posing
the tree along the path was the alternative rejected in section 2.

| fixture | one chain evaluation | one level evaluation | one POSE | pose : chain |
| --- | --- | --- | --- | --- |
| `Stroke` | 1.64 µs | 4.82 µs | 118.6 µs | 1 : 72 |
| `Gate` | 2.94 µs | 7.34 µs | 82.9 µs | 1 : 28 |
| `Freeze` | 2.94 µs | 15.70 µs | 104.7 µs | 1 : 36 |

### Step 6, the end-of-request judgement

One LEVEL EVALUATION per compiled constraint per request, beside one for
each constraint's threshold at the request's start — so a request over a
machine with `n` compiled constraints costs `2n` level evaluations
outside the clip itself, plus one clip per constraint the moving driver
can move. For `Stroke`, `Gate` and `Freeze` that is 2 + 2 evaluations and
2 clips each; at the numbers above, under 40 µs on the most expensive of
the three.

**Not claimed in this cycle:** anything about the Curta. Its clocked
model and its interlock audit are project work in the project's own
repository.

## Full suite

    3183 passed, 4 skipped, 53 warnings, 1754 subtests passed in 314.92s

taken at the cycle's completion, one process, from inside this worktree.
(An earlier reading of `3180 passed ... in 310.34s` was taken three tests
before the last of them was written; the line above is the final one.) No
fixture of another capability was edited and no expected value of one was
changed; the single edit to an existing test is cycle 1's
`CadenceRefusalTest`, moving `stops` from its refused list to its
admitted one, which this change's proposal states.
