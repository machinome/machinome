## Why

The pilot drove the operating Curta in the studio and found it "still
very slow" in the browser. That machine is
`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`, HEAD
`9fb725f`, published as `simulation.running:OperatingCurta` — a version 7
document with 208 coordinates, 268 law edges, 547 branch placeholders,
8 594 shared bindings and 148 pieces. It is the largest running document
this viewer has ever been asked to execute, and it is the one the studio
opens.

The producer answered its own half of that finding on 2026-09-16 in two
framework cycles, both accepted and on `solid-node`'s `curta-speed`
worktree (`c3f3348`, `debd760`):

- **ADR-123, `cut-at-the-kink`**: `abs`, `min` and `max` are KINKS, and a
  kinked quantity is solved at its own breakpoints rather than searched.
  It explicitly left the published `affine` flag two-valued and left this
  viewer searching such a quantity — "correct, and slower".
- **ADR-124, `evaluate-only-what-moves`**: a quantity FOLLOWED along a
  tick's path is evaluated as a path — the standing part computed once
  per piece, only the moving cone per point, bit-identical. The Curta's
  Python tick fell 3.279 s → 0.727 s. Its Consequences name this
  repository:

  > The viewer's TypeScript run has the same whole-graph-walk shape and
  > would take the same win, with no document or flag change owed to it —
  > a finding for solid-node-viewer, not proposed here.

This cycle takes that win. It is the FIRST of three the measurements
below separate; the other two are named under Non-goals with the numbers
that put them there.

### What this viewer does today, measured on the base

Base: worktree `solid-node-viewer/WTs/curta-speed`, branch `curta-speed`,
base `4be96e5` (package `0.2.0` unreleased, `solidNodeViewerApi: 16`,
`solidNodeDocumentVersions: [1..7]`, highest ADR 059). Bench: node
v24.11.1, the engine bundled by esbuild and loaded in-thread, which is
how `workflow/warts.md`'s own numbers were taken. The document is the
project's own `_build_running/viewer.json`
(sha256 `16fe9ce6…5cd5a2af`, 1 168 517 bytes), copied out of the project
and read-only.

Step `1/240` s, the viewer's own `DEFAULT_DT`. Three runs each, 100 idle
ticks then the document's own `Turn crank` instruction and 60 more:

| | idle tick | crank tick |
| --- | --- | --- |
| ms/tick | **18.27 / 19.13 / 19.32** | **156.70 / 160.61 / 161.63** |
| DAG nodes computed per tick | 20 513 | 1 428 635 |

Those two counts reproduce `workflow/warts.md`'s to the unit (20 513 and
1 392 215 at a shorter crank), so this is the wart's own bench.

**Where the time goes.** `node --cpu-prof` over the same two runs,
attributed to the nearest enclosing evaluation SITE:

| site | idle | crank |
| --- | --- | --- |
| `Walk.skeletonAt` — a self-read law's skeleton | 0.1 %¹ | **66.6 %** |
| `Walk.levelOfJump` — a dependent jump's level | 0.1 %¹ | **13.1 %** |
| `branchesAt` / `levelAt` — a plan partition's levels | **63.8 %** | 8.9 % |
| `blockIncrements`, the rest | 17.5 % | 2.4 % |
| everything else (`advance`, load, GC) | 18.6 % | 9.0 % |

¹ An idle tick reaches neither: the whole self-read walk is 0.10 % of
it, because a walk over a step in which no source moves returns zero
without evaluating the law.

And by self time, `nest` is 40.6 % of an idle tick and 16.0 % of a crank
tick — the wart's 40.1 % / 20.0 %, reproduced.

**That is the producer's own shape.** ADR-124 measured 55.1 % + 22.5 % =
77.6 % of a Python tick inside the same two sites; this engine measures
66.6 % + 13.1 % = 79.7 %. And the decisive ratio is the same: of a
searched skeleton's **680** interned DAG nodes only **104 move** along
the tick's path (15.3 %; 1 560 of 9 951 over all fifteen followed
skeletons), against ADR-124's 57 of 511. Eighty-five per cent of every
evaluation was this engine recomputing a float that stands.

**And the cost is entirely inside two blocks.** The document loads as 223
entries: 2 blocks with 47 members and 425 selectors, 22 free plans, and
**32 laws that read the coordinate they drive**, every one of them a
block member, none published affine. Over 20 crank ticks all 40 040
skeleton evaluations, all 40 624 level evaluations and all 600 searches
are under **15** of those 32 coordinates — the tens sliders of the carry
mechanism. An idle tick evaluates nothing of them: its 20 513 nodes are
the two blocks' selector partition, which is re-located whether or not
anything moves.

