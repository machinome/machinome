# Evidence — execute-bounds-reading-other-coordinates

Every run below was made in the cycle worktree
`solid-node-viewer/WTs/bounds-read-other-coordinates`, on branch
`bounds-read-other-coordinates`, off viewer main `1aefbc0`.
`node_modules` is the main checkout's, reached through a symlink; no
`npm ci` and no `npm install` was run.

## 0. The baseline, on the planning commit `dabe2a2`

Package `0.2.0`, declared API version `12`, `documentVersions ==
[1, 2, 3, 4, 5]` — none of the three moves in this cycle.

`npm run typecheck`:

```text
> @solid-node/widget@0.2.0 typecheck
> tsc --noEmit
```

(clean, no output.)

`npm test`:

```text
 Test Files  36 passed (36)
      Tests  732 passed (732)
   Start at  18:18:52
   Duration  4.34s
```

`npm run build`:

```text
> @solid-node/widget@0.2.0 build
> node build.mjs

  dist/solid-widget.js  674.6kb

⚡ Done in 101ms
```

Python suite, `PYTHONPATH=<worktree>
/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/ -q -rs`:

```text
105 passed, 27 warnings in 91.21s (0:01:31)
```

Nothing skipped: the workspace venv carries Playwright and Chromium, so
`needs_playwright` and `needs_bundle` are both satisfied here.

### 0.4 The refusal this cycle removes

`loadProgram` on
`projects/Locks/Pin_tumbler_lock/_build/viewer.json`, on this base:

```text
viewer.json declares document version 5 and the bound declared on
"plug.key.insert" names "plug.turn", which it may not read. It may read:
plug.key.insert. Quoting the expression: "(-60.0 - (-60.0 * (abs(plug.turn)
> 0)))". The document is malformed: refusing it rather than running a
machine this viewer cannot execute.
```

## 1. The corpus

### 1.1 Copied byte for byte

```text
b43111d2356f864d64a005b3ed3f63d4dd6ac27d250e859fdc5a11f2b88450b1  solid-node/WTs/bounds-read-other-coordinates/tests/running-corpus.json
b43111d2356f864d64a005b3ed3f63d4dd6ac27d250e859fdc5a11f2b88450b1  solid_node_viewer/widget/src/running-corpus.json
```

14 scenarios, 12 distinct machines, 276 ticks, tolerance
`{"float": 1e-09}`. The machines, in order: Train 0.05/30, Train 0.1/20,
Window 0.05/24, Remainder 0.05/24, Wrapped 0.05/20, Throwing 0.05/20,
Clutch 0.05/24, CarryLead 0.05/24, CarryLead 0.1/14, Ratchet 0.05/20,
Swept 0.01/16, TwoStops 0.05/12, StopAndJump 0.05/12, **Captured
0.05/16**.

### 1.2 RED — `npm test -- running-corpus` on the untouched engine

Thirteen scenarios green; `Captured` red, and nothing else:

```text
   ✓ the running corpus > replays StopAndJump at dt=0.05 (scenario 13) 1ms
   × the running corpus > replays Captured at dt=0.05 (scenario 14) 1ms
     → running-corpus.json#Captured declares document version 5 and the bound
       declared on "key.travel" names "plug.turn", which it may not read. It
       may read: key.travel. Quoting the expression: "(20 * (plug.turn > 0))".
       The document is malformed: refusing it rather than running a machine
       this viewer cannot execute.

 FAIL  src/run/running-corpus.test.ts > the running corpus > is the framework's own fixture, unedited
AssertionError: expected [ …(14) ] to have a length of 13 but got 14

      Tests  2 failed | 15 passed (17)
```

### 1.3 The width guard, widened

`REQUIRED` gains `'a bound reading another coordinate'` and `'a stop
reached by the motion of what a bound reads'`, both computed the
generator's way (`tools/generate_running_corpus.py:285-331`): the first
over a span side whose free names, CLOSED over the fixture's own
`bindings`, hold a bank id other than the span's key (a `freeNamesOf`
closure written in the test file, reading the fixture and nothing else);
the second over a recorded stop whose coordinate holds the same value in
the previous tick's bank — or the published `initial`, on tick one — as
in its own.

