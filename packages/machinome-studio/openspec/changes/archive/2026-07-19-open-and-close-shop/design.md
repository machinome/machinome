## Context

`docs/product/sprints/SPRINT-001-shop-floor-interface.md` is the source of
truth for this change. It defines shop-floor as browser-based software run by
Codex for a maker creating a functional 3D-printable project. The maker's
intended direct Codex interactions are opening and closing the shop.

This is a new implementation in this worktree. No prior proof-of-concept code,
service contract, or architecture is an input to the design.

## Goals / Non-Goals

**Goals:**

- Give Codex one clear way to start and stop a local FastAPI shop-floor
  service.
- Give the maker a stable browser location when the shop has opened.
- Keep an already-open browser page informed when that service stops and
  restarts.
- Establish a clean foundation for the Sprint 1 browser interface.

**Non-Goals:**

- Showing agents, projects, designs, or functional models.
- Routing instructions between the maker and foreman.
- Defining the menu, view, and chat behaviors beyond the browser entry point.
- Reusing or preserving an earlier proof-of-concept implementation.

## Decisions

### Decision: Shop-floor is a FastAPI service at a stable local location

Codex launches shop-floor as a distinct local FastAPI service and reports its
browser location only after that service is available. Codex owns the matching
stop operation. Restarting the service uses the same local browser location so
an already-open browser page can reconnect.

This expresses the sprint's distinction between Codex as shop runner and the
maker as browser user, while naming the concrete server required for this
lifecycle slice.

Alternative considered: making the maker start a server command directly.
Rejected because it contradicts the sprint's intended interaction.

### Decision: The browser monitors lifecycle through Server-Sent Events

The browser page opens a long-lived Server-Sent Events connection to a
lifecycle-status endpoint. A connected stream supplies the `Shop is open`
state. Connection loss supplies the `Shop is closed` state. The browser's SSE
reconnection behavior restores `Shop is open` when the FastAPI service returns
at the same location, without reloading the page.

Server-Sent Events provide the one-way, long-lived status channel needed by
this slice without preempting the bidirectional maker-to-foreman chat from a
later story.

Alternative considered: polling a health endpoint. Rejected because the pilot
specified that the monitor keeps a Server-Sent Events connection open.

### Candidate: The first browser surface is intentionally minimal

The initial service supplies a browser entry point but does not simulate the
later menu, view, or chat capabilities. Those user-visible areas are owned by
their corresponding Sprint 1 story slices.

Alternative considered: building the whole three-area interface now. Rejected
because it would preempt the later stories and obscure the evidence from this
first lifecycle slice.

### Decision: Build independently in this worktree

The implementation begins with new source and tests in this worktree. It does
not copy, refactor, or use prior proof-of-concept code as a baseline.

## Risks / Trade-offs

- [A service can fail during startup] → Codex reports that opening failed and
  does not claim the browser interface is available.
- [The status stream can disconnect for a reason other than intentional close]
  → The browser accurately reports the service as unavailable; a later
  lifecycle story can distinguish further causes if needed.
- [A minimal first surface can be mistaken for the finished shop interface] →
  Keep the later sprint capabilities explicitly outside this change.
- [Process cleanup can be incomplete] → Add lifecycle tests and a manual
  open/close verification before declaring the slice built.

## Review Status

The pilot ratified the `shop-floor-lifecycle` behavioral specification, the
minimal-browser-surface decision, and confirmed the FastAPI and Server-Sent
Events decisions on 2026-07-19. The independent-build decision records the
pilot's explicit direction from 2026-07-19.
