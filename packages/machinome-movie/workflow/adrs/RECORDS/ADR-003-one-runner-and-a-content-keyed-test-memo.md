# ADR-003: One runner, and a content-keyed memo of the slow proofs

Status: Accepted (OpenSpec change `one-runner`, 30 September 2026); amended
in place by `react-stage` and `test-memo-sharing` (30 September 2026)

Filed under `RECORDS`: the decision is how the repository keeps and reuses
its own proofs. A memoized verdict is a record that a proof held for given
content, and the rules below bind every test written after it. The seam it
adds to `src/render.mjs` is a consequence, not the decision; the pipeline's
behaviour does not change, which is why this is not a `PIPELINE` record.

## Context

The Node suite ran under `node --test`, one file at a time: 209 tests, about
five and a half minutes on every run, nothing reused, and a Chromium
launched for every browser session (about a hundred per run). The testing
policy in `AGENTS.md` asks for one runner per language (vitest for Node),
pure tests in parallel before the slow layers run serially, one Chromium and
one asset server per run, and two memos keyed on content, honest and tested.
The React stage that comes next in the declarative-python campaign writes
stage tests that must be memoized from the first one written.

The precedents are the tool's own shot cache (`src/shot-cache.mjs`: content
keys, verified generations, index published last) and the framework's
persistent verdict store.

## Decision

1. **vitest runs every Node test**, as two projects (`vitest.config.mjs`):
   `pure` first and in parallel; `slow` (anything that launches Chromium,
   runs FFmpeg or writes a build directory, listed by file) after it, one
   file at a time in one worker sharing one module graph. `npm test` runs
   it; `experiments/` are outside the suite.
2. **One Chromium and one asset server per run.** The slow project's global
   setup (`test/support/toolchain.mjs`) launches one Chromium server with the
   command line's flags; `test/support/stage.mjs` connects to it once and
   makes one asset server, and passes both to `preview`, `render` and
   `browserSession` through their new `browser` and `assets` options. Without
   them, as from the command line, a session launches and closes its own
   browser and server as before. A setup file counts launches and fails a
   file that launched undeclared.
3. **Two memos in `.test-memo/`** (ignored, never committed; moved beside
   the common Git directory by the `test-memo-sharing` amendment), both in
   `test/support/memo.mjs`:
   - the **verdict memo**: every test of a slow file is a `slowTest`, whose
     pass is recorded under the SHA-256 of its name and file, the content of
     everything a slow test can read (`src/`, `bin/`, `fixtures/`, `schema/`,
     the non-test modules under `test/`, its own file, `package.json`,
     `package-lock.json`, `vitest.config.mjs`) and the toolchain (Node,
     Chromium, FFmpeg, ffprobe, Git, and the files and hashes of the four
     faces the stage binds), obtained once per run. A hit does not run the
     body, sets the task's meta to "passed from the memo" and logs those
     words; the memo reporter lists every such test by name. A failure, or a
     pass during which an input changed, is never recorded;
   - the **artefact memo**: an input product a slow test builds (today the
     review-pack fixture film and the picture media encodes) is kept under
     the SHA-256 of its name, parameters, input files, producer source and
     toolchain, produced in a staging directory whose index is written after
     every part, and verified part by part on every reuse.
   A damaged, partial or unverifiable entry of either is removed and made
   again whole. Keys are content, never an mtime.
4. **The cold switch** is `npm test -- --cold` (carried to the tests as
   `VIDEOMAKER_TEST_COLD=1`, the same switch for any vitest invocation): the
   memo is neither read nor written.
5. **The memo's honesty is a layer 9 test** (`test/memo.test.mjs`) over a
   tiny step: changed, added, removed and renamed inputs, another toolchain
   or test name miss; a touched mtime hits; forged, truncated and corrupted
   entries are regenerated; failures are not recorded; the cold switch runs
   everything and leaves the memo untouched; a memoized pass is labelled.

What a slow test reads outside the key decides no verdict, and is named so
the rule stays checkable: the repository's Git `HEAD`, which `render` records
as provenance (the content it names is keyed); the clock, read by `render`
only to log elapsed time and by one review-pack test only to bound its waits
on files it gates; random names of temporary directories and generations;
loopback sockets. No test reaches a network or the speech provider, which is
doubled. A step whose verdict depended on any of these would have to be
doubled before it could be memoized.

## Options considered

- **Keep `node --test`, add a memo around it.** Contradicts one runner per
  language, and the stage's jsdom tests need vitest anyway.
- **One vitest project, everything serial.** Simplest, but the pure layer
  would wait behind Chromium, which the policy rules out.
- **A browser per test file** (isolated modules). Simpler lifetimes, but
  eight launches and eight servers per run where the policy says one.
