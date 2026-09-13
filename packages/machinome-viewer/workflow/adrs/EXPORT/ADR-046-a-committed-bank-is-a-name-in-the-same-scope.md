# ADR-046: A committed bank is a name in the same scope as a driver

**Status:** Accepted

**Date:** 2026-09-13

**Change:** `run-in-the-worker`

**Extends:**
- [ADR-043: Hash-consed expression evaluation](ADR-043-hash-consed-expression-evaluation.md)
- [ADR-044: A binding name resolves into the shared DAG](ADR-044-a-binding-name-resolves-into-the-shared-dag.md)

## Context

A version 5 document's tree is posed by its **coordinates**: a joint's
placement names `units.drum.turn`, and a flexible leaf's `params` name
bank ids too. The run commits one bank per tick, and something has to
turn that bank into matrices.

The viewer already has an evaluator that does exactly this for drivers —
a page-scoped hash-consed DAG, memoized by a pass stamp, with a bounded
re-evaluation that walks only the nodes whose free variables moved. The
question was whether a bank is a second kind of thing.

Two facts decided it. First, `ChangeSet.drivers` already means "the
qualified ids whose values moved this frame", and a coordinate id is a
qualified id. Second, and less comfortably: the shipped scope builder
split a qualified id at its **first dot only**, so `units.drum.turn`
reached the evaluator as `{units: {'drum.turn': 7}}` and resolved to
`undefined`. Measured against the shipped modules,
`evalExpr('(-1 * units.drum.turn)', {time: 0, drivers: store.scope()})`
was `NaN`. Every coordinate id is three segments or more, so the run
could not pose a single part without fixing it — and the same bug has
been silently breaking a three-segment **driver** id in every document
version since drivers existed.

## Decision

**The bank poses the geometry through the evaluator the widget already
has**, by widening the evaluation scope rather than adding a second pose
path. Per rendered frame the scope is the committed bank and the
program's clock name, nested as driver values are, with the document's
own bindings table beside them; the tree's bounded update takes the
frame's `moved` ids as its change set. No second pose path and no second
table of poses exists, and `flexible.ts` needs no change at all.

**A qualified id nests at EVERY segment.** `nest(flat)` builds
`{units: {drum: {turn: v}}}` for as many segments as the id has, and is
used by the engine's scopes and by `DriverStore.scope()` alike. It
changes no correct pose: it changes a `NaN` into the number the producer
meant.

**An id set that cannot be nested is refused at load**, naming both ids —
`a.b` holding a value beside `a.b.c` holding one would have to make a
number an object. Nothing the framework publishes produces that shape
today; the refusal is what keeps it loud if it ever does.

**The program's clock name is a bank-shaped name, not `$t`.** Under a run
it binds to elapsed simulation seconds, which never wrap; with no run — a
still capture, a thumbnail — it binds to zero, the instant the rest pose
is defined at. `$t` stays 0 for a version 5 document, because no
expression in one reads it.

**Every evaluation gets a fresh scope object.** `expressions.ts` takes an
identity fast path — a scope object it has already seen is assumed to
hold the same values — so an engine that reused one object and mutated it
between evaluations would read the *previous* evaluation's memoized
numbers, silently and everywhere. The engine keeps the rule by having
exactly one call site (`evaluateExpression`) rather than by discipline at
many.

**The program's held node ids are generation-guarded.** The loaded
program holds one interned id per published expression and re-prepares
from the expression strings it keeps when `expressionGeneration()` has
moved, exactly as `bindings.ts` does — otherwise a long `solid develop`
session that republished past the node ceiling would integrate a machine
out of another document's nodes.

## Alternatives weighed

- **Look the whole dotted name up in a flat map inside `resolveName`,
  before the member chain.** It fixes the same bug more simply and would
  let the scope be flat — but it changes a name-resolution rule that is
  ratified for every document version and pinned by the parity fixture,
  and it changes the pass comparison for every document on the page, to
  avoid a refusal for a shape nothing emits.
- **Disable the evaluator's identity fast path.** It is what makes one
  `tree.update` walk cost one pass rather than one per operation, on
  every document version.

## Consequences

- A machine whose carry is idle re-evaluates only the nodes the moving
  drum reaches, exactly as a slider on one axis already did.
- A three-segment driver id in a version 2 to 4 document now resolves;
  nothing that resolved before resolves differently.
- `sign` resolves by the producer's own `(x > 0) − (x < 0)` rather than
  `Math.sign`, which differs from it at negative zero. The run reads a
  `sign` branch off the same formula, so one definition serves both.
- The bindings table of a version 5 document carries entries only a jump
  plan can evaluate (`_b33 = (360.0 * _j0)`). This viewer has never
  evaluated the table forward, so they cost it nothing; a placeholder
  reached from an **operation** is still refused, because no scope binds
  it there.
