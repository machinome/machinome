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
with its `plus`) SHALL be take seconds within the take. A posed loop's
document says `normalized-loop` and carries no `take` block.

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
the field and `outside the take`.

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

### Requirement: Both runtimes replay a take and hold its banks to the record

Both runtimes SHALL replay a take document's steps from `initial`: before a
step the bank is the one the step before it ended with; a step ends with
its input at `end` and the `targets` of every commit written. At every
mark, the bank the replay gives (the initial bank at 0, otherwise the bank
the step ending there ended with) MUST equal the recorded bank in `banks`
exactly, id by id, or the document MUST be refused naming
`take.banks.<mark>`, the mark and the first differing id. The Python side
makes this check on every document it evaluates or checks; the Node side
makes it among the static checks, so `check` refuses such a document before
any take of speech is read and no frame of it is resolved.

#### Scenario: A bank that differs from the replay
- **WHEN** the bank recorded at `ten` says `units` 1 and the steps replayed
  from `initial` leave `units` at 0
- **THEN** both runtimes refuse the document naming `take.banks.ten`, `ten`
  and `units`.

#### Scenario: The evaluated take replays to its record
- **WHEN** the fixture movie `count` is evaluated, and its document is
  checked by Node
- **THEN** the replay of its steps gives exactly the bank recorded at
  `one`, `nine` and `ten`, so the document is accepted.

## ADDED Requirements

### Requirement: The commands film a clocked take, and refuse a running machine

`check`, `preview`, `render` and `build` SHALL load a document whose
`model.timeMode` is `take` and whose export publishes the clocked machine
its `take` block was recorded on, resolve it against its cached takes of
speech as any document, and film it. A document whose `model.timeMode` is
`normalized-loop` MUST be refused when its export publishes a clocked
machine, naming `model.timeMode` and the export's `clocked` block, and an
export that publishes a running program MUST be refused for either time
mode, naming `program`. A YAML episode is loaded and refused as before.

#### Scenario: The counter on the commands
- **WHEN** `check` runs on the fixture movie `count`
- **THEN** it passes, and `preview` and `render` film it.

#### Scenario: A clocked export filmed as a loop
- **WHEN** a document says `"timeMode": "normalized-loop"` and its export's
  manifest has a `clocked` block
- **THEN** the load refuses it naming `model.timeMode` and `clocked`.

#### Scenario: A running machine
- **WHEN** a document's export has a `program` block
- **THEN** the load refuses it naming `program` and that a running machine
  is not filmable.

### Requirement: A view on a take is posed by the bank of its take time

In a take document, the frame SHALL give each placed view element `bank`,
the machine's whole bank at the view's take time, and no loop `time`. The
take time is the shot's model time at that instant, its marks and keys
resolved in take seconds. The bank at a take time `t` SHALL be: `initial`
for `t` at or before 0; otherwise, for the step with `at < t ≤ at +
duration` and `f = (t − at) / duration`, the bank before that step with its
input at `origin + f · (end − origin)` (exactly `end` at `f = 1`) and the
`targets` of every commit whose `fraction ≤ f` written; past the last step,
the bank it ended with. The bank SHALL be computed from the document alone,
the same instant twice giving the same bank.

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

### Requirement: `check` reports the take

For a take document, `check` SHALL print, after the chapters' lines, one
line giving the take's number of steps, each mark with its take seconds,
the take's length, and that the replay of its steps gives the recorded bank
at every mark.

#### Scenario: The counter's take
- **WHEN** `check` passes on the fixture movie `count`
- **THEN** it prints `Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s
  long; the replay of its steps gives the recorded bank at every mark`.

### Requirement: Preview and render hold the viewer to the take

Before the first frame of a session, `preview` and `render` SHALL replay
each step of a take document on the viewer: restore the bank before the
step on the viewer's machine with the take's identity, ask the same move
(`to` or `by`), and compare the request the viewer returns with the record
exactly: `origin`, `end`, the number of commits and each commit's
`fraction`, `value` and `targets`. On any difference they MUST stop before
capturing, naming the step (its id and `take.steps[i]`) and the field. At
every posed frame, the bank the stage reports for a view on a take MUST be
exactly the frame's, and at a frame whose take time is a mark exactly the
recorded bank at that mark, or the session MUST stop naming the view, the
shot, the time, the mark when there is one, and the first differing id.

#### Scenario: A viewer that writes another digit
- **WHEN** the viewer's answer to `step-2` writes units 7 at its first
  commit where the take records 2
- **THEN** `preview` stops before capturing, naming `step-2`,
  `take.steps[1]` and `commits[0].targets.units`.

#### Scenario: The fixture counter on the real viewer
- **WHEN** the fixture movie `count` is previewed with a Viewer API 29
  bundle
- **THEN** every step's request equals the record, and the bank at the
  marks `one` and `nine`, where shots begin, equals the record.
