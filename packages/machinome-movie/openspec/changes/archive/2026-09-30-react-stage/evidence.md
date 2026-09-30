# Implementation evidence

## Authority and scope

The third cycle of the react-stage campaign (`workflow/ongoing/react-stage-campaign/plan.md`,
cycle S), on branch `react-stage-runtime`, cut from `react-stage` at
`502ef71`. Planning commit `72e221c`, made for the orchestrator's review
(task 0.2, not claimed here). Nothing was pushed or published; no network or
paid request was made; no `.env` was read; the runs had no speech key. The
Leonardo spec was read; nothing was written in the Leonardo repository, the
framework, the viewer, the studio, the primary checkout or another worktree.
`node_modules` is the campaign worktree's install; nothing was installed.
Parts of the work were delegated to subagents under written briefs (the spec
deltas, the stage runtime, the pure tests, the slow tests, the manual pages);
every result was reviewed and integrated here.

Environment of every run: Linux, Node v24.11.1, vitest 5.0.3, Playwright's
Chromium 151.0.7922.34, `ffmpeg version 6.1.1-3ubuntu5`, `git version 2.43.0`,
esbuild 0.28.2, TypeScript 7.0.2, React 19.3.0, jsdom 30.1.1, Python 3.12.3
with pytest 9.1.1.

## Base

`npm test -- --cold` on `502ef71`, before any change: **23 files, 198 tests
collected: 190 passed, 8 failed, and 2 files failed to load**
(`test/movie-document.test.mjs`, `test/movie-pipeline.test.mjs`), 315.5 s
(5 min 16 s wall). Every failure has one cause: `src/schema.mjs` reads
`schema/machinome-movie-0.1.json` at import, which `declarative-stage`
removed; the two files import it, and the eight failing `review-pack` tests
spawn the command line, which imports it too (`review MANIFEST.json must
succeed without author sources: ... ENOENT ... machinome-movie-0.1.json`).
Python suite at the base: 186 passed.

## Red and green, pure layers (2, 3, 4 and the ported pure tests)

The code of D1–D4 was written before its layer-2 and layer-3 tests, so their
first run is the honest record of what they caught:

