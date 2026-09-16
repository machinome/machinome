## Why

This viewer's `execute-the-selection` cycle (commit `5a3e1d7`) made the
worker execute a version 7 document: it re-derives a BLOCK from the
published edges' own `needs` and `gives`, re-derives each member's
SELECTORS from the published `level` expressions, and orders the members
ONCE PER PIECE of a step, because the published order of a block's
members is a LISTING and not an execution order. Its own tasks 0.3
recorded the hole in the evidence for that:

> `ShiftedCarry` replays GREEN — and so it does with its two block
> members EXCHANGED in the published listing, which is the measurement
> that says the scenario does not discriminate the ordering at all.

That finding went back to the producer, which fixed it in the framework
cycle `pin-the-block-order` (solid-node `d3c2242`, five ahead of
`8e15791`, stacked on `select-the-source` `0b0f02a`). The producer
changed ONE script — `ShiftedCarry` now cranks `2.0` over `0.3 s`
instead of `0.2 s`, so the higher wheel's `carry.travel >= 0.5` gate
crosses STRICTLY INSIDE tick 2 rather than landing on a tick boundary —
added one REQUIRED feature to its generator, `'an in-block gate crossing
inside a tick'`, and added its own `BlockOrderTest` pinning the
discrimination directly. Its proposal's Non-goals names this repository
and this cycle:

> `solid-node-viewer` commits its own copy of `tests/running-corpus.json`
> and its own mirror of `REQUIRED` … Both need the same update … in that
> repository's own cycle, and it is that cycle, not this one, that proves
> the browser worker orders the block.

So this cycle takes the refreshed corpus and the refreshed guard, and —
because the engine here is a second implementation and not a second copy
— proves against this engine what the producer proved against its own.

### What this viewer does today, measured on the base

Base: worktree `solid-node-viewer/WTs/mirror-the-gate-guard`, branch
`mirror-the-gate-guard`, base `5a3e1d7` (package `0.2.0` unreleased,
`solidNodeViewerApi: 16`, `solidNodeDocumentVersions: [1..7]`, highest
ADR 058). `npm test` → 36 files, 922 tests, 51.42 s; `npm run typecheck`
clean; `npm run build` → `dist/solid-widget.js` 723.9 kb (741,244 bytes).

**The committed corpus copy is stale by exactly one regeneration.**
Compared with the framework's `tests/running-corpus.json` at `d3c2242`:

- both files: **19 scenarios, 16 machines, 356 ticks**; `generated_by`,
  `corpus` and `tolerance` equal; the scenario keys
  `(name, dt, steps)` equal and in the same order;
- added: none; removed: none; **changed: exactly
  `('ShiftedCarry', 0.05, 20)`** — its `script` cranks over `0.3 s`
  where the committed copy cranks over `0.2 s` (twice, `h0` and `h2`),
  and 10 of its 20 ticks moved with it. Its `document` is BYTE-IDENTICAL,
  key order included, and still declares `version: 7`.

**The replay is already green over the new file, and that is the good
news.** The framework's file at `d3c2242`, replayed scenario by scenario
through the shipped engine on this base: **all 19 green**, the new
`ShiftedCarry` ticks included — `higher.turn` `0.16666666666666669` at
tick 2 where the stale entry commits `0.5`, and two crossings in tick 2
where the stale entry records none. Nothing in the engine needs to
change: it already orders each piece from the published edges, which is
what ADR-058 built. The whole widget suite with the new file in place is
green too — 36 files, 922 tests — so the corpus swap alone breaks
nothing, and `running-corpus.test.ts` is the only test file that reads a
scenario's `script` or `ticks` at all (six others read only the
byte-identical documents).

**The guard does not know the producer's new feature, and that is the
bug.** `uncoveredFeatures` in
`solid_node_viewer/widget/src/run/running-corpus.test.ts` mirrors the
generator's `REQUIRED` and its `_selection`/`_member_of` re-derivation.
Measured with the producer's new entry appended to `REQUIRED` and its
detection NOT yet mirrored:

| corpus | `REQUIRED` + the feature, no detection | + the detection mirrored |
| --- | --- | --- |
| the producer's at `d3c2242` | `['an in-block gate crossing inside a tick']` | `[]` |
| this viewer's committed copy | `['an in-block gate crossing inside a tick']` | **`['an in-block gate crossing inside a tick']`** |

The second row is what makes the corpus refresh load-bearing rather than
cosmetic: with the detection mirrored, the copy committed here does not
supply the feature at all, and `ShiftedCarry` is the ONLY machine of the
producer's 19 scenarios that supplies it — exactly what the producer's
own `spikes/gate_survey.py` found on its side.

**And this engine does discriminate the order — measured, not assumed.**
The block reaches the run through `ProgramEdge.block`, a mutable field of
the loaded program whose `ProgramBlock.activeReads` the suite already
substitutes (`run/jumps.test.ts:1079-1091`), and `Engine`'s constructor
takes a `LoadedProgram` (`run/engine.ts:37`). A substitute whose
`activeReads` answers the EMPTY SET makes every member ready at once, so
the Kahn loop in `blockOrder` (`run/jumps.ts:1142-1162`) returns the
members in the order they are stored — which is the published listing
order, because the components come back with each one's indices sorted
ascending (`run/program.ts:547-601`) and `_blocked` never re-sorts them
(`run/program.ts:1380-1399`).
Replaying the corpus's own scripts through `Engine` that way:

