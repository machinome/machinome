## MODIFIED Requirements

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
with its `plus`) SHALL be take seconds within the take. Every one of these
sums SHALL be exact: each duration is the decimal its shortest form writes,
and a step's `at`, the length and a mark are the number nearest the exact
sum of the durations before it (an integer when the sum is whole), so three
steps of 1.2 s end at 3.6. A posed loop's document says `normalized-loop`
and carries no `take` block.

Before any take of speech is read, both runtimes MUST refuse, naming what
is at fault: a `timeMode` that is neither `normalized-loop` nor `take`; a
`take` document without a `take` block, naming `model.timeMode`; a loop
document with one; given the export's manifest, an export that publishes no
clocked machine, an `identity` that differs from the export's (naming
`take.identity` and `clocked.identity`), a step whose `input` the export
does not declare (naming `take.steps[i]`, the step's id, `input` and the
name), and an `initial` bank whose ids are not the export's drivers and
states; steps that do not play end to end from 0, a step with both or
neither of `to` and `by`, a step id used twice; a length that is not the
take's; a mark that is not 0 or the end of a step, or that has no bank; and
a shot whose model time is outside the take, naming the chapter, the shot,
the field and `outside the take`. A step's `at`, the length and a mark
MUST equal the exact sum they stand for, with no tolerance: a document
whose sums were made in floats is refused naming the field.

#### Scenario: The counter's document
- **WHEN** the fixture movie `count` evaluates
- **THEN** its document says `"timeMode": "take"`,
  `"expectedDurationSeconds": 8`, marks `one` 2, `nine` 6 and `ten` 8, and
  a `take` block whose identity is the counter export's `clocked.identity`.

#### Scenario: A step naming an input the export lacks
- **WHEN** a take document's first step moves `cranky`
- **THEN** both runtimes refuse it naming `take.steps[0]`, `step-1`,
  `input` and `cranky`.

#### Scenario: Model time past the take
- **WHEN** a shot of a take document runs model time to 9 and the take
  lasts 8 s
- **THEN** both runtimes refuse it naming the chapter, the shot, `model.to`
  and `outside the take`.

#### Scenario: A take document without its take
- **WHEN** a document says `"timeMode": "take"` and has no `take` block
- **THEN** both runtimes refuse it naming `model.timeMode`, `take` and
  `missing`.

#### Scenario: Another machine's identity
- **WHEN** a take document's identity differs from the one its export's
  `clocked` block publishes
- **THEN** both runtimes refuse it naming `take.identity` and
  `clocked.identity`.

#### Scenario: A mark summed in floats
- **WHEN** a take document's three steps last 1.2 s each, start at 0, 1.2
  and 2.4, its length is 3.6, and its last mark `ten` is written
  `3.5999999999999996`, the float sum
- **THEN** both runtimes refuse it naming `marks.ten` and `end of a step`.

### Requirement: A view on a take is posed by the bank of its take time

In a take document, the frame SHALL give each placed view element `bank`,
the machine's whole bank at the view's take time, and no loop `time`. The
take time is the shot's model time at that instant, its marks and keys
resolved in take seconds. The bank at a take time `t` SHALL be: `initial`
for `t` at or before 0; otherwise, for the step with `at < t ≤ at +
duration` and `f = (t − at) / duration`, the bank before that step with its
input at `origin + f · (end − origin)` (exactly `end` at `f = 1`) and the
`targets` of every commit whose `fraction ≤ f` written; past the last step,
the bank it ended with. A step's end, `at + duration`, SHALL be read as the
document writes it, the next step's `at` or, for the last step, the take's
length, never added again in floats. The bank SHALL be computed from the
document alone, the same instant twice giving the same bank.

#### Scenario: Inside a step
- **WHEN** the counter's frame is resolved at take time 4, half-way through
  `step-2` (crank 360 to 3240 over 4 s, a commit every eighth)
- **THEN** its view's bank has crank 1800 and units 5, the commit at
  fraction 0.5 written and the one at 0.625 not.

#### Scenario: At a mark
- **WHEN** the counter's frame is resolved at take time 6, the mark `nine`
- **THEN** its view's bank is exactly `take.banks.nine`.

#### Scenario: A commit at the very end of a step
- **WHEN** a step's only commit is at fraction 1, as each of the Curta's
  strokes is
- **THEN** no target of it is written before the step's end, and at its end
  every one is.

#### Scenario: A mark the float sum would miss
- **WHEN** a take's third step of 1.2 s starts at 2.4 and ends at the mark
  3.6, and its fourth step has a commit at fraction 0
- **THEN** the bank at take time 3.6 is the one the third step ended with,
  and the fourth step's commit is not written until the instant after.

### Requirement: `check` reports the take

For a take document, `check` SHALL print, after the chapters' lines, one
line giving the take's number of steps, each mark with its take seconds,
the take's length as the document writes it, and that the replay of its
steps gives the recorded bank at every mark.

#### Scenario: The counter's take
- **WHEN** `check` passes on the fixture movie `count`
- **THEN** it prints `Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s
  long; the replay of its steps gives the recorded bank at every mark`.

#### Scenario: A take of decimal durations
- **WHEN** `check` passes on a take whose three steps last 1.2 s each, with
  a mark after each
- **THEN** its take line gives the marks at 1.2, 2.4 and 3.6 s and the
  length `3.6 s long`.
