# Implementation evidence

## Authority and scope

A cycle of Videomaker's fix-warts campaign, on branch `viewer-instances`
(worktree `WTs/viewer-instances`), cut from `fix-warts` at `8d6c842` (wave 1
merged: `pose-repaints`, `narration-end-anchor`, `speech-key-lookup`,
`fixture-hygiene`), for wart 5 of "The React stage" and wart 4 of "Cut and
Advance, version 2" (`workflow/warts.md`, 30 September 2026), under the
orchestrator's ruling quoted in the proposal. Nothing was pushed or
published; no network or paid request was made; nothing was installed.
Integration into `fix-warts` is the orchestrator's. Another agent ran the
`flaky-pixel-proofs` investigation in its own worktree at the same time;
the machine's load is recorded with each run.

Environment of every run: Linux, 16 cores, Node v24.11.1, vitest 5.0.3,
Playwright's Chromium, `ffmpeg version 6.1.1-3ubuntu5`, the viewer double.

## Red

Layer 5 first, in `test/browser/stage.test.mjs`, the whole file run cold on
the unchanged runtime (`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow
test/browser/stage.test.mjs`, 20:03, load 8.94). The two new tests and the
existing test whose mount count was updated to the lease fail; the other
ten pass:

    × a view keeps its viewer instance across the cuts inside its chapter 688ms
    × a view that leaves frees its instance, and the next view is drawn on it as on a fresh one: highlight restored, layers shown again, canvas refilled 902ms
    × no order of frames mounts more viewer instances than one frame places views, and each frame is drawn the same in every order 5325ms

    AssertionError: the instance the session's first frame mounted for opening.wide, leased to balance.mill when it left
    2 !== 1
     ❯ test/browser/stage.test.mjs:239:10

    AssertionError: one instance serves both views
    2 !== 1
     ❯ test/browser/stage.test.mjs:273:10

    AssertionError: two instances in the order A, B, AB
    3 !== 2
     ❯ test/browser/stage.test.mjs:327:12

          Tests  3 failed | 10 passed (13)
    Test memo: 0 passed from the memo, 13 run

Layer 4, in `stage/stage.test.tsx`, before `leaseViews` existed
(`npx vitest run --project stage stage/stage.test.tsx`):

    × below API 28 an instance is leased only to the lens it mounted with 0ms
    × no sequence of frames mounts more instances than one frame places views, and a placed view keeps its instance 1ms
    FAIL  |stage| stage/stage.test.tsx > viewer lease > a placed view keeps its instance; a view without one takes the lowest free; one mounts only when none is free
    TypeError: leaseViews is not a function
          Tests  3 failed | 15 passed (18)

