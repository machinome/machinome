# `flaky-pixel-proofs` — the two intermittent pixel proofs, investigated

Status: finished investigation, 1 October 2026 (begun 30 September), cycle
`flaky-pixel-proofs` of the fix-warts campaign (branch `flaky-pixel-proofs`,
cut from `fix-warts` at 8d6c842, after `pose-repaints` merged). No behaviour
changed, so no OpenSpec change was cut and nothing here is ratified. The wart
is "A second intermittent pixel test", `workflow/warts.md`, "The test suite"
(one-runner cycle), item 1.

In one paragraph: **neither proof failed in twenty cold runs on the current
stage under load.** The same twenty runs on the old film page, where both
failures were recorded, reproduced the partial picture replay twice, with the
recorded message, and its cause was found: the old page sized a picture only
after decoding it at its natural size, and Chromium's GPU rasterization then
draws an image shown at about half its size or less one of two ways, chosen
per page, a level apart at its detailed pixels. The React stage sizes its
pictures in CSS before they load, and draws them one way in every page. The
other recorded failure, the incremental film's frame 1, did not reproduce on
either page and stays unexplained. The evidence files are in
`flaky-pixel-proofs/` beside this report.

## The two failures on record

Both were seen once, each in a whole-suite base run, and both passed when
their file ran alone right after.

| proof | seen in | code under test | message |
|---|---|---|---|
| `every incremental PNG equals a separately cold film across the first reused-shot gap` (then `test/incremental-rendering.test.mjs`) | the `movie-document` cycle's base run, source 6e86728, `node --test` | the old film page, `src/film.html` and `src/film.js` | global frame 1's PNG hash differed between the incremental and the cold film |
| preview's picture proof inside `a movie document is refused before its takes, then checks, speaks, previews and renders from them` (then `test/movie-pipeline.test.mjs`) | the `one-runner` cycle's base run, source 5dae43f, `node --test --test-concurrency=1` | the old film page | `Partial picture replay is not deterministic: wheel #0 at 1.00 s` |

Neither run kept its PNGs. Both failures predate the `react-stage` change,
which replaced the film page with the React stage (`stage/runtime.tsx`); no
failure of either proof has been recorded on the stage. Since `react-stage`
the two proofs passed in every recorded run that executed them: the cold
whole-suite run of `react-stage`, the two of `test-memo-sharing`, the
whole-suite runs of the campaign with no slow pass from the memo
(`speech-key-lookup`, `narration-end-anchor`, the campaign head bf4083a), the
five cold runs of the slow project in `pose-repaints`, and the twenty below.

## Machine and load

Linux, 16 cores, 15 GB, Node v24.11.1, vitest 5.0.3, Playwright 1.62.0 with
Chromium 151.0.7922.34 (headless shell, `--use-angle=swiftshader
--enable-unsafe-swiftshader`), `ffmpeg version 6.1.1-3ubuntu5`.

