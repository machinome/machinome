## MODIFIED Requirements

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
