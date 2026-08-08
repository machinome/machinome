## Why

Sprint 1 defines shop-floor as the browser-based interface for the AI-first
SolidNode Studio. A maker should use Codex to open and close that interface,
instead of operating the shop-floor service themselves.

This change establishes that entry and exit point as the first independent
slice of shop-floor. It does not inherit behavior, code, or architecture from
an earlier proof of concept.

## What Changes

- Build a new local FastAPI shop-floor service that Codex can open for a maker.
- Make the opened shop available at a stable local browser location.
- Show the browser whether the shop is open or closed, including across a
  service restart without a page reload.
- Allow Codex to close the shop-floor service when the maker asks.

## Capabilities

### New Capabilities

- `shop-floor-lifecycle`: The maker-visible FastAPI and browser lifecycle for
  opening, monitoring, closing, and restarting shop-floor through Codex.

### Modified Capabilities

- None.

## Impact

- Introduces the first FastAPI shop-floor application, its local service
  lifecycle, and its browser status surface.
- Establishes the browser as the unified interface surface for later Sprint 1
  work.
- Does not implement agent activity, project browsing, design observability,
  functional-model viewing, or the foreman conversation workflow from the
  later story slices.

## Review Status

The pilot ratified the `shop-floor-lifecycle` behavioral specification on
2026-07-19. The FastAPI and Server-Sent Events decisions were also confirmed
by the pilot. The intentionally minimal browser-surface candidate remains
subject to implementation evidence.
