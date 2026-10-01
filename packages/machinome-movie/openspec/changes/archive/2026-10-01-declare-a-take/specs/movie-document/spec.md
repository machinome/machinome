## ADDED Requirements

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
