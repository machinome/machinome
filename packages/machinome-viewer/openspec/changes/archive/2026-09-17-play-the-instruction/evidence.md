# Evidence: `play-the-instruction` (solid-node-viewer)

Every RED run below was made and SEEN to fail for the stated reason
before the change that turned it green. Commands were run from
`solid_node_viewer/widget` (`npx vitest run`, `npx tsc --noEmit`,
`npm run build`) or from the worktree root (`pytest`), inside
`solid-node-viewer/WTs/clocked-machine` on branch `play-the-instruction`.
`npm ci`, `npm install` and `scripts/check-dist` were never run.

## The base (task 0.1, re-verified at implementation)

`solidNodeViewerApi: 18`, `solidNodeDocumentVersions [1..8]`, worktree
head `d365f7c` (the ratified planning commit over viewer main `757ad84`).
`src/clocked-corpus.json` 139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`.

## 1.1 The census, moved to the numbers the new file carries — RED

`npx vitest run src/clocked/clocked-corpus.test.ts` → **6 failed | 38
passed**, every failure naming the OLD file:

```
the clocked corpus > is the producer's file, byte for byte
  AssertionError: expected 139262 to be 145673
the census this build claims > is 81 steps over 30 machines
  AssertionError: expected 76 to be 81
the census this build claims > carries 917 recorded numbers in all
  AssertionError: expected 722 to be 917
the census this build claims > counts the 13 machines whose interlocks
  this build must execute
  AssertionError: expected 36 to be 41
the census this build claims > is derived from the file: a machine added
  to it is counted
  AssertionError: expected 83 to be 88
the census, closed > replayed every machine, every step and every
  recorded number
  AssertionError: expected 76 to be 81
```

The md5 assertion failed with it (`852b86b8…` vs `bc4174cf…`).

## 1.2 The producer's file, copied byte for byte — RED (the cycle's corpus red)

`cp solid-node/WTs/play-the-instruction/tests/clocked-corpus.json
src/clocked-corpus.json` → 145 673 bytes, md5
`bc4174cf47f844b035125ed3afcee3aa` (verified after the copy, equal to the
producer's own). `npx vitest run src/clocked/clocked-corpus.test.ts` →
**2 failed | 42 passed**: the census is green on the new file and the
replay is red on the new verb.

```
the viewer reproduces the framework's own clocked corpus > replays Calculator
  Error: Calculator step 12 {"trigger":"Set four"}: unknown script step
the census, closed > replayed every machine, every step and every recorded
  number
  AssertionError: expected 77 to be 81
```

## 1.3 BOTH ENDS compared on every step — RED

Adding `exactly(result.origin, …)` and `exactly(result.end, …)` to
`replayStep` → **30 failed | 14 passed**, every machine red on a field
that does not exist:

```
replays Counter  — Counter step 0 {"move":{"input":"crank","by":3700}}
                   origin: expected undefined to be +0
replays Register — Register step 0 {"move":{"input":"operand","to":4}}
                   origin: expected undefined to be 1
