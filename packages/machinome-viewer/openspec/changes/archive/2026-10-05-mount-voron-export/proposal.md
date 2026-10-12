## Why

Voron-2's unchanged portable printer export first stalled in Chromium before any model request. The applied validation correction now reaches all 1,565 model paths, exposing a second concrete blocker: immediate request fan-out causes 290 Chromium `ERR_INSUFFICIENT_RESOURCES` failures and the full mount still fails. Both costs are viewer-owned; the producer's valid document and geometry remain intact.

## What Changes

- Complete validation of a large binding-rich posed document as one coherent synchronous expression operation, preserving all existing refusals.
- Reuse successfully established absence of reserved profile calls within that document's validation operation, so shared aliases are not repeatedly walked for every operation and flexible parameter.
- Admit rigid model and marking loads through one finite queue shared by this bundle's viewers, preserving independent overlap, real asset bytes, duplicate-URL semantics, early draw-order reservations and load/error/disposal ownership.
- Add counted regression tests and browser acceptance that prove loading reaches geometry and preserves default and instructed poses, using Voron-2's actual full export as the mandatory integration gate.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: make the existing expression-cache-pressure mount promise explicit for large posed portable exports, bound geometry request fan-out across simultaneous viewers, and preserve malformed-input, draw-order, loaded/error and disposal guarantees.

## Impact

Viewer-owned loader/expression validation, geometry admission/ownership and their tests, primarily `machinome_viewer/widget/src/viewer.ts`, `expressions.ts`, `tree.ts` and a small private admission helper if appropriate. Existing binding-table validation, generation guards and finite reclamation remain. No new dependency, document schema, host option, API version or numerical algorithm is needed. The framework, project sources, manifest, models and shared venv are unchanged by the fix.

Originating evidence: `workflow/warts.md`, “Voron-2 — portable export stalls before model loading”; the pinned export belongs to project `projects/3D-Printers/Voron-2` (`Voron2.4`, `a67893b88cd05e58eaa88bbf381455144f65117f`). Its current HEAD is `52a9ad17439556648f7a3ab638e065137ad6d37d`, a later authority-documentation update; the acceptance export is unchanged. See `docs/RESUME.md`, `docs/evidence/resumed-main-validation.json` and proposal diagnostics in `evidence.md`.

Standalone viewer worktree: `WTs/mount-voron-export`, branch `mount-voron-export`, based on clean `main` at `5838b97e1e1c10bf468d2f3a40a0c86a0a4448b7`. The pilot authorized proposal/application subject to parent review and local rebase/merge after successful actual Voron review and spec sync/archive. The parent reviewed and approved this bounded plan on 5 October 2026 under that authority, after reading the applicable baseline and ADR-043/044 and passing strict validation. A different Sol 6.1 agent applies. Keep planning and implementation/archive in separate commits. Nothing authorizes pushing or publication.

Planning commit `0ca25281b4905b5072b2809feb1a0e31e0ac250b` covers the initial validator correction. On 5 October 2026 the parent reviewed and approved this additional geometry-loading revision against the actual failed browser result and existing load/ownership/draw-order contracts. Strict validation passed. The newly discovered blocker has a separate planning-only amendment commit before the different applier resumes; implementation and archive remain a later, separate commit. The seven completed tasks and their evidence are retained, without claiming a successful mount.
