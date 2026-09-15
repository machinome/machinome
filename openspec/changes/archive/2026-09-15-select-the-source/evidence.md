# Evidence: applying `select-the-source`

Every measurement below was taken on this worktree, branch
`select-the-source`, base `4045916`, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` and one job at a time.

Python: `PYTHONPATH="$PWD" ../../../.venv/bin/python`.

## Group 1 — fixtures

`tests/carriage_project/` (`__init__.py`, `machine.py`), covered by
`tests/pyproject.toml` like every other fixture package under `tests/`.

### What each fixture gets TODAY (task 2.2's sibling record)

Probed by constructing `Sim(klass(), dt=.02)` on this worktree before any
compile change:

| fixture | today |
| --- | --- |
| `ShiftedCarry` (1.1) | `UnsupportedLaw: the relations (crank, shift, clearing, carry.travel, higher.turn) drives higher.turn, (lower.turn, higher.turn, shift, carry.travel) drives carry.travel form a cycle the run cannot order: ...` — the note's message VERBATIM |
| `ShiftedCarryBody` (no time base) | `CouplingError: ... it reads lower.turn, the coordinate it drives, and a relation that reads its own driven end states INCREMENTS ...` |
| `LoopingShiftedCarry` (`Time(loop=4)`) | the same `CouplingError` |
| `FixedZero`, `FixedOne` (1.1 twins) | CONSTRUCTED, bank all zero |
| `Unconditional` (self-reads kept) | today's cycle message, naming both relations |
| `UnconditionalBare` (self-reads removed) | `DoublyBound: higher.turn would be bound by the relation (crank, carry.travel) drives higher.turn and by the author's simulate()` |
| `SelectedBare` (selections, no self-read) | `DoublyBound: higher.turn ...` |
| `SelectedUnguarded` (no rest default) | `UnreachedCoordinate: (crank, shift, carry.travel) drives higher.turn: waiting for carry.travel` |
| `SignGated` | `DoublyBound: lower.turn ...` |
| `BothActive` | `DoublyBound: lower.turn ...` |
| `PortInBlock` | `DoublyBound: wheel.turn ...` |
| `GroupInBlock` | `DoublyBound: lower.turn ...` |
| `WiringInBlock` | `DoublyBound: ... .spindle ...` |
| `DerivedInBlock` | `DoublyBound: ... .hub ...` |
| `UnbankedCycle` | CONSTRUCTED, bank `{'crank': 0.0, 'wheel.turn': 0.0}` |
| `CurtaCarriage` (1.2) | today's cycle message naming all SEVEN relations — three levers and four dials in ONE block |

Both measured predictions of design.md fact 2 hold on these fixtures:
`DoublyBound` where the block's driven ends carry rest guards
(`SelectedBare`), `UnreachedCoordinate` where they do not
(`SelectedUnguarded`).

## Groups 2, 3, 4 and 6 — recognition, rest, evaluation, the run-time refusal

Tests: `tests/test_running_selection.py` (38), plus
`tests/test_running_simulation.py::SelectionConstructionTest` (3).

### 2.1 RED, before any compile change

```text
FAILED tests/test_running_simulation.py::SelectionConstructionTest::test_the_selected_union_constructs
E   UnsupportedLaw: the relations (crank, shift, clearing, carry.travel,
    higher.turn) drives higher.turn, (lower.turn, higher.turn, shift,
    carry.travel) drives carry.travel form a cycle the run cannot order: ...
```

GREEN: `Sim(ShiftedCarry(), dt=.02)` constructs, bank
`{'carry.travel': 0.0, 'clearing': 0.0, 'crank': 0.0, 'higher.turn': 0.0,
'lower.turn': 0.0, 'shift': 0.0}`.

### 2.2 Green on the FIRST run, before any change

`test_a_cycle_no_selection_breaks_is_refused` passed against the
unmodified worktree and goes on passing: it asserts today's message as a
SUBSTRING, which the change extends with one sentence about what a
switch is rather than replacing.

### The remaining RED evidence

The recognition, the pre-pass and the block runtime were applied in one
pass before the rest of the group's tests were written, so each of those
tasks' red was taken afterwards by REVERTING the exact mechanism the task
names and running its tests. Every revert was restored immediately; the
worktree carries none of them.

