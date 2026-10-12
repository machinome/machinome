## ADDED Requirements

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

### Requirement: A view keeps one viewer across its chapter

Each view element SHALL be drawn by its own viewer instance, positioned over
the box of the slot it is placed in. A view placed in several shots of one
chapter SHALL keep the same instance from one shot to the next, whatever slot
holds it, and two views placed in one shot SHALL be two instances, each with
its own camera, visibility, highlight and marks. Each frame SHALL state each
instance's whole state, so no instance depends on the frames posed before.

#### Scenario: The mill moves from the whole frame into the split
- **WHEN** the chapter `drive` of *Cut and Advance* shows `mill` in
  `Leonardo`'s `stage` in `wheel` and then in `LeonardoSplit`'s `right` in
  `coupling`
- **THEN** the same viewer is posed in both shots, in the new box after the
  cut, with the camera the chapter's last move left it at.

#### Scenario: Two views side by side
- **WHEN** a shot on `split` places two views of one chapter, one in `left`
  and one in `right`, and highlights a part on the left one only
- **THEN** each half shows the model through its own camera, and only the
  left half shows the highlight.

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
SHALL report the bundle it built or reused.

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
- **WHEN** a stylesheet `stage.tsx` imports changes
- **THEN** the next `check` rebuilds the bundle and reports its new hash.

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
