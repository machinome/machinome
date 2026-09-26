# ADR 0025: Retire Codex as a shop agent backend

**Status:** Superseded by [ADR 0032](./0032-restore-scoped-codex-backend.md)

**Date:** 2026-08-12

**Deciders:** Pilot

**Origin:** OpenSpec change `retire-codex-backend`

**Amends:** [ADR 0006](./0006-pluggable-agent-backend-orchestration.md),
[ADR 0011](./0011-profile-defined-shop-runtime.md),
[ADR 0017](./0017-project-selected-per-agent-runtime.md),
[ADR 0018](./0018-multi-backend-orchestration.md),
[ADR 0022](./0022-control-idle-agent-runtimes-in-place.md),
and [ADR 0023](./0023-replace-pristine-agent-backends.md)

## Context

Codex app-server was the shop's first agent backend and, until this decision,
its default: every profile agent had to declare a Codex runtime table, and an
agent the active project did not name opened on Codex.

Since then the shop has grown the scoped-agent-tools capability. A profile
declares the exact tool set an agent may use, the floor exposes those tools over
its own MCP server, and project edits travel through reviewable floor
operations. Claude and OpenCode can be launched with that policy enforced —
their native file, shell, and network tools are replaced by the floor surface.

Codex cannot. A Codex session retains native command execution and file editing
regardless of what the profile declares. The codebase already encoded the
exception: profile validation rejected any Codex table whose `tools` was not
`inherit`, and the `scoped-agent-tools` specification carried an explicit
"Role selects codex" scenario stating that the capability did not apply.

That made tool policy conditional on which backend a project happened to name,
and the condition was invisible in the project's own `pyproject.toml`. It also
meant the one backend that ignored the policy was the one every unnamed agent
got by default.

## Decision

Retire Codex as a selectable agent backend. `claude` and `opencode` are the
complete selectable set.

Enforceable tool policy becomes a condition of selectability rather than a
per-backend exception: a backend whose sessions keep tools the profile did not
declare is not offered at all.

Claude becomes the profile-explicit default. `PROFILE_BACKENDS` is `("claude",)`,
each profile agent declares exactly one runtime table, and an agent the active
project does not name opens on that Claude declaration. OpenCode keeps its
bounded adapter-owned compatibility policy from ADR 0012 and remains reachable
only through an explicit project selection.

A `codex:<model>` project selection is rejected with an error naming the
offending agent key and value, before any project or backend side effect.

This retirement concerns the *agent runtime backend* only. Codex as a
repository-development assistant is unaffected: `.codex/config.toml` and the
shop's assistant-portability goal stand.

## Alternatives considered

**Keep Codex behind a documented warning.** Rejected: the shop cannot verify
the warning was read, and the resulting sessions still edit project files
outside the reviewable floor path.

**Keep Codex behind an explicit opt-in flag.** Rejected: it preserves the same
hole and adds a control surface to maintain, for a capability the shop has
decided it does not want.

**Make OpenCode the default instead of Claude.** Rejected: ADR 0012 keeps
OpenCode's policy adapter-owned and gives it no profile table, so it cannot
supply a profile-declared default.

**Substitute Claude for a `codex:` selection.** Rejected: the project's declared
model and effort would not survive the substitution, and the maker would not
learn the selection was ignored.

## Consequences

The portable `AgentBackend` seam is unchanged; two adapters implement it instead
of three. `floor/backends/codex.py`, its fake app-server and echo fixtures, and
its adapter-specific acceptance tests are removed. Backend-neutral orchestrator
coverage moves to the remaining fakes.

The assignment-acknowledgement message loses its non-scoped variant: every
selectable backend now acknowledges through the `floor_acknowledge` MCP tool,
so the CLI form is no longer emitted.

A project declaring `codex:<model>` for an agent fails to open until that line
names a Claude or OpenCode runtime. The shop keeps a route to OpenAI models
through OpenCode; it stops keeping an unconstrainable one.

The shop's single-provider fallback story is now Anthropic-only by default,
which is a narrower default than before. That is accepted: the alternative was a
default that could not honour the shop's own tool contract.