| task | mechanism reverted | red |
| --- | --- | --- |
| 2.4 | `_selectors` returns nothing (every jump reads the block) | 4 failed — `UnsupportedLaw: ... form a cycle the run cannot order ...` on the reduced fixture: with no selector, nothing is switched |
| 2.5 | `_refuse_unselectable` not called | 4 failed — `AssertionError: UnsupportedLaw not raised` (group), and `LandingInvariantError: the construction pre-pass marked the relations determining spindle, wheel.turn ... and the compile found relay.turn, spindle, wheel.turn` (wiring, derived, port) |
| 2.6 | the `block` line not emitted | `ValueError: "block ['higher.turn', 'carry.travel']" is not in list`; `AssertionError: <digest> == <digest>` — the identity no longer distinguishes membership |
| 3.2 | the pre-pass marks nothing | 4 failed — `DoublyBound: higher.turn would be bound by the relation (crank, shift, carry.travel) drives higher.turn and by the author's simulate()`, and `LandingInvariantError: the construction pre-pass marked the relations determining none ... the compile found carry.travel, higher.turn` |
| 3.5 | the assertion short-circuited | `AssertionError: LandingInvariantError not raised` |
| 3.6 | `release_tree` does not clear | `AssertionError: Items in the first set but not the second: True` |
| 4.3 | forcing removed from `_partition` and `_branches` | `AssertionError: Lists differ: [Crossing(..., primitive='>=', level=0.0, t=0.5)] != []` — the member re-locates the selector's surface inside the piece; and `AssertionError: 0.0 != 1.0` — flipping the forced branch no longer changes the answer |
| 4.7 | the block reports the LAST landing | `AssertionError: 1.0 != 3.0` — exactly design.md section 3's prediction: the landing commits and the later piece's `+2.0` is silently lost |
| 4.8 | forcing removed from `_branches` | `AssertionError: 0.25 != 5.0` — the switched-out source reaches the answer |
| 6.1 | (before the change) | `DoublyBound: lower.turn would be bound by the relation (crank, shift, higher.turn) drives lower.turn and by the author's simulate()` — the fixture did not construct at all |

### 4.1 The selected machine equals the frozen twin

Cranked by `2.0` over 12 ticks of `dt = 1/12`:

| coordinate | selected, `shift = 0` | `FixedZero` | selected, `shift = 1` | `FixedOne` |
| --- | --- | --- | --- | --- |
| `lower.turn` | `1.9999999999999998` | `1.9999999999999998` | `0.0` | `0.0` |
| `higher.turn` | `1.4999999999999998` | `1.4999999999999998` | `1.9999999999999998` | `1.9999999999999998` |
| `carry.travel` | `1.0` | `1.0` | `1.0` | `1.0` |

At `dt = 1.0`, one tick: `lower.turn 2.0`, `higher.turn 1.5000000000000002`,
`carry.travel 1.0` against the twin's identical values — and against
`spikes/arbitrary.py`'s `1.4800000000000013` under declaration order and
`0.0` under the reverse.

### 4.7 A landing and then motion

`LandedCarry` at `dt = 1.0`, crank by `4.0` and shift `0 -> 1`:
`carry.travel` commits `3.0` — the landing `1.0` from the piece before the
detent plus the `2.0` the higher wheel gives it after. Run to the FIRST
half only (`dt = 0.5`), it commits `1.0`, which is what "the last
landing" would have committed for the whole tick.

### 6.1 The run-time refusal, transactionally

```text
UnsupportedLaw: over the piece [0.5, 1.0] of this tick the relations
(crank, shift, higher.turn) drives lower.turn, (crank, shift, lower.turn)
drives higher.turn form a cycle the run cannot order: each waits on a
coordinate another determines, and the selection this piece was read under
leaves every dependency on this cycle active. The selectors read
lower.turn: >= on
(shift - 0.5) reads 1.0; higher.turn: >= on (shift - 0.5) reads 1.0. The
tick committed nothing: ...
```

`sim.state`, `sim.tick`, `sim.crossings` and `sim.stops` are the previous
tick's, and the command that moved `shift` reports `refused`.

## Deviations from the design, and why

