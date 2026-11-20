# Evidence: draw a press from its first frame

Applied on the bench `machinome/WTs/draw-a-press-from-its-first-frame`,
branch `draw-a-press-from-its-first-frame`, HEAD `6428a08c` (the planning
commit, one above the base `fd3345970acba6a7da3a80421626494a59ace6c1`),
20 November 2026. The tree was clean and `openspec validate
draw-a-press-from-its-first-frame --strict` reported the change valid
before anything was written (task 1.2). Every run below was made alone,
one at a time; vitest 3.2.7, Python 3.12.3, pytest 9.1.1, headless
Chromium through Playwright with SwiftShader.

## Red on the base

### 2.1 `clocked/drawing.test.ts` (source unmodified)

`vitest run src/clocked/drawing.test.ts`: 5 failed, 16 passed (21). Every
existing test passed; the five new ones failed for the reason the design
names:

```
× a drawing BEGINS where the scene stands > a drawing begins where the scene stands
  → expected [ 'x', 'n', 'm' ] to deeply equal []
× a drawing BEGINS where the scene stands > landing a drawing that drew no frame moves the whole transition
  → expected [] to deeply equal [ 'm', 'n', 'x' ]
× the drawing's CLOCK starts at its first drawn frame > reads 0 at its first frame, whatever wall time that frame carries
  → (0 , drawingClock) is not a function
× the drawing's CLOCK starts at its first drawn frame > sums the wall seconds of every later frame
  → (0 , drawingClock) is not a function
× the drawing's CLOCK starts at its first drawn frame > adds a long later frame whole, so a drawing advanced by it lands as before
  → (0 , drawingClock) is not a function
```

D1 and D2 fail on the `moved` lists; C1 to C3 fail at the call, and the
file's other tests ran.

### 2.2 `flexible.test.ts` and `color.test.ts` (source unmodified)

`vitest run src/flexible.test.ts`: 5 failed, 27 passed (32); every existing
test passed.

```
× judging a pose shows nothing > judges a moving candidate without showing it                (T1)
  → tree.admit is not a function
× judging a pose shows nothing > asks molejo nothing for a reached part whose values stand    (T2)
  → tree.admit is not a function
× judging a pose shows nothing > refuses with molejo's own message and leaves every part standing (T3)
  → expected [Function] to throw error matching /must be a finite number/ but got 'tree.admit is not a function'
× judging a pose shows nothing > refuses a transform before asking molejo anything            (T4)
  → expected [Function] to throw error matching /later.*operation 0/ but got 'tree.admit is not a function'
× judging a pose shows nothing > propagates a throwing parameter expression as `update` would, and writes nothing (T5)
  → expected 'tree.admit is not a function' to be 'Cannot use \'in\' operator to search …' // Object.is equality
```

`vitest run src/color.test.ts`: 1 failed, 21 passed (22); every existing
test passed.

```
× version-14 model colors > judges a chosen color without showing it, and refuses an invalid one as an update would (T6)
  → lit.admit is not a function
```

Each new test fails because `admit` does not exist.

### 2.3 Browser class `PressDrawnFromItsFirstFrameInABrowserTest` (bundle of the base source)

Bundle built with `npm run build` from the base source (only test files
modified at that point; `git diff` of `src/` outside `*.test.ts` empty),
SHA256 `4b2e8fdc2bb10a55c512d142da4c6b9363b7de882eba6202cf9a2c5c51ab7693`.
`pytest tests/test_calculator_document.py -k
PressDrawnFromItsFirstFrameInABrowserTest -rs -s`: 4 failed, 4 passed, no
skip. Printed:

```
draws in the task: host move 6, Stroke 12, Set four 12, nudge 12
crank at the first frame: Stroke 3.006, nudge 3.006, slow Stroke 56.988; operand at Set four's first frame 1
drawn frames: Stroke 120, Set four 30, nudge 120, slow Stroke 102
```

