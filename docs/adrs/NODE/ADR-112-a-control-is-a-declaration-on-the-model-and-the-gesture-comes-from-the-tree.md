# ADR-112: A Control Is a Declaration on the Model, and the Gesture's Geometry Comes from the Tree

**Status:** Accepted
**Date:** 2026-09-14
**Depends on:**
- [ADR-105: The run owns the coordinates and binds them](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md)
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md)
**Cites:**
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
- solid-node-viewer ADR-048, *Running controls submit requests; nothing binds back*
**OpenSpec change:** `declare-controls-on-parts`

## Context and Problem Statement

A running machine (ADR-105) is driven from a panel beside the model: one
button per declared instruction, a nudge pair and a jog pair per
declared input. The viewer's ADR-048 ratified that chrome and closed with
a promise — *"the next viewer cycle binds a pick to a declared input
through this same command interface"* — and the 2026-09-12 ratification
in `workflow/open-run-simulation/design.md` had already named the third
thing a control can be: "clicking a button, holding a jog control or
**dragging a part**". The Pascaline module made the promise concrete:
click the dial, and the dial advances.

The question this ADR answers is *where the binding between a part and
a request lives*, and what the framework derives once it is stated.

A viewer cannot infer the binding from the published document, and the
module's own `viewer.json` is the proof:

- `program.sources['tens.input.turn']` is `['tens_entry', 'units_entry']`
  — the carry from the column below moves the tens dial too. Nothing in
  the document says which of the two a hand on the tens dial means.
- `units.drum.turn` is in the bank and the number drum turns with it,
  but a hand does not turn the drum: it sits under the lid, and the
  ratchet is on the input arbor. A viewer that made every posed part
  draggable would let a maker do what the machine forbids.

What the document *does* carry is the gesture's geometry: `units.input`
is posed by `['r', 'units.input.turn', [1, 0, 0]]` and `units.input.dial`
is a leaf under it, so the joint, its axis and the point it turns about
are already in the tree.

## Decision Drivers

- The pilot's model: an **input** exposes a coordinate; an
  **instruction** is a named, reusable request; a **control** is how a
  person issues one. A control references an instruction and never
  repeats its definition, and authors "do not maintain two matching
  lists just to make named actions usable".
- Nothing binds back. A control moves nothing itself; ownership,
  admission, stops and outcomes stay exactly what `trigger`, `move` and
  `rate` state.
- A number stated twice is a number that drifts: the ratio between a
  dial's degrees and its input's digits is a relation the compiled
  program already holds.
- The program identity, the conformance corpus (ADR-111) and every
  document published today must not move.
- Every mistake is refused with the facts, as early as the facts exist.

## Considered Options

1. **Infer the binding in the viewer** from the reaching table and the
   posed tree. Rejected: ambiguous exactly where it matters, and it
   makes untouchable parts touchable.
2. **Declare the binding in the model, and declare the ratio too**
   (`per_turn=`). Rejected: the author restates a relation the program
   holds, and the two can disagree silently.
3. **Declare the binding in the model; derive the geometry from the
   tree and measure the ratio from the compiled program.** Chosen.
4. **Publish the table under a new document version 6.** Rejected for
   now by the document's own version ladder: `bindings` and `program`
   force a version because a consumer that ignored them would pose the
   machine wrongly; `loop` and `instructions` were additive because a
   consumer that ignored them still rendered the truth. `controls` is
   of the second kind. The viewer's API version is the capability gate.

## Decision

**A control is a declaration on the model, published beside the
instructions; the framework derives the gesture's geometry from the tree
and measures its ratio from the compiled program.**

1. An assembly declares `controls`, a mapping of display name to
   control, beside `instructions`. `Button(part, instruction)` is a
   press on `part` submitting the named instruction. `Turn(part, input)`
   is a drag on `part`, about the rotational coordinate the part rides,
   issued as relative moves on `input`. Both name a **node**, written the
   way a relation's path ends are (`units.input.dial`), and both qualify
   through the declaring node's instance path exactly as instructions
   do, so a button's instruction reference equals a key of the
   instruction table by construction. `Turn`'s input is the `Driver`
   declaration itself, never a qualified-id string, so a driver keeps
   one address.
