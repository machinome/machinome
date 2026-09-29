## ADDED Requirements

### Requirement: Show a named still or clip in a shot

In a format 0.4 episode, the author SHALL be able to name stills (PNG, JPEG,
WebP or SVG) and clips (MP4 or WebM) held in the project repository in
`production.yaml`, and show one of them in a shot for a shot-local interval,
over the model stage or the whole frame, fitted whole (`contain`, the default)
or filling the area (`cover`). A picture
MUST cover its whole area on the film's background colour; picture-in-picture
and partial regions are not provided. Text overlays SHALL stay above a
picture, and the film's masthead and progress rule SHALL stay above it as they
stay above transitions. The pictures of one shot MUST NOT overlap in time.

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

### Requirement: A still pans and zooms as its keys say

The author SHALL be able to key a still's view by `center` (a point of the
picture, in fractions of its width and height) and `zoom` (1 is the fitted
picture), at shot-local instants, each segment eased with one of the campaign's
five easing names (default `smooth`). Every key MUST be met exactly at its
instant; before the first key and after the last the view SHALL hold. A zoom
between two keys SHALL keep still on screen the picture point that both keys
place alike, so that approaching a detail never drifts away from it first.
No frame MAY show the background beside a picture that overfills its area, nor
cut off a picture that underfills it.

#### Scenario: Push in from the whole folio onto the saw sketch
- **WHEN** a shot keys the *Codex* still from `{center: [0.5, 0.5], zoom: 1}`
  at 1 s to `{center: [0.5, 0.27], zoom: 1.9, ease: in-out}` at 8 s
- **THEN** the whole sheet holds until 1 s, the view then closes steadily onto
  the saw sketch, and from 8 s the sketch holds, exactly framed as keyed.

#### Scenario: A view that leaves the picture
- **WHEN** a key's centre would show the background beside a covering picture
  at some frame
- **THEN** `check` refuses it, naming the shot, the picture and the video time.

### Requirement: Pixels are never enlarged beyond the author's allowance

A raster still or clip MUST NOT be drawn larger than one output pixel per
source pixel at the output size unless its production entry allows more with
`upscale`. `check` MUST refuse a picture whose peak enlargement over its
interval exceeds its allowance, naming the picture, the shot, the enlargement,
the source and area sizes and the ways to resolve it; `render` at a larger
width MUST refuse the same way before capturing. `upscale` on an SVG MUST be
refused.

#### Scenario: The museum photograph fills the frame
- **WHEN** the 1175×781 photograph is shown with `area: frame` in a 1920×1080
  film without an allowance
- **THEN** `check` refuses it as a 1.38× enlargement; with `upscale: 1.4` on the
  still it passes and the manifest records 1.38 and 1.4; with `area: stage` it
  passes without an allowance.

### Requirement: A clip plays from its in-point, frame for frame

The author SHALL be able to show a named clip for an interval starting at a
chosen clip second (`inPoint`). Each film frame MUST show the clip frame that
is on screen at the corresponding clip instant, never a blended, interpolated
or retimed frame, whatever the clip's frame rate. Clip sound MUST NOT be
played. `check` MUST refuse, naming the shot, a clip that ends before its
interval does (including any continuation a transition shows past the shot's
end), a negative or non-finite in-point, and a clip whose frames have no
well-defined instants (missing or non-increasing timestamps), which is
interlaced, or which carries non-square pixels or a rotation.

#### Scenario: Try the simulation
- **WHEN** a shot shows a screen recording of the interactive simulation from
  its 3.5 s mark for six seconds
- **THEN** each film frame shows the recording's frame at 3.5 s plus the time
  elapsed in the interval, and the film's sound is the narration alone.

#### Scenario: A clip too short
- **WHEN** a clip lasting 7.97 s is shown for six seconds from an in-point of 3.5 s
- **THEN** `check` refuses it before any frame is rendered, naming the clip,
  its end and the time the cue needs.

### Requirement: The model beneath a picture keeps its timeline

While a picture is shown, the model SHALL keep being posed at the model time,
camera and visibility its shot's timeline gives for each frame. Annotations and
highlights of the same shot MUST NOT overlap a picture's interval; `check`
refuses the overlap naming both cues. A picture MAY fade in and out over the
model with `fadeIn` and `fadeOut`, each a duration of at least two frames and an
optional easing name (default `smooth`).

