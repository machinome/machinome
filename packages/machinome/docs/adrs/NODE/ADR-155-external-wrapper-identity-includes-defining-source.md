# ADR-155: External Wrapper Identity Includes Its Defining Source

**Status:** Accepted
**Date:** 2026-09-27
**Ratified:** The pilot approved defining-source-qualified internal identity after reviewing Curta's reproduced cache collision; root accepted implementation/design review before this extraction.
**Extends:** ADR-026 and ADR-063 — the class component of external-file artifact identity
**Preserves:** ADR-055, ADR-060, ADR-071, ADR-081, ADR-098 and ADR-102 — tracked wrapper sources, scoped currency, specialization identity and producer recipes
**OpenSpec change:** [external-wrapper-cache-identity](../../../openspec/changes/archive/2026-09-27-external-wrapper-cache-identity/)

## Context

Curta-Type-I-3x defines `FittedDialType2` in both `simulation/dial_fits.py`
and `simulation/dial_frames.py`. Both import the same STEP and retain the
same inherited adjustment; the framed wrapper adds an axle frame. External
adapters mirror the asset's directory and basename rather than the Python
wrapper's. Qualname and parameters alone therefore gave these distinct
wrappers one artifact path. Their correctly different tracked source closures
kept invalidating each other's cache, and the faceted register build did not
terminate. Synthetic STEP/STL wrappers with different adjustments also prove
that the shared path can expose the wrong cached geometry.

## Decision

Only the built-in source-bound adapters `StlNode`, `StepNode`, `OpenScadNode`
and `JScadNode` qualify their canonical class component with the real defining
Python source relative to the project owning the resolved external asset.
An unambiguous JSON pair encodes qualname and relative origin. Complete
constructor arguments or resolved declared parameters retain their existing
serialization, as do the 60-character readable-prefix and 12-hex hash limits.
Tree names remain excluded. Ordinary Python canonical bytes do not change.

A private lightweight mixin admits the actual adapters without examining
arbitrary author attributes or importing other CAD backends. Origin resolution
uses the already discovered asset project after existing validation and before
artifact paths are assigned. No geometry, source content or time enters the
key. A previously admitted nonproject wrapper around an asset inside a project
remains admitted, with a relative `..` origin when necessary. This adds no
support for assets with no discoverable project and changes no containment or
missing-file refusal.

Import aliases and symlink aliases of the defining source share identity.
Project-local wrappers moving with their project retain keys; moving a project
away from a stationary outside wrapper is not covered by that promise.
Generated site-joint and fresh-mate specializations retain the copied author's
module and qualname and therefore its geometry key. Distinct authored classes
remain distinct. Artifact layout and every existing source/recipe currency
rule remain unchanged.

## Alternatives rejected

- Qualname alone is the reproduced collision. Renaming wrappers or adding a
  magic author cache name makes callers compensate for an internal bug.
- Absolute checkout paths break relocation; module names depend on import
  aliases rather than defining source.
- Source-content or timestamp keys duplicate currency and churn paths on
  edits. Weakening currency would merely conceal stale or wrong geometry.
- Qualifying every ordinary Python class needlessly invalidates unrelated
  caches already separated by their defining-source layout.

## Consequences and evidence

Affected external-wrapper caches rebuild once through normal production;
ambiguous old artifacts are not migrated to either new owner. There is no
author migration, schema change or Studio contract change. Existing sweep
rules still own obsolete artifacts.

Bounded native builds use fresh instances and the STL build entry, prove
simultaneous independent STL/BREP currentness, and perform an unchanged fresh
rebuild without exports. Cached STL and BREP geometry distinguishes synthetic
adjustments. Metadata, relocation, aliases, ordinary identity, complete
parameters, names and all four adapters' specializations are executable
regressions. Geometry-affecting wrapper/helper edits keep keys but invalidate
and rebuild through existing currency. Root-owned caller and final regression
evidence are recorded in the change rather than inferred from unequal paths.
