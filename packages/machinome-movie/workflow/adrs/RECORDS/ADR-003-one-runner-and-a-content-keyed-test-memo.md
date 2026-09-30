# ADR-003: One runner, and a content-keyed memo of the slow proofs

Status: Accepted (OpenSpec change `one-runner`, 30 September 2026)

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
3. **Two memos in `.test-memo/`** (ignored, never committed), both in
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
