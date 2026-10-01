# declarative-movie Specification

## Purpose
A project declares a movie of its model in Python, lists it in
`pyproject.toml`, and evaluates it once, purely, to the movie document the
renderer reads; mistakes are refused by name before speech is generated.
Created by the archived change `declarative-movie`.
## Requirements
### Requirement: A movie is declared in Python and listed in the project

An author SHALL declare a movie as a Python class tree in the project: a
`Movie` whose chapters are `Chapter` instances, each chapter owning one
`Narration`, the elements its shots place and its `Shot`s, found by type in
declaration order and named by the attribute that holds them. The project
SHALL list the movie in `pyproject.toml` under `[tool.machinome.movies]` as
`name = "module:Class"`, as it lists models, and the tool SHALL list and
evaluate the movies of a project from that table.

#### Scenario: List a project's movies
- **WHEN** the author runs `python -m machinome_movie list <project>`
- **THEN** every name in the project's `[tool.machinome.movies]` table is
  printed with its reference, in table order.

#### Scenario: Evaluate a movie by name
- **WHEN** the author runs `python -m machinome_movie evaluate <project> <movie>`
- **THEN** the movie's module is imported from the project and its document
  is written to `_build/movie.json` beside the module, with `root` `..`.

#### Scenario: Unknown movie name
- **WHEN** the name is not in the table
- **THEN** the command refuses, naming it and the movies the table declares.

### Requirement: A movie evaluates to one deterministic document