- **Key each test on only the files it imports.** Narrower and faster to
  invalidate, but an import graph misses fixtures read from disk, the viewer
  double written from source and child processes; an over-broad key is honest
  by construction, and narrowing is left to evidence.
- **A timestamp or Git revision as the key.** Rejected by the policy: a
  revision does not see uncommitted edits and an mtime is not content.

## Consequences

- A warm run of the whole suite takes seconds; a change under `src/` reruns
  every slow test once. Before a cycle integrates, the suite runs cold once
  and the evidence says so.
- A flaky slow test that passed once is not rerun until its inputs change;
  the cold run before integration is where flakiness shows.
- The command line is unchanged; tests share one long-lived Chromium process,
  each session in a fresh page and context.
- `src/render.mjs` is hashed into the shot cache key, so existing shot caches
  are recaptured once.
- Test files stay at the top of `test/`; moving browser and pipeline tests to
  `test/browser/` and `test/pipeline/` is left to a later cycle, and the slow
  list in the config names them until then.

## Amendment (30 September 2026, `react-stage`)

The browser and pipeline tests moved to `test/browser/` and `test/pipeline/`,
and the slow project selects them by directory instead of a list. The stage's
component tests (`stage/**/*.test.tsx`) run under jsdom in a third project,
`stage`, beside `pure`. The verdict key also reads `stage/` and the fixture
project. The decision above stands.

## Amendment (30 September 2026, `test-memo-sharing`)

The pilot, watching the react-stage campaign: "Make sure memoization and
caching is making process faster." Two parts of decision 3 kept the memo
from speeding up development, and are replaced; everything else stands.

**Where the memo lives.** The store is no longer `.test-memo/` at each
checkout's root but one directory every worktree of the repository shares:
`<common dir>/videomaker-test-memo/`, where `<common dir>` is
`git rev-parse --path-format=absolute --git-common-dir` at the root (the
`.git` of the primary checkout, which every linked worktree names). Outside a
Git work tree it falls back to `.test-memo/` at the root. The slow project's
global setup finds it once per run. Chosen over
`$XDG_CACHE_HOME/videomaker/test-memo/` because it is scoped to the repository
whose proofs it records, is found with no configuration, goes with the clone,
is never inside a working tree, and survives a worktree's removal; a
user-level cache would also share between clones, which no one asked for,
and would write outside the repository. Keys were already content-only; the
fingerprints are now relative to the root of the checkout the suite runs in,
so equal content in two worktrees gives equal keys. Two suites may write the
store at once: verdicts are written to a name carrying the writer's PID and
renamed; an artefact is staged in a directory carrying the PID and renamed,
and a writer that finds the entry published first by another uses it when it
verifies; a damaged entry is renamed aside before it is removed. The next
run's global setup removes the staging directories, entries put aside and
pending writes of processes that are gone.

**What a verdict's key covers.** No longer everything a slow test could
read, but what it can reach (`test/support/reach.mjs`): the import graph of
its file (relative static imports, re-exports and `import()` of a literal
path, followed transitively); what a reached module serves or reads without
importing it, declared in one table (`src/render.mjs` serves `src/film.html`
and the stage bundle built from `stage/`; `src/schema.mjs` reads `schema/`;
the fixture movie helper copies the fixture project and reads `fixtures/`;
two pipeline tests spawn the command line, which is followed through its own
imports); and always `test/support/`, the viewer double, the test's own file,
`package.json`, `package-lock.json`, `vitest.config.mjs` and the toolchain
record. Test files are never part of a served directory. A pure test refuses,
by name, a reached module that locates a repository file by path and has no
entry in the table, so the table cannot silently fall behind the code. The
schema of a verdict is `verdict-memo-v2`.

The evidence (the change's `evidence.md`): the base run of a fresh worktree
whose `.test-memo/` held 108 verdicts copied from the campaign worktree
reused all 108 (10.6 s), so only the memo's place stopped two worktrees
sharing. Measured before adoption, the browser tests and the render pipeline
reach 30 of the 33 files under `src/`, `stage/` and `bin/` (`src/episode.mjs`
imports `src/movie.mjs`, which reaches most of `src/`), so an edit to
`src/speech.mjs` or `src/timeline.mjs` still reruns every slow file; but a
fixture movie or the fixture project's stage now reruns only `stage` and
`movie-pipeline`, a stage or render-side edit leaves `pictures`,
`source-scenes` and `speech` warm, and the command line reruns only the two
files that spawn it. The option "key each test on only the files it imports"
was rejected above because an import graph misses fixtures, the served stage
and child processes; the declared table and its tripwire are what make it
honest.

**Cold products.** A cold run's artefacts are made inside one run directory,
`<tmp>/videomaker-cold-run-<pid>-<random>/`, which the global setup opens and
its teardown removes; the next run removes a killed run's. They were made in
one temporary directory each and removed on a process exit that vitest's
workers never reach (wart 10 of the React stage).
