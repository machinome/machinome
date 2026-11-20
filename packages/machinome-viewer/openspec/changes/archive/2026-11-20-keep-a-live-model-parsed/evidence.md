# Evidence: keep-a-live-model-parsed

Applier's record of tasks 1.2 to 6.1 and 7.1, 20 November 2026, on the bench
`machinome/WTs/keep-a-live-model-parsed` (branch `keep-a-live-model-parsed`,
HEAD `4868799d`, one commit above `c8437407`). Every vitest run below was one
file at a time from `packages/machinome-viewer/machinome/viewer/web/widget/`,
with the primary checkout's `node_modules/.bin/vitest` (v3.2.7). Node counts
are `expressionMetrics()` readings; they are deterministic. The heap readings
are Node readings, not Chromium's, and are evidence, not assertions.

The new tests A to I are in `src/expression-reuse.test.ts`, a new file beside
`expression-lifetime.test.ts`. Line numbers quoted in the red outputs are the
line numbers of the file as it stood at that run.

## 1.2 The bench

Clean tree; `git log` shows `4868799d plan: keep a live model parsed between
operations` directly above `c8437407`; `openspec validate
keep-a-live-model-parsed --strict` printed "Change 'keep-a-live-model-parsed'
is valid".

## 2.1 Tests A and B, red on the base source

Run against the unmodified source (`src/expression-reuse.test.ts` holding A and
B only):

```
 × A: keeps one large document prepared across adjacent operations 1032ms
   → expected 2 to be 1 // Object.is equality
 × B: operates a large and a small document alternately without reclaiming 1258ms
   → expected 7 to be 6 // Object.is equality

 FAIL  A
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/expression-reuse.test.ts:83:38
     81|     for (let operation = 0; operation < 3; operation += 1) {
     82|       expect(read(table, `_b${LARGE - 1}`, operation)).toBe(2 * operat…
     83|       expect(expressionGeneration()).toBe(generation);

 FAIL  B
AssertionError: expected 7 to be 6 // Object.is equality
 ❯ src/expression-reuse.test.ts:121:38
    119|       expect(read(small, '_b2', round)).toBe(3 * round + 1);
    120|       expect(read(small, '_b1', round)).toBe(3 * round);
    121|       expect(expressionGeneration()).toBe(generation);

 Tests  2 failed (2)
```

Both failures are the generation assertion: A at its first ordinary operation
after the load (the value assertion on the line before passed), B at the first
small-document operation of the alternation, once the large document had been
rebuilt beside it. No timeout, recursion error or fixture error. The 66,000-entry
document has 132,004 nodes after its load.

## 2.2 The shipping-policy half and the twin, red on the base source

`validation-pressure.test.ts`, "prepares one coherent validation graph above
finite headroom and keeps it for the next operation":

```
 FAIL  src/validation-pressure.test.ts > prepares one coherent validation graph above finite headroom and keeps it for the next operation
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/validation-pressure.test.ts:60:34
     59|   expect(Object.is(result, 3164)).toBe(true);
     60|   expect(expressionGeneration()).toBe(generation);
 Tests  1 failed | 11 passed (12)
```

`expressions.test.ts`, "keeps the table past the node ceiling between
operations, and drops it at a load":

```
 FAIL  src/expressions.test.ts > retainExpressions / releaseExpressions (D8) > keeps the table past the node ceiling between operations, and drops it at a load
AssertionError: expected 3 to be 6 // Object.is equality
 ❯ src/expressions.test.ts:514:41
    513|       const second = prepare('(5300012 + 2)');
    514|       expect(expressionMetrics().nodes).toBe(6); // both expressions k…
 Tests  1 failed | 87 passed (88)
```

The twin fails on the base at its plain-preparation half (the base reclaimed
before the second preparation: 3 nodes, not 6), so its load half is not
reached there; on the base `withDocumentLoad` is not exported at all.

## 3.1, 3.2 Implementation, and the files of 2.1 and 2.2

After 3.1 and 3.2 the four new tests passed (`expression-reuse.test.ts` 2/2;
the new tests in `validation-pressure.test.ts` and `expressions.test.ts`
green). Before 4.1, the existing pressure tests that the design lists failed
as Decision 5 predicts:

- `validation-pressure.test.ts`: "... reconstructs afterward" (expected 3 to be
  4, its generation rise) and "refuses an invalid unreferenced late entry ..."
  (expected 28 to be greater than 28, the assertion 4.1 moves);
