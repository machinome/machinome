## MODIFIED Requirements

### Requirement: Show a named still or clip in a shot

In a format 0.4 episode, the author SHALL be able to name stills (PNG, JPEG,
WebP or SVG) and clips (MP4 or WebM) held in the project repository in
`production.yaml`, and show one of them in a shot for a shot-local interval,
over the model stage or the whole frame, fitted whole (`contain`, the default)
or filling the area (`cover`). In a movie document the same pictures SHALL be
`picture` elements, shown on cue in the slot a shot places them in. A picture
SHALL fill the box of its slot: an episode's `area: stage` is the paper sets'
slot `plate`, over the model stage, and its `area: frame` their slot `full`,
the whole frame. A picture MUST cover its whole box on the film's background
colour; picture-in-picture and partial regions of a box are not provided.
Text overlays SHALL stay above a picture, and the film's masthead SHALL stay
above it as it stays above transitions. The pictures of one shot MUST NOT
overlap in time.

#### Scenario: The museum photograph, full screen and still
- **WHEN** the restaged *Revolutions v2* `museum-reference` shot shows the
  museum still with `area: frame` for its whole length
- **THEN** every frame shows the whole photograph, uncropped, centred on the
  film's background, with no movement, and the model is not visible.

#### Scenario: Start on the photograph, then cut to the model
- **WHEN** the restaged `question-and-feedback` shot shows the photograph from
  0 to 6.2 s
- **THEN** the frame at 6.2 s shows the reconstruction at the model time and
  camera the shot's timeline gives for 6.2 s, as if the picture had never been
  there.

#### Scenario: A drawing in a template's slot
- **WHEN** a shot of *Cut and Advance* places the picture `iso` in
  `Leonardo`'s slot `plate` and shows it on cue
- **THEN** the still is fitted whole inside the box `Leonardo` draws for
  `plate`, on the background, and the masthead stays above it.

### Requirement: Preview proves pictures before a render

`preview` SHALL save stills of each picture at its start, at each view key, at
each fade's midpoint and at its last frame, and of each clip at its first and
last frames, and MUST refuse, naming the shot and time, a drawn picture whose
rectangle differs from the one its fit and view give for the box the stage
reports for its slot, a clip whose displayed frame is not the one the clip's
timestamps select, or an enlargement beyond the allowance. Fade proof MUST
compare the picture as authored, fully drawn and absent at the same model and
video instant, leaving out only the reported chrome; model motion between
frames MUST NOT stand in for evidence that the fade reached the pixels.

#### Scenario: A synthetic ramp moves as its keys say
- **WHEN** a test still whose colours encode each pixel's coordinates is keyed
  to pan and zoom
- **THEN** at each key the pixel at the box's centre shows the keyed centre
  and a pixel at a known offset shows the point the keyed zoom predicts.

#### Scenario: A picture drawn outside its slot
- **WHEN** a set's styles push a picture's drawn rectangle past the box its
  slot reports
- **THEN** preview refuses, naming the shot, the picture and the time.

### Requirement: Format 0.4 only; older episodes unchanged

`pictures` SHALL be accepted only in format 0.4 and MUST be refused in a 0.2 or
0.3 episode, naming the shot and format 0.4. Picture cues, view keys, fades and
the `stills` and `clips` entries MUST refuse unknown fields. Episodes in
formats 0.2 and 0.3 SHALL show no picture, drawn on the same sets as an
episode without pictures, and SHALL ignore `stills` and `clips` in their
production file. Pictures MUST NOT raise the Viewer API an episode needs.

#### Scenario: Pictures in a 0.3 episode
- **WHEN** a 0.3 episode's shot carries `pictures`
- **THEN** `check` refuses it and asks for format 0.4, rather than rendering the
  model where the picture belongs.

#### Scenario: Stills declared but unused
- **WHEN** a 0.3 episode's production file declares `stills`
- **THEN** its frames equal the frames of the same episode without them.
