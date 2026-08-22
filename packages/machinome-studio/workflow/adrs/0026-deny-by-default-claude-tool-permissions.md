# ADR 0026: Grant Claude roles their declared floor tools, deny everything else

**Status:** Accepted

**Date:** 2026-08-22

**Origin:** `scope-claude-tool-permissions`

**Supersedes:** [ADR 0015](./0015-profile-owned-claude-autonomous-permissions.md)

## Context

ADR 0015 decided that a Claude runtime table declares
`permission = "manual" | "autonomous"`, and that the adapter maps `autonomous`
to `--permission-mode bypassPermissions`. At the time a role session held
Claude's own `Bash`, `Read`, `Write`, and `Edit` tools; the ADR is explicit that
the authority granted "permits arbitrary commands available to the operator
account", bounded by role contract rather than by any sandbox.

The scoped-agent-tools work replaced that surface. A role session now reaches
only the floor MCP tool set: every path-taking tool is contained by the active
project, there is no generic shell tool, no generic network tool, and no
destructive git operation. The MCP surface is the boundary. Disabling the
runtime's permission checking on top of it grants nothing the shop wants, and
removes the one runtime backstop that would contain a session whose tool
scoping failed.

Measurement against Claude Code 2.1.237 also showed the scoping itself was not
in force. `--tools` filters only the built-in set: a session launched with
`--tools mcp__floor__read_file` advertised all 28 floor tools. Three of the four
shipped roles declare capabilities resolving to the complete floor tool set, so
nothing looked wrong; the librarian, which declares no `Edit`, expected 26 tools
against 28 advertised and failed the adapter's readiness comparison.

## Decision

The Claude adapter passes no `--permission-mode` at all. A role session runs in
the runtime's default, deny-by-default permission mode and is granted exactly
its resolved floor tools by name with `--allowedTools`, so a declared tool never
waits for a confirmation no one is present to give.

Scope is enforced with the two controls that actually enforce it: `--tools ""`
removes every built-in tool, and `--disallowedTools` removes every floor tool
the role did not declare, so the advertised set equals the declared set. The
adapter's existing readiness check — comparing the init frame's advertised tools
against the expected ones — remains the live proof on every session.

A profile no longer declares a Claude permission policy. The declared tool list
is the entire authority a role session holds. A Claude runtime table must
declare that list concretely; `tools = "inherit"` and the `--safe-mode`
compatibility branch it selected are removed, because that was the last path
that could open a Claude session holding native tools.

## Consequences

- No Claude session the shop opens has permission checking disabled, and none
  can reach a tool outside the floor MCP surface.
- ADR 0015's concern — that autonomy be visible and reviewable in the profile
  rather than a hidden adapter default — is preserved by the tool list, which
  is declared in the same profile table and is now exactly the authority
  granted.
- A floor tool added to the server but mapped to no profile capability lands on
  every role's denylist, and a renamed floor tool produces a readiness mismatch
  on the next floor open. Both fail loudly rather than silently widening or
  narrowing a role.
- A profile still carrying `permission` fails validation. That is intended: the
  field no longer has a meaning, and ignoring it would leave its author
  believing a policy is in force.
- The grant depends on two Claude Code CLI arguments whose semantics were
  verified live for this decision. A future change to them is detected by the
  readiness check rather than by silent over-permission.
