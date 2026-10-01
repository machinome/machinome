# react-stage Specification

## Purpose
The template owns the screen: every film is drawn by sets and elements
registered in React, the project's own or the tool's, bundled per movie and
typed from the document, with nothing on the page the document did not ask
for. Created by the `react-stage` change (30 September 2026).
## Requirements
### Requirement: The template owns the screen

Every frame of every film SHALL be drawn by a set: a React component a stage
module registers with `defineSet` under its kind, declaring its named slots,
each drawn where the component renders a `Slot`. The set SHALL draw
everything the frame shows besides the elements placed in its slots: the
background, the layout, and any masthead, series label or other chrome the
template decides. The page the stage is drawn in MUST carry no colour, word
or layout of its own: no bar, no brand and no series label that the
document, through its sets and their props, did not ask for. A slot the shot
leaves empty SHALL be drawn as the set draws an empty box.

#### Scenario: Leonardo's film drawn by its own template
- **WHEN** the shot `coupling` of Leonardo's *Cut and Advance*
  (`videos/cut_and_advance`) is drawn in the project's set `LeonardoSplit`,
  with the source panel in `left`, the view `mill` in `right` and a title in
  `headline`
- **THEN** its frames show the layout, colours and masthead that
  `stage.tsx` draws for `LeonardoSplit`, with each element inside its slot's
  box, and nothing the template did not draw.

#### Scenario: A shot on the shipped frame
- **WHEN** a shot on the shipped set `frame` places a view in `stage`
- **THEN** the view fills the whole picture, and no masthead, series label,
  bar or brand appears on any of its frames.

### Requirement: A derived set inherits chrome, not layout

A set registered for a kind whose entry names a `base` SHALL draw its own
layout, with the slots its own entry lists in full, and SHALL show the chrome
of its base by composing it, the chrome reading the derived set's merged
props. A derived set MUST NOT inherit its base's slots or their boxes.

#### Scenario: The split keeps Leonardo's masthead
- **WHEN** `LeonardoSplit`, derived from `Leonardo`, is drawn with the slots
  `left`, `right` and `headline`
- **THEN** it shows the masthead `Leonardo` draws, with the series label its
  own entry's props give, and none of `Leonardo`'s slots `stage`, `plate` or
  `aside`.

### Requirement: Chrome is marked, kept above transitions and masked by the proofs

A set SHALL mark what it draws above pictures and transitions by wrapping it
in `Chrome`. The stage SHALL draw chrome above every transition, blend and
picture, SHALL leave it out of the picture-only captures from which
transitions and blended marks are composed, and SHALL report the rectangles
it covers, which every pixel proof of `preview` MUST leave out of its
comparison and nothing else. What a set draws outside `Chrome` SHALL be part
of the picture: it dissolves, wipes, slides and fades with it.

#### Scenario: The masthead holds through a dissolve
- **WHEN** a shot of *Cut and Advance* comes in from the one before it with a
  dissolve
- **THEN** the masthead `Leonardo` marks as chrome stays still and sharp on
  every frame of the join, while the two pictures beneath it blend, and the
  dissolve's proof compares every pixel outside the masthead's reported
  rectangles.

#### Scenario: A label drawn outside Chrome
- **WHEN** a project set draws a series label without wrapping it in `Chrome`
- **THEN** the label is part of the picture, fades with it through a fade to
  a colour, and is compared by the pixel proofs like the rest of the picture.

### Requirement: Elements draw their state and report what they measured

An element SHALL be a React component a stage module registers with
`defineElement` under its kind. It SHALL draw only the state the frame gives
it for the instant, and SHALL be pure in video time: no wall clock, no state
carried from one frame to the next, and no measurement that changes what is
drawn. Each placed element SHALL report its box and what it measured; the
renderer SHALL check each report against the frame requested and MUST refuse
a frame whose report differs, naming the shot, the element and the video
time. A project element SHALL receive its declared props and its active
actions, each with its parameters, its start and end in the shot and its
progress through them.

