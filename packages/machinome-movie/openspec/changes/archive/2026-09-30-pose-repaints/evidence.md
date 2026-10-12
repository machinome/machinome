# Implementation evidence

## Authority and scope

A cycle of Videomaker's fix-warts campaign, on branch `pose-repaints`
(worktree `WTs/pose-repaints`), cut from `fix-warts` at `e30b05f`, for wart 4
of "The React stage" and wart 5 of "Cut and Advance, version 2"
(`workflow/warts.md`, 30 September 2026). Nothing was pushed or published;
no network or paid request was made; nothing was installed (`npm ci` had
been run in the worktree). Integration into `fix-warts` is the
orchestrator's.

Environment of every run: Linux, 16 cores, Node v24.11.1, vitest 5.0.3,
Playwright's Chromium, `ffmpeg version 6.1.1-3ubuntu5`. The machine is
shared with other agents' suites; each measurement below records the load
average when it started, and durations are comparable only within this
record.

## Measured before any change (task 0.2)

Method. A scratch harness outside the repository (not committed) copies and
commits the fixture project, loads the fixture movie `tour`, and runs one
`browserSession` at the tour's output size (1280×720, 30 fps) with the
viewer double. It poses every output frame exactly as `render`'s capture
loop does, `pose(frame.time)` then `page.screenshot()`, over the 567 frames
`outputShotUnits` lists, timing each call with Node's `performance.now()`.
Temporary lines in `stage/runtime.tsx`, removed before every commit,
accumulated `performance.now()` in the page around `setFrame`'s phases and
around every `repaint()`. The harness also ran the command line's `check`
and `render` of the same tour at its output size, timed end to end (bundle
reuse, capture, shot cache, encode, review pack).

Before (the unchanged runtime; three runs of the loop, load 3 to 4):

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| capture loop, 567 frames | 115.74 s, 4.90 frames/s | 116.05 s, 4.89 frames/s | 118.01 s, 4.80 frames/s |
| Node: `pose()` | 84.14 s (148.4 ms/frame) | 85.30 s (150.4 ms/frame) | 85.47 s (150.7 ms/frame) |
| Node: `page.screenshot()` | 31.60 s (55.7 ms/frame) | 30.75 s (54.2 ms/frame) | 32.54 s (57.4 ms/frame) |
| `setFrame` calls / repaints in them | 778 / 778 | 778 / 778 | 778 / 778 |
| commit (`flushSync`, slot check) | 0.25 s (0.32 ms/pose) | 0.25 s (0.32 ms/pose) | 0.26 s (0.34 ms/pose) |
| `poseViews` (views, canvas wait, marks) | 2.07 s (2.67 ms/pose) | 2.36 s (3.03 ms/pose) | 2.13 s (2.74 ms/pose) |
| `decodePictures` | 0.03 s | 0.02 s | 0.03 s |
| `repaint` in `setFrame` | 42.21 s (54.25 ms/pose) | 43.49 s (55.90 ms/pose) | 42.86 s (55.09 ms/pose) |
| `measure` | 0.10 s | 0.10 s | 0.11 s |
| repaints in compositions | | | 194, 10.79 s |
| command line `render`, end to end | | 127.60 s | |

