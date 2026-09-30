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
identical pixels; that a pose waits for a repaint only when something outside
the views' canvases changed, and that a title whose words change between
poses still gives identical pixels posed A, B, A; that nothing is drawn as
chrome unless a set marks it; that chrome is absent from picture-only
captures; that two views in one shot are two viewer instances and that a
view keeps its instance across a cut inside its chapter; that a view
element's instance is leased to another when it leaves, draws the other's
state as a fresh instance would and is leased back when it returns, and that
no order of frames mounts more instances than one frame places views; that a
project element's state reaches its component; and every pixel proof
`preview` makes. These tests SHALL be slow tests, memoized by the content
they read, the stage's sources and the fixture project included.

#### Scenario: A view across a cut
- **WHEN** the fixture movie places one view in two shots of a chapter
- **THEN** the browser test asserts that the same viewer instance is posed in
  both, and that a second view placed beside it is another instance.

#### Scenario: A view that leaves and returns
- **WHEN** the fixture's view A is posed with a standing highlight and a
  hidden layer, then another chapter's view B with neither in another box,
  then A again, with a viewer that sizes its canvas on its own animation
  frame
- **THEN** the browser test asserts that one instance served all three, that
  the highlight was restored and the layer shown again before B was drawn,
  that each canvas filled its box, that A's pixels are identical before and
  after, and that B's equal those of a session where B is posed first.

#### Scenario: Frames in any order
- **WHEN** a frame placing A alone, one placing B alone and one placing both
  side by side are posed in each of their six orders
- **THEN** the browser test asserts that every order mounts two instances,
  and that each frame's pixels are the same in all six.

#### Scenario: Chrome only where a set asks for it
- **WHEN** a fixture shot is drawn on the shipped `frame`
- **THEN** the stage reports no chrome rectangle, and the frame's pixels hold
  no masthead or bar.

#### Scenario: A pose that changes only a view
- **WHEN** the fixture's frame of the view alone is posed, then posed again,
  then posed at another instant of its shot
- **THEN** the browser test asserts that neither later pose requests an
  animation frame.

#### Scenario: A title whose words change
- **WHEN** a fixture frame with a title is posed, then posed with the title's
  words changed, then posed as first
- **THEN** the browser test asserts that the changed pose requests animation
  frames for a repaint, that its pixels differ, and that the first and last
  poses give identical pixels.

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

### Requirement: The layout `check` measures is the layout a frame is drawn in

The suite SHALL prove in Chromium, with the stage bundle of the fixture tour,
that the boxes `check` measures for a set equal the boxes the stage reports
when a frame of that set is posed at the same size, for the shipped `frame`
and `split` and for the tour's own `Playbill` and `PlaybillSplit`, the box of
a picture placed in a slot included, and that a slot whose box is as tall as
what it holds is reported as such rather than compared. The pipeline tests
SHALL count the Chromium launches of the command line's own process.

#### Scenario: The plate measured and drawn
- **WHEN** the probe measures `Playbill` at 1280×720 and the tour's frame of
  shot `still`, which places the still in `plate`, is posed at 1280×720
- **THEN** the posed frame's slot boxes equal the probe's for every slot the
  probe trusts, the picture's element box equals the probe's picture box for
  `plate`, and `headline` is reported as sized by what it holds.

#### Scenario: A check without pictures launches nothing
- **WHEN** the command line's `check` runs on the fixture movie `minimal`
- **THEN** its process launches no Chromium, and on the tour it launches one.

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