#### Scenario: The jobs lit on cue
- **WHEN** a cue of *Cut and Advance* fires `light` with `job: "advance"` on
  the chapter's `Jobs` element until a later spoken phrase
- **THEN** the `Jobs` component receives its `jobs` prop and the `light`
  action with its parameter and progress from the cue's instant to its end,
  draws the second job lit over that interval only, and posing an instant
  inside it, one outside, and the first again gives identical pixels.

#### Scenario: A source that does not fit its slot
- **WHEN** the source panel reports that its excerpt overflows the box of the
  slot it is placed in
- **THEN** `preview` or `render` refuses, naming the shot, the element and the
  video time, rather than shrinking or clipping the source silently.

### Requirement: The tool ships two sets for movies, three for episodes, and four elements

The tool SHALL ship the sets `frame` (one slot, `stage`: the whole picture)
and `split` (`left` and `right`: two halves inside the safe inset), which draw
no chrome and which a movie document lists with exactly their shipped slots.
It SHALL ship, for YAML episodes only, the sets `paper`, `paper-split` and
`source-only`, which draw the earlier film page's layouts, overlay positions
and masthead, and no progress rule; a movie document naming one of them
MUST be refused by name, as a set the tool ships for episodes. It SHALL ship
the elements `view` (the model through a camera, with its highlight and
marks), `source` (a pinned excerpt, typed and lit), `title` (words shown on
cue) and `picture` (a still or clip shown on cue); a project MUST NOT
register a set or element under a shipped kind.

#### Scenario: A document asks for the paper page
- **WHEN** a movie document's stage block lists `paper` without a module
- **THEN** `check` refuses it, naming `stage.sets.paper` and the sets the tool
  ships for movies, `frame` and `split`.

#### Scenario: The shipped split with a wrong slot
- **WHEN** a document lists `split` with the slots `left` and `middle`
- **THEN** it is refused naming `stage.sets.split` and its shipped slots.

### Requirement: View elements lease viewer instances

Each view element placed in a frame SHALL be drawn by a viewer instance of
its own in that frame, positioned over the box of the slot it is placed in;
two views placed in one frame SHALL be two instances, each with its own
camera, visibility, highlight and marks. Instances SHALL be leased: a view
element placed in consecutive frames SHALL keep its instance, whatever slot
holds it; an instance whose view element a frame does not place SHALL be
free, and MAY be leased to another view element of that frame or of a later
one; a view element placed without an instance SHALL take a free instance,
and a new instance SHALL mount only when none is free. With a viewer that
declares API 28 or later, a film SHALL therefore mount no more viewer
instances than the largest number of view elements one of its frames places.
A viewer below API 28 cannot be given another up or field of view, so its
instance SHALL be leased only to a view element with the up and field of
view it mounted with. Each frame SHALL state each instance's whole state,
applied against what the instance holds (the layers it hides and the
highlight left standing, whichever view element it served before), so a
leased instance draws exactly what a fresh one would and no instance depends
on the frames posed before.

#### Scenario: The mill moves from the whole frame into the split
- **WHEN** the chapter `drive` of *Cut and Advance* shows `mill` in
  `Leonardo`'s `stage` in `wheel` and then in `LeonardoSplit`'s `right` in
  `coupling`
- **THEN** the same viewer is posed in both shots, in the new box after the
  cut, with the camera the chapter's last move left it at.

#### Scenario: A film whose frames show one view each
- **WHEN** *Cut and Advance*, whose six view elements are placed one per
  frame, is previewed or rendered
- **THEN** one viewer instance mounts, and each chapter's view is drawn on it
  with that chapter's camera, hidden layers, highlight and marks.

#### Scenario: A highlight left standing by the previous view
- **WHEN** a frame highlights a part of one view element, and the next frame
  places another view element, with no highlight, on the instance it freed
- **THEN** the highlight is restored before the new state is applied, the
  layers the first view hid and the second does not are shown again, and the
  frame's pixels are those the second view gives on a fresh instance.

#### Scenario: Two views side by side
- **WHEN** a shot on `split` places two views of one chapter, one in `left`
  and one in `right`, and highlights a part on the left one only