(The layer 4 red is only the missing function; the layer 5 red is the
behaviour's.)

Green, after the change, the same two commands: `Tests 13 passed (13)`,
`Test memo: 0 passed from the memo, 13 run` (20:06, load 10.89), and
`Tests 18 passed (18)`. `npx tsc --noEmit -p stage/tsconfig.json` printed
nothing.

## Mutations (task 1.4), each reverted at once

- **A lease that forgets what the instance holds** (the leased instance's
  `hidden`, `applied` and `restore` reset without restoring): the lease test
  fails when A is drawn again, `Error: page.evaluate: Error: View
  balance.mill in shot source: A highlight is already standing` (the
  double refuses a second highlight over one never restored), and the
  six-orders test fails `A is drawn the same in the order B, A, AB as in A,
  B, AB` (the highlight B left on the instance tints A's canvas).
- **A lease that never takes a free instance** (a view mounts whenever it
  held none at the frame before): `2 !== 1` for the cuts test, `4 !== 1`
  for the lease test, `4 !== 2` for the six orders. The unchanged runtime
  (one mount per view element) is the red above.
- **The lens ignored** (layer 4, `leaseViews` leasing any free instance):
  `below API 28 an instance is leased only to the lens it mounted with`,
  `expected [ +0 ] to deeply equal [ -1 ]`.

## The count on the fixture tour

A scratch harness outside the repository (not committed) loaded the tour
and posed its 567 output frames in order at 640 pixels wide, as `render`'s
capture loop does (transitions and faded marks composed as they are),
recording `window.viewerInstances` and which view elements each reported
instance drew:

- the unchanged runtime: `"mounts":4,"served":{"1":["opening.wide"],
  "2":["balance.mill"],"3":["tip.close"],"4":["tip.wide"]}`;
- the lease: `"mounts":1,"served":{"1":["opening.wide","balance.mill",
  "tip.close","tip.wide"]}`.

## What *Cut and Advance* will mount (task 3.4)

Read from the film's resolved document
(`videos/cut_and_advance/_build/movie-resolved.json` of the Leonardo
project, read only): six chapters, six view elements (`question.mill`,
`drive.mill`, `feed.mill`, `ropes.mill`, `ropes.wide`, `closing.mill`),
twelve shots, and every shot places exactly one view. Its joins (a
dissolve into `coupling` and into `carriage`, a wipe into `stroke`) are
composed from the outgoing and incoming pictures posed one after the other,
each a frame placing one view. It needs Viewer API 28 (marks and
highlights), so the lens rule does not apply. Under the lease the film
mounts **one** viewer instance, not six. (The brief expected two, "the film
places at most two views in one frame"; no stage frame of the film places
two: a join's two pictures are two frames.) The memory with the real viewer
is the orchestrator's measurement after the merge (task 4.1).

## Three cold runs of the slow project (task 2.1)

`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow` from the worktree,
three times in a row on the final content (the stage, the tests and the
renderer as committed; only records changed afterwards, and no slow key
reads them). Another agent's work loaded the machine throughout:

| run | started (load, 1 min) | Test Files | Tests | Duration | Test memo |
|---|---|---|---|---|---|
| 1 | 20:13:24 (9.81) | `10 passed (10)` | `115 passed (115)` | `651.80s (tests 100%)` | `0 passed from the memo, 115 run` |
| 2 | 20:24:16 (10.95) | `10 passed (10)` | `115 passed (115)` | `660.24s (tests 100%)` | `0 passed from the memo, 115 run` |
| 3 | 20:35:18 (14.20) | `10 passed (10)` | `115 passed (115)` | `652.21s (tests 100%)` | `0 passed from the memo, 115 run` |

Three of three green, none from the memo: every A-B-A proof of layer 5,
the two new lease tests, `the tour previews` (pixel replay, the picture,
transition, entrance and emphasis replays), and `incremental-rendering`'s
"every incremental PNG equals a separately cold film" held on every run.

## The whole suites on the final content (task 2.2)

After the archive (only `evidence.md` changed since, which no key reads):

- **Node**, `npm test` (20:46, load 9.78):

      Test Files  30 passed (30)
           Tests  312 passed (312)
        Duration  651.01s (tests 98%, import 1%, transform 1%)
      Test memo: 29 passed from the memo, 283 run

  The 29 memoized passes are `test/pipeline/pictures.test.mjs` (16),
  `source-scenes.test.mjs` (5) and `speech.test.mjs` (8), whose keys reach
  neither the stage nor the renderer; each also ran cold, and passed, in the
  three runs above.
- **Python**, `python -m pytest -q` in `python/`: `189 passed in 16.11s`.

`openspec archive viewer-instances --yes` renamed and replaced the
requirement in `react-stage` and replaced the requirement in `test-suite`
(`~ 2`, `→ 1`); it moved the renamed requirement to the end of
`react-stage` and removed the blank line before `## Requirements` and the
file's last blank line, which were put back by hand (the requirement where
it stood). It archived with 11 of 13 tasks: 0.2 (the orchestrator's review)
and 4.1 (the owed measurement) are not claimed. `openspec validate --specs
--strict`: `Totals: 16 passed, 0 failed (16 items)`.

## Findings

1. **Below Viewer API 28 an instance cannot take another view's lens**, and
   the ruling's premise ("each frame states each instance's whole state")
   fails there: `setView` below 28 takes camera and target only, and a movie
   document needs 28 only when a view *moves* to a lens other than its own
   (`movieViewerApi`), so two view elements with different lenses can be
   produced at API 21 with one instance each. Leasing across them would draw
   the second through the first's lens, and below 28 the renderer does not
   check the lens. The change leases such an instance only to its own lens
   (design D3), so the bound is per lens below 28 and exact from 28; the
   contract sentences say so. No fixture or film is below 28 with two
   lenses, so this rule has only its layer 4 test. The alternative, making
   two lenses in one movie require API 28, is a change to the document
   contract's API rule and the orchestrator's to take.
2. **The brief's expected count for *Cut and Advance* was two; it is one**
   (above). A frame the stage draws places one view; a join is two frames.
3. **YAML episodes gain the most**: an episode is one chapter per shot, so
   each shot that shows the model had its own view element and mounted its
   own viewer; under the lease an episode mounts one (below API 28 all its
   views share its first camera's lens, which `requiredViewerApi` already
   enforces). A lens whose up differs only in length from the first
   camera's would count as another lens and mount one more instance; this is
   conservative and no episode does it.
4. **The instance number is visible in the page's content** through the
   marks' clip-path ids (`uid`). A frame drawn on another instance than at
   the last repaint therefore differs in content and repaints under
   `pose-repaints`' rule; that costs a repaint the frame would have had
   anyway, since moving a host into another box is a resize.
5. **Which instance a view is drawn on depends on the frames posed before;
   nothing drawn does.** The six-orders test shows each frame's pixels equal
   in all six orders with the late-canvas double, and preview's replay
   proofs and incremental rendering's exact bytes hold on every cold run.

## What was not done, and why

- No disposal API: the count is bounded, and the brief excludes it.
- The viewer double's mount, the shot cache and the canvas wait are
  unchanged. The double records no `setVisible` call, so the lease test
  wraps the instance's method in the page (`window.film.viewer`) instead of
  changing the double.
- Memory with the real viewer was not measured: layer 6 has no test, the
  real bundle and the Leonardo project are outside this cycle's reach, and
  the measurement is the orchestrator's after the merge (with
  `viewer-integration-layer`).
- The lens rule below API 28 has no browser test: the fixture tour needs
  API 28, and a second fixture movie at API 21 with two lenses was not
  built for a rule no film exercises (finding 1).
- The rule requiring API 28 for two lenses in one movie was not adopted:
  it would change the document contract's API rule, which is the
  orchestrator's.
