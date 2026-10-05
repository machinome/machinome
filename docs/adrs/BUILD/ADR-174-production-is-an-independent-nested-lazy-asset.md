# ADR-174: Production Is an Independent Nested Lazy Asset

**Status:** Accepted
**Date:** 2026-10-04
**Change:** [production-layer](../../../openspec/changes/archive/2026-10-04-production-layer/)
**Related:** [ADR-175](../NODE/ADR-175-model-consumption-is-rest-only-and-generation-coherent.md)

## Context

Curta-Type-I-3x needs a production profile over its existing mechanistic
model: four printed crank units, seven sourced M4 nuts and fifteen made-wire
springs whose manufacturing assignment remains unknown. Two crank units are
simulation-fit replacements; the whole machine is not fabrication-approved.
Another profile must be able to describe the same model instance independently.

## Decision

Bundle dependency-light production modules in machinome, with an empty
production package root and defining-module imports. `Production[Model]`
binds an existing instance; nested profiles delegate reference-selected actual
subtrees. `Item` states a typed process, optional material and explicit mass
basis. Neutral Standard/Product records belong outside production.

BOM, stock, steps, mass, findings and export are independently lazy properties
or operations, not an `evaluate()` lifecycle. Manufactured grouping includes
canonical geometry, the complete recipe and direct finishing instructions;
sourced grouping uses explicit requirement and offer. Exclusive ownership
prevents nested double-counting. Missing, invalid and absent selections remain
diagnostic rows, and unknown mass remains in the full candidate denominator.

Instruction and measurement files retain their defining-module attribution.
Portable export pins inputs and geometry, refuses destructive destinations,
and publishes an atomic draft. Coverage completeness is not acceptance.

## Alternatives considered

- Model-owned current production would couple mechanical source to one
  workshop choice and prevent independent profiles over the same instance.
- Flattened declarations lose scoped child ownership and instructions.
- An explicit evaluate lifecycle introduces stale state and redundant calls.
- Class-name or provenance-based manufacturing inference invents a recipe
  where the Curta evidence explicitly leaves one unknown.

## Consequences

Profiles add no mandatory CAD kernel. Sourced BOM and structural diagnostics
avoid geometry, while manufactured BOM explicitly pays for it. Authors must
declare material, sourcing and mass evidence rather than receive guessed
defaults. Conservative boundaries expose reconciliation gaps instead of
claiming a complete build. Focused framework tests and the independent Curta
consumer prove the implemented contract; final regression evidence is kept
in the change record.