… and 28 more, one per machine.
```

Verified against the file first: 65 recorded requests carry `origin` and
`end`, and every refused or session step carries neither.

## 2.1 The two ends, in `machine.test.ts` — RED

Six new tests → **6 failed | 31 passed**, all `expected undefined to be
…`: the ends verbatim from the bank before and after; every event's
value on the segment they span (`Pawl`); the stop's landing as the second
end (`Pawl`, 1100 → 1098 for an asked 1070); the two ends equal at zero
travel (`Standing`); NATIVE units told from `admitted` by a scaled driver
(`ScaledStroke`: `admitted` 4.5 design, `end` 9 native); a `to` over an
integer driver at its converted native value (`Register`, 1 → −1).

## 2.2 `ClockedRequest` gains `origin` and `end` — GREEN

`machine.ts`: the two fields returned from `origin` (`:292`) and
`clippedTarget` (`:364`), the two values `move` already held, with the
design/native asymmetry stated in the interface's doc comment as the
producer states it. `npx vitest run src/clocked/machine.test.ts
src/clocked/clocked-corpus.test.ts` → **2 failed | 79 passed**: 1.3 green
on all 30 machines, only the `trigger` verb still red.

## 3.1 `trigger` executes, in `machine.test.ts` — RED

Seven new tests → **6 failed | 38 passed**. Four threw
`ClockedRequestError` from `machine.ts:425` (the refusal by name this
cycle lifts); the two refusal tests failed on the message:

```
expected 'trigger(\'Turn crank\') asks this mac…' to contain 'Set four'
expected 'trigger(\'Stroke\') asks this machine…' to contain 'none'
```

## 3.2 / 3.3 `trigger` implemented, and the replay's fourth verb — GREEN

`ClockedMachine.trigger` resolves the instruction from
`machine.instructions`, takes its one entry and delegates to `move` — no
conversion, no rounding, no second copy of the driver resolution. The
replay's `move` branch became a request MAKER shared by both verbs, so an
instruction is compared by exactly the code a `move` is compared by.
The existing cadence regression was updated red-first in the same run:
`trigger` left the list, `step` and `rate` kept their messages.

`npx vitest run src/clocked/machine.test.ts` → 44 passed;
`src/clocked/clocked-corpus.test.ts` → **47 passed**, the whole corpus
replayed: 30 machines, 81 steps, 917 numbers, and `Calculator` step 14
(the trigger) equal field for field to step 16 (the same request by
hand), both reproduced.

## 4.1 An unplayable instruction, in `document.test.ts` — RED

Eleven new tests → **9 failed | 36 passed**, every failure
`the document was not refused`: both forms, neither form, no driver, two
drivers, a state, the clock (`Regulator`'s `time`), an undeclared id, a
travel that is not a finite number, and a duration that is negative,
infinite, NaN, a string, null or absent. The two that PASSED red are the
two that must: the producer's own `Stroke`/`Set four` load, and all
thirty corpus documents load.

## 4.2 `readInstructions` validates — GREEN

Refusals are made in the loader's own shape, naming
``its `instructions.<name>` ``and ``its `instructions.<name>.duration` ``.
`npx vitest run src/clocked/document.test.ts` → **45 passed**. Zero is a
duration and is accepted; it lands the transition at once.

## 5.1 The drawing, in `src/clocked/drawing.test.ts` — RED

16 tests written first → the file did not load at all:

```
Error: Cannot find module './drawing' imported from
  src/clocked/drawing.test.ts
```

## 5.2 `src/clocked/drawing.ts` — GREEN

`drawing(request, start, duration, integer)` with `advance(elapsed)` and
`land()`; `DrawnFrame = {value, bank, moved, done}`. **16 passed.** What
the tests pin: linear between the two ends; the endpoint the request's
OWN `end` rather than a computed approximation (proved on
`0.30000000000000004`); the origin held before 0 and the end past 1;
commits applied AT their own fraction and not before; `moved` exactly the
ids a frame changed, measured for frame 0 against the request's END bank
(where the tree stands when the drawing begins); the last frame equal to
`Pawl`'s real machine bank value for value; `land()` from any point equal
to that last frame; a DOWNWARD request drawn by the same line; a whole
number whole at every frame and never past `end` rising OR falling;
`duration: 0` landing in one frame; a zero-travel request moving nothing;
a zero-span request's `fraction: 1` commits landing at the end.

The last test COUNTS the executor's calls: `trigger` once, then 201
`advance` calls and a `land`, and the count is still 1 — with the
module taking no machine at all, so there is nothing for it to call.

## 6.3 The chrome, node half — RED then GREEN

`src/clockedControls.test.ts`, two tests rewritten and five added:

```
LISTS declared instructions PRESSABLE, carrying the outcome of the last
  press and nothing else
  AssertionError: expected undefined to be null
reports a press WHERE IT WAS MADE, by the instruction's name
  AssertionError: expected undefined to be { status: 'completed', …(4) }
what a drawn frame rewrites in the panel > (5 tests)
  TypeError: (0 , clockedFollowing) is not a function