1. **Where the pre-pass runs.** design.md section 11 places it "between
   `release_tree(node)` and `_bind_initial(state)`". Measured, that is too
   late: `Sim.__init__`'s FIRST statement after the constructor's
   bookkeeping is `qualified_drivers(node)`, which the file's own comment
   calls "another `drive_tree`", and it enumerates the relations. On
   `SelectedBare` it raises `DoublyBound: higher.turn would be bound by
   the relation (crank, shift, carry.travel) drives higher.turn and by the
   author's simulate()` before `release_tree` is reached at all. The
   release and the pre-pass therefore moved TOGETHER to just before that
   walk, keeping their order and keeping the pre-pass before every
   enumeration of the construction. The design's requirement -- membership
   decided before the rest render -- is met more strictly, not less.
2. **`_Block.switched` and `_Block.unconditional` exclude the member's own
   driven end.** ADR-121's self-read is not a wait on anything else and
   `_ordered` already excludes it; carrying it in the sets would have made
   every self-reading member look as though it waited on itself.
3. **The block's crossings are sorted by their fraction of the stretch**
   before they reach the run's record. A selector's crossing is located
   over the whole stretch and a member's own is rescaled out of its piece,
   so without the sort the listing would depend on which was computed
   first. ADR-107's own `_partition` sorts for the same reason.

## Group 5 — stops, constraints and retention

Tests: `tests/test_running_stops.py::BlockStopTest` (7) and
`::CarriageInterlockTest` (2), plus
`tests/test_running_selection.py::CurtaShapedTest` (2).

Fixtures added: `RangedBlock` (a block coordinate declaring
`range=(None, 0.6)`, with an input that reaches it only through a
switchable term), `StoppedLanding` (the same with a gate that LANDS the
coordinate and a setter that then carries it past the bound).

| task | measured |
| --- | --- |
| 5.1 | `carry.travel` commits `0.6` AT its bound, one stop at `t = 0.3` naming `('crank',)`, `crank` retired `blocked` with `0.5999999999994543` admitted; `edge.affine == [False, False]`, so the localization took the SEARCHED path |
| 5.2 | `StoppedLanding`: the gate cuts at `t = 0.1667` and lands the lever at `0.5`, the setter carries it past `0.6`, and the bank commits `0.6` — the bound, over the landing, with the crossing still recorded |
| 5.3 | stop first: stop at `t = 0.3`, selector crossings at `t = 0.5` (both), from ONE tick. Crossing first: selector crossings at `0.5`, stop at `t = 0.7` |
| 5.4 | `spin` reaches the stopped lever only through `lower * (shift < 0.5)`, inactive at `shift == 1`: `spin` retires `completed` with its whole `1.0` and `lower.turn == 1.0`, while `crank` retires `blocked`. `_pushes('crank', ...)` is True and `_pushes('spin', ...)` is False against the same values, and `program.sources[carry.travel]` is the over-broad `['crank', 'shift', 'spin']`. The block is ONE entry of `program.determiner`, giving `['higher.turn', 'carry.travel']`, so `_pushes` runs the whole block before its `key in edge.gives` break. A displacement probe over a genuinely cyclic piece raises the SAME string the tick over that piece raises (asserted equal, not merely both refusing) |
| 5.5 | `CurtaCarriage`: with the carriage DOWN and every lever standing at `1.0`, `position` is retired `blocked` with `0.0` admitted, `seat` stands at `20.0`, the stop names `('position',)`, and every dial and lever holds the float it held. Lifted first, the same shift completes |
| 5.6 | `CurtaCarriage` retention, at `dt = 0.02`: after cranking at position 1, `dial2 = 72`, `dial3 = 72` (each `+36` from the lever facing the dial below it) and every lever at `1.0`. Lift, shift to position 2, drop: every coordinate but the carriage's unchanged. Reset while lifted: levers return to `0.0`, `dial3` still `72`. Crank again: `dial2 = 108` (crank only), `dial3 = 144` (crank plus the lever it NOW faces), `lever2` still `0.0` |

## Group 7 — composition with ADR-121

Tests: `tests/test_running_reads.py::BlockSelfReadTest` (4).

`LandedCarry` at `dt = 1.0`, crank by `4.0` and shift `0 -> 1`, records
four crossings in one tick, in path order:

```text
('carry.travel', '<', 0.25)   the lever's own gate, rescaled out of its piece
('higher.turn', '>=', 0.25)   the wheel's gate on the lever
('higher.turn', '<', 0.5)     the selector, located over the stretch
('carry.travel', '<', 0.5)    the selector, located over the stretch
```

