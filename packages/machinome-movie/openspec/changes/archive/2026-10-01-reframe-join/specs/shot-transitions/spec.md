## ADDED Requirements

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
