## Context

The package knows one kind of take, `Loop` (`python/machinome_movie/take.py`):
a posed model's normalized loop, with `marks` in model seconds, and the
declarations a view needs (`Camera`, `Layer`, `Source`, `Still`), each owned
by the first `Loop` that holds it. A `View`, a `Source.panel`, a `Picture`
and a shot's model time (`Loop.run`, `Loop.keys`) name a `Loop`; evaluation
(`evaluate.py`) finds the one take a movie films, reads its export's
`manifest.json` and `source-revision.txt`, refuses an export without
`animation.loop`, and writes `model` with `timeMode: "normalized-loop"`;
`document.py` checks the document against the schema and the rules Python
can check before speech.

The contract (`docs/movie-document.md`, "The take"; the schema's `take`
block and `$defs.bank`) is written. The framework's clocked `Sim`
(`machinome.simulation.Sim`, public surface) gives what a take needs:
`Sim(model)` over a root that declares a `State` takes no `dt`;
`sim.move(input, by=|to=)` and `sim.trigger(name)` return a `Request` with
`input`, `by`, `to`, `origin`, `end` (native units), `admitted` (design
units), `commits` (each `relations`, `fraction`, `value`, `targets`) and
`stops` (each `coordinate`, `side`, `bound`, `value`, `input`, `fraction`);
`sim.snapshot().values` is the bank, every driver and state by qualified id;
`sim.clocked` says whether the root is clocked. The export of a clocked root
(document version 8) carries `drivers`, `states`, `instructions` and a
`clocked` block whose `identity` is a digest of the compiled machine. A
probe on the fixture counter (below) showed that constructing the `Sim` and
making three requests builds no CAD, reads no clock or randomness, and opens
only the project's `pyproject.toml` (several times) and the model's source
file; the `Sim`'s identity equals the export's, but the `Sim` publishes it
only on a private attribute.

## Goals / Non-Goals

Goals: declare the take the film needs exactly as the contract states it;
record it once, deterministically, through the framework's public surface;
refuse every mistake by name, at class creation where the classes know it
and at evaluation otherwise; check a take document in Python by the rules
both runtimes will make; give both runtimes a real clocked fixture. Non-goals:
those of the proposal.

## Decisions

### D1. `Take` beside `Loop`, on one base

`Loop` and `Take` derive from one private base, `_Take`, which carries
what both declare and check identically: `model`, `export`, `readiness`,
the ownership of `Camera`, `Layer`, `Source` and `Still` declarations, the
layer paths, `declarations(kind)`, `export_directory()`, `run(start, end)`
and `keys({...})`. `Loop` adds `marks` written as a mapping; `Take` adds
`steps` and derives `marks` and `length` from them. Every place that asked
"is this a `Loop`" for a view, a panel, a picture or the one-take check
asks "is this a take" (`_Take`). A `Take` that writes `marks` is refused:
its marks are its `Mark` steps.

Rejected: `Take(Loop)`. A take is not a loop: its marks are computed, not
written, its time has an end rather than a period, and every `issubclass(x,
Loop)` check would admit a clocked take where a posed loop is meant (the
`animation.loop` read of evaluation above all).

### D2. Steps, and how they name the machine

