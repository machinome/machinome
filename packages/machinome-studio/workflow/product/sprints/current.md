# SPRINT-001: Shop-floor interface

## Goal

Give the maker one browser-based shop-floor interface that Codex can open and
close, with a menu, artifact view, and chat. Establish the first observable
slice of live shop activity while preserving room for project browsing,
artifact inspection, and foreman conversation to evolve incrementally.

## Stories

- [x] STORY-001 — Open and close the shop
  - Source: `docs/product/stories/STORY-001-open-and-close-shop.md`
  - OpenSpec changes: `2026-07-19-open-and-close-shop`,
    `2026-07-19-go-shop-floor-lifecycle`,
    `2026-07-19-rebuild-floor-fastapi`
  - Integration: `97a3ca5`
- [x] STORY-002 — Use one browser workspace
  - Source: `docs/product/stories/STORY-002-use-one-browser-workspace.md`
  - OpenSpec change: `2026-07-20-use-one-browser-workspace`
  - Integration: `35fa1b2`
- [ ] STORY-003 — Direct the foreman
  - Source: `docs/product/stories/STORY-003-direct-the-foreman.md`
  - OpenSpec change: not started
  - Integration: pending
- [x] STORY-004 — See agent work state
  - Source: `docs/product/stories/STORY-004-see-agent-work-state.md`
  - OpenSpec change: `2026-07-19-manifest-shop-agent-lifecycle`
  - Integration: `19336c7`
- [ ] STORY-005 — Inspect the functional model
  - Source: `docs/product/stories/STORY-005-inspect-functional-model.md`
  - OpenSpec change: not started
  - Integration: pending

## Ratified scope

- Included: service lifecycle, one browser workspace, foreman conversation,
  visible agent state, and functional-model inspection.
- Excluded: detailed project browsing, design-process observability, and direct
  chat with agents other than the foreman.

## Decisions and scope changes

- 2026-07-20 — Reconstruct the existing Sprint 001 implementation through the
  sprint-base and per-OpenSpec-cycle worktree protocol.

## Outcome

Pending.
