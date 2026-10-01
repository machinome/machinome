# ADR-011: A clocked take is the framework's requests, recorded once by evaluation

Status: Accepted (OpenSpec change `declare-a-take`, 1 October 2026);
amended in place by `take-identity` (1 October 2026)

Numbered 011 by the curta-video campaign's plan; ADR-010 is another cycle's
of the same campaign. A merge that reorders them renumbers.

## Context

Until this change a movie filmed one kind of take: a posed model's
normalized loop, where model time is a fraction of a period and the export
poses any instant on its own. The Curta film of the curta-video campaign
(*Addition*, `23 + 145`) films a clocked machine: it has no loop, stands at
a bank of values, and moves only when asked, one request at a time, writing
its states at the events a request's path crosses (the framework's clocked
machines, export document version 8). Which states a stroke writes, and
where on the stroke, is the machine's answer, not something a film may
compute. The framework's simulation gives that answer through its public
surface: `Sim(model)`, `sim.move(input, to=|by=)` and `sim.trigger(name)`
return a `Request` (its two ends, the travel admitted, each event with the
fraction of the path and what it wrote, the stops), and `sim.snapshot()`
the bank. The orchestrator's contract (`docs/movie-document.md`, "The take")
puts the record in the movie document.

## Decision

A movie on a clocked machine declares a `Take` beside the model: the steps
(`Move(input, to=|by=, over=seconds)`, `Trigger(instruction)`) with the
seconds each is drawn over on screen, and `Mark(name)`s between them. The
take's time is declared, not computed: a move's `over`, an instruction's
declared duration. **What the machine does in that time is the framework's,
recorded once**: evaluation constructs the framework's simulation of the
declared model, makes the steps in order through its own requests, and
writes into the document's `take` block what it returned, verbatim, with
the bank before the first step and at every mark, and the identity of the
machine the export publishes. Nothing in the tool solves an event, chooses
a landing or invents a pose; a pose at any take time is the recorded bank
before the step with the input interpolated along the recorded path and the
recorded events up to that fraction written, which is the rule the viewer
draws an instruction by. A document is held to its record: both runtimes
replay the steps from the initial bank and refuse banks that differ.

Steps name the machine as the framework resolves it: an input by its
qualified id, which a step may write as the model's own `Driver`
declaration (resolved at class creation, so a misspelling fails at its
line) or as the id itself; an instruction by its key in the model's
`instructions` table, resolved at class creation for its duration. A
request the framework refuses, or stops before it moves, is refused with
the framework's words, naming the take and the step.

## Options considered

- **Compute the poses in the tool** from the export's published laws. Two
  implementations of the machine's events would then have to agree, and the
  film would show the tool's answer rather than the machine's.
- **Record the take with a framework command** and read its file. No second
  project asks for one; the public `Sim` already gives the record, and a
  command is a later step if one does.
- **Record at class creation.** Importing a movie would run the framework;
  evaluation is where a movie reads files and is already the one place that
  turns declarations into the document.
- **`Take` as a kind of `Loop`.** A take's marks are computed from its steps
  and its time ends rather than wraps; every check that a take is a posed
  loop would admit it. Both derive from one base instead.
- **Read the simulation's identity to compare with the export's.** The
  framework keeps it on a private attribute; the document check compares
  the recorded bank's ids with the export's drivers and states instead, and
  the viewer's restore, which takes the document's identity, is where a
  changed law with the same ids is caught.

## Consequences

- A movie document can carry a clocked take (`model.timeMode: "take"`, the
  `take` block), and Python checks one completely, the replay included. The
  commands read it from the `pose-a-take` change on; until then they refuse
  it.
- Evaluating a movie on a take imports the framework's simulation and
  constructs the model once (about 0.15 s for the fixture counter after the
  framework's import); it reads the model's own project files, and still no
  clock, randomness, network or CAD. A loop's evaluation is unchanged.
- The record is exact: both runtimes copy the framework's floats, so a
  replay compares them exactly, and a hand-edited document must copy them.
- An instruction declared on a part, rather than on the model's root, cannot
  be triggered yet; a move can name that part's driver by its qualified id.

## Amendment (1 October 2026, `take-identity`)

The option rejected above, reading the simulation's identity, is now the
decision. The framework publishes it (its `main` 096217f, the requirement
"A clocked simulation publishes its machine's identity"):
`Sim(model).identity` is the compiled clocked machine's identity, the string an
export of the same model carries as `clocked.identity`, whatever the bank
holds. Before this amendment the take block's `identity` was copied from
the export's manifest, so the document named the machine the export
carries, never the one that made the record; a model whose law changed
since its export, with the same drivers and states, was recorded without a
word (wart 9 of the Curta film *Addition*).

- **The take's identity is the simulation's**, read once after the
  simulation is constructed and found clocked, and compared with the
  export's `clocked.identity` **before the first step**. When they differ,
  evaluation is refused naming the take, the model as `module:Class` (the
  identity depends on the module the model is imported from as well as on
  its tree), the export, both identities and what to do: export the model
  again, or declare the model the export was made from. The comparison is
  made in evaluation, in the declaration's terms, before the steps of
  another machine can fail in words about a step; the document check keeps
  comparing a document's `take.identity` with its export's, as the
  contract's rule in both runtimes.
- **The bank's ids stop standing in for the identity.** The document
  check's rule that `take.initial` holds the drivers and states of the
  machine the export publishes stays in both runtimes, because it refuses
  what the identity cannot: a document whose identity is right and whose
  bank lacks a driver or state, or holds a name that is none (a damaged or
  hand-edited record, which the replay does not see, since it compares
  recorded banks key by key). Since the identity is checked before it, its
  words no longer say the take was recorded against another machine: they
  say a take's bank holds every driver and state of its machine and
  nothing else.
- The Node commands do not run the simulation: a document evaluated before
  this amendment from a changed model carries the export's identity and is
  caught by the viewer's `restore` at preview, as before; evaluating the
  movie again catches it at evaluation.
