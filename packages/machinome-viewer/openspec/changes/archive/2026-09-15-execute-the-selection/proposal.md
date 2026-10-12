## Why

solid-node's ADR-122 lets a machine's dependencies be SELECTED by where
one of its own parts stands. The Curta's carry levers belong to the FIXED
frame and its number dials ride on the CARRIAGE, so the same lever is
tripped by dial `s` and advances dial `s + 1`, where `s` is the carriage
position the maker chose. At any one position the active dependencies are
a chain and acyclic; their UNION over the working positions is CYCLIC,
and the union is what the compiled program orders.

The producer compiles such a union as a **BLOCK** — the nontrivial
strongly connected components of the dependency graph over the edges'
`needs` and `gives`, a need an edge itself gives excluded, each
contracted to ONE entry — and orders that entry once per **PIECE** of a
tick rather than once per program. A **SELECTOR** is a jump node of a
member's law whose level reads nothing the block determines; a source is
**SWITCHED** when folding that node's branch to zero removes it from the
law. Over a stretch the selectors' crossings are located first, the
stretch is cut there, and on each piece the branches read at the midpoint
are FORCED into every member's own plan while the members are Kahn-ordered
over what the run-time fold leaves active.

Such a program is published as a **version 7** document with **NO new
key**. A consumer re-derives the block from the published edges' own
`needs` and `gives` and the selectors from each plan's published `level`
expressions, and — this is the breaking part — **the published order of a
block's members is a LISTING, not an execution order.**

The framework's requirement note item 7, "paired replay through the
independent viewer", is discharged by THIS cycle, in this repository,
against the corpus that change regenerated. ADR-110/111 is the standing
shape: one published program, one conformance corpus, two runtimes that
are one algorithm.

### What this viewer does with such a document today, measured

**In a real page it refuses it by name, which is correct.**
`RENDERED_VERSIONS` is `[1, 2, 3, 4, 5, 6]`
(`widget/src/viewer.ts:1824`) and `assertRenderable`
(`viewer.ts:1933-1942`) turns a version 7 document away before a single
pose is evaluated. The producer's own export says so: exporting the
framework's `tests/carriage_project/machine.py:CurtaCarriage` from a
throwaway copy of solid-node at `0b0f02a` printed

```text
WARNING - core.export - this model needs document version 7, and the
  installed browser viewer renders 1, 2, 3, 4, 5, 6 (solid-node-viewer
  0.1.0). The export is written anyway: an export is an artifact a LATER
  viewer may open, and a viewer that cannot read it refuses it by name
  rather than rendering part of a machine it does not understand.
```

**In the engine it does not refuse it at all — it executes the listing.**
`loadProgram` (`widget/src/run/program.ts:321-968`) reads no version
number, does no Kahn ordering and has no cycle detection anywhere: it
trusts `program.edges` in the order they are published and inverts
`gives` into `determiner` (`program.ts:715-718`), and `Run.pass`
(`run.ts:526-553`) walks `this.program.edges` in that order once per
stretch. So a block reaches the engine as an ordinary run of law edges in
the producer's LISTING order, which is exactly the silent wrong answer
ADR-122's table records.

Measured on this base, with the corpus's own `ShiftedCarry` document —
the note's reduced fixture, two wheels, one fixed lever and a live
`shift` — cranked by `2.0` in ONE tick of `dt = 1.0`:

| run | `lower.turn` | `higher.turn` | `carry.travel` |
| --- | --- | --- | --- |
| the producer at `0b0f02a` (ground truth) | `2.0` | **`1.0`** | `1.0` |
| this viewer, published listing order | `2.0` | **`0`** | `1.0` |
| this viewer, the block's two members swapped | `2.0` | **`1`** | `1.0` |

Nothing is reported in any case: no refusal, no crossing, no stop. The
carry is simply lost, and by a different amount for each order the
producer might have listed. (Ground truth from
`Sim(ShiftedCarry(), dt=1.0)` in a throwaway copy of solid-node at
`0b0f02a`; the viewer's two rows from `Engine.load` over the corpus's own
copy of that document, with and without `edges[1]` and `edges[2]`
exchanged.)

### The corpus gap, measured on this base

The committed copy at `solid_node_viewer/widget/src/running-corpus.json`
is stale by ONE framework regeneration, `select-the-source`. Compared
byte for byte with the framework's `tests/running-corpus.json` at
`0b0f02a`:

- committed: **17 scenarios, 14 machines, 328 ticks**; framework:
  **19 scenarios, 16 machines, 356 ticks**;
- added: `('ShiftedCarry', 0.05, 20)` and `('RangedBlock', 0.05, 8)`,
  inserted before `Captured`;
- removed: none; **changed: none** — every pre-existing scenario is
  byte-identical, and `generated_by`, `corpus` and `tolerance` are equal.

The framework's file replayed through the shipped engine on this base,
scenario by scenario, fails **exactly one** of the nineteen:

```text
× replays RangedBlock at dt=0.05 (scenario 18)
  → RangedBlock at dt=0.05, tick 1, the number of crossings:
    expected 3, got 2
```

