# ADR-044: A binding name resolves into the shared DAG

**Status:** Proposed

**Date:** 2026-09-07

**Change:** `read-expression-bindings`

**Extends:**
- [ADR-043: Hash-consed expression evaluation](ADR-043-hash-consed-expression-evaluation.md)

**Amends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

**Depends on:**
- solid-node's ADR-080: A shared subexpression is named once — the
  document's bindings table (`openspec/changes/archive/2026-09-07-expression-bindings/`)

## Context

ADR-043 fixed the frame: a repeated subexpression is resolved once per
evaluation pass, whichever operation asks for it. It could not fix the
wire, because the redundancy was in the document — 31.6 MB of expression
text for one clock, about seven million written subexpressions over 263
distinct ones.

The producer has now fixed the wire. solid-node's ADR-080 publishes each
subexpression occurring more than once as one named entry in an ordered
top-level `bindings` array — `_b0`, `_b1`, … in table order, each naming
only `$t`, declared driver ids and entries before it — referenced by bare
name everywhere it occurred, and declares such a document `version: 4`.
The grasshopper clock's document falls from 31,638,555 bytes to 32,227,
its expression text from 31,611,478 bytes to 3,130, its longest expression
from 3.3 MB to 212 characters.

The bump is deliberately not additive: a consumer that ignored the table
would resolve `_b56` to nothing and place the machine in a wrong pose, so
it must refuse instead. That consumer is this viewer, and ADR-080 states
its three rules — bindings resolve before driver ids, dependence flows
transitively through a binding, every other name is unchanged — so that
this half could be written from them.

Two facts about the real document shaped the decision. Not one of its 116
operation expressions contains `$t` as text, yet 22 of them are
time-dependent, every one of them through the table: a consumer reading
dependencies off the expression string alone finds a document that is not
animated, builds no timeline, and never re-evaluates anything when time
changes. And substituting the table back reproduces the flat document
character for character — 116 of 116 expressions, 31,611,478 characters —
so the two documents are the same arithmetic, differently written.

## Decision

**A binding name is an ordinary name that resolves into the shared
hash-consed DAG, and the table that gives it meaning belongs to the
document and travels in the evaluation scope.**

- Each entry's expression is interned at load exactly as an operation's
  is, giving a root node id. An entry naming an earlier entry parses to a
  name node for that entry, so the table's dependency structure *is* the
  DAG's edge structure and no forward evaluation pass is needed: the DAG's
  own recursion is the order. Name resolution gains one step, `$t` →
  **binding** → driver map → math context, which puts a binding before a
  driver id exactly where ADR-080's rule puts it.
- Consequences that fall out rather than being built: an entry is
  evaluated only when something reads it; it is memoized per pass like any
  other node, so an entry read by fourteen operations costs one
  resolution per frame; and an entry interns into the same table the
  operations do, so the producer's table is the DAG the viewer would have
  hash-consed, handed over already built.
- The DAG store is page-scoped and binding names are document-scoped, so a
  module-global name-to-root map is refused: two documents mounted on one
  page, or one document republished, would overwrite each other's entries
  and render a wrong pose in silence. The map travels in `EvalScope`
  beside the driver values, and the document-level object that owns
  validation, the map and the dependency closure is per document.
- Two guards make that safe, and neither is optional. The pass comparison
  includes the binding map, because the name node for `_b3` is one node id
  for the whole page and two documents at equal time and drivers would
  otherwise share its memoized value. And the store carries a generation
  counter, because a reset — the last mount releasing, or the node ceiling
  tripping during a long republish session — hands ids out again from
  zero, which would leave a held map pointing at reallocated nodes; a
  table re-prepares its roots when the generation moved.
- **Dependence is closed transitively, at the document's table.**
  `freeVariables` keeps its exact meaning — which names an expression
  mentions, page-scoped and memoized per node — and a separate, per
  document closure answers which inputs it *reads*, replacing each binding
  name by what that entry transitively reads and leaving every other name
  alone. The closure is applied where each node's free set is already
  built, so the bounding rule, `animated`, `needsUpdate` and a flexible
  leaf's `free` are unchanged in wording and follow a binding in effect.
  What an expression reads therefore follows the table it is read through:
  a republish carrying a table whose entries read different inputs
  invalidates a node's closure even where the expression naming them is
  byte-identical, so a machine that becomes time-driven on a republish
  gains its timeline and one that stops being time-driven loses it. A name
  that is not an entry stays in the set, which is what turns a dangling
  reference into the existing undeclared-driver refusal.
