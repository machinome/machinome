## Why

The pilot, watching the react-stage campaign on 30 September 2026: "I see
things take a long time to run. Make sure memoization and caching is making
process faster." The test memo of the `one-runner` change (ADR-003) makes a
re-run of unchanged content take seconds, but it does not speed up
development, for two reasons the campaign met:

- **The memo lives in `.test-memo/` at each worktree's root.** A cycle
  worktree starts cold (the `react-stage` cycle's worktree had no memo for two
  hours), and a merge into the campaign worktree runs cold again although the
  content is identical. The keys are content hashes, so nothing but the
  location stops two worktrees sharing. The evidence is this worktree's own
  base run: 108 verdicts copied by hand from the campaign worktree were all
  reused (108 passed from the memo, 170 run, 10.6 s).
- **The verdict key covers everything a slow test could possibly read**:
  every file under `src/`, `bin/`, `stage/`, `fixtures/`, `schema/`, the
  fixture project and every helper under `test/`. Any source edit misses every
  slow verdict, so inside a cycle the memo never hits. ADR-003 called the
  over-broad key "honest by construction" and left narrowing "to evidence";
  the campaign's cycles are that evidence.

The need is the campaign's and the pilot's, not an episode's: this is
repository maintenance of the proof harness the testing policy mandates, and
it changes nothing a film or an author sees, except wart 11's wording below.

Two warts of the react-stage change are fixed with it, because they are the
memo's own (wart 10) or a one-line refusal met in the same tests (wart 11):

- Wart 10: with the cold switch the artefact memo writes into
  `/tmp/videomaker-cold-*` and removes them only on process exit, which
  vitest's workers never reach; 28 such directories are under `/tmp` now.
- Wart 11: `viewerApiRefusal` says "This episode needs Viewer API ..." for a
  movie document too.

## What Changes

- **One memo per repository, shared by its worktrees.** The store moves from
  `<worktree>/.test-memo/` to `<git common dir>/videomaker-test-memo/`, found
  with `git rev-parse --git-common-dir` by the slow project's global setup;
  outside a Git work tree it falls back to `.test-memo/` at the root. Keys
  stay content-only, so two worktrees with equal content share verdicts and
  artefacts. Concurrent writers from two worktrees are safe: verdicts are
  written to a unique temporary name and renamed; an artefact is staged in a
  unique directory and renamed into place, and a writer that loses the race
  to an equal, verified entry keeps the winner's. `--cold` still ignores the
  store entirely.
- **The verdict key narrows to what a slow test can reach**, measured first
  and recorded in `evidence.md`: the static import graph of the test file
  (relative `import ... from` and `import(...)` in `.mjs`, `.ts` and `.tsx`),
  followed through the modules it reaches; the files a reached module reads
  without importing them (the stage sources and `src/film.html` the renderer
  serves to the browser, the schema, the fixtures and the fixture project), and
  the import graph of the command line when a reached test spawns it; plus,
  always, every file under `test/support/`, the viewer double, the test's own
  file, `package.json`, `package-lock.json`, `vitest.config.mjs` and the
  toolchain record. A pure tripwire test refuses a module a slow test reaches
  that locates a repository file by path without declaring what it reads.
- **Cold artefacts leave nothing behind.** Each run's cold artefacts go
  under one run directory the global setup makes and its teardown removes;
  the next run removes what a killed run left behind (cold run directories,
  staging directories and pending verdict writes whose process is gone).
- **A viewer refusal names its source**: "This movie needs Viewer API ..."
  for a movie document, "This episode needs Viewer API ..." for a YAML
  episode, at `check`, `preview` and `render`.
- Records: ADR-003 amended in place with a dated section; `AGENTS.md`,
  `README.md` and the architecture overview where they name the memo;
  `CHANGELOG.md` under `Unreleased`; warts 10 and 11 triaged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-suite`: where the memo lives (shared by the repository's worktrees),
  what the verdict key covers (what a slow test can reach, not everything),
  and that a cold run leaves nothing under the temporary directory.
- `part-annotations`: the older-viewer refusal names a movie as a movie.

## Impact

Changed: `test/support/memo.mjs` (store location, root-relative keys,
concurrent writers, cold run directory, sweep), `test/support/toolchain.mjs`
(finds the store, makes and removes the cold run directory, sweeps what a
killed run left), a new `test/support/reach.mjs` (the import graph and the
declared reads), `test/memo.test.mjs` (the new honesty tests),
`src/episode.mjs` and `src/render.mjs` (the refusal's subject; one line in
`render.mjs`, which is hashed into the shot cache key, so shot caches are
recaptured once), `bin/videomaker.mjs` (passes the subject at `check`),
`test/annotations.test.mjs` and `test/movie-document.test.mjs` (the wording).
`.gitignore` keeps `.test-memo/` for the fallback. The existing
`.test-memo/` directories of worktrees are left alone; nothing reads them once
the store has moved, and removing them is the pilot's.

## Non-goals

Memoizing a pure test; narrowing the key per test inside a file; making the
command line reuse a browser; any change to the stage, the timeline, the
formats, the Python package or the shot cache; the intermittent pixel tests of
wart 1 of the test suite. No publication, push or paid request.
