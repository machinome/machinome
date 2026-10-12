## Why

The producer regenerated its conformance corpus on 2026-09-16 in the
framework cycle `cut-at-the-kink` (solid-node `c3f3348`, ADR-123: `abs`,
`min` and `max` are KINKS, and a kinked quantity is solved at its own
breakpoints rather than searched). The regeneration added ONE scenario,
`KinkedStop`, and one entry to the generator's `REQUIRED` list:
`'a stop on a kinked determiner inside a tick'`. ADR-123's own
Consequences name this repository:

> The two runtimes now locate a kinked crossing differently. Python
> solves it; the viewer, reading `affine: false`, still searches it. They
> agree inside the corpus's own `1e-9` window … and no viewer change is
> required for CORRECTNESS.

This viewer commits its own byte-for-byte copy of
`tests/running-corpus.json` and its own mirror of `REQUIRED`, and ADR-047
makes that corpus the contract between the two runtimes. So this cycle
takes the refreshed fixture and the refreshed guard, and proves against
THIS engine what the producer proved against its own — exactly the shape
`mirror-the-gate-guard` (`openspec/changes/archive/2026-09-16-mirror-the-gate-guard/`)
established, and for the same reason.

It is deliberately a FIXTURE-AND-GUARD cycle and not an engine change.
The engine change that ADR-123 leaves open here — solving a kinked
quantity instead of searching it — is proposed separately as
`solve-at-the-kink`, and is stacked on this one because the guard this
cycle installs is what that cycle's audit is read against.

### What this viewer does today, measured on the base

Base: worktree `solid-node-viewer/WTs/curta-speed`, branch `curta-speed`,
head `a35957d` (`walk-only-what-moves` implemented, ADR-060 Accepted;
package `0.2.0` unreleased, `solidNodeViewerApi: 16`,
`solidNodeDocumentVersions: [1..7]`, highest ADR 060). `npx vitest run`
→ 37 files, **962 tests**, 37.3 s; `npx tsc --noEmit` clean.

**The committed corpus is stale by exactly one regeneration.** Compared
with the framework's `tests/running-corpus.json` at `debd760`
(`solid-node/WTs/curta-speed`, read-only):

| | committed here | the producer's at `debd760` |
| --- | --- | --- |
| md5 | `7b9eb6c894c3863710cdbaac68c5fe74` | `651a3b5750c49eecad4587438dc9a85a` |
| bytes | 263 308 | 267 185 |
| scenarios | 19 | **20** |
| distinct machines | 16 | **17** |
| ticks | 356 | **360** |

`generated_by`, `corpus` and `tolerance` are equal. Scenario keys
`(name, dt, steps)`: **added exactly one**, `('KinkedStop', 0.1, 4)`,
appended LAST; removed none; and every one of the 19 pre-existing
scenarios is equal key for key, value for value, in the same order —
script, document and all 356 ticks. `KinkedStop`'s own document declares
`version: 5`, carries ONE law edge — `lever drives slide.travel` as
`4 + 72 · clamp01((lever − 113.5)/11.25)`, published `affine: [false]`
with NO jump plan — and one span, `slide.travel` high 40.

**The replay is already green over the new file.** Replayed scenario by
scenario through the shipped engine on this base, all **20** agree,
`KinkedStop` included: the viewer's 64-sample search of that kinked
determiner lands inside the corpus's own `1e-9` relative window. With the
new file in place the whole `src/run/` suite is green but for ONE
assertion — the census (`19`, `16`, `356`) — and that is the whole of
what breaks: 14 files, 339 → 340 tests, one failure, and it is the
failure this cycle exists to fix. Six other test files import the corpus
and read only the byte-identical documents.

**But the agreement is a TOLERANCE and not an identity, and that is worth
recording here rather than discovering later.** Of the **2 018** floats
the refreshed corpus records — every banked value, every crossing `t` and
level, every stop `t` and value, every command's admitted travel — this
engine reproduces 2 009 BIT FOR BIT and disagrees on **9**, every one of
them `KinkedStop`'s and every one of them a consequence of the single
searched stop:

```text
tick 1  stop slide.travel t   0.47812500000009095   corpus 0.478125
tick 1-4  bank lever           119.12500000000364    corpus 119.125
tick 1-4  command h0 admitted   19.125000000003638   corpus 19.125
```

9.09e-14 on the fraction, which is the search's own tolerance and the
same order as the 9.3e-14 ADR-123 measured on the Python side before it
solved. Inside the window; not the producer's number. `solve-at-the-kink`
is what closes it, and this cycle states the gap rather than hiding it.

**The guard does not know the producer's new feature, and that is the
bug.** `uncoveredFeatures` in
`solid_node_viewer/widget/src/run/running-corpus.test.ts` mirrors
`tools/generate_running_corpus.py`'s `REQUIRED` and its derivations.
Measured with the producer's new entry appended to `REQUIRED` and its
detection NOT yet mirrored:

