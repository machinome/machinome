## Why

The pilot needs Codex again as an explicit Studio role backend, using a separate one-time Studio Codex login on the pilot's existing account while preserving the profile's exact tool authority. ADR 0025 retired it because native execution could not be removed; the 26 September `codex-tool-isolation` spike now demonstrates a bounded route on Linux with Codex CLI 0.157.1, GPT-6 Sol and Astra, without dangerous permissions.

## What Changes

- Restore explicit `codex:<model>[:<reasoning>]` selections and the Codex choice in Agents; retain Claude profile defaults and the existing pristine/idle mutation rules.
- Implement persistent Codex role sessions with precisely the profile's resolved floor operations and declared skill catalogue, using client-executed dynamic tools and no native execution environment.
- Refuse unsupported binaries, models, tool registries, effective configuration and authentication modes; report actionable failures without substituting a backend or weakening permission policy.
- Support ordinary delivery, steering, trusted notices, idle model changes, portable activity, text/image tool results, errors and bounded teardown through the existing backend seam.
- Supersede the backend retirement decision after validation; document the measured support matrix and its limits. A durable Studio-owned file-backed login and one shared authenticated app-server preserve simultaneous projects; normal CLI credentials remain untouched.
- Keep wider executor authority hardening and operating-system isolation of project CAD code deferred. This change makes no claim that existing floor operations sandbox hostile project code.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: qualify and operate a scoped persistent Codex backend through the portable seam.
- `project-runtime-selection`: admit supported explicit Codex selections and its fixed OpenAI provider in Agents.
- `scoped-agent-tools`: enforce the same exact declared tool boundary for qualified Codex sessions and bind dynamic calls to their owning role/session.

## Impact

Studio only: backend factory/probe, a hub-owned shared Codex service and project-specific adapters, runtime resolution, existing floor-tool protocol integration, Agents choices, adapter/orchestrator/browser regression fixtures, README/operating contract/reference architecture and ADR 0032. Spike evidence is carried on the cycle branch. No copied operator refresh tokens, profile Codex default table, framework mutation, publication, integration, push, external research surface or global role adapter is introduced.
