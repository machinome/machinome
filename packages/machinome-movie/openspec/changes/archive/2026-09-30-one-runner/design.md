## Context

`npm test` is `node --test --test-concurrency=1 test/*.test.mjs
experiments/dark-source/emphasis.test.mjs`: 22 files, 209 tests, one at a time,
about five and a half minutes. Thirteen files are pure (they import `src/`
modules and assert on values); eight launch Chromium through
`src/render.mjs`, run FFmpeg, Git or the command line, or write temporary build
directories. `browserSession` in `src/render.mjs` starts an HTTP server for the
film page's assets and launches its own headless Chromium for every session,
and the browser tests open dozens of sessions, so a run launches Chromium
about a hundred times.

Tests use `node:test`'s `test`, the context's `t.after`, `t.test` subtests
(three files) and `t.diagnostic` (one test), and `node:assert/strict`
throughout. `vitest 5.0.3` and `jsdom 30.1.1` are declared dev dependencies
since the campaign's toolchain commit.

The policy being implemented is `AGENTS.md` "Testing policy", in particular
"Rules across the layers" and "Memoization of slow tests". The tool's own shot
cache (`src/shot-cache.mjs`: content keys, verified generations, index
published last) and the framework's persistent verdict store are the named
precedents for the memo's discipline.

## Goals / Non-Goals

Goals: one runner (vitest) for all Node tests with every assertion kept; pure
tests in parallel before slow tests run serially in one worker; one Chromium
and one asset server per run; an artefact memo and a verdict memo obeying
every rule of the policy, tested for honesty; the records updated.

Non-goals: moving test files under `test/browser/` and `test/pipeline/` (a
later cycle), the React stage and its layer 4 tests, `tsc --noEmit`, any change
to the film page, the timeline, the formats, the command line's behaviour or
the Python package.

## Decisions

### D1. Two vitest projects, ordered

`vitest.config.mjs` declares two projects:

- `pure`: `test/**/*.test.mjs` except the slow list, `sequence.groupOrder: 0`,
  files in parallel, test timeout 30 s.
- `slow`: the slow list, `sequence.groupOrder: 1` (it starts after every pure
  file has finished, so a pure failure is reported before Chromium works),
  `fileParallelism: false` (one worker), `isolate: false` (the files share one
  module graph in that worker, which is what lets one connection and one asset
  server serve every file), test and hook timeouts of ten minutes (the
  `node --test` suite had none; the longest test takes about a minute).

The slow list is explicit in the config: `incremental-rendering`,
`movie-pipeline`, `render`, `review-pack`, `source-only-browser` (Chromium);
`pictures`, `source-scenes` (FFmpeg, Git); `speech` (writes build
directories); and this change's `browser-seam`. A file is slow when it
launches Chromium, runs FFmpeg or writes a build directory; everything else is
pure. The include and exclude are complementary, so every file is in exactly
one project.

Alternative: one project with `--test-concurrency=1` semantics
(`fileParallelism: false` everywhere). Rejected: the policy asks for the pure
layer to run in parallel and first. Alternative: move the slow files to
`test/browser/` and `test/pipeline/` now and select by directory. Deferred:
the imports and fixture paths of eight files would change in the same commit
as their runner, and the move is its own cycle in the campaign.

`experiments/` is outside `test/` and therefore outside both projects;
`experiments/dark-source/emphasis.test.mjs` stays a `node:test` file run with
`node --test experiments/dark-source/emphasis.test.mjs`, as its README will say.

### D2. The conversion is mechanical

Each file imports `test` (and `describe` where needed) from `vitest`, keeps
`node:assert/strict`, and changes only what the runner requires:

- `t.after(fn)` becomes `t.onTestFinished(fn)`, the vitest test context's
  equivalent (runs after the test, pass or fail); `project-fixture.mjs` takes
  the same context.
- A `t.test` subtest becomes a `test` inside a `describe` named as the parent
  test was, with the parent's shared helper at the group's scope. The count
  therefore changes: the three parents that `node --test` counted as tests are
  now groups (209 − 3 parents − 3 experiment tests = 203 converted tests).
- `t.diagnostic(message)` becomes `console.log(message)`.

No assertion, fixture or tolerance changes.

### D3. The seam in `src/render.mjs`

`browserSession(e, viewer, width, captions, action, {browser, assets} = {})`,
and `preview` and `render` pass `browser` and `assets` through from their
options:

