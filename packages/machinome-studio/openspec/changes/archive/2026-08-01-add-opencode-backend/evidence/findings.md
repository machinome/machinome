# OpenCode 1.18.11 Isolation Probe

**Date:** 2026-08-01

`spike.py` launched a password-protected loopback server from a temporary
active-project repository. It passed all of the proposed isolation controls:

```text
opencode serve --pure --hostname 127.0.0.1 --port <ephemeral> --print-logs
OPENCODE_CONFIG=<generated config>
OPENCODE_CONFIG_DIR=<generated empty role config directory>
OPENCODE_DISABLE_PROJECT_CONFIG=true
```

The temporary project included a root `AGENTS.md`, an `opencode.json`, and a
`.opencode/agents/hostile.md` file. The server became healthy as OpenCode
1.18.11, accepted Basic authentication, exposed authenticated provider defaults
for `openai/gpt-5.6-terra-fast` and `opencode/big-pickle`, and created a
persistent session rooted at the temporary project. Those model values describe
the probed operator environment; they are not proposed shop defaults.
The complete redacted request and configuration record is `spike-1.18.11.json`.

## Result

The process log in that record shows OpenCode loading these user-global paths
despite all of the controls above:

```text
/home/asa/.config/opencode/config.json
/home/asa/.config/opencode/opencode.json
/home/asa/.config/opencode/opencode.jsonc
/home/asa/.opencode/opencode.json
/home/asa/.opencode/opencode.jsonc
```

`OPENCODE_CONFIG` and `OPENCODE_CONFIG_DIR` supplement the global sources;
they do not replace them. Isolating the configuration home would hide those
sources but would also hide the operator-managed provider authentication and
default model the design requires the server to reuse.

Therefore OpenCode 1.18.11 cannot support the originally proposed combination
of:

1. Reusing operator-managed authentication and inherited default model.
2. Disabling all user OpenCode agents, skills, plugins, MCP servers, hooks,
   configuration, and instruction files.
3. Loading only the active project root `AGENTS.md` as supplemental guidance.

The pilot chose the revised boundary on 2026-08-01: the backend intentionally
inherits operator-global OpenCode configuration needed for authentication and
provider defaults while it disables project OpenCode configuration and manually
composes only the active project's root `AGENTS.md` as supplemental guidance.
The measured `--pure` mode also disables external plugin execution. This
evidence proves that bounded inherited-configuration boundary rather than
blocking adapter implementation.

The probe does not prove per-session role-contract composition, allowlisted
skill injection, deny-by-default permissions, model/variant selection in
a role turn, SSE delivery correlation, or exactly-once steering. Those remain
unchecked implementation gates. The viable policy therefore keeps existing
profiles unchanged and makes model/variant/tool compatibility defaults and
permissions adapter-owned for now. That is a bounded exception to the shop's
profile-explicit runtime policy, not evidence that OpenCode 1.18.11 exposes
equivalent controls.
