# test-suite Specification

## Purpose
The maintainer runs the repository's Node proofs with one command under one
runner: pure tests first and in parallel, slow tests one at a time on one
browser, and slow proofs remembered by the content they read, reported as
such, verified on reuse and ignored entirely by the cold switch.
## Requirements
### Requirement: One runner runs the Node proofs, pure tests before slow ones

The maintainer SHALL run every Node test of the repository with one command,
`npm test`, under one runner. Tests that only compute on values SHALL run in
parallel and finish before any slow test starts; tests that launch Chromium,
run FFmpeg or write a build directory SHALL run one at a time. The tests of
`experiments/` MUST NOT be part of the suite.

#### Scenario: A pure failure is reported before the browser works

- **WHEN** a timeline test fails and the maintainer runs `npm test`
- **THEN** the failure is reported by the pure tests, which all finish before
  the first slow test starts.

#### Scenario: An experiment is run on its own

- **WHEN** the maintainer runs `npm test`
- **THEN** no test under `experiments/` runs, and the experiment's README
  names the command that runs its tests.

### Requirement: One browser serves every browser test of a run

Within one run of the suite, Chromium SHALL be launched once and one asset
server SHALL serve every browser test. The command line SHALL keep launching
and closing its own browser and asset server for each session.

#### Scenario: Two browser tests share the browser

- **WHEN** two browser sessions run in the suite
- **THEN** no further Chromium is launched, both pages are served by the same
  asset server, and the browser remains open for the next test.

#### Scenario: The command line launches its own

- **WHEN** a session runs without a browser given to it, as the command line
  runs it
- **THEN** exactly one Chromium is launched for it and closed after it.

### Requirement: Slow tests are memoized by content, and a reused pass says so

A slow test's pass SHALL be kept in an ignored memo, keyed on the content of
everything the test can reach and the versions of Node, Chromium, FFmpeg, Git
and the stage's fonts, obtained once per run. What a test can reach SHALL be:
the modules its file imports, followed transitively; the files a reached
module reads without importing them (the stage sources and the page the
browser is served, the schema, the fixtures and the fixture project), and the
modules of the command line when a reached test runs it; and always the test
helpers the runner loads around a test, the viewer double, the test's own
source and the dependency lock. A module a slow test reaches that locates a
repository file by path without declaring what it reads SHALL fail the suite,
naming the module. A test whose key is unchanged SHALL be reported as "passed
from the memo", in those words, and never as a fresh run. A modification time
MUST NOT enter a key. A failure MUST NOT be recorded.

#### Scenario: An unchanged test is passed from the memo

- **WHEN** the maintainer runs `npm test` twice with nothing changed
- **THEN** the second run reports each slow test as passed from the memo, by
  name, without running its body.

#### Scenario: A changed source reruns the tests

- **WHEN** a file under `src/` that a slow test imports, directly or through
  another module, changes between two runs
- **THEN** that test runs again, and only its passes are recorded.

#### Scenario: A change nothing reaches keeps the memo

- **WHEN** only a file that a slow test neither imports, nor is served, nor
  reads changes, such as the fixture project for a test that never copies it
- **THEN** that test is passed from the memo.

#### Scenario: The stage the browser is served is keyed

- **WHEN** a stage source changes between two runs
- **THEN** every browser test runs again, although no test imports it.

#### Scenario: An undeclared read fails the suite

- **WHEN** a module a slow test reaches starts reading a repository file by
  its path without declaring it
- **THEN** a pure test fails naming that module.

#### Scenario: A touched file is not a change

- **WHEN** only a file's modification time changes
- **THEN** the memoized pass is still reused.

### Requirement: Expensive products are memoized and verified on reuse

An expensive product a slow test builds as its input SHALL be kept in the memo
under the content hash of what produced it, with an index written after every
part of it. On every reuse each part's hash SHALL be checked, and a damaged,
partial or unverifiable entry MUST be regenerated whole. The test's assertions
SHALL still run on every run.

#### Scenario: A damaged product is regenerated

- **WHEN** a part of a memoized product is changed or removed, or its index
  is missing
- **THEN** the next use produces the whole product again rather than reusing
  any of it.

### Requirement: The cold switch ignores the memo

`npm test -- --cold`, or the environment variable `VIDEOMAKER_TEST_COLD=1`,
SHALL run every test with the memo neither read nor written. What a cold run
produces in place of memoized products SHALL be removed when the run ends,
and what a killed run left SHALL be removed by the next run; a cold run MUST
NOT leave directories in the system's temporary directory.