`Move(input, *, to=None, by=None, over=None)`, `Trigger(instruction)` and
`Mark(name)` are plain values that store what was written; `Take`
validates them when its class is created, so every refusal can name the
take, the step's place in `steps` and the step as written (`Take Turns:
steps[2], Move(Counter.crank, to=3, by=4): ...`).

What names an input is what the framework resolves: `Sim.move` takes a
driver's **qualified id**, and that id is what the document's `input`
carries. A step may write the model's own `Driver` declaration,
`Counter.crank`, which `Take` resolves at class creation to the attribute
that holds it on the model (or a base), the qualified id of a root driver,
so a misspelling fails at its line as a misspelled part does; or the
qualified id as a string, passed to the framework as written and refused
by the framework's words at evaluation if it names nothing. Both are kept
because each covers what the other cannot: a declaration cannot name a
driver declared on a child before the tree exists, and a string is not
checked until evaluation. An instruction is named the same way: a key of
the model's `instructions` table (`'Turn once'`, the name `sim.trigger`
takes) or the `Instruction` that table holds (`Counter.instructions['Turn
once']`), resolved to its key. It is resolved at class creation, because
its declared `duration` is the step's duration and the take's length must
be known when shots check their model time. An instruction declared on a
child is refused (its qualified name is the tree's), and the film's are
its root's.

Rejected: only declarations (cannot name a child's driver; and the plan's
sketch writes `Move("digit_1", ...)`); only strings (a misspelled driver
found only at evaluation, unlike every part a movie names).

### D3. Take time and marks

A step's `duration` is `over` for a move and the instruction's declared
`duration` for a trigger. Step `k` starts at `at_k = at_{k-1} +
duration_{k-1}`, summed in declaration order from 0, and the take's
`length` is the last step's `at + duration`. A mark is the instant after
the step before it; a mark before every step is at 0 and its bank is
`initial`, as the contract says ("a mark at 0 is the initial bank"). A
mark that is not a name (`[A-Za-z_][A-Za-z0-9_]*`, as a loop's), a mark
named twice, and two marks with no step between them (two names for one
instant) are refused. A take whose steps are all marks is refused as "no
steps": its document would have none, and the schema requires one.

The cycle brief also asks to refuse "a mark before any step"; the contract
gives that mark a meaning. The contract is built and the contradiction is
recorded as a finding with the smallest correction.

### D4. Step ids

A document step's `id` is `step-<n>`, `n` counting the moves and triggers
from 1 in declaration order: a slug, stable while the steps before it are,
and what refusals of the document name beside `take.steps[<n-1>]`. A step
declares no name of its own; nothing in the film needs one, and a refusal
at class creation names the step as written.

### D5. Recording, once, through the public surface

`evaluate()` on a `Take` reads the export's manifest, refuses an export
whose `clocked` block is absent ("publishes no clocked machine") naming the
take and the export, then records: `Sim(model())`, refusing a model the
framework refuses to simulate or that `sim.clocked` says is not clocked;
`initial = sim.snapshot().values`; each step made with `sim.move(input,
to=|by=)` or `sim.trigger(name)`; after each step, the bank of every mark
that follows it. A step's document entry is `id`, `at`, `duration`, the
request's `input`, its `to` or `by`, and `origin`, `end`, `admitted`,
`commits` (`fraction`, `value`, `targets`, `relations` as a list) and
`stops` (`coordinate`, `side`, `bound`, `value`, `input`, `fraction`, the
framework's `Stop` fields) verbatim. The `identity` is the export's
`clocked.identity`, read as `sourceRevision` is read.

The simulation is imported only when a movie films a `Take`, so a loop's
evaluation does not load it. The recording is a pure function of the model's
declarations: the framework's clocked requests are solved exactly, in path
order, with no clock and no tolerance a run could vary, so two evaluations
are identical (asserted).

The brief asks to refuse a `Sim` whose identity differs from the export's
"if the framework exposes it". The public surface does not (`Sim` keeps it
on a private attribute); reading it there is not done. What the document
check does instead (D7), on the evaluated document as on any other, is
refuse an `initial` bank whose ids are not exactly the export's drivers and
states: an export older than a model that gained or lost an input or a state
is refused by name. A changed law with the same ids is not caught in Python;
`pose-a-take`'s parity check on the viewer, which restores with the
document's identity, is where it is. Recorded as a finding (a framework
`Sim` property would close it).

### D6. What the framework refuses

A request the framework refuses (`ValueError`, `KeyError`, `TypeError` or
its clocked errors: an unknown input, a state named as an input, a commit
that writes a state out of its range) is refused naming the
take, the step's id and the step as written, followed by the framework's
own words. A request that stops before travelling at all, `admitted == 0`
with stops where the step asked for travel, is refused the same way with
the stops as the framework writes them: a step the machine refuses to make
is not something to film for its duration. A step stopped part-way is
recorded as the framework returned it, its stops included; the contract's
rule draws it to its `end`.

### D7. The document check knows takes

`check_document` gains the take rules, so the evaluation checks its own
output by them and the shared invalid fixtures run through them:

- `model.timeMode` is `normalized-loop` or `take`, refused naming the value
  otherwise; `take` needs the `take` block (refused as missing, naming
  `model.timeMode`), and a `normalized-loop` document carries none.
- With the manifest: an export without a `clocked` block is refused; the
  `identity` must equal `clocked.identity`, refused naming both; every
  step's `input` must be a driver of the export (or its clock where it
  declares one), refused naming `take.steps[i]`, the step's id, `input` and
  the name; `initial` must hold exactly the export's drivers and states (and
  its clock), refused naming the first id missing or extra.
- Steps: ids unique; exactly one of `to` and `by`; the first at 0 and each
  at the end of the one before (within 1e-9 s, so a hand-written document
  is not refused for a float's last digit); `expectedDurationSeconds` the
  last step's end (same tolerance).
- Marks: each mark is 0 or a step's end (within 1e-9 s), `banks` has
  exactly the marks.
- **The replay.** From `initial`, step by step: the input at `end`, every
  commit's `targets` written; the bank at each mark (the initial bank at 0,
  otherwise the bank after the step ending there) must equal the recorded
  one exactly, id by id, or the document is refused naming
  `take.banks.<mark>`, the mark and the first differing id in sorted order.
  Exact, because both sides hold the framework's floats verbatim and the
  rule only copies them.
- A shot's model time (`model.from`, `model.to`, each key's `seconds`, a
  mark plus its `plus`) must lie in `[0, length]`, refused naming the
  chapter, the shot, the field and `outside the take`. This is checked for
  take documents only: the loop's check against its period is the Node
  side's today and is left as it is.

