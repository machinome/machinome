## MODIFIED Requirements

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
