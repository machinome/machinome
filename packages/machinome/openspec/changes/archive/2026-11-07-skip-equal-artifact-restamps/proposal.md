## Why

Enigma's ordinary publication diagnosis found eight verified-source currency
restamps that requested the artifacts' already-correct exact mtimes, needlessly
changing their ctime; such a write invalidates an identity a consumer already
holds. Avoiding this
unnecessary mutation is useful maintenance in its own right; the cause of other
delayed ctime changes and a cure for the intermittent full-build refusal remain
unproved.

## What Changes

- Make `currency.restamp` leave an artifact alone when its current integer
  `st_mtime_ns` exactly equals the requested integer timestamp.
- Retain actual restamping when timestamps differ and the existing best-effort
  `OSError` behavior. Preserve all recipe, fingerprint, retained-source digest,
  record migration, generation and artifact identity checks.
- Keep the content-verified caller's currency-record refresh even when no
  artifact timestamp write is needed.
- Prove the matching-mtime fallback red first using a source-owned fixture and
  a real, already-open `ArtifactSnapshot`; preserve genuine timestamp-change,
  coarse-filesystem and stale/replacement refusal coverage.
- Validate Enigma through its canonical declared model and ordinary build first
  on the WT-owned core, then through the locally integrated installed runtime's
  plain command. Retain actual outcomes and any remaining limitation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `build-pipeline`: content-proven currency refresh must not write an artifact's
  timestamps when its exact desired mtime already holds; record refresh and all
  existing refusal boundaries remain mandatory.

## Impact

Core ownership is `packages/machinome/machinome/currency.py`, with focused core
tests and the core `build-pipeline` specification. No public API, viewer/Studio
code, dependency, document format/version or lamp appearance behavior changes.
No Enigma geometry is vendored into the framework. The origin evidence and
scope are indexed in `workflow/ongoing/skip-equal-artifact-restamps.md`.

This is a standalone cycle from clean primary `main`
`b0829b39809e64e889e56eb9bececa57cd3430ad`, in managed branch/worktree
`skip-equal-artifact-restamps`, slot 15. Workspace `goal.md` authorizes correcting
ordinary-delivery limitations in the owning package; root explicitly requires
review of this complete proposal before apply. On 2026-11-07 root reviewed and
approved proposal/design/spec/tasks under that active goal and released the
planning-commit/apply hold. Authorized stages are planning commit 1, real-red
implementation, focused checks, canonical WT-runtime caller acceptance and
sync/archive/completion commit 2. Local integration is authorized after root
reviews green caller evidence and the exact two-commit handoff. This is delegated
agent review under pilot goal authority, not a claim the pilot reviewed the
finished text. No push, publication, public/API or lamp implementation.
