# shot-transitions Specification

## Purpose
Join two shots by a fade through a colour, a dissolve, a wipe or a slide, and
fade the film in and out, in format 0.4 and in a movie document, and, in a
movie document, by a reframe that moves a view's box live from one set into
the next (the `reframe-join` change, 1 October 2026), without moving any
shot's timing and with every transition frame a function of video time
proved in pixels.
## Requirements
### Requirement: A shot can come in from the one before it

In format `machinome-video-draft/0.4` the author SHALL be able to give any shot
but the first a `transition` that joins it to the shot before it: a `fade`
through a colour, a `dissolve`, a `wipe` or a `slide`, with a duration in video
seconds and an easing name from the campaign vocabulary (default `smooth`). A
wipe or slide SHALL take a direction, `left` or `right` (default `left`),
naming the way the motion goes. A shot without `transition` SHALL begin with a
hard cut, as before.

#### Scenario: Dissolve from the machine into the source
- **WHEN** the demo's source shot declares `transition: {kind: dissolve,
  duration: 1}` after the moving whole machine
- **THEN** for the first second of the source shot the machine fades away as
  the code panel and its model view fade in, and from then on the source shot
  is seen alone.

#### Scenario: Back to the machine through the paper colour
- **WHEN** the shot after the source declares `transition: {kind: fade,
  duration: 1.2}`
- **THEN** the source picture fades to the paper colour, the plain colour is
  seen at the midpoint, and the moving mechanism fades up from it; code and
  machine are never on screen together.

#### Scenario: Slide and wipe
- **WHEN** a shot declares `transition: {kind: slide, duration: 0.8,
  direction: left}`, and a later one `{kind: wipe, duration: 0.8, direction:
  right}`
- **THEN** in the slide both pictures travel left, the new one entering from
  the right edge and the frame always covered; in the wipe a straight edge
  travels right, revealing the new picture from the left edge.

### Requirement: The film can fade in and fade out

The first shot SHALL accept `fadeIn` and the last shot `fadeOut`, each with a
duration, an optional easing and an optional colour. The film's first frame
SHALL be the plain colour when it fades in, and its last frame SHALL be the
plain colour when it fades out, outside the chrome its set draws. The fade
colour SHALL default to the film's `style.background` and MAY be set to any
quoted `#rrggbb`.

#### Scenario: A paper film fades up from the page
- **WHEN** a cream-paper film's first shot declares `fadeIn: {duration: 1.5}`
- **THEN** its first frame shows the paper colour with the masthead, and the
  moving machine appears over one and a half seconds.

#### Scenario: Fade out to black on request
- **WHEN** the last shot declares `fadeOut: {duration: 2, color: "#000000"}`
- **THEN** the picture darkens over the last two seconds and the film's last
  frame is black outside the masthead.

#### Scenario: A set without chrome fades whole
- **WHEN** the first shot of a movie document, drawn in the shipped `frame`,
  fades in
- **THEN** its first frame is the plain colour everywhere.

### Requirement: Transitions leave the screenplay's timing alone

A transition MUST NOT change any shot's `start` or `end`. It SHALL occupy the
first seconds of the shot that declares it, whose model time, camera, overlays,
annotations, highlights, code typing and narration keep the times the author
wrote. Narration audio and captions MUST be unaffected. The chrome a set
draws, such as the paper sets' masthead, SHALL stay in place through every
transition.

#### Scenario: Narration starts on time through a dissolve
- **WHEN** a shot whose narration starts 0.2 s after its `start` comes in with
  a one-second dissolve
- **THEN** the narration and its captions start at the same instant as with a
  hard cut, while the picture is still dissolving.

#### Scenario: The masthead holds through a slide
- **WHEN** a shot of an episode comes in with a slide
- **THEN** both pictures travel while the masthead stays where the paper set
  draws it, on every frame of the slide.

### Requirement: The outgoing shot keeps moving while it is still seen

While a transition still shows the outgoing shot past its `end`, that shot
SHALL continue: its model runs on at the rate it had at its end (a held model
stays held), its camera holds its last position, every cue that ran to its end
stays on, and its code panel holds its completed text. The model MUST NOT be
asked for a time beyond the export's duration.

#### Scenario: The saw keeps stroking through the dissolve
- **WHEN** the whole-machine shot dissolves into the source shot
- **THEN** the saw and wheel keep moving at their pace until the machine has
  faded away, rather than stopping at the cut.

