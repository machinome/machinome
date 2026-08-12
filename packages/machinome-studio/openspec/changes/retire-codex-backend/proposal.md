## Why

The shop's scoped-agent-tools capability exists so a profile can decide exactly
which tools an agent may use, and so agents edit project files only through the
floor's own reviewable operations. Codex cannot be constrained that way: a Codex
session always retains its native command-execution and file-editing tools
regardless of what the profile declares, so its runtime tables must say
`tools = "inherit"` and its sessions route around the shop's editing path. A
selectable backend that silently ignores profile tool policy is a hole in a
contract the rest of the shop enforces, and it is not worth keeping for the
model access it provides — OpenCode already reaches those models through a
backend that does honour the policy.

## What Changes

- **BREAKING** Remove `codex` from the selectable backends. `claude` and
  `opencode` remain.
- **BREAKING** Profile agents declare a Claude runtime table only, and an agent
  the active project does not name falls back to Claude rather than Codex.
- **BREAKING** Reject `codex:...` project runtime selections in
  `[tool.solid-node-studio.agents]`.
- Delete the Codex app-server adapter, its fake app-server and echo fixtures,
  and Codex-only acceptance, profile, and runtime-selection tests.
- Make scoped tool enforcement a condition of selectability rather than a
  per-backend exception: every selectable backend enforces its profile-declared
  tool policy.
- Remove the Codex backend picker entry, its fixed `OpenAI` provider mapping,
  and Codex wording from the floor browser.
- Remove active Codex behavior from baseline specifications, the reference
  architecture, the reference design's backend catalogue, runtime guidance, and
  product documentation.
- Record the retirement in ADR 0024, amending the Codex-specific portions of
  ADRs 0006, 0011, 0017, 0018, 0022, and 0023.

Codex as a *repository-development assistant* is out of scope. `.codex/config.toml`
and the shop's assistant-portability goal are unaffected; this change retires
only the Codex agent runtime backend.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `scoped-agent-tools`: Replace the Codex exemption with a rule that a backend
  which cannot enforce a profile tool policy is not selectable.
- `shop-agent-backend`: Reduce selectable and test-fixture backends to Claude
  and OpenCode and remove the Codex runtime-update requirements.
- `shop-runtime-profile`: Require one Claude runtime table per agent instead of
  a Codex and Claude pair, and make the shipped profiles valid with Claude and
  OpenCode.
- `project-runtime-selection`: Remove Codex from accepted selection values, make
  Claude the unselected-agent fallback, and drop Codex from the provider-first
  runtime controls.
- `shop-agent-lifecycle`: Remove Codex from the backends covered by the
  profile-driven role lifecycle contract.
- `shop-floor-lifecycle`: Remove Codex from the backends covered by the floor
  startup and lifecycle contract.
- `shop-live-state-stream`: Remove Codex from the mixed-backend live-state
  scenarios.

## Impact

The change removes `floor/backends/codex.py`, its registration in
`floor/backends/__init__.py`, `codex` from `floor/backends/probe.py` and the
orchestrator's catalogue fan-out, `CODEX_MODELS`/`CODEX_EFFORTS` and Codex
parsing from `floor/preparation.py`, the Codex branch in `floor/sessions.py`,
the Codex profile schema and default-resolution path in `floor/profiles.py`, the
Codex tables in `profiles/builder/profile.toml` and
`profiles/fordesmac/profile.toml`, the Codex entries in the floor browser, and
`tests/fixtures/fake_codex_app_server.py` and
`tests/fixtures/fake_codex_echo_server.py` with their dependent tests. It updates
active OpenSpec baselines, ADR status and index entries, the architecture
overview, README, AGENTS.md, the running-the-shop and debug-workflow skills, the
Fordesmac role prompts, and the reference design's backend catalogue.

Projects declaring `codex:<model>` for an agent must select a Claude or OpenCode
runtime instead; the run fails with a message naming the agent and value rather
than silently downgrading the selection.
