## 1. Lock the breaking contract

- [x] 1.1 Add and run focused tests proving `codex` is rejected by backend creation, the probe set, project runtime selection, and profile validation, and that an unselected agent falls back to Claude; retain the red result as evidence before implementation.

## 2. Remove the Codex runtime surface

- [x] 2.1 Remove Codex registration from `floor/backends/__init__.py`, delete `floor/backends/codex.py`, and drop `codex` from `floor/backends/probe.py` and the orchestrator's catalogue fan-out.
- [x] 2.2 Remove `CODEX_MODELS`, `CODEX_EFFORTS`, and Codex parsing from `floor/preparation.py`, and the Codex branch from `floor/sessions.py`.
- [x] 2.3 Reduce `PROFILE_BACKENDS` to Claude in `floor/profiles.py`, move the unselected-agent fallback to `agent.backends["claude"]`, and reject a Codex runtime table as a retired backend key.
- [x] 2.4 Remove the `[agents.backends.codex]` tables from `profiles/builder/profile.toml` and `profiles/fordesmac/profile.toml`.
- [x] 2.5 Remove the Codex backend entry, its fixed `OpenAI` provider mapping, and Codex wording from `floor/frontend/src/main.tsx`.

## 3. Remove Codex test infrastructure

- [x] 3.1 Re-point backend-neutral orchestrator, lifecycle, floor-API, and scoped-tool tests at a remaining fake fixture rather than deleting their coverage.
- [x] 3.2 Delete `tests/fixtures/fake_codex_app_server.py`, `tests/fixtures/fake_codex_echo_server.py`, and the Codex-only acceptance, probe, product-identity, runtime-profile, and runtime-selection cases.
- [x] 3.3 Run the focused backend, profile, orchestrator, lifecycle, scoped-tool, and product-identity suites.

## 4. Record the current product and architecture

- [x] 4.1 Add ADR 0025, amend the Codex-specific portions of ADRs 0006, 0011, 0017, 0018, 0022, and 0023, and update the ADR index.
- [x] 4.2 Update the reference architecture, README, AGENTS.md, the running-the-shop and debug-workflow skills, the Fordesmac role prompts, and the reference design's backend catalogue to describe only Claude and OpenCode, leaving Codex-as-development-assistant references intact.
- [x] 4.3 Sync all seven delta specifications into their baseline specifications, including the `shop-agent-backend` purpose statement.

## 5. Validate and close the implementation

- [x] 5.1 Run the complete automated test suite and strict OpenSpec validation.
- [x] 5.2 Scan tracked active product surfaces for Codex references and verify every survivor is either a historical record or a repository-development-assistant reference.
