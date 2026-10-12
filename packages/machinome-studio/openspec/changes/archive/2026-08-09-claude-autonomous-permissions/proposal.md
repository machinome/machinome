## Why

Claude role sessions currently start in Claude Code's default manual permission
mode. A role can have `Read` in its declared tool policy but still pauses to
ask the maker before it can read its profile prompt, preventing an unattended
shop run.

The shop needs an explicit, reviewable way for a Claude profile to opt into
autonomous tool execution without re-enabling operator-machine customization
or silently broadening a role's declared tool set.

## What Changes

- Add a Claude permission-mode declaration to the validated per-agent backend
  runtime policy.
- Let a Claude profile explicitly select autonomous execution, translated to
  Claude Code's non-interactive `bypassPermissions` session mode.
- Keep the existing profile-declared tool list as the role's available-tool
  boundary and retain safe mode, so autonomous execution neither adds tools nor
  loads project, user, plugin, hook, memory, or MCP customization.
- Configure the shipped Builder and Fordesmac Claude roles for autonomous
  execution so a first-time Claude-backed shop can proceed without approval
  prompts.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `shop-runtime-profile`: profile backend policy gains an explicit,
  enforceable Claude permission-mode setting.
- `shop-agent-backend`: Claude role sessions honor the selected permission mode
  while retaining their declared available tools and isolated configuration.

## Impact

- `floor/profiles.py` and its profile-validation tests.
- `profiles/builder/profile.toml` and `profiles/fordesmac/profile.toml`.
- `floor/backends/claude.py` and Claude backend command tests.
- `openspec/specs/shop-runtime-profile/spec.md`,
  `openspec/specs/shop-agent-backend/spec.md`, and architecture documentation.
