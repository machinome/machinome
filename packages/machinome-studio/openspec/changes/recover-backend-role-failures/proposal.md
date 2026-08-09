## Why

A recoverable per-role backend failure, such as Claude Code exhausting a session limit, currently raises through the event router and shuts down the entire shop. The maker loses the live floor precisely when they need a visible explanation and a way to continue once the external limit clears.

## What Changes

- Keep the broker, browser, and unaffected role sessions running when one backend role reports `role_failed`.
- Record the failed role and backend-provided reason in current run state and show that failure in the browser.
- Reopen a failed role lazily when the broker next delivers an envelope to it, preserving the broker and project state rather than requiring a floor restart.
- Clear the visible failure when that replacement session opens, so a maker message can re-trigger a failed user-facing agent and a surviving Foreman can subsequently re-trigger a failed specialist.
- Preserve fail-closed behavior for `backend_failed`, which means the selected backend as a whole can no longer route work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: A role-scoped backend failure no longer ends the run; the orchestrator releases the failed session and reopens it on its next delivery.
- `shop-agent-lifecycle`: The roster records and restores a role's failed state and reason until the role is recovered.
- `shop-live-state-stream`: Current failure state is included in snapshots and live updates so reconnecting browsers remain accurate.
- `shop-browser-workspace`: The workspace visibly explains a role failure and removes that explanation after recovery.

## Impact

The change affects `floor/orchestrator.py`, broker run state and events in `floor/app.py`, the React workspace under `floor/frontend/`, the generated static bundle, and their unit/browser tests. It changes no backend-native protocol and introduces no dependency. The existing portable distinction between `role_failed` and `backend_failed` remains authoritative.
