## Why

Every Claude role the shop opens today runs with
`--permission-mode bypassPermissions`. That flag disables Claude Code's
permission checks for the whole session. It was decided in ADR 0015 when a role
session held Claude's native `Bash`, `Read`, `Write`, and `Edit` tools and a
manual permission mode made an unattended floor impossible.

That premise no longer holds. `scoped-agent-tools` replaced the native surface
with the floor MCP tool set: every tool is project-contained, there is no
generic shell tool, no generic network tool, and no destructive git operation.
The MCP surface *is* the boundary. Disabling permission checks on top of it
grants nothing the shop wants and removes the one runtime backstop that would
contain a session whose tool scoping failed.

Live evidence against Claude Code 2.1.237 (recorded in `design.md`) shows the
bypass is unnecessary and that the current scoping is not what the shop
believes it is:

- With `--allowedTools` naming the floor tools and **no** `--permission-mode`,
  the session reports `permissionMode: default` and calls an allowlisted floor
  tool with no prompt and no denial. A tool that is not allowlisted is refused
  and recorded in `permission_denials`, and its side effect does not happen.
- `--tools` does **not** filter MCP tools. A session launched with
  `--tools mcp__floor__read_file` advertises all 28 floor tools. `--tools` only
  narrows the built-in set. `--disallowedTools` does remove MCP tools from the
  advertised set.

So the per-role tool scoping the profile declares is not enforced for Claude:
the foreman, designer, and machinist happen to declare capabilities that resolve
to the complete floor tool set, which hides it. The librarian declares no `Edit`
and therefore expects 26 tools while the session advertises 28 — the readiness
check in `floor/backends/claude.py` compares those sets and fails the delivery
with `tool list mismatch`.

## What Changes

- **BREAKING** The Claude adapter stops passing `--permission-mode`. Scoped
  sessions run in Claude Code's default permission mode, which is
  deny-by-default, and are granted exactly their declared tools through
  `--allowedTools`.
- The adapter passes `--disallowedTools` for every floor tool the role does not
  declare, so the advertised tool set equals the declared one and the existing
  readiness check becomes satisfiable for a role that declares less than
  everything.
- **BREAKING** A Claude runtime table no longer declares `permission`. The
  declared tool list is the whole policy; there is no second knob and no value
  that turns permission checking off. Claude permission handling becomes
  adapter-owned and deny-by-default, as OpenCode's already is.
- **BREAKING** A Claude runtime table must declare a concrete tool list;
  `tools = "inherit"` is rejected. That removes the last code path — the
  `--safe-mode` compatibility branch — that could open a Claude session holding
  native tools, and with it the last path that could combine native tools with
  disabled permission checks.

After this change no Claude session the shop opens can reach a tool outside the
floor MCP surface, and none runs with permission checks disabled.

## Capabilities

### Modified Capabilities
- `shop-agent-backend`: the Claude adapter's permission and tool-scoping
  arguments, stated in terms of what the session can reach rather than a vendor
  permission mode.
- `shop-runtime-profile`: a Claude runtime table declares model, effort, and a
  concrete tool list, and no longer declares a permission policy.
- `scoped-agent-tools`: the backend-scope requirement gains the guarantee that a
  scoped session's permission checks stay enabled, and that a tool outside the
  declared set is unreachable rather than merely undeclared.

## Impact

- `floor/backends/claude.py` — `_role_command` gains `--allowedTools` and
  `--disallowedTools`, loses `--permission-mode` and the unscoped `--safe-mode`
  branch.
- `floor/profiles.py` — `BackendRuntime.permission` and its validation are
  removed; `tools` must be a concrete list for a Claude table.
- `profiles/fordesmac/profile.toml`, `profiles/builder/profile.toml` — the
  `permission` line is dropped from all five Claude runtime tables.
- `docs/adrs/0015-profile-owned-claude-autonomous-permissions.md` — superseded
  by a new ADR; `docs/adrs/README.md` and `docs/architecture-overview.md`
  updated.
- `tests/test_orchestrator.py` — the assertion that the argv carries
  `bypassPermissions` is replaced by assertions about the allowlist, the
  denylist, and the absence of any permission-mode flag.
- No change to the floor MCP tool set, the broker, the browser, or any profile
  prompt.