### D8. Model time on a take at class creation

`Take.run` and `Take.keys` are the base's; a shot's `Simulation.check`
refuses, for a `Take`, a number outside `[0, length]` naming the shot and
`outside the take`, as it refuses an unknown mark. A loop's check is
unchanged.

### D9. The fixture

`models/counter.py` is the tutorial's chapter-9 model with the classes of
chapters 3, 4 and 8 it imports, in one file, unchanged but for its imports,
with a header naming its source, commit and licence, and
`models/digits.svg` beside it, which its drum's marking reads. Registered as
`counter` in the project's models table and exported by the framework's
command (`machinome export counter -o export/counter --no-widget`): four
small meshes. `videos/takes.py` declares `Turns(Take)` (not `Tally`, the
name the brief suggested, which the tour's project element and the manual
already give an element):
`Trigger("Turn once")`, `Mark("one")`, `Move(Counter.crank, to=3240,
over=4)`, `Mark("nine")`, `Trigger("Turn once")`, `Mark("ten")`: a take of
8 s through a trigger (`by`), a move (`to`) with eight commits and the
carry, a camera and the source excerpt of the counter's relations.
`videos/count/movie.py` films it in one chapter of three shots: the view
on `Frame` for the first turn and for the eight more, then on `Split`
beside the typed source panel, with a highlight of the tens drum and an
emphasis of `commits`, joined by a dissolve. Its speech double is made by
the fixtures' recipe. The pin script writes the project's revision into
`source-revision.txt` of every export directory of the project, so the
count document pins it as the tour pins the seesaw's.

### D10. What evaluation may read

A movie on a `Loop` opens what it opens today. A movie on a `Take` also runs
the framework's simulation, which reads the model's own project files (the
project's `pyproject.toml`, the model's source); no clock, randomness,
network or CAD, which a test asserts with a `cadquery.Workplane` that
refuses to be made. The spec and the manual say so.

## Refusal words

The words both runtimes name for the new invalid fixtures (`fixtures/
README.md`, "Refusal words", gains them):

- `take-step-input-unknown`: `take.steps[0]`, `step-1`, `input`, the name;
- `take-model-time-past-the-end`: the chapter, the shot, `model.to`,
  `outside the take`;
- `take-block-missing`: `model.timeMode`, `take`, `missing`;
- `take-bank-differs`: `take.banks.<mark>`, the mark, the differing id;
- `take-identity-differs`: `take.identity`, `clocked.identity`.

## Risks / Trade-offs

- The Node suite is red on the merge until `pose-a-take` (proposal,
  Impact). Mitigation: the evidence names each failing test and its cause.
- A take's evaluation constructs the model and runs the framework: costlier
  than reading a manifest (about 0.15 s for the counter, after the
  framework's import) and dependent on the framework's version. That is the
  contract: the take is what the framework returned.
- The replay is exact; a document edited by hand must copy the framework's
  floats. That is the point of recording them.