#### Scenario: Dissolve from the model into a drawing
- **WHEN** a picture has `fadeIn: {duration: 0.8}`
- **THEN** over its first 0.8 s the drawing and its background dissolve in over
  the still-moving model, the first frame showing the model alone.

#### Scenario: An arrow under a photograph
- **WHEN** a shot's annotation interval overlaps its picture's interval
- **THEN** `check` refuses it rather than drawing an arrow at a covered part.

### Requirement: Only truthful pictures from the project are shown

Stills and clips MUST resolve to files inside the project's Git repository
with a supported extension, as source excerpts must; a picture MUST NOT be
fetched from any address. `check` MUST refuse, naming the picture: a file
outside the repository; an unsupported extension; a raster still that is not
exactly one PNG, JPEG or WebP picture (an animated picture changes with
wall-clock time); an SVG without a `viewBox`, or containing scripts, animation
or references outside the file; an unknown still, clip or field name.

#### Scenario: A still outside the project
- **WHEN** a still's `file` resolves to a path outside the project repository
- **THEN** `check` refuses it before any frame is rendered.

#### Scenario: A carpentry drawing without a viewBox
- **WHEN** an SVG still declares only `width="420"` and `height="240"`
- **THEN** `check` refuses it and suggests `viewBox="0 0 420 240"`.

### Requirement: Pictures carry their provenance to the release

Each named picture SHALL declare `credit` and `rights`, either as text or as
`null` while unresolved. The build manifest MUST record, for every picture
shown, its repository path, SHA-256, size, credit, rights, allowance, peak
enlargement and whether it is committed unchanged at the project's HEAD, and
for every clip its extraction, decoder version and cadence (frames dropped or
repeated). The release description SHALL receive picture credits through
`{{pictureCredits}}`. A rehearsal MAY show a picture with unresolved credit or
rights or an uncommitted file, but `releaseReady` MUST then be false with the
reasons recorded. Changing a picture's file, the clip decoder or a cue MUST
start a new frame cache.

#### Scenario: The unverified museum photograph in a rehearsal
- **WHEN** the museum still with `credit: null` and `rights: null`, from the
  ignored research copy, is rendered
- **THEN** the film renders, `description.md` marks its credit as pending, and
  the manifest records `releaseReady: false` with the three reasons.

### Requirement: Picture frames are reproducible

A frame with a still or a clip MUST depend only on its video time, the episode
and the hashed picture files. Seeking away and back, or resuming an
interrupted render, SHALL yield identical pixels.

#### Scenario: Revisit a pan-and-zoom and a clip frame
- **WHEN** preview poses an instant inside a pan-and-zoom and one inside a clip,
  poses another instant, and returns to each
- **THEN** the pixels match the first captures exactly.

### Requirement: Preview proves pictures before a render

`preview` SHALL save stills of each picture at its start, at each view key, at
each fade's midpoint and at its last frame, and of each clip at its first and
last frames, and MUST refuse, naming the shot and time, a drawn picture whose
area, position or size differs from what the episode specifies, a clip whose
displayed frame is not the one the clip's timestamps select, or an enlargement
beyond the allowance.

#### Scenario: A synthetic ramp moves as its keys say
- **WHEN** a test still whose colours encode each pixel's coordinates is keyed
  to pan and zoom
- **THEN** at each key the pixel at the area's centre shows the keyed centre
  and a pixel at a known offset shows the point the keyed zoom predicts.

### Requirement: Format 0.4 only; older episodes unchanged

`pictures` SHALL be accepted only in format 0.4 and MUST be refused in a 0.2 or
0.3 episode, naming the shot and format 0.4. Picture cues, view keys, fades and
the `stills` and `clips` entries MUST refuse unknown fields. Episodes in
formats 0.2 and 0.3 SHALL produce exactly the frames they produced before this
change, and SHALL ignore `stills` and `clips` in their production file.
Pictures MUST NOT raise the Viewer API an episode needs.

#### Scenario: Pictures in a 0.3 episode
- **WHEN** a 0.3 episode's shot carries `pictures`
- **THEN** `check` refuses it and asks for format 0.4, rather than rendering the
  model where the picture belongs.
