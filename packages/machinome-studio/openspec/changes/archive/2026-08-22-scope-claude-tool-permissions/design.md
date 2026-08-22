## Context

`floor/backends/claude.py::_role_command` builds one Claude Code argv per role.
For a role with a declared tool list it passes:

```
--mcp-config <role.json> --strict-mcp-config
--tools mcp__floor__<name>,…
--permission-mode bypassPermissions        # from permission = "autonomous"
```

and for a role whose `tools` is `inherit` it passes `--safe-mode` instead of the
MCP arguments, still with the permission mode.

Two controls are conflated in that argv. `--tools` is meant to be the scope and
`--permission-mode` is meant to be the confirmation policy, so ADR 0015 reasoned
that `bypassPermissions` "does not add tools". That reasoning was sound when the
declared tools were Claude's own `Bash`, `Read`, `Write`, and `Edit`. Since
`scoped-agent-tools`, the declared capabilities resolve to floor MCP tools
instead, every one of them project-contained, and the reasoning is obsolete: the
bypass now only removes a backstop.

The readiness check in `_read_stdout` already encodes the intended invariant —
it compares the init frame's advertised `tools` against
`session_tool_names(agent.skills, runtime.tools)` and fails the delivery on
mismatch. The evidence below shows that invariant cannot hold under the current
argv.

## Spike evidence

Recorded 2026-08-22 against Claude Code 2.1.237 and the real
`floor.mcp_server`, driven through `claude -p --output-format stream-json` with
`--mcp-config`/`--strict-mcp-config`, in a throwaway git repository outside the
workspace.

**1. `--tools` does not scope MCP tools.** With
`--tools mcp__floor__read_file`, the init frame advertised all 28 floor tools.
`--tools` narrows only the built-in set; it did remove every built-in.

**2. An allowlist replaces the bypass.** With
`--allowedTools mcp__floor__read_file` and no `--permission-mode`, the init
frame reported `"permissionMode":"default"` and the session called
`mcp__floor__read_file` and received the file content. No prompt, no denial, no
bypass.

**3. Deny-by-default is real.** In that same session, asked to write a file, the
call was refused with "Claude requested permissions to use
mcp__floor__write_file, but you haven't granted it yet", the refusal was
recorded in the result frame's `permission_denials`, and no file was created.

**4. `--disallowedTools` removes MCP tools from the advertised set.** Adding
`--disallowedTools mcp__floor__write_file,mcp__floor__delete_file` reduced the
advertised set to 26 and both names were absent.

**5. The intended argv, at the librarian's exact scope.** With `--tools ""`, the
librarian's 26 resolved tools in `--allowedTools`, and the remaining three
(`edit_file`, `apply_patch`, `load_skill`) in `--disallowedTools`:

- the init frame advertised exactly 26 tools, all `mcp__floor__*`, no built-in;
- `permissionMode` was `default`;
- an allowlisted `write_file` call executed and created the file, with
  `permission_denials` empty;
- `edit_file` was not advertised and could not be called.

That is the configuration that fails today with `tool list mismatch`.

## Goals / Non-Goals

**Goals:**

- No Claude session the shop opens has permission checks disabled.
- A session's reachable tool set equals its profile-declared set, for every
  role, not only for roles that happen to declare everything.
- One control, not two: the declared tool list is the whole policy.

**Non-Goals:**

- Changing the floor MCP tool set, its containment, or which capability
  resolves to which tool.
- OS-level sandboxing. Containment remains the MCP server's path gate and the
  bounded tool surface.
- OpenCode. Its permission handling is already adapter-owned and
  deny-by-default.
- A human-in-the-loop approval channel. The floor has no surface on which a
  maker could answer a per-tool prompt, which is why `manual` is retired rather
  than made to work.

## Decisions

### Grant tools with an allowlist, in the default permission mode

The adapter passes `--allowedTools` naming exactly the session's resolved floor
tools and passes no `--permission-mode` at all. Permission checking stays on;
the declared tools are pre-granted; anything else is denied and recorded.

Alternative considered: keep `bypassPermissions` and fix only the scoping.
Rejected — it keeps a session in which a scoping regression, a future MCP
server that gains a broader tool, or a vendor default change would be
unconstrained, in exchange for nothing. The allowlist is proven equivalent for
permitted tools (evidence 2 and 5).

Alternative considered: `--permission-mode acceptEdits` or `dontAsk`. Rejected —
both are session-wide relaxations that grant by category rather than by name,
and neither is needed once the exact names are known.

### Enforce scope with a denylist, and keep the readiness check as the proof

`--tools ""` removes every built-in. `--disallowedTools` names every floor tool
the role did not declare, which removes them from the advertised set
(evidence 4). The existing init-frame comparison then verifies the result on
every real session rather than only in tests: the shop states the expected set,
the runtime reports the actual set, and a mismatch fails the delivery.

Alternative considered: rely on `--allowedTools` alone and let an undeclared
tool be denied at call time. Rejected — the tool would still be advertised, so
the role could spend turns calling something it will never be allowed to use,
and the readiness invariant would have to be weakened to a subset check, giving
up the only live proof that scoping works.

### Retire the profile `permission` declaration

`BackendRuntime.permission`, its validation, and the `permission` line in the
shipped profiles are removed. With the bypass gone, `autonomous` would be the
only workable value: `manual` in a headless `-p` session means every tool call
is refused with nobody to ask, so it describes a role that cannot work rather
than a role that asks first.

Alternative considered: keep the field and map `autonomous` to the allowlist.
Rejected — a two-valued knob whose second value silently produces a dead agent
is worse than no knob, and keeping it preserves the impression that a shop
profile can turn permission checking off.

This supersedes ADR 0015. Its concern — that autonomy must be visible and
reviewable in the profile rather than a hidden adapter default — is preserved
by the tool list, which is exactly the authority granted and is declared in the
same profile table.

### Require a concrete tool list on a Claude runtime table

`tools = "inherit"` is rejected for a Claude table, and the `--safe-mode`
compatibility branch is removed. It is the only path that could still open a
session holding Claude's native tools, `scoped-agent-tools` already forbids
selecting a backend whose sessions keep native tools, and no shipped profile
uses it.

## Risks / Trade-offs

- **A future floor tool is denied until it is mapped.** A tool added to
  `TOOL_NAMES` but to no capability in `PROFILE_TOOL_MAP` lands on every role's
  denylist. That is the safe direction and it fails loudly at readiness rather
  than silently widening a role.
- **The allowlist is name-exact.** Renaming a floor tool without updating the
  capability map produces a readiness mismatch on the next floor open. Again
  loud, and covered by tests.
- **Vendor flag surface.** `--allowedTools` and `--disallowedTools` are Claude
  Code CLI arguments; a semantics change upstream would need the same kind of
  live re-verification this change records. The readiness check is the detector.

## Migration

A profile with a `permission` line fails validation after this change with an
unknown-key error, which is the intended loud failure: the field no longer has a
meaning, and silently ignoring it would leave the author believing a policy is
in force. Both shipped profiles are updated in this change. No project data,
broker state, or on-disk runtime record carries the field.