| Test | Design | Base |
| --- | --- | --- |
| `test_a_drawn_press_draws_nothing_in_its_own_task` | B1 | FAILED `12 != 0 : 'Stroke' drew` |
| `test_a_publishing_door_draws_in_its_own_task` | B1 guard | passed (6 draws) |
| `test_the_first_frame_after_a_press_reads_the_origin` | B2 | FAILED `3.006 != 0` (Stroke's first frame) |
| `test_a_slow_press_still_begins_at_the_origin` | B3 | FAILED `56.988 != 0` |
| `test_the_part_stands_where_it_stood_in_the_press_task` | B4, in the task | passed |
| `test_the_part_stands_where_it_stood_at_the_first_frame` | B4, first frame | FAILED: the rect moved, `x` 145.575 to 132.569 |
| `test_the_watched_part_moves_with_the_crank` | B4's precondition | passed |
| `test_the_page_logged_no_errors` | | passed |

B1 fails on a draw count above 0 inside the press (12: two renders of 6),
B2 and B3 on a first-frame reading above 0, B4 on the first-frame screen
rectangle; the guard and B4's in-task half pass.

## The part chosen for B4

`['crank_dial']`, the dial the `crank` driver turns (`r crank [0, 0, 1]`).
The class checks it on the page before using it: its `partOnScreen` is the
same on two idle frames, differs between `crank` 0 and 180 (set with the
host's `move`), and returns to the first reading after a reset. The
comparison is of the whole `partOnScreen` answer (rectangle and search
point), serialized, compared exactly.

## 4.2 The wiring vitest cannot reach

Each sabotage was applied to the implementation's `viewer.ts`, followed by
`npm run build` and a run of the class, then restored from a copy of the
implementation; `diff` against the copy was empty after each restoration
and `git diff` showed no sabotage line.

(a) The drawing's clock bypassed (`drawingFrame` adding every wall delta,
the first included, to a running total): 3 failed, 5 passed.

```
draws in the task: host move 6, Stroke 0, Set four 0, nudge 0
crank at the first frame: Stroke 3.006, nudge 3.006, slow Stroke 54; operand at Set four's first frame 1
FAILED test_a_slow_press_still_begins_at_the_origin            54 != 0
FAILED test_the_first_frame_after_a_press_reads_the_origin     3.006 != 0
FAILED test_the_part_stands_where_it_stood_at_the_first_frame  (rect x 132.569 against 145.575)
```

B2 and B3 red, B1 green, as the task requires; B4's first-frame half is red
too, for the same reason (the first frame moves the dial).

(b) The hook's `judging` branch removed (the hook updates and renders as on
the base): 3 failed, 5 passed.

```
draws in the task: host move 6, Stroke 6, Set four 6, nudge 6
crank at the first frame: Stroke 0, nudge 0, slow Stroke 0; operand at Set four's first frame 1
FAILED test_a_drawn_press_draws_nothing_in_its_own_task        6 != 0 : 'Stroke' drew
FAILED test_the_part_stands_where_it_stood_at_the_first_frame  (point null against a found point; rect x differs in the 14th digit)
FAILED test_the_part_stands_where_it_stood_in_the_press_task   (the same)
```

