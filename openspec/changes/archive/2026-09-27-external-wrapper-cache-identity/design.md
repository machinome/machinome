## Context

ADR-026 separates tree names from class-and-parameter artifact identity.
Ordinary Python nodes mirror their defining source directory and basename,
but external-file adapters mirror the external asset instead. Two wrappers
with the same qualname and arguments can therefore claim the same artifact
even when their Python definitions differ. Curta's original and framed
`FittedDialType2` import the same STEP and retain the same inherited adjustment;
the latter adds an axle frame. Their different source closures demonstrate
mutual source currency invalidation, not differing geometry. Synthetic wrappers
with genuinely different adjustments will additionally prove correct geometry
isolation. ADR-055 correctly tracks STL/STEP wrapper code; that
tracking exposes, rather than causes, the collision.

Read contracts: architecture node/adapters/build synthesis; `node-model`
identity and source-bound leaf requirements; `build-pipeline` layout and
currency; ADR-026, ADR-055 and ADR-063. Relevant implementation is canonical
serialization in `node/base.py`, external source resolution in adapters,
`manifest.project_root`, and `declarative._specialize` (which copies author
module and qualname). Pre-spec context is
`workflow/ongoing/external-wrapper-cache-identity.md`.

## Goals / Non-Goals

Goals: distinguish external wrappers by stable author origin; preserve class,
parameters and naming semantics; terminate builds with independently current
correct geometry; keep author identity through generated joint specialization.

Non-goals: global class identity redesign, new author declarations or strings,
changing ordinary Python identity, changing containment/manifest support,
replacing source or producer-recipe currency, mechanical-contract changes,
viewer schema changes, or editing the caller during framework proposal/apply.

## Decisions

### Defining source qualifies only external-wrapper identity

For built-in source-bound adapters (`StlNode`, `StepNode`, `JScadNode`,
`OpenScadNode`), include a normalized real defining Python source path relative
to the project root that owns the resolved external source, plus the class
qualname in canonical identity. Retain the existing complete argument or
resolved-declared-parameter serialization, hash length and sanitized readable
prefix limits. Use an unambiguous internal encoding of the origin component;
authors neither supply nor see a new configuration field. Read only source
metadata to resolve origin, not CAD geometry.

Use the actual defining source, not the module import name, alias through which
the class is reached, absolute checkout path, wrapper source contents or
mtime. Thus project-local declarations keep keys when the same project and
its wrappers move together, and import aliases do not split one class. Different
qualnames in one file remain different; equal class/parameters share artifacts;
`name=` remains excluded. Source edits invalidate through existing currency,
not through ever-changing keys.

Alternatives rejected: qualname alone is the reproduced failure; a magic author
cache name or renaming Curta wrappers makes callers compensate for an internal
bug; absolute paths break relocation; module names vary with loading aliases;
content/timestamp hashes duplicate currency and churn keys on edits; extending
all ordinary Python identity needlessly invalidates unrelated caches.

### Origin resolution preserves existing construction boundaries

The artifact-owning root is already obtained from the resolved external file
by full node construction. Reuse that root rather than requiring a separate
manifest for the wrapper. Existing wrappers defined outside a project can
still resolve an external source inside a project; their defining Python path
is expressed relative to the artifact root, including `..` as necessary.
Do not add a new refusal or support for constructing complete nodes whose
external source has no discoverable project. Existing missing-file and
containment checks retain their behavior and ordering.

There is no promise of an unchanged key when a project moves away from a
stationary nonproject wrapper: their relative origin then genuinely changes.
The relocation guarantee concerns the same project and its local wrappers
moving together. A no-manifest defining-module regression must prove the
currently accepted case remains accepted, not manufacture new constructor
acceptance from a containment-check fallback.

### Generated specialization retains author origin

Declaration-site joints and fresh mates specialize node classes internally.
Their copied author module/qualname must still resolve the original author
source; runtime-generated class implementation locations must not enter the
cache identity. Preserve same geometry key between an author class and its
joint-specialized realizations. A genuinely distinct authored subclass gets
its own defining source/qualname as usual. No joint metadata or bank identity
changes are involved.

### Currency and artifact layout remain unchanged

Keep the external asset's mirrored directory and basename rules, existing
tracked-source closure/scoping, exact nanosecond stamping, fingerprints,
content digest fallback and recipe checks. Unique wrapper keys allow these
rules to operate independently; do not mask collisions by weakening currency,
accepting stale artifacts or bounding the build loop while keeping wrong
geometry. STL/STEP wrapper edits and imported helpers still invalidate their
dependants as before. STEP's STL/BREP cache pair must remain independently
current for each wrapper.

## Risks / Trade-offs

- External-wrapper keys change once → regenerate the affected artifacts via
  normal builds; do not migrate an old ambiguous cache entry into either new
  owner or delete unrelated caches.
- Origin lookup might accidentally use an ephemeral specialized class → pin
  declaration-site and fresh-mate tests to the unspecialized author identity.
- Unit identity tests can pass while geometry is still shared → red-first
  tests must materialize different `adjust` results, exercise the real build
  path with a finite timeout, and assert both artifacts current together.
- Path normalization may regress external defining modules → test relative
  `..` compatibility, alias loading, cwd independence and whole-project
  relocation; no absolute path participates in project-local keys.

## Migration Plan

Apply only after root review and the planning-only commit. First reproduce the
actual collision in bounded framework fixtures, then implement and validate.
Coordinate any CAD caller validation with the root; the root owns Curta's
pending model edits and project evidence. Record tested framework/caller
content and termination/currentness, not merely unequal path strings.

After accepted implementation, follow the framework-change workflow for ADR
disposition (a focused qualification of ADR-026 if warranted), synchronization,
archive and the single implementation record; no publication is implied.
Rollback restores prior code but also restores the collision; new artifacts
are simply unreferenced and normal sweep rules apply. No author migration or
Studio API edit is required.

## Open Questions

None consequential within the ratified scope. If implementation cannot retain
existing nonproject wrapper acceptance or specialization identity with this
origin rule, stop and return the evidence before substituting a new contract.
