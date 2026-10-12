## ADDED Requirements

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

A slow test's pass SHALL be kept in an ignored memo directory, keyed on the
content of everything the test reads (the sources, the command line, the
fixtures, the test helpers and viewer double, the test's own source, the
dependency lock) and the versions of Node, Chromium, FFmpeg, Git and the
stage's fonts, obtained once per run. A test whose key is unchanged SHALL be
reported as "passed from the memo", in those words, and never as a fresh run.
A modification time MUST NOT enter a key. A failure MUST NOT be recorded.

#### Scenario: An unchanged test is passed from the memo

- **WHEN** the maintainer runs `npm test` twice with nothing changed
- **THEN** the second run reports each slow test as passed from the memo, by
  name, without running its body.

#### Scenario: A changed source reruns the tests

- **WHEN** a file under `src/` changes between two runs
- **THEN** every slow test runs again, and only its passes are recorded.

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
SHALL run every test with the memo neither read nor written.

#### Scenario: A cold run before integration

- **WHEN** the maintainer runs `npm test -- --cold`
- **THEN** every test runs, none is reported as passed from the memo, and the
  memo directory is not changed.

### Requirement: The memo's honesty is itself tested

The suite SHALL prove, with fast tests over a tiny memoized step, that a
changed input misses, a corrupted entry is regenerated, the cold switch runs
everything, a failure is not recorded, a reuse reproduces the same verdict,
and a memoized pass is labelled as one.

#### Scenario: The memo is honest

- **WHEN** the pure tests run
- **THEN** each of those properties is asserted, and a memo that reused a
  changed input or an unlabelled pass fails them.