- **THEN** each half shows the model through its own camera, only the left
  half shows the highlight, and frames placing either view alone, before or
  after, mount no third instance.

### Requirement: The stage refuses what it cannot draw, by name, at mount

Before drawing the first frame, the stage MUST refuse, naming the kind and
what is at fault: a set kind of the document that no stage module registers;
a set whose registered slots differ from the slots the document lists for its
kind; an element kind a chapter uses that no stage module registers; a kind
registered twice; and a viewer whose API is below the one the movie needs.
`preview` and `render` MUST stop on the refusal before capturing any frame.

#### Scenario: A set the module forgot to register
- **WHEN** the document's shots use `leonardo-split` and `stage.tsx`
  registers only `leonardo`
- **THEN** `preview` stops before any capture, naming `leonardo-split`.

#### Scenario: Slots out of step with the declaration
- **WHEN** `stage.tsx` registers `leonardo-split` with the slots `left` and
  `right` and the document lists `left`, `right` and `headline`
- **THEN** the stage refuses naming `leonardo-split` and both slot lists.

#### Scenario: An element kind registered twice
- **WHEN** two stage modules both register the element kind `jobs`
- **THEN** the stage refuses naming `jobs`.

### Requirement: One stage bundle per movie, typed from the document and rebuilt by content

The tool SHALL bundle, for each movie, its own stage runtime with the stage
modules the document names into one script and one stylesheet under
`<root>/_build/stage/`, and SHALL generate from the document's stage block
the types of each project set's props and slots and each project element's
props and actions' parameters. When a module is TypeScript, the modules
SHALL be checked against those types, and a mismatch MUST be refused by
`check`, naming the module and what the check found, whether or not the
chapters' takes are cached, so it is found before `speech` is run. The
bundle SHALL be rebuilt only when the content of one of its inputs changes
(the runtime, a module or a file it reads, the stage block, the versions of
the bundler, the type checker and React), never because of a modification
time. A YAML episode SHALL be drawn by a bundle of the runtime alone. `check`
SHALL report the bundle it built or reused, with the SHA-256 of its script
and the SHA-256 of its stylesheet, so a change to either shows in the line.

#### Scenario: A prop of the wrong type
- **WHEN** `stage.tsx` reads the `Jobs` prop `jobs` as a string while the
  document declares it a `list`
- **THEN** `check` refuses, naming `stage.tsx` and the prop, and nothing is
  requested from the speech provider.

#### Scenario: A touched module
- **WHEN** only the modification time of `stage.tsx` changes between two runs
  of `check`
- **THEN** the second run reuses the bundle and reports it as reused.

#### Scenario: A changed stylesheet
- **WHEN** a stylesheet `stage.tsx` imports changes, and nothing else
- **THEN** the next `check` rebuilds the bundle and its `Stage:` line
  reports the stylesheet's new hash beside the script's unchanged one.

### Requirement: The stage bundle is part of what a frame was made from

The hashes of the stage bundle a render draws with SHALL be common inputs of
every cached shot, so a changed template or runtime recaptures every shot
and an unchanged one reuses verified frames, and the render manifest SHALL
record the bundle's SHA-256.

#### Scenario: The template is restyled
- **WHEN** the author changes the colour `Leonardo` draws its masthead in and
  renders again
- **THEN** no shot is reused from the earlier render, and the manifest
  records the new bundle's hash.

### Requirement: A pose waits for what can change the picture

Posing a frame SHALL end with a repaint of the whole page when the frame is
a proof pose of `preview`, when a view's viewer was mounted, placed again
after shots without it, or its box resized on that pose, or when anything
the page draws outside the pixels of the views' canvases (an element, an
attribute, a word) differs from what the page drew at its last repaint. Any
other pose, in which at most the pixels of the views' canvases change, SHALL
NOT wait for a repaint. Whatever a pose waits for, its pixels MUST NOT
depend on the frames posed before it: posing one instant, another, then the first again
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

### Requirement: A reframe moves a view's host and fades the rest

