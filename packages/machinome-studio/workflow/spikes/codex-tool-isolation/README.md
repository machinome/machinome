# Codex tool isolation spike

Date: 2026-09-26. Studio base: `c912033`. Executable: `codex-cli 0.157.1`,
installed from the OpenAI npm package. Platform: Linux.

Status: feasibility evidence, not a ratified design or an implemented backend.
Origin: the pilot wants Codex restored while preserving the profile's exact
tool policy, without `danger-full-access`.

## Result

A working route exists in the tested version: run app-server with no execution
environment, a controlled model catalogue, an isolated configuration home, and
client-executed dynamic tools. The successful mock requests advertised exactly
`functions.floor_hello`; a second role with no tools advertised none. Forced
calls to native tools were rejected before execution. Authenticated GPT-6 Sol
and GPT-6 Astra both successfully used the custom tool. A restarted server
resumed the conversation and custom tool successfully with an explicit
no-environment override on the next turn.

This qualifies a new adapter for proposal work. It does not restore Codex in
Studio, supersede ADR 0025, or establish OS isolation for floor operations.

## What was measured

`probe.py` starts the real installed app-server against a local HTTP Responses
fixture. The fixture captures the actual model request, including tools encoded
as `additional_tools` input items, and emits deliberate calls to forbidden
tools. This avoids treating a model's voluntary refusal as enforcement proof.
No credentials or external model endpoint are used in that experiment.

`live.py` runs a separate authenticated smoke test with the operator's existing
file-backed Codex login. It copies only `auth.json` into a private temporary
home, removes that copy afterward, and does not load the operator's MCP,
plugins, instructions or configuration. Its prompts contain only synthetic
fixture content. Neither script passes `danger-full-access` or bypass flags.

| Experiment | Observed outcome |
| --- | --- |
| No environment plus disabled feature flags, bundled GPT-6 catalogue | Native shell/patch calls rejected, but code-mode and collaboration tools still advertised; `collaboration.list_agents` actually callable |
| Controlled catalogue, no environment at thread start | Exactly the declared custom tool; forced native calls rejected |
| Same configuration, ordinary later turns and model change | Exact tool list preserved; custom call succeeds |
| Restart and plain `thread/resume`, no turn override | Native `apply_patch` reappears; forced patch reaches its handler and is blocked by read-only sandbox |
| Explicit `environments: []` on every turn, including after resume | Exact tool list preserved; forced native patch call is unsupported |
| Second role, `dynamicTools: []` | Empty advertised tool list; first role's tool rejected |
| Positive control: fresh thread with default environment | `apply_patch` reappears, proving the inspection detects environment-backed tools |
| Authenticated Sol custom call | Returns the client-supplied `HELLO_SPIKE_RESULT` |
| Authenticated request for native file read/write | Model reports unavailable access; sentinel content is not disclosed and target file is absent |
| Authenticated switch to Astra and process restart/resume | Custom tool still works |

The passing mock run has 23 cases, including shell variants, stdin, native
patching, image reads, MCP-resource listing, delegation, questions, planning,
web-tool invocation, code mode and an undeclared floor operation. It also
checks harmless filesystem sentinels and verifies every captured tool list.

## Required configuration discovered by the spike

1. Use app-server's experimental API and supply each role's exact
   `dynamicTools`. Handle `item/tool/call` in the trusted client. Dynamic tools
   persist through resume in this version.
2. Send `environments: []` at thread creation **and every `turn/start`**.
   `ThreadResumeParams` in this version has no `environments` field. The
   thread-start setting alone is insufficient after process restart.
3. Keep `sandbox = "read-only"` and `approvalPolicy = "never"` as backstops.
   Never auto-approve unexpected server requests; the fixture denies them.
4. Use a controlled `model_catalog_json`. Starting from the installed bundled
   catalogue, the spike sets `tool_mode = "direct"`, removes
   `multi_agent_version`, and clears `experimental_supported_tools`.
   It preserves model identities and the rest of their metadata. This is a
   deliberate model-tool configuration change, not a model substitution.
