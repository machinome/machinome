# Implementation evidence

## Authority and scope

A cycle of Videomaker's fix-warts campaign, on branch
`viewer-integration-layer` (worktree `WTs/viewer-integration-layer`), cut
from `fix-warts` at `0fb4c2f` (`pose-repaints`, `viewer-instances`,
`fixture-hygiene`, `narration-end-anchor`, `speech-key-lookup` merged), for
wart 1 of "Cut and Advance, version 2" and wart 5 of "The React stage"
(`workflow/warts.md`, 30 September 2026). Nothing was pushed or published;
no network or paid request was made; nothing was installed. Integration into
`fix-warts` is the orchestrator's. Other agents ran suites in their own
worktrees throughout (the one-minute load average was 18 to 24 during every
run below).

Environment: Linux, Node v24.11.1, vitest 5.0.3, Playwright's Chromium,
`ffmpeg version 6.1.1-3ubuntu5`. The viewer bundle is the one the framework's
`machinome viewer` report names on this machine (report: `apiVersion` 28,
`documentVersions` 1 to 13, `version` 0.7.0; SHA-256
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`), passed
as `VIDEOMAKER_VIEWER_BUNDLE`; its path is written nowhere in the repository.
Its sources were not read: the tests use its `mount`, `apiVersion` and the
methods the stage calls.

## The export's provenance

- Framework: the workspace venv's `machinome` command (the installed
  distribution reports version 0.7.0 through `importlib.metadata`; the
  command has no version option).
- Command, from `python/tests/fixtures/project/`:

      machinome export seesaw -o export/seesaw --fps 30 --frames 600 --no-widget

- Result: `export/seesaw/manifest.json` (format `machinome-export`, version
  2, `animation: {fps: 30, frames: 600, loop: 20.0}`, the tree `Seesaw` /
  `Base`, `Stand`, `Beam` / `Plank`, `Weight`, `pivot`, each block
  `color: "#8f9aa3"`, the beam's operation
  `(20 - (4 * abs((($t * 20.0) - 10))))` degrees about y, then 55 up) and one
  mesh, `models/models/seesaw-Block-211d0bb8cf4f.stl`, 684 bytes (12
  triangles, the 40×10×10 box). The build directory the command left in the
  project was removed.
- The model (`models/seesaw.py`) gained `time = Time(loop=20)` (without it
  the export carries no `loop` and every fixture movie is refused "Model
  duration differs"), rest placement in `render()`, the tipping in
  `simulate()`, and `color` on `Block` (below, finding 2). Lines 22 to 24,
  the excerpt the movies pin, are unchanged in text and number.
- Re-pin: `node scripts/pin-fixture-project.mjs --python <venv python>`:
  revision `58ed09a` → `4619b17056c4c82081c665ddc7f12af01fd450ca`, documents
  `minimal` and `tour` changed; `node scripts/pin-resolved.mjs minimal tour`.
  Reviewed: in all four files only `model.readiness` ("Fixture export written
  by hand; nothing is simulated." → "Exported by machinome export; the beam
  tips on its pivot through the loop.") and `model.sourceRevision` changed.
  The invalid fixtures were not re-pinned (design D1; they already carried
  older revisions, `99219d3` and `6aebe87`).

## Red

**Pure, before the gate and the key existed** (`npx vitest run --project
pure test/memo.test.mjs`):

     × in this repository, every read of every slow test is declared and the stage is keyed for the browser tests
     × unset, the layer is skipped by name; a path with no file is refused naming it
     × only the viewer layer reaches the selected bundle, named by its variable
     × a selected file is keyed by its bytes under its variable, never by its path
     × the memo report lists a skipped test by its note, and counts it neither passed nor run
    Error: ENOENT: no such file or directory, scandir '.../test/viewer'
    Error: Cannot find module '/test/support/viewer-bundle.mjs' imported from .../test/memo.test.mjs
    TypeError: selectedInputs is not a function
    AssertionError: other bytes miss   ('memo' !== 'ran': the bundle's bytes were not in the key)
    AssertionError: Expected values to be strictly deep-equal:
    -   'Skipped, no viewer bundle selected: 2',
    -   '  skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > the canvas fills its box',
    -   '  skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > the tour renders'
          Tests  5 failed | 21 passed (26)

**The layer on the hand-written export** (the fixture project, documents and
pins at the base content, the real bundle, `VIDEOMAKER_TEST_COLD=1 npx
vitest run --project viewer`): every test fails, because the real viewer
refuses the hand export outright:

    Error: page.evaluate: Error: /model/manifest.json declares document version 4, which this viewer does not render; it renders versions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13. The document is written to a schema this build cannot read: refusing it rather than rendering part of a machine it does not understand.
    Error: page.evaluate: Error: View opening.wide in shot hook: the viewer did not mount: /model/manifest.json declares document version 4, ...
          Tests  6 failed (6)
       Duration  9.29s (tests 84%, setup 8%, transform 6%, import 2%)
    Test memo: 0 passed from the memo, 6 run

**The canvas wait disabled** (`if(resized)` → `if(false&&resized)` in
`stage/runtime.tsx`, local and reverted with `git checkout`):

     × a view's canvas fills its box on a fresh mount, after a change of set, and when the view returns
    AssertionError: every frame is posed, its canvas its box's size
    +   'balance.mill in source: canvas 435.0×288.0 in a box 281.6×244.8',
    +   'opening.wide in hook: Viewer canvas does not fill its view: opening.wide in hook at 1.22 s (canvas 282.0×245.0, box 435.2×288.0)'

and in the whole layer, the A-B-A test and the command line fail too
(`Tests 3 failed | 3 passed (6)`; the command line's preview: `Highlight did
not restore exactly: source cues[1].actions[0] at 7.97 s`).

**The wait only on a fresh mount** (the leased host's move and a changed box
no longer count as a resize; local, reverted): the canvas and A-B-A tests
fail with `Viewer canvas does not fill its view: opening.wide in hook at
1.22 s (canvas 282.0×245.0, box 435.2×288.0)`.

A probe with the wait disabled, posing hook, source, hook: `["hook","ok",
435,288,435.19,288]`, `["source","ok",435,288,281.59,244.80]`, then the
refusal above. The fresh mount fills without the wait on this bundle; the
change of set leaves the canvas larger than its box (which the renderer does
not refuse, finding 1) and the return leaves it smaller.

**The gate** (the layer alone):

- `VIDEOMAKER_VIEWER_BUNDLE=<scratch>/no-such-viewer.js`: `Tests 6 failed
  (6)`, `Error: The selected viewer bundle <scratch>/no-such-viewer.js does
  not exist (VIDEOMAKER_VIEWER_BUNDLE)`.
- `VIDEOMAKER_VIEWER_BUNDLE=test/viewer-double.mjs` (a module, not a
  viewer): `Tests 6 failed (6)`, `Error: The selected viewer bundle
  .../test/viewer-double.mjs does not define MachinomeViewer
  (VIDEOMAKER_VIEWER_BUNDLE)`.
- An API 27 viewer double written to a scratch file, the API test: `Error:
  The selected viewer bundle <scratch>/api27.js declares Viewer API 27; the
  fixture movie needs 28 (VIDEOMAKER_VIEWER_BUNDLE)`.

## Green

- **The layer cold** (`VIDEOMAKER_TEST_COLD=1 npx vitest run --project
  viewer`, 21:22, load 22.65):

      ✓ the bundle declares the Viewer API the tour needs, read from a mounted instance 1704ms
      ✓ a view's canvas fills its box on a fresh mount, after a change of set, and when the view returns 1191ms
      ✓ posing A, then B, then A gives identical pixels across a camera move, a ghosted highlight, a hidden layer and a leased instance 1737ms
      ✓ a label's target is on screen through the real partOnScreen and project, and its text inside the frame 1209ms
      ✓ the tour is checked, previewed and rendered with the real viewer 161669ms
      ✓ the memory of one and of two viewer instances is read and recorded 1335ms
            Tests  6 passed (6)
         Duration  171.54s (tests 99%)
      Test memo: 0 passed from the memo, 6 run

- **The key by content**: a warm run filled the store (`Test memo: 0 passed
  from the memo, 6 run`, 173.07 s); the same bundle copied to another path
  under the session's scratch space: `Tests 6 passed (6)`, `Duration 4.30s`,
  `Test memo: 6 passed from the memo, 0 run`.

## The memory, recorded (not asserted)

The page's JavaScript heap from CDP `Performance.getMetrics` (after
`HeapProfiler.collectGarbage`) and the resident memory (`VmRSS`) of
Chromium's process tree from `/proc`, read by Node from the browser PID the
global setup provides. The tour's seesaw, 640 wide:

| run | before the session | one instance | two instances |
|---|---|---|---|
| layer cold, 21:22, load 22.65 | Chromium 534 MB, 6 processes | heap 3.9 of 4.3 MB; Chromium 540 MB | heap 4.3 of 4.8 MB; Chromium 545 MB |
| whole suite with the bundle, 21:43, load 21.39 | Chromium 553 MB, 6 processes | heap 3.9 of 4.8 MB; Chromium 558 MB | heap 4.3 of 5.1 MB; Chromium 564 MB |
| first green run, 21:18, load 18.67 | Chromium 536 MB, 6 processes | heap 3.9 of 4.6 MB; Chromium 541 MB | heap 4.3 of 4.8 MB; Chromium 548 MB |

An instance of the fixture's five boxes costs about 5 to 7 MB of Chromium's
resident memory and 0.4 MB of page heap. The sawmill's cost (about 1.5 GB
for six instances before `viewer-instances`) is a property of its model, not
of the fixture; measuring it on *Cut and Advance* remains the orchestrator's.

## The whole suites on the final content

- **Node, with the bundle** (`VIDEOMAKER_VIEWER_BUNDLE=<bundle> npm test`,
  21:43, load 21.39):

       Test Files  31 passed (31)
            Tests  322 passed (322)
         Duration  439.93s (tests 97%, import 1%, transform 1%, environment 1%)
      Test memo: 100 passed from the memo, 222 run

- **Node, without it** (`npm test`, after the run above):

       Test Files  31 passed (31)
            Tests  316 passed | 6 skipped (322)
         Duration  19.82s (tests 65%, import 15%, transform 11%, environment 7%, setup 2%, worker 1%)
      Test memo: 115 passed from the memo, 201 run
      Skipped, no viewer bundle selected: 6
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > the bundle declares the Viewer API the tour needs, read from a mounted instance
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > a view's canvas fills its box on a fresh mount, after a change of set, and when the view returns
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > posing A, then B, then A gives identical pixels across a camera move, a ghosted highlight, a hidden layer and a leased instance
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > a label's target is on screen through the real partOnScreen and project, and its text inside the frame
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > the tour is checked, previewed and rendered with the real viewer
        skipped, no viewer bundle selected: test/viewer/real-viewer.test.mjs > the memory of one and of two viewer instances is read and recorded

  vitest's default reporter says ` ✓ |viewer| test/viewer/real-viewer.test.mjs
  (6 tests | 6 skipped)`; with `--reporter verbose` each line ends
  `[no viewer bundle selected]`.
- **The first whole run without the bundle**, cold for every slow test the
  new export reaches (21:28, load 23.51): `Test Files 31 passed (31)`,
  `Tests 316 passed | 6 skipped (322)`, `Duration 795.89s`, `Test memo: 0
  passed from the memo, 316 run`, the same six skips. Every browser and
  pipeline test passed on the real export with the double.
- **Python**, `python -m pytest -q` in `python/`: `189 passed in 19.06s`.

A whole-suite `--cold` run was not made; the viewer layer ran cold (above),
and the browser and pipeline tests ran cold in the first run without the
bundle because the fixture project they key had changed.

`openspec archive viewer-integration-layer --yes`: `test-suite: + 1 added,
~ 3 modified`; it archived with 13 of 15 tasks (0.2, the orchestrator's
review, and 6.1, the pilot's, are not claimed). The spec file's layout was
checked (no blank line lost); `openspec validate --specs --strict`: `Totals:
16 passed, 0 failed (16 items)`.

## Findings

1. **The renderer does not refuse a canvas larger than its box.** Its check
   (`Viewer canvas does not fill its view`) requires the canvas to be at least
   98 % of the box. With the wait disabled, the change of set left the real
   viewer's canvas at 435×288 in a 282×245 box and `preview` passed that
   frame; the canvas overflowed its slot. The layer's own assertion (the
   canvas is its box's size, within a pixel) catches it; the stage's wait
   prevents it today. Smallest correction, not made here (the renderer is
   out of this cycle): refuse a canvas more than a pixel larger than its box.
2. **The real viewer tints and dims only parts that declare a colour**, as
   `docs/FORMAT.md` says. The first preview of the tour on the exported
   seesaw, before the block declared one, refused `Highlight did not reach
   the pixels: rise cues[2].actions[2] at 15.28 s` (`highlight(Seesaw.stand,
   others="dim")`: no pixel changed); `ghost` changed pixels. Preview's proof
   caught it, as it would for a film.
3. **The hand-written export was not a document any real viewer reads**: its
   `"version": "4"` is a string, and the viewer refused it ("declares document
   version 4, which this viewer does not render"). Every fixture movie had
   been proved only against the double.
4. **vitest runs each project in its own worker process** (measured: two
   PIDs), and loads a global setup once per project with its own module
   instance; the main process's `globalThis` is shared. So the run keeps one
   Chromium for both projects, but the viewer project has its own asset
   server; the `test-suite` requirement "One browser serves every browser
   test of a run" was restated to one asset server per project.
5. **On this bundle a fresh mount fills without the wait**; the failures the
   film met are the change of set (canvas too large) and the return (canvas
   too small). The fresh-mount case is asserted and could not be shown red.
6. **ADR-007 holds on the real viewer**: one instance served
   `balance.mill` (ghosted highlight, ground hidden), `opening.wide` (mid
   move) and `balance.mill` again, A's pixels identical, and B's equal to B
   on a fresh instance.
7. **The fixture's cameras frame the seesaw small** (written for a hand
   export with no geometry); the storyboard is legible but the model fills a
   fraction of each view. Not changed: the cameras are in every fixture
   document and their pins, and nothing needs a larger picture (task 6.1).
8. The CDP session works over the shared Chromium reached with
   `chromium.connect`; the browser's resident memory before the session
   (about 535 to 553 MB) is the shared browser's, grown by the suite before
   it.

## What was not done, and why

- No scenario take, no running or clocked fixture, and no bank checks: the
  brief's cut; `AGENTS.md` now says only the first sentence of layer 6
  exists.
- No change to the viewer, the stage, the renderer or a refusal of the tool;
  finding 1 is recorded, not fixed.
- No threshold on memory; the sawmill's memory on *Cut and Advance* is the
  orchestrator's.
- The invalid fixtures keep the old readiness sentence and older revisions;
  each is refused before either is read.
- `docs/architecture-overview.md` does not list the test layers; unchanged.
- A whole-suite `--cold` run was not made (the brief does not ask it); the
  viewer layer ran cold, and the other slow tests ran cold once because the
  fixture changed.
- The red runs of the canvas wait were local edits of `stage/runtime.tsx`,
  reverted with `git checkout -- stage/runtime.tsx` before the green runs.