GREEN on the new corpus and RED on a narrowed copy (`Train` alone), which
now names both:

```text
   ✓ the corpus's width > exercises every feature the producer's generator requires
   ✓ the corpus's width > is refused when the corpus is narrowed
```

## 2. Reading the bound (`src/run/program.ts`)

### 2.1–2.2 RED — `npx vitest run src/run/program.test.ts`

Seven of the new cases red before the change:

```text
   × loads a bound naming a second bank coordinate
   × loads a bound reaching its read ONLY through the bindings table
   × sorts the reads, and never holds the own coordinate
   × derives the sub-program: the determining edges, in published order, and never a check
   × derives the candidates: the union of the reaching-input lists
   × makes no entry for a self-only bound, a number or an absent side
   × refuses a bound naming a published computed value, saying so

Error: … the bound declared on "first.turn" names "gate.lift", which it may
  not read. It may read: first.turn. Quoting the expression:
  "(90 * (abs(gate.lift) <= 0.05))". …
Error: … names "gate.lift" … Quoting the expression: "(90 * _b1)". …
TypeError: Cannot read properties of undefined (reading 'size')
AssertionError: expected 'http://example.test/viewer.json decla…' to contain
  'a published computed value'
      Tests  7 failed | 43 passed (50)
```

(The clock, the unknown id and the branch placeholder were already
refused and stayed refused — those three cases are green both sides, and
they are the ones that must not change.)

### 2.3–2.4 GREEN

`loadProgram` now publishes `constraints: ReadonlyMap<string,
Constraint>`; `program.test.ts` is 55 passed.

## 3–4. Executing the bound (`src/run/run.ts`)

### RED — the framework's own numbers, against the engine without the substitution

With `boundsNow()` returning `boundOf(...)` for every side (the one line
that makes a constraint a constraint removed, everything else in place):

```text
 FAIL  the Gate > turns once every pin clears
AssertionError: expected +0 to be close to 30, received difference is 30
 FAIL  the Gate > admits insertion and refuses turning in one tick
AssertionError: expected 'blocked' to be 'completed'
 FAIL  the Gate > stops the key withdrawing from a turned plug (the sampled path)
AssertionError: expected +0 to be close to 30, received difference is 30
 FAIL  the Gate > admits the same travel at any cadence
AssertionError: expected 'completed' to be 'blocked'
 FAIL  the Gate > replays a constraint stop identically from a snapshot
TypeError: Cannot read properties of undefined (reading 'coordinate')
 FAIL  the Captured gate > stops the key at once
AssertionError: expected +0 to be close to 30, received difference is 30
 FAIL  the Captured gate > returns the plug and refuses the withdrawal in one tick
AssertionError: expected 'blocked' to be 'completed'
 FAIL  the PawlRatchet > releases the reverse when the pawl clears early
AssertionError: expected 36 to be close to 30, received difference is 6
 FAIL  a quiet bound costs nothing > takes no sample when nothing the constraint depends on moves
AssertionError: expected 1 to be greater than 1
      Tests  9 failed | 21 passed (30)
```

The line was then restored and the full widget suite re-run green. Two
of the thirteen new cases — the plug blocked at `t = 0` and the pawl
clearing late — happen to agree with the unsubstituted engine by
coincidence of the numbers, so they are not part of the red set.

### GREEN — every number is the framework's own

`tests/test_running_stops.py` reproduced as `bench()` documents in
`src/run/run.test.ts`: `PinCrossingTest` (6 cases), `CaptureTest` (2),
`PawlRatchetTest` (2), a quiet-bound pair, a one-event numeric + constraint
case, and the sub-program pass (a jumping law inside it, and the group
rule). `run.test.ts`: 32 passed.

## 5. The corpus, green

