## Context

Every browser test (layer 5) and pipeline test (layer 8) draws its views
with the viewer double (`test/viewer-double.mjs`): a flat canvas, a pinhole
`project`, a `partOnScreen` that invents rectangles. The fixture export
(`python/tests/fixtures/project/export/seesaw/manifest.json`) was written by
hand, with the part names and no meshes ("nothing is simulated"), enough for
the double and not for a real viewer. The stage's contract with the real
viewer (`stage/runtime.tsx`, `stage/marks.ts`) is exercised only by films.

*Cut and Advance* met two failures of that contract on its first render
(wart 1 of "Cut and Advance, version 2"): the real viewer sizes its canvas on
its own animation frame, and shrinks a detached host's canvas to 0×0. The
stage now waits for the canvas, bounded, when a view is mounted, placed again
or resized; the double's `lateCanvas` imitates the behaviour. `viewer-instances`
(ADR-007) then made view elements lease instances, and `pose-repaints`
(ADR-004 amended) made a pose skip the repaint when only canvases changed.
Each was proved on the double only.

The slow project's global setup (`test/support/toolchain.mjs`) launches one
Chromium server per run and provides its endpoint; `test/support/stage.mjs`
connects to it once per worker and makes one asset server.

A probe before this proposal: vitest 5 runs each project's global setup in
the main process with its own module instance, and each project's tests in
their own worker process (measured with two projects of `isolate:false`: two
PIDs; `globalThis` of the main process is shared by the two setups).

A second probe, with the real bundle on the exported seesaw: `check` reads
its banner (API 28), and `preview` of the tour first refused "Highlight did
not reach the pixels: rise cues[2].actions[2]": the real viewer tints and
dims only parts that declare a colour (`docs/FORMAT.md` says so), and a
freshly exported block has none. With a colour declared on the block, the
tour previews on the real viewer, every proof passing (56 s at 640 wide).

## Goals / Non-Goals

Goals: the layer `AGENTS.md` describes, for the posed fixture that exists;
never passed without a bundle, never assuming the bundle's API, never naming
a bundle's path in the repository or in a memo key; the memory of one and
two instances measured. Non-goals: those of the proposal.

## Decisions

### D1. The real export replaces the hand-written one

The seesaw is exported by the framework's own command, from the fixture
project:

    machinome export seesaw -o export/seesaw --fps 30 --frames 600 --no-widget

`--no-widget` keeps the viewer out of the repository; the manifest and its one
mesh are committed. For the export to be a posed loop the documents accept
(`animation.loop` 20, as `Playground` declares), the root declares
`time = Time(loop=20)`; without it the export carries no `loop` and every
fixture movie is refused ("Model duration differs"). The beam turns on its
pivot, `20 - 4·|t - 10|` degrees about y (level rising at the `rise` mark,
top at `top`, level falling at `fall`), and the blocks declare a colour so a
highlight can tint and dim them. Lines 22 to 24 of `models/seesaw.py`, the
excerpt the fixture movies pin, keep their text and numbers (the colour
replaces a blank line; the import of `Time` replaces another).

