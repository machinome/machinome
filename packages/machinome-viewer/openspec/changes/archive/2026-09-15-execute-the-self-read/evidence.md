# Evidence — execute-the-self-read

Every run below was made in the cycle worktree
`solid-node-viewer/WTs/execute-the-self-read`, on branch
`execute-the-self-read`, off viewer main `28dfc79`, on the planning
commit `69042a3`. `solid_node_viewer/widget/node_modules` is the main
checkout's, reached through a symlink; no `npm ci` and no `npm install`
was run.

The framework side this cycle consumes is solid-node main `8e15791`,
read-only at `/home/asa/devel/libresolid-studio/solid-node`.

## 0. The baseline

### 0.1 The base

```text
$ git rev-parse --show-toplevel
/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/execute-the-self-read
$ git log --oneline -1
69042a3 openspec(execute-the-self-read): propose executing a law that reads the coordinate it drives
$ git log --oneline -1 28dfc79
28dfc79 feat(widget): draw the markings a part carries; API 14; ADR-056
```

`solid_node_viewer/widget/package.json`:

```json
  "version": "0.2.0",
  "solidNodeViewerApi": 14,
  "solidNodeDocumentVersions": [
    1,
    2,
    3,
    4,
    5
  ],
```

`pyproject.toml` `version = "0.2.0"`. The highest ADR in
`docs/adrs/EXPORT` is `ADR-056-a-marking-is-a-decal-in-the-parts-own-group.md`.
`ls -la solid_node_viewer/widget/node_modules` →
`node_modules -> /home/asa/devel/libresolid-studio/solid-node-viewer/solid_node_viewer/widget/node_modules`.

### 0.2 The baseline measurements

`npm run typecheck`:

```text
> @solid-node/widget@0.2.0 typecheck
> tsc --noEmit
```

(clean, exit 0, no output.)

`npm test`:

```text
 Test Files  36 passed (36)
      Tests  806 passed (806)
   Start at  16:46:09
   Duration  20.07s (transform 2.95s, setup 0ms, collect 10.73s, tests 21.41s, environment 10.36s, prepare 8.13s)
```

`npm run build`:

```text
> @solid-node/widget@0.2.0 build
> node build.mjs


  dist/solid-widget.js  685.7kb

⚡ Done in 117ms
$ ls -l dist/solid-widget.js
-rw-rw-r-- 1 asa asa 702107 Sep 15 16:46 dist/solid-widget.js
```

Python suite,
`PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q`:

```text
114 passed, 53 warnings in 106.24s (0:01:46)
```

Nothing skipped: this environment carries Playwright, Chromium and
Pillow, so `needs_playwright` and `needs_bundle` are both satisfied.
The 53 warnings are pre-existing Pillow `getdata` deprecations in
`tests/test_widget_e2e.py`.

The cost measurements `src/run/cost.test.ts` prints on this base, from
two consecutive runs of the whole suite (this host's numbers vary by a
few per cent run to run):

```text
  CarryLead, affine plans: 20000 ticks in 0.447 s = 44774 ticks/s
  CarryLead, plans forced to search: 1000 ticks in 0.129 s = 7771 ticks/s
  Train, no constraint: 20000 ticks in 0.252 s = 79321 ticks/s
  Captured, blocking ticks: 2000 ticks in 0.033 s = 60852 ticks/s
  the lock, idle: 2400 ticks in 0.253 s = 9470 ticks/s
  the lock, advancing the key: 2400 ticks in 17.630 s = 136 ticks/s
  the Pascaline at dt = 1/240: 2400 ticks in 0.071 s = 34028 ticks/s
```

