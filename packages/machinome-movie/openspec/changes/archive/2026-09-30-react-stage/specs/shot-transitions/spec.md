## MODIFIED Requirements

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
