# Architecture Decision Records

Each ADR records a single consequential architectural decision—what was
decided, why, and the consequences accepted. ADRs are **deltas**: they capture
the context and reasoning at a point in time.

The **reference architecture** that incorporates all accepted decisions is
`docs/architecture-overview.md` — read that first. When an ADR and the
overview disagree during a transition, the ADR says *why* the change was made;
the overview says *what is true now*.

## Index

| # | Title | Status | Date |
|---|---|---|---|
| `0001` | [Use a FastAPI broker and Server-Sent Events for shop-floor lifecycle](./0001-go-broker-sse-shop-floor-lifecycle.md) | Accepted | 2026-07-19 |
| `0002` | [Use Python Playwright for shop-floor browser E2E tests](./0002-python-playwright-shop-floor-e2e.md) | Accepted | 2026-07-19 |
| `0003` | [Separate the porter lifecycle role from the foreman](./0003-porter-and-foreman-boundary.md) | Superseded by 0005 | 2026-07-20 |
| `0004` | [Use published build artifacts as the functional-model boundary](./0004-static-build-artifact-boundary-for-functional-model-inspection.md) | Accepted | 2026-07-20 |
| `0005` | [Use one app-server owner for live Codex shop orchestration](./0005-single-owner-codex-shop-orchestration.md) | Superseded by 0006 | 2026-07-21 |
| `0006` | [Generalize shop orchestration to a pluggable agent backend](./0006-pluggable-agent-backend-orchestration.md) | Accepted | 2026-07-26 |
| `0007` | [Depend on Hermes' off-spec second-prompt steering for active-turn corrections](./0007-hermes-second-prompt-steering.md) | Accepted | 2026-07-30 |
| `0008` | [Add a Claude Code backend, and let a backend own one process per role](./0008-claude-backend-one-process-per-role.md) | Accepted | 2026-07-30 |
| `0009` | [Carry Claude corrections on a channel the role has trusted since its first instruction](./0009-claude-correction-channel-consistency.md) | Accepted | 2026-07-30 |

## Conventions

- Accept a new ADR when a decision is consequential, irreversible without
  substantial rework, or establishes a long-lived boundary.
- Record the date it was accepted, not drafted.
- When a later ADR supersedes an earlier one, update the earlier ADR's status
  to `Superseded by NNNN` and record the superseding decision's number.
- After accepting an ADR, update `docs/architecture-overview.md` to reflect
  the new state of the architecture.
- Propose a change only after reading the architecture overview and the
  relevant ADRs to understand the current boundaries and their reasoning.