#### Scenario: An arrow that runs to the cut stays with its part
- **WHEN** an arrow is active until the end of the outgoing shot and that shot
  is dissolved into the next
- **THEN** the arrow keeps following its part while the outgoing picture is
  visible, and production stops, naming the outgoing shot and the time, if the
  part leaves the frame during that tail.

### Requirement: Transition frames are reproducible

A frame inside a transition MUST depend only on its video time and the episode.
Seeking away and back, or resuming an interrupted render, SHALL yield
identical pixels.

#### Scenario: Revisit a dissolving instant
- **WHEN** preview poses the midpoint of a dissolve, poses another instant and
  returns
- **THEN** the two captures of the midpoint are identical.

### Requirement: Preview proves each transition in pixels

`preview` SHALL sample each transition at its first frame, quarters, midpoint
and last frame, and SHALL prove from the plain frames of the two shots at the
same instant that: a dissolve's midpoint is their blend at the eased progress
within 2 levels of 255; a wipe's midpoint is exactly the outgoing picture on
one side of the edge and the incoming on the other; a slide's midpoint is
exactly the two pictures at their offsets; a fade blends its colour with the
picture as its easing predicts, and is exactly the colour at its full point.
Every proof SHALL leave out of its comparison the chrome rectangles the stage
reports, and only those. A failed proof MUST stop preview and keep the images
it compared.

#### Scenario: A dissolve that does not blend
- **WHEN** the composed midpoint of a dissolve differs from the predicted blend
  by more than 2 levels anywhere outside the reported chrome
- **THEN** preview stops, naming the shot and the time, and keeps the outgoing,
  incoming and composed images for inspection.

#### Scenario: The bottom band is proved
- **WHEN** a fade to a colour reaches its full point on a paper set
- **THEN** every pixel outside the masthead's rectangles, the bottom edge of
  the frame included, is proved to be exactly the colour.

### Requirement: Invalid transitions are refused before rendering

`check`, `preview` and `render` MUST refuse, naming the shot: a transition,
`fadeIn` or `fadeOut` in a 0.2 or 0.3 episode; an unknown field, kind,
direction or easing; a direction on a fade or dissolve, or a colour on a
dissolve, wipe or slide; a colour that is not a quoted `#rrggbb`, including a
defaulted `style.background`; a duration shorter than two frames; a
transition longer than either shot it joins, or a fade longer than its shot;
`transition` on the first shot, `fadeIn` on any other shot, `fadeOut` on any
shot but the last; a shot whose incoming transition and fade-out together are
longer than it; and an outgoing shot whose continued model would pass the
export's duration.

#### Scenario: A dissolve longer than the shot before it
- **WHEN** a five-second dissolve follows a four-and-a-half-second shot
- **THEN** `check` refuses, naming both shots and their lengths.

#### Scenario: The machine would run past the export
- **WHEN** the outgoing shot's model ends at the export's last second and still
  moving, and the next shot dissolves in
- **THEN** `check` refuses, naming the outgoing shot, the model second it would
  reach and the export's duration, and asks for an earlier end or a shorter
  transition.

#### Scenario: A misspelled duration
- **WHEN** a transition is written `{kind: dissolve, durration: 1}`
- **THEN** `check` refuses the unknown field instead of cutting hard.

### Requirement: Older episodes are unchanged

Episodes in formats `machinome-video-draft/0.2` and `0.3` SHALL parse and
render with hard cuts at every boundary. Transitions SHALL require format
`machinome-video-draft/0.4`; a 0.2 or 0.3 episode that carries one MUST be
refused and asked to change its format, never rendered with hard cuts in its
place. Adding a transition to one shot SHALL change only the frames of that
transition: every other frame of the film, on the same sets, keeps its
pixels. Transitions MUST NOT raise the Viewer API an episode needs.

#### Scenario: A 0.3 episode with a transition
- **WHEN** the feed-mechanism demo, still in format 0.3, gains a `transition`
- **THEN** `check` refuses it and asks for format 0.4.

#### Scenario: Existing films
- **WHEN** the sawmill rehearsal, the *Revolutions* episodes and the 0.3 demos
  are checked and previewed unchanged
- **THEN** they pass, with a hard cut at every boundary, drawn on the paper
  sets as every episode is.

#### Scenario: One transition added
- **WHEN** a 0.4 shot gains a one-second dissolve and the episode is rendered
  again with the same viewer, browser and output settings
- **THEN** only the frames of that first second differ from the render
  without it.