```

Green after `ClockedInstructionControl` lost `disabled`/`reason` and
gained `outcome`, `INSTRUCTIONS_DISABLED` was deleted, and
`clockedFollowing(machine, bank, moved)` was added — the narrow decision
behind `ClockedChrome.follow`: which ids a frame rewrites, split into
handles and readouts, each saying what the rebuilt panel would have said.
**20 passed.**

## 6.1 / 6.2 / 6.4 The page — GREEN

`src/viewer.ts`: one drawing at a time beside the clock's transport;
`clockedPlay(name)` as the ONE door for the button and for
`machine().trigger(name)`; `drawFrame` posing through
`tree.update(clockedScope(bank), posed(moved))` and following the panel
through the narrow writer; `drawingFrame(elapsed)` in the render loop
beside `clockFrame`; `landDrawing()` called by every other path
(`clockedRequest`, the handle's `move`/`trigger`/`restore`/`reset`, the
panel's reset, `clockFrame`, a second press) and by `dispose`;
`drawnBank` read by `scope()` and by the panel's rebuild, so a `$t` frame
and a focus change during a drawing show what the drawing shows; the
posed `ViewerHandle.trigger` refused by name under a clocked document.

## 6.5 `npx tsc --noEmit` and `npx vitest run` — GREEN

**46 files, 1218 tests, 30.2 s, all green**, typecheck clean. The base
was 45 files / 1168 tests / 31.9 s: +1 file (`drawing.test.ts`) and +50
tests.

One EXISTING test moved with the corpus and is recorded here rather than
buried: `src/clocked/cost.test.ts`'s "holds the whole corpus's 76 steps
inside one frame budget" went red on `expected 81 to be 76`. It gained
the `trigger` verb in its own loop (a pressed instruction is one request,
so it belongs in the measured loop) and now replays **81 steps over 30
machines in 11.4 ms**.

## 7.1 The fixture, re-exported — RED then GREEN

RED first: `pytest tests/test_calculator_document.py` → 2 failed, on
`15000` bytes and on `apiVersion 18`.

Re-exported from a THROWAWAY COPY of the producer (copied to the
scratchpad, never written in the read-only worktree):

```
PYTHONPATH="$PWD" solid export \
    tests/clocked_project/calculator.py:Calculator -o <dir> --no-widget