## What Changes

**A quantity this viewer FOLLOWS along a step's path is evaluated as a
PATH.** The part of its expression that reads no name the step moves is
computed ONCE per piece and read back at every point of that piece; only
the moving cone is evaluated per point. Which names move is the run's own
`delta`, never inferred. The arithmetic is unchanged — the same nodes, in
the same order, through the same operator table, on the same operand
values — so every float is the float the whole-graph walk gives, bit for
bit.

Five call sites of `src/run/jumps.ts` follow a quantity, and all five
take it:

- `Walk.skeletonAt` — one path value per walk, re-bound per piece on the
  piece's own `branches`;
- `Walk.levelOfJump` — one per dependent jump, whose moving names are the
  step's plus the driven coordinate, because the walk hands that
  coordinate its own value at every point;
- `branchesAt`, `crossingsOf`/`bisect` through `levelAt`, and the walk's
  outer layer — one path value per jump per scope, held in a `LevelPaths`
  built where the scope is and dropped with it, re-bound whenever the
  piece identifying it changes.

Nothing outlives the step: a path value is built where the path is known
and dropped with it, so there is no cache to go stale and no question
about when it does.

**A path value resolves a name against the run's FLAT bank.** The whole-
graph evaluator reads a qualified id as member access and so needs the
bank nested at every segment, which is why `evaluateExpression` calls
`nest(values)` on every call — 67 261 id segments split and allocated per
idle tick, for 20 513 arithmetic nodes. A path value reads
`values['units.drum.turn']` directly. The two agree because
`loadProgram` already refuses, through `assertNestable`, the one id shape
that could make them disagree: an id that is a strict prefix of another.
This retires the larger part of `workflow/warts.md`'s scope-rebuild
finding as a side effect rather than as a separate mechanism.

**A path evaluation reports its node visits to the same probe.**
`expressionMetrics().resolutions` is how this repository asserts cost as
work performed rather than as elapsed time, and a path walk that reported
nothing would make the run's cost invisible to it.

**No knob, no document change, no API change.** The saving is structural:
no declaration, option, tolerance, cache size or sampling count, and
nothing an author writes selects it. `solidNodeViewerApi` stays 16,
`solidNodeDocumentVersions` stays `[1..7]`, and the document the producer
publishes is untouched — this is one repository's change, not two.

### What it buys, measured on a prototype

A complete prototype of the above, over a copy of `src/` patched at those
five sites (`scratchpad/spikes/proto`), against the SAME document and the
same bench, three runs each:

| | idle tick | crank tick |
| --- | --- | --- |
| before | 18.27 / 19.13 / 19.32 ms | 156.70 / 160.61 / 161.63 ms |
| after | **8.68 / 9.30 / 9.60 ms** | **38.91 / 39.78 / 40.36 ms** |
| DAG nodes computed | 20 513 → **7 674** | 1 428 635 → **10 492** |

**2.1× an idle tick and 4.0× a crank tick**, against ADR-124's own 4.5×
on the Python side. The studio integrates one tick per rendered frame
(`libresolid-studio` `8b814b5`), so at 60 Hz that is a 16.7 ms frame
budget: an idle tick stops missing it (19 ms → 9 ms) and a crank tick
goes from 6 fps to 25 fps.

**Nothing moved.** The bank, every recorded crossing and every stop after
100 idle ticks and 60 crank ticks — 213 lines — are byte-identical
between the base engine and the prototype, on all three runs. The
prototype passes all **294** tests of `src/run/`'s own ten test files
over the COMMITTED corpus, exactly as the base does, and replays all
**20** scenarios of the producer's refreshed corpus green — the new
`KinkedStop` included.

**And the small machines did not pay for it.** `run/cost.test.ts` on the
base and on the prototype, same bench:

| machine | base | prototype |
| --- | --- | --- |
| `Train`, no constraint | 164 138 ticks/s | 182 211 |
| the Pascaline at `1/240` | 34 555 ticks/s | 33 734 |
| `CarryLead`, affine plans | 87 831 ticks/s | 98 358 |
| `Clearing`, a solved self-read | 6 170 ticks/s | **10 570** |
| `ShiftedCarry`, a quiet block tick | 4 375 ticks/s | **7 895** |
| the Curta fixture at `1/240` | 211 ticks/s | **300** |
| the Curta carriage at `0.02` | 298 ticks/s | **699** |
| the lock, advancing the key | 148 ticks/s | 150 |
| `RangedBlock`, a searched stop | 252 ticks/s | 261 |

