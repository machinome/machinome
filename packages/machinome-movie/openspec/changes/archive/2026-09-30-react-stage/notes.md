# react-stage — working notes (for a successor)

Planning commit: 72e221c. Base suite (502ef71, cold): 23 files, 198 tests,
190 passed, 8 failed, and 2 files that fail to load (`movie-document`,
`movie-pipeline`), 315.5 s; every failure is the removed
`schema/machinome-movie-0.1.json` (read by `src/schema.mjs` at import, so the
command line fails too: the 8 `review-pack` CLI tests).

## Done
- `src/schema.mjs` (0.2 keywords), `src/text.mjs`, `src/style.mjs`,
  `src/movie.mjs` (port of `check_document`: all 61 invalid fixtures refused
  with their words; `resolveMovie`; `loadMovie`), `src/chapters.mjs`,
  `src/words.mjs` (film shape; YAML word timing), `src/code.mjs`
  (`sourceState`), `src/pictures.mjs` (media probe for movies; `extractClips`
  with uses), `src/timeline.mjs` (the frame), `src/episode.mjs`
  (`episodeFilm`, the YAML conversion).
- `fixtures/resolved/{minimal,tour}.json` pinned (reviewed by hand: anchors
  on the 30 fps grid, emphasis onsets unsnapped, hold clamped at the cut).

- `stage/` (runtime, shipped sets and elements, `stage/stage.test.tsx`),
  `src/stage-build.mjs` (+ `buildFilmStage`), `test/stage-types.test.mjs`,
  the tour's `stage.tsx`/`stage.css` (plate slot a 3.9 % stamp: the fixture
  still is 48×32 with upscale 1.5).
- `src/render.mjs` on the stage (every proof masks both sets' chrome;
  overlapping entrance/exit checks recorded as skipped), `src/shot-cache.mjs`
  (no progress), `src/review-samples.mjs` (element states), `src/pixels.mjs`
  (proveMark masks chrome), `bin/videomaker.mjs` (check prints the bundle),
  `src/film.html` (three layers); `src/film.js` deleted.
- Fixture project re-pinned (revision via the recipe; documents re-evaluated
  with Python; resolved re-pinned); Python suite 186 passed.
- `test/support/fixture-movie.mjs`: the fixture project copied and committed
  by the recipe, a document written beside its movie, takes installed.
- End to end by hand: tour check/preview/render/review pass (567 frames, 2 min
  cold; second render 0 captured, 567 reused); YAML fixture
  check/preview/render/review pass.

## State at archive
Every item above and the three follow-ups below are done: tests ported and
moved (`test/browser/`, `test/pipeline/`), manual and records written, change
archived with specs synced. Open for others: the orchestrator's review (task
0.2), the contract findings in evidence.md, the film (task 4.1).

## Follow-ups closed after the docs review
1. `check` bundles and type-checks a document's stage before it needs takes.
2. The renderer poses the first frame that places a view before capturing,
   so a viewer below the movie's API is refused first.
3. Project elements must report a box.
