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

## Red

Each item's tests were written before its code and run with
`npx vitest run --project pure <files>`:

- **Item 1, the shared store** (`test/memo.test.mjs`, "one memo for every
  worktree of the repository"): 3 of 3 fail. `memoDirectory is not a
  function`; `the other worktree reuses the pass` (the fingerprint was
  relative to the repository of the memo module, not to the root the suite
  runs from, so two roots of equal content computed different keys); and the
  concurrent writers: `ENOTEMPTY: directory not empty, rename
  '.../artefacts/.staging-dw1fk8' -> '.../artefacts/film-5ffc43173244a2ac'`,
  the second writer failing because the first had published. After the code,
  one failure remained and was the test's: its third call used another
  producer, whose source is part of the key; it now reuses the same producer.
- **Item 2, the narrowed key** (four tests under "the verdict key covers
  what a slow test can reach", and `test/repository.test.mjs`'s key test,
  which asserted the directory `stage` and now asserts its served files and
  not `stage/stage.test.tsx`): 4 of 4 fail, `Cannot find module
  '/test/support/reach.mjs'`. Targeted mutations of `test/support/reach.mjs`,
  each reverted at once:

  | mutation | failing tests |
  |---|---|
  | every file under `src/` in every key (the old rule's breadth) | `a file reached only through an import misses when changed; an unreached file hits`; `what a reached module serves is keyed; a spawned command is followed through its imports` |
  | a spawned command keyed as a file, not followed | `what a reached module serves is keyed; ...` |
  | `import()` not followed | `a file reached only through an import misses ...` |
  | the tripwire disabled | `a reached module that locates a file by path without declaring it is refused by name` |
  | `stage/` not declared as served by `src/render.mjs` and `src/stage-build.mjs` | `in this repository, every read of every slow test is declared and the stage is keyed for the browser tests` |

- **Item 3, wart 10** ("a cold run leaves nothing behind"): 3 of 3 fail.
  The cold artefact was made at `/tmp/videomaker-cold-film-LaoH26`, outside
  the cold directory given (and that red run itself leaked it);
  `openColdRun is not a function`; `sweep is not a function`.
- **Item 4, wart 11** (`test/annotations.test.mjs`,
  `test/movie-document.test.mjs`): 2 of 2 fail. `viewerApiRefusal(marks, 27,
  'movie')` returned "This episode needs Viewer API 28 for marks (shot push)
  ..."; the refusal `stageConfig` gives the stage for the fixture movie did not
  match `^This movie needs Viewer API 28 for highlight (shot source), ...`.

Green after each item: the memo tests 15, then 19 (and 25 with
`repository.test.mjs`), then 22 in `memo.test.mjs`; the pure and stage
projects together 18 files, 182 tests.

## Green

The shared store is `/home/asa/devel/machinome/videomaker/.git/videomaker-test-memo/`
(`git rev-parse --path-format=absolute --git-common-dir` from this worktree
gives `/home/asa/devel/machinome/videomaker/.git`). It did not exist before
the first warm run.

- **Cold** (`npm test -- --cold`, after items 1 to 4): 28 files, **290
  pass, 582.9 s** (583.6 s wall), "0 passed from the memo, 290 run". The store
  was not created. `/tmp` held 55 `videomaker-cold-*` directories before and
  the same 55, by name, after (27 more than at the base: the old code's pure
  runs and the red run of item 3 leaked them before the fix); no
  `videomaker-cold-run-*` remained. The slow files: incremental-rendering
  174.3 s, movie-pipeline 174.2 s, render 113.2 s, stage 52.2 s,
  review-pack 33.4 s, source-only-browser 20.6 s, pictures 7.5 s,
  browser-seam 1.2 s, speech 0.5 s, source-scenes 0.5 s.
- **Filling the store** (`npm test`): 290 pass, 586.6 s, "0 passed from the
  memo, 290 run"; 108 verdicts and three artefacts recorded
  (`pictures-media-matrix-d604da8147010e1e`,
  `render-picture-media-f3e2c7a72b22a3ef`,
  `review-fixture-film-a01700849e43114c`: the same names as in the copied
  `.test-memo/`, since those keys never depended on the checkout).
- **Warm** (`npm test`): 290 pass, **9.23 s**, "108 passed from the memo,
  182 run" (the 182 are the pure and stage tests, never memoized).

### Probe edits (a line appended, run, reverted)

| edit | slow tests run | passed from the memo | time | under the old rule |
|---|---|---|---|---|
| `fixtures/README.md` | `stage` (9), `movie-pipeline` (7) | 92: every other slow file | 232.1 s | all 108 run, about 587 s |
| `test/frame-fixtures.mjs` | `pictures` (16) | 92: every other slow file | 12.7 s | all 108 run, about 587 s |
| reverted | none | 108 | 9.1 s | 108 |

The fixture edit is the cheap stand-in for the fixture project's
`videos/tour/stage.tsx` (both are read only through
`test/support/fixture-movie.mjs`); editing the fixture project itself fails
its revision pin by design (`fixtures/README.md`'s recipe re-pins it), so it
was not used as a probe. The other rows of the measurement table are the
rule's computation, not runs.

### Sharing across checkouts of the same repository

A second worktree was not made. Instead the worktree's content was copied
(`tar`, without `.test-memo/`) into a temporary directory under the session's
scratch space; its `.git` file names this worktree's administrative
directory, so Git resolves the same common directory, and `diff -rq` found
the content identical. `npm test` there: 28 files, **290 pass, 7.02 s,
"108 passed from the memo, 182 run"**: every slow verdict the worktree had
recorded was reused from the other checkout, and nothing ran cold. The copy
was then removed. The test `equal content in two roots is passed from one
store; a different content misses` proves the same over two real worktrees of
a temporary repository.

## Final, on the final content

After the records and the archive (only `evidence.md` changed since, which
no key reads):

- **Cold**: `npm test -- --cold`: 28 files, **290 pass, 574.1 s** (574.7 s
  wall), "0 passed from the memo, 290 run". Every file of the store (161)
  byte-identical before and after (SHA-256 of all). `/tmp` held the same 55
  `videomaker-cold-*` directories of the old code before and after, and no
  `videomaker-cold-run-*`.
- **Warm**: `npm test`: 28 files, **290 pass, 9.40 s**, "Test memo: 108
  passed from the memo, 182 run": every slow test, by name, as the reporter
  lists them.

Against the base: the base's warm run (10.6 s) needed the 108 verdicts copied
by hand from another worktree; now any worktree or checkout of the repository
reads them from one store, so a cycle worktree and the merge into the
campaign worktree start warm for every content already proved anywhere in
the repository. A cold run costs about 575 s here (the cold run is
the policy's before integration, unchanged).

## What was not done, and why

- A second Git worktree was not created; the sharing was proved by the test
  over two real worktrees of a temporary repository and by a copy of the
  content recognised by Git as the same repository (above).
- The probe edits ran for a fixture file and a test helper only; the other
  rows of the measurement table are computed by the rule. An edit to
  `src/speech.mjs` or `src/timeline.mjs` reruns every slow file under either
  rule, so running it would have measured only the cold time again.
- The 55 `videomaker-cold-*` directories under `/tmp` left by the old code
  and the worktrees' old `.test-memo/` directories (this one's included) were
  left in place: nothing reads them now, a leftover of the old code carries no
  owner and may belong to a suite still running it in another worktree, and
  deleting them is the pilot's (task 6.1).
- The architecture overview does not describe the test memo; unchanged.
- `src/render.mjs` changed by one line (the refusal's subject), which changes
  the shot cache key: every project's shot caches are recaptured once.