5. Set `tools.experimental_request_user_input.enabled = false` and
   `tools.update_plan.enabled = false`. Disable web search and unrelated tool
   features. `probe.py:DISABLED` and `Client` are the exact tested configuration.
6. Use a private runtime home and a minimal process environment. Do not load
   operator or project MCP servers as a side effect of obtaining authentication.

Model metadata takes precedence over the code-mode feature switch, and the
bundled GPT-6 metadata also selects multi-agent v2. Consequently, a list of
`--disable` flags alone is not an exact-tool policy. Disabling the code-mode
host merely made its advertised `exec` tool return an error; it did not remove
the tool. The controlled catalogue is necessary for the tested solution.

## Evidence and reproduction

- `default-catalog.json`: records the extra advertised and callable surface.
- `unguarded-resume.json`: records the failed exact-tool assertion after restart.
- `guarded.json`: passing deterministic cases and observed tool registries.
- `live.json`: authenticated tool calls and final responses for four smoke cases.

Run from the Studio worktree root with the installed Codex executable on PATH:

```sh
python3 docs/spikes/codex-tool-isolation/probe.py --controlled-catalog --guard-turns --output /tmp/codex-guarded.json
python3 docs/spikes/codex-tool-isolation/live.py --output /tmp/codex-live.json
```

The live script makes authenticated model requests and consumes the operator's
quota. The deterministic script writes a compact summary and a separate
`.raw.json` containing the full local mock-model requests. The retained JSON
evidence is reduced to relevant facts; full requests are intentionally not
committed because they repeat large vendor instruction blocks.

To reproduce the failures, omit `--controlled-catalog` for the bundled model
surface, or use `--controlled-catalog` without `--guard-turns` for the resume
failure. The latter exits nonzero after saving its failed assertion.

## Limits and implications for an adapter

- Pin the supported binary and controlled catalogue contract. Experimental
  fields and model metadata are not a vendor guarantee of stable isolation.
  Unknown versions, models or an expanded registry must fail closed. A future
  adapter needs a tested capability check; this spike observes outbound model
  requests and does not discover a production tool-registry attestation API.
- The authenticated smoke test proves actual model/tool interoperability, but
  exact registry inspection and forced rejection tests use the local provider.
- The installed app-server logs that this host cannot create the user namespaces
  required by its Linux sandbox. The no-environment tool path nevertheless
  works, without dangerous flags. This is not proof of a functioning OS sandbox;
  the tool registry is the primary boundary measured here.
- A private home removes user configuration inheritance. System/enterprise
  configuration can still exist and needs effective-policy checks in an adapter.
  Do not override managed restrictions to make a runtime start.
- Only synthetic custom-tool dispatch was exercised. Full Studio operations,
  image results, steering, cancellation, approval handling, failures, concurrent
  roles and authentication renewal remain adapter integration work.
- The probe does not execute hostile CAD or prove host containment of the
  current floor tools. Executor-side role checks and isolated project-code
  workers are the separately deferred recommendations in the workspace's
  `docs/studio-containment-recommendations.md`.
- The runtime should keep the project out of Codex's direct environment and
  provide profile instructions and tool results through the adapter. Every
  callback still needs role/session/name/argument checks, even when Codex's
  registry rejected all out-of-policy calls in this spike.

## Sources

- Installed `codex app-server generate-json-schema --experimental` output:
  `ThreadStartParams`, `TurnStartParams`, `ThreadResumeParams`,
  `DynamicToolCallResponse`.
- Installed `codex debug models --bundled` and `codex features list`.
- [App-server documentation](https://learn.chatgpt.com/docs/app-server).
- [Configuration schema](https://developers.openai.com/codex/config-schema.json)
  (`ToolsToml`, `ExperimentalRequestUserInput`, `UpdatePlanToolConfig`).
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  (`model_catalog_json`, tool feature switches).
- Current Codex source retrieved through Context7: tool registration in
  `core/src/tools/spec_plan.rs`, tool-mode selection in `core/src/tools/mod.rs`,
  and thread environment fields in `app-server-protocol/src/protocol/v2/thread.rs`.
