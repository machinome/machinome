## MODIFIED Requirements

### Requirement: The viewer layer proves the fixture take

When a bundle is selected, the viewer layer SHALL prove the clocked take on
the fixture counter's real export, recorded by the Python side: that the
bundle declares at least Viewer API 29, asserted from a mounted instance;
that every step of the take, replayed on the viewer's machine from its
recorded bank, returns the recorded request exactly; that posing one bank,
then another, then the first gives identical pixels; that the bank the
stage reports at each mark where a shot begins is the recorded one; that a
mark on a part the take moves follows the part from one bank to another;
that a mounted view shows no viewer control; that the fixture movie `count`
passes `check`, `preview` and `render`; and that a copy of the take with
one commit's target forged is refused, naming the step and the field. The
browser layer SHALL prove the same pose, refusals, pixels and mark with the
viewer double's machine, whose answers a test can make disagree with the
take, and whose part rectangles are a function of the bank it holds, as
they are a function of the loop time without a machine. The mark SHALL be
proved at both layers by one assertion. A double's machine that names no
input for its part rectangles to follow, or one its bank does not hold,
SHALL be refused when the double is mounted, naming the input.

#### Scenario: The recorded take on the real viewer
- **WHEN** the viewer layer runs with a Viewer API 29 bundle
- **THEN** each of the counter's three steps, replayed on the viewer, gives
  the recorded `origin`, `end` and commits, and the replay is reported as
  matched.

#### Scenario: A forged commit
- **WHEN** the first commit of `step-2` is made to write units 7 in a copy
  of the take
- **THEN** the session stops before its first capture naming `step-2` and
  `commits[0].targets.units`.

#### Scenario: A bundle below the take's API
- **WHEN** the selected bundle declares Viewer API 28
- **THEN** the take's API test fails naming the path, 28 and 29.

#### Scenario: A mark between two banks
- **WHEN** a ring on the counter's units drum is posed at the take's start,
  at the mark `one`, and at the take's start again, with the viewer double
  and, when a bundle is selected, with the real viewer
- **THEN** each pose reports the bank its frame asks for, the view's box is
  the same at both instants, the ring's rectangle and anchor at `one`
  differ from those at the start, and the start posed again gives the first
  pose's rectangle, anchor and pixels exactly.

#### Scenario: A double whose parts stand still
- **WHEN** the browser layer's take is posed with the double's machine at
  the instants above, and the stage reads a part's rectangle before
  restoring the bank, or the double's rectangles do not follow the bank
- **THEN** the mark proof fails at layer 5, before the viewer layer runs.

#### Scenario: A double's machine that follows nothing
- **WHEN** a test mounts the double with a machine that names no input to
  follow, or names `crank_arm`, which its bank does not hold
- **THEN** the mount is refused naming `machine.follows`, and `crank_arm`
  with the ids the bank holds.
