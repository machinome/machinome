# Evidence: applying `pin-the-block-order`

Every measurement below was taken on this worktree, branch
`pin-the-block-order`, base `0b0f02a`, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` and one job at a time.

Python: `PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python`.

## Group 1 — Red: record the finding on this tree

### 1.1 Spikes copied and re-run

`spikes/order.py`, `spikes/patched_corpus.py`, `spikes/gate_survey.py`,
`spikes/alternatives.py` and `spikes/regenerate.py` were already present
in the change's `spikes/` directory (carried by the planning commit
`c0b49bb`), together with `spikes/README.md`, `spikes/gates_debug.py`
and `spikes/crossings_dump.py`. Re-copying them from the scratchpad
produced no diff (`git status --short` clean before and after), so the
committed copies are byte-identical to the scratchpad originals. Each
was re-run from the worktree root; output below.

#### `order.py`

```text
tolerance: 1e-09 relative, window = tol * max(1, |a|, |b|)

### 1. The COMMITTED script (crank by 2.0 over 0.2 s)
    script: [{"tick": 1, "move": {"input": "crank", "by": 2.0, "duration": 0.2}, "handle": "h0"}, {"tick": 8, "move": {"input": "shift", "by": 1.0, "duration": 0.2}, "handle": "h1"}, {"tick": 14, "move": {"input": "crank", "by": 2.0, "duration": 0.2}, "handle": "h2"}]
    dt 0.05, 20 steps
    LISTING ORDER PASSES: every tick within the corpus tolerance, every discrete field equal
    in-block gate crossings strictly inside a tick (unpatched): 0
    final bank:
      carry.travel: producer 1.0 / listing 1.0
      clearing: producer 0.0 / listing 0.0
      crank: producer 4.0 / listing 4.0
      higher.turn: producer 3.5 / listing 3.5
      lower.turn: producer 2.0 / listing 2.0
      shift: producer 1.0 / listing 1.0

### 2. The CANDIDATE script (crank by 2.0 over 0.3 s)
    script: [{"tick": 1, "move": {"input": "crank", "by": 2.0, "duration": 0.3}, "handle": "h0"}, {"tick": 8, "move": {"input": "shift", "by": 1.0, "duration": 0.2}, "handle": "h1"}, {"tick": 14, "move": {"input": "crank", "by": 2.0, "duration": 0.3}, "handle": "h2"}]
    dt 0.05, 20 steps
    LISTING ORDER DIVERGES, 21 disagreement(s):
      tick 2 higher.turn: corpus 0.16666666666666669 vs listing order 0.0 (delta 0.166667)
      tick 2: 2 crossing(s) in the corpus, 1 under listing order
      tick 3 higher.turn: corpus 0.5 vs listing order 0.33333333333333337 (delta 0.166667)
      tick 4 higher.turn: corpus 0.8333333333333333 vs listing order 0.6666666666666669 (delta 0.166667)
      tick 4: 0 crossing(s) in the corpus, 1 under listing order
      tick 5 higher.turn: corpus 1.1666666666666667 vs listing order 1.0000000000000004 (delta 0.166667)
      tick 6 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      tick 7 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      tick 8 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      tick 9 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      tick 10 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      tick 11 higher.turn: corpus 1.5 vs listing order 1.3333333333333337 (delta 0.166667)
      ... and 9 more
    in-block gate crossings strictly inside a tick (unpatched): 1
      tick 2: higher.turn >= on 0.0 relation=(crank, shift, clearing, carry.travel, higher.turn) drives higher.turn t=0.49999999999999994
    final bank:
      carry.travel: producer 1.0 / listing 1.0
      clearing: producer 0.0 / listing 0.0
      crank: producer 4.0 / listing 4.0
      higher.turn: producer 3.5 / listing 3.3333333333333335   <-- DIFFERS
      lower.turn: producer 2.0 / listing 2.0
      shift: producer 1.0 / listing 1.0
