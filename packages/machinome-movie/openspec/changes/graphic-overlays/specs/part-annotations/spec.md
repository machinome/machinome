## ADDED Requirements

### Requirement: A ring singles out a part without words

In a format 0.4 episode, the author SHALL be able to add an annotation of kind
`ring` aimed at a part (a production layer name or one assembly path), with
shot-local `from`/`to` seconds and an optional `padding` in safe-area widths.
While it is active, every frame SHALL draw a ring in the accent colour that
encloses the part's whole on-screen rectangle, grown by the padding, following
the part as it moves and as the camera moves. A layer holding several parts
SHALL be ringed as one. A ring MUST carry no words and MUST NOT change the
model, the camera or the visibility of any part.

#### Scenario: Ring the pawl the caption is about
- **WHEN** the restaged *Revolutions* `pawls` shot rings the driving pawl while
  the caption says "Pull · advance one tooth" and the holding pawl while it says
  "Return · hold that progress"
- **THEN** on every frame of each interval a ring encloses that pawl's on-screen
  bounds, moving with it, and the audience can tell which pawl each caption
  means without an added word.

#### Scenario: Ring a rope section while the camera moves
- **WHEN** the *Revolutions v2* `two-rope-reduction` shot rings the large-radius
  rope reserve and then the central small-radius take-up while the camera
  travels from `rope-wide` to `reduction`
- **THEN** each ring stays around its section throughout the move.

### Requirement: A callout is an arrow with words

Words on a plate with a leader to the part they name SHALL be written as an
`arrow` with `text`; there MUST NOT be a second kind for the same mark.

#### Scenario: Looking for a callout
- **WHEN** an author writes `kind: callout`
- **THEN** `check` refuses the unknown kind, and the format's documentation shows
  the arrow with text as the callout.

### Requirement: Marks arrive and leave on the campaign's curves

In a format 0.4 episode, every annotation (arrow, label or ring) SHALL accept an
optional `enter`, a `fade` or a stroke `draw`-on, and an optional `leave`, a
`fade`, each with a duration and an optional easing name from the campaign's
five (default `smooth`). An entrance SHALL occupy the first part of the cue and
an exit its last part, so the mark is gone at `to` as before. A fade SHALL
change only the mark's opacity; a draw-on SHALL reveal a ring's stroke around
the ring from its top, clockwise, and an arrow's stroke from its words to its
tip, the words shown from the start. At the entrance's first frame nothing of a
faded mark, and none of a drawn stroke, SHALL be visible. An entrance or exit
MUST NOT change where the mark is: from the entrance's end when that instant is
inside the cue, and at the exit's start, the mark SHALL be drawn exactly as it
is without one. The mark SHALL keep
following its part throughout.

#### Scenario: One ring leaves as the next is drawn
- **WHEN** the restaged `pawls` shot gives the driving pawl's ring
  `enter: {kind: draw, duration: 0.8}` and `leave: {kind: fade, duration: 0.4}`,
  and the holding pawl's ring `enter: {kind: draw, duration: 0.8}` from 5.366 s
- **THEN** the first ring draws itself round the pawl in its first 0.8 s, fades
  away in the 0.4 s before 5.366 s, and the second ring begins drawing at 5.366 s.

#### Scenario: An arrow draws itself to the pawl
- **WHEN** the restaged `name-the-pawls` shot gives its arrow
  `enter: {kind: draw, duration: 0.8, ease: out}` and its label
  `enter: {kind: fade, duration: 0.5}`
- **THEN** the words "Driving pawl" are there from 0.2 s and the arrow grows from
  them to the pawl, arriving at rest at 1.0 s; the label fades in from nothing
  between 1.9 s and 2.4 s instead of appearing in one frame.

#### Scenario: A mark into a transition
- **WHEN** a cue that runs to its shot's end has a `leave` and the next shot
  enters by a transition
- **THEN** the mark has left by the shot's end and does not reappear in the
  outgoing picture during the transition; a cue without `leave` stays, as
  transitions already continue it.

### Requirement: Marks with entrances are reproducible