- `browser`: an already launched or connected Playwright browser. When given,
  the session opens its page on it and closes only that page (which closes the
  page's own context); it never launches or closes the browser. When absent,
  the session launches Chromium with `CHROMIUM_ARGS` and closes it, exactly as
  today.
- `assets`: a server made by the new exported `assetServer()`: one HTTP server
  on 127.0.0.1 whose request handler is mounted by one session at a time
  (`mount(handler)` returns the release; a second mount while one is standing
  is refused naming the asset server). When absent, the session makes its own
  and closes it, exactly as today.

`CHROMIUM_ARGS` (the SwiftShader flags) is exported so the test run launches
the same browser the command line would. `bin/videomaker.mjs` passes neither
option; its behaviour and output are unchanged. The frames are unchanged: the
page, its URLs and its viewport are the same; only who owns the process and
the socket changes.

### D4. One Chromium per run

`test/support/toolchain.mjs` is the `slow` project's global setup. It runs
once per run in the main process: it launches one Chromium with
`chromium.launchServer({headless: true, args: CHROMIUM_ARGS})`, connects once
to read its version, and provides the WebSocket endpoint to the tests.
Teardown closes it.

`test/support/stage.mjs` wraps `preview`, `render` and `browserSession`: on
first use in the worker it connects to that endpoint and makes one
`assetServer()`, then passes both to every call. Because the slow project has
one worker and shares its module graph (D1), that is one connection and one
asset server for the whole run. A verdict memo hit never calls the wrapper,
so a fully memoized run connects to nothing. The slow test files import these
three names from `test/support/stage.mjs` instead of `src/render.mjs`; other
imports from `src/render.mjs` (such as `fadeSubsets`) are unchanged.

`test/support/one-browser.mjs`, a setup file of the slow project, counts calls
to `chromium.launch` in the worker and fails a file's `afterAll` when more
launches happened than a test declared it would make, naming the shared
browser in `test/support/stage.mjs`. `test/browser-seam.test.mjs` proves the
seam by counting launches: two sessions on the shared browser launch nothing,
share one asset server origin and leave the browser connected; one session
without a browser (the command line's path) launches exactly one Chromium and
closes it.

Command-line tests (`movie-pipeline` `check`, `review-pack` `render`) spawn
`bin/videomaker.mjs` in a child process, which launches its own Chromium, as
the command line must. They are counted in the evidence, not doubled.

### D5. The toolchain fingerprint

The global setup obtains, by running each once per run: `process.version`;
the Chromium version from the launched browser; the first line of
`ffmpeg -version` and of `ffprobe -version`; `git --version`; and for each face
`render` binds (`DejaVu Sans` regular and bold, `DejaVu Sans Mono` regular and
bold) the file `fc-match` resolves and that file's SHA-256. A tool that is
absent is recorded as absent (the run will fail where it is needed). The
record is provided to the tests and enters every memo key.

### D6. The verdict memo

`slowTest(name, fn, options)` from `test/support/memo.mjs` is a vitest `test`
whose body is:

1. With the cold switch: run `fn`; read and write nothing.
2. Otherwise compute the key: SHA-256 of `{schema: "verdict-memo-v1", test, inputs,
   toolchain}` where `test` is the file's path relative to the repository and
   the test's full name, and `inputs` is the content fingerprint (D8) of
   everything a slow test can read: `src/`, `bin/`, `fixtures/`, `schema/`,
   every non-test module under `test/` (the helpers, the viewer double, the
   support modules, the memo itself), the test's own file, `package.json`,
   `package-lock.json` and `vitest.config.mjs`.
3. A verified entry for the key (D9) is a hit: the body does not run; the
   test's `task.meta.memo` is set to `"passed from the memo"` and the words
   `passed from the memo: <test>` are logged. The reporter (D10) lists these
   by name at the end of the run.
4. A miss runs `fn`. Only when it passes, and the input fingerprint computed
   again after it is unchanged (an edit during the run records nothing), the
   entry is written. A failure is never recorded, so a failing test fails
   again on every run.

The slow test files take `test` from this module (`import {slowTest as test}`),
so every test in a slow file is memoized and none of their bodies change.

What a slow test reads that is not in the fingerprint, and why that is honest:
the Git `HEAD` of this repository, which `render` records as provenance (no
assertion depends on its value, and the content it names is fingerprinted);
the wall clock, which `render` reads only to log elapsed time and
`review-pack`'s decode-gate test reads only to bound its waits (the verdict is
decided by files the test gates on, and a timeout fails the test, which is
never recorded); `randomUUID` names of temporary directories and generations;
and loopback sockets. No slow test reaches a network or the speech provider:
the provider is doubled and the key removed, as today.

### D7. The artefact memo

`artefact(name, {params, files}, produce)` returns a directory holding what
`produce(dir)` wrote. The key is SHA-256 of `{schema: "artefact-memo-v1", name,
params, files (their content fingerprint), producer: produce.toString(),
toolchain}`. A verified entry (D9) is returned without producing; otherwise
`produce` writes into a staging directory inside the memo, the index is
written last, and the staging directory is renamed into place. Callers copy
from it and never write into it. With the cold switch, `produce` writes into a
fresh temporary directory outside the memo, removed when the process exits.

Applied where a slow test builds an input product rather than the thing under
test: `review-pack`'s fixture film (an FFmpeg encode used by a dozen tests),
the still, clip frames and the two lossless clip encodes of `render`'s picture
test, and the media set of `pictures`' media fixture. No slow test today
renders a film only to use it as an input (each render in the suite is the
subject of its test), and the fixture export is a JSON file written in
milliseconds; the memo is ready for the stage's fixture films when they exist.

### D8. Content, never mtime

The fingerprint of a set of paths walks each directory in sorted order and
hashes, for every regular file, its relative path and the SHA-256 of its
bytes; symbolic links are hashed as their target text. `stat` is used only to
tell a directory from a file. An mtime never enters a key; a honesty test
touches a file's mtime and asserts the hit survives.

### D9. Verified reuse

- A verdict entry is `.test-memo/verdicts/<key>.json`, written to a temporary
  name and renamed (the entry is its own index). It holds the key, the test,
  `verdict: "pass"`, and `check`, the SHA-256 of the rest. It is a hit only
  when it parses, its key and test match, its verdict is `pass` and its check
  verifies; anything else is removed and treated as a miss.
- An artefact entry is `.test-memo/artefacts/<name>-<key 16>/` with
  `index.json` listing every file's relative path, size and SHA-256, written
  after every file and before the rename into place. It is a hit only when the
  index parses, names the key, and the directory holds exactly the listed
  files with those hashes. A damaged, partial (no index) or unverifiable entry
  is removed and regenerated whole.

### D10. Where the memo lives, the cold switch, the label

- The memo lives in `.test-memo/` at the repository root, added to
  `.gitignore` and never committed.
- `npm test -- --cold` runs `scripts/test.mjs`, which removes `--cold` from its
  arguments, sets `VIDEOMAKER_TEST_COLD=1` and runs `vitest run` with the rest;
  `VIDEOMAKER_TEST_COLD=1` with any vitest invocation is the same switch.
  (Vitest refuses unknown options, so the switch needs this front.) Cold, the
  memo is neither read nor written.
- `test/support/memo-reporter.mjs`, added beside vitest's default reporter,
  prints at the end of a run the number of tests passed from the memo and
  their names, and the number run.

### D11. The memo's honesty, layer 9

`test/memo.test.mjs` (pure, fast) exercises the memo module over a tiny step
in a temporary directory with an explicit toolchain record: a first run
executes and records; a second run is a hit that does not execute, twice, with
the same verdict; a changed input file, a new file and a changed toolchain
each miss; a touched mtime still hits; a corrupted, truncated or forged verdict
entry is regenerated; a failing step is not recorded and fails again; the cold
switch runs the step and leaves the memo directory untouched; an artefact is
produced once and reused byte-identical; a damaged, partial or extended
artefact entry is regenerated whole; a memoized pass sets the task's meta to
"passed from the memo" and logs those words.

### D12. The ADR's category

ADR-003 is filed under `RECORDS`: the decision is how the repository keeps and
reuses its own proofs (a memoized verdict is a record that a proof held for
given content), and its rules bind every future test. The seam in
`src/render.mjs` is a consequence recorded in the ADR, not the decision; the
pipeline's behaviour is unchanged, which is why it is not a `PIPELINE` ADR.

## Risks / Trade-offs

- [One long-lived Chromium process instead of one per session could change
  pixels or let state leak between sessions] → every session still gets a new
  page in a new browser context; the determinism tests (pose A, B, A; a fresh
  session reproducing a rendered frame) run on the shared browser. Any
  difference is a finding recorded in the evidence, not hidden.
- [`isolate: false` lets module state and patched globals leak between slow
  files] → `src/` holds no mutable module state; the tests that patch `fetch`,
  the key or `console` restore them after the test.
- [An over-broad key recomputes more than needed] → honest by construction: a
  change under `src/` reruns every slow test once. Narrowing a test's inputs is
  a later refinement, never a guess.
- [A memoized pass hides a flaky test] → the intermittent
  `incremental-rendering` test is recorded, and the policy's cold run before
  integration runs everything; the evidence carries that cold run.

## Migration Plan

`npm test` changes meaning in one commit. Rollback is reverting the commit;
the memo directory can be deleted at any time.

## Open Questions

- Whether the command line should one day accept a browser endpoint (not in
  scope; the policy asks only the tests to share one).
- Narrower per-test inputs for the verdict key, once the stage's tests exist
  and their reads are known.