```

Matches proposal.md's tables exactly: the committed script passes under
BOTH the listing order and (per proposal.md's table, taken previously on
this worktree) the reversed order; the candidate diverges by one sixth
of a turn from tick 2, never healing, final `higher.turn` `3.5` (producer)
against `3.3333333333333335` (listing).

#### `patched_corpus.py`

```text
Train            dt=0.05  PASSES under listing order
Train            dt=0.1   PASSES under listing order
Window           dt=0.05  PASSES under listing order
Remainder        dt=0.05  PASSES under listing order
Wrapped          dt=0.05  PASSES under listing order
Throwing         dt=0.05  PASSES under listing order
Clutch           dt=0.05  PASSES under listing order
CarryLead        dt=0.05  PASSES under listing order
CarryLead        dt=0.1   PASSES under listing order
Ratchet          dt=0.05  PASSES under listing order
Swept            dt=0.01  PASSES under listing order
TwoStops         dt=0.05  PASSES under listing order
StopAndJump      dt=0.05  PASSES under listing order
Clearing         dt=0.05  PASSES under listing order
Clearing         dt=0.1   PASSES under listing order
StoppedClearing  dt=0.05  PASSES under listing order
ShiftedCarry     dt=0.05  PASSES under listing order
RangedBlock      dt=0.05  DIVERGES (1)
Captured         dt=0.05  PASSES under listing order
```

19 scenarios; 18 pass under listing order, `RangedBlock` diverges once.

#### `gate_survey.py`

```text
machines supplying the feature today: []
```

No committed machine supplies `'an in-block gate crossing inside a
tick'`.

#### `alternatives.py`

```text
committed: dt=0.05 duration=0.2 steps=20 -> 0 disagreement(s), 0 in-block gate crossing(s) inside a tick, crossings=[]
    final higher.turn: producer 3.5 / listing 3.5
chosen   : dt=0.05 duration=0.3 steps=20 -> 21 disagreement(s), 1 in-block gate crossing(s) inside a tick, crossings=[(2, 'lower.turn', '>', 0.5), (2, 'higher.turn', '>=', 0.5)]
    first: tick 2 higher.turn: corpus 0.16666666666666669 vs listing order 0.0 (delta 0.166667)
    final higher.turn: producer 3.5 / listing 3.3333333333333335
alt 0.4  : dt=0.05 duration=0.4 steps=20 -> 0 disagreement(s), 0 in-block gate crossing(s) inside a tick, crossings=[]
    final higher.turn: producer 3.25 / listing 3.25
alt 0.15 : dt=0.05 duration=0.15 steps=20 -> 22 disagreement(s), 0 in-block gate crossing(s) inside a tick, crossings=[(1, 'lower.turn', '>', 0.75), (1, 'higher.turn', '>=', 0.75), (2, 'carry.travel', '<', 0.5), (2, 'higher.turn', '>', 0.5)]
    first: tick 1 higher.turn: corpus 0.16666666666666674 vs listing order 0.0 (delta 0.166667)
    final higher.turn: producer 3.5000000000000004 / listing 3.3333333333333335
dt=1.0, crank by 2.0 over 1.0 s: producer {'carry.travel': 1.0, 'clearing': 0.0, 'crank': 2.0, 'higher.turn': 1.0, 'lower.turn': 2.0, 'shift': 0.0}
                                  listing  {'carry.travel': 1.0, 'clearing': 0.0, 'crank': 2.0, 'higher.turn': 0.0, 'lower.turn': 2.0, 'shift': 0.0}
```

Matches design.md §1's table exactly.

#### `regenerate.py`

```text
top-level keys identical: True
  generated_by: True
  corpus: True
  tolerance: True
removed: []
added  : []
changed: [('ShiftedCarry', 0.05, 20)]
order preserved: True
ticks: 356 was 356
```

### 1.2 RED (the replay)

From `order.py` section 1 above: with `_Block._order` patched to return
the members in listing order, the COMMITTED `ShiftedCarry` entry replays
with **zero disagreements** — `LISTING ORDER PASSES: every tick within
the corpus tolerance, every discrete field equal`, and the final bank
matches on every coordinate (`higher.turn` producer `3.5` / listing
`3.5`).

Reversed order (from `proposal.md`, taken previously on this worktree
with the two block members swapped) also reproduces the corpus exactly
— design.md §3 explains why: reversed is `carry` before `higher`, which
is the order the producer itself uses while `shift < 0.5`.

### 1.3 RED (the whole corpus)

From `patched_corpus.py` above: all 19 committed scenarios were replayed
under the listing-order patch. 18 reproduce their bank exactly.
`RangedBlock dt=0.05` is the only disagreement. Isolated with a small
script (`compare()` from `spikes/order.py`, run standalone against just
that entry):

```text
tick 1: 3 crossing(s) in the corpus, 2 under listing order
```

The per-scenario table:

| scenario | dt | listing order |
| --- | --- | --- |
| Train | 0.05 | passes |
| Train | 0.1 | passes |
| Window | 0.05 | passes |
| Remainder | 0.05 | passes |
| Wrapped | 0.05 | passes |
| Throwing | 0.05 | passes |
| Clutch | 0.05 | passes |
| CarryLead | 0.05 | passes |
| CarryLead | 0.1 | passes |
| Ratchet | 0.05 | passes |
| Swept | 0.01 | passes |
| TwoStops | 0.05 | passes |
| StopAndJump | 0.05 | passes |
| Clearing | 0.05 | passes |
| Clearing | 0.1 | passes |
| StoppedClearing | 0.05 | passes |
| ShiftedCarry | 0.05 | passes |
| RangedBlock | 0.05 | **diverges (1)** — tick 1, 3 crossings vs 2 |
| Captured | 0.05 | passes |

### 1.4 RED (the guard)

Ran `uncovered_features` over the committed corpus (`tests/running-corpus.json`)
with `'an in-block gate crossing inside a tick'` appended to `REQUIRED`
in memory:

```python
import json, os, sys
sys.path.insert(0, os.getcwd())
import tools.generate_running_corpus as gen
fixture = json.load(open('tests/running-corpus.json'))
gen.REQUIRED = gen.REQUIRED + ('an in-block gate crossing inside a tick',)
missing = gen.uncovered_features(fixture['machines'])
print('missing:', missing)
```

Output:

```text
missing: ['an in-block gate crossing inside a tick']
```

Confirmed: the new feature is the ONLY entry missing (every other
`REQUIRED` feature is already covered by the committed corpus), matching
task 1.4's expectation exactly.

## Group 2 — The scenario

### 2.1 / 2.2 The script and its comment

`tools/generate_running_corpus.py`'s `ShiftedCarry` entry of `CORPUS`:
both `move` actions changed `'duration': 0.2` to `'duration': 0.3`.
Nothing else in the entry moved — `dt` stays `0.05`, `steps` stays `20`,
the shift move at tick 8 is untouched, all three handles unchanged. The
comment above the entry was extended to say what the script is FOR: the
gate the higher wheel reads on the lever now crosses strictly inside
tick 2, which is what makes the scenario discriminate the block's order.

### 2.3 Regenerate and diff

```text
$ PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python tools/generate_running_corpus.py
.../tests/running-corpus.json: 19 scenarios over 16 machines (Captured,
CarryLead, Clearing, Clutch, RangedBlock, Ratchet, Remainder,
ShiftedCarry, StopAndJump, StoppedClearing, Swept, Throwing, Train,
TwoStops, Window, Wrapped), 356 ticks, 263308 bytes
```

Diff against the pre-regeneration copy:

```text
top-level keys identical: True
  generated_by: True
  corpus: True
  tolerance: True
removed: []
added  : []
changed: [('ShiftedCarry', 0.05, 20)]
order preserved: True
ticks: 356 was 356
scenarios: 19 was 19
```

Exactly one entry changed, order preserved, 19 scenarios / 356 ticks —
matches the task's expectation exactly.

### 2.4 The document is untouched

```text
document byte-identical: True
version: 7
script differs: True
ticks differ: True
```

The regenerated `ShiftedCarry` entry's `document` is byte-identical to
the committed one and still publishes `version: 7`; only the `script`
and the recorded `ticks` (the run's own output) changed, confirming the
script is not part of the published document.

## Group 3 — The generator's refusal

### 3.1 `REQUIRED`

Appended `'an in-block gate crossing inside a tick'` to `REQUIRED`,
after `'a tick carrying both a selection crossing and a stop'` — the
last entry.

### 3.2 / 3.3 The derivation

Added `_in_block_names(edge, primitive, bindings, gives)` beside
`_selection` and `_member_of` in `tools/generate_running_corpus.py`: for
one edge's jumps carrying `primitive`, resolves each level's free names
transitively through `bindings` (the same walk `_selection` already
does) and splits them into GATES (naming a coordinate `gives` holds
other than the edge's own driven end) and SELECTORS (naming none of
`gives`), leaving a jump naming only the edge's own driven end (a
self-read) in neither list. No new import; `free_names` is reused.