The walk's landing is committed: over the first half alone the bank reads
`carry.travel == 1.0` and the tree's own slot reads `1.0`.

The `_Retained` split is decided ONCE at compile with the selectors still
symbolic: the wheel's `dependent` is `['$j3']` (its own angle) and its
`outer` is `['$j0', '$j1', '$j2']` (both selectors and the lever gate);
the lever's `dependent` is `['$j2']` and its `outer` is `['$j0', '$j1']`.
A law with NO block is partitioned exactly as before —
`CurtaInterface`'s dial keeps its `2` dependent and `2` independent
nodes, and its program is still six plain `law` edges.

## Group 8 — publication and the corpus

Tests: `tests/test_running_document.py::BlockDocumentTest` (6),
`tests/test_running_corpus.py` (12, two of them new).

- `ShiftedCarry` publishes `version: 7`; `Train` still `5` and
  `Clearing` still `6`. `tests/test_running_document.py`'s whole
  byte-identity suite passes untouched.
- A block's members publish as ORDINARY law edges, contiguous at the
  block's position: `[['lower.turn'], ['higher.turn'], ['carry.travel']]`
  in that order, each carrying `affine`, `description`, `expressions`,
  `gives`, `kind`, `needs`, `plans`, `stated_by` and nothing else.
- `program`'s keys are still `clock`, `coordinates`, `edges`,
  `identity`, `intermediates`, `limits`, `sources`, `spans`; a jump
  entry's keys are still `affine`, `level`, `name`, `primitive`.
- The block and its selectors are re-derived IN THE TEST from the
  published edges alone — the SCC over `needs`/`gives` with `needs ∩
  gives` excluded gives `{1, 2}` and `{carry.travel, higher.turn}`, and
  resolving each jump's `level` transitively through the document's
  `bindings` picks out `['>=', '<']` for the wheel and `['<', '>=']` for
  the lever.
- Placeholder minting over a document with a block is still
  `_j0 … _j8` in edge order and then postorder over the FLAT list of law
  edges (2 + 4 + 3).

### The corpus (8.4 – 8.6)

Two machines added to `CORPUS`: `ShiftedCarry` (`dt = 0.05`, 20 ticks)
and `RangedBlock` (`dt = 0.05`, 8 ticks). Three `REQUIRED` entries added,
each detected from the document and the tick log the way the existing
ones are, with the block and its selectors re-derived in
`_selection(program, bindings)` exactly as a consumer must.

Regenerated and diffed against the committed corpus:

```text
top-level keys identical; generated_by / corpus / tolerance unchanged
removed: []
added  : [('RangedBlock', 0.05, 8), ('ShiftedCarry', 0.05, 20)]
changed: []
order of the pre-existing entries: preserved
```

The generator refuses a corpus without them
(`test_a_corpus_with_no_block_is_refused`,
`test_a_corpus_with_no_selection_crossing_is_refused`), and the committed
fixture replays exactly (19 scenarios over 16 machines, 356 ticks).

## Group 9 — regression, cost, documentation

### 9.1 The named suites

```text
tests/test_running_simulation.py tests/test_running_jumps.py
tests/test_running_stops.py tests/test_running_reads.py
tests/test_running_document.py tests/test_running_corpus.py
tests/test_running_selection.py tests/test_couplings.py
tests/test_export.py tests/test_build_publication.py
611 passed, 3 warnings, 762 subtests passed in 61.13s
```

The whole suite, once:

```text
3001 passed, 4 skipped, 53 warnings, 1679 subtests passed in 348.54s (0:05:48)
```

And once more after the review closure (round 1), with the one test that
closure added:

```text
3002 passed, 4 skipped, 53 warnings, 1679 subtests passed in 345.74s (0:05:45)
```

### 9.2 Cost

