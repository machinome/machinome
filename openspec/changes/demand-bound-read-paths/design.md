## Context

ADR-137 gives every demanded, determined law coordinate a motion path and permits a running Bound search to use that path instead of replaying its sub-program at each sample. `Program.deltas_of` currently demands coordinates used by downstream edges, but not coordinates consumed only by `Program.constraints`. On the frozen Curta `7586002`, the physical crank high Bound reads the retained anti-reversal pawl; that pawl is not otherwise demanded, so its path is absent and the Bound replays a four-edge prefix 65 times per ordinary tick. The low Bound already reads an actual path. A process-local union of Bound reads into propagation demand gave exact float-bit parity on all 2,600 ordered search levels of an ordinary 360° turn, an exact 213-coordinate final bank, and 59.11→27.87 CPU seconds for the turn.

## Goals / Non-Goals

**Goals:** Make a compiled Bound read a genuine path consumer; reuse the same `Motion` that the coordinate's determiner produces; keep every existing search fraction, arithmetic operator, error/refusal/rollback and bank float; obtain a material real-Curta cost reduction without project-specific knowledge.

**Non-Goals:** Inventing a path for Play or another untraced source, approximating an own-read law from endpoints, changing bound ownership, sampling, dt, tolerances, laws, program/document identity or viewer code.

## Decisions

1. Derive the propagation demand set from both existing downstream edge needs and the read IDs of already-compiled `Program.constraints`, mapping those names through the program's qualified bank keys. Compute that immutable set once after constraint compilation. `deltas_of` hands it to `Propagation`; no new public declaration, program edge, document field or state value is introduced.
2. Leave `trajectory.propagate`, `Run._searched_constraint`, and `_constraint_level` unchanged. A demanded law takes its existing `law_motion` route and publishes its actual `Motion`; a constraint uses it only when all required paths are determined. Play and any untraced descendant still have no such motion and keep the exact existing prefix replay. The Bound's own argument remains the tick-start bank value.
3. Require red-first tests showing an own-read law named only by a Bound is missing from the old demand set, then exactly one traced search-local path after the fix. Test unavailable-path replay, finite/NaN/signed-zero and error precedence through the existing framework corpus. Prove ordered level float bits, all bank values, ordinary and stopped Curta behavior, and CPU gain on frozen `7586002` before integration.

Alternatives: a Curta-specific pawl demand is not a framework fix; interpolating the pawl's net displacement changes its path; reducing 64 samples or weakening tolerances changes the stop contract. Re-running a new demanded prefix only when `_searched_constraint` notices the missing path would duplicate propagation and complicate event/refusal order, so the already-declared Bound consumer participates in the same normal demand pass.

## Risks / Trade-offs

- [A previously undemanded law path can evaluate additional points] → The change must preserve first errors and refusal rollback. Run the full relevant conformance corpus, explicit inactive-Bound/error fixtures, and originating Curta parity; revise the design if any new error appears.
- [More paths may be built for constraints not reached in a tick] → Demand only declared Bound reads, not arbitrary graph nodes, and measure both whole-turn CPU and small-framework controls. The Curta has 34 distinct Bound reads, 30 newly demanded, yet the net turn gain is substantial.
- [An unavailable path might be mistaken for a chord] → Preserve the `motions`/`untraced` check in the existing Bound search and test Play/prefix replay explicitly.

## Migration Plan

Private running-program optimization only. Existing snapshots and published documents retain their identities; reverting the implementation restores the old demand set.

## Open Questions

Whether broader fixtures expose an earlier error from constructing an otherwise unused demanded path. This is a gate for accepting the implementation, not permission to change refusal semantics.