and beyond the first assertion the same tick differs in three more ways:

| | the producer | this base |
| --- | --- | --- |
| crossings in tick 1 | 3 (`>=` at `t=0.25`, `>=` at `t=0.5`, `<` at `t=0.5`) | 2 (the `t=0.25` one missing) |
| the stop's fraction | `0.29999999999972715` | `0.3` |
| `spin`, `lower.turn` | `0.5999999999994543` | `0.6` |
| `h0` admitted | `0.5999999999994543` | `0.6` |

The cause is structural and is the second half of this cycle: `carry.travel`
is a block give, so `Edge.affine` is `False` on it at the producer
(`program.py:1605-1610`) and `Run._locate` takes `_searched`; the
consumer reads the MEMBER's published `affine: [true]` and takes
`piecewise` (`run.ts:852-861`), solving a bound on a value that is
re-ordered across the selector partition.

**`ShiftedCarry` replays GREEN on this base, and that is not evidence of
anything.** Its twenty ticks at `dt = 0.05` record no crossing at all,
and the one in-block dependency — the wheel's `carry.travel >= 0.5` gate
— never changes branch inside a tick: it is already open at the left end
of every tick in which the crank moves. Exchanging the two members in the
published listing changes not one float of that scenario, which is the
measurement that says so. The same document at `dt = 1.0` is the table
above. A corpus scenario that passes under two different orders proves
neither.

The width guard tells the same story from the other side. A JavaScript
mirror of the generator's own `_selection`/`_member_of` re-derivation,
run over both files, finds on the framework's file the blocks
`{higher.turn, carry.travel}` for both new machines — the pair ADR-122's
evidence group 8 names — with selector primitives `{<}` and `{>=}` for
`ShiftedCarry`, and reports all three of the producer's new required
features covered; over the committed file it reports all three
UNCOVERED. The existing `REQUIRED` tuple is satisfied by both files, so
nothing in the suite is red until it gains the three.

## What Changes

- **The loader re-derives the BLOCKS, and refuses what cannot be one.**
  `loadProgram` takes the strongly connected components of the graph over
  the published edges' `needs` and `gives` with `needs ∩ gives` excluded
  — the same exclusion it already makes for the self-read — by an
  iterative Tarjan in the published order, and contracts each nontrivial
  one into a compound `block` entry at the position of its first member.
  It does NOT trust the published listing to be contiguous: the order it
  executes is the one it derived. It refuses at load, by name and quoting
  the document, exactly what the producer refuses at construction: a
  wiring or a formula in a block, a member driving more than one
  coordinate, a member whose driven end is not a bank coordinate, and a
  block whose UNCONDITIONAL dependencies still form a cycle.
- **The loader re-derives each member's SELECTORS, fold and all.** A
  selector is a jump of a member's plan whose published `level`, closed
  over the document's bindings table and resolved transitively through
  the placeholders it names, reads no id the block gives. The FOLD sets
  every foldable selector's placeholder to zero in the published skeleton
  and folds `x*0→0`, `0*x→0`, `0/x→0`, `0+y→y`, `y+0→y`, `y−0→y`,
  `0−y→−y`; foldable is `floor`, `ceil`, `%` and the comparisons and NOT
  `sign`, whose zero is a point rather than an interval. One all-zero
  fold per member gives its unconditional in-block reads, and what the
  unfolded reads have beyond them is what a selection can switch.
- **A tick runs a block PIECE BY PIECE.** Every member's selector
  crossings are located over the whole stretch through the existing
  partition, on a plan of that member's selectors alone, and merged into
  ONE cut list in the members' order and each member's postorder. On each
  piece every selector's branch is read at the MIDPOINT, the run-time
  fold gives each member's active in-block reads, Kahn over those gives
  the order — memoised per branch VALUE vector — and the members run over
  the piece with their in-block values carried forward. A still-cyclic
  piece refuses the tick with the producer's message word for word.
- **A selector is a CONSTANT on a piece.** The branch the block read is
  SUBSTITUTED into the member's own plan through a new `forced` map,
  threaded to exactly the two points the producer threads it to:
  `partition` skips locating a forced node's crossings, and `branchesAt`
  returns the forced value. Everything downstream — the walk's two
  layers, its probe, its cuts, its far-side landing — reads the same
  `branches` map and inherits it.
- **What a block reports.** For a coordinate any piece LANDED, the
  ABSOLUTE value the block advanced it to by the stretch's END — the
  landing plus every later piece's increment — because `Run.landed`
  commits a reported landing absolutely and would otherwise discard the
  motion after it. `affine` is FALSE on every give of a block, so a stop
  on a block coordinate is SEARCHED. Crossings are rescaled
  `a + t·(b − a)` out of their piece and the whole located list is sorted
  by fraction before it reaches the record.
