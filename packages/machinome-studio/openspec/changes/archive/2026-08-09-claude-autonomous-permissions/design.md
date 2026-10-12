## Context

The Claude adapter passes each role's model, effort, and available-tool policy
to a long-lived `claude -p` process. It also uses `--safe-mode` to prevent
project and operator customization from redefining the repository-owned role
contract. Claude Code's default permission mode is manual, so an available
`Read` tool still stops at an approval prompt before the Foreman can load its
required profile prompt.

The user wants an unattended Claude-backed floor. This is a security boundary:
the existing role policy includes unrestricted `Bash` for the Builder,
Foreman, Designer, and Machinist. A blanket adapter default would hide that
choice and make later profile additions unexpectedly autonomous.

## Goals / Non-Goals

**Goals:**

- Make autonomous Claude tool execution a visible, validated profile choice.
- Translate that choice to Claude Code's `bypassPermissions` session mode.
- Preserve the profile's model, effort, and available-tool restriction.
- Preserve `--safe-mode`, so local CLAUDE.md files, hooks, plugins, skills,
  MCP configuration, memory, and user settings cannot alter a role.
- Set the two shipped profiles to autonomous execution after the pilot has
  ratified the explicit risk.

**Non-Goals:**

- Adding an autonomous policy to Codex, Hermes, or OpenCode.
- Changing a role's available tools, sandbox, network, project-root boundary,
  broker topology, or its maker-facing authority.
- Treating a tool-list restriction as operating-system sandboxing.
- Circumventing Claude Code permissions through local settings or ambient
  operator configuration.

## Decisions

### A Claude-specific, explicit policy value

Add `permission = "manual" | "autonomous"` to each Claude runtime table and
carry it in the resolved runtime object. It is required for Claude and rejected
for other backends, because only Claude exposes an enforceable per-session
permission-mode control in the declared runtime policy.

`manual` retains Claude Code's confirmation behavior. `autonomous` maps exactly
to `--permission-mode bypassPermissions`. Both shipped profiles declare
`autonomous`; a future profile must make its own explicit selection.

Alternatives considered:

- Make all Claude sessions autonomous in the adapter: rejected because it
  silently changes every existing and future profile.
- Depend on `--allowed-tools`: rejected because it selects available tools but
  does not answer approval prompts.
- Use Claude Code settings files: rejected because that makes local operator
  state part of a repository-owned role contract and conflicts with safe mode.

### Keep available tools and permission approval distinct

The adapter continues to pass only the role's declared `--tools` list. The new
permission mode only decides whether Claude asks before using one of those
available tools. It neither broadens that list nor gives a role access to an
undeclared tool.

This is a contract boundary, not a host sandbox: a role that is declared to use
`Bash` can issue arbitrary commands available to the operator account. The
profile review is where that authority is intentionally accepted.

### Preserve isolated runtime configuration

`--safe-mode` remains mandatory alongside the new permission mode. Autonomous
execution must not reactivate project or user Claude configuration, hooks,
plugins, MCP servers, memory, or skills. The existing system prompt and broker
envelope behavior are unchanged.

### Record the durable decision

Create ADR 0015 to document why autonomous execution is profile-owned, its
relation to available tools, and its limitations. Update the architecture
overview and ADR index when the decision is accepted.

## Risks / Trade-offs

- [Autonomous roles can execute destructive commands through declared `Bash`]
  → The policy is explicit per Claude role, tool lists remain reviewed profile
  data, and the profile prompts retain project/repository boundaries.
- [Claude Code changes the semantics or availability of `bypassPermissions`]
  → Assert the generated argv in the fake-CLI suite and validate the installed
  CLI version during an operator smoke test.
- [A future profile omits the policy]
  → Profile validation fails before any project or backend side effect.
- [A tool-list restriction is mistaken for OS containment]
  → State plainly in the ADR and architecture documentation that it is not a
  sandbox.

## Migration Plan

1. Add and validate the Claude-only policy field.
2. Mark every shipped Claude role as `autonomous`.
3. Pass the matching permission mode in the Claude adapter and add red-first
   regression tests for both autonomous and manual selection.
4. Run focused profile/backend tests and the full suite.
5. On the pilot's next requested floor launch, start a fresh run; existing
   Claude role processes retain the arguments with which they were created and
   must not be expected to change in place.

Rollback is a profile change back to `manual`, followed by a fresh floor
launch. No persistent state or migration is involved.

## Open Questions

_None. The pilot selected autonomous Claude execution for the shipped
profiles._
