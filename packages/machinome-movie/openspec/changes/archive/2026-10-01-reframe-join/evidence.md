# Implementation evidence

## Authority and scope

Cycle 3 of Videomaker's curta-video campaign
(`workflow/ongoing/curta-video-campaign/plan.md`), on branch `reframe-join`
(worktree `WTs/reframe-join`), cut from `curta-video` at `ad8f444`, under
the orchestrator's ruling quoted in the proposal, for the Curta film
*Addition*, chapter 4. Planning commit `75fe3e6`. Nothing was pushed or
published; no network or paid request was made; nothing was installed.
Integration into `curta-video` is the orchestrator's. Another agent ran the
campaign's spike in its own worktree at the same time; durations below are
not comparable across runs.

Environment of every run: Linux, 16 cores, Node v24.11.1, vitest 5.0.3,
Playwright's Chromium, `ffmpeg version 6.1.1-3ubuntu5`, the workspace venv's
Python for pytest; the viewer layer with
`VIDEOMAKER_VIEWER_BUNDLE=/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`
(API 28), passed in the environment only.

## Red, innermost first

**Layer 1** (pytest, `python/`). The tests first, before `Reframe` existed:

    E   ImportError: cannot import name 'Reframe' from 'machinome_movie' (…/python/machinome_movie/__init__.py). Did you mean: 'Frame'?
    !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!

