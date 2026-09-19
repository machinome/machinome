## Context

Pilot ratification: on 2026-09-19 the pilot explicitly directed execution of
the presented design, companion viewer work, adversarial review, integration
to main, and resumption of the complex Vault. This is a standalone cycle from
framework main `b9b64ddaf0bc1d51d715d3d971b77b6ee58880bf`, on branch
`unilateral-running-pickup` in `machinome-framework/WTs/unilateral-running-pickup`,
integrating back to framework main. No push or publication is authorized.

ADR-121 integrates a self-read expression by choosing each dependent jump branch at the piece's left end and following the candidate path under that branch.  For the Vault law `dial * ((dial-held >= 3) + (dial-held <= -329))`, an engaged candidate moves `dial` and `held` together, so the relative level stays on its surface after a reversal and the existing rule intentionally remains engaged.  All existing self-read controls pass; changing their surface rule would silently redefine version-6 documents.

The required mechanism is the scalar **play operator** (also called backlash): for source `x`, retained follower `y`, and ordered offsets `low < high`, a monotonic source segment ends at

`y' = max(x' - high, min(y, x' - low))`.

The interval retains `y`; reaching a flank collects it; reversing immediately leaves it retained; crossing the interval collects it at the other flank.  This is the whole requested contact behavior and needs neither an epsilon nor a second state bank.

## Goals / Non-Goals

**Goals:**

- Give the Vault an explicit `Time.running()` declaration for one-dimensional clearance and unilateral flank contact.
- Preserve existing laws and serialized versions exactly unless a model opts in.
- Make admitted source paths, stops, snapshots, and publication deterministic and independently testable.
- Support the Vault's three-wheel cascade.

**Non-Goals:**

- A general collision/contact, force, friction, impact, or complementarity solver.
- Inferring contact semantics from existing comparisons or repairing strict gates with tolerances.
- Clocked state, host callbacks, hidden project mutation, or a second controller.
- Arbitrary sources that can reverse inside a tick, branching play graphs, or play laws with additional inputs.
- Implementing version 9 in `machinome-viewer`; that requires a separate repository cycle.

## Decisions

### 1. Add an explicit `Play` law marker

The public spelling is:

```python
from machinome.simulation import Play

(dial & wheel.turn).drives(
    wheel.turn,
    law=Play(low=-329.0, high=3.0),
)
```

`low` and `high` are finite offsets in the two coordinates' native common unit and MUST satisfy `low < high`.  The source group is exactly `(source & retained)`, the driven end is exactly that same retained coordinate, and all three resolved coordinates are scalar.  `Play` is a declaration consumed by relation realization and compilation, not a general `machinome.math` expression and not mutable runtime state.

This is preferred to changing ADR-121 because it is opt-in and says the hysteretic mechanism directly.  A `unilateral=True` flag on an arbitrary law was rejected because it leaves which terms and surfaces are contact flanks implicit.  A new graph primitive was rejected because ordinary graph evaluation is stateless and would give it a false meaning outside a run.  A new `plays()` relation verb was rejected because `drives` already states mechanical direction.

At `Sim` construction, the retained value MUST lie in the closed admissible interval `[source-high, source-low]`.  Otherwise construction refuses with the relation, values, and interval; it never teleports an invalid rest state.  Exact endpoints are valid contacts.

### 2. Admit only a monotone chain whose full path is known

A play source MUST be either a run-owned `Driver` or the driven coordinate of exactly one other play edge.  Play edges therefore form linear rooted chains; compilation refuses cycles, fan-in ambiguity, ordinary-law/wiring/formula sources, and multiple writers by their identities.  A driver request is affine and monotone within a tick, and projecting a monotone path through a play operator is monotone, so the restriction proves every admitted source segment has the endpoint semantics above.

