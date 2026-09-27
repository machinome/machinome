## Why

Curta Type I's `simulation/dial_fits.py` and `simulation/dial_frames.py`
define different `FittedDialType2` wrappers for the same STEP (with the same
inherited adjustment; one adds an axle frame), but both claim one cached STL
artifact. Their different source closures and currency alternately invalidate
that artifact, and a real faceted register build failed to terminate before
interruption; the finding is recorded in `workflow/warts.md`.

## What Changes

- Qualify internal external-file wrapper identity by the stable defining
  Python source path relative to the artifact-owning project, plus the
  existing class qualname and parameters.
- Preserve ordinary Python node identity bytes, parameter/name behavior,
  generated declaration-site and fresh-mate specialization identity, source
  currency and artifact layout.
- Prove distinct cached geometry and build termination/currentness for the
  originating STEP-to-STL collision, plus synthetic differing-adjustment
  STEP/STL coverage for incorrect geometry reuse.
- Affected external-wrapper cache keys change and rebuild once. There is no
  author-facing API, magic string, coordinate/control or viewer-schema change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-model`: qualify external-wrapper artifact identity by defining source
  while retaining ordinary Python canonical serialization.
- `build-pipeline`: independently current artifacts for different wrappers
  of one external source, without repeated mutual invalidation.

## Impact

Internal identity resolution in `machinome/node/base.py` and existing
source-bound adapters, with identity, adapter, specialization and build tests.
No new dependencies or publication format changes. Studio's public
class-plus-parameters identity description remains correct; no companion edit
is required. The pilot explicitly ratified this narrow direction on
27 September 2026 after the explanation of Curta's collision.

Standalone cycle: branch/worktree `external-wrapper-cache-identity` at
`machinome/WTs/external-wrapper-cache-identity`, clean base
`928ac64c0968838ccedd84dc86336fac125c691b`, intended integration target
framework `main`. This is proposal-only; another Sol applies after the root's
adversarial review and planning commit. Curta remains caller-owned.