B1 red, and B4's first-frame half red as expected: the drawing assumes the
scene never left the start, so with the end posed and frame 0 moving
nothing the scene stays at the transition's end. B4's in-task half is red
as well, for the same reason (the end pose is now what stands in the
press's task; on the base frame 0 re-posed the origin in that task). B2
and B3 stay green: the panel reads `drawnBank`, the origin.

## Draw counts and first-frame readings

| | Base (`4b2e8fdc…`) | Implementation (`e26c15c1…`) |
| --- | --- | --- |
| Draw calls in the click's task: `'Stroke'` | 12 | 0 |
| `'Set four'` | 12 | 0 |
| whole-turn nudge of `crank` | 12 | 0 |
| guard, host `move('feed', {by: 1})` | 6 | 6 |
| `crank` at the first frame after `'Stroke'` | 3.006 | 0 |
| after the nudge | 3.006 | 0 |
| after a press plus 300 ms in its task | 56.988 | 0 |
| `operand` at the first frame after `'Set four'` | 1 | 1 |
| frames until landing: Stroke, Set four, nudge, slow Stroke | 120, 30, 120, 102 | 120, 30, 121, 121 |

## 4.3 Green on the implementation

Bundle built from the implementation, SHA256
`e26c15c1a0f687ca6cefc411edd86befd465b9fc5507832b6075d784acb56a04` (the
same bytes at every rebuild of the implementation, the final one
included).

- `PressDrawnFromItsFirstFrameInABrowserTest`: 8 passed.
- `InstructionDrawnInABrowserTest`: 1 passed. `calculator drawing: 119
  frames over 2.02 s (59.0 fps), per-frame pose median 0.50 ms, worst
  10.20 ms`.
- `GestureDrawnInABrowserTest`: 1 passed. Printed:

```
calculator gesture: 121 frames over 2.01 s (60.1 fps), per-frame pose median 0.40 ms, worst 1.10 ms
the first press after setting the amount moved to 360 (moved 360 deg)
the element focused when a value was committed became '', the field then reading '0'
tempo declared: 122 frames over 2.03 s, 0 -> 360 (122 distinct poses)
tempo twelfth: 11 frames over 0.18 s, 0 -> 30 (11 distinct poses)
tempo twice: 242 frames over 4.03 s, 0 -> 720 (242 distinct poses)
tempo targetsOnly: 13 frames over 0.22 s, 1 -> 9 (9 distinct poses)
tempo unnamed: 13 frames over 0.22 s, 0 -> 25 (13 distinct poses)
tempo press: 122 frames over 2.03 s, 0 -> 360 (122 distinct poses)
a twelfth of the travel took 0.090 of the time
twice the travel took 1.984 of the time
clipped: 1103 -> 1098 in 3 frames over 0.045 s, reported 'moved -5 deg, held by crank_dial.turn (low 1098)'
the clipped gesture took 0.045 s, the declared rate on its admitted travel being 0.028 s
the pressed instruction took 1.000 of the gesture of the same travel
frozen mid-nudge at crank 48.006, three quarters in at 272.98404, landed at 360
```

  Test 10e: `|0.045 - 0.028| = 0.017 s` against the allowed `4/60 =
  0.0667 s`, a margin of about 0.050 s (three frames at 60 fps). It held
  as written. 10a 2.03 s in (1.5, 3.5); 10b 0.090 in (1/24, 1/6); 10c
  1.984 in (1.5, 2.5); 10d 0.22 s below 2.03 / 4 and above 0.05; 10f
  1.000 in (0.7, 1.4); `FREEZE` at 30 frames 48.006 and at 90 frames
  272.98 (both inside (0, 360) and rising).
- `tests/test_clocked_pose_admission.py`: 3 passed.

## 5. Gate

- Widget suite, `vitest run` once: 68 files, 67 passed and 1 skipped;
  1778 tests, 1776 passed, 2 skipped, 0 failed. The two skips are
  environmental and pre-existing: `run/profile-installed-benchmark.test.ts`
  ("reports one pinned installed Curta v13 integration attempt",
  `it.skipIf(!process.env.CURTA_INSTALLED_PROFILE_DOCUMENT)`) and
  `run/profile-contact.test.ts` ("loads the pinned actual-cover v13 Bound
  and replays its numeric stop",
  `it.skipIf(!process.env.CURTA_PROFILE_V13_DOCUMENT)`); neither variable
  is set on this bench.
- Typecheck, `tsc --noEmit`: exit 0, no output.
- Bundle, `npm run build`: `dist/machinome-viewer.js`, SHA256
  `e26c15c1a0f687ca6cefc411edd86befd465b9fc5507832b6075d784acb56a04`.
- Viewer Python suite, `pytest tests` once on the bench's venv after that
  build: 284 passed, 2 skipped, 215 subtests passed, 71 warnings, 0
  failed, in 290 s. The two skips are environmental and pre-existing,
  `tests/test_curta_drawing.py:375` and `:469`, both "the Curta's own
  builds are not at
  .../WTs/projects/Calculators/Curta-Type-I-3x/_build" (design Decision 9
  expected this class skipped on this bench). No browser test was skipped
  for a missing Chromium or Playwright.

## Decisions the design left open

- **T5's assertion of "the same message".** On the base a missing `admit`
  is itself a `TypeError`, so asserting only the error's class (as the
  previous change's test D does for `update`) would pass on the base. T5
  instead publishes the same candidate on an identically mounted twin with
  `update` and asserts that `admit` throws a `TypeError` with exactly that
  message; that is the design's claim ("every throw propagates
  unchanged, so the refusal's message is the one `update` would give").
- **T1 to T4's fixtures.** T1 and T3 use Decision 1's measurement fixture:
  a rigid `AssemblyNode` translated by `(2 * valvetrain.lift)` beside a
  spring whose height is `sqrt((10 - valvetrain.lift))`, mounted at lift 0.
  T4 adds the same rigid node before the existing `sqrt(1 -
  valvetrain.lift)` sibling, so "nothing changes" is checked on a matrix
  as well as on the spring.