- **A table the viewer cannot resolve is refused when the document is
  loaded**, beside the refusals already made there, naming the entry: a
  malformed array or entry, a duplicate name, an entry naming itself or a
  later entry, a name colliding with a declared driver id, a referenced
  name absent from both tables, and an entry whose expression carries a
  form the evaluation cannot support. Never a wrong pose, and never first
  met inside a frame. The table is read whenever it is present, whatever
  version the document declares, and a version-4 document with nothing in
  its table is not refused: the posture is to refuse what would be wrong,
  not what is merely unexpected.
- Accepted document versions become `[1, 2, 3, 4]`, and **the declared API
  version rises to 7**: reading a version-4 document is a capability a host
  may require, the same kind the version rose to 5 for when version-3
  flexible documents arrived.

## Alternatives considered

- **Evaluate the table top to bottom into a per-pass values map**, the
  literal reading of ADR-080's "one forward pass" sentence, consulted
  during name resolution. Rejected: it evaluates every entry on every pass
  whether or not anything reading it is being re-evaluated — a driver move
  that touches none of the grasshopper's 56 time-only entries would
  evaluate all of them, giving back the exact bound ADR-043 bought — and it
  allocates a map per pass, which is the per-call scope spread ADR-043 D5
  removed, one level up. It also forces evaluation eagerly, so a binding
  that throws throws while the scope is being built rather than where the
  flat expression would have, and it duplicates the pass detection outside
  the module that owns it. The sentence is a guarantee about the table's
  ordering, not an instruction about mechanism.
- **A module-global name-to-root map.** Rejected: binding names are
  document-scoped and the store is page-scoped, so two mounted documents
  would silently read each other's values.
- **Rewriting binding names to be document-unique at load.** Rejected: a
  text rewrite, which defeats the interning that lets two identical
  documents share nodes, for a problem the scope already solves.
- **Keying the DAG store per document.** Rejected: it throws away the
  page-scoped sharing ADR-043 established, to avoid two guards that are one
  comparison and one integer each.
- **Making `freeVariables` binding-aware.** Rejected: its per-node memo is
  page-scoped, so a binding-aware answer would be wrong for the next
  document to use the same name. The two questions — which names does this
  mention, which inputs does this read — are genuinely different and now
  have different answers.
- **Deriving the closure from the scope handed to `update`.** Rejected: it
  fails `animated`, which is read outside any update and decides whether a
  timeline exists at all — precisely the grasshopper clock's failure mode.
- **Refusing a `bindings` table on a document declaring version 2 or 3.**
  Rejected: honouring it renders the machine the producer described, and
  refusing would turn away a document that is renderable.

## Consequences

- A version-4 document mounts, poses and animates as the flat document it
  was published from does. Bit-identically: the two carry the same
  expressions, and the bound reading differs only by reusing a value
  already computed, so the caller check asserts `Object.is` rather than a
  tolerance.
- A document animated only through its table gets its timeline, which is
  every animated document the framework will now publish.
- The viewer gains one module, `bindings.ts`, and `expressions.ts` gains a
  resolution step, a comparison term and a generation counter. The
  bounding rule, `operationsMatrix`, `FlexibleShape.evaluate`, the mount
  options, the handle, the published names, the capture and the
  development server are untouched.
- The parity fixture now carries a `bindings` table and cases that name it,
  so the corpus pins the table's semantics as well as the functions'. Every
  case pinned before keeps its key, its expression and its expected value.
- The viewer now depends on the table's forward-only ordering for
  termination, and validates it at load rather than trusting it.
- The API version rises to 7. The `viewer` extra's version floor in the
  framework — the first published viewer that reads version 4 — remains the
  framework's to write once this package is released.