- `expressions.test.ts`: "drops and rebuilds the table when the node ceiling
  is passed" (expected 6 to be 3) and "a held BindingTable re-prepares its
  roots after a reset" (the old id still read 9900102).

`expression-lifetime.test.ts` and `run/program.test.ts` were edited under 4.1
before being run against the implementation.

## 4.1 Existing tests

Done as Decision 5 lists them; each file restores both fields of
`EXPRESSION_LIMITS` in its `afterEach` or the test's `finally`. After 4.1:
`expression-lifetime.test.ts` 11/11, `validation-pressure.test.ts` 12/12,
`expressions.test.ts` 88/88, `run/program.test.ts` 98/98.

## 4.2, 4.3 Tests C to I, and node counts

Default configuration for A, B and C; H = 5 for D; H = 50 for E to I; every
one with `everyOperation` false.

| Test | Reading |
| --- | --- |
| A | 132,004 nodes after the load (`peakNodes` 132,004); 132,004 after three reads and a tree update; one table preparation; no generation change |
| B | 132,006 nodes once both documents have been operated once (`peakNodes` 132,006); 132,008 after the alternation; the large table prepared twice in the test |
| C | 58 machines (30 clocked, 28 running) plus a posed tree: no second pass added a node; 638 nodes at the end, no generation change in the whole test |
| D | g = 47, bound (H − 1) + 2g = 98, high-water `peakNodes` 85; 180 generation changes over the 60 iterations (three per iteration: the replacement's start, the refusal's start, the refusal's end); no installation reclaimed |
| E | 63 nodes held before the release; 3 after the release and the survivor's operation; one generation |
| F | the good document's graph 9 nodes; the refused load's high-water 126; 8 after the following operation; one generation |
| G | 9; 125 after the abandoned document's validation; 8 after the following operation; one generation; the later `installed()` changed nothing with the store above H again |
| H | 127 after the successor's validation; 244 after the standing document was rebuilt in the window; 125 after the installation's reclamation and the successor's first read; two generations |
| I | no table preparation and no generation change in three operations after the installation |

Test D's documents: b and its replacements use entry expressions a does not
share (`_b0 + (i + 1000)`), so the two loaded graphs are disjoint apart from
names and small constants, as in the design's revision-time experiment
(g = 45, bound 94, high-water 82).

### Removed-reclamation reds of 4.3

Each variant was applied to `src/expressions.ts`, `expression-reuse.test.ts`
was run whole, and the file was restored from a copy (SHA256 before and after,
`8bfa3a70c70eb12ac4f95964668544134fa00b8f4a85eb2328fc8f0e6fac1f88`).

| Variant | Failed | Passed |
| --- | --- | --- |
| E: `releaseExpressions` without its request at H | E: `expected 63 to be less than 53` (`nodes` < H + 3) | A, B, C, D, F, G, H, I |
| F: a refused load without its request at H | F: `expected 126 to be less than 59` (`nodes` < H + graph) | A, B, C, D, E, G, H, I |
| G and H: `installed()` and `abandoned()` requesting nothing | G: `expected 125 to be less than 59`; H: `expected 268 to be 269` (the settlement's generation rise) | A, B, C, D, E, F, I |
| I: `installed()` requesting at H instead of H + A | I: `expected 337 to be 336` (a generation change at the first operation after the installation, which also re-prepared the table) | A to H |

## 4.4 Every file singly, and the switch spot-checks

Run singly after the variants were restored: `expression-lifetime.test.ts`
11 passed, `validation-pressure.test.ts` 12 passed, `expressions.test.ts` 88
passed, `run/program.test.ts` 98 passed, `expression-reuse.test.ts` 9 passed.

With its `everyOperation` line removed (and the file restored after), each
spot-checked forced-pressure test fails on the generation assertion added or
kept for it:

| File | Test | Failure without the switch |
| --- | --- | --- |
| `expression-lifetime.test.ts` | reconstructs a pose scope acquired before reclamation | `expected 1 to be greater than 1` |
| `expression-lifetime.test.ts` | replays all clocked corpus operations unchanged under pressure | `Counter: expected 1 to be greater than 1` |
| `validation-pressure.test.ts` | prepares one coherent validation graph above finite headroom and reconstructs afterward | `expected 1 to be 2` |
| `expressions.test.ts` | drops and rebuilds the table when the node ceiling is passed | `expected +0 to be 1` |
| `run/program.test.ts` | re-prepares from the expression strings after a store reset | `expected 0 to be greater than 0` |

## 5.1 Gate

- Whole widget suite (`vitest run`, once): 68 files, 67 passed and 1 skipped;
  1,758 tests, 1,756 passed, 2 skipped, 0 failed; 54.8 s. The two skips are
  environment-gated: `run/profile-contact.test.ts` "loads the pinned
  actual-cover v13 Bound ..." (`CURTA_PROFILE_V13_DOCUMENT` unset) and
  `run/profile-installed-benchmark.test.ts` (`CURTA_INSTALLED_PROFILE_DOCUMENT`
  unset).
- Typecheck (`tsc --noEmit`): exit 0, no output.
- Python suite: see below.

The Python suite was run twice, because the first run found no bundle:

1. Before 5.2, with no `dist/` on the bench:
   `.venv/bin/python -m pytest tests` from `packages/machinome-viewer`
   reported 6 failed, 127 passed, 145 skipped, 196 subtests passed (5.2 s).
   Every failure and every skip names the missing bundle: the six failures
   (among them `test_capture.py` `CaptureFailureTest.test_a_stale_bundle_is_refused_and_nothing_is_staged`
   and `test_the_bundle_is_made_current_before_it_is_staged`, `test_cli.py:87`
   and `test_server.py:137` and `:150`) raised or asserted on "Viewer bundle not
   found at .../widget/dist/machinome-viewer.js"; the skips read "widget
   bundle not built (npm run build)" (142), "this installation carries no
   built bundle" (2) and "no built bundle in this checkout" (1). The suite
   does not build the bundle itself.
2. After 5.2 built it, once: 276 passed, 2 skipped, 0 failed, 214 subtests
   passed, 71 warnings (280.0 s). Both skips are `tests/test_curta_drawing.py`
   (lines 375 and 469): "the Curta's own builds are not at
   .../WTs/projects/Calculators/Curta-Type-I-3x/_build". The warnings are
   Pillow `getdata` deprecations and the like. The bundle's SHA256 was the
   same after the run as after the build.

## 5.2 Bundle

`npm run build` (esbuild, 164 ms):
`packages/machinome-viewer/machinome/viewer/web/widget/dist/machinome-viewer.js`,
921,858 bytes, SHA256
`4724e735496f0057a7c791df23fa3417fd19ce56c914b1d501df95585c4b6505`.

## 6.1 Heap readings of the test-A document

`NODE_OPTIONS=--expose-gc vitest run src/expression-reuse.test.ts -t "A: keeps"`
(the test logs a reading after a forced collection only when the collector is
exposed):

| State | `heapUsed` | `nodes` |
| --- | --- | --- |
| loaded | 88.7 MB | 132,004 |
| after the three reads and the tree update | 88.7 MB | 132,004 |
| after the final disposal (the store emptied; the document, its table and the test's references still alive) | 54.5 MB | 0 |

The difference, 34.2 MB for 132,004 nodes, is about 270 bytes per node for
this synthetic shape in V8 under Node, the figure the design's probe gave
(36 MB). The operations added nothing to the heap.

## Decisions the design left open

- `withDocumentLoad(action)` returns `{ value, settlement }`; `assertRenderable`
  spreads the value and adds `settlement` to its `LoadedDocument`
  (`DocumentSettlement`, an exported interface of `expressions.ts`).
- Pending requests are kept as one number, the lowest threshold requested
  while a scope is open; the outermost scope's end resets once if the store
  holds at least that many nodes or if the last release is pending with no
  mount retained since. A threshold is computed when it is requested (H read
  then, and for `installed()` the generation compared then); no reset can
  happen inside a scope, so the generation cannot move between the request
  and its honouring.
- The last release with no scope open resets at once and requests nothing
  further, so a release makes at most one reset; inside a scope it sets the
  existing disposal flag and requests at H, both honoured at the scope's end
  by one reset at most.
- A, the nodes a load added, is the store's size at the end of the load's
  action minus its size after the load's own start check.
- In `viewer.ts` the settlement's `try`/`finally` begins immediately after
  `await loadDocument(...)` returns, so `assertCaptureDocument` is inside it;
  a refusal by `loadDocument` itself has no settlement and is reclaimed by the
  load's own refusal request.
- Test G's idempotence check prepares 30 unrelated expressions, taking the
  store back above H, before the late `installed()`, so that a second request would have reset the store; with the
  store below H that check would have passed whatever `installed()` did.
- Tests E to I use wide documents; the successor in H and I and b in D shift
  their entries (`_b0 + (i + 1000)`) so that their graphs are not hash-consed
  onto the standing document's.

## Deviations from the design

- "discards negative facts between document meanings and operations ..."
  (`validation-pressure.test.ts`): the added generation assertion is that the
  generation rose across the first lowered load, and by at least two across
  the refused one (its start, with a's graph resident, and its own end). A
  rise across the last good load, which an earlier draft of this edit
  asserted, does not happen: the refused load's end already emptied the
  store, so the last load starts below H. Each of the three validations still
  starts from an emptied store.
- Test A's tree is built after the load and before the three reads; on the
  base its construction reads only strings the load had already prepared, so
  the base's first reclamation falls at the first read, which is where the
  red output shows it.

## Reviewer's record: review of the implementation and task 6.2

Written by the repository agent, 20 November 2026, after the applier stopped
with its work uncommitted.

### Review of the implementation

The diff of `expressions.ts` and of `viewer.ts` (read with whitespace ignored)
was checked against design Decision 1 point by point, and the test edits
against Decision 5 for weakened assertions; none was found beyond the one move
the design sanctions. Run again by the reviewer, one file at a time:
`expression-reuse.test.ts` 9 of 9, `expression-lifetime.test.ts` 11 of 11,
`validation-pressure.test.ts` 12 of 12, `expressions.test.ts` 88 of 88,
`run/program.test.ts` 98 of 98; `tsc --noEmit` exit 0. A rebuild of the bundle
from the final source gave the same SHA256 as 5.2.

One correction to 1.2 and to the plan's wording: the bench has its own
`node_modules` at its root, installed when `uv sync` built the viewer package,
from the same lockfile as the primary checkout's. The widget's imports
resolved there, not by parent lookup into the primary checkout; only the
`vitest` and `tsc` executables named on the command lines were the primary's.

### 6.2 The Enigma I page

Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
`a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`. Headless
Chromium through Playwright on the same host as the originating evidence
(AMD Ryzen 9 5900X virtual machine, no GPU). Every WebGL draw call is counted
and not executed, so the times are script only; nothing here is a statement
about a GPU. Each instruction is its own button, pressed by `element.click()`.
All figures are single runs.

**(b) Probe build of the bench's source** (the widget's own entry, unminified,
plus a handle on the scene, on the mounted inspector and on the store's
metrics, generation, binding preparations and retain/release), at the default
configuration (`EXPRESSION_LIMITS.nodes` 125,000, `everyOperation` false).

The store, read on the page:

| When | Generation | Binding preparations | Nodes |
| --- | ---: | ---: | ---: |
| After mount | 0 | 1 | 546,768 |
| After the nine instructions below | 0 | 1 | 546,768 |

The initial mount therefore reclaimed nothing (Decision 2, case 2 with an empty
store), and nine instructions neither moved the generation nor prepared the
table again nor added a node.

| Instruction (declared seconds) | Press task, ms | Script per changing frame, ms | Frames that changed the picture |
| --- | ---: | ---: | ---: |
| Key A (0), the key already selected | 52 | none | 0 |
| Press (2) | 775 | 340 | 5 |
| Release (2) | 618 | 314 | 6 |
| Right wheel on (0.4) | 677 | 171 | 2 |
| Right wheel back (0.4) | 630 | 168 | 2 |
| Open flap (1.5) | 49 | 30 | 46 |
| Close flap (1.5) | 47 | 27 | 48 |
| Open hood (4) | 50 | 29 | 124 |
| Close hood (4) | 48 | 28 | 129 |

Against the originating evidence's first column (the base): press tasks of
2,398 to 7,225 ms, 1,737 to 3,591 ms per changing frame, and two pictures per
instruction. An idle frame's script was 24 ms in this run, against 42 ms on
the base and 34 ms in the evidence's ceiling-lifted run; the three runs were
hours apart on a shared host, so the differences between this run and the
ceiling-lifted one are not attributed to the change. No page error.

**The store's resident size.** V8 heap (`Runtime.getHeapUsage` after two forced
collections) with the store full: 253,960,532 bytes. After the store was
emptied through the probe's `releaseExpressions()` and `retainExpressions()`
(generation 0 to 1, nodes 546,768 to 0): 138,341,976 bytes. The store is
therefore **115.6 MB** on this page, about 211 bytes per node. This replaces
the 150 MB estimate of the design's Decision 4, and the "about 30 MB" of
`workflow/evidence/enigma-press-script-cost-2026-11-20.md`, which was a
difference between two readings both taken with the store full. The base
holds the same store between operations.

The first press after that emptying (Open flap) took 1,820 ms and showed two
pictures: one re-preparation. It left 433,722 nodes, not 546,768: a rebuild
prepares what the operation reads, not the whole document.

**One `reload()` of the mounted viewer**, the only run of the viewer's own
settlement calls on a real page:

| When | Generation | Binding preparations | Nodes |
| --- | ---: | ---: | ---: |
| Before `reload()` | 1 | 2 | 433,722 |
| When its promise settled, 140.9 s later | 2 | 3 | 546,768 |
| After the first press that followed | 2 | 3 | 546,768 |

One rise, at the load's start; none at the installation; the incoming table
prepared once, by its validation; and the first press after it (Open flap)
took 66 ms and showed 37 pictures. This is Decision 2, case 1, with nothing
operated in the window. The other exits of `replaceTree`, and
`manifestChanged`, were not run on a page; they stand on the review of the
diff and on the applier's exit-by-exit trace.

**(a) The built bundle of 5.2** (SHA256 `4724e735…5b6505`, 921,858 bytes)
mounted on the same page, timed by the same wrapped `requestAnimationFrame`
with no handle on the scene or the store. No page error in either of two runs.

| Instruction (declared seconds) | Press task, ms | Frames begun within the declared time | Script per frame, median ms |
| --- | ---: | ---: | ---: |
| Press (2) | 770 | 14 | 25 |
| Release (2) | 687 | 14 | 27 |
| Right wheel on (0.4) | 679 | 5 | 27 |
| Right wheel back (0.4) | 670 | 6 | 26 |
| Open flap (1.5) | 55 | 53 | 26 |
| Close flap (1.5) | 55 | 52 | 27 |
| Open hood (4) | 56 | 130 | 28 |
| Close hood (4) | 47 | 140 | 26 |

These frame counts are animation-frame callbacks, moving or not, so they are
not comparable with "frames that changed the picture" above; the press tasks
are, and agree with the probe build's.

**Selecting a key.** With the built bundle, Key A pressed as the first act
after mounting took 593 ms, Key B 435 ms and Key A again 398 ms. The probe
build, pressed in the same order with the change tracker, gave: Key A (already
selected) 45 ms with nothing changed; Key B 381 ms and Key A again 369 ms, each
with **no mesh moved and 86 flexible parts refilled** (8,470,912 triangles);
Key A once more, unchanged, 41 ms; generation 0 and one preparation
throughout. A key selection that changes the key is therefore not a
re-preparation: it is the flexible-part finding of the same warts section,
seen without any motion at all. The built bundle's 593 ms for its first press,
where the probe build's first press took 45 ms, is not explained: the built
bundle was pressed before any animation frame had run and the probe build two
frames after. It is below the 1,820 ms of a re-preparation.

**Acceptance (task 6.2).** No page error; the generation does not change
across the presses after mount; the press tasks, the per-frame script and the
distinct pictures are of the order of the originating evidence's
ceiling-lifted column or better. Accepted.

**Not measured.** Any GPU's frame time; a browser other than Chromium; a page
with more than one viewer; `manifestChanged` on a page; a replacement refused
after validation on a page; memory other than the two V8 heap readings.

### Archival

`openspec archive` refused the delta as first written: its MODIFIED block
left out the baseline scenario "Consecutive ticks reuse a fitting graph",
which the planned delta had meant the any-size scenario to replace, and the
command does not drop a scenario. The scenario is still true of the changed
viewer and its test (`expression-lifetime.test.ts`, the 102,700-node graph)
stays, so the reviewer restored it verbatim in the delta beside the new
scenarios and archived. This corrects a planning artifact after the planning
commit; it is carried by the implementation commit, not by an amended one.

### Final gate

Run by the reviewer on the finished state, after the archive, one at a time.

- Whole widget suite: 68 files, 67 passed and 1 skipped; 1,758 tests, 1,756
  passed, 2 skipped (the two environment-gated Curta files of 5.1), 0 failed;
  53.6 s.
- `tsc --noEmit`: exit 0. The bundle's SHA256 is unchanged
  (`4724e735…5b6505`).
- Python suite: 275 passed, 2 skipped (the two of 5.1), 1 failed, 280 s. The
  failure was `tests/test_licence.py`
  `test_every_header_states_the_grant`, which lists files through the git
  index and could not open
  `openspec/changes/keep-a-live-model-parsed/.openspec.yaml`: the archive had
  moved the change and the move was not yet staged. With the finished state
  staged, `tests/test_licence.py` and `tests/test_documentation.py` were run
  again: 19 passed, 169 subtests. The new test file is now tracked, so its
  licence header is among the ones that test checks. The whole Python suite
  was not run a third time.
- `openspec validate --specs --strict`: 16 passed, 0 failed.
