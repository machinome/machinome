# ADR-143: Exact Booleans Preserve Their Reusable Inputs

**Status:** Accepted
**Date:** 2026-09-23
**Extends:** [ADR-073: The Comparison Kernel Is a Property of the Test Run](./ADR-073-the-comparison-kernel-is-a-property-of-the-test-run.md)
**Related to:** [ADR-142: A Shared-Interior Witness Refuses an Empty Exact Common](./ADR-142-a-shared-interior-witness-refuses-an-empty-exact-common.md)

## Context

Curta Type I's reverser-tooth survey repeatedly compared a fresh native tooth
against one posed native drum. OCCT's default destructive Common changed that
drum's vertex tolerances during earlier comparisons; the 40th comparison then
returned an invalid, grossly incorrect common. A fresh pose at the identical
shaft position returned a valid, tiny positive common. Framework exact tests
also retain native artifacts and placed shapes for repeated comparisons, so
avoiding reuse only in the project would not protect the framework's inputs.
The [archived change evidence](../../../openspec/changes/archive/2026-09-23-preserve-native-boolean-inputs/evidence.md)
records the reconstructed trial, source pins and controls.

## Decision

Framework-owned OCCT Common and Fuse receive private exact copies of both
operands, then run in their existing default mode. The Section used for
ADR-142's independent empty-common witness receives private copies too. The
input B-reps are caller-owned, potentially retained, and must not be amended
by these operations. Copies are local to one operation; they do not enter the
retained artifact or placement caches. A copy failure refuses the operation
with its named pair, rather than falling back to shared inputs. Argument
order, parallel choice, exact contact and failure policy remain unchanged.

## Alternatives

- OCCT `SetNonDestructive(True)` protected the reused Curta drum but made a
  distinct fresh-input Curta common at crank 169° invalid where the default
  mode returned a valid positive result. The output-mode regression persisted
  with parallelism off, so this mode is rejected.
- Disabling the project-local drum cache alone would avoid the observed
  sequence but leave framework-owned retained shapes vulnerable; the project
  used that fresh-pose workaround while this change was validated.
- Treating the invalid common as clearance, substituting a mesh volume, or
  adding fuzzy Boolean tolerance would change the exact verdict and is
  expressly rejected.

## Consequences

Repeated framework exact operations preserve the sampled topology counts,
vertex coordinates, and all vertex, edge and face tolerances of both inputs
in the Curta reproduction. All ten measured contact-boundary classifications
and shaft endpoints match fresh-input controls; the measured ten boundary
endpoint dictionaries, including small positive volumes, are bit-identical
to the fresh-input default-mode control. Copying the operands costs per-call
CPU and memory, but does not retain them. No universal cure for OCCT failures
is claimed. Any input already mutated in a running process must be freshly
loaded. The browser viewer's faceted kernel does not call these native OCCT
operations.