Extra load came from this worktree's pure project in endless loops (`npx
vitest run --project pure`, 179 tests, about three seconds a pass; none of
the 6876 passes failed): one loop during runs 1 to 11 on the stage, two from
run 12 on and during all twenty runs on the old page. Other agents' suites ran
in their own worktrees at the same time, sampled once at each run's start (a
suite that ran between samples is missing): the orchestrator's in `fix-warts`
during stage runs 1 and 2, `viewer-instances` during stage runs 2 to 10,
`check-measures-the-stage` during 13 to 15, `viewer-integration-layer` during
14 to 17; none was seen at the starts of the old-page runs, whose load
averages (15 to 41) show that others' work ran during them.

## Twenty runs on the current stage

Content 8d6c842. Each run: `VIDEOMAKER_TEST_COLD=1 KEEP_VIDEOMAKER_TEST=1
TMPDIR=<scratch>/tmp-NN npx vitest run --project slow
test/pipeline/movie-pipeline.test.mjs
test/pipeline/incremental-rendering.test.mjs` from the worktree, in a plain
shell loop; a run's kept fixtures were removed only when it passed.

| run | started (load, 1 min) | ended (load) | result | Duration |
|---|---|---|---|---|
| 01 | 19:58:35 (1.37) | 20:05:00 (11.89) | pass | 384.22s |
| 02 | 20:05:00 (11.89) | 20:11:23 (9.00) | pass | 381.82s |
| 03 | 20:11:24 (9.00) | 20:17:44 (13.84) | pass | 378.81s |
| 04 | 20:17:44 (13.84) | 20:24:05 (10.66) | pass | 380.20s |
| 05 | 20:24:05 (10.66) | 20:30:29 (10.22) | pass | 382.69s |
| 06 | 20:30:29 (10.22) | 20:36:55 (13.13) | pass | 385.12s |
| 07 | 20:36:56 (13.13) | 20:43:18 (11.02) | pass | 381.07s |
| 08 | 20:43:18 (11.02) | 20:49:43 (13.13) | pass | 383.68s |
| 09 | 20:49:43 (13.13) | 20:56:06 (11.46) | pass | 382.20s |
| 10 | 20:56:06 (11.46) | 21:02:24 (11.04) | pass | 377.09s |
| 11 | 21:02:25 (11.04) | 21:08:43 (8.97) | pass | 377.16s |
| 12 | 21:08:43 (8.97) | 21:16:10 (19.83) | pass | 445.75s |
| 13 | 21:16:10 (19.83) | 21:23:57 (26.03) | pass | 465.56s |
| 14 | 21:23:57 (26.03) | 21:31:45 (22.21) | pass | 467.29s |
| 15 | 21:31:46 (22.21) | 21:39:26 (22.91) | pass | 459.02s |
| 16 | 21:39:27 (22.91) | 21:47:02 (22.78) | pass | 454.37s |
| 17 | 21:47:02 (22.78) | 21:54:34 (23.27) | pass | 450.26s |
| 18 | 21:54:34 (23.27) | 22:02:23 (21.67) | pass | 467.18s |
| 19 | 22:02:23 (21.67) | 22:09:47 (22.86) | pass | 443.52s |
| 20 | 22:09:48 (22.86) | 22:17:09 (19.73) | pass | 440.06s |

Every run printed `Test Files  2 passed (2)`, `Tests  27 passed (27)` and
`Test memo: 0 passed from the memo, 27 run`.

The proofs ran, and not vacuous versions of them: in a kept run of `the tour
is checked, previewed, rendered twice and reviewed from the command line`
(cold, 140.31 s), `preview/report.json` records one picture check,
`tip.plate` in shot `still`, with `partialReplay: true` at 16.92 s, opacity
0.5. The incremental proof compares all sixteen PNGs and the encodes by hash.

## Twenty runs on the old film page

To learn whether this machine and this load can show the failures at all, the
code where both were seen ran the same way: a scratch clone of the repository
checked out at 5dae43f (the `one-runner` base), `node_modules` linked from this
worktree (the same Playwright 1.62.0), and `KEEP_VIDEOMAKER_TEST=1
TMPDIR=<scratch>/tmp-NN node --test --test-concurrency=1
test/incremental-rendering.test.mjs test/movie-pipeline.test.mjs`, twenty
times, two pure loops running throughout (24 tests a run).

| run | started (load) | ended (load) | result | wall |
|---|---|---|---|---|
| 01 | 22:21:48 (0.40) | 22:26:01 (19.18) | pass | 253.0 s |
| 02 | 22:26:01 (19.18) | 22:30:14 (19.66) | pass | 253.3 s |
| 03 | 22:30:15 (19.66) | 22:34:26 (18.77) | pass | 251.6 s |
| 04 | 22:34:26 (18.77) | 22:38:37 (20.58) | pass | 251.0 s |
| 05 | 22:38:38 (20.58) | 22:42:50 (18.46) | pass | 252.4 s |
| 06 | 22:42:50 (18.46) | 22:47:06 (20.63) | pass | 255.7 s |
| 07 | 22:47:06 (20.63) | 22:51:21 (21.96) | pass | 255.2 s |
| 08 | 22:51:21 (21.96) | 22:55:34 (17.25) | pass | 252.6 s |
| 09 | 22:55:34 (17.25) | 22:59:48 (21.62) | pass | 254.0 s |
| 10 | 22:59:48 (21.62) | 23:04:02 (18.39) | pass | 253.6 s |
| 11 | 23:04:02 (18.39) | 23:08:23 (20.28) | pass | 261.1 s |
| 12 | 23:08:24 (20.28) | 23:12:44 (21.45) | pass | 260.7 s |
| 13 | 23:12:45 (21.45) | 23:17:10 (15.74) | pass | 265.3 s |
| 14 | 23:17:10 (15.74) | 23:21:30 (17.31) | pass | 259.8 s |
| 15 | 23:21:30 (17.31) | 23:26:00 (24.43) | pass | 270.1 s |
| 16 | 23:26:00 (24.43) | 23:30:14 (34.47) | **fail** | 253.5 s |
| 17 | 23:30:14 (34.47) | 23:34:57 (24.04) | pass | 282.8 s |
| 18 | 23:34:57 (24.04) | 23:39:42 (41.65) | pass | 285.4 s |
| 19 | 23:39:43 (41.65) | 23:44:31 (31.77) | pass | 288.5 s |
| 20 | 23:44:31 (31.77) | 23:48:56 (37.34) | **fail** | 264.5 s |

Both failures were the recorded one, word for word: `Error: Partial picture
replay is not deterministic: wheel #0 at 1.00 s; inspect
preview/picture-wheel-0-partial-replay-{before,after}.png` (`ℹ tests 24`,
`ℹ pass 23`, `ℹ fail 1`). The incremental proof passed in all twenty.

### The pixels

The two failures' pairs are byte-identical to each other: run 16's `before`
and run 20's `before` are the same file, and so are the two `after`s
(`old-page-partial-replay-{before,after}.png`). The old fixture's still is
ffmpeg's `testsrc2` at 640 × 360 (`old-fixture-still.png`), drawn over the
whole 320 × 180 preview frame, exactly half its size, and blended at opacity
0.5 over the stage. Between `before` and `after`, **453 of 57,600 pixels
differ, each by one level in one channel**, all inside the still's detail:
its timecode at the top left (rows 3 to 8, x 1 to 46) and its moving checker
block at the bottom right (rows 112 to 153, x about 200 to 280); nothing on a
glyph of the page, a plate edge or the view's rectangle
(`old-page-partial-replay-difference.png`, differing pixels in red). Two
discrete renderings, not noise.

### Where in the proof

The old proof (`src/render.mjs` at 5dae43f) blends a partial picture as
`round(o × capture with the picture at opacity 1 + (1 − o) × capture
without it)` in a CPU canvas. A scratch instrumentation of the clone recorded,
for the first partial pose of each page and ten more poses of the same instant
in the same page, the two captures, the blend canvas's own pixels
(`toDataURL`) and the screenshot. In twelve pages of the preview test
(load 19 to 26): in eight, all eleven poses were identical; in four, the
**first** pose's capture with the picture differed from the later ones (by one
level at 840 pixels, the same detail areas), while the capture without the
picture never differed, and the blend canvas and the screenshot differed only
through it. The later poses in those pages were the rendering the other pages
had (in one page one later pose kept the first rendering). So the screenshot,
the blend and the repaint were faithful; the picture itself had been drawn
two ways.

### The mechanism, outside the film

`flaky-pixel-proofs/two-renderings.mjs` draws one PNG at a given size on a
plain 320 × 180 page, in fresh pages of one Chromium launched with the
renderer's flags, repaints the whole page as the stage does, and counts the
distinct screenshots. Its mode `late` sets the image's source, decodes it and
only then gives it its size, as the old page's `drawPicture()` did (`src`,
`await decode()`, then `left`, `top`, `width`, `height`); `sized` gives the
size first, as the stage's picture element does (its size comes from CSS on
its first layout).

| still | drawn at | mode | flags | pages | renderings |
|---|---|---|---|---|---|
| old `testsrc2`, 640 × 360 | 320 × 180 (0.50) | late | the renderer's | 24 | **2** (12 / 12) |
| old `testsrc2` | 320 × 180 | sized | the renderer's | 48 | 1 |
| fixture plate, 864 × 576 | 300 × 200 (0.35) | late | the renderer's | 16 | **2** (7 / 9) |
| fixture plate | 300 × 200 | sized | the renderer's | 16 + 48 | 1 |
| fixture plate | 432 × 288 (0.50) | late | the renderer's | 24 | **2** (17 / 7) |
| fixture plate | 432 × 288 | sized | the renderer's | 24 | 1 |
| fixture plate | 300 × 200 | late | `--disable-gpu-rasterization` added | 16 | 1 |

Earlier scratch versions of the same experiment (images sized late, with and
without a doctype, served through Playwright's routing or over HTTP, at
integer or fractional offsets, with a decode of the image before the first
pose, with five or thirty repaints or three seconds before it, with a hidden
or visible canvas beside it, in new pages or new browsers) all gave two
renderings, each page keeping one of them over 30 poses; the plate drawn at
605 × 403 (0.70) and late gave one rendering in 12 pages, and the threshold
lay between 0.70 and 0.55. With software rasterization the late image is
drawn one way. So: **Chromium 151's GPU rasterization (on SwiftShader) draws
an image shown at about half its size or less, whose layout gave it another
size before it was decoded, one of two ways chosen per page**, a level apart
at its high-frequency pixels; which way does not depend on load as far as
these runs show. The old proof failed when the first partial pose of a page
drew it one way and the replay the other; given the page-level choice, a
higher load was not needed, and the two failing runs' higher load averages
(24 to 41) are not evidence that it was.

### Why the stage is not exposed

The stage's picture element renders `<img class="vm-picture-img">` with its
geometry in custom properties and its size from `stage/stage.css` on its
first layout, so the image is never laid out at its natural size; `compose()`
draws captures at their own size and `composeMarkBlend()` draws them 1:1 in a
canvas, so neither scales. Measured in stage pages (a scratch harness calling
`browserSession` on the fixture tour with one shared Chromium): the plate
fully shown in the middle of shot `still`, posed in fresh pages at widths 320
(drawn at 0.348 of its size), 240 (0.263) and 480 (0.522), 10 pages each, and
in the earlier draft of a layer-5 test at width 320, 48 pages: one rendering
each time. A plain `<img>` of the still appended to the stage page and sized
before decoding: one rendering in 16 pages. In the tour at its preview width
of 640 the plate is drawn at about 0.70 of its size, above the threshold
anyway.

## What was looked at, and whether each suspected cause is possible

1. **A screenshot taken before the compositor presented the last change.**
   Every stage pose whose document differs from the document at the last
   repaint, and every composition, ends in `repaint()` (two animation frames
   with the body's background flipped, two after restoring it); with the
   viewer doubles these two files use, a pose that skips it changed nothing on
   the page. A scratch experiment that changed text and screenshot after 0, 2
   and 10 animation frames, with and without a WebGL canvas, with GPU or
   software rasterization, matched a fresh raster 216 of 216 times. **Not the
   cause of the recorded failure** (its screenshot and blend were faithful),
   and not possible on the stage in these files.
2. **A font that decodes late.** No stage stylesheet has an `@font-face` or
   `url()`; the faces are the system's DejaVu through fontconfig, and `boot()`
   and every screenshot wait for `document.fonts.ready`. **Not possible.**
3. **An image that decodes late, or draws two ways.** Not late: every picture
   is decoded before the pose's repaint. Two ways: **the cause of the recorded
   partial picture replay failure**, above; not possible for the stage's
   pictures, which are sized before they load.
4. **The viewer double's canvas sized on its own animation frame.** Only
   `lateCanvas` does that, used only by `test/browser/stage.test.mjs`; the
   doubles of these two files fill their host at once. **Not exercised.**
5. **A wait that `pose-repaints` removed and the load exposes.** The rule
   removes the repaint only from poses whose document equals the one at the
   last repaint, never from `fresh` poses or compositions; the picture replay's
   poses all change the document, and the incremental double's `setTime`
   recolours its canvas, so every pose there repaints. **Not possible in these
   two files**; and the old page failed before the rule existed.
6. **An encode difference.** The failures were a screenshot comparison and a
   PNG hash; the MP4 comparison never failed. **Not the recorded failure.**
7. **Chromium's glyph edges left outside an invalidated area.** The reason the
   repaint exists; the experiment of item 1 did not show it, nor did
   `pose-repaints` on the fixture. Not seen.
8. **A clock or a random number in the stage.** None in `stage/` or the
   tour's stage module, and no CSS transition or animation.

## The incremental frame, still unexplained

Global frame 1 of the old incremental fixture (shot A at 0.5 s: the code panel
mid-typing, the double's canvas recoloured, no picture) differed once between
two renders in two pages. It passed in all forty runs here, twenty on each
page. The mechanism found above needs a scaled image, and that fixture has
none; the old page did not repaint that frame (it repainted only fresh,
picture and source-only frames), the stage does. Its cause is not known.

## What a future failure should keep

A flaky proof is not run again once it passed (the verdict memo), so the cold
run before integration is where one shows, and it should leave its evidence:

- Run the cold slow layer with `KEEP_VIDEOMAKER_TEST=1` and `TMPDIR` set to a
  directory that survives, so a failing test's fixture directory stays; remove
  the passing runs' directories afterwards.
- For preview's proofs keep `_build/preview/*-{before,after}.png` and
  `report.json`; for the incremental proof, both shot-cache assemblies the two
  manifests name (`incremental-manifest.json` in the fixture and in `cold/`).
- Diff the pair pixel by pixel (`src/pixels.mjs` `decodePng`): the count, the
  box, the largest channel difference, and what is there (glyph edges, a
  picture's detail, a canvas, a plate edge). A difference of one level inside
  a picture's detail is this mechanism; `two-renderings.mjs` tells whether the
  page in question draws that image two ways.
- Record the run's load and the other suites running.

The fixture helpers could keep a failing test's directory by themselves
(vitest's `onTestFinished` sees the test's state); not done, because it changes
every slow test's key and no failure on the stage has asked for it.

## What could be built, and was not

- **A layer-5 proof that a picture is drawn alike in every page**: the plate
  fully shown in shot `still`, posed in sixteen fresh pages at width 320 (drawn
  below half its size), screenshots byte-equal. Drafted and run cold three times
  (13.4 to 14.6 s each): it passed, so it could not be shown red on the stage,
  and it was not committed; it would catch a picture element, a shipped one or
  a project's, that sets its size after decoding.
- **`--disable-gpu-rasterization` in `CHROMIUM_ARGS`**: it removes the two
  renderings outside the stage, but changes how every film's pictures are
  resampled (by up to one level: in a 256 × 256 ramp enlarged 2.8 times, 235,480
  channel values differ from GPU rasterization), and with it the whole slow
  project cold (740.36 s, two pure loops running) failed one assertion,
  `render.test.mjs:181`, whose expected ramp value `128+40/(720/256)` (142.22)
  puts the pixel centre half a pixel off (141.90 at the centre; GPU rasterization
  gives 142, software 141); the old page's highlight proof then failed in 12 of
  12 runs. Not a change for a mechanism the stage does not meet.

## A finding outside this cycle: the chrome vanishes during every fade

Looking at the kept tour's frames: **during a mark's or a picture's fade the
set's chrome is not drawn.** In the tour rendered at 640 × 360, 47 of 567 frames
lack the masthead ("VIDEOMAKER · FIXTURES", "TOUR") although their set draws
it: 361–371, 394–404 and 436–446 in shot `rise` (the plank's ring and label
fading in and out) and 501–514 in shot `still` (the plate fading in); frames
360 and 499 have it, 365 and 507 do not. It is deterministic, not a flake.

Cause: `showPicture()` (`src/render.mjs`) poses each fade variant with
`{pictureOnly:true,fresh:true}`, which sets the body's `picture-only` class,
and the stage's `composeMarkBlend()` clears the transition classes but not
`picture-only`, so `.picture-only #chrome{visibility:hidden}` still hides the
live chrome over the blend. The old page posed its variants with the caller's
options, so its blended frames kept the chrome; `react-stage` (0a14a30) made
the variants picture-only. No proof sees it: the fade proofs' `mid` phase only
asserts the composed frame differs from both references, and their `end` phase
has no variants.

Smallest correction: give `composeMarkBlend` the caller's `pictureOnly`, as
`compose` takes it, and set the class before its repaint; then drop the
`classList.add('picture-only')` that `showPicture` does after the blend.
Clearing the class after the repaint instead would change the document after
the last repaint, the condition the repaint exists to prevent. A proof: a
blended frame's chrome rectangles equal the unblended frame's. Left to the
orchestrator's triage.

## What was not done, and why

- No fix: on the stage nothing reproduced, and the mechanism found does not
  apply to how the stage draws pictures; the brief forbids inventing one. No
  retry, no tolerance, no change to the memo.
- No OpenSpec change, ADR amendment or changelog bullet: no behaviour changed.
- The real viewer was not used: these proofs run on the doubles.
- The incremental frame's cause was not found (above).
- The chrome finding was not fixed: it is not this cycle's wart, and its fix
  changes what films show.