- **The walk's arithmetic is parenthesised**, here as on the producer:
  `Walk.run`'s `ownAt` closure (`jumps.ts:566-567`) and `Walk.probe`
  (`jumps.ts:700`) compute `ownLeft + (S − base)`, not
  `(ownLeft + S) − base`, so a piece whose skeleton does not move adds a
  true zero instead of an ulp. This is a behaviour change for VERSION 6
  documents too and it is what makes "a selection change alone moves
  nothing" a bit-for-bit promise rather than an approximate one.
- **`run.ts` does not change in shape**, and that is a claim with a
  reason: the producer's `run.py` did not either. `pass`, `landed`,
  `locate`, `along`, `groupOf` and `pushes` meet a block through the edge
  interface they already call, and `pushes`'s `edge.gives.includes(key)`
  break happens AFTER the whole block has run under one input's
  displacement, which is what makes an input coupled only through an
  inactive selection not stopped.
- **`documentVersions` becomes `[1, 2, 3, 4, 5, 6, 7]`** and the declared
  widget API version rises **15 → 16**: executing a version 7 document is
  a capability a host may require before it mounts a bundle that would
  refuse the Curta's carriage by name. `bundle.py`'s
  `RELEASED_DOCUMENT_VERSIONS` does not move. `capture.py`'s
  `carries_program` (`capture.py:71-73`) and `viewer.ts`'s program gate
  (`viewer.ts:1962`) are already FLOORS at version 5 and need no change —
  checked, not assumed.
- **The committed conformance corpus is replaced by the framework's
  regenerated one** — 19 scenarios over 16 machines, 356 ticks — and
  replayed green; the width guard gains the producer's three new required
  features (`a switched source`, `a selection crossing inside a tick`,
  `a tick carrying both a selection crossing and a stop`), re-derived as
  the generator's own `_selection`/`_member_of` do.
- **The Curta's carriage runs in a real page.** The framework's
  `tests/carriage_project/machine.py:CurtaCarriage` — four dials, three
  fixed levers, the lift, and an interlock `Bound(..., reads=)` on the
  carriage's own joint — exports at `0b0f02a` as a 32,791-byte version 7
  document whose nine law edges hold ONE block of seven. It is committed
  as `tests/fixtures/carriage/`, mounted in Chromium, lifted, shifted,
  dropped and cranked, and read back against the producer's own numbers.
- **Not** a change to the document's shape, to the framework, or to the
  contract between the two packages. No new document key exists to read:
  the block is `needs`/`gives` and the selectors are the published
  `level` expressions.

## Capabilities

### New Capabilities

None. This cycle widens capabilities the viewer already has.

### Modified Capabilities

- `viewer-package`: **ADDED** — "The worker orders a block per piece":
  the re-derived block and its selectors, the fold, the four load-time
  refusals, the per-piece ordering and its run-time refusal, the forced
  branch, the advanced absolute a block reports, and the searched stop.
  **MODIFIED** — "One loader reads either published document" (the
  rendered version list becomes 1–7, and what a version 7 document
  carries); "The viewer declares its API version" (16); "The step
  reproduces the producer's own integration" (a block's contribution, its
  landing and its stop); "A program the viewer cannot execute is refused
  by name" (the four block shapes refused at load); "The two runtimes
  agree on a conformance corpus" (the three features the producer's
  generator now requires); "The worker executes a law that reads the
  coordinate it drives" (the walk's own arithmetic, and the forced
  selector a member holds through it).

## Impact

- `solid_node_viewer/widget/src/run/program.ts` — the block
  re-derivation (Tarjan over `needs`/`gives`), the contraction into a
  `block` edge with its `ProgramBlock` reading, the selector derivation,
  the fold, the unconditional and switched sets, and the four load-time
  refusals; `EdgeKind` gains `block`.
- `solid_node_viewer/widget/src/run/jumps.ts` — the `forced` parameter on
  `partition`, `branchesAt`, `planIncrement`, `planCuts`,
  `retainedIncrement`, `retainedCuts` and `Walk`; and the parenthesised
  `ownAt`/`probe`.
- `solid_node_viewer/widget/src/run/edges.ts` — `edgeIncrements` and
  `edgeCuts` route a `block` edge to the block; `edgeValues` returns
  nothing for one.
- `solid_node_viewer/widget/src/run/run.ts` — no structural change; the
  block reaches `pass`, `landed`, `locate`, `along`, `groupOf` and
  `pushes` through the interface they already call.
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS`.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi`,
  `solidNodeDocumentVersions`; `src/version.test.ts`.
- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  producer's regenerated copy; `src/run/running-corpus.test.ts` — the
  census and the width guard; `src/run/cost.test.ts` — what a block tick
  costs.
- `tests/fixtures/carriage/` (new), `tests/support.py`, and a new
  Playwright acceptance beside `tests/test_clearing_document.py`.
- `CHANGELOG.md` under `0.2.0 — unreleased`, `README.md`'s version
  claims; `docs/adrs/EXPORT/ADR-058`, extracted after implementation, and
  `docs/adrs/README.md`.
- Nothing in the framework, nothing in another checkout, and nothing of
  the document's shape.
