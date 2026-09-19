## Why

ADR-122 made a selected cycle a BLOCK and ordered its members ONCE PER
PIECE of a tick, and it named the conformance corpus (ADR-111) as the
thing that pins that order between the framework's run and any other
runtime: "a consumer must re-derive the block from `needs` and `gives`
… one that executes the published order moves the machine by whatever
that order happens to give — silently". The scenario the cycle added for
the block, `ShiftedCarry`, does not pin it.

**Measured on this worktree** (`spikes/order.py`, `spikes/patched_corpus.py`;
`_Block._order` monkeypatched at RUNTIME to return the members in the
order they are LISTED — exactly what a consumer that ignored ADR-122 and
executed the published edges in order does):

| scenario | listing order | reversed order |
| --- | --- | --- |
| `ShiftedCarry`, dt 0.05, 20 ticks | **reproduces the corpus exactly** | **reproduces the corpus exactly** |
| `RangedBlock`, dt 0.05, 8 ticks | one disagreement: 2 crossings in tick 1, not 3 | bank diverges (`crank`, `higher.turn` `0.0` vs `1.0`), a stop lost, `h2` `blocked` vs `completed` |
| the other 17 scenarios | reproduce exactly | reproduce exactly |

So across the whole committed corpus the LISTING order — the single most
likely wrong answer, and the one a version 6 consumer gives for free —
reproduces **every committed bank value, every stop, every command status
and every admitted travel**. The one thing it gets wrong anywhere is the
COUNT of crossings in one tick of one other scenario. The scenario
written FOR the block agrees with the producer under BOTH orders of the
two members its block has — the machine declares three laws, and the
block is the pair `{higher.turn, carry.travel}`; `lower.turn` is ordered
ahead of it as an ordinary edge.

The reason is in the script. `ShiftedCarry` cranks by `2.0` over `0.2 s`
at `dt = 0.05`: four ticks of `0.5`, so the lever's `carry.travel`
reaches its `>= 0.5` detent EXACTLY at the end of tick 1. The block's one
in-block dependency — the higher wheel reads the lever the lower wheel
pushes — is therefore either shut for a whole tick or open for a whole
tick, never crossing inside one, and the run records **no crossing at all
in twenty ticks**. Reading the gate at the left end of a tick and reading
it after the lever has advanced within that tick give the same answer, so
the order cannot matter.

The originating evidence is the viewer cycle `execute-the-selection`
(`solid-node-viewer`, commit `5a3e1d7`, 2026-09-15), whose worker
executes a version 7 document: its replay of this corpus was green
before its block ordering was written. The producer-side reproduction is
`spikes/order.py` on this worktree.

## What Changes

- **`ShiftedCarry`'s corpus script cranks by `2.0` over `0.3 s` instead
  of `0.2 s`.** Six ticks of `1/3`, so `carry.travel` reaches `0.5` at
  one and a half ticks and the gate the higher wheel reads crosses
  STRICTLY INSIDE tick 2. Everything else stands: the same machine, the
  same `dt`, the same twenty steps, the same shift at tick 8 and the
  same second crank at tick 14. Measured (`spikes/order.py`), the
  producer now records two crossings inside tick 2 — the lower wheel's
  own self-read clearing surface at `t = 0.5000000000000001`, and the
  in-block gate `carry.travel >= 0.5` under the higher wheel's relation
  at `t = 0.49999999999999994` — and the listing order DIVERGES:

  | tick | `higher.turn`, producer | `higher.turn`, listing order |
  | --- | --- | --- |
  | 2 | `0.16666666666666669` | `0.0` |
  | 3 | `0.5` | `0.33333333333333337` |
  | 6 | `1.5` | `1.3333333333333337` |
  | 20 | `3.5` | `3.3333333333333335` |

  One sixth of a turn, from the first tick the gate crosses inside, and
  it never heals: the listing order reads the lever BEFORE the lower
  wheel has pushed it through the detent and loses the half tick. The
  crossing itself moves from tick 2 to tick 4. Twenty-one disagreements
  in twenty ticks, against zero today.

