## MODIFIED Requirements

### Requirement: An arrow or label follows its target

The author SHALL add timed `arrow` and `label` marks to a view, each aimed at
one part (a production layer name or one assembly path) or one world point:
in an episode, annotations of a shot with shot-local `from`/`to` seconds; in
a movie document, `arrow` and `label` actions on a view element the shot
places, lasting from their cue's `at` to its `until`. Each mark belongs to its
view. While a mark is active, every frame SHALL draw it at the target's
on-screen position for that frame's model pose and that view's camera: an
arrow runs from text fixed at an authored `place` to a tip on the target; a
label's text sits at an authored `offset` from the target. In a movie
document `place` and `offset` SHALL be fractions of the view element's box,
wherever the set puts it. In an episode they SHALL keep their safe-area
units, and the paper sets SHALL draw them at the same positions on screen as
the safe area gives. Marks MUST be drawn over their view and MUST NOT change
the model, the camera or the visibility of any part.

#### Scenario: Point at a moving pawl
- **WHEN** the *Revolutions* pawls shot adds an arrow from the words "Pulls one
  tooth" to the driving pawl for the downstroke
- **THEN** on every frame of that interval the arrow's tip lies on the driving
  pawl's on-screen bounds, moving as the pawl moves, and the words stay where the
  author placed them.

#### Scenario: Name a rope beside it
- **WHEN** the author labels a rope "Rope 1" with a small offset
- **THEN** the label travels with the rope's on-screen position through the cue.

#### Scenario: Annotation ends on time
- **WHEN** video time reaches the annotation's `to`, or its cue's `until`, or
  the shot cuts
- **THEN** the annotation is gone from that frame.

#### Scenario: An arrow on a view in the split
- **WHEN** a shot of *Cut and Advance* places `mill` in `LeonardoSplit`'s
  `right` and an arrow on `mill` has `place: [0.1, 0.2]`
- **THEN** the arrow's words sit a tenth of the way across and a fifth of the
  way down the right-hand view's box, not the frame's.

### Requirement: Invalid annotations are refused before rendering

`check`, `preview` and `render` MUST refuse, naming the shot: an annotation with
an unknown kind; with both or neither of a part and a point; naming a layer that
production does not define or an assembly path the exported model does not
contain; with times outside the shot or not increasing; an arrow without a place
in the safe area or with a place outside it; a label without text; a target the
same shot hides; and an episode using annotations without a declared safe inset.
In a movie document they MUST refuse the same faults of a mark action, naming the
chapter, the shot, the view and the action: an arrow with both or neither of a
part and a point, or without a `place`; a label without text; a part the export
does not contain or the view hides; and a mark on an element that is not a view.

#### Scenario: Misspelled part
- **WHEN** an annotation names `[Feed mechanism, Drving pawl]`
- **THEN** `check` fails and names the missing path before any frame is rendered.

#### Scenario: Arrow at a hidden part
- **WHEN** a shot hides the `feed` layer and points an arrow at the driving pawl
- **THEN** `check` refuses the contradiction instead of drawing an arrow at nothing.

### Requirement: An annotation never points at nothing

`preview` and `render` MUST refuse a frame on which an active annotation's target
is not on screen within its view's box, or whose text leaves the frame, naming
the shot, the annotation, its text and the video time. They MUST NOT drop the
annotation silently.

#### Scenario: Part leaves the frame
- **WHEN** a moving part leaves the camera's view while its arrow is active
- **THEN** preview or render stops with the shot, annotation and time, and the
  author shortens the cue or reframes.

### Requirement: Older episodes and older viewers are handled explicitly

Episodes in format `machinome-video-draft/0.2` SHALL parse and render with any
Viewer API 21 or later. Annotations SHALL require format
`machinome-video-draft/0.3` and Viewer API 28, and a movie document's marks
SHALL require Viewer API 28. `check`, `preview` and `render` MUST refuse an
episode or movie using annotations against a viewer declaring an older API,
with a message naming the field, the shot, the required and the declared API.

#### Scenario: Old episode, old viewer
- **WHEN** the unchanged sawmill or *Revolutions* episode is checked and previewed
  with the Viewer API 27 bundle
- **THEN** it passes as it did before this change.

#### Scenario: Annotated episode, old viewer
- **WHEN** an episode with annotations is previewed with a Viewer API 27 bundle
- **THEN** preview refuses before capturing, saying that annotations in that shot
  need Viewer API 28 and the bundle declares 27.

#### Scenario: Annotations in a 0.2 episode
- **WHEN** an episode still declaring format 0.2 carries `annotations`
- **THEN** `check` refuses it and asks for format 0.3, rather than ignoring the field.

### Requirement: A ring singles out a part without words

In a format 0.4 episode, the author SHALL be able to add an annotation of kind
`ring` aimed at a part (a production layer name or one assembly path), with
shot-local `from`/`to` seconds and an optional `padding` in safe-area widths;
in a movie document, a `ring` action on a view, with an optional `padding` in
widths of the view element's box. While it is active, every frame SHALL draw
a ring in the accent colour that encloses the part's whole on-screen
rectangle, grown by the padding, following the part as it moves and as the
camera moves. An episode's padding SHALL grow the ring by the same pixels
through the paper sets as the safe area gives. A layer holding several parts
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

### Requirement: Invalid rings and entrances are refused

`check`, `preview` and `render` MUST refuse, naming the shot and the annotation:
a kind other than arrow, label or ring; a ring aimed at a world point, or given
text, a place or an offset; a padding outside `[0, 0.25]` or on an arrow or a
label; an unknown entrance or exit field or kind; an easing name outside the
five; a draw-on on a label; an entrance or exit shorter than two frames or
longer than the cue; an entrance and exit that together exceed the cue; and any
of `ring`, `padding`, `enter` or `leave` in a 0.2 or 0.3 episode, which MUST be
asked to change its format rather than be rendered without them. A ring on a
part the shot hides MUST be refused as an arrow's target is. A movie
document's `ring`, `label` and `arrow` actions MUST be refused for the same
faults of their fields, entrances and exits, naming the chapter, the shot, the
view and the action.

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
wholly on its view's box, or on which the ring leaves the frame, naming the
shot, the annotation and the video time, including frames where the ring is
entering or leaving. They MUST NOT clip or drop the ring silently.

#### Scenario: A ringed part moves out of view
- **WHEN** a ringed part moves partly past the edge of its view during its cue
- **THEN** preview or render stops with the shot, the ring and the time, and the
  author shortens the cue or reframes.

#### Scenario: A padding too large for the frame
- **WHEN** a ring's padding makes it extend past the frame's edge
- **THEN** preview or render stops, naming the ring, and the author reduces the
  padding.

#### Scenario: A ring on a view in half the frame
- **WHEN** a ringed part is inside the frame but outside the box of the view
  in `LeonardoSplit`'s `right`
- **THEN** preview or render stops, naming the ring, rather than drawing it
  over the source panel beside the view.

### Requirement: Older episodes and plain 0.4 marks are unchanged

Episodes in formats 0.2 and 0.3 SHALL be drawn with the marks their format
allows and no other, and a 0.4 arrow or label declaring none of `padding`,
`enter` or `leave` SHALL be drawn exactly as the same annotation in 0.3 on the
same sets. Rings and entrances MUST NOT raise the Viewer API an annotated
episode needs.

#### Scenario: The 0.3 demos are unchanged
- **WHEN** `demo-annotate-a-part` and `demo-feed-mechanism` are previewed with
  the same viewer bundle, once as written in 0.3 and once with their format
  changed to 0.4 and nothing else
- **THEN** their stills are byte-for-byte identical.
