## ADDED Requirements

### Requirement: The viewer layer proves the fixture take

When a bundle is selected, the viewer layer SHALL prove the clocked take on
the fixture counter's real export, recorded by the Python side: that the
bundle declares at least Viewer API 29, asserted from a mounted instance;
that every step of the take, replayed on the viewer's machine from its
recorded bank, returns the recorded request exactly; that posing one bank,
then another, then the first gives identical pixels; that the bank the
stage reports at each mark where a shot begins is the recorded one; that a
mounted view shows no viewer control; that the fixture movie `count` passes
`check`, `preview` and `render`; and that a copy of the take with one
commit's target forged is refused, naming the step and the field. The
browser layer SHALL prove the same pose, refusals and pixels with the viewer
double's machine, whose answers a test can make disagree with the take.

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