Then with the class alone, no refusal, and the tour not yet changed (the
behaviour's red):

    E       Failed: DID NOT RAISE MovieError
    FAILED tests/test_declarations.py::test_a_reframe_without_a_view_in_both_shots_is_refused_naming_both
    FAILED tests/test_declarations.py::test_a_chapter_that_opens_with_a_reframe_is_refused_by_its_movie
    FAILED tests/test_evaluation.py::test_a_title_in_a_slot_and_the_end_of_the_narration
    FAILED tests/test_evaluation.py::test_a_reframe_from_the_project_set_into_its_split
    4 failed, 190 passed in 14.63s

**Layer 2** (vitest, `test/movie-document.test.mjs`), the Python side green,
the documents re-pinned, `src/movie.mjs` unchanged:

    AssertionError: reframe-without-a-shared-view.json: refused for another reason: "chapter only, shot words, transition.kind: 'reframe' is not a transition; use dissolve, fade, wipe or slide" does not name "whole"
          Tests  15 failed | 7 passed (22)

(the other fourteen: the re-pinned tour's `reframe` refused as an unknown
kind.)

**Layer 3** (vitest, pure, `test/reframe.test.mjs`). An order slip,
recorded as such: the timeline's reframe branch (`reframeAt`) was written
before this test. The red was taken by removing the branch from
`transitionAt` (the frame then falls through to the composed joins' path)
with `reframeBoxes` not yet written, and the branch restored after:

    × a reframe draws the incoming shot live: its set, slots and elements, and nothing of the outgoing shot
    × the moving view's box runs from its outgoing slot's box to its incoming slot's by the eased progress
    × a reframe whose boxes were not measured is refused naming the shot; no box is guessed
    × the boxes come from the measured layout, as fractions of the frame
    × a reframe slot sized by what it holds is refused naming the shot, the view, the set and the slot
    AssertionError: nothing of the outgoing shot is posed
    TypeError: Cannot read properties of undefined (reading 'drive.view')
    AssertionError: Missing expected exception.
    TypeError: reframeBoxes is not a function
          Tests  5 failed | 3 passed (8)

**Layer 4** (vitest, jsdom, `stage/stage.test.tsx`), before the stage
changed:

    × every element but the moving views is drawn at the progress as opacity, and none at its end or without one
    × the moving host's inline box is the frame's, in pixels of the page, to the layout's 1/64 pixel, relative to its element
    AssertionError: expected '' to be '0.4' // Object.is equality
    TypeError: reframeHost is not a function
          Tests  2 failed | 18 passed (20)

**Layer 5** (Chromium, the viewer double, `test/browser/reframe.test.mjs`,
cold), the stage changed, the renderer not yet:

    × a reframe moves the view from its outgoing slot's box to its incoming slot's, fades the rest in, and ends on the incoming frame 1043ms
    × with a viewer that sizes its canvas late, every frame of a reframe waits for its canvas; the cost per frame 416ms
    Error: Shot question comes in by a reframe whose slot boxes are not measured; check and every browser session measure them on the stage
          Tests  2 failed (2)
    Test memo: 0 passed from the memo, 2 run

**Layer 8** (the command line, `test/pipeline/movie-pipeline.test.mjs -t
"the tour is checked|reframe into a slot"`, cold), the renderer's session
changed, `check` and `preview`'s proof not yet:

    × the tour is checked, previewed, rendered twice and reviewed from the command line 1770ms
    × check refuses a reframe into a slot sized by what it holds, before any take exists 1552ms
    AssertionError: The input did not match the regular expression /^Reframe into question: opening\.wide from playbill stage 870\.4×576 at 64,86\.4 to playbill-split right 563\.2×489\.6 at 652\.8,158\.4$/m. Input: 'Layout playbill at 1280×720: …'
    AssertionError: The input did not match the regular expression /^Shot question comes in by a reframe that moves opening\.wide into slot headline of set playbill-split, which is sized by what it holds; a reframe moves a view between slots whose boxes stay put$/m.
          Tests  2 failed | 9 skipped (11)

Green after each step: layer 1, `195 passed`; layer 2, `Tests 22 passed
(22)`; layer 3, `Tests 8 passed (8)`; layer 4, `Tests 20 passed (20)` and
`tsc --noEmit -p stage/tsconfig.json` silent; layer 5, `Tests 2 passed (2)`,
`Test memo: 0 passed from the memo, 2 run`; layer 8, `Tests 2 passed | 9
skipped (11)`, `Test memo: 0 passed from the memo, 2 run` (the tour's full
check, preview, render, cached second render and review, 140.7 s).

**Layer 6** (the real viewer) was written after the renderer change and
passed on its first run; it is not a red-first proof.

## Mutations, each reverted at once (layer 5, cold)

- **The host ignores the frame's box** (`reframeHost` given no box): both
  tests fail on the renderer's per-frame check, `Reframe box differs from
  the timeline: opening.wide in question at 2.43 s (drawn 326.4, 79.2,
  281.6, 244.8, the frame's 32.0, 43.2, 435.2, 288.0)`.
- **No fade** (`Slot` writes no opacity): both fail, `Reframe fade differs
  from the timeline: opening.title in question at 2.43 s (opacity 1
  instead of 0)`.
- **No snapping to 1/64 px**: the test still passes. The fixture's boxes at
  640 px land on the layout unit anyway, so the end proof does not show the
  snap is needed; it is kept as a guard (finding 3).

## The pins

`node scripts/pin-fixture-project.mjs --python <venv python>`: revision
`4619b17…` → `8e173754dc8382ba6064dd6dfd7c8ff363f52aa2`; `minimal` and
`tour` re-evaluated. `node scripts/pin-resolved.mjs minimal tour`; the
diffs, reviewed: both carry the new `sourceRevision`; `tour`'s `question`
changes `set` (`playbill` → `playbill-split`), `places` (`stage`/`aside` →
`right`/`left`, `headline` kept) and gains `transition: {kind: reframe,
duration: 0.8}`; every time is unchanged (`question` still ends at
2.3333 s of its chapter). No take fixture changed.

## The cost per frame

A reframe resizes the view's host on every frame, so the canvas wait runs
on every frame. Median time to pose one frame of the tour's `question` at
640 px, over the join's 24 frames and over the 24 frames just after it
(whose title is fading out, so each of them repaints too):

- late-canvas double: 99.9 ms in the join, 66.8 ms after it (100.0 and 66.6
  in an earlier run);
- the real viewer (API 28): 100.0 ms in the join, 66.5 ms after it.

The join adds one canvas wait (two animation frames, about 33 ms) to a
frame that repaints anyway (about 67 ms). Machine loaded by the parallel
spike; durations are indicative.

## Suites on the final content

The whole Node suite, with the viewer bundle selected
(`VIDEOMAKER_VIEWER_BUNDLE=… npm test`, 01:27 to 01:41, load 14.5 rising
to 18.4 with the spike running in its worktree). The runtime changed, so
every slow key is new: nothing came from the memo, so the slow and viewer
layers ran cold; the viewer layer ran (`✓ |viewer|
test/viewer/real-viewer.test.mjs (7 tests) 144790ms`):

     Test Files  34 passed (34)
          Tests  341 passed (341)
       Duration  800.96s (tests 99%, import 1%)
    Test memo: 0 passed from the memo, 341 run

The Python suite (`env -C python <venv python> -m pytest -q`):

    195 passed in 15.50s

`openspec validate --specs --strict`: `Totals: 16 passed, 0 failed (16
items)`.

## Findings

1. **The contract's "box as fractions of the frame" needs a measured
   layout in the timeline.** The frame is a pure function of the resolved
   document and video time, and a slot's box is the stage's; so the
   reframe's slot boxes are measured on the stage (ADR-009's probe) and
   attached to the film as data, by `check` and by each browser session.
   `frameAt` refuses a reframe frame of a film that carries none. A film's
   frames during a reframe therefore depend on the session that measured
   them (its width), as its pictures' rectangles already did; the shot
   cache keys the frames, boxes included.
2. **A reframe through a slot sized by what it holds is refused** (it has
   no box before its content is drawn). The tour's `headline` is such a
   slot; the refusal is pinned at layer 8 with the view moved there.
3. **The 1/64 px snap is not proved necessary by the fixture** (mutation
   above). It is kept so a measured box comes back to the layout unit at
   any width; a film whose boxes do not land on it would show whether it
   matters.
4. **React leaves `style=""`** on an element box whose fade ended; the
   runtime removes it after each commit so the page's content (which
   decides whether a pose repaints) is the frame's alone. Pixels do not
   depend on it.
5. **Python refuses no transition on the film's first shot**, the Node
   resolver does (`the first shot comes in from nothing`); a reframe there
   is refused the same way, after the takes, by Node only. Unchanged by
   this cycle; the smallest correction would be the same rule in
   `check_document` and an invalid fixture.
6. **`openspec archive` refused the movie-document delta** whose scenario
   "No picture, no browser" had been renamed in the planning commit
   ("No picture, no reframe, no browser"): the CLI keeps every scenario
   name. The delta was renamed back, its text kept, after the planning
   commit; the archive also dropped a blank line before `## Requirements`
   in `react-stage`, restored by hand. The `shot-transitions` purpose was
   amended to name the reframe.
7. **The schema was not changed** (design D1): its `join.kind` is a
   string both runtimes check semantically.

## What was not done, and why

- No change to the four composed joins, the lease, the viewer, the YAML
  formats or the schema (out of scope, or not needed: D1).
- No reframe of a source, title or picture, and none across chapters (the
  ruling's "Out").
- No layer 6 red: the real-viewer test was added after the renderer
  change, to measure the real canvas's cost and confirm the moving box
  fills; it is evidence, not a red-first proof.
- The orchestrator's ratification of the planning commit (task 0.2) and
  the integration are the orchestrator's.
- The film (cycle 4) and its real join are not made here; the per-frame
  cost there is the Curta's, unmeasured.
