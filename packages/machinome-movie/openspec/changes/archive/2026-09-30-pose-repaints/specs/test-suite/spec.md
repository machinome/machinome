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
view keeps its instance across a cut inside its chapter; that a project
element's state reaches its component; and every pixel proof `preview`
makes. These tests SHALL be slow tests, memoized by the content they read,
the stage's sources and the fixture project included.

#### Scenario: A view across a cut
- **WHEN** the fixture movie places one view in two shots of a chapter
- **THEN** the browser test asserts that the same viewer instance is posed in
  both, and that a second view placed beside it is another instance.

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
