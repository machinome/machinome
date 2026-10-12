# ADR-054: A constraint is derived from the published document, never published

**Status:** Accepted

**Amended by:** [ADR-069](ADR-069-moving-stops-attribute-push-at-first-contact.md):
the located contact bracket, not complete-request endpoints, identifies pushing
admissions. The derived document contract and static-read path are unchanged.

**Date:** 2026-09-14

**Change:** `execute-bounds-reading-other-coordinates`

**Extends:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Builds on:**
- [ADR-043: Hash-consed expression evaluation](ADR-043-hash-consed-expression-evaluation.md)

**Consumes:**
- solid-node ADR-113: A bound may read other coordinates

## Context

ADR-045 put the run in a worker and ADR-047 pinned it to the producer's
own corpus, and both rest on one sentence: the two runtimes are ONE
algorithm, written twice. A declared bound was, until now, a number or an
expression over the bounded coordinate's own id — evaluated once per step
from the committed bank, compared at the ends of a stretch, solved or
searched, and snapped to.

solid-node's ADR-113 widened that. A bound may now READ OTHER
COORDINATES, and reading them gives it a running meaning it did not have:
a CONSTRAINT between the bounded coordinate and what it reads, which can
be violated INSIDE a step and satisfied again at its end — the plug that
turns while the pins align in the same tick, the key that withdraws while
the plug returns. A test at the ends alone commits all of them.

The pin tumbler lock is the originating project and the reason this
cycle exists. Its published document was refused by name on load:

```text
the bound declared on "plug.key.insert" names "plug.turn", which it may
not read.
```

That refusal was correct — a consumer that cannot execute what it was
given must say so — and it was the last thing between a lock that
actually locks and a browser.

Two facts of that document shaped this decision. Its `plug.turn` bounds
are `(((((90.0 * _b10) * _b13) * _b16) * _b19) * _b22)`: every read
reached through the document's BINDINGS table, none of them a free name
of the text itself, and the expression never names `plug.turn` at all.
Its `plug.key.insert` low bound is `(-60.0 - (-60.0 * (abs(plug.turn) >
0)))`, which reads one coordinate directly.

## Decision

**A constraint is DERIVED when the document is loaded, and the producer
publishes nothing new for it.** `loadProgram` builds a table keyed
`` `${identifier}:${side}` ``, each entry carrying the bound's
expression, its READS, its SUB-PROGRAM and its CANDIDATES:

- the **reads** are the expression's free names CLOSED OVER the
  document's bindings table, minus the bounded coordinate's own id,
  sorted;
- the **sub-program** is the published edges determining the bounded
  coordinate and every read, and everything those need, in the
  document's own edge order, a check edge never among them;
- the **candidates** are the sorted union of the published
  reaching-input table over the bounded coordinate and every read.

Each of the three is a projection of what the document already carries.
The framework decided (ADR-110) that a projection with no decision in it
is not published, and a viewer that asked for one would be asking for a
document change the producer has already refused — and would let the two
runtimes disagree about a derivation neither of them decides.

**The reads are the CLOSURE, not the raw free names.** This is the
load-bearing half of the decision. The lock's plug bound's raw free names
contain no coordinate at all. A viewer deriving reads from
`freeVariables` alone would find none, take the static-reads shortcut on
every tick, evaluate the bound from five standing lifts and run a lock
that turns while its pins move — silently, and only for documents that
share a subexpression. Because the own id may be absent, the test is
CONTAINMENT and never equality.

**The worker executes such a bound as ADR-113 does, function for
function.** The bounded coordinate inside the expression takes the value
it holds in the STEP's committed bank — never the staged value, which is
what makes a ratchet's tooth the tooth it started the step on. Every read
takes the value it has along the stretch's path, computed by one pass
over the bound's sub-program with every admission scaled by the fraction,
on a FRESH delta map, using the same per-edge arithmetic the segment is
later committed by. A stretch in which nothing the bound depends on moves
evaluates nothing; one in which no READ moves evaluates the bound ONCE
and dispatches into the existing numeric stop path unchanged. Otherwise
the level is sampled at the published subdivisions, bracketed against the
previous sample and bisected to the published crossing tolerance, and the
fraction taken is the INSIDE end. There is no snap: the segment committed
at that fraction satisfies the bound by the same arithmetic that located
it, and the run asserts that it does — in a SECOND loop over the event,
after every entry's group and record, because a numeric snap on another
entry of the same event mutates the committed state the assertion must
see.

**Everything else about a bound is refused by name, at load.** The span
check admits the bounded coordinate's own id and the program's bank
coordinates. An intermediate, the clock, a branch placeholder or an
unknown name is refused with the offending name, what such a bound may
read, the expression quoted and the document named — and a name the
document publishes as a COMPUTED VALUE is told so, because such a bound
must name the joint the port follows.

**The corpus is what holds the two runtimes together here too.** The
committed corpus is the producer's regenerated one — 14 scenarios, 12
machines, 276 steps, the new `Captured` machine — and the suite's width
guard requires both new features the producer's generator requires, the
first computed through the corpus's own bindings table.

## Consequences

- A document whose bound reads other coordinates loads, runs, and agrees
  with the framework step for step. The pin tumbler lock's own published
  build mounts in a page and shows the mechanism: the plug turns its
  whole 90° with the key seated, the key is captured while the plug
  stands turned, and the plug will not turn with the key withdrawn.

- **A bound over the bounded coordinate alone is untouched**: same
  meaning, same code path, same cost. The Pascaline acceptance is
  unchanged to the digit, and `Train` — which declares no such bound —
  measures what it always measured.

- **A constraint that samples is expensive, and one that is quiet is
  not.** Measured here on the bench: the lock idle **18,310 steps/s**
  (0.055 ms), the lock turning its seated plug **≈3,400 steps/s**, the
  lock advancing its key **144 steps/s (6.9 ms)** — the worst case, where
  three bounds sample over a seven-edge sub-program at 64 subdivisions.
  The framework measured 45 ms for the same tick on CPython, so the
  hash-consed DAG is about seven times cheaper; it is still **above the
  4.2 ms a step costs at the default `1/240` s step size**, so the lock
  does not advance its key at real time in a browser. That is recorded
  as a finding, not mended by a coarser step or a skipped sample. The
  framework's own recorded follow-ups — `f(start)` once per stretch per
  edge, and one sampling for the two sides of one coordinate — are where
  it is bought back, in both runtimes together.

- **A wrong closure would fail silently**, which is the worst shape a bug
  can have here. It is guarded three ways: the derived table is asserted
  directly against the lock fixture; the corpus's `Captured` machine
  carries no bindings at all and is not relied on to catch it; and a
  hand-written document whose bound reaches its read only through a
  binding is a test of its own.

- **Nothing public moves.** `documentVersions` stays `[1, 2, 3, 4, 5]`,
  the shape of a span is unchanged, and the declared widget API version
  stays at 12. The refusal surface widens by exactly one class of name —
  a bank coordinate — so a producer bug in which a span names the wrong
  coordinate is now quieter, and no consumer could ever have seen that.