When a frame carries a reframe, the stage SHALL draw the incoming set with
its slots and chrome as for any frame, and SHALL position the viewer host of
each view element the reframe moves over the box the frame gives it, in
fractions of the frame, instead of over its slot's box, keeping the host
inside its slot's element so the set's stacking order holds; the slot's own
box SHALL stay what the set draws. The stage SHALL report that box as the
element's `box`, draw the view's marks over it, and wait for the canvas to
fill it before measuring, whenever its size changed. Every other element the
frame places SHALL be drawn at the frame's progress as opacity, and during a
reframe every element SHALL report its opacity. At progress 1 the stage
SHALL draw exactly what it draws for the same frame without a join. The
positioning and the fade SHALL be functions of the frame alone.

#### Scenario: The host follows the frame's box
- **WHEN** a frame of a reframe gives `opening.wide` the box
  `[0.27, 0.17, 0.56, 0.74]` of a 1280×720 page
- **THEN** its host is drawn at 345.6, 122.4, 716.8 by 532.8 pixels, to
  the layout's unit of 1/64 pixel, which the stage reports as the element's
  box, while the `right` slot keeps its own box.

#### Scenario: A view drawn under the set's headline
- **WHEN** the incoming set draws its headline above its right slot and a
  reframe moves the view held there
- **THEN** the headline stays above the moving view on every frame of the
  join.

#### Scenario: Without a reframe
- **WHEN** the next frame carries no reframe
- **THEN** the host fills its element's box again and no element carries an
  opacity of the join.

### Requirement: A view on a take is posed by restoring its bank

For a view element whose frame state carries `bank`, the stage SHALL mount
its viewer instance without a loop time, and on every frame SHALL restore
the bank on the viewer's machine handle, `machine().restore({identity,
bank})` with the take's identity and the whole bank, then set the camera;
it MUST NOT set a loop time for that view. The view's report SHALL carry
the bank the machine holds after the pose. At mount, the stage MUST refuse,
naming the view and the shot: a viewer that gives no machine handle for the
clocked document, and a machine whose identity differs from the take's,
naming both identities and `take.identity`. A movie on a take SHALL need
Viewer API 29, for the reason `clocked take`, and the stage's refusal of an
older viewer SHALL name it.

#### Scenario: A pose by bank
- **WHEN** the stage draws a frame of the counter whose view carries a bank
  with crank 1800 and units 5
- **THEN** the viewer's machine is restored to that bank with the
  counter's identity, the camera is set after it, no loop time is set, and
  the view reports that bank.

#### Scenario: A viewer without a machine
- **WHEN** the viewer mounted for a view on a take gives no machine handle
- **THEN** the stage refuses at mount naming the view, the shot and the
  machine it lacks.

#### Scenario: Another machine
- **WHEN** the machine's identity differs from the take's
- **THEN** the stage refuses at mount naming the view, both identities and
  `take.identity`.

#### Scenario: The requirement named
- **WHEN** the movie films a take and also highlights a part
- **THEN** it needs Viewer API 29, and the refusal of a viewer declaring 28
  names `clocked take` among its reasons.

### Requirement: A view's canvas is its box's size, neither smaller nor larger

The stage SHALL wait, a bounded number of animation frames, for every
view's canvas to fill its box and exceed it by no more than one pixel in
either dimension, whenever the view was mounted, placed again or its box
changed size, so a canvas left larger by a shrinking box is waited for as a
canvas left smaller by a growing one is. The renderer MUST refuse a posed
frame whose view's canvas is more than one pixel larger than its box in
either dimension, `Viewer canvas exceeds its view`, naming the view, the
shot, the time and both sizes, as it refuses a canvas that does not fill
it.

#### Scenario: A canvas that follows a shrink late
- **WHEN** a reframe shrinks a view's box and the viewer resizes its canvas
  some animation frames later
- **THEN** the stage poses the view only once its canvas is the box's size
  within a pixel.

#### Scenario: A canvas that never follows
- **WHEN** a view's box shrinks and its canvas stays at the old size
- **THEN** the renderer stops naming the view and `Viewer canvas exceeds
  its view`.

