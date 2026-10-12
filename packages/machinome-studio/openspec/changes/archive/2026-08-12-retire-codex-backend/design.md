## Context

Codex app-server was the shop's first agent backend and remains the profile
default: `PROFILE_BACKENDS` requires a Codex table on every agent, and
`resolve_profile_runtime()` falls back to `agent.backends["codex"]` for any agent
the active project does not name.

Since then the shop has grown a scoped-agent-tools capability. A profile declares
the exact tool set an agent may use, the floor exposes those tools over its own
MCP server, and project edits travel through reviewable floor operations. Claude
and OpenCode can be launched with that policy enforced. Codex cannot: its session
keeps native command execution and file editing whatever the profile says. The
codebase already admits this — `profiles.py` rejects any Codex table whose
`tools` is not `inherit`, and `scoped-agent-tools` carries an explicit
"Role selects codex" exemption scenario.

So Codex is not merely unconstrained; it is the one selectable backend that can
route around the editing path the rest of the shop is built to observe. The
pilot has decided to remove it.

The removal crosses the backend registry and probe, project runtime selection
parsing, the strict profile schema and both shipped profiles, the orchestrator's
catalogue fan-out, the browser's runtime controls, tests and fixtures, seven
baseline specifications, the reference architecture and design, guidance skills,
and ADR history.

## Goals / Non-Goals

**Goals:**

- Make Claude and OpenCode the complete selectable backend set.
- Make enforceable profile tool policy a precondition of selectability, so the
  Codex exemption cannot reappear as a per-backend special case.
- Move the profile default and the unselected-agent fallback to Claude.
- Remove all executable Codex integration and its dedicated test surface.
- Make active specs and documentation describe only the remaining system.

**Non-Goals:**

- Retire Codex as a *repository-development assistant*. `.codex/config.toml`,
  `AGENTS.md`, and the assistant-portability goal are untouched; this change is
  about the runtime backend the floor opens for shop agents.
- Change the portable `AgentBackend` protocol or the remaining adapters.
- Add OpenCode tables to profiles; ADR 0012's bounded adapter-owned
  compatibility exception remains in force.
- Migrate existing projects automatically or rewrite archived changes, sprint
  records, or historical ADR bodies.

## Decisions

1. **Remove Codex rather than keep it with a documented warning.** A backend
   that ignores declared tool policy makes `scoped-agent-tools` conditional on
   which backend a project happened to name, and the condition is invisible in
   the project's own `pyproject.toml`. Keeping Codex behind a warning was
   rejected because the shop cannot verify the warning was read; keeping it
   behind an opt-in flag was rejected because it preserves the same hole for the
   cost of another control surface.

2. **Make Claude the profile default and the unselected-agent fallback.** Claude
   is the other profile-explicit backend: it already carries model, effort,
   tools, and permission per agent in both shipped profiles, so the fallback
   moves without inventing new declarations. OpenCode was rejected as the
   default because it has no profile table by design — ADR 0012 keeps its policy
   adapter-owned, so it cannot supply a profile-declared default.

3. **Collapse the profile backend set to Claude alone.** `PROFILE_BACKENDS`
   becomes `("claude",)` and each agent declares exactly one runtime table.
   Retaining the map shape (rather than flattening `backends` into inline agent
   fields) keeps the manifest ready for a future second profile-explicit backend
   and avoids a second breaking profile-schema change.

4. **Turn the Codex exemption into a selectability rule.** `scoped-agent-tools`
   loses its "Role selects codex" scenario and gains a requirement that every
   selectable backend enforces its profile-declared tool policy, and that a
   backend which cannot is not selectable. This states the reason for the
   removal as a durable contract instead of a one-time deletion.

5. **Reject `codex:` selections loudly.** Project values naming `codex` fail
   preparation with the same "unknown backend" error path as any other unknown
   name, before any project or backend side effect. Silently substituting Claude
   was rejected: the project's declared model and effort would not survive the
   substitution, and the maker would not learn their selection was ignored.

6. **Preserve history but remove active claims.** ADR 0025 records the
   retirement and amends the Codex-specific portions of ADRs 0006, 0011, 0017,
   0018, 0022, and 0023. ADR 0005 is already superseded by 0006 and needs no
   status change. Archived OpenSpec changes, sprint evidence, and
   `docs/shop-history.md` remain historical records.

7. **Use negative contract tests for the breaking removal.** Before deleting the
   implementation, tests assert that backend creation, the probe set, project
   selection parsing, and profile validation no longer accept or require Codex.
   Those assertions supply the red state; deleting the Codex code and tables
   turns them green.

## Risks / Trade-offs

- **A project's `pyproject.toml` declares `codex:<model>`** → The run exits with
  an error naming that agent key and value. Migration is one edited line to a
  Claude or OpenCode selection; the error text points at it.
- **Losing access to OpenAI models** → OpenCode reaches them through a provider
  that honours the tool policy. The shop keeps a route to those models; it stops
  keeping an unconstrainable one.
- **The single-entry `PROFILE_BACKENDS` invites a shortcut that hardcodes
  Claude** → Keep validation iterating the declared map, and keep the
  orchestrator routing on resolved runtime data rather than a backend name, as
  `shop-agent-backend` already requires.
- **Deleting Codex-heavy test modules hides unrelated coverage** →
  `tests/test_orchestrator.py` carries 133 Codex references, most of them fixture
  wiring for backend-neutral behavior. Re-point those cases at the fake Claude or
  generic fake backend instead of deleting them, and run the complete suite.
- **Active Codex references survive in less obvious surfaces** → Search the
  tracked tree after implementation and classify every survivor as either a
  historical record or a repository-development-assistant reference.

## Migration Plan

1. Add failing contract tests for the selectable backend set, project selection
   parsing, and the profile schema.
2. Remove Codex registration, the adapter, probe entry, catalogue fan-out entry,
   preparation constants and parsing, profile schema entries, and both profiles'
   Codex tables; move the resolution fallback to Claude.
3. Re-point backend-neutral orchestrator and lifecycle tests at a remaining
   fixture; delete the Codex fixtures and Codex-only cases.
4. Remove the Codex entries and provider mapping from the floor browser.
5. Record ADR 0025, amend the affected ADRs and the index, and update the
   architecture overview, README, AGENTS.md, guidance skills, role prompts, and
   reference design.
6. Sync the seven delta specifications into their baselines and run the complete
   suite plus strict OpenSpec validation.

## Open Questions

None. The pilot has directed the removal; the fallback move to Claude follows
from Decision 2 and is recorded here as the working assumption.
