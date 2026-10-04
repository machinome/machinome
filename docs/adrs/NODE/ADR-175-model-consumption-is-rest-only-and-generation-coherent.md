# ADR-175: Model Consumption Is Rest-Only and Generation-Coherent

**Status:** Accepted
**Date:** 2026-10-04
**Change:** [production-layer](../../../openspec/changes/archive/2026-10-04-production-layer/)
**Related:** [ADR-174](../BUILD/ADR-174-production-is-an-independent-nested-lazy-asset.md),
[ADR-066](ADR-066-render-at-rest-simulate-per-instant.md)

## Context

Curta-Type-I-3x creates legacy child instances in constructors and binds a
running simulation to the same model used by production. Consumers need its
actual inherited replacements, parameters and occurrences without preparing
an alternate tree or disturbing driver banks, time or operations. Structural
reports and later artifact copies must describe one coherent input generation.

## Decision

Expose `ModelSnapshot`, `Reference`, `Occurrence` and `GeometryFacts` through
`machinome.model`. The facade adapts core-owned validated rest-only child
enumeration, preserving actual child identities and root-relative scope.
Assemblies, rigid pieces, flexible pieces and fusion features remain distinct;
markings and frames are not production items. Duplicate paths or instances and
malformed render results are refused deterministically.

Structural reads never invoke simulation, preparation, assemble or presentation.
Known stateful legacy rendering is refused before execution. Fresh render reads
of runtime drivers, time or ports are refused; failure cleanup is limited to
framework-owned structural state, not arbitrary user-state rollback.

The snapshot captures source closure and consumed artifact hashes plus stat
facts. Changes invalidate the entire shared generation, including held child
bindings. Facts and copied bytes use the same pinned artifact. Direct model
bindings report unverified-direct-binding provenance; sealed loader generations
can report verified-source-generation. Neither claim establishes fabrication
acceptance.

The facade permits selected native materialization only when geometry or a copy
is requested. Production imports this public seam rather than private core.
Vet classifies ModelSnapshot and the production writer as effectful while
allowing pure Reference and recipe records in pure model closures.

## Alternatives considered

- Private-core traversal would make an independent asset depend on internals.
- Simulate/save/restore cannot safely restore arbitrary user mutation and would
  disturb the real running bank before discovering unsupported rendering.
- Reconstructing default children would miss actual constructor parameters,
  inherited replacements and the bound instance's identity.

## Consequences

Consumers receive conservative immutable facts, not mutable node handles.
Stateful legacy models need a rest-only contract before structural consumption;
the facade does not pretend to support them through generic rollback. Source
and artifact races require a fresh binding, preventing mixed-generation draft
bundles. Focused tests cover advanced simulation preservation, active topology,
artifact races and held-child invalidation, and the real Curta consumer validates
the seam without a model rewrite.