A frame with a mark entering or leaving MUST depend only on its video time and
the episode. Seeking away and back, or resuming an interrupted render, SHALL
yield identical pixels.

#### Scenario: Revisit a half-drawn ring
- **WHEN** preview poses an instant in the middle of a ring's draw-on, poses
  another instant, and returns
- **THEN** the pixels match the first capture exactly.

### Requirement: Preview proves entrances and exits in pixels

`preview` SHALL sample every entrance and exit at its first frame, midpoint and
end when that instant lies inside the half-open cue, save those stills, and
prove: that a fade's midpoint is the blend of same-instant opaque full-mark
and absent-mark raster captures that its easing predicts, with every other cue
held as authored, within 2 levels of 255 on every pixel; that a draw-on's
midpoint shows part of the stroke and not the rest; that a faded or drawn
entrance starts from nothing; and that an active entrance end and the exit's
start equal the mark drawn without them. If `enter.duration` equals the cue's
duration, preview MUST record the `enter-end` check as skipped because it falls
at the exclusive `to` boundary, while checking the valid in-cue samples. A failed
proof MUST stop preview, naming the shot, the annotation, the check and the
time, and keep the compared images.

#### Scenario: A fade that is not the predicted blend
- **WHEN** a label's fade reaches the picture at an opacity other than its
  easing's value at the midpoint
- **THEN** preview stops, naming the shot, the label and the time, and keeps the
  composed, full and without images for inspection.

### Requirement: Invalid rings and entrances are refused

`check`, `preview` and `render` MUST refuse, naming the shot and the annotation:
a kind other than arrow, label or ring; a ring aimed at a world point, or given
text, a place or an offset; a padding outside `[0, 0.25]` or on an arrow or a
label; an unknown entrance or exit field or kind; an easing name outside the
five; a draw-on on a label; an entrance or exit shorter than two frames or
longer than the cue; an entrance and exit that together exceed the cue; and any
of `ring`, `padding`, `enter` or `leave` in a 0.2 or 0.3 episode, which MUST be
asked to change its format rather than be rendered without them. A ring on a
part the shot hides MUST be refused as an arrow's target is.

#### Scenario: A draw-on on a label
- **WHEN** a label says `enter: {kind: draw, duration: 0.5}`
- **THEN** `check` refuses it, saying a label has no stroke to draw and to enter
  with a fade.

#### Scenario: Entrance and exit overlap
- **WHEN** a 1.2-second ring has an entrance of 0.8 s and an exit of 0.6 s
- **THEN** `check` refuses it, naming the shot, the annotation and both durations.

#### Scenario: A ring in a 0.3 episode
- **WHEN** an episode declaring format 0.3 carries `kind: ring`
- **THEN** `check` refuses it and asks for format 0.4.

### Requirement: A ring never encloses what is not there

`preview` and `render` MUST refuse a frame on which an active ring's part is not
wholly on the model stage, or on which the ring leaves the frame, naming the
shot, the annotation and the video time, including frames where the ring is
entering or leaving. They MUST NOT clip or drop the ring silently.

#### Scenario: A ringed part moves out of view
- **WHEN** a ringed part moves partly past the edge of the stage during its cue
- **THEN** preview or render stops with the shot, the ring and the time, and the
  author shortens the cue or reframes.

#### Scenario: A padding too large for the frame
- **WHEN** a ring's padding makes it extend past the frame's edge
- **THEN** preview or render stops, naming the ring, and the author reduces the
  padding.

### Requirement: Older episodes and plain 0.4 marks are unchanged

Episodes in formats 0.2 and 0.3 SHALL produce exactly the frames and pixels they
produced before this change, and a 0.4 annotation declaring none of `padding`,
`enter` or `leave` SHALL be drawn exactly as the same annotation in 0.3. Rings
and entrances MUST NOT raise the Viewer API an annotated episode needs.

#### Scenario: The 0.3 demos are unchanged
- **WHEN** `demo-annotate-a-part` and `demo-feed-mechanism` are previewed with
  the same viewer bundle before and after this change
- **THEN** their stills are byte-for-byte identical.
