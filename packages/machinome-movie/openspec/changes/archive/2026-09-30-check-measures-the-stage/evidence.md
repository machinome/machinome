# Implementation evidence

## Authority and scope

A cycle of Videomaker's fix-warts campaign, on branch
`check-measures-the-stage` (worktree `WTs/check-measures-the-stage`), cut
from `fix-warts` at `0fb4c2f` (`pose-repaints`, `viewer-instances`,
`fixture-hygiene`, `narration-end-anchor` and `speech-key-lookup` merged),
for wart 1 of "The React stage" and wart 6 of "Cut and Advance, version 2"
(`workflow/warts.md`, 30 September 2026), under the orchestrator's ruling
quoted in the proposal. Nothing was pushed or published; no network or paid
request was made; nothing was installed. Integration into `fix-warts` is the
orchestrator's. Other agents ran their suites in their own worktrees at the
same time (a flaky-pixel-proofs investigation and the viewer-integration
layer); the load average is recorded with each run.

Environment of every run: Linux, 16 cores, Node v24.11.1, vitest 5.0.3,
Playwright's Chromium, the viewer double.

## Red

Layer 8 first, in `test/pipeline/movie-pipeline.test.mjs`, the new and
changed `check` tests run cold on the unchanged command
(`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow
test/pipeline/movie-pipeline.test.mjs -t "check"`, 21:08, load 8.49):

    × the tour is checked, previewed, rendered twice and reviewed from the command line 1492ms
    × check refuses a still enlarged beyond its allowance in a project set, before any take exists 1308ms
    × check refuses a picture view that leaves the picture in a project set, naming the shot and the time 2411ms
    ✓ check of a movie that shows no picture launches no Chromium 979ms

    AssertionError: check measures the layout in one Chromium
    0 !== 1
     ❯ test/pipeline/movie-pipeline.test.mjs:148:10

    AssertionError: The input did not match the regular expression /^Still plate would be enlarged 1\.40× in shot still \(864×576 source pixels in the 870\.4×576 box of slot plate of set playbill\); its upscale allowance is 1\.2\. Set upscale on the still, place it in a smaller slot, or use a larger source\.$/m. Input:
    'Chapter opening has spoken anchors and no cached narration take; run the speech command first (check, preview and render never generate speech)\n'

    AssertionError: Tour: 3 chapters, 9 shots, 18.9s; model 20s
    […]
    Picture still tip.plate (still plate): allowance 1.5×; enlargement checked against its slot's box at preview and render
    0 !== 1
     ❯ test/pipeline/movie-pipeline.test.mjs:267:10

          Tests  3 failed | 4 passed | 3 skipped (10)
    Test memo: 0 passed from the memo, 7 run

The test of a movie without pictures passes on the unchanged command, as it
must (it guards against the change launching a browser for nothing); the
tour's count of one launch shows the counting hook is not vacuous.

Layer 5, `test/browser/layout.test.mjs`, run cold before `src/layout.mjs`
existed (the module moved aside for the run, 21:12):

    FAIL  |slow| test/browser/layout.test.mjs [ test/browser/layout.test.mjs ]
    Error: Cannot find module '../../src/layout.mjs' imported from …/test/browser/layout.test.mjs
     Test Files  1 failed (1)
          Tests  no tests

