# ADR 0015: Make Claude autonomous permissions profile-owned

**Status:** Superseded by [ADR 0026](./0026-deny-by-default-claude-tool-permissions.md)

**Date:** 2026-08-09

**Origin:** `claude-autonomous-permissions`

**Amends:** [ADR 0008](./0008-claude-backend-one-process-per-role.md)

## Context

The Claude backend launches roles with an explicit available-tool list and
`--safe-mode`, but Claude Code's default permission mode is manual. As a
result, a Foreman that has the `Read` tool still pauses to ask the maker before
it can read the profile prompt that its trusted session contract requires. A
floor cannot run unattended under that behavior.

The available-tool list and permission approval are different controls. The
list determines which Claude tools a role can request; `bypassPermissions`
decides whether Claude confirms each request. The shipped Builder, Foreman,
Designer, and Machinist roles all declare `Bash`, so granting autonomous
execution is consequential: it permits arbitrary commands available to the
operator account. It is not operating-system sandboxing.

Making `bypassPermissions` an unconditional adapter default would also silently
grant that authority to every future Claude profile. Loading it from a local
Claude settings file would make operator-machine state part of a
repository-owned role contract and would conflict with the isolation established
by ADR 0008.

## Decision

Each Claude runtime table in a shop profile SHALL explicitly declare
`permission = "manual"` or `permission = "autonomous"`. The profile loader
rejects omission, invalid values, and the field on Codex or Hermes tables
before any project or runtime side effect.

The Claude adapter maps `manual` to `--permission-mode manual` and
`autonomous` to `--permission-mode bypassPermissions`. It continues to pass
only the profile's declared tool list and retains `--safe-mode`. Autonomous
permission therefore eliminates Claude confirmation prompts for available
tools; it does not add tools or re-enable project/user configuration, hooks,
plugins, MCP servers, memory, or skills.

The initial Builder and Fordesmac Claude roles declare `autonomous`. A future
profile must make the policy choice independently.

## Consequences

- A Claude-backed shop can load its role prompt and use its declared tools
  without maker approval dialogs.
- The authority is visible and reviewable in profile TOML instead of being a
  hidden adapter default or operator-machine setting.
- `Bash` in an autonomous role remains high authority and is bounded by the
  role contract and active-project discipline, not by an OS sandbox.
- A running Claude role session retains its startup arguments; policy changes
  take effect only in a newly opened floor.