The fixture movies keep their meaning: the part names are those the hand
export listed; cameras, layers and marks are unchanged. Only
`model.readiness` ("Exported by machinome export; the beam tips on its
pivot through the loop.") and `model.sourceRevision` change in the
documents, re-pinned with `scripts/pin-fixture-project.mjs` and
`scripts/pin-resolved.mjs` and reviewed. The invalid fixtures are left as
they are: each is refused before the readiness or the revision is read, and
they already carry older revisions.

Alternative: commit the real export beside the hand-written one under
another name. Rejected: the real export matches the manifest every document
was written against, so two exports would be two fixtures for one take.

### D2. Layer 6 is the `viewer` project

`vitest.config.mjs` gains a project `viewer`: `test/viewer/**/*.test.mjs`,
`sequence.groupOrder` 2 (after the slow project), `fileParallelism:false`,
`isolate:false`, the same global setup and setup file as the slow project.
The pure project excludes `test/viewer/`.

**One Chromium.** `toolchain.mjs` keeps the run's Chromium, toolchain record,
memo store and cold directory on the main process's `globalThis`, counted by
the setups that use it: the first setup of the run launches and records,
every later one provides the same, and the last teardown closes. So `npm
test` with a bundle launches one Chromium for both projects.

**An asset server per worker.** vitest runs the viewer project in its own
worker process, so it cannot reach the slow worker's in-process asset
server; it makes its own the same way (`sharedStage()`), once for all its
tests. The `test-suite` requirement is restated accordingly: Chromium once
per run, one asset server per project worker. Alternative: put `test/viewer/`
in the slow project. Rejected: the layer could not be selected or skipped as
a project (`--project viewer`), and the gate would sit among tests that need
no bundle.

### D3. The gate

`VIDEOMAKER_VIEWER_BUNDLE` selects the bundle by path. A layer 6 test is
declared with `viewerTest(name, fn)` (`test/support/viewer-bundle.mjs`):

1. Unset or empty: the test is skipped through vitest's context with the note
   **"no viewer bundle selected"**, before the memo is consulted, so a skip is
   neither recorded nor reported as a pass.
2. Set to a path with no file: the test fails, **"The selected viewer bundle
   <path> does not exist (VIDEOMAKER_VIEWER_BUNDLE)"**.
3. Otherwise the memo decides (D4); when the body runs, the bundle is first
   loaded into a blank page of the run's Chromium, and a file that does not
   define `MachinomeViewer` with a `mount` function fails, **"The selected
   viewer bundle <path> does not define MachinomeViewer
   (VIDEOMAKER_VIEWER_BUNDLE)"**. The path is resolved against the working
   directory and printed absolute.

The memo reporter lists skipped tests by their note after its line: `Skipped:
<n>, no viewer bundle selected`, then each test by name. Its `Test memo`
line is unchanged and never counts a skip as passed or run.

`npm test` runs the project in both cases: unset, it reports the skips.

### D4. The selected bundle is keyed by content, never by path

A layer 6 test's verdict key covers, besides what `reach.mjs` computes for
any slow test, the content of the selected bundle under the name of the
variable: `selected\0VIDEOMAKER_VIEWER_BUNDLE\0<sha256>`. `reach.mjs`
declares which slow tests reach a selected file (`SELECTED`: the files under
`test/viewer/` reach `VIDEOMAKER_VIEWER_BUNDLE`) and `selectedInputs(file)`
names them; `slowTest` passes them to the memo. The same bundle at another
path hits; another content misses. A path relative to the repository would
put the neighbouring checkout's layout into the key and differ between two
worktrees of one content.

### D5. What the layer proves

On the tour (API 28: marks and highlights), at 640 wide, through
`browserSession`, `preview` and `render` of `test/support/stage.mjs` and the
command line:

1. **The API, asserted.** `stageConfig(film).viewer.required.api` is 28; a
   session mounts, and `window.film.apiVersion` is at least that; otherwise
   the test fails naming the path, the declared and the required API.
2. **The canvas.** With the real viewer, a view's canvas fills its box on a
   fresh mount (`hook`), after a change of set (`source`, whose view is
   another element leased the same instance) and when the first view returns
   (`hook` again), read from the stage's report.
3. **A, B, A.** A is `balance.mill` in `source` with its highlight standing
   (`others: ghost`) and the ground hidden; B is `opening.wide` in `hook`
   during its move to `near`, on the instance A freed; A again is identical
   to A, and B equals B in a session where B is posed first. One instance
   serves all three (ADR-007).
4. **Marks on the real model.** In `rise`, at an instant where the `Plank`
   label and ring are fully shown, every mark's anchor is inside the view's
   box (the real `partOnScreen`), the label's text is inside the frame, and
   `window.film.project('tip.close', [target])` projects the camera's target
   inside the view's box (the real `project`).
5. **The command line.** `check`, `preview` and `render --width 640` of the
   tour with `--viewer <path>`: each exits 0, `check` names the API the
   bundle declares, preview's pixel replay holds, and `ffprobe` counts 567
   frames at 640×360.
6. **Memory**, recorded: after a frame placing one view, then a frame placing
   two side by side, the page's JavaScript heap (CDP `Performance.getMetrics`,
   `JSHeapUsedSize`) and the resident memory of Chromium's whole process tree
   (the sum of `VmRSS` over the browser process and its descendants, read
   from `/proc` by Node; the global setup provides the browser's PID). The
   test logs both and asserts only that they were read.

### D6. Red first

The canvas cases are the ones the film met: they are run once with the
stage's canvas wait disabled in a local, uncommitted edit of
`stage/runtime.tsx`, where the real viewer must fail them, and the edit is
reverted. The whole layer is run once on the hand-written export (the
fixture project at its base content), where the real viewer has nothing to
draw. The gate's and the key's pure tests are written before their code.

### D7. The refusal words

The three gate messages of D3 name the path and the variable. The skip note
is "no viewer bundle selected". The API assertion names the path, the
declared API and the required API.

## Risks / Trade-offs

- [The real bundle changes under the repository] → its content is in the
  key; a new bundle reruns the layer, and a bundle below the movie's API
  fails it by name.
- [The real viewer renders with the GPU Chromium has, here SwiftShader] →
  the layer proves the contract and the pixel replays in one session, never
  pixels against a stored image.
- [Memory numbers depend on the machine and on what else runs] → recorded
  with the machine's load, not asserted.
- [Two projects keep one Chromium through `globalThis`] → the setups run in
  the main process, which vitest keeps for the whole run; the last teardown
  closes it, whichever project ends last.

## Migration Plan

The fixture export and project change, so every browser and pipeline test
runs once cold. Without `VIDEOMAKER_VIEWER_BUNDLE` nothing else changes.
Rollback is reverting the commit.

## Open Questions

None.