- **The generator gains one REQUIRED feature, `'an in-block gate
  crossing inside a tick'`,** derived from the published document and
  the tick log exactly as the existing entries are, with the block and
  its members re-derived as a consumer must. A GATE of a block member is
  a jump whose level reads a coordinate ANOTHER member determines — the
  member's own driven end excluded, because ADR-121's self-read imposes
  no order. The corpus today supplies it from NO machine
  (`spikes/gate_survey.py`), so the generator would refuse the corpus as
  committed; with the new script `ShiftedCarry` supplies it.

- **One framework test pins the discrimination itself**, rather than
  trusting the feature list: `ShiftedCarry` replayed with `_Block._order`
  returning the members in listing order must DIFFER from the corpus
  beyond `_TOLERANCE` on at least one tick's bank, while the unpatched
  replay reproduces it. Red first on the current script, where the
  patched replay PASSES.

- **The export capability states the new feature** in the generator's
  refusal list. `simulation` is untouched: nothing about the run changes.
  No ADR — a corpus script and a coverage guard decide nothing about the
  architecture; ADR-122 already decided that the published order is not
  an execution order, and this change makes the corpus say so.

- **Nothing else changes**: no `solid_node/` source, no document, no
  version, no other corpus entry. Measured (`spikes/regenerate.py`):
  regenerating with the new script gives `removed: []`, `added: []`,
  `changed: [('ShiftedCarry', 0.05, 20)]`, the pre-existing entries'
  order preserved, 19 scenarios and 356 ticks as before.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `export`: ONE MODIFIED requirement, "The two runtimes share a
  conformance corpus" — the generator's refusal list gains an in-block
  gate crossing located strictly inside a tick, and one scenario is added
  for it. Every existing scenario of that requirement is carried
  unchanged under its exact title.

## Impact

- `tools/generate_running_corpus.py`: `CORPUS`'s `ShiftedCarry` entry
  (one `duration`, twice), one `REQUIRED` entry, and the derivation for
  it in `uncovered_features`.
- `tests/running-corpus.json`: regenerated; the `ShiftedCarry` entry only.
- `tests/test_running_corpus.py`: the narrowed-corpus test for the new
  feature, and the ordering test that replays `ShiftedCarry` under a
  patched `_Block._order`.
- `openspec/specs/export/spec.md`: one requirement, through the delta.
- `HISTORY.rst`: one line.
- `workflow/warts.md`: the finding recorded under the `select-the-source`
  section as FIXED by this cycle.
- No ADR. `docs/adrs/` and `docs/architecture.md` are untouched, and so
  is every file under `solid_node/`.

### Non-goals

- **Refreshing the viewer's copy of the corpus.**
  `solid-node-viewer` commits its own copy of `tests/running-corpus.json`
  and its own mirror of `REQUIRED` in
  `solid_node_viewer/widget/src/run/running-corpus.test.ts`
  (`uncoveredFeatures`, commit `5a3e1d7`). Both need the same update —
  the regenerated fixture and the same REQUIRED entry — in that
  repository's own cycle, and it is that cycle, not this one, that proves
  the browser worker orders the block. Until it lands, the viewer's copy
  is the OLD corpus and still passes there; nothing this cycle does can
  break it.
- **Changing what the run does.** `_Block._order` and everything else
  under `solid_node/` is correct and untouched; what is wrong is the
  script that was supposed to exercise it.
- **Making `RangedBlock` discriminate more.** Its one crossing-count
  disagreement is real and stays; this cycle fixes the scenario written
  for the block rather than adding a second one.
- **A generator that DERIVES which jump a crossing came from by
  evaluating levels.** The corpus publishes a crossing's `primitive` and
  its surface `level` (always `0.0` for a comparison), not the jump's
  identity; design.md §2 records why the feature is derived from the
  member's jumps and the tick's own bank instead, and what that
  derivation deliberately refuses to count.
- **A second order patch in the test.** Reversed order also reproduces
  the corpus today and is recorded above as evidence; the test pins the
  LISTING order, which is the order a document actually publishes.