The last two are the guard the other way: they are `run.ts`'s constraint
search, which this cycle does not touch, and they do not move.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: ONE ADDED requirement, "Only what moves along a
  step's path is walked" — what the viewer computes twice, stated so that
  no crossing, landing, branch reading, increment, stop, refusal or
  committed value may move with it.

## Impact

- `solid_node_viewer/widget/src/expressions.ts` — a path value over the
  shared DAG, and the moving-name set; both exported to `src/run/` only.
- `solid_node_viewer/widget/src/run/jumps.ts` — the five follow sites,
  and a `LevelPaths` holding one path value per jump per scope.
- `solid_node_viewer/widget/src/run/{jumps,expressions}.test.ts` — the
  bit-identity and structure tests, red first.
- `solid_node_viewer/widget/src/run/cost.test.ts` — the measured floors
  above, raised only where the prototype makes them unambiguous.
- `docs/adrs/EXPORT/ADR-060` and `docs/adrs/README.md`.
- `CHANGELOG.md` under `0.2.0 — unreleased`: one bullet.
- `openspec/specs/viewer-package/spec.md`: one requirement, through the
  delta.
- Nothing in `package.json`, nothing in `viewer.ts`'s
  `RENDERED_VERSIONS`, nothing in the Python package, nothing in the
  framework, and nothing in the project the finding came from.

### Non-goals

- **Mirroring ADR-123's kink cut.** Measured, not assumed: ADR-123's own
  `_shape_of`, re-implemented against this document (`spikes/classify.py`,
  validated by reproducing the producer's published census of 28 kinked
  and 41 unclassified skeletons exactly), classifies 17 of the Curta's 32
  self-read skeletons as KINKED and 15 as unclassified — and **100 % of
  the 40 040 skeleton evaluations, 40 624 level evaluations and 600
  searches of 20 crank ticks are under the 15 unclassified ones**, none
  under a kinked one. Cutting at kinks would buy this document nothing,
  exactly as ADR-123 measured on the Python side. It is a real
  improvement in EXACTNESS and in generality, and it belongs in its own
  cycle with its own audit of which floats move.
- **Taking the producer's refreshed corpus.** `tests/running-corpus.json`
  at `debd760` adds exactly one scenario, `KinkedStop` (4 ticks), and
  changes nothing else — every other machine, script and tick is
  byte-identical, and the census moves 19 → 20 machines and 356 → 360
  ticks. Replayed through the UNCHANGED base engine it is **green**: the
  viewer's 64-sample search of that kinked determiner agrees with
  Python's solve inside the corpus's own `1e-9` window. What is missing
  here is the census, the `REQUIRED` entry `'a stop on a kinked
  determiner inside a tick'` and its derivation (`_kinked_laws`: a law
  with a null plan whose expression, closed over the bindings table,
  calls `abs`, `min` or `max`). That is a fixture-and-guard cycle of
  exactly `mirror-the-gate-guard`'s shape, and mixing it into an engine
  change would put a red census assertion in front of every engine
  measurement.
- **Retiring the rest of the scope-rebuild wart.** After this change
  `nest` is 11.2 % of an idle tick's self time and 3.4 % of a crank
  tick's, against 40.6 % and 16.0 % before: the finding's own two
  proposed directions are no longer worth a cycle on this document, and
  the measurement says so. Recorded in `evidence.md` rather than taken.
- **Making the operating Curta interactive.** It does not, and does not
  claim to. A crank tick is still 39 ms and still 79 % inside the same
  two sites, because a searched self-read crossing costs 64 samples and
  up to 64 bisection rounds per piece whatever one evaluation costs. The
  two mechanisms that would cut THAT — a per-piece classification, and a
  compiled moving cone — are recorded with their numbers in ADR-124's own
  Considered Options and are the producer's to decide first.
- **Touching `run.ts`'s constraint search.** A stop's localization
  follows a quantity too, and the same mechanism would fit it; it is
  measured at 0 % of this document's tick (its two cost-test numbers do
  not move above) and is left for the cycle that has a document
  demanding it.
- **Restoring cross-expression hash-consing under a run.** A path value
  shares nodes within one followed quantity and not between two of them,
  exactly as the run's fresh-scope rule already prevented. That is the
  wart's second cost and it is not addressed here.