Evaluating a movie SHALL produce a `machinome-movie/0.2` document with the
fields of the contract page, written as canonical JSON: a `stage` block
listing the stage modules, every set kind a shot uses (with the project sets
they derive from) and every project element kind a chapter declares;
chapters declaring their elements; shots naming their set, their placements,
their end, their model time and their cues of actions. Evaluation MUST open
only the export's manifest and the source files of the excerpts an emphasis
lights (and, from the command line, the project's `pyproject.toml`); a
movie that films a clocked take SHALL in addition run the framework's
simulation of the declared model once, which reads only the model's own
project files. The document's `model.sourceRevision` SHALL be the export
manifest's `source.revision`, the revision the framework recorded when it
exported the model; an export whose manifest has no `source` MUST be
refused, naming the manifest, `source.revision` and that the model must be
exported again from the project's Git repository with a commit, and no
other file beside the manifest is read for it. Evaluation MUST NOT read a
clock, draw randomness, reach the network or build CAD, and two evaluations
of the same sources MUST be byte-identical. Anchors SHALL stay symbolic: a
phrase, the end of a phrase, the end of the narration, or a mark, with an
optional offset; the tool evaluating the movie never reads speech.
`lines.end()` SHALL evaluate to `{"narrationEnd": true}`, with its `plus`
when one is given, and never to a phrase the author did not write. Nothing
of `machinome-movie/0.1` is emitted.

#### Scenario: Evaluate twice
- **WHEN** a movie is evaluated twice
- **THEN** both documents are identical byte for byte.

#### Scenario: Evaluate a clocked take twice
- **WHEN** the fixture movie `count`, which films the counter's take
  `Turns`, is evaluated twice
- **THEN** both documents are identical byte for byte, and neither
  evaluation read a clock, drew randomness, reached the network or made a
  CAD workplane.

#### Scenario: Timing on a phrase
- **WHEN** a shot lasts until `lines.spoken("In the model")`
- **THEN** its `until` in the document is `{"spoken": "In the model"}`, and
  no seconds are written for it.

#### Scenario: Timing on the end of the narration
- **WHEN** a shot lasts until `lines.end(plus=0.9)` in a chapter whose
  narration ends "Up. Down. Up."
- **THEN** its `until` in the document is `{"narrationEnd": true, "plus":
  0.9}`, and no phrase of the narration is written for it.

#### Scenario: The document is valid
- **WHEN** any movie evaluates
- **THEN** its document validates against `schema/machinome-movie-0.2.json`.

#### Scenario: The stage block lists what the movie uses
- **WHEN** a movie's shots use the project set `LeonardoSplit`, derived from
  `Leonardo`, and the shipped `Frame`, and a chapter declares a `Jobs`
  element, all drawn by `stage.tsx` beside the movie
- **THEN** `stage.modules` is `["stage.tsx"]`, `stage.sets` holds
  `leonardo-split` with `base` `leonardo`, `leonardo` itself and `frame`
  with its slots only, and `stage.elements` holds `jobs` with its props'
  kinds and its actions' parameter kinds.

#### Scenario: The revision comes from the manifest
- **WHEN** the fixture movie `tour` is evaluated from the seesaw's export,
  whose manifest records `source.revision`
- **THEN** the document's `model.sourceRevision` is that revision, and the
  files evaluation opened are the manifest and the emphasised excerpt.

#### Scenario: An export without a source
- **WHEN** a movie is evaluated from an export whose manifest has no
  `source`
- **THEN** evaluation refuses, naming the movie, the manifest and
  `source.revision`, and saying to export the model again.

### Requirement: Parts are named by the model's declarations

A cue, a highlight or a layer SHALL name a part by the declaration path of
the model class (`Mill.feed.pawl`, `Mill.carriage`), never by a string. The
tool SHALL resolve it to the export's names and MUST refuse, at evaluation, a
path the export does not contain, naming the path as written and the export
path it resolved to.

#### Scenario: A path resolved to export names
- **WHEN** a ring is drawn around `LeonardoHydraulicSawmill.feed.pawl`
- **THEN** the document names the part `["Feed mechanism", "Driving pawl"]`.

#### Scenario: A stale export
- **WHEN** the model declares a part the export lacks
- **THEN** evaluation refuses, naming the declaration path.

### Requirement: Mistakes are refused by name before speech

The tool MUST refuse, naming the chapter or movie, the shot, and the thing at
fault (the slot, the element, the action, the parameter, the token, the
field), at class creation where every class involved is known and at
evaluation otherwise: a slot the shot's set does not declare, a slot filled
twice, an element the chapter does not declare, an element placed in two
slots of one shot, a phrase absent from or repeated in the chapter's
narration, an unknown mark, model keys that do not start at the shot's start
and end at its end, a camera not declared on the view's take, an action on an
element the shot does not place, a spanning action without the cue's
`until`, a project action's parameter missing, unknown or of the wrong type,
a project set or element without a stage module or with a prop that is not a
JSON value, an emphasis whose anchor is not a spoken phrase without offset, a
spoken word absent from or repeated in that phrase, a token absent from or
repeated in its excerpt, and a placed source panel whose typing does not
complete the excerpt when no earlier shot of the chapter completed it.

#### Scenario: A misspelled phrase
- **WHEN** a shot lasts until `lines.spoken("Buut")` and the narration says "But"
- **THEN** the chapter's class is refused, naming the chapter, the shot,
  `until` and `Buut`.

#### Scenario: A camera of another take
- **WHEN** a view on one loop moves to a camera declared on another
- **THEN** the chapter is refused, naming the shot and the camera.

#### Scenario: A project set
- **WHEN** a project declares its own `Set` subclass without a `module`
- **THEN** it is refused at class creation, naming the class and `module`,
  because a project's set is drawn by the stage module it names.

#### Scenario: A slot the set does not declare
- **WHEN** a shot on `LeonardoSplit` places an element in `LeonardoSplit.stage`
- **THEN** the chapter is refused, naming the shot, `stage`, `LeonardoSplit`
  and the slots it declares.

#### Scenario: A project action with a wrong parameter
- **WHEN** a cue calls `jobs.light(job=2)` and `light` declares `job=str`
- **THEN** it is refused naming `Jobs`, `light`, `job` and `string`.

#### Scenario: A token repeated in its excerpt
- **WHEN** an emphasis lights `drives` and the excerpt holds it twice
- **THEN** evaluation refuses naming the chapter, the shot, `drives` and the
  excerpt.

### Requirement: The shared fixtures pin the document

Every document registered in `fixtures/manifest.json` SHALL equal the
evaluation of the fixture movie of the same name, and every invalid fixture
that Python can refuse before speech SHALL be refused with a message
containing each of its `must_mention` substrings.

#### Scenario: A fixture document drifts
- **WHEN** a fixture movie's evaluation differs from its registered document
- **THEN** the Python suite fails, naming the fixture.

### Requirement: A project declares its own sets

An author SHALL declare a set as a `Set` subclass in the project with
`module`, the path of the TypeScript or JavaScript stage module that draws
it, relative to the declaring file; `Slot()` declarations, named by
attribute, in order; and plain class attributes, JSON values, as the static
props its component receives. The set's kind SHALL be the slug of its class
name unless the class writes `kind`. A derived set SHALL inherit its base's
chrome and module, not its layout: its slots are those its own body declares,
and the document names its base. A shot MAY leave slots empty. The tool
SHALL ship the sets `Frame` (slot `stage`) and `Split` (slots `left` and
`right`).

#### Scenario: A derived set
- **WHEN** `LeonardoSplit(Leonardo)` declares `left`, `right` and `headline`
- **THEN** its kind is `leonardo-split`, its slots are exactly those three,
  its base is `leonardo`, and its module is the one `Leonardo` names.

#### Scenario: A slot that says what it holds
- **WHEN** a set declares `stage = Slot("view")`
- **THEN** the set is refused, naming the set and the slot, because a set
  does not know what it holds.

#### Scenario: A prop that is not data
- **WHEN** a set's class attribute is a camera or an object
- **THEN** the set is refused naming the set and the attribute.

### Requirement: A project declares its own elements

An author SHALL declare an element as an `Element` subclass in the project
with `module` and `Action(param=type, …)` declarations, each parameter typed
`str`, `int`, `float` or `bool`. An instance's keyword arguments SHALL be its
props, JSON values checked when it is created. Calling a declared action on
an instance SHALL yield a cue's action whose parameters are checked, by name,
against the declared types. The element's kind SHALL be the slug of its class
name.

#### Scenario: A card lit on cue
- **WHEN** a chapter declares `jobs = Jobs(jobs=["Move the saw", "Feed the
  log"])` and a cue does `jobs.light(job="saw")`
- **THEN** the chapter's `elements` hold `{"kind": "jobs", "props": {"jobs":
  [...]}}` and the cue's action is `{"element": "jobs", "action": "light",
  "params": {"job": "saw"}}`.

#### Scenario: An action parameter of an unsupported type
- **WHEN** an element declares `light = Action(job=list)`
- **THEN** the element is refused naming the element, `light` and `job`.

### Requirement: The shipped elements carry their actions

The tool SHALL ship the elements `View` (a camera on the take, with the
actions `move`, `highlight`, `ring`, `label` and `arrow`, whose marks point
at parts of that view), `Source.panel` (an excerpt, with `type` and
`emphasize`), `Title` (text and an optional subtitle, with `show`, its fades
and a spoken reveal) and `Picture` (a still of the take, with `show`, its
fades and keyed pan and zoom). Titles and pictures are elements placed in a
set's slots, not actions.

#### Scenario: A mark bound to its view
- **WHEN** a cue does `mill.ring(Mill.feed.pawl, enter=("draw", 0.8))`
- **THEN** the action names the element `mill`, the action `ring` and the
  part as export names, and the shot must place `mill`.

#### Scenario: A title in a slot
- **WHEN** a shot places `title = Title("CUT AND ADVANCE", subtitle="One
  wheel, two jobs")` in `Leonardo.headline` and a cue does
  `title.show(enter=0.6, leave=0.6)`
- **THEN** the shot's `places` map `headline` to `title` and the cue shows it
  with two fades of 0.6 s.

### Requirement: Emphasis pairs spoken words with source tokens

`emphasize` SHALL take words, each either a token spelled as the narrator
says it or a pair of the spoken words and the source token they light, on any
line of the excerpt, and an optional `line`. Its cue's anchor MUST be a spoken
phrase without offset; each spoken part MUST occur exactly once in that
phrase, word-bounded (not preceded or followed by an ASCII letter, digit or
underscore). A token is an identifier or a dotted path of identifiers and
occurs where its text is word-bounded the same way, a dot being a boundary:
`waterwheel` occurs in `water_drive.waterwheel.spin`, `feed.pawl.turn` is one
token, `pawl` does not occur in `pawl_mount`. Each token MUST occur exactly
once in the whole excerpt or, when `line` names a file line inside the
excerpt, exactly once on that line; a `line` outside the excerpt MUST be
refused naming it.

#### Scenario: A concept spelled differently in the source
- **WHEN** a cue anchored on "the rocker pulls a hook, the driving pawl, and
  the ratchet" emphasises `("the driving pawl", "feed.pawl.turn")`
- **THEN** the action's words hold `{"spoken": "the driving pawl", "token":
  "feed.pawl.turn"}`, and evaluation accepts it because the token occurs once
  in the excerpt.

#### Scenario: A word inside a dotted path, chosen by line
- **WHEN** the excerpt spells `waterwheel` inside `water_drive.waterwheel.spin`
  on two of its lines and the action names `line=415`
- **THEN** evaluation accepts `waterwheel` as a token occurring once on that
  line and writes `"line": 415` on the action; without `line` it refuses,
  naming `waterwheel`, `ambiguous` and the excerpt.

#### Scenario: A token absent from the named line
- **WHEN** the token occurs in the excerpt but not on the `line` the action names
- **THEN** evaluation refuses, naming the token, `absent` and `line`.

### Requirement: An element keeps its state across its chapter

An element SHALL be one instance across the shots of the chapter that
declares it. A source panel completed by an earlier shot of the chapter
SHALL need no typing when a later shot places it again, and typing it again
MUST be refused; a shot placing a panel not yet completed MUST type it
through its last line.

#### Scenario: A completed panel placed again
- **WHEN** `pawls` types the excerpt through its last line and `holding`, the
  next shot of the chapter, places the same panel with no typing cue
- **THEN** the chapter is accepted.

### Requirement: A clocked machine is filmed through a declared take

An author SHALL be able to declare a `Take`, the second kind of take beside
`Loop`, beside the model with `model`, `export`, `readiness`, cameras,
layers, source excerpts and stills exactly as a `Loop` takes them, and
`steps`: a list of `Move(input, to=|by=, over=seconds)`,
`Trigger(instruction)` and `Mark(name)`. An input SHALL be named by the
model's own `Driver` declaration or by the qualified id the framework's
simulation takes; an instruction by its key in the model's `instructions`
table or by the `Instruction` that table holds. A move SHALL be drawn over
its `over`, a trigger over its instruction's declared duration; take time
SHALL be the sum of the durations, each step starting where the one before
ended, and a mark SHALL name the instant after the step before it, or 0
when no step is before it. The sum SHALL be exact: each duration is the
decimal its shortest form writes, the durations are added without
rounding, and a step's start, a mark and the take's length are the number
nearest that exact sum (an integer when it is whole), never a running sum
of floats. A `View`, a source panel, a `Picture` and a shot's model time
(`run`, `keys`) SHALL work on a `Take` as on a `Loop`, with model time in
take seconds or marks.

The tool MUST refuse at class creation, naming the take, the step's place in
`steps` and the step as written: a step that is neither a `Move`, a
`Trigger` nor a `Mark`; a `Move` with both `to` and `by` or neither, or
whose `over` is not a positive number; an input that is not a driver the
model declares; an instruction the model's table does not hold, or one
with no duration; a mark that is not a name, a mark named twice, and two
marks at one instant; a take with no `Move` or `Trigger`; and a take that
writes `marks`. A shot whose model time lies outside the take, before 0 or
past its length, MUST be refused naming the chapter, the shot and the take.

#### Scenario: The counter's take
- **WHEN** `Turns` declares `Trigger("Turn once")`, `Mark("one")`,
  `Move(Counter.crank, to=3240, over=4)`, `Mark("nine")`,
  `Trigger("Turn once")` and `Mark("ten")`, and the counter's instruction
  `Turn once` declares a duration of 2 s
- **THEN** its steps start at 0, 2 and 6 s, its length is 8 s, its marks
  are `one` at 2, `nine` at 6 and `ten` at 8, and the move's input is
  `crank`.

#### Scenario: Durations that are not binary fractions
- **WHEN** a take on the counter declares three moves of the crank, each
  `over=1.2`, with a mark after each
- **THEN** its steps start at exactly 0, 1.2 and 2.4 s, its marks are
  exactly 1.2, 2.4 and 3.6 and its length is exactly 3.6 s, on the class
  and in the evaluated document, never `3.5999999999999996`.

#### Scenario: A move told both where and how far
- **WHEN** a take declares `Move(Counter.crank, to=3, by=4, over=1)`
- **THEN** its class is refused naming the take, the step's place in
  `steps`, `to` and `by`.

#### Scenario: A mark named twice
- **WHEN** a take marks `one` after two different steps
- **THEN** its class is refused naming the take and `one`.

#### Scenario: Model time past the take
- **WHEN** a shot on `Turns` runs `Turns.run("nine", 9)` and the take lasts
  8 s
- **THEN** the chapter is refused naming the shot and `outside the take`.

### Requirement: Evaluation records a take through the framework's simulation

Evaluating a movie that films a `Take` SHALL record the take once: it SHALL
construct the framework's simulation of the declared model, make each step
with the simulation's own request (`move` or `trigger`) in order, and write
the document's `take` block from what the framework returned: the bank
before the first step, each step's request verbatim, and the bank at every
mark; with `model.timeMode` `take`, `model.expectedDurationSeconds` the
take's length, `marks` in take seconds, and the machine identity the
export's `clocked` block publishes. The tool MUST refuse, naming the take:
an export that publishes no clocked machine; a model the framework does not
simulate as a clocked machine; and, naming the step and the framework's own
words, a request the framework refuses and a step that admits no travel
because the machine stopped it.

#### Scenario: The requests recorded verbatim
- **WHEN** the fixture movie `count` is evaluated
- **THEN** its `take` block is `kind` `clocked` with the export's identity,
  `initial` `{"crank": 0, "tens": 0, "units": 0}`, the move's step with
  `origin` 360, `end` 3240 and eight commits, the last writing `units` 9,
  and the bank at `ten` `{"crank": 3600, "tens": 1, "units": 0}`.

#### Scenario: An input the machine does not have
- **WHEN** a take moves `"cranky"` and the counter declares only `crank`
- **THEN** evaluation is refused naming the take, the step and the
  framework's words, which name `cranky` and `crank`.

#### Scenario: A step the machine stops
- **WHEN** a take, after a turn, moves the crank back by 100, against its
  ratchet
- **THEN** evaluation is refused naming the step and the stop the
  framework reports.

### Requirement: A shot can come in by a reframe

A shot SHALL accept `transition=Reframe(duration, ease=)` beside
`Dissolve`, `Fade`, `Wipe` and `Slide`, written `{"kind": "reframe",
"duration"}` with `ease` when given (smooth otherwise). A reframe whose shot
and the shot before it place no view element in both MUST be refused by
name, at class creation where both shots are known: by the chapter when
both shots are its own, by the movie when the shot is its chapter's first
(whose previous shot is the last of the chapter before, which never shares
a view). The refusal SHALL name the chapter or movie, both shots, the
transition and `no view element in both`. A direction or a colour on a
reframe MUST be refused.

#### Scenario: The tour's reframe
- **WHEN** the fixture tour's `question` places `wide` in
  `PlaybillSplit.right` with `transition=Reframe(0.8)` after `hook`, which
  places `wide` in `Playbill.stage`
- **THEN** it evaluates to `{"kind": "reframe", "duration": 0.8}` on
  `question`, twice identically.

#### Scenario: No view in both shots
- **WHEN** a chapter's shot placing only a source panel comes in by
  `Reframe(0.8)` from a shot placing only a view
- **THEN** the chapter's class is refused naming the chapter, both shots
  and `no view element in both`.

#### Scenario: A chapter that opens with a reframe
- **WHEN** a chapter's first shot comes in by `Reframe(0.8)`
- **THEN** the movie's class is refused naming the shot, the last shot of
  the chapter before and `no view element in both`.