(The proposal's numbers — `Train` 73 188, `Captured` 60 339, the lock
idle 8 488, the lock advancing 132, the Pascaline 32 942 — were measured
on the same base while proposing; these are the same figures within this
host's run-to-run spread.)

### 0.3 The corpus gap, measured on the base

The committed copy and the framework's are two regenerations apart:

```text
$ md5sum solid_node_viewer/widget/src/running-corpus.json \
         /home/asa/devel/libresolid-studio/solid-node/tests/running-corpus.json
9ef7a3691dd63be82da0b114ee1ba9ea  solid_node_viewer/widget/src/running-corpus.json
0ba7939ad5b5988f739aa114a26ab464  /home/asa/devel/libresolid-studio/solid-node/tests/running-corpus.json
$ git -C /home/asa/devel/libresolid-studio/solid-node log --oneline -1
8e15791 Merge branch 'retained-angle-clearing'
```

(185 576 bytes committed here; 229 068 bytes in the framework. The
framework's working copy of that file is clean at `8e15791`.)

With the framework's file copied byte for byte over the committed one
(`md5sum` of the copy `0ba7939ad5b5988f739aa114a26ab464`, confirming the
copy), `npx vitest run src/run/running-corpus.test.ts`:

```text
⎯⎯⎯⎯⎯⎯⎯ Failed Tests 4 ⎯⎯⎯⎯⎯⎯⎯

 FAIL  src/run/running-corpus.test.ts > the running corpus > is the framework's own fixture, unedited
AssertionError: expected [ …(17) ] to have a length of 14 but got 17

- Expected
+ Received

- 14
+ 17

 ❯ src/run/running-corpus.test.ts:225:30

 FAIL  src/run/running-corpus.test.ts > the running corpus > replays Clearing at dt=0.05 (scenario 14)
Error: Clearing at dt=0.05, tick 8, bank wheel.turn: expected 359.5 within 1e-9 relative, got 408

 FAIL  src/run/running-corpus.test.ts > the running corpus > replays Clearing at dt=0.1 (scenario 15)
Error: Clearing at dt=0.1, tick 2, bank wheel.turn: expected 359.5 within 1e-9 relative, got 488

 FAIL  src/run/running-corpus.test.ts > the running corpus > replays StoppedClearing at dt=0.05 (scenario 16)
Error: StoppedClearing at dt=0.05, tick 3, bank ring: expected 341.1428571428571 within 1e-9 relative, got 336.73469387755097


 Test Files  1 failed (1)
      Tests  4 failed | 16 passed (20)
   Start at  16:49:23
   Duration  604ms
```

Exactly the four the proposal names and nothing else: the other thirteen
scenarios — both `Train` scenarios among them, whose DOCUMENTS differ
from the committed copy — and both width-guard cases are green. The
committed file was then restored (`md5sum` back to
`9ef7a3691dd63be82da0b114ee1ba9ea`, `git status` clean but for this
evidence file).

### 0.4 The framework's own record, read

Read on solid-node main `8e15791`, read-only, nothing written there:
`docs/adrs/NODE/ADR-121-a-law-may-read-the-coordinate-it-drives.md`;
`openspec/changes/archive/2026-09-15-read-the-driven-coordinate/design.md`
§3, §4, §6 and its dated implementation notes;
`openspec/specs/simulation/spec.md` "A law may read the coordinate it
drives"; `openspec/specs/export/spec.md`; and the implementation this
cycle mirrors — `solid_node/simulation/program.py`'s `_dependence`
(l. 598), `_on_surface` (620), `_ordinal` (639), `_from_ordinal` (647),
`_chattering` (653), `_Retained` (663), `_Walk` (717), `_unlanded`
(1083), `LandingInvariantError` (150), `Edge._retained_ends` (1158),
`Edge.increments` (1215), `Edge.cuts` (1269); and
`solid_node/simulation/run.py`'s `_landed` (661), `_pass` (678) and
`integrate` (506).

### 0.5 The refusal this cycle removes

The framework corpus's `Clearing` document declares version 6, and
`assertRenderable` on this base answers:

```text
running-corpus.json#Clearing/viewer.json declares document version 6,
which this viewer does not render; it renders versions 1, 2, 3, 4, 5.
The document is written to a schema this build cannot read: refusing it
rather than rendering part of a machine it does not understand.
```

## 1. The corpus, red first

### 1.1 The copy

```text
$ sha256sum solid_node_viewer/widget/src/running-corpus.json \
            /home/asa/devel/libresolid-studio/solid-node/tests/running-corpus.json
75259d3fb7f7453e4d478377c3e890f443c8147b7fbea116a143581c91f6171b  solid_node_viewer/widget/src/running-corpus.json
75259d3fb7f7453e4d478377c3e890f443c8147b7fbea116a143581c91f6171b  /home/asa/devel/libresolid-studio/solid-node/tests/running-corpus.json
```

Byte for byte. Its census: 17 machines entries, 14 distinct names, 328
ticks, tolerance `{'float': 1e-09}`, the names `Captured, CarryLead,
Clearing, Clutch, Ratchet, Remainder, StopAndJump, StoppedClearing,
Swept, Throwing, Train, TwoStops, Window, Wrapped`. Nothing here edits
it and nothing here regenerates it.

### 1.3 RED, with the census updated

`npx vitest run src/run/running-corpus.test.ts`:

```text
 ❯ src/run/running-corpus.test.ts (20 tests | 3 failed) 44ms
 FAIL  src/run/running-corpus.test.ts > the running corpus > replays Clearing at dt=0.05 (scenario 14)
Error: Clearing at dt=0.05, tick 8, bank wheel.turn: expected 359.5 within 1e-9 relative, got 408
 FAIL  src/run/running-corpus.test.ts > the running corpus > replays Clearing at dt=0.1 (scenario 15)
Error: Clearing at dt=0.1, tick 2, bank wheel.turn: expected 359.5 within 1e-9 relative, got 488
 FAIL  src/run/running-corpus.test.ts > the running corpus > replays StoppedClearing at dt=0.05 (scenario 16)
Error: StoppedClearing at dt=0.05, tick 3, bank ring: expected 341.1428571428571 within 1e-9 relative, got 336.73469387755097
 Test Files  1 failed (1)
      Tests  3 failed | 17 passed (20)
```

0.3's list minus the census assertion, and nothing else.

### 1.4 The width guard, widened

The three the producer's generator now requires, computed the way
`tools/generate_running_corpus.py`'s `uncovered_features` computes them.
One note on the mirror: the generator's self-read HOLD test skips the
first tick outright (`if previous is None: continue`) rather than
falling back to `program.coordinates[...].initial`, which tasks.md's
parenthetical allows for. The generator is the authority the task names,
so the guard here skips tick one exactly as it does; the feature is
covered many times over by `Clearing`'s later ticks either way.

```text
$ npx vitest run src/run/running-corpus.test.ts -t "width"
 ✓ src/run/running-corpus.test.ts (20 tests | 18 skipped) 7ms
      Tests  2 passed | 18 skipped (20)
```

Green on the producer's corpus, and the "narrowed corpus is refused"
case now names all three as well as the four it already named.

## 2. Reading the self-read (`src/run/program.ts`, design D1)

### 2.1–2.5 RED

The new `describe('a law that reads the coordinate it drives (design
D1)')` block run against the BASE `src/run/program.ts`
(`git show HEAD:… > src/run/program.ts`, restored immediately after):

```text
 × 2.1 is recognised from `needs` met with `gives`, and its BAND gate … is dependent
   → Target cannot be null or undefined.
 × 2.2 reads `affine` off the edge's published per-end flag and recomputes nothing …
   → Cannot read properties of undefined (reading '0')
 × 2.3 a plan with no dependent node at all keeps the WHOLE plan as its outer layer …
   → Cannot read properties of undefined (reading '0')
 × 2.3 a nested dependent node makes its ENCLOSING node dependent
   → Cannot read properties of undefined (reading '0')
 × 2.4 refuses a self-read law that drives more than one coordinate
   → expected loadProgram to refuse this document
 × 2.4 refuses a self-read of a published computed value
   → expected loadProgram to refuse this document
 × 2.4 refuses a read that survives the SKELETON
   → expected loadProgram to refuse this document
 × 2.5 a version 6 document with NO self-read edge loads with no reading at all
   → expected undefined to deeply equal []
 × 2.5 a version 5 document is never given a reading …
   → expected undefined to deeply equal []
      Tests  9 failed | 11 passed | 44 skipped (64)
```

### 2.1–2.5 GREEN

```text
$ npx vitest run src/run/program.test.ts
 ✓ src/run/program.test.ts (64 tests) 24ms
      Tests  64 passed (64)
```

**One place the design's prose was widened to match `program.py`, as the
briefing's rule requires.** Design D1 refusal 3 says "a self-read edge
whose plan's SKELETON still names the driven id". The producer's own
check is `skeleton = plan.skeleton if plan is not None else graph`
(`program.py` l. 2580): for an end carrying NO plan the EXPRESSION is
the skeleton, and a graph naming the driven id is refused there too.
The loader here does the same, so a self-read that never passes through
a jump node is refused rather than silently integrated as
`f(end) − f(start)` — which is the exact failure the version bump
exists to prevent. Refusals 1 and 2 are likewise judged on any law edge
whose `needs ∩ gives` is non-empty, not only on a plan-bearing one.

## 3. The float primitives (`src/run/jumps.ts`, design D3)

RED, against the base `src/run/jumps.ts`:

```text
 × the float primitives (design D3) > orders +0 and -0 to the SAME ordinal 0
   → (0 , ordinalOf) is not a function
 × … is `_ordinal` to the bit, at every magnitude  → (0 , ordinalOf) is not a function
 × … makes ADJACENT floats differ by exactly one ordinal  → (0 , ordinalOf) is not a function
 × … round-trips through `fromOrdinal` …  → (0 , ordinalOf) is not a function
 × … is `math.nextafter`  → (0 , nextAfter) is not a function
 × … is `math.ulp`  → (0 , ulpOf) is not a function
 × … is `math.copysign(1.0, x)`, NEGATIVE ZERO included  → (0 , copySign) is not a function
      Tests  7 failed | 23 skipped (30)
```

Every expected value in those tests is the answer CPython gives on this
host for the same argument, read off rather than reasoned about:

```text
$ .venv/bin/python -c "import struct, math; …"
0.0 0          -0.0 0         1.0 4607182418800017408
-1.0 -4607182418800017408    1e+300 9094988921128908188
5e-324 1       0.5 4602678819172646912   2.0 4611686018427387904
359.5 4645032007074578432
ulp(1) 2.220446049250313e-16      ulp(359.5) 5.684341886080802e-14
nextafter(1,2) 1.0000000000000002 nextafter(1,0) 0.9999999999999999
nextafter(0,1) 5e-324             nextafter(0,-1) -5e-324
copysign(1,-0.0) -1.0
ordinal(nextafter(1e300,inf)) - ordinal(1e300) == 1
```

GREEN after `ordinalOf`, `fromOrdinal`, `ulpOf`, `nextAfter` and
`copySign` land.

One thing the design did not name and `program.py` decides: Python's
`//` in `_far_side`'s ordinal bisection is FLOOR division, where
BigInt `/` truncates toward zero. The two differ for a negative odd sum,
which is every other round on a negative coordinate, so `halved()`
reproduces the floor.

## 4. The walk (`src/run/jumps.ts`, design D2)

`_Retained` and `_Walk` are mirrored function for function into
`jumps.ts`, reusing that file's own `partition`, `branchesAt`, `levelOf`,
`surfacesOf`, `branchOf` and the module's bisection rather than copies.
The bench for the unit tests is `Clearing`'s own shape — `GAP = 0.5`,
`STATION = (100.0, 500.0)`, the dial resting at `108`.

`npx vitest run src/run/jumps.test.ts` — **48 passed** (30 before this
cycle's additions), covering 4.1 the increment and the landing, 4.2 the
zeroed own delta, 4.3 the zero-source early return, 4.4 both layers,
4.5 `onSurface` and the chattering refusal, 4.6 the earliest-surface
rule, 4.8 the far-side landing and the one-cut grouping, 4.9 the
unlanded message and 4.10 `maxCrossings`.

### 4.7 The three defects the framework found after ratification

Each was REINTRODUCED into the implementation and its test shown red,
then the correction restored.

**Defect one** — `level === previous` skipped, and `surface !== previous`
filtered out of the searched sub-interval:

```text
 × 4.7 defect one: a level that does not MOVE crosses nothing … the PHANTOM
   → (setter, ring, wheel.turn) drives wheel.turn: over one tick wheel.turn
     would cross 1001 surfaces of floor, more than the 1000 a single law is
     admitted in one tick. …
```

**Defect two** — `wanted = branchOf(jump.primitive, probe)` instead of
`branchOf(jump.primitive, nextAfter(surface, probe))`:

```text
 × 4.7 defect two: a flipped node takes the branch of the region the level
   departs INTO, never the branch at the probe …
   → expected null to be 36 // Object.is equality
```

(The dial never moves at all: the flip to a branch a whole tooth away
closes the gate at the left end.)

**Defect three** — layer one's folding applied in layer two, dropping a
crossing within the crossing tolerance of a piece's left end:

```text
 × 4.7 defect three: a genuine crossing a hair inside a piece's left end is
   NOT folded away …
   → expected null to be 359.5 // Object.is equality
```

**A FINDING the design did not anticipate, and the reason D2 was right to
demand these tests.** With each of the three defects reintroduced in
turn, the whole conformance corpus stays GREEN:

```text
=== corpus with defect one ===    Tests  20 passed (20)
=== corpus with defect two ===    Tests  20 passed (20)
=== corpus with defect three ===  Tests  20 passed (20)
```

The corpus does not reach any of them: `Clearing`'s skeleton is affine,
so its crossings are SOLVED and never touch the searched path's two
corrections; its dial never stands exactly on a tooth boundary with a
rate-changing gate; and its crossings never fall within `1e-12` of a
piece's left end. The three node tests in `jumps.test.ts` are the only
thing in this repository that would catch them — which is exactly what
design D2's risk note said, measured.

## 5. Reporting and committing (`edges.ts`, `run.ts`, design D4, D5)

RED, with `src/run/program.ts` back at its base content (the self-read
unrecognised, everything else this cycle in place) — the version 5
reading of the same documents:

```text
 × 5.1 fills `landings` for a driven end at least one of whose cuts placed it
   → expected undefined to be 359.5
 × 6.1 loads with the shape the framework publishes
   → expected [] to have a length of 1 but got +0
 × 6.2 the dial clears to its gap and the RING RUNS ON
   → expected 148 to be less than or equal to 0.5
 × 6.4 swept BACKWARD … the band's UPPER edge  → expected false to be true
 × 6.5 a dial standing EXACTLY at a band edge …  → expected false to be true
 × 6.6 the same sweep at one tick, twelve and two hundred and forty …
   → expected false to be true
 × 6.8 `StoppedClearing`: … the BOUND wins
   → expected 336.73469387755097 to be close to 341.1428571428571
 × 5.2 applies the landing after the FULL-STRETCH pass …
   → expected 103.7 to be 11.9
 × 5.2 applies the landing after the SEGMENT pass too …
   → expected 63.7 to be 11.9
      Tests  9 failed | 54 passed (63)
```

`148` where the dial should be within `0.5` of `360` is the gate frozen
open — the same failure the framework measured on its own side, and the
same one the corpus reports as `408`.

### 5.2 Each of the two places `landed` is applied, pinned separately

The landing is the difference between the float the walk left the
coordinate at and `value + delta`, and those agree far more often than
not — `x + (y − x) === y` for about two float pairs in three. Both tests
therefore use a gate whose surface is NOT a float the tick's own
arithmetic reproduces: a `floor(wheel.turn / 1.7)` gate closing at
`11.9` from a rest of `3.7`, where `3.7 + (11.9 - 3.7)` is
`11.899999999999999` and `Math.floor(11.899999999999999 / 1.7)` is `6`,
not `7` — a ulp back toward the surface, on the ENGAGED side of the gate.

With the FULL-STRETCH `landed` call removed:

```text
 × 5.2 applies the landing after the FULL-STRETCH pass, before the bounds are examined
   → expected 11.899999999999999 to be 11.9 // Object.is equality
```

With the SEGMENT `landed` call removed:

```text
 × 5.2 applies the landing after the SEGMENT pass too -- the place a later
   stretch cannot quietly put right
   → expected 11.899999999999999 to be 11.9 // Object.is equality
```

(The segment case needs a stop that blocks the input for the REST of the
tick — a bounded shaft the ring drives — because otherwise the later
stretch re-lands the coordinate and hides the missing call. Worth
recording: a segment landing is only observable when nothing afterwards
can put it right.)

## 6. The framework's own numbers, mirrored (`src/run/run.test.ts`)

`Clearing` and `StoppedClearing` reproduced as benches, from
`tests/running_project/machine.py`'s own `missing_tooth`, `GAP` and
`STATION`. `6.8` asserts the producer's third tick to the digit:
`wheel.turn` exactly `400`, `gauge.turn` exactly `40`, `ring`
`341.1428571428571`, `setter` `56.85714285714286`, the two stops in the
order `gauge.turn` (at `t = 0`, blocking `gauge_in`) then `wheel.turn`
(at `t = 0.8428571428571429`, blocking `ring` and `setter`) — the same
numbers the corpus's scenario 16 carries.

`npx vitest run src/run/run.test.ts` — **45 passed**.

## 7. The corpus, green

```text
$ npx vitest run src/run/running-corpus.test.ts
 ✓ src/run/running-corpus.test.ts (20 tests) 61ms
      Tests  20 passed (20)
```

All 17 scenarios over 14 machines, 328 ticks, exactly for discrete state
and within `1e-9` relative for floats; plus the census and both width
cases. The corpus went green on the FIRST run after the walk landed,
with no adjustment to any tolerance, ordering or branch rule.

Whole widget suite at this point: `npm run typecheck` clean,
`npm test` **36 files, 860 tests, 0 failed** (806 on the base).

## 8. Versions (design D6)

RED, with the tests moved first and nothing else:

```text
 × API_VERSION > declares the self-read API as version 15
   → expected 14 to be 15 // Object.is equality
 × DOCUMENT_VERSIONS > is declared in package.json, where a Python caller can read it
   → expected [ 1, 2, 3, 4, 5 ] to deeply equal [ 1, 2, 3, 4, 5, 6 ]
      Tests  2 failed | 4 passed (6)
```

GREEN after `package.json`'s `solidNodeViewerApi` 14 → 15 and
`solidNodeDocumentVersions` → `[1, 2, 3, 4, 5, 6]`, with
`RENDERED_VERSIONS` following in `viewer.ts`.

### 8.3 The program gate

RED, the version 6 document whose `program` key is ABSENT — which the
second clause of the gate cannot catch:

```text
 × refuses a version 6 document with NO program at all -- the second clause
   of the gate must not let it through as a treeful document with nothing to run
   → expected [Function] to throw error matching /"program"/ but got
     '/m.json has expressions naming undecl…'
```

GREEN after `document.version === 5` becomes `document.version >= 5`.
The pre-existing "refuses a version it does not render" case moved from
6 to 7 with it, and now reads `renders versions 1, 2, 3, 4, 5, 6`.

### 8.4 `capture.py`'s `carries_program`

RED in the Python suite:

```text
>       self.assertTrue(carries_program({"version": 6}))
E       AssertionError: False is not true
```

GREEN after `document.get("version") == 5` becomes a FLOOR
(`isinstance(version, int) and version >= 5`). The companion case — an
animation instant refused for a version 6 staged document — passed
already, through the `program` key, which is why the direct test on the
predicate is the one that matters.

### 8.5 `RELEASED_DOCUMENT_VERSIONS` does NOT move

`tests/test_bundle.py` gains
`test_the_released_floor_does_not_move_with_the_build`, asserting it is
still `[1, 2, 3, 4]` AND that it now differs from
`bundle.document_versions()`, which is `[1, 2, 3, 4, 5, 6]`.

### 8.6, 8.7 The record

`README.md`'s row is now `| 0.2.0 | 15 | 1, 2, 3, 4, 5, 6 |`, the
parenthetical about 13 left as it is, and nothing else in the file
touched. `CHANGELOG.md`'s existing API-8 bullet had its last clause
amended from "A version 6 document is refused by name and by list" to
name version 7 — the smallest true edit, made where the untrue claim is.

Three further version assertions elsewhere had to follow the number,
none of them a behaviour change: `tests/test_widget_e2e.py`'s
`result['bundle']` 14 → 15, `tests/test_cli.py`'s reported
`documentVersions`, and the `apiVersion` assertions inside
`tests/test_lock_document.py` and `tests/test_running_document.py`.

## 9. The Curta, in a real browser (design D9)

### 9.1 The export

From a throwaway copy of solid-node at main `8e15791`
(`git archive 8e15791 | tar -x -C <scratch>`), never the pilot's
checkout:

```text
$ PYTHONPATH="$PWD" solid export \
    tests/clearing_project/machine.py:CurtaInterface -o <dir> --no-widget
WARNING - core.export - this model needs document version 6, and the
  installed browser viewer renders 1, 2, 3, 4, 5 (solid-node-viewer
  0.1.0). The export is written anyway: an export is an artifact a LATER
  viewer may open, and a viewer that cannot read it refuses it by name
  rather than rendering part of a machine it does not understand. A
  browser that runs the machine is the viewer package's own next release.
Exported to …/clearing-export
```

The producer's own warning names the refusal this cycle removes.

The file written is `manifest.json`, 16,153 bytes, `md5
cd9a3de93d232f15185638f534c0c942`, and it is committed byte for byte as
`tests/fixtures/clearing/viewer.json` — the rename being the only thing
done to it, since every other running fixture here is called
`viewer.json` and the loader reads either by the fields they share. It
declares **version 6**, one driver (`clearing`), six coordinates at the
fixture's own rests (`result0.turn` 36, `result1.turn` 72,
`result2.turn` 108, `counter0.turn` 144, `counter1.turn` 180,
`counter2.turn` 216), thirty bindings, and **six law edges, each with
`needs ∩ gives` non-empty and `affine: [false]`**.

**What the export needed, and what it did not change.**
`tests/clearing_project/machine.py` reaches its `Arbor` through
`from ..running_project.parts import Arbor`, which resolves under pytest
and not under `solid export`: the framework's loader takes
`tests/pyproject.toml` as the project root, so the module loads as
`clearing_project.machine` and the relative import goes beyond the
top-level package (`Error loading node: attempted relative import beyond
top-level package`). In the throwaway copy that ONE line became
`from running_project.parts import Arbor`.

That it changed nothing was checked rather than assumed:

```text
$ pytest tests/test_running_reads.py -k Curta   # pristine copy
3 passed, 32 deselected, 19 subtests passed
$ pytest tests/test_running_reads.py -k Curta   # the edited copy
3 passed, 32 deselected, 19 subtests passed
```

and the published program is **byte-identical** between the two copies
apart from its `identity` hash:

```text
sn2 identity eb3404956f88c88b0652efe4b1da947ed43ad5d2c25fe8c1dc39e556aee82ead
sn  identity 7425122fcfafee5a96152d79dd6a4ec4d66d1745a569abe7997ee9d00db4eecb
PUBLISHED PROGRAMS BYTE-IDENTICAL apart from identity
```

with every dial clearing to exactly `359.5` under `Sim` in both. **A
FINDING for the pilot, on the framework's side and not this cycle's: a
program's `identity` is not invariant under the machine's import path.**
It is a restore gate — "this state came from this machine" — so nothing
here depends on it, and the fixture's README records both strings so
nobody rediscovers this.

### 9.2 The geometry stood in

The one distinct model path the document names —
`models/running_project/parts-Arbor-ff269d604af9.stl`, referenced by all
six dials — holds the 684-byte binary unit cube
`tests/fixtures/pascaline` already carries.
`tests/fixtures/clearing/README.md` says in that fixture's voice what is
verbatim, what is a stand-in, which framework commit it came from, and
the import line. `tests/support.py` gains `CLEARING = FIXTURES /
'clearing'`, and `ClearingFixtureTest` checks that all six model
references resolve, that the document is 16,153 bytes at version 6, and
that every one of the six laws reads the end it drives.

### 9.3 Through `Engine.load`

Four vitest cases, all green first run: the fixture loads; each of the
six edges carries a one-entry `retained` naming its own driven end; each
reading's `dependent` is exactly the band's `['floor', '>=']` and its
`outer` the rack's reach comparisons; and every reading's `affine` is
`false` — the `clamp01` station window, which makes every one of this
fixture's self-read crossings a SEARCHED one.

### 9.4, 9.5 The browser

`tests/test_clearing_document.py`, in `test_lock_document.py`'s shape
(`needs_playwright`, `needs_bundle`, `serve_directory`, `page.evaluate`
over the mounted handle). The measured banks, printed by the test:

```text
the Curta clearing in a browser: runsInWorker=True
  rest:    {'clearing': 0, 'counter0.turn': 144, 'counter1.turn': 180,
            'counter2.turn': 216, 'result0.turn': 36, 'result1.turn': 72,
            'result2.turn': 108}
  cleared: {'clearing': 1, 'counter0.turn': 359.5, 'counter1.turn': 359.5,
            'counter2.turn': 359.5, 'result0.turn': 359.5,
            'result1.turn': 359.5, 'result2.turn': 359.5}
  again:   {'clearing': 2, 'counter0.turn': 359.5, 'counter1.turn': 359.5,
            'counter2.turn': 359.5, 'result0.turn': 359.5,
            'result1.turn': 359.5, 'result2.turn': 359.5}
  crossings on the first sweep: 18, on the second: 0, stops: 0
```

`359.5` is `360 − GAP`, which is the framework's OWN expected value for
the same machine (`CurtaShapeTest.test_every_dial_clears_to_its_gap`
asserts `sim.state[f'{name}.turn'] == 360.0 - GAP` for all six). It
mounted with no refusal, reported `apiVersion` 15, `dt` `1/240`, tick 0
and the published rests; one sweep of `clearing` completed its whole
travel and left all six dials inside the band on the disengaged side; a
second sweep completed its whole travel and moved no dial AT ALL — bit
for bit, `assertEqual` on the floats, and zero crossings; no stop was
recorded anywhere; and every crossing named a dial's own coordinate.

`4 passed, 12 subtests passed in 5.44s`.

Two inspected screenshots:
`tests/_shots/curta-clearing-at-rest.png` and
`tests/_shots/curta-clearing-cleared.png`. **What they show, honestly:**
the six stand-in cubes in the diagonal line the machine's `render()` puts
them in, the `clearing` readout at `0.0000` and then `1.0000`, and the
clock at `0:00.00` and then `0:01.00`. The cubes are 1 mm against a
125 mm spread, so a dial's 251.5° of rotation is not perceptible at this
scale — the canvas DID change (the page's own
`restShot !== clearedShot` assertion passes, and
`clearedShot === afterSecondSweep` passes too, which is the mechanism),
but the pixels that carry it are a handful. That is what a stand-in cube
buys, and it is the fixture the design asked for.

## 10. What it costs (design D8)

`src/run/cost.test.ts` gains two printed measurements. The numbers, from
one run of the whole suite:

```text
  CarryLead, affine plans: 20000 ticks in 0.581 s = 34397 ticks/s
  CarryLead, plans forced to search: 1000 ticks in 0.138 s = 7230 ticks/s
  Train, no constraint: 20000 ticks in 0.207 s = 96813 ticks/s
  Captured, blocking ticks: 2000 ticks in 0.038 s = 52918 ticks/s
  the lock, idle: 2400 ticks in 0.274 s = 8750 ticks/s
  the lock, advancing the key: 2400 ticks in 18.926 s = 127 ticks/s
  Clearing, a solved self-read: 20000 ticks in 3.760 s = 5319 ticks/s
  the Curta fixture at dt = 1/240: 2400 ticks in 12.723 s = 189 ticks/s
  the Pascaline at dt = 1/240: 2400 ticks in 0.066 s = 36258 ticks/s
```

Against the producer's own numbers for the same shapes — `Clearing`
1 349 ticks/s and `CurtaInterface` 24.4 ticks/s in Python — this engine
is about 3.9× and 7.7× faster respectively.

### 10.2 A machine with no self-read does not move

Measured on this bench, `src/run/cost.test.ts` run ALONE so the
comparison is like for like: `Train, no constraint` **140 663 ticks/s**
with every source file at its base content, **165 250 ticks/s** with this
cycle's. That is inside this host's run-to-run spread (the same bench
prints anywhere from 73 000 to 168 000 ticks/s depending on what ran
before it), and in the direction of no cost either way: a document with
no self-read edge pays one array-length test per edge per tick.

### 10.3 **THE FINDING: the Curta fixture does NOT run at real time at the viewer's default step**

At `dt = 1/240` real time is **240 ticks a second**. The committed Curta
fixture runs at **189 ticks/s** on this bench — **0.79× real time**.

It runs CORRECTLY at `1/240`: the browser acceptance drives 240 ticks per
sweep at that step and every dial lands on the framework's own number.
It is not fast enough to do so in real time on this machine, so a maker
watching it sweep would see it take about 1.27 s of wall clock per second
of machine time.

Nothing was widened, coarsened or skipped to make that number look
better, as design D8 requires. The cause is stated in the design and
measured here: the `clamp01` station window makes
`_affine_in_sources(plan.skeleton)` answer false for all six edges, so
every one of this fixture's self-read crossings falls to the 64-sample
search plus its bisection — six dials of it — where the corpus's own
`Clearing`, whose skeleton IS affine, solves and runs at 5 319 ticks/s,
twenty-eight times faster. The framework recorded the same shortfall
shape on its own side and named the same follow-up: a cheap exact path
for a kinked-but-piecewise-affine skeleton. It is neither package's
this cycle.

## 11. The whole suite, and the build

```text
$ npm run typecheck
> tsc --noEmit
(clean, exit 0)

$ npm test
 Test Files  36 passed (36)
      Tests  869 passed (869)
   Duration  ~21 s
```

(806 on the base; 63 added.)

```text
$ npm run build
  dist/solid-widget.js  702.5kb
⚡ Done in 126ms
$ ls -l dist/solid-widget.js
-rw-rw-r-- 1 asa asa 719398 Sep 15 17:23 dist/solid-widget.js
```

(685.7 kb / 702 107 bytes on the base: +16.8 kb, +17 291 bytes.)

```text
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests -q
121 passed, 53 warnings, 12 subtests passed in 112.72s (0:01:52)
```

(114 on the base; 7 added — four in `test_clearing_document.py`, two in
`test_capture.py`, one in `test_bundle.py`.) Nothing skipped: this
environment carries Playwright, Chromium and Pillow. The 53 warnings are
the same pre-existing Pillow `getdata` deprecations.

`acceptance.test.ts` — the Pascaline module — is unchanged to the digit,
`tens.drum.turn` still `65.54` after ten `Add one`; and
`test_lock_document.py` is unchanged but for the API version number it
asserts.

## 12. The record

`CHANGELOG.md` gains four bullets at the head of `0.2.0 — unreleased`:
the worker executing a law that reads the coordinate it drives, the
Curta's clearing interface in a browser, the regenerated corpus, and the
version moves. The existing API-8 bullet's untrue clause was amended in
place (§8.7 above).

`openspec validate execute-the-self-read --strict`:

```text
Change 'execute-the-self-read' is valid
```

12.2 (ADR-057) and 12.3 (spec sync and archive) are the reviewer's, and
are deliberately NOT done here.

## Everything this cycle changed

Widget source:

- `solid_node_viewer/widget/src/run/program.ts` — `LandingInvariantError`,
  `RefusalKind` gains `'landing'`, the `RetainedReading` interface,
  `ProgramEdge.retained`, the derivation in `loadProgram` and the three
  load-time refusals.
- `solid_node_viewer/widget/src/run/jumps.ts` — `ordinalOf`,
  `fromOrdinal`, `ulpOf`, `nextAfter`, `copySign`, `halved`,
  `onSurface`, `chattering`, `unlanded`, the `Walk` class, and
  `retainedIncrement`/`retainedCuts`.
- `solid_node_viewer/widget/src/run/edges.ts` — `edgeIncrements` takes a
  `landings` output and dispatches on `edge.retained.length > 0`;
  `edgeCuts` routes a self-read end through `retainedCuts`.
- `solid_node_viewer/widget/src/run/run.ts` — `landed()`, the `landings`
  map threaded through `pass()` and applied in both places `integrate`
  builds a committed state, and `LandingInvariantError` in the catch.
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS` and the
  program gate.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi` 15,
  `solidNodeDocumentVersions` `[1, 2, 3, 4, 5, 6]`.
- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  producer's regenerated copy, byte for byte.
- `solid_node_viewer/widget/dist/solid-widget.js` — rebuilt.

Widget tests: `src/run/program.test.ts`, `src/run/jumps.test.ts`,
`src/run/edges.test.ts`, `src/run/run.test.ts`,
`src/run/running-corpus.test.ts`, `src/run/cost.test.ts`,
`src/version.test.ts`, `src/document.test.ts`.

Python: `solid_node_viewer/capture.py`; `tests/support.py`;
`tests/test_clearing_document.py` (new); `tests/fixtures/clearing/`
(new: `viewer.json`, `README.md`, the stand-in mesh);
`tests/test_capture.py`, `tests/test_bundle.py`, `tests/test_cli.py`,
`tests/test_widget_e2e.py`, `tests/test_lock_document.py`,
`tests/test_running_document.py`; `tests/_shots/curta-clearing-at-rest.png`
and `tests/_shots/curta-clearing-cleared.png`.

Record: `CHANGELOG.md`, `README.md`, and this change's own
`tasks.md`/`evidence.md`.

Nothing in the framework, nothing in another checkout, nothing staged or
committed anywhere.

## 12.4 Findings for the pilot

1. **The Curta fixture does not run at real time at the viewer's default
   `1/240` s step.** 189 ticks/s against the 240 a second real time
   needs — 0.79×. It runs CORRECTLY at that step; it is not fast enough
   to keep up with a wall clock on this bench. The cause is the
   `clamp01` station window making all six skeletons non-affine, so
   every self-read crossing is searched; the corpus's `Clearing`, whose
   skeleton IS affine, solves and runs 28× faster. The follow-up — a
   cheap exact path for a kinked-but-piecewise-affine skeleton — is the
   one the framework already named on its own side, and is neither
   package's this cycle. Nothing was widened, coarsened or skipped.

2. **The corpus catches none of the three defects the walk's
   corrections exist for.** With each reintroduced in turn, all 17
   scenarios stay green (§4.7). The three node tests in
   `jumps.test.ts` are the only thing here that would catch them. Worth
   knowing on both sides: the corpus pins the ALGORITHM'S ANSWERS on the
   machines it carries, not the corrections themselves, and a second
   runtime can be wrong in ways one fixture cannot see.

3. **A program's `identity` is not invariant under the machine's import
   path** (§9.1) — the same class, reached as
   `tests.clearing_project.machine` and as `clearing_project.machine`,
   publishes a byte-identical program under two different identity
   hashes. A framework observation, not this cycle's; the identity is a
   restore gate, so nothing here depends on it, and the fixture's README
   records both strings.

4. **Where the design and `program.py` disagreed, `program.py` won,
   once** (§2): design D1's refusal 3 names "the plan's SKELETON", and
   `program.py` l. 2580 checks `plan.skeleton if plan is not None else
   graph` — so a self-read carrying NO plan is judged on its expression.
   The loader here does the same, which is a slightly WIDER refusal than
   the design's prose and the only way the sentence stays true.

5. **`src/partControls.ts` contains literal NUL bytes** (its
   `` `${kind}\0${part}` `` key), so `grep` treats it as a binary file
   and needs `-a` to search it. Harmless, pre-existing, and a trap for
   anyone searching this tree.

6. **A segment landing is only observable when nothing after it can put
   it right** (§5.2). The first attempt at that test passed with the
   segment's `landed` call deleted, because the remaining stretch landed
   the coordinate again. Anyone writing a similar test needs a stop that
   blocks the input for the rest of the tick.
