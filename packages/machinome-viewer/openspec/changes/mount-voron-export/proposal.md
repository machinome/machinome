## Why

Voron-2's unchanged portable printer export succeeds but stalls in Chromium before any model request, so its maker cannot inspect or operate the delivered printer. Read-only diagnostics now establish repeated rebuilding of its oversized binding graph during validation and repeated structural checks of the same shared aliases; these are viewer costs, not evidence that the producer's valid document should be simplified.

## What Changes

- Complete validation of a large binding-rich posed document as one coherent synchronous expression operation, preserving all existing refusals.
- Reuse successfully established absence of reserved profile calls within that document's validation operation, so shared aliases are not repeatedly walked for every operation and flexible parameter.
- Add counted regression tests and browser acceptance that prove loading reaches geometry and preserves default and instructed poses, using Voron-2's actual full export as the mandatory integration gate.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: make the existing expression-cache-pressure mount promise explicit for large posed portable exports and retain its malformed-input and document-local-meaning guarantees.

## Impact

Viewer-owned loader/expression validation and its tests, primarily `machinome_viewer/widget/src/viewer.ts`, `expressions.ts`, and their test seams. Existing binding-table validation, generation guards and finite reclamation remain. No new dependency, document schema, host option, API version or numerical algorithm is needed. The framework, project sources, manifest, models and shared venv are unchanged by the fix.

Originating evidence: `workflow/warts.md`, “Voron-2 — portable export stalls before model loading”; the pinned export belongs to project `projects/3D-Printers/Voron-2` (`Voron2.4`, `a67893b88cd05e58eaa88bbf381455144f65117f`). Its current HEAD is `52a9ad17439556648f7a3ab638e065137ad6d37d`, a later authority-documentation update; the acceptance export is unchanged. See `docs/RESUME.md`, `docs/evidence/resumed-main-validation.json` and proposal diagnostics in `evidence.md`.

Standalone viewer worktree: `WTs/mount-voron-export`, branch `mount-voron-export`, based on clean `main` at `5838b97e1e1c10bf468d2f3a40a0c86a0a4448b7`. The pilot authorized proposal/application subject to parent review and local rebase/merge after successful actual Voron review and spec sync/archive. The parent reviewed and approved this bounded plan on 5 October 2026 under that authority, after reading the applicable baseline and ADR-043/044 and passing strict validation. A different Sol 6.1 agent applies. Keep planning and implementation/archive as two commits. Nothing authorizes pushing or publication.