2. The control's coordinate is the one owned by the nearest
   ancestor-or-self of the part that declares a joint the run banks.
   This release names one: a posing node with several joints, or a joint
   owning several coordinates, is refused, and under that narrowing the
   coordinate is always bare in its joint's own operation, so nothing is
   ever parsed out of a published expression.
3. `axis` and `origin` are the values the joint's own placement used, in
   the joint node's frame — the site carry applied — so a consumer
   computes the world line from one node's world matrix with no case
   analysis. `origin` exists because `Revolute(at=...)` turns about a
   line that does not pass through the node's placed origin.
4. `per_unit`, the coordinate units per input design unit, is
   **measured**: the compiled program is propagated once from the rest
   bank with the input displaced by a power-of-two amount in each
   direction and nothing else moved. Both readings zero is refused (the
   part does not move with that input at rest); readings disagreeing
   beyond a relative window of its own, wider than the program's tick
   agreement, are refused (a kink, a jump or a one-way law at rest). The
   published number is the forward reading, taken at rest, and the spec
   says so: a curved law makes a pointer lead or lag the part and never
   moves it wrongly, because the part is posed only by what the run
   commits. The measurement is pure arithmetic over the program — the
   tick's own `values_of` and `deltas_of`, now on `Program` and delegated
   to by `Run` — because publication must not construct a `Sim` over a
   tree a live run owns.
5. Refusals fire where the facts exist: at class definition (a part the
   declaring class does not hold, a coordinate or driver written where a
   part belongs, a repeated child, an input of another class, a
   `controls` attribute that is not a table — the name is reserved on a
   node class); at compile (an undeclared instruction, a part nothing
   run-owned poses, several joints or coordinates, a `Turn` over a
   non-rotational coordinate, an input that does not reach the
   coordinate, naming the inputs that do); at publication (zero or
   disagreeing ratio). A control under a root without `Time.running()`
   is refused at simulation construction and at publication.
6. A version 5 document whose tree declares a control carries a
   top-level `controls` table beside `instructions`, keyed and ordered
   by qualified name: `kind`, `part` and `joint` as node-name paths,
   `instruction` or `input` with `per_unit`, `coordinate`, `axis`,
   `origin`. It is additive: the version does not move, the key is
   absent when the table is empty, it carries no expression and never
   enters the `bindings` pass, and `Program.described()` — hence
   `identity` and the corpus — never learns a control exists. The
   build's `viewer.json` and the export's `manifest.json` publish it; the
   headless browser-snapshot capture does not, because it bakes one
   instant and publishes an empty instruction table for the same reason.
   A part this render omitted drops its control rather than refusing the
   build.

## Consequences

- An author states the binding once, in the tree's vocabulary, and
  nothing else: no second list, no ratio, no axis. On the Pascaline
  module the six entries are three `Button`s on existing instructions
  and three `Turn`s, each dial measuring `-36.0` degrees per digit.
- Every document published before this decision is byte-identical after
  it; the program identity of the Pascaline module's own build is
  unchanged with or without its controls declared.
- What a viewer does with the table — hover affordance, pick, drag plane,
  quantum, blocked-travel reporting — is the viewer's own cycle,
  reading exactly this shape.
- `controls` is a reserved class-body name on node classes. No project
  in the workspace used it.
- Two compatible extensions are recorded rather than taken: a control on
  a composed joint or a `Free` (choosing one coordinate), and `Slide`
  for a prismatic drag. A `Button` on a part nothing poses is likewise a
  later, additive relaxation.
- The ratio is a reading at rest. A machine whose dial ratio changes
  with state gets a looser drag, not a wrong one.
