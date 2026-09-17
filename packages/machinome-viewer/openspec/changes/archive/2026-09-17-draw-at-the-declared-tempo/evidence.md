# Evidence: `draw-at-the-declared-tempo`

Every red logged before its fix, every measurement as it came out of the
machine. Worktree
`solid-node-viewer/WTs/clocked-machine`, branch `draw-at-the-declared-tempo`,
base commit `331621c` (the ratified planning commit over `06576a3`).

## 0. The base, re-checked at implementation time

- `md5sum src/clocked-corpus.json` -> `bc4174cf47f844b035125ed3afcee3aa`
  (unchanged from tasks 0.1; this cycle never touches it).
- `dist/solid-widget.js` 804 950 B.
- `git status --short` carried only the change directory.
- The fixture the acceptance runs on, read at implementation time:
  `tests/fixtures/calculator/viewer.json` is version 8, `clocked.clock`
  `null`, drivers `crank, feed, operand, ring, setting`, instructions in
  declaration order `"Set four"` (`targets operand 4`, duration 0.5) then
  `"Stroke"` (`by crank 360`, duration 2.0). One `targets` source that is
  not a tempo and one `by` source that is; `feed`, `ring`, `setting` named
  by neither.

## RED 1 — the tempo has no function to answer it (task 1.1)

`npx vitest run src/clockedControls.test.ts` with the corrected and
extended policy test, before `gestureSeconds` existed:

```
 FAIL  src/clockedControls.test.ts > the clocked chrome > states how long a
 drawn GESTURE takes: the TEMPO its input's declared instruction states, and
 the viewer's own short duration where the document states none
TypeError: (0 , gestureSeconds) is not a function
 ❯ src/clockedControls.test.ts:220:12
 Test Files  1 failed (1)
      Tests  1 failed | 20 passed (21)
```

GREEN after task 1.2 (`gestureSeconds` in `clockedControls.ts`):
`21 passed (21)`.

## RED 2 — every gesture is drawn over a fifth of a second (tasks 2.1, 4.1-4.4)

`viewer.ts` has no node-level harness, so the wiring's red is a browser
one. The acceptance of §4 was written first and run against the BASE
bundle (`dist/solid-widget.js`, 804 950 B, the committed ADR-065 build,
with `gestureSeconds` implemented but nothing calling it).

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=$PWD \
  .venv/bin/python -m pytest \
  tests/test_calculator_document.py::GestureDrawnInABrowserTest -q -s

  calculator gesture: 12 frames over 0.20 s (60.3 fps), per-frame pose
      median 0.40 ms, worst 0.70 ms
  tempo declared:    12 frames over 0.20 s,  0 -> 360  (12 distinct poses)
  tempo twelfth:     12 frames over 0.20 s,  0 ->  30  (12 distinct poses)
  tempo twice:       12 frames over 0.20 s,  0 -> 720  (12 distinct poses)
  tempo targetsOnly: 12 frames over 0.20 s,  1 ->   9  ( 9 distinct poses)
  tempo unnamed:     12 frames over 0.20 s,  0 ->  25  (12 distinct poses)
  tempo press:      121 frames over 2.02 s,  0 -> 360  (121 distinct poses)

