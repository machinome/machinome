# movie-document Specification

## Purpose

Let a project's declarations drive a film through a data document,
`machinome-movie/0.2`: sets with slots, elements and cues of actions,
narration in chapters of one take each, times anchored to spoken phrases and
marks and resolved from the cached takes to one resolved document that YAML
episodes load into too, one schema and one set of fixtures shared with the
Python side. Created by the `movie-document` change and rewritten for 0.2 by
the `react-stage` change (30 September 2026).
## Requirements
### Requirement: A movie document is a source the tool produces from

`check`, `speech`, `preview`, `render` and `build` SHALL accept a
`machinome-movie/0.2` JSON document wherever they accept a YAML episode, and
SHALL produce from it with the same checks of the export, the pinned
revision, the source excerpts, the pictures and the evidence files, the same
proofs and the same outputs. The document SHALL be data: its relative paths
resolve against its `root`, and the tool's outputs go to `<root>/_build/`. A
document in any other format, `machinome-movie/0.1` included, MUST be refused
naming its format and the format this build reads, before anything else is
read.

#### Scenario: The validation film from its document
- **WHEN** the author runs `check` on
  `videos/cut_and_advance/_build/movie.json` after `speech`
- **THEN** the document is checked against the export, the pinned revision,
  the source excerpts and the pictures, its stage is bundled, and `preview`
  and `render` produce the film from it.

#### Scenario: A document of the previous format
- **WHEN** a document says `"format": "machinome-movie/0.1"`
- **THEN** it is refused naming `machinome-movie/0.1` and
  `machinome-movie/0.2`, and nothing else is checked.

#### Scenario: A document of a later format
- **WHEN** a document says `"format": "machinome-movie/9.9"`
- **THEN** it is refused naming `machinome-movie/9.9` and the format this
  build reads, and nothing else is checked.

### Requirement: The document is checked against its schema first

The tool SHALL validate an unresolved document against
`schema/machinome-movie-0.2.json` before any other rule: field names, types,
required fields, closed field lists and the fields each shipped action
takes. A field the schema does not know, on the document, its stage block, a
chapter, an element, a shot, a cue or an action, MUST be refused naming the
field and where it is, so a misspelling or a field of a later build is never
silently dropped. Both runtimes validate against this one file.

#### Scenario: Narration written on a shot
- **WHEN** a shot of a document carries `narration`
- **THEN** it is refused naming `narration` and the shot's place in the
  document, because narration belongs to the chapter.

#### Scenario: A misspelled field on an action
- **WHEN** a `ring` action of a cue carries `paddin`
- **THEN** it is refused naming the field and the cue's place in the shot,
  rather than drawing the ring with its default padding.

### Requirement: A chapter's narration is one take

A document SHALL group shots into chapters, each with its own narration,
optional speech offset (default 0.2 s), optional direction and its own
elements. `speech` SHALL generate one take per chapter from the narration
alone, before anything in the document is resolved, and place it at the
chapter's start plus its speech offset. The take MUST fit its chapter, ending
at least 0.1 s before the chapter's last shot does; a take that does not is
refused after caching, naming the chapter and its measurement. Captions SHALL
follow the chapter's recorded alignment. A spoken reveal or source emphasis
in a shot SHALL read its chapter's narration and take, at the instant the
take starts relative to that shot.

#### Scenario: A paragraph across a cut
- **WHEN** the `drive` chapter's narration spans the shots `wheel`, `coupling`
  and `stroke`
- **THEN** it is synthesized once, heard without a restart at either cut, and
  its captions follow the one take.

#### Scenario: Emphasis in a later shot of the chapter
- **WHEN** `coupling`, the second shot of `drive`, emphasizes `waterwheel`,
  `drives` and `crankshaft` on the source panel as they are spoken
- **THEN** each token lights at its word's measured onset in the chapter's
  take, counted from the shot's own start.

### Requirement: Cuts, keys and cues can be anchored to spoken words

