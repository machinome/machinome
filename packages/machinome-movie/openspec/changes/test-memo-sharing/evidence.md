# Implementation evidence

## Authority and scope

A cycle of the react-stage campaign, on branch `test-memo-sharing`
(worktree `WTs/test-memo-sharing`), cut from `react-stage` at `55f255d`, for
the pilot's request of 30 September 2026 ("Make sure memoization and caching
is making process faster"). Nothing was pushed or published; no network
request or paid request was made; no `.env` was read and the runs had no
speech key in their environment. `node_modules` is the campaign worktree's
install, reached through the worktree's symlink; nothing was installed.
Integration into `react-stage` is the pilot's.

Environment of every run: Linux, Node v24.11.1, vitest 5.0.3, Playwright's
Chromium, `ffmpeg version 6.1.1-3ubuntu5`, `git version 2.43.0`.

## Base

`npm test` on the base content (`55f255d`) before any change, with the
worktree's `.test-memo/` holding 108 verdicts and three artefacts copied from
the campaign worktree (`WTs/react-stage`) at the same content:
**28 files, 278 tests, 278 pass, 10.62 s** (11.2 s wall), "Test memo: 108
passed from the memo, 170 run". Every copied verdict was reused: the keys are
content, and only the memo's place kept the two worktrees from sharing.

`/tmp` held 28 `videomaker-cold-*` directories left by earlier cold runs of
the old code (wart 10).

## The narrowed key, measured before adoption (task 0.2, design D4)

The rule of design D4, run on the base content by a scratch copy of what
became `test/support/reach.mjs` (the same graph, table and `ALWAYS` list).
The old rule is ADR-003's: every file under `src/`, `bin/`, `stage/`,
`fixtures/`, `schema/`, the fixture project and every non-test module under
`test/`, so under it every edit below misses all ten slow files.

undeclared readers: []

| slow file | of 33 files under src/, stage/, bin/: old rule | new rule | not covered by the new rule |
|---|---|---|---|
| `test/browser/browser-seam.test.mjs` | 33 | 30 | `src/command-timing.mjs`, `stage/stage.test.tsx`, `bin/videomaker.mjs` |
| `test/browser/render.test.mjs` | 33 | 30 | `src/command-timing.mjs`, `stage/stage.test.tsx`, `bin/videomaker.mjs` |
| `test/browser/source-only-browser.test.mjs` | 33 | 30 | `src/command-timing.mjs`, `stage/stage.test.tsx`, `bin/videomaker.mjs` |
| `test/browser/stage.test.mjs` | 33 | 30 | `src/command-timing.mjs`, `stage/stage.test.tsx`, `bin/videomaker.mjs` |
| `test/pipeline/incremental-rendering.test.mjs` | 33 | 30 | `src/command-timing.mjs`, `stage/stage.test.tsx`, `bin/videomaker.mjs` |
| `test/pipeline/movie-pipeline.test.mjs` | 33 | 32 | `stage/stage.test.tsx` |
| `test/pipeline/pictures.test.mjs` | 33 | 13 | `src/command-timing.mjs`, `src/film.html`, `src/pixels.mjs`, `src/render.mjs`, `src/review-pack.mjs`, `src/review-samples.mjs`, `src/shot-cache.mjs`, `src/stage-build.mjs`, `stage/components.tsx`, `stage/css.d.ts`, `stage/index.ts`, `stage/marks.ts`, `stage/registry.ts`, `stage/runtime.tsx`, `stage/shipped.tsx`, `stage/stage.css`, `stage/stage.test.tsx`, `stage/tsconfig.json`, `stage/types.ts`, `bin/videomaker.mjs` |
| `test/pipeline/review-pack.test.mjs` | 33 | 32 | `stage/stage.test.tsx` |
| `test/pipeline/source-scenes.test.mjs` | 33 | 14 | `src/command-timing.mjs`, `src/pixels.mjs`, `src/render.mjs`, `src/review-pack.mjs`, `src/review-samples.mjs`, `src/shot-cache.mjs`, `src/stage-build.mjs`, `stage/components.tsx`, `stage/css.d.ts`, `stage/index.ts`, `stage/marks.ts`, `stage/registry.ts`, `stage/runtime.tsx`, `stage/shipped.tsx`, `stage/stage.css`, `stage/stage.test.tsx`, `stage/tsconfig.json`, `stage/types.ts`, `bin/videomaker.mjs` |
| `test/pipeline/speech.test.mjs` | 33 | 13 | `src/command-timing.mjs`, `src/film.html`, `src/pixels.mjs`, `src/render.mjs`, `src/review-pack.mjs`, `src/review-samples.mjs`, `src/shot-cache.mjs`, `src/stage-build.mjs`, `stage/components.tsx`, `stage/css.d.ts`, `stage/index.ts`, `stage/marks.ts`, `stage/registry.ts`, `stage/runtime.tsx`, `stage/shipped.tsx`, `stage/stage.css`, `stage/stage.test.tsx`, `stage/tsconfig.json`, `stage/types.ts`, `bin/videomaker.mjs` |

| edit | old rule: slow files that miss | new rule: slow files that miss | new rule: slow files passed from the memo |
|---|---|---|---|
| `src/speech.mjs` | all 10 | all 10 | none |
| `src/timeline.mjs` | all 10 | all 10 | none |
| `stage/shipped.tsx` | all 10 | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, review-pack | pictures, source-scenes, speech |
| `src/review-pack.mjs` | all 10 | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, review-pack | pictures, source-scenes, speech |
| `python/tests/fixtures/project/videos/tour/stage.tsx` | all 10 | stage, movie-pipeline | browser-seam, render, source-only-browser, incremental-rendering, pictures, review-pack, source-scenes, speech |
| `src/render.mjs` | all 10 | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, review-pack | pictures, source-scenes, speech |
| `src/film.html` | all 10 | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, review-pack, source-scenes | pictures, speech |
| `fixtures/documents/tour.json` | all 10 | stage, movie-pipeline | browser-seam, render, source-only-browser, incremental-rendering, pictures, review-pack, source-scenes, speech |
| `bin/videomaker.mjs` | all 10 | movie-pipeline, review-pack | browser-seam, render, source-only-browser, stage, incremental-rendering, pictures, source-scenes, speech |
| `stage/stage.test.tsx` | all 10 | none | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, pictures, review-pack, source-scenes, speech |
| `test/frame-fixtures.mjs` | all 10 | pictures | browser-seam, render, source-only-browser, stage, incremental-rendering, movie-pipeline, review-pack, source-scenes, speech |

Reading: the browser tests and the render pipeline reach 30 of the 33 files
under `src/`, `stage/` and `bin/`: `src/episode.mjs` imports
`src/movie.mjs`, which reaches most of `src/`, and `src/render.mjs` serves
the whole stage. An edit to `src/speech.mjs` or `src/timeline.mjs` misses
every slow file under either rule; that is what those files can reach. The
narrowing is kept where it buys something:

- a fixture movie or the fixture project's stage (the stage campaign's
  frequent edit) now misses only `stage` and `movie-pipeline`; the two
  longest files, `incremental-rendering` and `render`, stay warm;
- a stage or render-side edit leaves `pictures`, `source-scenes` and
  `speech` warm;
- the command line misses only the two files that spawn it, a stage
  component test (`stage/*.test.tsx`) misses none, and a helper outside
  `test/support/` misses only the files that import it.