| scenario | per-piece order | listing order |
| --- | --- | --- |
| `ShiftedCarry` at `d3c2242` | reproduces the corpus | **21 disagreements** |
| `ShiftedCarry`, the stale copy | reproduces the corpus | **0 disagreements** |
| `RangedBlock` (either copy) | reproduces the corpus | 1 (tick 1's crossing COUNT) |

The first listing-order disagreements on the new entry are
`tick 2 higher.turn: corpus 0.16666666666666669, run 0`;
`tick 2 crossings: corpus 2, run 1`;
`tick 3 higher.turn: corpus 0.5, run 0.33333333333333337`. One sixth of
a turn, from the first tick the gate crosses inside, and it never heals —
the producer measured the same 21 disagreements and the same floats on
its side. On the stale copy the same substitution changes nothing at all,
which is the finding this cycle closes, reproduced in this engine.

## What Changes

- **The committed corpus is replaced by the producer's at `d3c2242`,
  BYTE FOR BYTE.** Nothing here edits it, ever; the census is unchanged
  (19 scenarios, 16 machines, 356 ticks), so `running-corpus.test.ts`'s
  census assertion does not move.
- **The width guard gains the producer's new required feature**,
  `'an in-block gate crossing inside a tick'`, appended to `REQUIRED` in
  the producer's own position and spelling, after `'a tick carrying both
  a selection crossing and a stop'`.
- **Its detection mirrors `tools/generate_running_corpus.py`'s
  `_in_block_names` and the previous-bank rule exactly**: a crossing
  located strictly inside a tick (`0 < t < 1`, the first tick of a
  scenario skipped because it has no predecessor), under a coordinate
  whose determining edge is a block member; that member's jumps carrying
  the crossing's primitive, their levels closed over the document's
  bindings table and resolved transitively through the placeholders they
  name, split into GATES — naming a coordinate the block gives OTHER than
  the member's own driven end, ADR-121's self-read excluded because a
  self-read imposes no order — and SELECTORS, naming none of the block's
  gives; and the crossing counts when some gate's in-block name MOVED
  across the tick and no such selector reads anything that moved or
  anything the tick's bank does not carry. It is a SECOND deliberate copy
  beside `loadProgram`'s own derivation, for the reason the file already
  gives: the guard must be red on a narrowed corpus even when the engine
  is broken.
- **The narrowed-corpus test names the new feature**, as it already names
  the self-read's three and one of the selection's three.
- **A viewer-side order-discrimination test mirrors the producer's
  `BlockOrderTest`**, and NO seam is added to the engine to make it
  possible: it substitutes a `ProgramBlock` whose `activeReads` answers
  the empty set into the loaded program, replays `ShiftedCarry`'s own
  corpus script through `Engine`, and asserts that the substituted replay
  disagrees with the corpus by more than the stated tolerance on at least
  one tick's bank while the unsubstituted replay reproduces it. That
  second half is what stops the first from passing by breaking the
  fixture.
- **Nothing about what the viewer reads or executes changes.**
  `solidNodeViewerApi` stays 16, `solidNodeDocumentVersions` stays
  `[1..7]`, `RENDERED_VERSIONS` stays `1–7`, and no line of ENGINE
  source changes — `program.ts`, `jumps.ts`, `edges.ts`, `run.ts`,
  `engine.ts` and `viewer.ts` are untouched, and the only file under
  `src/run/` this cycle edits is `running-corpus.test.ts`: this is a
  corpus copy and a guard mirror. No
  ADR — a fixture refresh and a coverage guard decide nothing about the
  architecture, and ADR-058 already decided that the published order is
  not an execution order.
- **The Python side is untouched and its suite is unaffected**: the
  corpus is a widget test fixture, imported only by TypeScript test
  files, it is not in `dist/solid-widget.js` (no `src/` module imports
  it) and it is not packaged — `bundle.py`, `server.py` and `capture.py`
  never see it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: ONE MODIFIED requirement, "The two runtimes agree on
  a conformance corpus" — the width the suite asserts gains an in-block
  gate crossing located strictly inside a step, and the corpus SHALL
  discriminate the order in which a block's members are run. Every
  existing scenario of that requirement is carried unchanged under its
  exact title.

## Impact

- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  framework's file at `d3c2242`, byte for byte.
- `solid_node_viewer/widget/src/run/running-corpus.test.ts` —
  `REQUIRED`, the `inBlockNames` mirror and its detection in
  `uncoveredFeatures`, the narrowed-corpus assertion, and the
  order-discrimination test.
- `CHANGELOG.md` under `0.2.0 — unreleased`: one bullet.
- `openspec/specs/viewer-package/spec.md`: one requirement, through the
  delta.
- Nothing under `solid_node_viewer/widget/src/run/` other than that test
  file; no `package.json` version, no `README.md` version claim, no ADR,
  nothing in the framework, and nothing in another checkout.

### Non-goals

- **Making `RangedBlock` discriminate more.** Its one crossing-count
  disagreement under listing order is real, is reproduced here, and
  stays; the producer fixed the scenario written for the block rather
  than adding a second one, and this cycle mirrors that choice.
- **Adding an ordering seam to the engine.** None is needed (measured
  above), and an exported knob whose only caller is a test would be a
  production interface invented for a fixture.
- **Re-deriving the feature from the engine's own block.** The guard
  reads the corpus's documents and tick logs only, exactly as it already
  does for the self-read and the selection, so it stays red on a narrowed
  corpus even when `loadProgram` is broken.
- **Changing the engine, the document ladder, or the API version.**
  Nothing about what the viewer reads or executes changes.