- **T6** is one test in two halves: a `{when: powered}` colour judged at
  `powered` 1 from 0 (colour, material identity and the assembly's
  reported colour stand), then the existing atomic-colour fixture with
  `sqrt(2 - powered)` on the later leaf, judged at `powered` 3.
- **The browser class runs the page once** (`setUpClass`) and reads each
  claim in its own test method, so B1, B2, B3, B4's two halves, the guard
  and the precondition each fail or hold on their own; the existing
  classes of the file use `setUp` and one method. The harness page, the
  fixture copy, the server and the Chromium launch arguments are theirs.
- **`publishJudged`.** The publication of Decision 1 is one helper used by
  both doors: it updates the tree over the ids whose value differs
  between the bank before the request and the bank after it, and does
  nothing when none does. `clockedPlay` calls it only for a judged request
  (duration above zero) that started no drawing; `clockedRequest` for any
  drawn request (`draw` true) that started no drawing. In `clockedPlay`
  the case is unreachable on present inputs (a duration above zero that
  starts no drawing has equal ends and no commits, so nothing moved); the
  call is kept so the two doors state one rule.
- **`startDrawing` sets `clockPlaying = false` unconditionally** where the
  base set it and rebuilt only when the clock was playing; the door's one
  rebuild then shows it stopped. Setting false when already false changes
  nothing.
- **Where the publication sits.** After `startDrawing` and before the one
  panel rebuild, in both doors; the panel reads `machine.state()` either
  way, so the order is not observable in it.
- **Sabotage (a)** bypassed the clock by keeping a running total of every
  wall delta on the drawing record (`(running as any).total`), which is
  the base's accumulation.

No deviation from the design's decisions, its spec delta or any existing
test's meaning. The one existing expectation changed is the one Decision 9
names: the first expectation of "reports as MOVED exactly the ids the frame
changed" in `drawing.test.ts`, from `advance(0).moved.sort()` equal to
`['m', 'n', 'x']` to `advance(0).moved` equal to `[]`, with its comment.

## Out of scope, found while proposing

From the design's last section, in its own words, not addressed here:

- A frame of a playing clock renders three times: the hook renders inside
  `clockFrame`'s request, `clockedRequest` renders after its rebuild, and
  the loop renders. The panel's step renders three times likewise, and the
  panel's reset follows the hook's update with an update of the whole tree
  (`'all'`). None of these is a drawn press.

## Reviewer's record: review of the implementation and task 6.2

Written by the repository agent, 20 November 2026, after the applier stopped
with its work uncommitted.

### Review of the implementation

The two doors in `viewer.ts` were read in full against design Decisions 1 to
5: the `judging` flag is set immediately before the one request call and
cleared in a `finally` around that call alone, so it is false on every exit;
a drawn press makes no `tree.update` and no render; the panel is rebuilt once
after `drawnBank` holds the origin. `FlexibleShape.admit` and
`WidgetTree.admit` write nothing. The existing tests' diffs are additions
only, except the one expectation Decision 9 names in `drawing.test.ts`. Run
again by the reviewer, one file at a time: `clocked/drawing.test.ts` 21 of
21, `flexible.test.ts` 32 of 32, `color.test.ts` 22 of 22, `tree.test.ts` 69
of 69; `tsc --noEmit` exit 0. A rebuild of the bundle from the final source
gave the SHA256 the applier reports (`e26c15c1…acb56a04`).

### 6.2 The Enigma I page

Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
`a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`. Same host
and method as `workflow/evidence/enigma-press-path-2026-11-20.md` (headless
Chromium, no GPU, draw calls counted and not executed, so script only; a
probe build of the bench's source with `WidgetTree.prototype.update`,
`WidgetTree.prototype.admit`, `FlexibleShape.prototype.evaluate` and
`FlexibleShape.prototype.admit` wrapped to count and time; each instruction
pressed by `element.click()`; the per-frame change tracker), and the built
bundle of 5.2 for the press tasks. Single runs. No page error in either, and
the expression store stood at generation 0 with one binding preparation
throughout.

Inside the click, before (viewer `fd334597`, from the evidence file) and
after:

| Instruction (declared seconds) | Press task, ms | Tree updates | Judgements | Draw calls | Press task with the built bundle, ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Key B (0), a different key | 155 → 165 | 1 → 1 | 0 | 6,694 → 6,694 | 130 |
| Press (2) | 381 → 192 | 2 → 0 | 1 (186 ms) | 6,694 → 0 | 164 |
| Release (2) | 376 → 168 | 2 → 0 | 1 (164 ms) | 6,694 → 0 | 164 |
| Right wheel on (0.4) | 249 → 109 | 2 → 0 | 1 (105 ms) | 6,694 → 0 | 122 |
| Right wheel back (0.4) | 261 → 107 | 2 → 0 | 1 (104 ms) | 6,694 → 0 | 114 |
| Open flap (1.5) | 48 → 7 | 2 → 0 | 1 (2 ms) | 6,694 → 0 | 9 |
| Close flap (1.5) | 52 → 5 | 2 → 0 | 1 (2 ms) | 6,694 → 0 | 8 |

Of a Press's judgement, 122 ms is in the 86 flexible judgements; of a wheel
step's, 42 to 52 ms.

The frames after it:

| Instruction (declared seconds) | Frames that changed the picture | The first of them began, ms after the click | Script per such frame, ms |
| --- | ---: | ---: | ---: |
| Press (2) | 9 → 10 | 382 → 226 | 193 → 211 |
| Release (2) | 9 → 11 | 378 → 200 | 195 → 183 |
| Right wheel on (0.4) | 2 → 1 | 250 → 424 | 79 → 51 |
| Right wheel back (0.4) | 2 → 1 | 262 → 380 | 83 → 43 |
| Open flap (1.5) | 44 → 46 | 49 → 31 | 30 → 29 |
| Close flap (1.5) | 45 → 45 | 53 → 31 | 29 → 30 |

In the same run's pass over the nine instructions of the originating
evidence: Press 10 and Release 11 changing frames with press tasks of 176 and
173 ms; the flap 42 and 46, the hood 120 and 109 changing frames with press
tasks of 6 to 7 ms.

### The expectations of task 6.2

Met: a drawn instruction's click makes no outermost `update`, one `admit` and
no draw call, and `Key B` keeps its one `update`; the press tasks fall inside
the predicted ranges (a wheel step 107 to 122 ms against 100 to 150, a Press
164 to 192 ms against 160 to 230); the first frame after a click changes
nothing and the first changing frame follows it.

**Not met: a 0.4 s wheel step still changes the picture once, at its end.**
The design predicted four to six changing frames and held "more than 2" to
be firm. The prediction rested on the step having a picture between its
start and its end, and it has none: the Enigma declares
`operation.right_wheel` a whole number (`dtype: 'int'`, range -26 to 26),
"Right wheel on" moves it by 1, and `drawing.ts` draws a whole-number input
truncated (`origin + Math.trunc(delta)`), as ADR-064 decided. The drawn value
therefore stands at the origin until the transition's end and jumps there.
On the base the two changing frames were the same jump seen through a clock
that had already spent 0.25 s. No change to the press path can show a wheel
between two positions; that takes either a model whose wheel input is not a
whole number or a different rule for drawing one, and neither is this
change's. The reviewer told the pilot before the change that it would make
the wheel steps move; that was wrong, and for a reason one look at the
document's driver table would have shown.

**Acceptance.** The change does what its design decided, on every count the
measurement can see, and no page error occurred. Accepted, with the wheel
step recorded as not improved in what is seen and improved only in the
click's cost.

**Not measured.** Any GPU's frame time; a browser other than Chromium; the
left and middle wheels; a refused drawn request on this page; a press made
while a drawing runs; a hidden tab.

### Final gate

Run by the reviewer on the finished state, after the archive and with it
staged, one at a time.

- Whole widget suite: 68 files, 67 passed and 1 skipped; 1,778 tests, 1,776
  passed, 2 skipped (the two environment-gated Curta files), 0 failed;
  52.8 s.
- `tsc --noEmit`: exit 0. The bundle's SHA256 is unchanged
  (`e26c15c1…acb56a04`).
- Python suite: 284 passed, 2 skipped, 0 failed, 215 subtests, 290 s. Both
  skips are `tests/test_curta_drawing.py` (lines 375 and 469): the Curta's
  own builds are not on this bench.
- `openspec validate --specs --strict`: 16 passed, 0 failed.
