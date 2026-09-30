## MODIFIED Requirements

### Requirement: A movie evaluates to one deterministic document

Evaluating a movie SHALL produce a `machinome-movie/0.2` document with the
fields of the contract page, written as canonical JSON: a `stage` block
listing the stage modules, every set kind a shot uses (with the project sets
they derive from) and every project element kind a chapter declares;
chapters declaring their elements; shots naming their set, their placements,
their end, their model time and their cues of actions. Evaluation MUST open
only the export's manifest and source revision and the source files of the
excerpts an emphasis lights (and, from the command line, the project's
`pyproject.toml`), MUST NOT read a clock, draw randomness, reach the network
or build CAD, and two evaluations of the same sources MUST be byte-identical.
Anchors SHALL stay symbolic: a phrase, the end of a phrase, or a mark, with an
optional offset; the tool evaluating the movie never reads speech. Nothing of
`machinome-movie/0.1` is emitted.

#### Scenario: Evaluate twice
- **WHEN** a movie is evaluated twice
- **THEN** both documents are identical byte for byte.

#### Scenario: Timing on a phrase
- **WHEN** a shot lasts until `lines.spoken("In the model")`
- **THEN** its `until` in the document is `{"spoken": "In the model"}`, and
  no seconds are written for it.

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

## ADDED Requirements

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
line of the excerpt. Its cue's anchor MUST be a spoken phrase without offset;
each spoken part MUST occur exactly once in that phrase, word-bounded; each
token MUST occur exactly once in the whole excerpt, identifier-bounded, so a
dotted path such as `feed.pawl.turn` is one token.

#### Scenario: A concept spelled differently in the source
- **WHEN** a cue anchored on "the rocker pulls a hook, the driving pawl, and
  the ratchet" emphasises `("the driving pawl", "feed.pawl.turn")`
- **THEN** the action's words hold `{"spoken": "the driving pawl", "token":
  "feed.pawl.turn"}`, and evaluation accepts it because the token occurs once
  in the excerpt.

#### Scenario: A segment of a dotted path
- **WHEN** the token is `waterwheel` and the excerpt spells it only inside
  `water_drive.waterwheel.spin`
- **THEN** evaluation refuses, naming `waterwheel`, `absent` and the excerpt.

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
