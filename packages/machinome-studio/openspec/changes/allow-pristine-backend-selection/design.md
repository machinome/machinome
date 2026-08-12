## Context

Every roster role currently receives a persistent backend handle during project open. The runtime control equates that allocation with use, even though a newly opened handle contains no maker message, assignment, accepted delivery, or native activity. Existing in-session updates deliberately keep backend/provider fixed because conversation migration is not portable. This change distinguishes replacement of an unused handle from migration of a used session.

The project runtime string remains the durable authority, profile declarations remain the source of tools and permissions, and the browser remains an explanatory client of server-enforced lifecycle gates.

## Goals / Non-Goals

**Goals:**

- Permit an immediate backend/provider/model/reasoning replacement while a role is permanently pristine.
- Preserve the existing idle, context-preserving update path after first use.
- Make OpenCode provider/model options come from the running backend's live catalogue.
- Keep a persisted, revision-checked `pyproject.toml` update as the default.
- Roll back or abandon a replacement without losing the existing pristine handle when validation, opening, or configuration publication fails.

**Non-Goals:**

- Migrating, replaying, or summarizing conversation state between backends.
- Re-enabling backend/provider switching after work completes.
- Changing profile-owned tools or permissions.
- Queuing a runtime choice for later.

## Decisions

### The broker owns a monotonic pristine bit

Each manifested role starts pristine. Creating an accepted message envelope or assignment for the role, or recording any role activity, permanently clears the bit. The bit is included in browser state and queried by the orchestrator under the same role delivery gate used for runtime mutation. Idle remains a separate, reversible state.

Deriving pristine from an empty activity list or current `waiting` state was rejected because activity is bounded and completed assignments return to waiting.

### Fresh-session and in-session catalogues share a portable choice shape

Runtime choices identify backend, optional provider, model, and supported reasoning values. An adapter catalogue requested without a role handle describes combinations that can open a fresh role session; one requested with a handle describes context-preserving choices for that existing session. Codex supplies its validated static set, Claude supplies fresh-session choices but rejects in-session changes, and OpenCode obtains provider/model/variant combinations from its live provider catalogue.

Hard-coding OpenCode providers or treating a profile default as its catalogue was rejected because operator authentication and installed providers vary.

### Backends are created lazily and registered with the open session

The session registry supplies the orchestrator with an async backend resolver. It reuses an existing process owner or creates and starts the requested backend, registers its event-routing task, and adds it to bounded session cleanup. This avoids requiring every supported executable to launch merely because a project opens, while allowing the catalogue and replacement path to activate another configured backend on demand.

### A pristine backend/provider change replaces, rather than mutates, the handle

Under the role delivery lock, the orchestrator rechecks native idle, broker idle, and broker pristine; validates the complete requested choice; opens a replacement handle using the requested runtime and profile-derived policy; and publishes the revision-checked project edit when requested. Only after those operations succeed does it atomically swap backend ownership and runtime state, publish browser state, and close the unused old handle. Failure before the swap closes the replacement and retains the old handle and project file.

A same-backend pristine change may also use replacement when the adapter cannot change the existing process in place, which makes Claude selectable before use without claiming context preservation.

### The server derives profile-owned policy for the selected backend

PATCH accepts backend, provider, model, and effort. For Codex and Claude, the session takes tools and permission from that role's corresponding profile table. For OpenCode it uses the profile's portable Claude tool allowlist with the existing OpenCode permission policy. The client cannot submit tools or permission.

## Risks / Trade-offs

- [Opening a live OpenCode catalogue has process cost] → Create it only when runtime controls need fresh choices, reuse it for subsequent roles, and include it in normal session cleanup.
- [A message can race a replacement] → Use the existing per-role delivery lock and recheck both idle and pristine immediately before commit/swap.
- [Old-handle cleanup can fail after a successful swap] → Treat cleanup as best-effort after the new state is authoritative; session shutdown still owns the backend process.
- [Optional backend startup can fail] → Keep choices from working backends available and report the unavailable backend reason without disturbing the current handle.

## Migration Plan

No stored data migration is required. Existing open sessions begin with the bit derived at manifestation; because deployment restarts ephemeral sessions, every new role accurately begins pristine. Rollback restores the prior API/UI behavior and leaves persisted runtime strings valid.

## Open Questions

None. The pilot selected immediate application, default persistence, joint backend/provider/model/reasoning changes, and permanent locking after first use.
