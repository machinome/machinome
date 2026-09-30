## ADDED Requirements

### Requirement: The stage is proved against the real viewer when a bundle is selected

When the maintainer selects a machinome-viewer bundle by its path in the
environment variable `VIDEOMAKER_VIEWER_BUNDLE`, the suite SHALL prove the
stage in Chromium with that bundle over the fixture project's export, which
the framework's export command made: that the bundle declares at least the
Viewer API the fixture movie requires, asserted from what a mounted instance
reports; that a view's canvas fills its box on a fresh mount, after a change
of set and when a view returns after frames without it; that posing A, then
B, then A gives identical pixels across a camera move, a highlight, a hidden
layer and an instance leased from one view element to another; that a
mark's target is on screen and its text inside the frame through the
viewer's own part rectangles and projection; that the fixture movie passes
`check`, `preview` and `render` with the bundle; and it SHALL record, without
a threshold, the memory Chromium uses with one and with two instances. These
tests SHALL be slow tests, memoized with the bundle's content, never its
path, in their key. Without a selected bundle every such test SHALL be
reported as skipped with the words "no viewer bundle selected", by the
runner and by the memo's report, and MUST NOT be reported as passed. A
selected path with no file, or a file that does not define the viewer, SHALL
fail every such test, naming the path.

#### Scenario: No bundle selected
- **WHEN** the maintainer runs `npm test` without `VIDEOMAKER_VIEWER_BUNDLE`
- **THEN** every test of the viewer layer is reported skipped, "no viewer
  bundle selected", the memo's report lists each by name as skipped, and none
  is counted as passed or run.

#### Scenario: A path that is not a viewer
- **WHEN** `VIDEOMAKER_VIEWER_BUNDLE` names a file that does not exist, or a
  file that does not define `MachinomeViewer`
- **THEN** every test of the viewer layer fails, and the failure names that
  path.

#### Scenario: A bundle below the movie's API
- **WHEN** the selected bundle declares a Viewer API below the one the
  fixture movie requires
- **THEN** the API test fails naming the path, the declared and the required
  API, rather than assuming the bundle can draw the movie.

#### Scenario: The canvas the film met
- **WHEN** the stage's wait for a viewer's canvas is removed and the viewer
  layer runs with the real bundle
- **THEN** the canvas test fails, because the real viewer sizes its canvas
  on its own animation frame and shrinks a detached host's canvas to nothing.

#### Scenario: The same bundle elsewhere
- **WHEN** the same bundle's bytes are selected from another path
- **THEN** the viewer layer's passes are reused from the memo, and a bundle
  with other bytes runs the layer again.

## MODIFIED Requirements

### Requirement: One browser serves every browser test of a run

Within one run of the suite, Chromium SHALL be launched once, whichever
projects of browser tests the run includes, and the browser tests of one
project SHALL be served by one asset server. The command line SHALL keep
launching and closing its own browser and asset server for each session.

#### Scenario: Two browser tests share the browser

- **WHEN** two browser sessions run in the suite
- **THEN** no further Chromium is launched, both pages are served by the same
  asset server when their tests belong to one project, and the browser
  remains open for the next test.

#### Scenario: The viewer layer uses the run's browser

- **WHEN** `npm test` runs the slow tests and the viewer layer with a bundle
  selected
- **THEN** one Chromium serves both, and it is closed when the run ends.

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
modules of the command line when a reached test runs it; the content of a
file outside the repository that the maintainer selects for it in the
environment (the viewer bundle of the viewer layer), named by its variable
and never by its path; and always the test helpers the runner loads around a
test, the viewer double, the test's own source and the dependency lock. A
module a slow test reaches that locates a repository file by path without
declaring what it reads SHALL fail the suite, naming the module. A test whose
key is unchanged SHALL be reported as "passed from the memo", in those words,
and never as a fresh run. A modification time MUST NOT enter a key. A failure
MUST NOT be recorded, and neither MUST a skip.

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

#### Scenario: A selected file is keyed by its content

- **WHEN** the selected viewer bundle's bytes change between two runs, or
  the same bytes are selected from another path
- **THEN** the viewer layer runs again in the first case and is passed from
  the memo in the second.

#### Scenario: An undeclared read fails the suite

- **WHEN** a module a slow test reaches starts reading a repository file by
  its path without declaring it
- **THEN** a pure test fails naming that module.

#### Scenario: A touched file is not a change

- **WHEN** only a file's modification time changes
- **THEN** the memoized pass is still reused.

### Requirement: Browser and pipeline tests sit in their own directories

Tests that drive Chromium with the viewer double SHALL sit under
`test/browser/`, tests that run the commands end to end under
`test/pipeline/`, and tests that need the real viewer under `test/viewer/`;
the slow part of the suite SHALL select its tests by those directories
rather than by a list of names, so a slow test added there runs serially
with the others and a test elsewhere runs among the pure ones. The tests
under `test/viewer/` SHALL run after the other slow tests, as their own
project. Stage component tests SHALL sit beside the stage sources they test.

#### Scenario: A new browser test
- **WHEN** the maintainer adds a test file under `test/browser/`
- **THEN** `npm test` runs it among the slow tests, one at a time, after every
  pure test, with no change to the runner's configuration.

#### Scenario: A new viewer test
- **WHEN** the maintainer adds a test file under `test/viewer/`
- **THEN** `npm test` runs it in the viewer layer, after the other slow
  tests, gated on the selected bundle, with no change to the runner's
  configuration.
