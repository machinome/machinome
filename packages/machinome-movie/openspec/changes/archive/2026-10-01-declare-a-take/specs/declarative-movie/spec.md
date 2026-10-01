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
`pyproject.toml`); a movie that films a clocked take SHALL in addition run
the framework's simulation of the declared model once, which reads only the
model's own project files. Evaluation MUST NOT read a clock, draw
randomness, reach the network or build CAD, and two evaluations of the same
sources MUST be byte-identical. Anchors SHALL stay symbolic: a phrase, the
end of a phrase, the end of the narration, or a mark, with an optional
offset; the tool evaluating the movie never reads speech. `lines.end()`
SHALL evaluate to `{"narrationEnd": true}`, with its `plus` when one is
given, and never to a phrase the author did not write. Nothing of
`machinome-movie/0.1` is emitted.

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

## ADDED Requirements

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
when no step is before it. A `View`, a source panel, a `Picture` and a
shot's model time (`run`, `keys`) SHALL work on a `Take` as on a `Loop`,
with model time in take seconds or marks.

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
