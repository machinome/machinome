## Why

The Node suite runs under `node --test`: 209 tests, all serial, about five and
a half minutes on every run, with nothing reused between runs. The testing
policy in `AGENTS.md` asks for something else, and the next step of the
declarative-python campaign depends on it. The React stage cycle that follows
this one writes stage tests (layers 4 and 5) which "must be memoized from the
first test written, not retrofitted", under one JavaScript runner. Without the
runner and the memo in place first, the stage campaign would either write its
tests under a runner it must leave, or write unmemoized slow tests and pay the
full render cost on every change.

The policy rules this change implements, all quoted from `AGENTS.md` "Testing
policy":

- "One runner per language. pytest for Python; vitest for all TypeScript and
  Node code including the renderer."
- "Slow layers run serially over one build directory; never two suites at
  once. Everything inside layer 4 runs in parallel and in seconds, so a change
  is felt before Chromium opens."
- "Within one run, Chromium is launched once, one asset server serves every
  browser test, and the fixture export is built once."
- "`experiments/` carry their own tests and are not part of the suite."
- The whole "Memoization of slow tests" section: an artefact memo and a verdict
  memo keyed on the content hash of every input, verified on reuse, in an
  ignored directory, ignored entirely by a `--cold` switch, with a memoized pass
  reported as one, and the memo's own honesty tested in layer 9.

The need is the campaign's, not an episode's: this is repository maintenance
the testing policy mandates, ordered for this step of the campaign
(`workflow/ongoing/declarative-python-api.md`), and it changes nothing a film
or an author sees.

## What Changes

- `npm test` runs vitest 5 (already a declared dev dependency) instead of
  `node --test`. Every test under `test/` moves to vitest with its assertions
  kept; `node:assert/strict` stays where the tests use it. Subtests become
  described groups of tests. Test files keep their names and places.
- `experiments/dark-source/emphasis.test.mjs` leaves `npm test`; its README
  says how to run it on its own.
- The suite is two vitest projects: **pure** tests (timeline, easing, words,
  camera, keyframes, movie document, review samples and the other in-memory
  tests) in parallel, first; then **slow** tests (anything that launches
  Chromium, runs FFmpeg or writes a build directory) serially in one worker.
- Chromium is launched once per run, and one asset server serves every browser
  test. `src/render.mjs` gains a seam: `browserSession`, `preview` and `render`
  accept an already launched `browser` and a shared `assets` server through
  their options; the command line passes neither and launches its own, as
  today. A test counts launches.
- Two memos in one module under `test/support/`: the **verdict memo** (a slow
  test's pass, keyed on the content hash of everything it read) and the
  **artefact memo** (expensive products the slow tests build: fixture films and
  media encodes). The key is content, never an mtime, and includes the versions
  of Node, Chromium, FFmpeg, Git and the stage's fonts, obtained once per run.
  Reuse is verified; damaged entries are regenerated whole; the memo lives in
  the ignored `.test-memo/`; `npm test -- --cold` (or `VIDEOMAKER_TEST_COLD=1`)
  ignores it entirely; a reused verdict is reported as "passed from the memo".
- Fast honesty tests of the memo (layer 9): a changed input misses, an
  unchanged input whose mtime moved still hits, a corrupted entry is
  regenerated, a failure is never recorded, the cold switch runs everything,
  and a memoized pass is labelled as one.
- Records: ADR-003 under `docs/adrs/RECORDS/`, a changelog bullet, the
  `AGENTS.md` status sentence about the Node suite, `README.md` on running the
  tests.

## Capabilities

### New Capabilities

- `test-suite`: how the maintainer runs the repository's Node proofs: one
  runner, pure tests before slow ones, one browser per run, and the two memos
  with their honesty rules and the cold switch.

### Modified Capabilities

None. No baseline spec names `node --test` or the test command; no behaviour
of the tool changes.

## Impact

New: `vitest.config.mjs`, `scripts/test.mjs` (the `--cold` switch in front of
`vitest run`), `test/support/memo.mjs`, `test/support/toolchain.mjs` (global
setup: the one Chromium and the toolchain fingerprint),
`test/support/stage.mjs` (the shared browser and asset server),
`test/support/one-browser.mjs` (a launch guard), `test/support/memo-reporter.mjs`,
`test/memo.test.mjs`, `test/browser-seam.test.mjs`, ADR-003. Changed:
`package.json` (`test` script), `.gitignore`, `src/render.mjs` (the seam only),
every `test/*.test.mjs` (runner imports, `t.after` to `t.onTestFinished`,
subtests to groups; the slow files take their `test` from the memo and their
browser entry points from `test/support/stage.mjs`), `test/project-fixture.mjs`,
`experiments/dark-source/README.md`, `AGENTS.md`, `README.md`, `CHANGELOG.md`,
`docs/adrs/README.md`. `src/render.mjs` is hashed into the shot cache key, so
existing shot caches are recaptured once, as every source change does.

## Non-goals

Moving browser and pipeline tests under `test/browser/` and `test/pipeline/`
(a later cycle; the policy's layout is not needed to run them serially). The
React stage and its tests, `tsc --noEmit`, the Python suite, any change to the
film page, the timeline, the formats or the Python package. Making the command
line reuse a browser. Memoizing a pure test. No publication, push or paid
request.