- `test/movie-document.test.mjs` (layer 2, rewritten for 0.2): all its tests
  passed on first run. Before the implementation, the same checks ran by hand
  over the fixtures (a scratch script): the first resolution of `tour` was
  refused three times on rules of the YAML formats the document breaks (an
  emphasis hold past the cut, a 0.6 s dissolve out of a 0.5 s shot, an
  incoming dissolve overlapping the last shot's fade-out) and on an entrance
  and exit overlapping a 0.5 s cue; each became a recorded reading (design
  D2.3, findings 3–6). All 61 invalid fixtures were refused with their words
  on the first complete run.
- `test/timeline.test.mjs` (layer 3, new): 2 of 17 failed on first run, both
  mistakes of the test (a float comparison, an expected time).
- The ported `workflow` pin `lens03Rolled` failed red at 2.5 s (`[1,0,1]` where
  a unit up `[0.7071,0,0.7071]` is pinned; `camera` and `keyframes` too): after
  a move that changes up, the held up was the preset's raw vector. Fixed in
  `viewState`: in a shot where a move changes a view's up, up is a unit vector
  throughout (the YAML rule, applied to documents too; readback compares unit
  directions, so no picture changes).
- `stage/stage.test.tsx` (layer 4, jsdom) and `test/stage-types.test.mjs`
  (`tsc --noEmit` over `stage/` and over the generated `movie.d.ts`) were
  written with the runtime; no red was recorded before it existed.

Green: `pure` 16 files, 149 tests, 2.6 s; `stage` 1 file, 15 tests, 1.6 s.

## Red and green, slow layers (5, 8, 9)

Browser and pipeline tests moved to `test/browser/` (render 17,
source-only-browser 8, browser-seam 3, stage 9 new) and `test/pipeline/`
(incremental-rendering 20, movie-pipeline 7, review-pack 18, pictures 16,
speech 5, source-scenes 5); the slow project selects them by directory, and
the verdict key also reads `stage/` and the fixture project. Layer 9 pins are
`test/repository.test.mjs` (pure).

Red recorded while porting, each fixed in the code and green after:

- a YAML mark lost its authored name in refusals (`#<annotation>` had become
  `pawls.view cues[0].actions[0]`): the ring and arrow-to-the-cut tests red;
- a picture proof sample at opacity 0 read an undrawn clip frame
  (`undefined !== 3`);
- enlargement was measured at the output width, so `render --width 3840`
  let an over-enlarged still through (the refusal test red);
- a displaced source panel in the `source-only` set was accepted (its slot
  is now checked against the paper geometry);
- the viewer-API probe pose was counted in `framesChecked` (seven
  incremental tests off by one);
- a shot's cache key did not bind its resolved measured instants: a
  sub-frame onset change reused stale frames (now bound through the frames'
  element states and the take's checksum);
- `check` refused a document without takes for its missing take before
  type-checking its stage (`check refuses a stage module that does not
  type-check before it asks for the takes`: red, the output named the take;
  green after `check` bundles from the unresolved document first).

The new stage tests (readback, A-B-A replay, a set without `Chrome` draws no
masthead, picture-only captures hide chrome, two views two instances, an
instance kept across a cut, the `Tally` lit, the refusals at mount, the
tour's proofs, `check` type-checking) passed on their first run, because the
runtime existed; each non-vacuous one has a control that fails: a viewer that
ignores the field of view is refused naming `tip.close`, a drifting viewer
breaks A-B-A, the playbill band does show its masthead, live chrome pixels
differ from a picture-only capture.

By hand before the tests (scratch scripts over the fixture movie and the YAML
fixture episode): the tour's `check`, `preview`, `render` and `review` pass;
567 frames at 1280×720 in about two minutes cold; a second render captured
nothing and reused 567. Reading the first storyboards found the review plan's
emphasis labels without a line (fixed: the line is counted in the excerpt)
and the contact sheet out of order past a hundred samples (names now have
three digits). The preview proofs first failed on: the viewer double knowing
only `Feed/Pawl` (it now knows the seesaw's parts), the fixture still being
enlarged 25× in the tour's first plate (the template's plate is now a
stamp), a highlight in the double's colour hiding a drawn ring (the double
tints), overlapping entrance and exit checks with no instant to compare
(recorded as skipped), and the wipe proof comparing two sets' different
chrome (both sets' chrome is masked).

## Contract findings

For the orchestrator; the reading taken keeps both runtimes able to agree
(the Python side never produces frames or resolved documents). The schema was
not edited. `docs/movie-document.md` marks each where its wording changed.

1. **A picture's rectangle needs the slot's box**, which only the stage
   knows. Reading: the frame carries the picture's `view` (`center`, `zoom`)
   and `fit`; the stage computes the rectangle (CSS arithmetic over its box)
   and reports it as `drawn` with `natural`; the renderer checks it, the
   enlargement and the framing against the reported box. Correction: say so.
2. **A picture state's `kind` collides with the element's `kind`.** Reading:
   `media` (`still` or `clip`).
3. **The resolved document needs word times the contract does not name.**
   Reading: an `emphasize` action gains `until` (phrase end plus hold) and
   each word an `at`; a spoken `reveal` gains `onsets`.
4. **An emphasis hold past the shot's end** (the Python side emits it):
   ends with the shot.
5. **A join longer than the shot it leaves** (the tour's 0.6 s dissolve out
   of a 0.5 s shot): accepted; the outgoing shot continues.
6. **An incoming join overlapping a fade-out** (the tour's last shot):
   accepted; the join is drawn until it ends.
7. **An entrance and an exit overlapping in a short cue** (the tour's
   picture): accepted; the opacity is the lesser of the two.
8. **A ring's `padding`** is a fraction of the view's box width, like
   `offset` and `place`.
9. **Viewer API 28** for a view mark, a highlight, or a camera whose lens or
   up differs from the view's own.
10. **The YAML sets' slots** carry indexed positions (`top-2` … `top-8`,
    `plate`, `full`) beyond the contract's list, so several overlays or
    pictures of one position in one shot stay separate elements; `plate` is
    the model stage's box and `full` the frame (the old `area`).
11. **Chrome across two sets in a join**: the live chrome is the incoming
    set's; both sets' chrome is masked in the proofs.
12. **`window.film`** also has `project(key, points)` and `views()`;
    `viewer` and `apiVersion` are the first mounted view's, and the renderer
    poses the film's first view frame before anything is captured, so a
    viewer below the movie's API is refused first.
13. **Up after an up-changing move** is a unit vector throughout that shot,
    as in YAML.

## Final runs, on the final content (after archive)

- **Cold**: `npm test -- --cold` with `.test-memo/` removed: **28 files, 278
  tests, 278 passed, 576.4 s** (9 min 37 s wall), "0 passed from the memo,
  278 run". Slow files: incremental-rendering 172.8 s (20), movie-pipeline
  171.7 s (7), render 113.6 s (17), stage 52.8 s (9), review-pack 30.7 s
  (18), source-only-browser 21.2 s (8), pictures 7.1 s (16), browser-seam
  1.2 s (3), speech 0.6 s (5), source-scenes 0.4 s (5). 278 = 149 pure +
  15 stage (jsdom) + 108 slow + 6 repository pins.
- **Warm, filling the memo** (`npm test`): 278 passed, 584.1 s, 0 from the
  memo (the cold run writes nothing).
- **Warm**: `npm test`: **278 passed, 9.0 s**, "108 passed from the memo,
  170 run".
- **Python**: `python -m pytest` in `python/`: **186 passed**, 10.9 s, after
  the fixture project's revision was re-pinned (`211efd07…` → the tour's
  template and stylesheet changed it) and the documents re-evaluated.

`check` on the fixture tour prints:

    Tour: 3 chapters, 9 shots, 18.9s; model 20s
    Viewer API 28 required for highlight (shot source), camera up/field of view (shot push), marks (shot push), marks (shot rise), highlight (shot rise), camera up/field of view (shot rhythm), highlight (shot invitation); <bundle> declares API 28
    Stage: bundled <root>/_build/stage/stage.js (sha256 9bec793ded70) from stage.tsx; types checked
    Picture still tip.plate (still plate): allowance 1.5×; enlargement checked against its slot's box at preview and render

## Not done, and why

- Layer 6 (the real viewer) has no test: it needs a selected real bundle;
  memory with several viewer instances is unmeasured (wart).
- The film itself (task 4.1): the campaign's film step.
- The orchestrator's review of the planning commit (task 0.2) and of the
  contract findings above.