In `uncovered_features`'s tick loop, next to the existing "selection
crossing" check (which already looks up `_member_of(program,
coordinate)` against `selectors`), added the per-crossing check: skip
the first tick (no preceding bank); for a crossing with `0 < t < 1`
whose determining edge is a block member (`index in selectors`), split
its jumps by `_in_block_names`; count the crossing when some gate's
in-block names moved across the tick and no selector's names moved or
named a coordinate the bank does not carry. No new document key is
read or written.

### 3.4 GREEN

```text
missing over regenerated corpus: []
missing without ShiftedCarry: ['an in-block gate crossing inside a tick']
```

`uncovered_features` over the regenerated corpus returns `[]`; with
`ShiftedCarry` removed it returns exactly the new feature and nothing
else, confirming the derivation is specific to that scenario's block.

## Group 4 — The tests

### 4.1 / 4.2 The new coverage-guard cases

Added to `tests/test_running_corpus.py::CoverageGuardTest`:

- `test_a_corpus_with_no_in_block_gate_crossing_is_refused`: drops
  `ShiftedCarry` and asserts the new feature is in `missing`, and that
  `'a switched source'` is NOT (since `RangedBlock` still carries a
  block).
- `test_a_corpus_with_no_in_block_gate_movement_is_refused`: every
  machine kept but `ShiftedCarry`'s crossings blanked, asserting the new
  feature is still missing.

```text
$ PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m pytest tests/test_running_corpus.py::CoverageGuardTest -q
...........
11 passed in 0.23s
```

All 11 `CoverageGuardTest` cases (9 pre-existing + 2 new) pass.

### 4.3 `BlockOrderTest`

Added `BlockOrderTest` to `tests/test_running_corpus.py`: replays the
`ShiftedCarry` entry twice — once unpatched, once with
`solid_node.simulation.program._Block._order` monkeypatched to
`tuple(range(len(self.members)))` for the duration of the `try/finally`
block and restored after — and compares every tick's bank against the
corpus under the corpus's own tolerance window
(`tolerance * max(1, |a|, |b|)`). Asserts the UNPATCHED replay
reproduces the corpus exactly (so the ordering assertion cannot pass by
breaking the fixture) and that the PATCHED (listing-order) replay
disagrees on at least one tick, naming the expected divergence
(`higher.turn` by one sixth of a turn from tick 2 onward) in the failure
message.

```text
$ PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m pytest tests/test_running_corpus.py::BlockOrderTest -q
.
1 passed in 1.07s
```

### 4.4 RED first

Since the worktree's `tests/running-corpus.json` is already regenerated
(task 2.3), `BlockOrderTest` was proven red against the COMMITTED
(pre-task-2) `ShiftedCarry` entry by loading the saved pre-regeneration
copy of the fixture (taken before task 2.3's `generate_running_corpus.py`
run) instead of the worktree's file, and running the same
replay/disagreement logic `BlockOrderTest` uses — `solid_node/` untouched,
only which JSON is loaded differs:

```text
unpatched disagreements (should be empty): []
patched disagreements against the OLD (committed) script: []
assertTrue(patched) would FAIL -- RED, as expected
```

The unpatched replay reproduces the old corpus exactly (0 disagreements,
consistent with 1.2's evidence), and the patched (listing-order) replay
ALSO reproduces it exactly (0 disagreements) — so `self.assertTrue(patched, ...)`
would fail on the committed script, which is the red state task 4.4
records. After task 2's script change, the same logic against the
regenerated corpus (task 4.3's run above) gives `patched` non-empty and
the test passes.

### 4.5 `test_running_corpus.py` and `test_running_document.py`

```text
$ PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m pytest tests/test_running_corpus.py tests/test_running_document.py -q
............... [ 12%]
....................................................................... [ 70%]
....................................                 [100%]
122 passed, 2 warnings, 150 subtests passed in 5.81s
```

The 2 warnings are pre-existing `FutureWarning`s from `assembly.py`
(deprecated driver reads in unrelated fixtures' `render()`), unrelated
to this change.

### 4.6 The named running and export suites

```text
$ PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m pytest tests/test_running_simulation.py \
  tests/test_running_jumps.py tests/test_running_document.py \
  tests/test_running_corpus.py tests/test_export.py \
  tests/test_docs_exports.py tests/test_node_lazy_exports.py -q