```

`tests/fixtures/calculator/viewer.json` is that `manifest.json` verbatim:
**15 159 bytes**, md5 `d1d1aad665d22a734767ca7a7bdb5872` (was 15 000 /
`0884b61fe1ee8c8a79b0d4b78b28767a`). Diffed against the previous export,
the two differ in the `instructions` key and in the `mtime` fields ALONE,
and **both meshes are byte for byte identical**, so they were not
re-copied. `clocked.identity` is unchanged
(`979b1a0e…`): an instruction table is not part of what
`Clocked.described` hashes. The README records all of it.

## 7.2 The drawing, in a real browser — GREEN

`tests/test_calculator_document.py::InstructionDrawnInABrowserTest`, one
Chromium page, everything sampled PER ANIMATION FRAME. What it proves:

- the button is pressable (`disabled` false, no `aria-disabled`) and
  carries `aria-busy` from the instant of the press;
- the FIRST frame reads the transition's ORIGIN — `crank` 0, not 360 —
  although the machine already stands at 360: the press's own task posed
  frame 0 before the browser painted;
- the crank's panel reading rises monotonically over **120 frames** and
  ends at 360, with **more than five distinct readings**;
- **ONE SOLVE**: `machine.state()` is the SAME bank at every one of those
  120 samples, with `crank: 360` and `w0.digit: 1` from the first;
- the landing equals one `move('crank', {by: 360})` from the same start,
  bank for bank (`admitted` 360, `origin` 0, `end` 360, one commit), the
  panel equals the bank, and the button reports `moved 360 deg`;
- **two presses are two strokes**: crank 720, `w0.digit` 2;
- a GESTURE on another handle lands the drawing (crank jumps from a
  mid-stroke reading to 360, `aria-busy` gone) and then acts; so does a
  `restore` (crank 0 afterwards);
- the COMMIT is drawn at the frame the fraction reaches it: focused on
  `w0`, the digit reads `0` at every frame of the stroke and `1` at the
  frame that reaches it — `'Stroke'`'s commit is at fraction **1.0**, the
  corpus's own number for this machine;
- the POSED `viewer.trigger('Stroke')` is refused, naming `DRIVER TABLE`
  and pointing at `machine().trigger('Stroke')`;
- an unknown name is refused listing `Set four` and `Stroke`.

Screenshots (pixels are evidence), both of a clean single mount:
`tests/_shots/clocked-instruction-mid-stroke.png` — crank **171 deg**,
operand 4, the `Stroke` button highlighted and `aria-busy`, the outcome
reading `moved 360 deg`; and `tests/_shots/clocked-instruction-landed.png`
— crank **360**, the button no longer busy.

## 7.4 `pytest tests -q` — GREEN

**176 passed, 18 subtests passed, 183 s, no skips** (this host has the
Curta's builds, so `test_curta_drawing.py` ran rather than skipping).

Five existing browser acceptances and `test_widget_e2e.py` carried the
API version and were moved with it: `apiVersion 18 → 19` in
`test_carriage_document.py`, `test_clearing_document.py`,
`test_lock_document.py`, `test_regulator_document.py`,
`test_running_document.py`, and `bundle 18 → 19` in
`test_widget_e2e.py`. Each was seen red first (`AssertionError: 19 != 18`).

## 8.1 The Curta's own stroke, measured

`tests/test_curta_drawing.py`, SKIPPED where the builds are absent,
serving a temporary directory of SYMLINKS to
`_build/clocked_curta` and `_build/fast_curta` — nothing copied into this
repository. `'Turn crank'` played on each, in one browser session, with
the viewer's own animation-loop callback timed from the outside and an
IDLE phase on the same page first, so what a frame of a DRAWING costs can
be told from what a frame of that page costs.

```
the CLOCKED Curta's 'Turn crank' (2 s):
  mounted in 0.72 s; one solve 47.60 ms
  IDLE (no drawing): 20 frames over 6.61 s (3.0 fps), median 3.30 ms
  DRAWING: 5 frames over 2.52 s (2.0 fps), median 12.50 ms,
           worst 13.70 ms, 5 distinct poses drawn
  the POSE, by difference: +9.20 ms a frame

fast_curta's 'Turn crank' (6 s, posed Ramp):
  mounted in 0.63 s; one solve 0.00 ms
  IDLE (no drawing): 20 frames over 6.74 s (3.0 fps), median 3.60 ms
  DRAWING: 18 frames over 6.76 s (2.7 fps), median 13.10 ms,
           worst 21.10 ms, 19 distinct poses drawn
  the POSE, by difference: +9.50 ms a frame
```

**Read it as it is.** The per-frame POSE of the Curta's clocked build —
41 bank values over a 39-commit machine — costs **9.20 ms**, and the
posed `fast_curta`'s ramp over 8 drivers costs **9.50 ms** on the same
page in the same session. The clocked pose is NOT more expensive than the
posed one, and it is inside a 60 Hz frame budget.

What is NOT inside a frame budget on this host is the PAGE: it runs at
**3.0 fps while idle**, before anything is drawn, with headless Chromium
on `swiftshader` software rendering and 54 MB of meshes. The drawing does
not move that (2.0 fps against 2.7 fps for the posed build, over 5 and 18
frames — too few samples to separate). **The frame rate here measures the
software rasteriser, not this cycle**, and is recorded rather than
explained away: the number on a machine with a GPU is not known from
here. Screenshots of both landings are under the scratchpad
`viewer-acceptance/` (`curta-clocked-landed.png` shows the Curta posed
with `crank_rotation` reading 360), and the canvas was not blank.

For a document the page CAN render at 60 Hz, the committed acceptance's
own number is the honest comparison:

```
calculator drawing: 120 frames over 2.02 s (59.4 fps),
  per-frame pose median 0.40 ms, worst 1.30 ms
