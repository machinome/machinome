## Why

Enigma's ordinary Studio controls now complete, but a screenshot of its unchanged 2,023-part inspection model still times out after 180 seconds on the software GPU; the built-in static capture also starts the continuous viewer loop, whose capture contention is already documented in ADR-077. The project needs a reproducible photograph through the ordinary capture command, so this change tests and applies the existing on-demand rendering mode to eligible stills without changing the model or its operating semantics.

## What Changes

- Select the existing on-demand mode for a posed document without instructions and for a clocked document, using external animation, autoplay disabled, and both control surfaces disabled.
- Redraw the final fitted or requested view explicitly through the public viewer handle before announcing capture readiness.
- Keep the existing continuous path for running programs and posed documents with instructions, including the existing rest-state and animation-instant rules.
- Verify pixels, transparency, camera and bank preservation on small real browser fixtures, then measure one bounded capture of the unchanged Enigma publication and the ordinary project snapshot path.
- Preserve failed experiments and report the interactive Studio screenshot limitation separately. This is a correction to static capture, not a new interactive rendering mode or a claim that Studio's complete typing path works.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `snapshot-capture`: eligible still captures draw a ready frame without a continuing animation loop, while preserving existing capture content and unsupported-document behavior.

## Impact

The implementation is confined to `packages/machinome-viewer/machinome/viewer/web/capture.py` and its capture tests/specification. It consumes existing viewer API 29; package API, document versions, dependencies, project geometry, Studio source and interactive mounts remain unchanged. The intended benefit to Enigma is a working ordinary static photograph and less avoidable preview rendering work; measured performance and successful pixels are required before claiming that benefit.

Originating evidence is Enigma main `f6dc73b`, `sources/studio-quiet-controls-visual-v4.json`, and its pinned raw browser/process records. The document is version 4, has no instructions or program, and has SHA256 `f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a`. The screenshot failure is evidence of the need, not proof that this proposed change alone fixes it. ADR-077 records the already-established continuous-loop versus on-demand capture mechanism on Curta.

This standalone cycle branches from clean framework main `5c07ea93682bc1007849cefe7ef30f96710fd409` in registered worktree `machinome/WTs/capture-still-without-frame-loop`, slot 15. The pilot's 8 November instruction to finish ongoing work in all branches and merge everything to main supplies advance authority for implementation and local integration. The coordinating repository agent reviewed the complete proposal, design and tasks on that date and approved proceeding, requiring preserved view, bank/time, refusals, alpha and unchanged empirical budgets. This is agent review under advance authority, not a claim of human review of the finished artifacts. The coordinator will integrate into main after the completed two-commit cycle; publication, push and contact remain outside scope.
