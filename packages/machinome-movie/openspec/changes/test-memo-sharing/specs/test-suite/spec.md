## MODIFIED Requirements

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

#### Scenario: A changed source reruns the tests that reach it

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

## ADDED Requirements

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