```

## 8.2 A pressed instruction against the same request, in thread

`src/clocked/cost.test.ts`, both paths warmed and then timed ALTERNATELY
(at a tenth of a millisecond, whichever ran first would otherwise pay the
JIT's bill), median of 40 each, three separate runs:

```
move('crank', {by: 360})  0.1340 / 0.1349 / 0.1274 ms
trigger('Stroke')         0.1457 / 0.1248 / 0.1140 ms
the difference            +8.7% / -7.5% / -10.6%
```

The sign changes between runs: the two are the same request within this
bench's own noise, which is what "an instruction is a request and two
dictionary lookups" predicts. The producer measured its own at +0.22%.

## 8.3 The bundle and the suite

| | before | after |
| --- | ---: | ---: |
| `dist/solid-widget.js` | 800 054 B (main `757ad84`, API 18) | **804 744 B** (API 19) |
| widget suite | 45 files, 1168 tests, 31.9 s | **46 files, 1218 tests, 30.2 s** |
| Python suite | — | **176 passed, 183 s** |

## What is UNCHANGED, shown rather than claimed

`git diff --stat` over `src/run/`, `src/drivers.ts`, `src/tree.ts`,
`src/controls.ts` and `src/runControls.ts` is **EMPTY**: the worker, the
program, the posed `Ramp`, `toNative` and the running chrome are byte for
byte what they were. `src/running-corpus.json` is untouched (md5
`651a3b5750c49eecad4587438dc9a85a`), and `npx vitest run src/run` plus
the running corpus is **14 files, 366 tests, all green**. No fixture but
`tests/fixtures/calculator/` moved. `solidNodeDocumentVersions` is still
`[1..8]` and `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` still `[1,2,3,4]`.

## The corpus census, moved

| | before | after |
| --- | ---: | ---: |
| bytes | 139 262 | **145 673** |
| md5 | `852b86b8…` | **`bc4174cf…`** |
| machines | 30 | 30 |
| steps | 76 | **81** |
| recorded numbers | 722 | **917** |
| machines with bounds / their steps | 13 / 36 | 13 / **41** |
| `tolerance.float` | 0.0 | 0.0 |

Every number is DERIVED from the file by the suite itself, and the
closing census is read off the replay, so all 81 steps of all 30 machines
were compared — the two `trigger` steps included, and `origin`/`end` on
every one of the 65 recorded requests.

## Contradictions and findings, reported rather than resolved silently

1. **The design's "the drawing takes the request, the bank and the
   duration" needed a fourth argument that the design already names
   (`integer`)** — `drawing(request, start, duration, integer)`, as
   design §3's own signature has it. No departure; noted because the
   prose above the signature lists three.
2. **`advance(elapsedSeconds)` takes TOTAL elapsed, not a delta.** The
   design gives the signature and not the convention. Total is `Ramp`'s
   own (`valueAt(now)`) and makes a frame a sample of a function of time
   rather than an accumulation; `viewer.ts` keeps the running total.
3. **The first frame's `moved` is measured against the request's END
   bank, not against the start bank.** The request posed the end as part
   of itself (ADR-125), so that is where the TREE stands when a drawing
   begins; a diff against the start bank would leave frame 0 posing
   nothing and the model showing the end. The design does not say which;
   this is the only one that draws.
4. **A rebuild of the panel during a drawing follows the DRAWING.**
   `rebuildClockedChrome` reads `drawnBank ?? machine.state()`. The
   design only specified the narrow writer, but a focus change or a
   republish mid-drawing would otherwise jump the panel to the end bank,
   which the requirement forbids in the same sentence.
5. **The committed acceptance cannot show a MID-PATH commit.**
   `'Stroke'` is `by crank 360` from rest and the calculator's stroke
   relation fires at 360 — the corpus records `fraction: 1.0` — so the
   digit changes at the last frame and nowhere else. The fraction rule
   at 0.25 and 0.75, rising and falling, is pinned in
   `src/clocked/drawing.test.ts` instead. Stated rather than dressed up.
6. **`dispose()` does not remove the clocked panel.** Pre-existing
   (ADR-062): `dispose` removes `driverChrome` and `runChrome` and never
   `clockedChrome`, so two mounts on one host stack two panels. It bit
   the screenshots, which now clear the host first. NOT fixed here — it
   is not this cycle's surface — and reported for the pilot.
7. **The Curta's page runs at 3 fps IDLE on this host** (§8.1). The
   finding is the rasteriser's, not the pose's, and the per-frame pose
   number is recorded beside it rather than widened away.