315 passed, 3 warnings, 618 subtests passed in 59.35s
```

Per-file breakdown (re-run individually, final check):

| file | passed | subtests |
| --- | --- | --- |
| `test_running_simulation.py` | 88 | 21 |
| `test_running_jumps.py` | 43 | 314 |
| `test_running_document.py` | 107 | 93 |
| `test_running_corpus.py` | 15 | 57 |
| `test_export.py` | 25 | 5 |
| `test_docs_exports.py` | 8 | 26 |
| `test_node_lazy_exports.py` | 29 | 102 |
| **total** | **315** | **618** |

`test_running_corpus.py`'s 15 tests: `CorpusReplayTest` (2),
`CorpusDocumentTest` (1), `CoverageGuardTest` (11, 9 pre-existing + 2
new), `BlockOrderTest` (1, new).

("the export tests" taken as `tests/test_export.py`,
`tests/test_docs_exports.py` and `tests/test_node_lazy_exports.py` — the
three files under `tests/` whose name names the export capability.) The
3 warnings are the same pre-existing `FutureWarning`s (two from
`test_running_document.py`, one from `test_export.py`'s own
`ExportAnimationTest`), unrelated to this change. No other suite can see
this change — nothing under `solid_node/` moved, and the corpus, the
generator and its tests are the only things this cycle touches — so the
full ~2930-test suite was not run, per the task.

## Group 5 — Records

### 5.1 Synced spec

`openspec/specs/export/spec.md`'s "The two runtimes share a conformance
corpus" requirement replaced with the change's delta content (the delta
supplied the full requirement body, so this was a block replacement
rather than a scenario-only merge). All 7 pre-existing scenario titles
carried unchanged (`The framework reproduces its own corpus`, `The
corpus carries the document it was run against`, `A corpus missing a
primitive is refused`, `Every tick is present`, `A corpus missing a
bound reading another coordinate is refused`, `A corpus missing a law
that reads its own driven coordinate is refused`, `A corpus missing a
switched source is refused`), plus 2 new ones (`A corpus missing an
in-block gate crossing is refused`, `The corpus catches a consumer that
runs a block in the published order`). Verified with
`openspec validate pin-the-block-order --strict` → `Change
'pin-the-block-order' is valid`.

### 5.2 `HISTORY.rst`

One bullet added under `Unreleased`, ahead of the `select-the-source`
entry, describing the corpus fix in the file's own voice.

### 5.3 `workflow/warts.md`

One bullet added at the end of the `select-the-source` section:
`**FIXED by `pin-the-block-order`: the corpus's `ShiftedCarry` scenario
did not discriminate the block's order.**`, with the measured numbers
(green under both listing and reversed order before; 21 disagreements,
one sixth of a turn of `higher.turn`, after the fix).

### 5.4 Note for the viewer's cycle

Recorded here and in the final report: `solid-node-viewer`'s own copy of
`tests/running-corpus.json` and its `REQUIRED` mirror in
`solid_node_viewer/widget/src/run/running-corpus.test.ts`
(`uncoveredFeatures`) are now stale against this cycle's regenerated
fixture and new feature. Refreshing them, and proving the browser worker
orders the block, is that repository's own cycle — proposal.md's
Non-goals already say so; this cycle does not touch
`solid-node-viewer/`.

### 5.5 Validation

```text
$ openspec validate pin-the-block-order --strict
Change 'pin-the-block-order' is valid
```

Archiving is the reviewer's task, not applied here.

### 5.6 ADR-122 amendment

Added `## Amendment, 2026-09-16 (`pin-the-block-order`)` to
`docs/adrs/NODE/ADR-122-a-selection-decides-which-sources-a-law-reads.md`,
after its `Consequences` section, in the style of ADR-105's amendment
paragraph: the `ShiftedCarry` scenario replayed green under the
published listing order (and under the members reversed) until this
cycle changed its script, with the measured numbers, and the decision
itself is stated as unchanged. `docs/adrs/README.md`'s ADR-122 status
row gained only the amendment note (`amended 2026-09-16 (the corpus
scenario meant to pin the block's order did not, until
`pin-the-block-order` changed its script)`) between `**Accepted**` and
`amends 106`. `docs/architecture.md` was not touched.

## Style

`flake8 tools/generate_running_corpus.py tests/test_running_corpus.py`
found two continuation-indent issues (E128) in the new code, fixed by
one extra space of hanging indent each. The one remaining warning
(`tests/test_running_corpus.py:215:80: E501`) is a pre-existing long
method name, unrelated to this change (confirmed present in `HEAD`
before any edit).

## Design contradictions found while applying

None. The ratified design's script, derivation and test all applied
exactly as specified; every measurement matched the proposal's and
design.md's own numbers.
