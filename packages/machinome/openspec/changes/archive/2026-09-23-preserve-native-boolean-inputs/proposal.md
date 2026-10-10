## Why

An uncommitted Curta Type I station-1 reverser-tooth survey trial reused an unchanged posed native drum while refining a shaft boundary; the committed project baseline used fresh native poses. On the trial's 40th common, OCCT's default destructive mode had changed a cached drum vertex tolerance and returned an invalid common of bogus 1241.46 mm³ where a freshly posed drum yielded a valid 2.889e-12 mm³ common at the identical pose. Framework exact assertions also retain native placements, so this is not solely a project-tool cache issue. An initial `SetNonDestructive(True)` implementation protected the reused input but made a different fresh-input Curta common at crank 169° invalid where default OCCT remained valid. That mode is rejected for this change.

## What Changes

- Deep-copy each framework-owned native Common and Fuse operand privately before handing it to OCCT's existing default Boolean mode, protecting retained source and placed shapes while preserving the valid result mode and refusal policy.
- Give the section operation used for empty-common verification private copies too, so its bounded diagnostic cannot alter caller-owned inputs.
- Regress the original Curta 200-call failure sequence, the fresh-input 169° protected-mode regression, both shared Boolean operations, section input handling, ordinary tangent/disjoint/positive examples, and native error/refusal behavior. No mesh answer, healing, overlap epsilon, or output-validity waiver is introduced.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `exact-geometry`: exact operations preserve caller-owned native operands across repeated comparisons and compositions.

## Impact

Private `machinome/exact.py` operand isolation, exact-geometry tests/spec and project validation. No public knob or document version, viewer change, project source-shape change, sampling change, or geometry tolerance relaxation.
