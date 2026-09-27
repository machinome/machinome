## Context

The mate rest placement contract (spec `mates`, ADR-147 and architecture's
mate synthesis) composes `P_owner · F_fixed · F_moving⁻¹` and emits one
ordinary rotation followed by translation. `_axis_angle` obtains its angle
with atan2, uses skew components up to 90 degrees, and beyond that square
roots every diagonal-derived axis square. For a principal -95.6-degree Z
matrix, diagonal subtraction leaves approximately 2.5e-17 in zero component
squares; taking square roots creates approximately 5e-9 false components.
These exceed the existing 1e-9 snap.

Curta's selector migration independently compares leaf physical bases. Root's
fresh unchanged-framework run at `6ca6061` with the saved selector candidate
reported two tests in 1.033 seconds: structural adoption passes, pose comparison
fails at `.bank.digit_selector_axle_6.selector_shaft_bottom`, with Z -127.775
versus -127.77499998947587. No fit failure is established. The matrix-only
witness requires no CAD or caller rewrite.

## Goals / Non-Goals

Goals: remove numerical phantom components; retain genuine small components,
signed rotations, stable half-turn recovery and existing symmetric outputs;
make the unchanged originating comparison pass at its existing tolerance.

Non-goals: author API or frame/coordinate changes, new snap thresholds,
loosening tests, repairing arbitrary non-rotation matrices, replacing all
rotation conversions across the framework, schema/viewer/Studio changes or
modifying caller-owned Curta files.

## Decisions

### Stabilize component recovery, not tolerances

Retain the well-conditioned atan2 angle computation and existing identity/snap
rules. Above 90 degrees, recover nondominant axis components without taking
square roots of their cancellation-prone diagonal residuals. The preferred
small change is to choose a well-conditioned dominant component from the
diagonal, take its square root, and recover the other components from symmetric
off-diagonal terms divided by that dominant component and the corresponding
rotation factor. Orient the recovered axis using skew when it determines the
sign. Keep normalization consistent with a unit axis.

This route preserves genuinely small components because their off-diagonal
terms carry linear information rather than squared magnitudes. Enlarging snap
would erase genuine geometry and change the contract; returning skew alone
would be ill-conditioned near half turns. A global quaternion conversion
rewrite is unnecessary for the localized witness.

### Exact half-turn symmetry is compatibility evidence

At an exact half turn, axis sign is equivalent and skew can vanish; retain a
deterministic dominant-positive convention in that case. Dominant-component
recovery can give mathematically equal components different last bits, whereas
existing diagonal recovery intentionally returns identical square roots for
symmetric axes such as `(0, 1, 1)`. The implementer must preserve that existing
symmetry, with a narrow exact-half-turn handling or equivalent stable recovery,
not casually replace it. The plan does not dictate a broad near-half-turn
branch threshold. Any handling must also preserve genuine small components;
it cannot simply restore square roots of noisy near-zero diagonal squares.

Tests must use independently generated proper rotation matrices and matrix
reconstruction/physical bases, not expect only one sign representation at a
half turn. Existing explicit symmetric serialization expectations remain.
Reconstruction comparisons account for the unchanged documented `1e-9`
axis-component and angle snap; they do not demand machine-epsilon equivalence
where that snap intentionally changes the emitted rotation.

### Keep scope and records proportional

The defect is internal numerical implementation of accepted whole-triad pose
semantics. No new ADR is expected; report a nonarchitectural disposition rather
than inventing a design decision. If the implementation changes a public
interface or snap/caller tolerance, stop and bring that change to the pilot.

## Risks / Trade-offs

- A patch may fix only Z or one sign → cover all three principal axes and both
  signs above 90 degrees, including the exact Curta matrix.
- A clamp may erase real small components → test oblique axes with small
  components above snap, positive and mixed signs, beyond 90 and near 180.
- Half-turn skew vanishes and axis sign is ambiguous → compare reconstructed
  matrices, deterministic outputs and existing equal-component fixtures.
- Private helper tests may miss emitted operation behavior → add public-mate
  rest-operation/physical-basis regressions and unchanged caller evidence.

## Migration Plan

After root planning review/commit, a separate Sol applies red-first in this
worktree. Run matrix-only tests first, then public mate tests and relevant
motion regressions. Root owns the CAD lane and Curta migration; coordinate any
caller rerun, do not edit caller tests or tolerances. Record exact tested
framework/caller content and distinguish numerical pose success from fit
claims. Root adversarial review precedes sync/archive and the implementation
record; later integration/cleanup authority does not authorize this proposer
to perform them. No author migration or publication is involved.

## Open Questions

No unresolved interface question. The exact-half-turn arithmetic choice is
implementation detail gated by the explicit compatibility and reconstruction
tests; return evidence if those constraints cannot be met by a narrow fix.