(The layer 5 red is only the missing module; the behaviour's red is layer
8's above and the mutation below.)

Green, the same commands on the change: layer 5 cold, 21:12, load 20.07,
`Tests 1 passed (1)`, `Test memo: 0 passed from the memo, 1 run`; the whole
pipeline file cold, 21:13, load 21.93:

    ✓ |slow| test/pipeline/movie-pipeline.test.mjs (10 tests) 213857ms
     Test Files  1 passed (1)
          Tests  10 passed (10)
       Duration  217.10s (tests 100%)
    Test memo: 0 passed from the memo, 10 run

## Mutation, reverted at once

The probe calling every slot fixed (`fixed:true||…` in `measureSet`): the
layer 5 test fails `AssertionError: playbill.headline`, `- false + true`. A
headline measured empty has no picture box, so it would not have been
compared anyway; the explicit assertion is what catches a probe that stops
telling content-sized slots apart.

## What `check` prints on the tour

    Stage: bundled …/videos/tour/_build/stage/stage.js (sha256 311edde779ce) from stage.tsx; types checked
    Layout playbill at 1280×720: stage 870.4×576 at 64,86.4; plate 870.4×576 at 64,86.4; aside 243.2×288 at 972.8,216; headline sized by what it holds
    Layout frame at 1280×720: stage 1280×720 at 0,0
    Layout playbill-split at 1280×720: left 563.2×489.6 at 64,158.4; right 563.2×489.6 at 652.8,158.4; headline sized by what it holds
    Layout split at 1280×720: left 537.6×604.8 at 102.4,57.6; right 537.6×604.8 at 640,57.6
    Picture still tip.plate (still plate): peak 1.40×; allowance 1.5×

The bundle's hash, `311edde779ce`, is the base's: the runtime is unchanged,
so no film's shot cache moves.

## The probe's cost (task 4.2)

`check` of the fixture tour and of the fixture movie `minimal` from the
command line, each on its own copy of the fixture project with its takes,
bundles built once first, the base tool (an export of `0fb4c2f` in a scratch
directory, sharing the worktree's `node_modules`) and the change alternated
nine times (21:18, load 20.05 at the start, 18.95 at the end):

| movie | base, median | change, median | all runs, change |
|---|---|---|---|
| tour | 0.88 s | 1.96 s | 1.51, 2.41, 1.96, 1.99, 2.16, 1.57, 2.09, 1.74, 1.47 s |
| minimal | 0.82 s | 0.74 s | 0.69, 1.18, 0.70, 0.72, 0.83, 0.74, 1.08, 0.73, 1.55 s |

The probe costs the tour about 1.1 s (one Chromium launch, one page, four
set poses); a movie without pictures pays nothing measurable. An earlier
unalternated measurement of the base at load 9.5 gave 1.46 s (first run,
bundling), 0.77 s and 0.66 s for the tour.

## Both suites on the final content (task 4.1)

The Node suite, `npm test` from the worktree, 21:20:42 to 21:34:24, load
20.01 at the start and 24.33 at the end. `test/support/reach.mjs` is in every
slow test's key (it gained the `src/layout.mjs` entry), so no verdict was in
the memo and every test ran:

     Test Files  31 passed (31)
          Tests  316 passed (316)
       Duration  821.50s (tests 98%, import 1%, transform 1%)
    Test memo: 0 passed from the memo, 316 run

The Python suite, `python -m pytest -q` in `python/`, 21:34:37:

    189 passed in 20.22s

Only records changed after these runs (the archive, the evidence, the
tasks); no slow key reads them.

## Findings

1. **`src/pictures.mjs` is part of every film's shot-cache key.** The render's
   common key hashes `render.mjs`, `timeline.mjs`, `pictures.mjs` and five
   other modules whole, so the planned refactor of the two refusal messages
   into shared functions would have recaptured every film for a change to
   words no frame draws. The words are written in `src/layout.mjs` in the
   YAML wording instead (design D7, implementation note). Keying on the
   modules' drawing code rather than their bytes would take a decision this
   cycle does not make.
2. **A view's refusal needs the takes.** A picture view key's time may be
   anchored to the narration, so the frames of its cue are known only after
   the takes resolve; `check` refuses a leaving view then, before preview,
   not before `speech`. The enlargement needs no time (the peak is the
   largest key's zoom) and is refused before any take is read.
3. **The ruling's "no picture in a project's set" read as "no picture".** A
   movie document can use only `frame`, `split` and its own sets, and the
   first two are laid out by `stage.css` and the movie's safe inset, which
   Node does not know either; the ruling also says "for a project's set as
   for a shipped one". So a document with a picture in `frame` measures too,
   and a document with no picture opens no browser.
4. **When the probe runs, the stage's mount refusals come earlier.** A set
   the bundle does not register, or slots that differ from the document's,
   are refused at `check` (prefixed `Measuring the stage's layout for
   check:`) for a movie that shows a picture, and still only at preview for
   one that does not. Not a promise the spec makes; recorded.
5. **The content test is a probe.** A slot is "sized by what it holds" when
   its box changes once every slot holds a block three times the frame's
   size. The tour's `headline` (a width, no height) is caught; a layout that
   changes only for other content would be trusted wrongly, and preview and
   render would still refuse on the live box.

## What was not done, and why

- **The probe's boxes are not given to preview and render** as a project
  set's known layout. The renderer compares an element's box, which a set
  may pad inside its slot, and the boxes would come from another page or an
  earlier run; that is a decision (design D6), so it is left out as the
  ruling allows.
- **No refusal at `check` for a slot sized by what it holds**: its box is
  known only with the frame's content, which is preview.
- **The ruling's layer 5 set list is covered on the fixture tour only**
  (`frame`, `split`, `Playbill`, `PlaybillSplit`); no set whose slot grows
  with a sibling's content exists in the fixtures, and none was added for
  this test.
- **Nothing was measured on *Cut and Advance*.** The film is the project's;
  its `check` with the measured `Leonardo` layout is the orchestrator's to
  run after the merge.
- **The whole-suite cold run** was not asked for; the changed slow files ran
  cold (above), and the reach table's change put every slow test's key out
  of the memo, so the suite run below is cold for the slow layer by
  construction.