The 778 poses for 567 frames are the same-instant captures a transition or
a faded mark is composed from (`capture()` and `showPicture()`'s variants).
`pose()` outside `setFrame` (about 39 to 40 s) is the compositions (their
194 repaints, 10.8 s), the in-pose screenshots of those captures, the
`page.evaluate` round trips and the Node checks.

A probe of the rule, in the unchanged page (it computed the decision before
repainting and repainted anyway; fourth run, load 2.1): **207 of 778 poses**
were not fresh, had no view mounted, placed again or resized, and had the
same serialized document as at the page's last repaint. Serializing the
document cost 0.04 ms a pose; it was 992 characters at the tour's last
frame. That run's loop: 118.65 s, 4.78 frames/s, repaints in `setFrame`
44.63 s (57.37 ms/pose).

## Red

Test first, in `test/browser/stage.test.mjs`, "a pose waits for what can
change the picture: nothing when only a view changes, a repaint when a
title's words change", run cold on the unchanged runtime
(`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow
test/browser/stage.test.mjs -t "a pose waits"`):

    × a pose waits for what can change the picture: nothing when only a view changes, a repaint when a title's words change 1606ms
    AssertionError: the same frame posed again requests no animation frame

    4 !== 0

    - Expected
    + Received

    - 0
    + 4

     ❯ test/browser/stage.test.mjs:134:10
          Tests  1 failed | 10 skipped (11)
    Test memo: 0 passed from the memo, 1 run

Four animation frames: the repaint's two pairs. After the change the same
command: `✓ a pose waits for ... 1519ms`, `Tests 1 passed | 10 skipped
(11)`, `Test memo: 0 passed from the memo, 1 run`. `npx tsc --noEmit -p
stage/tsconfig.json` printed nothing.

## Mutations (task 1.3), each reverted at once

- **A stage that never repaints a pose** (`setFrame`'s condition made
  false; compositions still repaint). The new test fails at `a title whose
  words changed repaints the page`, its frame count. Its pixel half does
  **not** fail: posing A, B, A gave identical pixels for A and B differed
  (printed `true false true` for A2 equals A, B equals A, the repeated
  frame equals the first). The browser project then: every test passes but
  the new one and `the tour previews`, which refuses with `Picture replay
  is not deterministic: still cues[0].actions[0] at 16.92 s; inspect
  preview/picture-still-cues0actions0-replay-{before,after}.png`.
- **A stage that repaints only fresh and resized poses** (no content
  comparison). The browser project and `test/pipeline/incremental-rendering.test.mjs`,
  cold: `Test Files 1 failed | 4 passed (5)`, `Tests 1 failed | 58 passed
  (59)`; the one failure is the new test's frame count, `a title whose words
  changed repaints the page`. No pixel proof of the fixture, incremental
  rendering's exact bytes included, tells this weaker rule from the chosen
  one (finding 1).

## Five cold runs of the browser and pipeline projects (task 2.1)

`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow` from the worktree,
five times in a row on the final content (the stage and renderer as
committed; only records changed afterwards, and no slow key reads them):

| run | started (load, 1 min) | Test Files | Tests | Duration | Test memo |
|---|---|---|---|---|---|
| 1 | 18:54:38 (3.71) | `10 passed (10)` | `110 passed (110)` | `585.07s (tests 100%)` | `0 passed from the memo, 110 run` |
| 2 | 19:04:24 (4.08) | `10 passed (10)` | `110 passed (110)` | `585.00s (tests 100%)` | `0 passed from the memo, 110 run` |
| 3 | 19:14:10 (0.79) | `10 passed (10)` | `110 passed (110)` | `576.25s (tests 100%)` | `0 passed from the memo, 110 run` |
| 4 | 19:23:47 (0.61) | `10 passed (10)` | `110 passed (110)` | `575.26s (tests 100%)` | `0 passed from the memo, 110 run` |
| 5 | 19:33:23 (1.96) | `10 passed (10)` | `110 passed (110)` | `575.98s (tests 100%)` | `0 passed from the memo, 110 run` |

Five of five green, none from the memo: every A-B-A proof of layer 5, every
preview replay (`Pixel replay`, `Picture replay`, `Partial picture replay`,
`Transition replay`, the entrance and emphasis replays), and
`incremental-rendering`'s "every incremental PNG equals a separately cold
film" held on every run. (The cold time is the slow layer's; this change
saves little of it because the tests' poses are mostly proof poses and
compositions, which repaint as before.)

## The whole suites on the final content (task 2.2)

After the archive (only `evidence.md` changed since, which no key reads):

- **Node**, `npm test` (19:43, load 0.97):

      Test Files  28 passed (28)
           Tests  292 passed (292)
        Duration  571.21s (tests 98%, import 1%, transform 1%)
      Test memo: 26 passed from the memo, 266 run

  The 26 memoized passes are `test/pipeline/pictures.test.mjs` (16),
  `source-scenes.test.mjs` (5) and `speech.test.mjs` (5), whose keys reach
  neither the stage nor the renderer; each also ran cold, and passed, in the
  five runs above.
- **Python**, `python -m pytest -q` in `python/`: `186 passed in 12.82s`.
- `openspec validate --specs --strict`: `Totals: 16 passed, 0 failed (16
  items)`.

`openspec archive pose-repaints --yes` added the requirement to
`react-stage` and replaced the requirement in `test-suite` (`+ 1 added`,
`~ 1 modified`); it also removed the blank line before `## Requirements` of
`react-stage` and joined two lines of the new requirement, which were put
back by hand. It archived with 12 of 14 tasks: 0.3 (the orchestrator's
review) and 4.1 (the owed re-render) are not claimed.

## Measured after (task 2.3)

The same harness, the same machine, the rule in place (temporary lines
again, removed before the commit):

| | run 1 (load 2.7) | run 2 (load 3.1) |
|---|---|---|
| capture loop, 567 frames | **104.54 s, 5.42 frames/s** | **106.94 s, 5.30 frames/s** |
| Node: `pose()` | 74.20 s (130.9 ms/frame) | 74.60 s (131.6 ms/frame) |
| Node: `page.screenshot()` | 30.34 s (53.5 ms/frame) | 32.34 s (57.0 ms/frame) |
| `setFrame` calls / repaints in them | 778 / **571** | 778 / 571 |
| `repaint` in `setFrame` | 31.63 s (40.65 ms/pose, 55.4 ms per repaint) | |
| deciding (serialize and compare) | 0.03 ms/pose | |
| repaints in compositions | 194, 10.80 s | |
| command line `render`, end to end | **116.54 s** | |

Against before: 207 repaints fewer (the probe's count exactly), about
11 to 12 s less of the 116 to 118 s loop (10%), 4.8 to 4.9 frames a second
become 5.3 to 5.4, and the command line's render of the tour 127.6 s
becomes 116.5 s. A repaint still costs about 55 ms.

*Cut and Advance* was not re-rendered: the real viewer and the Leonardo
project are the orchestrator's. **Owed after the merge:** re-render it at
1080p and compare its 638 s for 1769 frames.

## Findings

1. **On the fixture, no pixel proof sees Chromium's glyph-edge effect.**
   A stage that repaints only fresh and resized poses passes every browser
   and incremental-rendering proof; a stage that never repaints a pose
   fails only preview's picture replay (a still). The content comparison is
   kept on the recorded evidence of real films (the old page's source-only
   seek differed at seven pixels; the code panel's leftmost column in the
   `shot-transitions` evidence), not on a fixture proof; the new test pins
   the rule itself by counting animation frames. A fixture that reproduces
   the effect would let a pixel proof judge the rule; none was found in
   this cycle.
2. **The repaint itself is the cost that remains**: about 55 ms each (two
   background flips, two pairs of animation frames at the headless
   compositor's rate), 571 of them in the tour's poses and 194 in its
   compositions, 42 s of a 105 s loop. How a repaint is made was out of this
   change; a later change could measure whether fewer frames suffice.
3. **The tour saves little because it is dense with cues**: typing,
   reveals, moving marks and emphasis change the page on most frames, and
   every composed frame's captures repaint. A film's held shots, where only
   the model moves, are where the rule saves; how much on *Cut and Advance*
   is the owed measurement.
4. **Content the serialization cannot see** (a shadow root, a scroll offset,
   a form control's value) would skip a repaint it needs. No shipped
   component and no fixture element uses one; `docs/stage.md` now says a
   component draws in the page's elements, not inside a shadow root.

## What was not done, and why

- *Cut and Advance* was not re-rendered and no real viewer was used: the
  project and the viewer bundle are outside this cycle's reach, and the
  comparison with its 638 s is the orchestrator's after the merge.
- How a repaint is made (the flip and its four animation frames) was not
  changed: the finding asked when a pose waits, and the brief excludes it.
- The instrumentation was not kept: the renderer has no timing report
  (`src/command-timing.mjs` is word timing, not performance), and adding
  one was not asked for.
- `docs/movie-document.md` was left as it is: its contract with the
  renderer does not say that every pose repaints.
  `docs/architecture-overview.md` was left as it is: it does not describe
  the repaint.
- No pixel proof that tells the rule from a weaker one was added (finding 1):
  none of the fixture's frames reproduces the effect, and inventing one
  without a real film's frame would be a guess.