#### Scenario: A cold run before integration

- **WHEN** the maintainer runs `npm test -- --cold`
- **THEN** every test runs, none is reported as passed from the memo, and the
  memo is not changed.

#### Scenario: A cold run leaves nothing behind

- **WHEN** a cold run ends, or a later run starts after a cold run was killed
- **THEN** no directory the cold run made remains in the temporary directory.

### Requirement: The memo's honesty is itself tested

The suite SHALL prove, with fast tests over a tiny memoized step, that a
changed input misses, a corrupted entry is regenerated, the cold switch runs
everything, a failure is not recorded, a reuse reproduces the same verdict,
and a memoized pass is labelled as one.

#### Scenario: The memo is honest

- **WHEN** the pure tests run
- **THEN** each of those properties is asserted, and a memo that reused a
  changed input or an unlabelled pass fails them.

### Requirement: The stage is proved in components before a browser opens

The suite SHALL prove the stage's components among the pure tests, under a
simulated document and without a browser: that each shipped set renders its
declared slots and its chrome, that each shipped element draws the state it is
given, that the registry refuses an unregistered kind, a slot mismatch and a
kind registered twice by name, and that the stage's sources and the types
generated from a fixture movie's stage block pass the TypeScript check. A
failure of these tests SHALL be reported before the first slow test starts.

#### Scenario: A set loses a slot
- **WHEN** a change makes the shipped `split` render only its `left` slot and
  the maintainer runs `npm test`
- **THEN** a pure test fails naming `split` and `right` before Chromium is
  launched.

#### Scenario: Generated types out of step
- **WHEN** the fixture project's template reads a prop its stage block does
  not declare
- **THEN** the TypeScript check among the pure tests fails naming the module
  and the prop.

### Requirement: The stage is proved in a browser against the viewer double

The suite SHALL prove the stage in Chromium, with the scripted viewer double
standing in for the viewer: that what the stage reports matches each frame
requested; that posing one instant, another, then the first again gives
identical pixels; that nothing is drawn as chrome unless a set marks it; that
chrome is absent from picture-only captures; that two views in one shot are
two viewer instances and that a view keeps its instance across a cut inside
its chapter; that a project element's state reaches its component; and every
pixel proof `preview` makes. These tests SHALL be slow tests, memoized by the
content they read, the stage's sources and the fixture project included.

#### Scenario: A view across a cut
- **WHEN** the fixture movie places one view in two shots of a chapter
- **THEN** the browser test asserts that the same viewer instance is posed in
  both, and that a second view placed beside it is another instance.

#### Scenario: Chrome only where a set asks for it
- **WHEN** a fixture shot is drawn on the shipped `frame`
- **THEN** the stage reports no chrome rectangle, and the frame's pixels hold
  no masthead or bar.

### Requirement: Browser and pipeline tests sit in their own directories

Tests that drive Chromium SHALL sit under `test/browser/` and tests that run
the commands end to end under `test/pipeline/`; the slow part of the suite
SHALL select its tests by those two directories rather than by a list of
names, so a slow test added there runs serially with the others and a test
elsewhere runs among the pure ones. Stage component tests SHALL sit beside the
stage sources they test.

#### Scenario: A new browser test
- **WHEN** the maintainer adds a test file under `test/browser/`
- **THEN** `npm test` runs it among the slow tests, one at a time, after every
  pure test, with no change to the runner's configuration.

### Requirement: The worktrees of the repository share one memo

The memo SHALL be one store that every worktree of the repository reads and
writes, so that a test passed in one worktree is passed from the memo in
another holding the same content, and an expensive product made in one is
reused in another. A different content MUST miss. Two suites writing the store
at once, from two worktrees, MUST NOT damage an entry or fail because the
other published the same entry first. Outside a Git work tree the memo SHALL
be kept at the root of the checkout.

#### Scenario: A merge does not run cold

- **WHEN** a cycle worktree has passed its slow tests and the same content is
  tested in the worktree it merges into
- **THEN** those tests are passed from the memo there, by name.

#### Scenario: A different content misses

- **WHEN** two worktrees differ in a file a slow test reaches
- **THEN** the test runs in each, and each records its own pass.

#### Scenario: Two writers of one product

- **WHEN** two suites produce the same memoized product at the same time
- **THEN** both use one verified entry, and neither fails.

