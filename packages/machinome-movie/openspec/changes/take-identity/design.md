## Context

A clocked take is recorded once by evaluation (ADR-011):
`python/machinome_movie/evaluate.py` (`_record`) constructs the framework's
`Sim` over the declared model, makes each step with its own requests, and
writes the `take` block from what it returned. The block's `identity` was
copied from the export manifest's `clocked.identity`, because the framework
kept the simulation's identity on a private attribute; ADR-011 records
"read the simulation's identity" as an option it could not take. So the
document's identity said which machine the export carries, never which
machine made the record, and evaluation then checked the document it had
just written with `check_document`, whose take rules are the contract's
(`docs/movie-document.md`, "The take") and are mirrored word for word in
`src/movie.mjs` (`checkTake`):

1. `take.identity` equals the manifest's `clocked.identity` (trivially
   true for a document evaluation wrote, since it copied it);
2. each step's `input` is a driver the export declares;
3. `take.initial` holds exactly the export's drivers and states: refused
   "take.initial lacks 'x', a driver or state the export declares; the take
   was recorded against another machine", or "holds 'x', which is not a
   driver or state of the export; the take was recorded against another
   machine";
4. the banks at the marks equal the replay of the steps from `initial`.

Rule 3 is what stood in for the identity at evaluation (`declare-a-take`,
evidence finding 2): a model whose drivers or states changed since its
export failed it, and a model whose law changed with the same ids passed
everything, its document carrying the export's identity.

The framework's `main` 096217f publishes `Sim(model).identity`: the
compiled clocked machine's identity, the string every producer publishes
as `clocked.identity` for the same model, independent of the bank;
reading it on a `Sim` that is not clocked raises a `TypeError` naming
`identity`. A probe on the fixture project (evidence) confirms it equals
the counter export's identity, and that a copy of the project whose
counter changed its commit law, or renamed its state `tens`, reports
another.

## Goals / Non-Goals

Goals: the take's identity is the identity of the machine that made the
record; a take over a machine the export does not carry is refused at
evaluation, naming both identities and what to do; the stand-in stops
standing in. Non-goals: those of the proposal.

## Decisions

### D1. Evaluation reads the identity from the simulation and compares it before the first step

`_record` reads `sim.identity` once, after the simulation is constructed
and found clocked, and before any step is made. When it differs from the
manifest's `clocked.identity`, evaluation is refused:

> Take Turns: the model models.counter:Counter is not the machine the
> export ../../export/counter publishes: the framework's simulation of the
> model has the identity `<sim>`, and the export's clocked.identity is
> `<export>`; the model changed since it was exported, or the take
> declares another model than the export was made from: export the model
> again, or declare the model the export was made from.

The model is named as a project's models table names it, `module:Class`,
because the identity depends on the model's module as well as its tree
(evidence: the same file imported under another module name reports
another identity), so the module is part of what the reader must check.
The export is named as the movie's other refusals name it, relative to the
movie's directory. The take block's `identity` is then `sim.identity`,
which equals the export's; the written document is byte-identical to what
it was for a matching export.

The comparison is in `_record`, not left to `check_document`: the document
check compares the document with the manifest, and a document whose
identity was read from the simulation would be refused there in the
document's words (`take.identity`), which tell a reader of a movie nothing
about the model they declared. Evaluation refuses in the declaration's
terms first; the document check stays the contract's.

Rejected: comparing after the steps are made (the steps of another
machine can fail first, in words about a step, hiding the cause);
refusing in `check_document` only (above); a tolerance or a fallback to
the manifest's identity when the simulation's is unreadable (the
simulation is clocked by the time the identity is read, so it is always
readable; and a step is not a protocol).

### D2. The bank-ids rule stays as the contract's completeness rule, in new words

After D1, rule 3 can no longer fail at evaluation for a sound export: the
simulation that recorded `initial` has the export's identity, so the same
drivers and states. It still refuses something the identity does not: a
document whose `take.identity` is the export's but whose `initial` lacks
a driver or state of that machine, or holds a name that is none of them,
a damaged or hand-edited document, which the contract forbids ("`initial`
is the bank before the first step: every driver and state of the machine
by qualified id") and which would otherwise reach the viewer's `restore`
as an incomplete bank. Rules 1 and 4 cannot see it: the identity is
right, and a replay from an incomplete bank is compared with recorded
banks key by key, so a name missing from both passes. The rule therefore
stays in both runtimes, as the contract's, and its words change: since
rule 1 runs first, "recorded against another machine" is never the cause
when it fires. New words, the same in both runtimes:

> take.initial lacks 'tens', a driver or state of the machine the export
> publishes; a take's bank holds every driver and state of its machine and
> nothing else

> take.initial holds 'time', which is not a driver or state of the machine
> the export publishes; a take's bank holds every driver and state of its
> machine and nothing else

Rule 3 had no Node test; a changed refusal gets its invalid fixture
(`AGENTS.md`, "Which layers a change touches"), so
`fixtures/invalid/take-initial-incomplete.json`, the evaluated count
document with `tens` removed from `take.initial`, must mention
`take.initial`, `tens` and `every driver and state`, and both suites refuse
it.

Rejected: removing rule 3 (it refuses the incomplete bank above, which
nothing else does before the viewer); keeping its words (they name a cause
rule 1 has excluded); moving it into evaluation only (Node reads documents
evaluation did not write).

### D3. The stale export is a real one

`test_an_export_older_than_the_model` faked a stale export by deleting
`states.tens` from a copied manifest and leaving its `clocked.identity`
alone: an export whose lists disagree with its own identity, which no
framework writes. It goes. Its place is taken by a copy of the fixture
project (export included) whose `models/counter.py` changed after the
export was made, evaluated by the command line (`python -m machinome_movie
evaluate <copy> count`) so that the copy's model is imported under its
project name, as a project's would be: once with the commit law advancing
by two (same drivers and states: recorded without a word before this
change) and once with the state `tens` renamed `decades` (refused about
`take.initial` before this change). Both are refused naming `Take Turns`,
`models.counter:Counter`, the export, the export's identity, the copy's
identity (read from the framework in the copy) and `export the model
again`. The fixture project itself does not change, so no export, document
or resolved pin is re-pinned.

## Risks / Trade-offs

- The identity depends on the model's module name (evidence). A take whose
  module imports the model under another name than the one the export used
  is refused as another machine; the refusal names the module so the
  reader can see it. That is the framework's definition, not this
  change's; recorded as a finding.
- The Node commands still do not run the simulation: a document evaluated
  before this change against a changed model carries the export's identity
  and passes `check`; the viewer's `restore` at preview is still where it
  is caught. Evaluating the movie again catches it now.
