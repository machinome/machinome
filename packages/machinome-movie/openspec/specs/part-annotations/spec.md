# part-annotations Specification

## Purpose
Arrows and labels, written beside the narration, that point at a part or a world
point and follow it on screen, drawn only where the target truly is.
## Requirements
### Requirement: An arrow or label follows its target

The author SHALL add timed `arrow` and `label` annotations to a shot, each aimed
at one part (a production layer name or one assembly path) or one world point,
with shot-local `from`/`to` seconds. While an annotation is active, every frame
SHALL draw it at the target's on-screen position for that frame's model pose and
camera: an arrow runs from text fixed at an authored place in the safe area to a
tip on the target; a label's text sits at an authored offset from the target.
Annotations MUST be drawn over the model and MUST NOT change the model, the
camera or the visibility of any part.

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
- **WHEN** video time reaches the annotation's `to`, or the shot cuts
- **THEN** the annotation is gone from that frame.

### Requirement: Annotated frames are reproducible

An annotated frame MUST depend only on its video time and the episode. Seeking
away and back, or resuming an interrupted render, SHALL yield identical pixels.

#### Scenario: Revisit an annotated instant
- **WHEN** preview poses an annotated instant, poses another instant, and
  returns
- **THEN** the arrow, its text and the model pixels match the first capture.

### Requirement: Invalid annotations are refused before rendering

`check`, `preview` and `render` MUST refuse, naming the shot, an annotation with
an unknown kind; with both or neither of a part and a point; naming a layer that
production does not define or an assembly path the exported model does not
contain; with times outside the shot or not increasing; an arrow without a place
in the safe area or with a place outside it; a label without text; a target the
same shot hides; and an episode using annotations without a declared safe inset.

#### Scenario: Misspelled part
- **WHEN** an annotation names `[Feed mechanism, Drving pawl]`
- **THEN** `check` fails and names the missing path before any frame is rendered.

#### Scenario: Arrow at a hidden part
- **WHEN** a shot hides the `feed` layer and points an arrow at the driving pawl
- **THEN** `check` refuses the contradiction instead of drawing an arrow at nothing.

### Requirement: An annotation never points at nothing

`preview` and `render` MUST refuse a frame on which an active annotation's target
is not on screen, or whose text leaves the frame, naming the shot, the
annotation, its text and the video time. They MUST NOT drop the annotation silently.

#### Scenario: Part leaves the frame
- **WHEN** a moving part leaves the camera's view while its arrow is active
- **THEN** preview or render stops with the shot, annotation and time, and the
  author shortens the cue or reframes.

### Requirement: Older episodes and older viewers are handled explicitly

Episodes in format `machinome-video-draft/0.2` SHALL parse and render exactly as
before, with any Viewer API 21 or later. Annotations SHALL require format
`machinome-video-draft/0.3` and Viewer API 28. `check`, `preview` and `render`
MUST refuse an episode using annotations against a viewer declaring an older API,
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

