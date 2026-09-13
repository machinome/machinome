# ADR-047: The corpus is what makes the two runtimes one algorithm

**Status:** Accepted

**Date:** 2026-09-13

**Change:** `run-in-the-worker`

**Beside:**
- ADR-022 (solid-node): one `$t` semantics reimplemented in several
  runtimes, and the producer-generated parity fixture that pins it

**Depends on:**
- solid-node's ADR-111: the running corpus
  (`openspec/changes/archive/2026-09-13-publish-the-mechanical-program/`)

## Context

The run is ADR-022's problem one layer up. A published program is
executed by the framework's own run **and**, from this change, by a
TypeScript engine in a browser, and nothing but a corpus can say they
agree. The tick is not a formula that can be inspected side by side: it
is admissions, a propagation order, a partition of a path at every jump
surface, a localization by division or by bisection, a group of blocked
inputs, and an atomic commit — and every one of those has a float in it.

solid-node's ADR-111 wrote `tests/running-corpus.json` from the
framework's own run. Every expected value in it is a value that run
**produced**, never one recomputed a second way, which is what makes a
disagreement mean the other runtime drifted.

## Decision

**The framework's corpus is committed here byte for byte** as
`src/running-corpus.json` — the same arrangement the expression parity
fixture already has, and for the same reason: the numbers in it are the
framework's, not ours. It is never regenerated in this repository.

**A vitest suite replays every scenario through the shipped engine,
in-thread**, tick by tick: build the engine from the fixture's own copy
of the published document at the fixture's step size, apply each scripted
command before the step it names in the order the corpus lists them,
integrate one tick, and compare.

**Agreement is EXACT for discrete state** — the tick number, every status
word, every coordinate, relation, primitive, bound side and input name,
every crossing level, and the ORDER of every list — **and within the
corpus's own stated relative tolerance for floats**, which is the run's
published agreement window, read from the fixture rather than from a
constant of ours. Every tick the corpus lists is compared; a sampled
comparison is not accepted.

**A divergence is a bug in this viewer.** Not a tolerance to widen, not a
scenario to skip, not a fixture to edit.

**The generator's own coverage list is mirrored here** over the committed
fixture — the discontinuous primitives, a multi-source law, a stop
located inside a step, a bound stated as an expression, a command retired
blocked, a rate, a state taken and restored, both instruction forms, and
a step carrying both a crossing and a stop — so a narrower corpus copied
in from a future framework is loud here without anyone running the
generator.

**The engine is what is replayed, not the worker.** The worker is a
transport and the engine is the algorithm; the worker gets its own small
test against a fake port, and the in-thread path the corpus exercises 260
times is the same module the worker runs.

## Consequences

- Thirteen scenarios over eleven machines, 260 ticks, all passing under
  the corpus's own `1e-9` relative window.
- The corpus is a guard on the features the producer **stated**, not on
  every float path this engine contains. Three paths are reached by no
  scenario in the committed fixture — a `wiring`'s factor and a
  `formula`'s accumulation (every edge in it is a `law`), a searched jump
  crossing (every published jump in it is affine), and both non-linear
  stop localizations — and each is covered instead by this package's own
  unit tests. That gap is recorded in the change's evidence as a finding
  for the producer rather than papered over here.
- The acceptance document — the Pascaline module's own published build —
  is run as a fourteenth scenario the corpus does not contain, in node
  and in a real browser.
