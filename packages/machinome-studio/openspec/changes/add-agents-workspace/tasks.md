## 1. Runtime and activity contracts

- [ ] 1.1 Add red backend-protocol and orchestrator tests for portable activity, runtime catalogues, context-preserving updates, backend/provider invariance, Claude rejection, and the joint native/broker idle gate
- [ ] 1.2 Add red Codex, Claude, and OpenCode fixture tests for normalized tool/message/error/diff activity and each adapter's runtime-update/catalogue behavior
- [ ] 1.3 Implement portable activity/catalogue/runtime-update values and the orchestrator's role-locked update path without backend-name branching
- [ ] 1.4 Implement Codex turn-scoped model/effort updates, OpenCode provider-catalogued session updates, Claude read-only behavior, and defensive native activity translation

## 2. Session API and project persistence

- [ ] 2.1 Add red broker, project-runtime, and Floor API tests for enriched snapshot state, bounded activity updates, runtime/catalogue routes, active/assigned conflict responses, temporary overrides, persisted updates, and stale-revision protection
- [ ] 2.2 Add `tomlkit` and implement revision-checked, atomic `[tool.solid-node-studio.agents]` mutation that preserves unrelated project TOML
- [ ] 2.3 Extend session, broker, and API surfaces with resolved runtime metadata, authoritative editability/idle state, activity replacement semantics, catalogues, and atomic update responses on the existing SSE path

## 3. Agents workspace

- [ ] 3.1 Add red browser acceptance coverage for interactive Agents navigation, roster selection, persisted area state, activity filters/details/diffs, Open in Code, disabled active and Claude controls, stale conflicts, and successful temporary/persisted updates
- [ ] 3.2 Implement the Agents roster context panel and mounted central inspector from `docs/design/agents/Agents.dc.html`, preserving Model, Code, and conversation state
- [ ] 3.3 Implement model/reasoning drafting with explicit Apply, checked-by-default persistence, catalogue-backed OpenCode choices, conflict/error feedback, and no backend/provider/apply-mode controls
- [ ] 3.4 Implement the live normalized activity feed, counts, filters, expandable results, unified diffs, token display when available, and Code navigation
- [ ] 3.5 Match the accepted desktop styles and narrow-window reachability without adding an icon font or another live connection

## 4. Verification and durable records

- [ ] 4.1 Run focused Python, frontend build, and Playwright suites; fix regressions and record honest gaps for any unavailable real backend
- [ ] 4.2 Add and accept an ADR for bounded in-session runtime control/activity normalization, update the ADR index, and rewrite the architecture overview to the implemented state
- [ ] 4.3 Sync every delta requirement to baseline specs, validate all OpenSpec records strictly, and archive `add-agents-workspace`
- [ ] 4.4 Commit the completed implementation/archive record, integrate the standalone branch into `main`, verify the integrated content, and safely remove the clean worktree