```text
   ✓ the running corpus > is the framework's own fixture, unedited
   ✓ … replays Train, Train, Window, Remainder, Wrapped, Throwing, Clutch,
     CarryLead, CarryLead, Ratchet, Swept, TwoStops, StopAndJump,
     Captured (scenarios 1–14)
   ✓ the corpus's width > exercises every feature the producer's generator requires
   ✓ the corpus's width > is refused when the corpus is narrowed
      Tests  17 passed (17)
```

All 14 scenarios, 276 ticks, exact for discrete state and within `1e-9`
relative for floats.

## 6. The whole suite, and the build

```text
> tsc --noEmit                       (clean)

 Test Files  36 passed (36)
      Tests  767 passed (767)
   Duration  18.82s

> node build.mjs
  dist/solid-widget.js  680.8kb
```

Python suite, with the rebuilt bundle:

```text
110 passed, 27 warnings in 98.35s (0:01:38)
```

Nothing skipped (105 before, +5 from `tests/test_lock_document.py`).

**6.3** — the Pascaline acceptance is unchanged to the digit:
`src/run/acceptance.test.ts` and
`tests/test_running_document.py` both still pin `tens.drum.turn` at
`65.54` after ten `Add one`, and both are green.

## 7. The lock, in a real browser

### 7.1 The document

`tests/fixtures/lock/viewer.json` is
`projects/Locks/Pin_tumbler_lock/_build/viewer.json`, `cmp`-identical,
**26,278 bytes**. Version 5; program identity
`b45402a563493d03462a51b456059300c74c75c61f74bc206a7f38cc7746c867`;
drivers `insertion` (mm, `[-60, 0]`) and `rotation` (deg, `[-90, 90]`);
six instructions; sixteen coordinates; fourteen edges; twenty-three
bindings; eleven flexible pieces.

### 7.2 The meshes

The tree names **fifteen model references over eleven distinct paths**
(the driver pin appears five times), not fifteen distinct files as the
tasks say. Each of the eleven holds the 684-byte unit cube
`tests/fixtures/pascaline/vendor/printables-28807/0_base-…stl` already
carries; the whole fixture is 80 kB instead of 3.2 MB.
`tests/fixtures/lock/README.md` says which half is verbatim.
`tests/support.py` gains `LOCK` and `published_lock`, and
`LockFixtureTest` asserts every model path resolves.

### 7.3 The derived table, asserted directly

The document carries **three** constraints, not two: `plug.turn`'s LOW
side reads the five lifts exactly as its high side does. Measured:

```text
plug.key.insert:low  reads ["plug.turn"]
                     edges 2  ["insertion drives plug.key.insert",
                               "rotation drives plug.turn"]
                     candidates ["insertion","rotation"]
plug.turn:low        reads ["plug.p1.lift","plug.p2.lift","plug.p3.lift",
                            "plug.p4.lift","plug.p5.lift"]
                     edges 7  ["insertion drives plug.key.insert",
                               "rotation drives plug.turn",
                               "plug.key.insert drives plug.p1.lift",
                               … p2 … p3 … p4 … p5]
                     candidates ["insertion","rotation"]
plug.turn:high       identical to plug.turn:low
```

The five `d*.lift` numeric spans make no entry.

### 7.4 The acceptance, `tests/test_lock_document.py`

Playwright and Chromium both ran here. Measured in the page (the run
executed in a Web Worker, `runsInWorker=True`):

```text
mounted:  identity b45402a5…, apiVersion 12, dt 1/240, tick 0,
          bank plug.turn = 0, plug.key.insert = 0,
          instructions ['Advance one pin', 'Back one pin',
                        'Return the plug', 'Seat the key',
                        'Turn the plug', 'Withdraw the key']

turned:   90 deg, [['rotation', 'completed', 90]]            no stop
captured: insert=0, [['insertion', 'blocked', 0]],
          stop={'tick': 361, 'coordinate': 'plug.key.insert',
                'bound': 'low', 'value': 0, 't': 0,
                'inputs': ['insertion']}
returned: [['rotation', 'completed', -90]]
withdrew: insert=-60, [['insertion', 'completed', -60]]
blocked:  turn=0, [['rotation', 'blocked', 0]],
          stops=[{'tick': 1873, 'coordinate': 'plug.key.insert',
                  'bound': 'low', 'value': -60, 't': 0,
                  'inputs': ['rotation']},
                 {'tick': 1873, 'coordinate': 'plug.turn',
                  'bound': 'high', 'value': 0, 't': 0,
                  'inputs': ['rotation']}]
```

