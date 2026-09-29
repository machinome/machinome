## ADDED Requirements

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
plain colour when it fades out. The fade colour SHALL default to the film's
`style.background` and MAY be set to any quoted `#rrggbb`.

#### Scenario: A paper film fades up from the page
- **WHEN** a cream-paper film's first shot declares `fadeIn: {duration: 1.5}`
- **THEN** its first frame shows the paper colour with the masthead and
  progress rule, and the moving machine appears over one and a half seconds.

#### Scenario: Fade out to black on request
- **WHEN** the last shot declares `fadeOut: {duration: 2, color: "#000000"}`
- **THEN** the picture darkens over the last two seconds and the film's last
  frame is black outside the masthead and progress rule.

### Requirement: Transitions leave the screenplay's timing alone

A transition MUST NOT change any shot's `start` or `end`. It SHALL occupy the
first seconds of the shot that declares it, whose model time, camera, overlays,
annotations, highlights, code typing and narration keep the times the author
wrote. Narration audio and captions MUST be unaffected. The film's masthead and
progress rule SHALL stay in place through every transition.

#### Scenario: Narration starts on time through a dissolve
- **WHEN** a shot whose narration starts 0.2 s after its `start` comes in with
  a one-second dissolve
- **THEN** the narration and its captions start at the same instant as with a
  hard cut, while the picture is still dissolving.

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
A failed proof MUST stop preview and keep the images it compared.

#### Scenario: A dissolve that does not blend
- **WHEN** the composed midpoint of a dissolve differs from the predicted blend
  by more than 2 levels anywhere
- **THEN** preview stops, naming the shot and the time, and keeps the outgoing,
  incoming and composed images for inspection.

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
render exactly as before, with hard cuts at every boundary. Transitions SHALL
require format `machinome-video-draft/0.4`; a 0.2 or 0.3 episode that carries
one MUST be refused and asked to change its format, never rendered with hard
cuts in its place. Transitions MUST NOT raise the Viewer API an episode needs.

#### Scenario: A 0.3 episode with a transition
- **WHEN** the feed-mechanism demo, still in format 0.3, gains a `transition`
- **THEN** `check` refuses it and asks for format 0.4.

#### Scenario: Existing films
- **WHEN** the sawmill rehearsal, the *Revolutions* episodes and the 0.3 demos
  are checked and previewed unchanged
- **THEN** they pass and produce the same frames as before this change.