E  AssertionError: 0.19980000001192094 not greater than 1.5
FAILED ...::test_a_gesture_on_a_handle_is_one_request_drawn_at_its_tempo
```

The red is the finding itself, measured: EVERY gesture takes 0.20 s
whatever the input and whatever the travel — a whole turn, a twelfth of
one, twice one, and two inputs no declared travel names, all twelve
frames — while the PRESSED instruction of the same 360-degree travel
already takes the 2.02 s it declares. A whole turn in twelve frames is
30 degrees a frame, and the Curta's 11.25-degree tooth passage falls
inside one of them.

The committed acceptance went red on the tempo in TWO further places
before it was updated, each logged rather than quietly rewritten:

- `frozen mid-nudge at crank 360, landed at 360` — `AssertionError: 360
  not less than 360`. The photograph's frame budget of 4 was sized to a
  0.2 s drawing; at the declared tempo the same nudge needs ~120 frames,
  so the budget is now 30 (a visible quarter-stroke) and the wait that
  follows it 3000 ms instead of 400 ms.
- the fixed 60-frame and 40-frame sample loops of §1, §2 and §3 no longer
  reach a landing at the declared tempo. They now sample UNTIL THE
  LANDING (the reading reaching the bank the request already stands at)
  with a cap of 900 frames, which is what "drawn" means and what a fixed
  count only stood for while every drawing was a fifth of a second.

## GREEN — the tempo, measured on the calculator (tasks 4.1-4.4)

Same page, same host, same frame rate (60 fps), with the wiring in and
the bundle rebuilt (805 192 B):

| gesture | frames | wall | travel | before (base) |
| --- | --- | --- | --- | --- |
| nudge of the DECLARED 360 on `crank` | 121 | 2.01 s | 0 -> 360 | 12 / 0.20 s |
| nudge of 30 (a twelfth) on `crank` | 11 | 0.18 s | 0 -> 30 | 12 / 0.20 s |
| typed 720 (twice) on `crank` | 241 | 4.02 s | 0 -> 720 | 12 / 0.20 s |
| nudge on `operand` (`targets` only) | 12 | 0.20 s | 1 -> 9 | 12 / 0.20 s |
| nudge on `feed` (named by nothing) | 12 | 0.20 s | 0 -> 25 | 12 / 0.20 s |
| PRESS of `'Stroke'` | 121 | 2.02 s | 0 -> 360 | 121 / 2.02 s |

Ratios asserted on the page rather than absolutes: a twelfth of the
travel took **0.091** of the time (1/11, the quantum being one frame),
twice the travel **2.000**, and the pressed instruction **1.005** of the
gesture of the same travel — the two ways of asking for one stroke,
drawn alike. 121 distinct poses where there were 12.

**The tooth passage**, which is what the pilot reported: 11.25 / 360 of
the stroke is now 11.25/360 x 121 = **3.8 frames** where it was
11.25/360 x 12 = **0.38 of one frame**. It is drawn.

## Mutation proof — the undrawn requests (task 2.3)

No red is possible for a negative, so each guard was broken on purpose,
the bundle rebuilt, and the failure recorded:

1. Panel `step()` routed through a DRAWN request
   (`clockedRequest(clock, {by: clockStep}, true)`):
   `test_regulator_document.py::RegulatorInABrowserTest` ->
   `AssertionError: False is not true : a step stopped the transport
   that asked for it`.
2. `clockFrame`'s played frame routed through a DRAWN request:
   same test -> `AssertionError: 0.06666666666666667 not greater than
   0.3 : the clock did not run` (the drawing fought the transport).
3. The MOUNT HANDLE's `move` given a drawing at the same tempo:
   `GestureDrawnInABrowserTest` -> `AssertionError: 0 != 360` at "The
   HOST's own handle is NOT drawn and lands at once".

`src/viewer.ts` was restored byte for byte from a copy taken before the
mutations and the bundle rebuilt after each.

## RED 3 — the Curta harness's own landing wait (task 5.1)

`tests/test_curta_drawing.py`'s `FREEZE` waited a fixed 1500 ms for a
nudge to land. At the declared two seconds it does not:

```
FAILED tests/test_curta_drawing.py::CurtaGestureTest::\
test_the_pilots_own_nudge_is_drawn_on_the_curta_and_timed
E  AssertionError: 72 != 360
```

(72 degrees of 360, caught part-way through the picture.) It now WAITS
FOR THE LANDING with a cap instead of for a fixed number of milliseconds
— which is what the assertion always meant — and the `watch(..., 1.0)`
windows are caps of 8 s that break at the landing, for the same reason.

## 5. The Curta, where the finding came from

The pilot's own build, READ-ONLY, served through a directory of SYMLINKS
(nothing copied into this repository). **The document as found at run
time**: version 8, `clocked.clock: "time"`, 23 drivers, one instruction
`{"Turn crank": {"by": {"crank_rotation": 360}, "duration": 2}}` — the
project has not republished with `clock: null` or a duration of 6, so
the tempo measured here is 360 degrees over 2 s.

This host renders the Curta's 54 MB of meshes on a software rasteriser
and idles that page at **2.2 fps**. Both runs below are on it, minutes
apart, with only `src/viewer.ts` and `src/clockedControls.ts` swapped
between HEAD's versions and this cycle's and the bundle rebuilt.

| the pilot's gesture | BEFORE (ADR-065) | AFTER (this cycle) |
| --- | --- | --- |
| nudge of 360 on `crank_rotation` | 1 frame over 1.16 s, readings `[0, 360]` | 3 frames over 2.21 s, readings `[0, 245.99, 323.98, 360]` |
| typed 720 (a travel of 360) | 1 frame, `[360, 720]` | 3 frames over 2.07 s, `[360, 587.97, 662.98, 720]` |
| press of `'Turn crank'` | 3 frames over 2.10 s | 3 frames over 2.28 s (unchanged) |
| nudge of 30 (a twelfth) | 1 frame | 1 frame (the tempo is 0.167 s; one frame here is 0.45 s) |

`[0, 360]` IS the teleport the pilot reported, in one line.

**The pictures at a fixed page rate.** The harness can hand the loop
timestamps at a stated spacing, which measures the RULE without this
host's frame rate in the way. Frozen two 50 ms frames into the same
nudge — what a 20 fps page draws in 100 ms:

- BEFORE: the crank stood at **180 degrees** (half the stroke, one
  frame of ADR-065's fifth of a second).
- AFTER: **18 degrees**. A tenfold finer picture at the same page rate,
  which is the whole of the change.

**5.2, the tooth passage, answered plainly.** A one-tooth advance is
`TOOTH_PITCH = 11.25` degrees of crank (`simulation/cycle.py:7`), so at
the declared tempo it occupies 11.25/360 of the drawing. On THIS host
that is 0.09 of a frame after the change and 0.03 before: **the host's
frame rate, not this cycle, is what stops the passage being drawn
here** — 2.2 fps cannot draw a 3% band of any stroke. At 60 Hz the same
tempo is 120 frames a stroke and **3.8 frames a passage**, where
ADR-065's fifth of a second gave the whole stroke 12 frames and the
passage 0.38 of one. The calculator fixture, which this host DOES render
at 60 fps, measures that directly: 121 frames a stroke, 3.8 a passage.

**5.3, the pictures**, kept OUTSIDE this repository (a measurement is
not a contract), in the scratchpad's `viewer-acceptance/`:
`curta-nudge-drawing.png` (part-way through a tempo-drawn nudge),
`curta-nudge-landed.png`, `curta-clocked-landed.png`,
`curta-fast-landed.png`. The base run's are beside them under
`viewer-acceptance-base/`.

## The closing suites (task 6.4)

- `npx tsc --noEmit` — clean.
- `npx vitest run` — **46 files, 1219 tests, 38.2 s, green** (from the
  base's 46 / 1219 / 35.2 s; the chrome's policy test was corrected and
  extended, not added).
- `pytest tests` from the worktree root on the workspace venv — **178
  passed, 18 subtests, 267.2 s, no skips**. This host carries the
  Curta's builds, so both Curta measurements ran rather than skipping.
- `npm run build` — `dist/solid-widget.js` **804 950 B -> 805 192 B**
  (+242 B).
- `src/clocked-corpus.json` untouched, md5 still
  `bc4174cf47f844b035125ed3afcee3aa`; `git diff --stat` over
  `src/clocked/drawing.ts`, `src/clocked/machine.ts`, the corpus,
  `src/run/`, `src/drivers.ts` and `src/runControls.ts` EMPTY.
- `solidNodeViewerApi` **19**, `solidNodeDocumentVersions` **[1..8]**,
  `src/version.ts` and `src/version.test.ts` untouched.
- `openspec validate --all --strict` — 7 passed, 0 failed.
