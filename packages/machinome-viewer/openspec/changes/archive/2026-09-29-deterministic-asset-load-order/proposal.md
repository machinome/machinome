## Why

Leonardo's `demo-incremental-source-grid` gave different pixels at frame 10, pixel (487, 262), across two fresh 70-frame Videomaker captures with the same inputs. A controlled two-coincident-STL ABBA experiment on the fixed Viewer API 28 bundle proves a narrower cause: changing only asynchronous STL response completion order flips the visible overlap colour. That demonstrated nondeterminism must be removed before Videomaker can require exact cold-versus-incremental frame equality; whether it explains the Leonardo pixel remains to be verified after repair.

## What Changes

- Make fresh-mount model and marking mesh/material construction and resulting equal-depth rendering order independent of asset fetch completion order, while retaining concurrent fetches and the document's existing geometry, colour, depth and marking behavior.
- Preserve targeted-update prepare-before-mutation and failed-update containment. Each failed load discards its newly reserved mesh and disposes its material and any returned geometry; test those local paths without expanding aggregate staging cleanup.
- Prove the correction red-first with deferred-load tests and the controlled ABBA browser capture, then test exact pixels on repeated real Leonardo cold captures and Videomaker's 80- and 70-frame cold/incremental consumers. A real-film mismatch after the controlled fix is a separate finding, not permission to weaken pixel equality.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: Fresh mounts of the same published document at the same view and pose do not vary their overlapping-part pixels with STL completion order; newly reserved resources are released when their own load fails, while targeted updates retain their existing failure containment.

## Impact

The correction is internal to the widget tree's load path and tests, with browser evidence using the existing bundle and public mount interface. The originating consumer is Leonardo's Videomaker film. No new author-facing field, document version, public viewer API, package dependency or host contract is proposed. No general graphics, aggregate update-cleanup or cross-history reconciliation determinism audit is included.
