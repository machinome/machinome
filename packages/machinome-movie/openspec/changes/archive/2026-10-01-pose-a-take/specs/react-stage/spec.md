## ADDED Requirements

### Requirement: A view on a take is posed by restoring its bank

For a view element whose frame state carries `bank`, the stage SHALL mount
its viewer instance without a loop time, and on every frame SHALL restore
the bank on the viewer's machine handle, `machine().restore({identity,
bank})` with the take's identity and the whole bank, then set the camera;
it MUST NOT set a loop time for that view. The view's report SHALL carry
the bank the machine holds after the pose. At mount, the stage MUST refuse,
naming the view and the shot: a viewer that gives no machine handle for the
clocked document, and a machine whose identity differs from the take's,
naming both identities and `take.identity`. A movie on a take SHALL need
Viewer API 29, for the reason `clocked take`, and the stage's refusal of an
older viewer SHALL name it.

#### Scenario: A pose by bank
- **WHEN** the stage draws a frame of the counter whose view carries a bank
  with crank 1800 and units 5
- **THEN** the viewer's machine is restored to that bank with the
  counter's identity, the camera is set after it, no loop time is set, and
  the view reports that bank.

#### Scenario: A viewer without a machine
- **WHEN** the viewer mounted for a view on a take gives no machine handle
- **THEN** the stage refuses at mount naming the view, the shot and the
  machine it lacks.

#### Scenario: Another machine
- **WHEN** the machine's identity differs from the take's
- **THEN** the stage refuses at mount naming the view, both identities and
  `take.identity`.

#### Scenario: The requirement named
- **WHEN** the movie films a take and also highlights a part
- **THEN** it needs Viewer API 29, and the refusal of a viewer declaring 28
  names `clocked take` among its reasons.

### Requirement: A view's canvas is its box's size, neither smaller nor larger

The stage SHALL wait, a bounded number of animation frames, for every
view's canvas to fill its box and exceed it by no more than one pixel in
either dimension, whenever the view was mounted, placed again or its box
changed size, so a canvas left larger by a shrinking box is waited for as a
canvas left smaller by a growing one is. The renderer MUST refuse a posed
frame whose view's canvas is more than one pixel larger than its box in
either dimension, `Viewer canvas exceeds its view`, naming the view, the
shot, the time and both sizes, as it refuses a canvas that does not fill
it.

#### Scenario: A canvas that follows a shrink late
- **WHEN** a reframe shrinks a view's box and the viewer resizes its canvas
  some animation frames later
- **THEN** the stage poses the view only once its canvas is the box's size
  within a pixel.

#### Scenario: A canvas that never follows
- **WHEN** a view's box shrinks and its canvas stays at the old size
- **THEN** the renderer stops naming the view and `Viewer canvas exceeds
  its view`.