The last tick carries TWO stops, not one: turning the plug would raise
the key's own low bound from `-60` to `0`, so the standing key at `-60`
becomes invalid and `rotation` is stopped by the key's bound as well as
by the plug's. That is the ratified "a dependency never overruns a
standing coordinate" scenario firing on the lock's own document, and the
acceptance asserts the plug's stop by containment.

### 7.5 The pixels

`tests/_shots/lock-plug-turned-key-seated.png` and
`tests/_shots/lock-key-held-by-turned-plug.png`, both inspected: the
lock's eleven molejo springs and its stand-in cubes render, the panel
reads `insertion 0.0000 mm` / `rotation 90.0000 deg` in both, and the
elapsed clock moves from `0:01.50` to `0:03.90` between them — 576 steps
in which the captured key admitted nothing and moved nothing. The
acceptance asserts the canvas CHANGED between rest and the turned plug,
and did NOT change across the capture.

## 8. What it costs (design D9)

Measured by `src/run/cost.test.ts` on this bench (Linux, the workspace
node):

| measurement | ticks/s | ms/tick | floor asserted |
| --- | --- | --- | --- |
| `Train`, no constraint (regression floor) | 182,029 | 0.0055 | 17,000 |
| `Captured`, blocking ticks | 130,907 | 0.0076 | 11,000 |
| the lock, idle | 18,310 | 0.055 | 1,500 |
| the lock, advancing the key | 144 | **6.9** | 15 |
| CarryLead, affine plans (unchanged) | 95,874 | — | 10,000 |
| CarryLead, forced to search (unchanged) | 17,054 | — | 1,000 |
| the Pascaline at dt = 1/240 (unchanged) | 34,485 | — | 2,400 |

Beside the framework's own (ADR-113, CPython): `Gate` 0.36 ms quiet /
5.4 ms active / 3.3 ms blocking; the lock 2.9 ms idle / 4.7 ms turning /
**45 ms advancing the key**.

**FINDING — the lock does not advance its key at real time.** At the
default step size `1/240` s a tick has about **4.2 ms**; advancing the
lock's key costs **6.9 ms**, so the worst case runs at about **0.6×**
real time. The worker is about **6.5× cheaper than CPython** for the same
tick (6.9 ms against 45 ms), which is the hash-consed DAG doing its job,
but it is not enough. Nothing was widened, coarsened or skipped to hide
it. The framework's own recorded follow-ups are where it is bought back,
and they belong in both runtimes together: `f(start)` once per stretch
per edge, and one sampling for the two sides of one coordinate — the
latter alone would halve this number, since `plug.turn`'s low and high
sides sample the identical seven-edge sub-program at 64 subdivisions.

Note also that a quiet constraint costs nothing measurable: the lock idle
runs at 18,310 ticks/s with three constraints declared, and `Train`, which
declares none, measures what it always measured.

## 9. The record

- `CHANGELOG.md` — four new bullets under `0.2.0 — unreleased`.
- `README.md` — **unchanged**. Its run and conformance paragraphs state
  neither the corpus's counts nor what a bound may read, so no statement
  in it became false.
- `docs/adrs/EXPORT/ADR-054-a-constraint-is-derived-from-the-published-document.md`,
  extracted after implementation, with the measurements above; added to
  `docs/adrs/README.md` in chronological order.
- `openspec validate execute-bounds-reading-other-coordinates --strict`:
  `Change 'execute-bounds-reading-other-coordinates' is valid`.
- Spec synchronization and archival are NOT done: this apply phase stops
  before them, and before any commit.
