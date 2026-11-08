## Why

Enigma needs its 26 existing lamp-glass bodies to show the source-backed dark/lit colors from the same model state that ordinary Studio controls operate. The core companion `color-model-lamps` proposes a supported two-color value; ignoring it would silently display the wrong electrical observation.

## What Changes

- Read conditional node `color: {when, on, off}` in version-14 documents and advertise viewer API 30 with document versions 1–14.
- Resolve finite zero/nonzero conditions through the existing pose/bank/binding scope and update the same mesh's declared base color, preserving geometry ownership and existing color inheritance.
- Keep hover/highlight as overlays over the current declared color; clearing them must reveal the latest model-selected color.
- Preserve existing placement admission and clocked request atomicity, including candidate color preparation, reset/restore/replay and independent-scope recovery.
- Retain legacy hex/null documents and all version-1–13 behavior; distinguish posed/clocked/running version-14 documents by their existing payloads, not `version >= 5` alone.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: consume the explicit color-choice format and apply it to existing geometry under the standing model state.

## Impact

Viewer-owned implementation targets are `machinome/viewer/web/widget/src/{types,tree,viewer,presentation}.ts`, existing document/binding validation and runtime/capture classification helpers, `widget/package.json`, viewer tests/fixtures and the viewer's unreleased change record. Core producer/helper/manual work belongs to paired `../machinome/openspec/changes/color-model-lamps/`; the Studio-owned API shop-skill sync is named there. No custom JavaScript API, display panel, texture/material platform, electrical calculation, optical brightness or geometry replacement is added.

This is a companion planning record in the same managed `illuminate-model-lamps` worktree, based on clean main `6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9`. ADR-188/194/196 establish this product's current monorepo ownership. The pilot’s active completion-and-merge goal supplies advance authority for planning, implementation and local integration; the coordinating agent reviewed both full plans and the Studio contract dependency. This records agent review, not human review of the finished text. The capture predecessor is integrated at the recorded base; verify the planning-only commit before apply. Installation, push and publication remain outside this cycle.
