## Why

The episode is the Curta film of the curta-video campaign, *Addition*
(the Curta Type I 3x project, `23 + 145`;
`workflow/ongoing/curta-video-campaign/plan.md`, "What the film needs that
the tool lacks", 1). The Curta that adds is `ClockedCurta`, a clocked
machine: it stands at a bank of values and moves only when asked, one
request at a time, committing its result and turns registers at the events
a stroke crosses. It has no loop. The package can declare only a `Loop`,
evaluation refuses an export without `animation.loop` ("only a posed model
with a normalized loop is filmable"), and the commands refuse anything but
a posed normalized loop. Nothing the film shows (setting 3 and 2, the crank
turning, the result reading 23, then 145 and the carry to 168) can be
declared.

The contract for this is written (`docs/movie-document.md`, "The take", and
the `take` block of `schema/machinome-movie-0.2.json`, the orchestrator's,
1 October 2026): a movie declares a **take**, the steps the machine is asked
to make with the seconds each is drawn over and the marks its shots cut on;
evaluation runs the steps once through the framework's simulation and
records what the machine did; the document carries the record, so a frame
is a pure function of take time and the viewer can be held to the same
answer. This change is the Python side of that contract: the declarations,
their evaluation and the fixture both runtimes share. The Node side
(loading `timeMode: "take"`, the bank per frame, the stage, the viewer
double's machine and layer 6) is the next change, `pose-a-take`.

What the film does with the result: `videos/addition/` of the Curta project
declares `class Addition(Take)` beside `ClockedCurta`, with `Move`s of the
setting slides, `Trigger("Turn crank")` and marks `set_23`, `added_23`,
`set_145`, `added_145`; its shots run model time between those marks; the
evaluated document carries the recorded requests and banks that
`pose-a-take` poses and holds the real viewer to.

## What Changes

- **`Take`, the second kind of take beside `Loop`.** Declared beside the
  model with `model`, `export`, `readiness`, cameras, layers, source
  excerpts and stills exactly as a `Loop` takes them, and `steps`, a list
  of `Move(input, to=|by=, over=seconds)`, `Trigger(instruction)` and
  `Mark(name)`. An input is the model's own `Driver` declaration
  (`Counter.crank`) or the qualified id the framework's `Sim` takes; an
  instruction is a key of the model's `instructions` table or the
  `Instruction` it holds. A trigger is drawn over its instruction's declared
  duration; a move over its `over`. Take time is the sum of the durations;
  a mark is the instant after the step before it (a mark before every step
  is the initial bank, at 0). A `View`, `Source.panel`, `Picture`, `run`
  and `keys` work on a `Take` as on a `Loop`.
- **Refused at class creation, by name** (the take, the step's place in
  `steps` and the step as written): a step that is neither a `Move`, a
  `Trigger` nor a `Mark`; a `Move` with both `to` and `by` or neither, or
  without a positive `over`; an input that is not a driver the model
  declares; an instruction the model's table does not hold, or one without
  a duration; a mark that is not a name, named twice, or at the instant of
  another mark; a `Take` with no `Move` or `Trigger`; a `Take` that writes
  `marks`. A shot's model time outside the take (`0` to its length) is
  refused naming the shot.
- **Evaluation records the take.** A movie on a `Take` evaluates with
  `model.timeMode: "take"`, `model.expectedDurationSeconds` the take's
  length, `marks` in take seconds, and the `take` block of the contract:
  `kind: "clocked"`, the `identity` the export's `clocked` block publishes,
  `initial` (the bank before the first step), each step with its `id`,
  `at`, `duration`, `input`, `to` or `by` and the request the framework
  returned verbatim (`origin`, `end`, `admitted`, `commits` with `fraction`,
  `value`, `targets` and `relations`, and `stops`), and `banks` at the
  marks. Recording constructs the framework's `Sim` over the declared model
  once per evaluation and makes the steps with `sim.move` and `sim.trigger`;
  two evaluations are identical. An export that publishes no clocked
  machine, a model the framework does not simulate as clocked, a request
  the framework refuses, and a step stopped before it travels at all are
  refused naming the take, the step and the framework's words.
- **The document check knows takes** (Python now; the same rules are the
  Node side's in `pose-a-take`): `timeMode` is `normalized-loop` or `take`;
  a `take` document has a `take` block and a loop document none; given the
  manifest, the identity is the export's, every step's input is a driver
  it declares and `initial` holds exactly its drivers and states; steps
  play end to end from 0, each with one of `to` and `by`; the take's length
  is `expectedDurationSeconds`; every mark is 0 or the end of a step and
  has its bank; the steps replayed from `initial` by the contract's rule
  give the recorded bank at every mark, or the document is refused naming
  the mark and the first differing id; a shot's model time is inside the
  take.
- **The fixture.** The framework tutorial's clocked counter
  (`docs/tutorial/counter/c09_clocked.py` and the chapters it imports),
  copied whole into the fixture project as `models/counter.py` with its
  `digits.svg`, registered as the model `counter`, exported for real to
  `export/counter/`; the take `Turns` in `videos/takes.py` (a turn, eight
  more to nine, the turn that carries, with marks); the movie
  `videos/count/` (three shots on `Frame` and `Split`, a view on the take,
  a source panel); its document registered in `fixtures/manifest.json`
  with its speech double; five invalid documents: a step naming an unknown
  input, a shot's model time past the take, a `take` document without a
  `take` block, a bank that differs from the replay, an identity that
  differs from the export's. `scripts/pin-fixture-project.mjs` writes the
  project's revision into every export of the project, not only the
  seesaw's.
- **Records**: ADR-011 (SOURCE): a clocked take is the framework's
  requests, recorded once by evaluation. `docs/declaring-a-movie.md` gains
  "The take, clocked"; `README.md`'s status line; `fixtures/README.md`;
  `docs/architecture-overview.md` where it draws the package;
  `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `declarative-movie`: a movie may film a clocked take declared with
  steps and marks; evaluation records it through the framework's
  simulation; the take's refusals; what evaluation may read.
- `movie-document`: the `take` block, `timeMode: "take"`, marks in take
  seconds, the checks of a take document, and the replay check both
  runtimes make (Node in `pose-a-take`).

## Impact

Code: `python/machinome_movie/take.py` (the shared base of `Loop` and
`Take`, the steps), `evaluate.py` (the recording), `document.py` (the take
checks), `stage.py` (a view, panel or picture on a `Take`), `__init__.py`;
the Python tests; `scripts/pin-fixture-project.mjs`; the fixture project,
`fixtures/`. No Node source, stage source or renderer changes. The schema
and the contract page are the orchestrator's and are not changed.

The Node suite goes red on the merge, by design, until `pose-a-take`: it
loads every registered document and refuses every invalid one by its listed
words, and today it refuses any `timeMode` but `normalized-loop` and knows
no take rule. The evidence names the failing tests; the orchestrator carries
the red between the two changes, as `declarative-stage` carried its red to
`react-stage`.

Adding the counter changes the fixture project's revision, so `minimal` and
`tour` are re-pinned (`sourceRevision` only) and every slow test misses the
memo once.

## Non-goals

The Node side: loading a take document, the bank per frame, the stage's
`restore`, the viewer double's machine, the parity checks on the real
viewer and layer 6 (`pose-a-take`). The posed loop is unchanged. No
framework change: a clocked `Sim` publishes what a take needs. No command
that records takes outside a movie's evaluation. No `rate`, no running
machine, no instruction declared on a child (its qualified id cannot be
named before the tree exists, and the Curta's are its root's). No
publication, push or paid request.