`tools/bench_selection.py`, `dt = 0.02`,
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time, best of
three:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  PYTHONPATH="$PWD" ../../../.venv/bin/python tools/bench_selection.py 3
```

| bench | ms/tick |
| --- | --- |
| `Train` — the control, no block | 0.482 |
| `FixedZero` — the frozen twin, three separate edges (the machine the project can build today) | 0.799 |
| `ShiftedCarry` — one block of two, no crossing | 1.306 |
| `ShiftedCarry` — the tick that crosses the detent (two pieces) | 2.671 |
| `RangedBlock` — the tick that drives a block coordinate INTO its range | 17.186 |
| `CurtaCarriage` — one block of seven, four dials and three levers | 10.658 |

Read against the honest baseline: a two-member block costs **1.6x** the
same laws run as separate edges with the carriage frozen, and **2.0x** on
the one tick that crosses a detent — the "about `p` times the members'
ordinary cost" design.md section 10 predicted, with `p` of 1 and 2. The
expensive case is the one section 10 named: a stop on a block coordinate
is SEARCHED, and at 17.2 ms that one tick is 22x a quiet one. The
control's `0.482 ms/tick` is this machine's number for a program with no
block at all; `docs/architecture.md`'s `1.05 ms/tick` was measured on a
different machine and no test pins either.

### 9.3 – 9.5 Documentation

- `docs/driving.rst`: a new section "A selection decides which sources a
  law reads", before "Derived coordinates" — the spelling, what a
  selector is, what the fold means, why `sign` cannot switch a source and
  a comparison can, the rest-default obligation, the run-time refusal and
  the four construction refusals.
- `docs/scenarios.rst`: a new section of the same name before "A range is
  a physical stop" — what the run does with a block, what it reports for
  a landed coordinate, the stop rules, and version 7.
- `HISTORY.rst`: the Unreleased entry, above the self-read one and in its
  voice, carrying the **BREAKING for consumers** version 7 sentence.
- `workflow/docs/curta-shifted-carry-association.md`: a **Taken up**
  paragraph in the shape of its predecessor's, naming
  `select-the-source` and ADR-122 (extracted after review).

## Design contradictions found while applying

None of the ratified design's DECISIONS were contradicted by the code.
Two of its stated PLACEMENTS were, both measured, both recorded above
under "Deviations from the design, and why" (the pre-pass's position, and
`release_tree` clearing the marks). A third, smaller one is recorded
there too.

The third placement deviation, stated in full:

3. **`release_tree` does NOT clear the marks** (design.md section 11 says
   it does). Measured: `program_of` constructs a `Sim` over a tree the
   producer owns and then, in its `finally`, calls `release_tree(root)`
   and `_restore(snapshots, root)` — which RE-RENDERS the tree. With the
   clearing in place that render finds the block's relations unmarked and
   refuses the model:

   ```text
   DoublyBound: higher.turn would be bound by the relation
   (crank, shift, carry.travel) drives higher.turn and by the author's
   simulate().
   ```

   The marks are a pure function of the tree's declared relations rather
   than run state, so nothing about the run's claim implies they should
   go with it. What design.md section 11 wanted the clearing for — a
   stale mark reaching a later NON-running enumeration — is delivered by
   the thing the same paragraph names as the real protection:
   `_step_relation`'s marked branch is guarded by
   `_under_running_root(record)`, and the pre-pass rewrites every mark
   from the records on each running construction. Both halves are tested
   (`MembershipTest.test_the_marks_survive_a_release_and_are_recomputed`,
   `test_a_non_running_tree_is_untouched_by_a_stale_mark`).

4. **The pre-pass also runs from `bind_declared_defaults`.** design.md
   section 11 names `sim.py` as the only caller. The producers do not go
   through `Sim` first: `tools/generate_running_corpus.py` and the
   serializer call `bind_declared_defaults(node)`, which is
   `qualified_drivers(root)` — an enumeration — before any program is
   compiled, and a block would be refused `DoublyBound` there. A guarded
   call was added at that one point, confined to a running root and
   idempotent, for the same reason as the one in `Sim`.

## Out of scope, found while applying

Recorded for the reviewer to file in `workflow/warts.md`; NOT fixed here.

1. **An input whose push depends on ANOTHER input moving the selection
   is invisible to `_pushes`, and the tick then refuses loudly.**
   Measured on `RangedBlock` at `dt = 1.0` with `spin` by `2.0`, `crank`
   by `0.2` and `shift` by `1.0` in one tick: `spin` drives the lever
   into its bound at `t = 0.3` and is blocked; over the remainder the
   carriage crosses its detent and `crank` then drives the lever past the
   bound through the OTHER wheel; but `Run._pushes` displaces `crank`
   alone with `shift` held, so the selection never changes in the probe,
   `crank` is not found to push, `_group` returns empty and the run
   raises

   ```text
   StopInvariantError: carry.travel left a declared bound over this tick,
   and locating the stop stopped no input that was moving -- after 3
   event(s), one per input admitting travel. ... The tick committed
   nothing.
   ```

   This is ADR-113's recorded one-input-at-a-time limit meeting a
   two-input coupling, not a wrong answer: the tick is refused
   transactionally. **It is PRE-EXISTING and not introduced by the
   block**: the same error comes out of a machine with no block at all —
   a clutch `(shaft & sleeve).drives(wheel.turn, law=s * (v > 0.5))`,
   `wheel.turn` ranged `(None, 0.3)`, `sleeve` 0 -> 1 and `shaft` 0 -> 1
   in one tick of `dt = 1.0`:

   ```text
   StopInvariantError: wheel.turn left a declared bound over this tick,
   and locating the stop stopped no input that was moving -- after 2
   event(s), one per input admitting travel. Every stop stops at least
   one moving input, so this is a broken invariant of the run rather
   than a coarse dt. The tick committed nothing.
   ```

   Measured on this worktree with the review's probe `two_input_push.py`
   and, by the reviewer, identically on the tree before this cycle. The
   wart is therefore filed against ADR-113's pushing test, not against
   the block; design.md section 7 now states the limit. design.md section 7 states the converse case (an
   input reaching a coordinate only through an INACTIVE selection) and
   does not state this one. A follow-up would have to displace the
   selecting input alongside the candidate, which is a change to the
   pushing test rather than to the block.

## Review closure (round 1)

Findings C1 to C5 of the adversarial review, closed on top of the
implementation, same worktree and same measurement conditions.

### C1 — the walk's `own_at` moved a held coordinate by an ulp

**Pre-existing**, in ADR-121's walk as it stands on main: `_Walk.run`'s
`own_at` and `_Walk._probe` both computed
`own_left + self._skeleton(s, branches) - base`, which Python takes left
to right as `(own_left + S) - base`. When `S == base` but `|S|` is
comparable to `|own_left|` the sum rounds and the result is
`own_left ± 1 ulp`, so a self-read member whose skeleton is UNCHANGED
over a piece still moved whenever any of its sources moved.

Reproduced with NO block anywhere, by the review's probe
`walk_noise.py`: a crank standing at `72.0`, a wheel resting at
`71.99999999999996`, the law `c + r * (own > 0.5) * (h < 0.5)`, and
`hoist` moved by `0.2`.

```text
before the fix:  wheel before 71.99999999999996 after 71.99999999999994 changed=True
after  the fix:  wheel before 71.99999999999996 after 71.99999999999996 changed=False
```

On the Curta-shaped fixture (`ulps3.py`, tick 41 — the first tick of a
lift, `hoist` 0 → 0.2, no selector crossing and no lever moving) the
dial member returned `-1.4210854715202004e-14` before and returns
exactly `0.0` after:

```text
    tick 41 lever0.travel: own=1.0 moving={'hoist': 0.2} -> increment=0.0 landing=None
    tick 41 dial2.turn: own=72.0 moving={'hoist': 0.2} -> increment=0.0 landing=None
    block totals: {}
    block landings: {}
