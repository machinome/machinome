## ADDED Requirements

### Requirement: A pose waits for what can change the picture

Posing a frame SHALL end with a repaint of the whole page when the frame is
a proof pose of `preview`, when a view's viewer was mounted, placed again
after shots without it, or its box resized on that pose, or when anything
the page draws outside the pixels of the views' canvases (an element, an
attribute, a word) differs from what the page drew at its last repaint. Any
other pose, in which at most the pixels of the views' canvases change, SHALL
NOT wait for a repaint. Whatever a pose waits for, its pixels MUST NOT depend on the
frames posed before it: posing one instant, another, then the first again
SHALL give identical pixels, and an incremental render SHALL equal a cold
one byte for byte.

#### Scenario: The mill turns in a held shot
- **WHEN** consecutive frames of a shot of *Cut and Advance* change only the
  camera and model time of the mill's view, with no mark, word, picture or
  layout changing
- **THEN** each of those poses after the first returns without waiting for
  an animation frame, and each frame's pixels are those a render of that
  frame alone gives.

#### Scenario: A title changes its words
- **WHEN** a frame is posed, then the same frame with its title's words
  changed, then the first again
- **THEN** the second and third poses repaint the whole page, and the first
  and third give identical pixels.

#### Scenario: The same frame posed twice
- **WHEN** a frame is posed twice in a row
- **THEN** the second pose requests no animation frame and gives the same
  pixels as the first.