| corpus | `REQUIRED` + the feature, no detection | + the detection mirrored |
| --- | --- | --- |
| the producer's at `debd760` | `['a stop on a kinked determiner inside a tick']` | `[]` |
| this viewer's committed copy | same one uncovered | **same one uncovered** |

The second row is what makes the corpus refresh load-bearing rather than
cosmetic. Three machines of the refreshed corpus carry a kinked
plan-less determiner — `Captured` (`p1.lift`, `p2.lift`), `Train`
(`slide.travel`) and `KinkedStop` (`slide.travel`) — and **`KinkedStop`
is the only one that records a stop on one**, at `0 < t < 1`. The
committed copy supplies the feature not at all.

## What Changes

- **The committed corpus is replaced by the producer's at `debd760`,
  BYTE FOR BYTE.** Nothing here edits it, ever. The census assertion
  moves with it: 19 → 20 scenarios, 16 → 17 distinct machines, 356 → 360
  ticks.
- **The width guard gains the producer's new required feature**,
  `'a stop on a kinked determiner inside a tick'`, appended to `REQUIRED`
  in the producer's own position and spelling — after `'an in-block gate
  crossing inside a tick'`.
- **Its detection mirrors `tools/generate_running_corpus.py`'s
  `_kinked_laws` and `_calls` exactly**: a law edge whose `plans` entry
  for a driven end is NULL and whose published `expressions` entry for
  that end, closed over the document's own bindings table, CALLS `abs`,
  `min` or `max`; and a recorded stop on such a coordinate with
  `0 < t < 1`. It is a SECOND deliberate copy beside `loadProgram`'s own
  reading, for the reason the file already gives: the guard must be red
  on a narrowed corpus even when the engine is broken. The existing
  `freeNamesOf` walks the bindings table for NAMES; this needs the same
  walk for CALLS, so the guard gains a `callsOf` beside it.
- **The narrowed-corpus test names the new feature**, as it already names
  the self-read's three, the selection's one and the block's one.
- **Nothing about what the viewer reads or executes changes.**
  `solidNodeViewerApi` stays 16, `solidNodeDocumentVersions` stays
  `[1..7]`, `RENDERED_VERSIONS` stays `1–7`, and no line of ENGINE source
  changes — `program.ts`, `jumps.ts`, `edges.ts`, `run.ts`, `engine.ts`
  and `viewer.ts` are untouched, and the only file under `src/run/` this
  cycle edits is `running-corpus.test.ts`. No ADR: a fixture refresh and
  a coverage guard decide nothing about the architecture, and the
  disposition of `mirror-the-gate-guard` is the precedent.
- **The Python side is untouched and its suite is unaffected**: the
  corpus is a widget test fixture imported only by TypeScript test files,
  no `src/` module imports it so it is not in `dist/solid-widget.js`, and
  it is not packaged — `bundle.py`, `server.py` and `capture.py` never
  see it. The bundle does not change and needs no rebuild.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: ONE MODIFIED requirement, "The two runtimes agree on
  a conformance corpus" — the width the suite asserts gains a stop
  located strictly inside a step on a KINKED DETERMINER, derived from the
  corpus's own documents as every other feature is. Every existing
  scenario of that requirement is carried unchanged under its exact
  title.

## Impact

- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  framework's file at `debd760`, byte for byte.
- `solid_node_viewer/widget/src/run/running-corpus.test.ts` — the census
  assertion, `REQUIRED`, a `callsOf` mirror, the `kinkedLaws` derivation
  and its tick rule in `uncoveredFeatures`, and the narrowed-corpus
  assertion.
- `CHANGELOG.md` under `0.2.0 — unreleased`: one bullet.
- `openspec/specs/viewer-package/spec.md`: one requirement, through the
  delta.
- Nothing under `solid_node_viewer/widget/src/run/` other than that test
  file; no `package.json` version, no `README.md` version claim, no ADR,
  no `dist/` rebuild, nothing in the framework, and nothing in another
  checkout.

### Non-goals

- **Solving the kinked stop.** The 9.09e-14 above is this viewer's
  search, it is inside the corpus's window, and closing it is an ENGINE
  change with its own audit of which floats move: `solve-at-the-kink`,
  stacked on this cycle. Mixing the two would put a red census assertion
  in front of every engine measurement, which is the mistake
  `walk-only-what-moves` already declined to make.
- **Re-deriving the feature from the engine's own classification.** The
  guard reads the corpus's documents and tick logs only, exactly as it
  already does for the self-read, the selection and the block. After
  `solve-at-the-kink` the engine will carry a classification of its own;
  this guard SHALL still not ask it.
- **Widening or narrowing the corpus in any other way.** No scenario is
  added here, none is dropped, and the file is a copy.
- **Changing the engine, the document ladder, or the API version.**
  Nothing about what the viewer reads or executes changes.