```

It is fixed in THIS cycle because the ratified SHALL depends on it:
"with its sources otherwise still, a tick in which a selection changes
SHALL commit every coordinate of the block unchanged" cannot be asserted
bit for bit while the walk adds an ulp of its own.

**RED.** New fixture `HeldAngle` in `tests/running_project/machine.py`
(the module that already owns ADR-121's self-read machines) and new
`HeldValueTest::test_a_tick_that_moves_only_an_outer_source_holds_the_angle`
in `tests/test_running_reads.py`:

```text
>       self.assertEqual(sim.state['wheel.turn'], held)
E       AssertionError: 71.99999999999994 != 71.99999999999996
tests/test_running_reads.py:611: AssertionError
1 failed in 1.00s
```

**GREEN.** Both expressions parenthesized as
`own_left + (self._skeleton(s, branches) - base)`; nothing else in the
walk changed. `1 passed in 0.87s`.

**The strengthened contract test.**
`CurtaShapedTest.test_a_shift_away_and_back_preserves_every_part` now
asserts BIT-FOR-BIT equality for every block coordinate across the
lift/shift/drop sequence (`assertEqual`, not the run's agreement
window), and the old comment's diagnosis — that the levers land one ulp
on every cut — is removed: the levers' increments over those ticks are
exactly `0.0`; what moved was the dials, through `own_at`.

**One assertion had to be relaxed, and why.** In the same test, after
the reset cam returns the levers, `lever0.travel`, `lever1.travel` and
`lever2.travel` were asserted `== 0.0` and now rest at
`1.1102230246251565e-16`. That is not walk noise: the cam's law is
`-reset` while the carriage is lifted, so the lever's travel is one
minus the float sum of the command's ten increments, and a tenth added
ten times does not sum to one. Traced over the reset step:

```text
before the fix (ten ticks)  1.0, 0.9, 0.7999999999999999 ... 0.09999999999999987, 0.0
after  the fix (ten ticks)  1.0, 0.9, 0.8 ... 0.10000000000000009, 1.1102230246251565e-16
```

The old exact `0.0` was the walk's ulp error cancelling the command
bookkeeping's, not an exact answer; the same trace shows `dial3.turn`
going from `71.99999999999994` to exactly `72.0`. The cam drives each
lever exactly ONTO its own `travel > RETURNED` surface, which is the
reading design.md section 4 explicitly puts outside the exact promise
("exact only where the float is not on a knife edge"), so those three
assertions now use the agreement window and say so in the test. The
bit-for-bit assertions above them are taken away from every surface.

**The corpus.** Regenerated with
`tools/generate_running_corpus.py` after the fix: byte-identical to the
file the implementation produced before it, and against the corpus
committed at the planning commit `4045916`:

```text
top-level keys identical: True
  corpus unchanged: True
  generated_by unchanged: True
  tolerance unchanged: True
