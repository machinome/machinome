## Why

The multi-backend orchestration change (archived `2026-07-26-multi-backend-orchestration`) defined the `AgentBackend` protocol, extracted `CodexBackend`, wired the `--backend` flag, and added a `HermesBackend` structural outline. The design document for that change classified the full Hermes ACP integration as a Non-Goal and shipped `HermesBackend` as a stub where every method raises `NotImplementedError`.

The pilot's original request was for the shop to support Hermes Agent as a second agent backend so the same harness can drive mechanical work through either Codex or Hermes. The `--backend hermes` flag exists and is accepted, but selecting it causes every orchestration operation to fail. This change finishes the implementation: it wires `HermesBackend` to a real `hermes acp` subprocess, reusing the JSON-RPC plumbing pattern already proven by `CodexBackend`.

## What Changes

- Replace the `HermesBackend` stub methods in `floor/backends/hermes.py` with a working implementation that launches `hermes acp` as a subprocess and speaks the ACP JSON-RPC protocol over stdio.
- Add acceptance tests that exercise `HermesBackend` through the portable `AgentBackend` protocol using the existing `fake_acp_server.py` fixture.
- Correct the archived design document's Non-Goals section: the Hermes backend IS wired to a real process (not merely a structural outline).

## Capabilities

### Modified Capabilities

- `shop-agent-backend`: The Hermes backend operates a real `hermes acp` subprocess. `HermesBackend.start()` launches the process and completes ACP `initialize`. `open_role()` sends `session/new` and injects role context via an initial prompt. `deliver_start()` and `deliver_steer()` use `session/prompt` with cancel+reprompt for active-turn steering. `interrupt()` sends `session/cancel`. Events translate from ACP `session/update` notifications and `session/prompt` responses into portable `BackendEvent` instances.

## Impact

- `floor/backends/hermes.py` — full implementation (~200 lines replacing the 77-line stub); mirrors the `CodexBackend` JSON-RPC plumbing pattern.
- `tests/test_orchestrator.py` — new acceptance test: `HermesBackend` with fake ACP fixture exercises all `AgentBackend` operations.
- `tests/fixtures/fake_acp_server.py` — unchanged (already speaks correct ACP surface).
- `openspec/changes/archive/2026-07-26-multi-backend-orchestration/design.md` — Non-Goals section amended: full Hermes ACP integration is now in scope.
- Broker, role cards, skills, product pipeline, browser UI, `AgentBackend` protocol, `CodexBackend`, and `--backend` flag — no changes.
