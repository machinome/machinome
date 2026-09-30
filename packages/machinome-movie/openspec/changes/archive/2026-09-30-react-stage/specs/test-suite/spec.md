## ADDED Requirements

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