Within the play-edge subgraph each coordinate has at most one outgoing play
edge; play fan-out is refused explicitly. Ordinary downstream observers do
not count as play branches. The Vault migration starts its first play edge
at the dial driver directly, while the cam remains an ordinary observer of
that driver; subsequent wheels form the play chain. The old callable prototype
is a regression control, not an acceptance fixture expected to change meaning.

This restriction is deliberate.  Applying the projection only to an arbitrary source's net increment is wrong when that source rises and falls within one tick.  A future project that needs such a source must bring evidence for partitioning its complete path; this change does not guess.

### 3. Evaluate and clip a chain from its originating input

The compiled program gains a dedicated play edge containing source id, retained/given id, and the two offsets.  Normal propagation applies the endpoint projection in program order.  A follower that stays inside its clearance reports a true zero increment; downstream ordinary edges read its committed increment normally.

Stop localization MUST replay the entire play prefix from the original driver at a candidate request fraction, then test the bounded follower.  It MUST NOT interpolate an immediate play source's net delta.  For example, two gaps of 10 driven `0 -> 100` produce `y=90`, `z=80`; a high stop `z=20` lands the input at `40`, not at the `1/3` suggested by interpolating `y`'s net 90.  On a stop, the originating input and every prefix coordinate commit at the located fraction atomically.  A bound on a follower that is released and stationary does not block the input.

Rejected ticks leave the bank, tick, crossing/stop records, and tree unchanged through the run's existing atomic envelope; commands that attempted travel retire `refused`, as they already do for every other running law. Snapshot, restore, and reset need no second state: the ordinary bank already contains every retained coordinate. Program identity includes edge kind and offsets, so an incompatible snapshot is refused.

Review clarification: preservation of existing refusal behavior controls the
earlier shorthand about atomic command state; no command outcome changes.
Cadence and split-path comparisons use the run's existing numeric agreement
contract, while a follower that remains retained keeps its exact held float.

### 4. Publish an explicit version-9 edge

A play edge is published as an ordinary program entry with `kind: "play"`, `needs: [source, retained]`, `gives: [retained]`, and finite numeric `low` and `high`.  No consumer is asked to infer play from an expression.  A document carrying one has minimum version 9; documents without one retain their current lowest version and bytes.  The running corpus gains single-edge and cascade cases, exact and non-integer flanks, reversal, split requests, stops, and snapshot replay.

The independent viewer currently declares versions 1 through 8.  Framework-side viewer guards will therefore refuse a version-9 document by name until a separately ratified viewer change implements the edge and passes the shared corpus.  The framework change is useful immediately through Python `Sim`, but it does not by itself restore browser operation for the Vault.

### 5. Proof starts with the originating failure

Tests first capture the unchanged Vault mesh-free path and independent oracle red.  Framework fixtures then cover finite ordered parameters, invalid rest, arbitrarily large/multiple-turn travel, exact endpoint reversal in both signs, measured non-integer offsets, one long versus split commands and cadences, the three-stage cascade, downstream reads, stops and release-side freedom, atomic refusal, snapshot/restore/reset, identity, version selection, and corpus coverage.  The existing 42 self-read tests and 62 subtests remain the regression control.

## Risks / Trade-offs

- **The source restriction excludes useful future mechanisms.** → Refuse them explicitly; expand only with a project demonstrating a complete path partition.
- **Naive stop interpolation is wrong through a cascade.** → Locate by replay from the originating driver and include the two-gap ranged-follower counterexample.
- **An invalid initial gap could be hidden by projection.** → Refuse construction instead of normalizing the bank.
- **Version 9 is not browser-operable today.** → Preserve the process boundary and require a separate viewer cycle before claiming parity.
- **The name “play” may be unfamiliar.** → Document it as backlash/clearance with the projection formula and a Vault example; do not introduce broader contact vocabulary.
- **Floating-point contact can tempt epsilon fixes.** → Use closed intervals and ordinary IEEE comparisons only; test exact and measured non-integer surfaces and keep genuine refusals atomic.