Wherever a shot takes a time (its `until`, a cue's `at` and `until`, a
`move`'s `until`, a model key's `at`, a picture view key's `at`), the author
SHALL be able to write a number or an anchor: `spoken` (the instant the
narrator begins a phrase: the onset of the first letter or digit of its first
word), `spokenEnd` (the instant its last character ends) or
`{"narrationEnd": true}` (the instant the chapter's narration ends: the end
of the last letter or digit of the chapter's take), each with an optional
`plus` in seconds, positive or negative. A number is shot-local seconds (for
`until`, the shot's duration). An anchor SHALL resolve to the chapter's start
plus its speech offset plus the phrase's time, or the narration's end, in the
cached take plus `plus`, snapped to the nearest frame of the output rate;
shots then run in order from zero, each starting where the one before ended,
and the film lasts until the last shot's end.

The phrase MUST occur exactly once in the chapter's written narration and its
spoken form (after `audio.replacements`) exactly once in the chapter's take;
otherwise the document is refused naming the chapter, the shot, the field by
its path in the shot (`until`, `cues[1].at`, `cues[0].actions[0].until`,
`model.keys[2].at`, `cues[3].actions[0].view[1].at`) and the phrase. A
`narrationEnd` anchor whose value is not `true`, or which carries a field
other than `plus`, MUST be refused naming the chapter, the shot, the field's
path and `narrationEnd`; one whose chapter's take holds no letter or digit
MUST be refused naming the chapter, the shot, the field and `narrationEnd`. A
shot whose `until` resolves at or before its start, a cue or key anchored
before its shot's start or after its end, a spanning action whose `until` is
at or before its `at`, and a `move` whose `until` is at or before its `at`
MUST be refused naming the shot and the anchor.

#### Scenario: A cut on a spoken phrase
- **WHEN** `coupling` has `until: {"spoken": "A crank"}`
- **THEN** the cut to `stroke` falls on the output frame nearest the instant
  the narrator begins "A crank" in the cached take, and moves with it when the
  take is regenerated.

#### Scenario: A highlight from one word to another
- **WHEN** a cue of `coupling` is `at: {"spoken": "waterwheel"}` and
  `until: {"spoken": "crankshaft"}` and highlights the waterwheel on `mill`
- **THEN** the highlight begins on the frame nearest the onset of
  "waterwheel" and is gone from the frame nearest the onset of "crankshaft".

#### Scenario: A cut after the narration ends
- **WHEN** the last shot of `drive` has `until: {"narrationEnd": true,
  "plus": 0.9}` and the chapter's narration ends "…turns the crankshaft."
- **THEN** the chapter ends on the output frame nearest 0.9 s after the end
  of the final "t" of "crankshaft" in the cached take, the same frame
  `{"spokenEnd": "crankshaft", "plus": 0.9}` would give, and moves with it
  when the take is regenerated.

#### Scenario: A narration end that is not true
- **WHEN** a shot's `until` is `{"narrationEnd": false}`
- **THEN** the document is refused by its schema, naming the chapter, the
  shot and `until.narrationEnd`, before any take is read.

#### Scenario: A phrase the narration does not contain
- **WHEN** an anchor names "the saw" in a chapter whose narration never says
  it
- **THEN** the document is refused, naming the chapter, the shot, the field
  and "the saw", before any take is read.

#### Scenario: An ambiguous phrase
- **WHEN** an anchor names a phrase said twice in its chapter
- **THEN** the document is refused as ambiguous, naming the chapter, the
  shot, the field and the phrase.

#### Scenario: A cut before its own start
- **WHEN** a shot's `until` names a phrase spoken before the shot begins
- **THEN** the document is refused naming the shot and its `until`.

### Requirement: Model seconds can name a mark

A document SHALL be able to name instants of the machine in `marks`, and
wherever it takes model seconds (`model.from`, `model.to`, a model key's
`seconds`) the author SHALL be able to write a number or a mark with an
optional `plus`, resolved to the mark's model seconds plus `plus`. An unknown
mark MUST be refused naming the shot and the mark.

#### Scenario: The pull settles on the return
- **WHEN** `pawls` keys `pull_start` at the cut, `return_start` with `out`
  easing at the spoken "On the return", and `cycle_end` at the shot's end
- **THEN** the model runs from 436 to 438 and eases into the hold on the
  words, and from 438 to 440 to the end.

#### Scenario: A misspelled mark
- **WHEN** a shot names mark `pull_stat`
- **THEN** it is refused naming the shot and `pull_stat`.

### Requirement: What a document names is checked before any take

Before reading any take, the tool SHALL check everything the document names
and MUST refuse, naming the chapter, the shot and the thing at fault: in the
stage block, a stage module that is not a TypeScript or JavaScript file
inside the project repository, a set or element whose module
`stage.modules` does not list, a shipped set
listed with other slots or a base, a project set without a module or under a
kind the tool ships, a base that is neither listed nor shipped, and a
project element under a shipped kind; a set kind a shot uses that the stage
block does not list; a slot the shot's set does not declare; an element the
chapter does not declare, or placed in two slots of one shot; an element of
a kind neither shipped nor listed, a field its kind does not take, or props
that do not match its kind's declared props; a camera, layer, source excerpt,
still or clip the document does not declare; a layer, highlighted part or
marked part the export does not contain; a model key list that does not start
at the shot's start or whose last key is not at the shot's `until`, written
as the same number or the same anchor; an action on an element the shot does
not place, an action its element's kind does not have, and a project
action's parameter missing, unknown or of the wrong kind; an emphasis whose
tokens are absent or ambiguous in the excerpt it lights; and a placed source
panel whose typing does not complete its excerpt when no earlier shot of the
chapter completed it.

A token SHALL be an identifier or a dotted path of identifiers, and SHALL
occur where its text is not preceded or followed by an ASCII letter, digit or
underscore, a dot being a boundary. Each token MUST occur exactly once in the
whole excerpt, on any line, or, when the action names a `line` inside the
excerpt, exactly once on that line; tokens are read from the excerpt's source
file at the pinned revision.

#### Scenario: A misspelled preset
- **WHEN** a `move` names the camera `faraway` and the document declares none
- **THEN** it is refused naming `faraway` and the shot, before `speech` is
  needed.

#### Scenario: A part the export does not have
- **WHEN** a highlight names the assembly path `Beam/Plonk`
- **THEN** it is refused naming `Beam/Plonk` and the shot.

#### Scenario: A token inside a longer identifier
- **WHEN** an emphasis lights `pawl` and the excerpt holds only `pawl_mount`
  and `feed.pawl.turn` once each
- **THEN** it lights `pawl` in `feed.pawl.turn`, because a dot is a
  boundary, and not in `pawl_mount`; an excerpt holding `feed.pawl` twice on
  different lines is refused as ambiguous unless the action names the line.

#### Scenario: A stage module outside the project
- **WHEN** `stage.modules` names `../../elsewhere/stage.tsx`, outside the
  project repository
- **THEN** it is refused naming the module before anything is bundled.

### Requirement: Anchors are resolved only from cached takes

`check`, `preview` and `render` SHALL resolve spoken anchors from the takes
`speech` cached and MUST NOT generate or purchase speech. A document with
spoken anchors in a chapter whose take is not cached MUST be refused, naming
the chapter and asking for `speech` to be run first. Each of them SHALL
write the **resolved document** to `<root>/_build/movie-resolved.json`
before rendering anything: the document itself, in its field order, with
`"resolved": true`, the film's duration, `start` and `end` on every chapter
and shot, and every time and every model second numeric, shot-local where the
document wrote it shot-local.

#### Scenario: Checked before speech
- **WHEN** `check` runs on a new document with spoken anchors
- **THEN** it refuses naming the first chapter without a take and asking for
  the `speech` command, and nothing is requested from the provider.

#### Scenario: Inspecting the resolution
- **WHEN** `check` passes
- **THEN** `_build/movie-resolved.json` holds the chapters with their
  resolved starts, ends and offsets and every shot, cue, action and key with
  numeric times, and resolving the same document against the same takes
  again writes the same file.

### Requirement: Both runtimes share the fixtures

The repository SHALL keep valid `machinome-movie/0.2` documents, their take
doubles and their pinned resolutions, and invalid documents with the words
their refusal must contain, under `fixtures/`, indexed so that a fixture is
registered once. The Node suite MUST load, check and resolve every registered
document against its takes to exactly its pinned resolution, twice
identically, and refuse every invalid document with every listed word, so a
fixture the other runtime adds is tested here too.

#### Scenario: A fixture added by the Python side
- **WHEN** the Python side adds an invalid document to `fixtures/invalid/`
- **THEN** the Node suite refuses it and asserts its listed words, with no
  change to the Node tests.

### Requirement: A shot is drawn in a set, with its chapter's elements in its slots

A shot SHALL name its `set`, a kind the document's stage block lists, and
SHALL place elements its chapter declares in slots that set declares, each
element in at most one slot of the shot; a slot the shot does not name is
empty. A set kind the stage block does not list, a slot the set does not
declare, an element the chapter does not declare, and an element placed in
two slots of one shot MUST be refused, naming the chapter, the shot and the
slot or element. `fadeIn` SHALL be accepted only on the film's first shot and
`fadeOut` only on its last, across chapters.

#### Scenario: The coupling beside its source
- **WHEN** `coupling` is drawn in `leonardo-split` with `{"left": "code",
  "right": "mill"}`
- **THEN** the source panel is drawn in the set's `left` box and the view in
  its `right` box, and the set's `headline` is left empty.

#### Scenario: A slot the set does not declare
- **WHEN** a shot in `leonardo-split` places `mill` in `stage`
- **THEN** it is refused naming the chapter, the shot, `stage` and
  `leonardo-split`.

#### Scenario: One element in two places
- **WHEN** a shot on `split` places `mill` in both `left` and `right`
- **THEN** it is refused naming the shot and `mill`.

#### Scenario: A fade-in on a later chapter
- **WHEN** the first shot of the second chapter declares `fadeIn`
- **THEN** it is refused naming the shot, because only the film's first shot
  fades in.

### Requirement: Elements act on cue

A cue SHALL fire, at its `at`, actions on elements the shot places: a view's
`move`, `highlight`, `ring`, `label` and `arrow`; a source panel's `type` and
`emphasize`; a title's and a picture's `show`; and a project element's
declared actions with their parameters. An action that spans SHALL last until
the cue's `until`, which it MUST have; `type` and `move` finish on their own.
An `emphasize` SHALL be anchored at a spoken phrase without `plus`, and each
of its `words` SHALL pair a word spoken exactly once in that phrase,
word-bounded, with a token of the excerpt; each token SHALL light from its
word's onset until the phrase ends plus `hold`, and MUST already be typed when
its word is spoken. The typing cues of a shot SHALL run in order, each from
where the chapter's previous typing stopped, and MUST complete the excerpt
before the shot ends unless an earlier shot of the chapter completed it. Two
moves, two highlights, or two overlapping `show`s of one element in one shot
MUST NOT overlap in time; an entrance or exit shorter than two frames or
longer than its span MUST be refused; an entrance and an exit that together
exceed a short span overlap, the element drawn at the lesser of the two. Each
refusal MUST name the chapter, the shot, the element and the action or field.

#### Scenario: A span without an end
- **WHEN** a cue fires `highlight` on `mill` and has no `until`
- **THEN** it is refused naming the shot, the cue and `until`.

#### Scenario: A project action with a wrong parameter
- **WHEN** a cue fires `light` on the `Jobs` element with `job: 2` and the
  stage block declares `job` a `string`
- **THEN** it is refused naming `jobs`, `light`, `job` and `string`.

#### Scenario: The driving pawl lights its call
- **WHEN** an emphasis at `{"spoken": "the driving pawl turns"}` pairs the
  spoken "driving pawl" with the token `feed.pawl.turn`
- **THEN** `feed.pawl.turn` lights at the onset of "driving" and clears after
  "turns" ends plus the hold.

#### Scenario: An emphasis anchored with an offset
- **WHEN** an emphasis cue is `at: {"spoken": "waterwheel", "plus": 0.2}`
- **THEN** it is refused naming the shot and the cue's `at`.

### Requirement: An element keeps its state across its chapter's shots

An element SHALL be one element across every shot of its chapter that places
it: a view SHALL start each shot at the camera where its last move in an
earlier shot of the chapter ended, or at its declared camera if it has not
moved, and a source panel SHALL keep the text typed in earlier shots of the
chapter and continue typing from there. Elements of two chapters SHALL never
share state, whatever their keys.

#### Scenario: Typing across a cut
- **WHEN** the chapter `drive` types lines 413 and 414 of its excerpt in
  `coupling` and line 415 in `stroke`
- **THEN** `stroke` opens with lines 413 and 414 already typed and types line
  415 from there.

#### Scenario: The same key in another chapter
- **WHEN** the chapters `drive` and `feed` each declare a view `mill`
- **THEN** the view of `feed` starts at its own declared camera, not where
  `drive`'s view was left.

### Requirement: A frame is a pure function of the resolved document and video time

The tool SHALL resolve each output instant to one frame from the resolved
document and the pinned files the load read, and from nothing else: the set,
the element in each slot, each placed element's complete state for that
instant, and the transition in progress with the outgoing shot's frame. A
frame MUST NOT depend on the frames resolved or posed before it, and MUST NOT
carry any film-wide position: how far through the film an instant lies is
not part of what is drawn. A title or picture that is placed and not shown
SHALL appear in the frame as not shown.

#### Scenario: The same instant twice
- **WHEN** the frame at 12.4 s of *Cut and Advance* is resolved, then the
  frame at 30 s, then 12.4 s again
- **THEN** the two frames at 12.4 s are identical.

#### Scenario: A film made longer
- **WHEN** a chapter is added after the last one
- **THEN** the frames of the earlier chapters are resolved exactly as
  before, because nothing in a frame depends on the film's duration.

### Requirement: A YAML episode loads into the same resolved shape

A YAML episode in formats `machinome-video-draft/0.2`, `0.3` and `0.4` SHALL
keep every validation, refusal and timing rule of its format, and SHALL load
into the same resolved shape as a movie document: one chapter per shot, with
the shot's narration and speech offset, and the shot's view, source panel,
overlays, pictures, marks, highlight and typing as elements and actions
placed in the shipped sets `paper` (a shot without code), `paper-split` (a
shot with code) and `source-only` (a shot with `layout: source-only`), whose
masthead shows the brand and the episode's series. More overlays of one
position or pictures of one area in one shot than those sets have slots for
MUST be refused naming the shot.

#### Scenario: The sawmill rehearsal after the stage
- **WHEN** Leonardo's `one-wheel-two-jobs` episode is checked and previewed
- **THEN** it passes every rule it passed before, its shots are drawn in the
  paper sets with the masthead `MACHINOME` and its series label, its cached
  takes are reused, and no progress rule is drawn.

### Requirement: `check` reports each chapter's take and tail

With every cut on a phrase, a film is as long as its takes and their tails.
After its summary line, `check` SHALL print one line per chapter, in order:
the chapter's id, its cached take's measured length, the chapter's resolved
length and its tail (the chapter's length minus its speech offset minus the
take), in seconds; a chapter whose take is not cached SHALL be reported as
having none, with its length. `check` MUST NOT generate or purchase speech to
report a take.

#### Scenario: Reading where a film's length comes from
- **WHEN** `check` passes on a movie whose chapter `drive` has a 5.68 s take,
  a speech offset of 0.2 s and resolves to 7.20 s
- **THEN** it prints `drive: take 5.68 s, chapter 7.20 s, tail 1.32 s`.

#### Scenario: A chapter without a take
- **WHEN** `check` passes on a source with a chapter whose times are all
  numbers and whose speech was never generated
- **THEN** its line says it has no cached take and gives its length, and no
  speech is requested.

### Requirement: `check` measures a document's set layouts

When a movie document shows a picture or comes in by a reframe, `check`
SHALL, after bundling the stage and before reading any take, measure the
layout of every set kind its shots use, once per kind, at the output size,
on the page the renderer serves, with the movie's bundle and no viewer
mounted: for each slot, its box, the box a picture element placed there
gets, and whether its box changes when the set's slots hold content. It
SHALL print one line per measured set giving each slot's box, or that the
slot is sized by what it holds. For each picture shown in a slot whose box
does not change with content, `check` SHALL print its peak enlargement and
its allowance, and MUST refuse, before any take is read, a raster picture
whose peak enlargement (the fit's scale in the measured box times the
largest zoom of its view keys) exceeds its allowance, naming the picture,
the shot, the enlargement, the source size, the slot's box and set, and the
allowance. For each reframe, `check` SHALL print the views it moves with
their outgoing and incoming slots' boxes, and MUST refuse, before any take
is read, a reframe whose outgoing or incoming slot is sized by what it
holds, naming the shot, the view, the set and the slot. Once the takes
resolve the times, `check` MUST refuse a still's view that, at any output
frame of its cue, shows the background beside a picture that overfills the
measured box or cuts off one that underfills it, naming the shot, the video
time, the element and the picture. A picture in a slot sized by what it
holds SHALL be reported as checked at preview and render, which judge it
against the box the stage reports. `check` MUST NOT open a browser for a
movie document that shows no picture and has no reframe, or for a YAML
episode, and MUST NOT need a viewer bundle to measure. Every browser
session of `preview` and `render` SHALL measure, on its own page before its
first frame, the slot boxes its reframes move views between.

#### Scenario: The tour's plate
- **WHEN** `check` runs on the fixture tour, whose still of 864×576 pixels
  is shown with `contain` in the `plate` slot of `Playbill` and keyed to a
  zoom of 1.4, in a 1280×720 film
- **THEN** it prints `Playbill`'s layout, with `plate` 870.4×576 and
  `headline` sized by what it holds, and `peak 1.40×; allowance 1.5×` for the
  still.

#### Scenario: The tour's reframe
- **WHEN** `check` runs on the fixture tour, whose `question` comes in by a
  reframe moving `opening.wide` from `Playbill`'s `stage` to
  `PlaybillSplit`'s `right`
- **THEN** it prints one `Reframe` line naming `question`, `opening.wide`
  and both slots with their measured boxes.

#### Scenario: A lowered allowance, before speech
- **WHEN** the tour's still is given an allowance of 1.2 and no take has
  been cached
- **THEN** `check` refuses it as enlarged 1.40× in shot `still`, naming the
  870.4×576 box of slot `plate` of set `playbill` and the allowance 1.2, and
  does not ask for the takes.

#### Scenario: A view that leaves the picture
- **WHEN** the tour's still's first view key is centred at (0.1, 0.5) at
  zoom 1
- **THEN** `check` refuses it naming the shot `still`, the time 16.67 s,
  the element `tip.plate` and the still `plate`.

#### Scenario: No picture, no browser
- **WHEN** `check` runs on a movie document whose shots show no picture and
  have no reframe
- **THEN** it launches no browser and prints no layout.

### Requirement: A clocked take is recorded in the document

A document that films a clocked machine SHALL say `model.timeMode: "take"`
and carry a `take` block: `kind` `clocked`; the machine `identity` its
export publishes; `initial`, the bank before the first step, every driver
and state by qualified id; `steps` in play order, each with a slug `id`,
its `at` in take seconds (the sum of the durations before it), its
`duration`, the `input` it moves, exactly one of `to` and `by`, and the
request the framework returned verbatim (`origin`, `end`, `admitted`,
`commits` with `fraction`, `value`, `targets` and `relations`, and
`stops`); and `banks`, the recorded bank at every mark. Its
`expectedDurationSeconds` SHALL be the take's length, the last step's `at`
plus its `duration`; its `marks` SHALL name take seconds, each 0 or the end
of a step; a shot's model time (`from`, `to`, a key's `seconds`, a mark
with its `plus`) SHALL be take seconds within the take. A posed loop's
document says `normalized-loop` and carries no `take` block.

Before any take of speech is read, a runtime MUST refuse, naming what is at
fault: a `timeMode` that is neither `normalized-loop` nor `take`; a `take`
document without a `take` block, naming `model.timeMode`; a loop document
with one; given the export's manifest, an export that publishes no clocked
machine, an `identity` that differs from the export's (naming
`take.identity` and `clocked.identity`), a step whose `input` the export
does not declare (naming `take.steps[i]`, the step's id, `input` and the
name), and an `initial` bank whose ids are not the export's drivers and
states; steps that do not play end to end from 0, a step with both or
neither of `to` and `by`, a step id used twice; a length that is not the
take's; a mark that is not 0 or the end of a step, or that has no bank; and
a shot whose model time is outside the take, naming the chapter, the shot,
the field and `outside the take`.

#### Scenario: The counter's document
- **WHEN** the fixture movie `count` evaluates
- **THEN** its document says `"timeMode": "take"`,
  `"expectedDurationSeconds": 8`, marks `one` 2, `nine` 6 and `ten` 8, and
  a `take` block whose identity is the counter export's `clocked.identity`.

#### Scenario: A step naming an input the export lacks
- **WHEN** a take document's first step moves `cranky`
- **THEN** it is refused naming `take.steps[0]`, `step-1`, `input` and
  `cranky` (Python in this change; Node in `pose-a-take`).

#### Scenario: Model time past the take
- **WHEN** a shot of a take document runs model time to 9 and the take
  lasts 8 s
- **THEN** it is refused naming the chapter, the shot, `model.to` and
  `outside the take` (Python in this change; Node in `pose-a-take`).

#### Scenario: A take document without its take
- **WHEN** a document says `"timeMode": "take"` and has no `take` block
- **THEN** it is refused naming `model.timeMode`, `take` and `missing`
  (Python in this change; Node in `pose-a-take`).

#### Scenario: Another machine's identity
- **WHEN** a take document's identity differs from the one its export's
  `clocked` block publishes
- **THEN** it is refused naming `take.identity` and `clocked.identity`
  (Python in this change; Node in `pose-a-take`).

### Requirement: Both runtimes replay a take and hold its banks to the record

Both runtimes SHALL replay a take document's steps from `initial`: before a
step the bank is the one the step before it ended with; a step ends with
its input at `end` and the `targets` of every commit written. At every
mark, the bank the replay gives (the initial bank at 0, otherwise the bank
the step ending there ended with) MUST equal the recorded bank in `banks`
exactly, id by id, or the document MUST be refused naming
`take.banks.<mark>`, the mark and the first differing id. The Python side
makes this check on every document it evaluates or checks; the Node side
makes it in the `pose-a-take` change, before any frame is resolved.

#### Scenario: A bank that differs from the replay
- **WHEN** the bank recorded at `ten` says `units` 1 and the steps replayed
  from `initial` leave `units` at 0
- **THEN** the document is refused naming `take.banks.ten`, `ten` and
  `units` (Python in this change; Node in `pose-a-take`).

#### Scenario: The evaluated take replays to its record
- **WHEN** the fixture movie `count` is evaluated
- **THEN** the replay of its steps gives exactly the bank recorded at
  `one`, `nine` and `ten`, so the document is accepted.