removed: []
added  : [('RangedBlock', 0.05, 8), ('ShiftedCarry', 0.05, 20)]
changed: []
order of the pre-existing entries preserved: True
```

No pre-existing entry moved by so much as an ulp; `19 scenarios over 16
machines, 356 ticks, 262355 bytes`.

### C2 — the membership assertion raised the wrong error

`MembershipInvariantError(RuntimeError)` added in `program.py` beside
`LandingInvariantError`, with a docstring saying it is an internal
invariant of the COMPILE and that it happens at construction, where
there is no tick. `_agree_on_membership` raises it, and its last
sentence is now "Construction refused the model." instead of "The tick
committed nothing."

RED, with the class in place and the raise still `LandingInvariantError`:

```text
E   solid_node.simulation.program.LandingInvariantError: the construction
    pre-pass marked the relations determining none as members of a block
    and the compile found carry.travel, higher.turn. ... The tick
    committed nothing.
1 failed, 5 passed
```

GREEN after the raise changed:
`MembershipTest.test_the_pre_pass_and_the_compile_must_agree` now also
asserts `Construction refused the model.` is present and `The tick
committed nothing` is not. It is NOT exported from
`solid_node.simulation`: that module's lazy table carries only
`UnsupportedLaw` and `TooManyCrossings`, and `LandingInvariantError` is
not there either.

### C3 — `_Block._refused`'s wording

"leaves both dependencies active" is wrong for a block of three or more
members. The message now says "leaves every dependency on this cycle
active"; every substring `RuntimeRefusalTest` asserts is untouched. The
message in full, measured:

```text
over the piece [0.5, 1.0] of this tick the relations (crank, shift,
higher.turn) drives lower.turn, (crank, shift, lower.turn) drives
higher.turn form a cycle the run cannot order: each waits on a
coordinate another determines, and the selection this piece was read
under leaves every dependency on this cycle active. The selectors read
lower.turn: >= on (shift - 0.5) reads 1.0; higher.turn: >= on
(shift - 0.5) reads 1.0. The tick committed nothing: the bank, the tick
count and the tree stand as they were.
```

### C4 — the two-input pushing blind spot is PRE-EXISTING

Measured here with the review's probe `two_input_push.py`, on a machine
with NO block; the output is quoted under "Out of scope" item 1 above,
which now states the finding as pre-existing. design.md section 7 gained
a paragraph stating the limit beside the "same machinery" sentence it
qualifies. No spec change: it is not new behaviour.

### C5 — the full suite

Recorded at the end of section 9.1.