### Requirement: A view can be reframed from one set into the next

A movie document SHALL accept the transition `{"kind": "reframe",
"duration", "ease"?}` on any shot but the film's first, joining it to the
shot before it, with an easing of the vocabulary (default `smooth`). A
reframe SHALL require at least one view element placed in both shots. For
the join's duration the live page SHALL show the incoming shot's set,
slots, elements and chrome: each view element placed in both shots SHALL be
drawn in a box that moves from the box of the slot holding it in the
outgoing set to the box of the slot holding it in the incoming set,
interpolated by the join's eased progress, with exactly the camera, lens and
model time the incoming shot's timeline gives at that instant; every other
element the incoming shot places SHALL be drawn at an opacity equal to the
eased progress; the outgoing shot's elements that the incoming shot does not
place SHALL NOT be drawn. A reframe frame SHALL be drawn live, without
captures or composition, and the resolved frame SHALL carry the join with
its progress and, for each moving view, the box it is drawn in as fractions
of the frame. The join SHALL NOT change any shot's timing; a cue of the
incoming shot, a `move` included, SHALL run under it.

#### Scenario: The Curta shrinks into the right half
- **WHEN** a shot of *Addition* places the Curta's view in the whole frame
  and the next shot of its chapter places the same view in the split set's
  right slot and the source panel in its left, coming in by
  `{"kind": "reframe", "duration": 1.2}`
- **THEN** for 1.2 s the Curta's box shrinks from the whole frame to the
  right half while its camera holds and its take runs on, the source panel
  fades in on the left, and from then on the split shot is seen alone.

#### Scenario: The ends of the join
- **WHEN** the fixture tour's `question` comes in from `hook` by
  `Reframe(0.8)`
- **THEN** at the join's first frame `opening.wide` is in the box of
  `Playbill`'s `stage` and the tally and title are not seen, at its
  midpoint the tally's and the title's boxes are at the eased progress's
  opacity, and at its end the frame is `question`'s without a join.

#### Scenario: Elements the incoming shot does not place
- **WHEN** the outgoing shot places a title that the incoming shot does not
- **THEN** the title is not drawn on any frame of the reframe.

### Requirement: Preview proves each reframe

`preview` SHALL sample each reframe at its first frame, quarters, midpoint
and last frame, and SHALL prove: on every posed reframe frame, that each
moving view's box is the frame's box within one pixel and its canvas fills
it, and that every other element's opacity is the join's progress; at its
first frame, that each moving view's box is its outgoing slot's box within
one pixel; at its midpoint, that the faded elements' opacity is the eased
progress, recorded in the report; at its end, that the join at progress 1
gives exactly the pixels of the incoming shot's frame at that instant
without a join, with each moving view in its incoming slot's box within one
pixel; and that posing the midpoint, another instant and the midpoint again
gives identical pixels. A failed proof MUST stop preview, naming the shot,
the view and the time.

#### Scenario: A host left where it was
- **WHEN** the stage drew a moving view in its incoming slot's box at the
  join's first frame
- **THEN** preview stops, naming the shot, the view and the time, because
  the box is not the outgoing slot's.

#### Scenario: The tour's reframe in the report
- **WHEN** the fixture tour is previewed
- **THEN** its report lists a transition check of kind `reframe` for
  `question`, with the views' boxes at the first frame and at the end, the
  faded elements' opacities at the midpoint, the end's pixel equality and
  the replay.

### Requirement: Invalid reframes are refused before speech

`check`, `preview` and `render`, and the movie document's checks in both
runtimes, MUST refuse before any take a reframe whose two shots place no
view element in both, naming the chapter, the incoming shot, the outgoing
shot, `transition` and `no view element in both`. `check` MUST refuse,
before any take, a reframe whose outgoing or incoming slot is sized by what
it holds, naming the shot, the view element, the set and the slot. A reframe
on the film's first shot, a direction or a colour on a reframe, and a
reframe shorter than two frames or longer than its shot MUST be refused as
for every join.

#### Scenario: Two shots that share no view
- **WHEN** a shot placing only a source panel comes in by a reframe from a
  shot placing only a view
- **THEN** the document is refused naming both shots and `no view element
  in both`.

#### Scenario: A view in a slot that grows with its content
- **WHEN** a reframe moves a view into a slot whose box changes with what
  the set's slots hold
- **THEN** `check` refuses it before reading a take, naming the shot, the
  view, the set and the slot, `sized by what it holds`.

