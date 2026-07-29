## Context

`floor/backends/hermes.py` currently defines `HermesBackend` as a structural outline. Every method raises `NotImplementedError`. The factory registers it, and `--backend hermes` is an accepted CLI choice, but selecting it causes every orchestration operation to fail.

`floor/backends/codex.py` already demonstrates the complete JSON-RPC-over-stdio subprocess pattern that `HermesBackend` needs: `asyncio.create_subprocess_exec`, a request/response future map, a notification queue, an async event iterator, and `_request`/`_notify`/`_read_stdout`/`_drain_stderr` plumbing methods. The `AgentBackend` protocol is stable and tested through both `CodexBackend` and `FakeBackend`.

Hermes ACP speaks JSON-RPC 2.0 over stdio (newline-delimited JSON). The relevant methods for this backend are:

- `initialize(protocolVersion, clientCapabilities, clientInfo)` → `InitializeResponse(agentCapabilities, authMethods, protocolVersion)`
- `session/new(cwd, mcpServers)` → `NewSessionResponse(sessionId, models?, modes?)`
- `session/prompt(prompt: ContentBlock[], sessionId)` → `SessionPromptResponse(stopReason)`
- `session/cancel(sessionId)` — notification (no response expected)
- `session/update(sessionId, update: SessionUpdate)` — server-to-client notification carrying agent messages

The `deliver_steer` case (mid-turn correction) is the only non-trivial translation. ACP has no native mid-turn message injection. The approach: cancel the active prompt via `session/cancel`, then immediately send a new `session/prompt` with the correction. The receipt's `delivery_id` tracks the new prompt's request ID. If the cancel+reprompt races with a natural completion, the `delivery_id` check surfaces `InactiveTurn` and the orchestrator retries with `deliver_start` — same contract as the Codex path.

## Goals / Non-Goals

**Goals:**

- Implement `HermesBackend` methods (`start`, `open_role`, `deliver_start`, `deliver_steer`, `interrupt`, `close_role`, `close`) as working ACP JSON-RPC operations over stdio.
- Reuse the `_request`/`_notify`/`_read_stdout`/`_drain_stderr` pattern from `CodexBackend`.
- Translate ACP `session/update` notifications into portable `BackendEvent` instances.
- Add an acceptance test that exercises `HermesBackend` through the fake ACP server fixture.
- All existing orchestrator and acceptance tests remain green.

**Non-Goals:**

- Validating the `deliver_steer` cancel+reprompt model against a real long-running Hermes agent turn. The fake ACP fixture returns immediately, so this race path is structurally tested but not timing-validated.
- Provider/model configuration passthrough to `hermes acp` (the subprocess inherits the user's configured Hermes provider).
- Session persistence across orchestrator restarts (Hermes ACP sessions live in the adapter process).
- Changing the `AgentBackend` protocol or any other backend.

## Decisions

### JSON-RPC plumbing — reuse, don't reinvent

`CodexBackend` already implements a clean `_request`/`_notify`/`_read_stdout`/`_drain_stderr` plumbing layer over `asyncio.create_subprocess_exec`. `HermesBackend` copies this pattern verbatim, changing only the method names and parameter shapes. No shared base class — the two backends already share `AgentBackend`; sharing JSON-RPC plumbing would add a third abstraction layer for two implementations, which is premature.

### deliver_steer → cancel + reprompt

ACP has no `session/steer` or equivalent mid-turn injection. The only way to redirect an active prompt is to cancel it and start a new one. This maps naturally to the `InactiveTurn` contract: if the cancel races with a completion, the new prompt's `delivery_id` won't match the orchestrator's expected `active_delivery_id`, and the orchestrator retries with `deliver_start`.

### Role context injection

`open_role()` sends `session/new` with `cwd` set to the active project root. Immediately after, it sends an initial `session/prompt` containing the role card and runtime context as a text content block. This mirrors how `CodexBackend.open_role()` injects `developerInstructions` into `thread/start`.

### Event translation

| ACP event | BackendEvent |
|---|---|
| Streamed `session/update` `agent_message_chunk`, foreman session | Assemble chunks; emit one `role_message(role="foreman", text=...)` before completion |
| `session/prompt` sent (request dispatched) | `turn_started(delivery_id=request_id)` |
| `session/prompt` response received (`stopReason` present) | `turn_completed(delivery_id=request_id)` |
| Process exits unexpectedly | `backend_failed(error=...)` |

Designer and machinist agent messages are internal specialist communication — they arrive through the broker's report mechanism, not as `role_message` events to the maker conversation.

### open_role establishes the role contract before manifesting

`open_role()` sends the initial context prompt as an ACP request and awaits its
completion before returning the handle. The prompt directs the session to load
the authoritative role card and every skill named in its frontmatter. Bootstrap
streaming output is suppressed so it cannot appear as maker conversation. Once
the bootstrap completes, the persistent session has no active model turn and
standby consumes no tokens.

## Risks / Trade-offs

- **cancel+reprompt may lose context** — If Hermes clears session history on cancel, the correction prompt arrives in an empty session. Mitigation: the fake ACP fixture preserves session state across cancel; a real-Hermes smoke test will reveal whether `session/cancel` preserves history. If not, the initial prompt can re-inject prior context before the correction.
- **The fake ACP fixture is not a real Hermes** — It returns `stopReason: end_turn` immediately. A real `hermes acp` process may take seconds to minutes, may emit `session/update` notifications interspersed with tool calls, and may cancel differently. The fixture validates structural correctness, not timing or real-agent behavior.
- **Live steering timing varies** — The cancel+reprompt race is covered by
  delivery-correlation tests; a live-process smoke check remains the bounded
  compatibility check for real ACP timing.

## Migration Plan

1. Read the `CodexBackend` JSON-RPC plumbing methods into `HermesBackend`.
2. Implement each `AgentBackend` method against the ACP protocol surface.
3. Add the event translation logic.
4. Write acceptance test: `HermesBackend` with `fake_acp_server.py` through all lifecycle operations.
5. Run full test suite — all existing tests green, new Hermes test green.
6. Run `--backend hermes` against a live `hermes acp` process as a one-off smoke test (not part of the test suite).

Rollback: `HermesBackend` is self-contained in one file. Reverting to the stub is a single-file revert.

## Open Questions

- The current ACP surface provides no separate developer-instructions field;
  role context is therefore established through an awaited initial
  `session/prompt` text block.
- Does cancellation preserve all model context in every supported Hermes ACP
  version? `deliver_steer` preserves the ACP session and correlates request IDs
  independently from session IDs, but compatibility remains covered by the
  bounded live smoke check.
