## MODIFIED Requirements

### Requirement: Evaluation records a take through the framework's simulation

Evaluating a movie that films a `Take` SHALL record the take once: it SHALL
construct the framework's simulation of the declared model, make each step
with the simulation's own request (`move` or `trigger`) in order, and write
the document's `take` block from what the framework returned: the bank
before the first step, each step's request verbatim, and the bank at every
mark; with `model.timeMode` `take`, `model.expectedDurationSeconds` the
take's length, `marks` in take seconds, and the machine identity the
framework's simulation of the model reports (`Sim(model).identity`). The
tool MUST refuse, naming the take: an export that publishes no clocked
machine; a model the framework does not simulate as a clocked machine; a
model whose simulation's identity differs from the export's
`clocked.identity`, before any step is made, naming the model as
`module:Class`, the export, both identities and what to do (export the
model again, or declare the model the export was made from); and, naming
the step and the framework's own words, a request the framework refuses
and a step that admits no travel because the machine stopped it.

#### Scenario: The requests recorded verbatim
- **WHEN** the fixture movie `count` is evaluated
- **THEN** its `take` block is `kind` `clocked` with the identity the
  framework's simulation of the counter reports, which is the export's,
  `initial` `{"crank": 0, "tens": 0, "units": 0}`, the move's step with
  `origin` 360, `end` 3240 and eight commits, the last writing `units` 9,
  and the bank at `ten` `{"crank": 3600, "tens": 1, "units": 0}`.

#### Scenario: A model changed since its export
- **WHEN** a copy of the fixture project whose counter advances its units
  by two at each stroke, with the same drivers and states, or whose state
  `tens` is renamed `decades`, is evaluated against the counter export made
  before the change
- **THEN** evaluation is refused naming `Take Turns`,
  `models.counter:Counter`, the export, the export's `clocked.identity`,
  the identity the copy's simulation reports and `export the model again`,
  and no step is made.

#### Scenario: An input the machine does not have
- **WHEN** a take moves `"cranky"` and the counter declares only `crank`
- **THEN** evaluation is refused naming the take, the step and the
  framework's words, which name `cranky` and `crank`.

#### Scenario: A step the machine stops
- **WHEN** a take, after a turn, moves the crank back by 100, against its
  ratchet
- **THEN** evaluation is refused naming the step and the stop the
  framework reports.
