## Context

Backend selection today is a single `--backend` flag (`floor/orchestrator.py:456`,
default `codex`) feeding two consumers: `load_profile(backend=...)`, which
collapses each agent's per-backend tables down to one `BackendRuntime` at load
time (`floor/profiles.py:149-153`), and `create_backend()`, which builds exactly
one adapter (`floor/orchestrator.py:407`). `ShopOrchestrator` then holds that one
adapter in `self.backend` and reaches for it at fourteen call sites, and `_serve`
consumes exactly one `backend.events` iterator in one `route_events` task.

Two other entry points hardcode the same value: `floor/__main__.py:33` and the
fallback profile load in `floor/app.py:119`.

Nothing in the shop reads a project file for configuration. A project's
`pyproject.toml` carries only `[tool.solid-node] model = "..."`, which the
framework reads to locate the model class. OpenCode has no model plumbing at all:
`PROFILE_BACKENDS` is `("codex", "claude")` and the loader requires exactly those
two keys, so an OpenCode table is currently *rejected*; the adapter's
`_prompt()` sends `agent` and `system` but no model, so OpenCode uses whatever
the authenticated operator default is.

The constraint driving this change is that a project should be a durable
statement of how it was built, including which model built each part of it, and
that one project may reasonably want its Designer and its Machinist on different
backends.

## Goals / Non-Goals

**Goals:**

- Backend, provider, model, and reasoning level are one per-agent value read
  from the project.
- A single run can open several backends concurrently.
- The project's `pyproject.toml` is the record; reading it tells you what built
  the project.
- Profile defaults still cover Codex and Claude models and effort, plus tools
  and permission for every agent.

**Non-Goals:**

- Any separate benchmark artifact, run log, or manifest. The `pyproject.toml`
  *is* the record; the shop writes nothing extra.
- Revisiting whole-backend failure semantics. Deferred by the pilot; see
  Open Questions.
- Project-selectable tool policy or Claude permission.
- OpenCode profile defaults.
- Any change to the broker, browser workspace, role prompts, shop skills, or the
  framework.

## Decisions

### D1 — One colon-delimited string, not separate keys

`<agent> = "opencode:anthropic:claude-sonnet-4-5:medium"`, dropping the provider
where the backend has one and dropping the reasoning level where the profile's
should stand:

```toml
[tool.solid-node-studio.agents]
foreman   = "codex:gpt-5.6-terra"
designer  = "opencode:anthropic:claude-sonnet-4-5:high"
machinist = "claude:sonnet:medium"
```

*Alternatives considered.* Separate `backend`, `provider`, `model`, and `effort`
keys per agent, or a project-level `backend` with per-agent models. Both were
rejected because the values are not independently meaningful: a model name is
only interpretable relative to its backend and provider, a reasoning level only
relative to the model, and separating them invites a project that names a Claude
model under the Codex backend. Keeping them in one string makes the invalid state
unrepresentable. Prior art in this repository runs the other way — archived
`2026-07-31-profile-defined-shop-runtime/design.md:86` chose structured TOML over
a `claude:sonnet[medium]` string precisely so the loader could validate
completeness — but that reasoning applies to a *set* of independent controls that
must each be present. Here there is one value with internal structure, which is
the case a string grammar suits.

Profile tables stay structured for the same reason, inverted: they carry tools
and permission alongside model and effort, so they remain a table.

### D1a — Position, disambiguated by the backend, rather than a second separator

Provider and reasoning level are both optional, so the grammar needs a way to
tell `codex:gpt-5.6-terra:high` from `opencode:anthropic:claude-sonnet-4-5`.
Position resolves it: the backend named in the first segment fixes whether a
provider is expected, and any remaining trailing segment is the reasoning level.
Codex and Claude admit two or three segments; OpenCode admits three or four.
Parsing therefore reads segment one, then knows the arity.

*Alternative considered.* A distinct separator for the reasoning level —
`codex:gpt-5.6-terra[high]` or `...@high` — which is self-describing and needs no
backend lookup to parse. Rejected as the primary form because it introduces a
second piece of syntax for what the pilot describes as one value, and because
`[medium]` is the exact notation the archived design rejected. The positional
form is unambiguous for every backend the shop supports, and both a wrong segment
count and an out-of-set value are caught by validation with the offending agent
key named. If a future backend has several providers *and* no reasoning control,
or the four-segment form proves hard to read in practice, switching to a bracketed
suffix is a contained change to the parser and the spec's grammar requirement.

### D2 — Selection lives in the project; defaults live in the profile

Codex and Claude keep their profile tables as defaults. OpenCode gets none: it is
reachable only by explicit project selection. This preserves the property that a
profile alone is a complete, runnable description of a floor — you can open any
project under any profile with no configuration — while making a deliberate
choice visible in the project that records it.

The precedence is one-directional and narrow: a project selection replaces the
*model*, supplies the provider, and replaces the *reasoning level* when it names
one. Tools and Claude permission resolve from the profile always. The line is
drawn at what a control governs rather than at what is convenient: model and
reasoning level determine how much thinking a role is given and cost what they
cost, which is the pilot's call per project, while tool policy and permission
govern what a role is allowed to touch, which belongs in the trusted,
repository-owned package that ADR 0011 established to hold it.

Effort is a default rather than a fixed value, so an agent whose selection omits
the trailing segment keeps its profile effort. That matters for readability: a
project that only wants a different model says so in two segments and inherits
the reasoning level the profile author chose for that role.

### D3 — Unknown agent keys are ignored and reported; unknown table keys are rejected

One project may be opened under several profiles with different rosters, so a
project legitimately carries selections for agents absent from the active roster.
Rejecting those would make a project usable under only one profile. Ignoring them
silently would make a misspelled agent ID inert with no signal, so the launcher
reports what it ignored.

Unknown *table* keys are the opposite case: there is no legitimate reason for one,
and silently ignoring `effort = "high"` would let a pilot believe they had set
something. Those are rejected, consistent with the profile loader's existing
`_only()` discipline.

### D4 — Read the project file before profile validation, without side effects

`shop-runtime-profile` requires profile validation to precede every project side
effect, and runtime selection now comes from the project — a genuine ordering
conflict. It is resolved by splitting what `prepare_project` does today into two
phases: a read phase (resolve and containment-check the path, parse one
`pyproject.toml` if present) and the existing side-effecting phase (scaffold,
`git init`, `solid viewer`, build). The read phase runs first, profile validation
and runtime resolution run next, and the side-effecting phase runs only after
both pass. Reading a file that may not exist is not a side effect, but the spec
has to say so explicitly rather than leave it to interpretation.

*Alternative considered.* Resolving runtime lazily, after preparation, at
`open_role()` time. Rejected: it would let an invalid selection scaffold a
repository and run a build before failing, which is exactly what the ordering
requirement exists to prevent.

### D5 — Resolution is a merge step, not a loader parameter

`load_profile()` loses its `backend=` parameter and `RuntimeProfile.backend`, and
stops collapsing to a single `BackendRuntime`. It validates *all* declared tables
and keeps them per agent. A separate resolution step then merges the project's
selections over those defaults and produces the effective per-agent runtime.

This is a better seam independently of this change: today the loader's behaviour
depends on which backend was selected, which is why the OpenCode special case had
to live inside it. After the split, the loader is a pure validator of a profile
package and the merge is the only thing that knows about projects.

### D6 — The orchestrator holds a backend per agent, and each backend once

`ShopOrchestrator.__init__` takes a mapping from agent ID to backend instance
rather than one backend. Construction instantiates each *distinct* selected
backend once — not one per agent — because backends already own their own process
cardinality under ADR 0008: Codex app-server is one process serving all its
roles, OpenCode is one server, Claude is one process per role. Routing an agent to
its owner is a dictionary lookup, so the orchestrator still branches on no backend
name and stays backend-neutral.

Three consequences follow mechanically. `start()` is called once per distinct
backend. `close()` releases every role session and then closes each distinct
backend exactly once, rather than closing `self.backend` after the role loop.
Event routing becomes one task per open backend, all feeding the single
`handle_event`, with `_wait_for_runtime` waiting on the delivery task plus N event
tasks.

### D7 — OpenCode's precedence sentence is amended, not deleted

`floor/backends/opencode.py:560-565` tells every OpenCode role that supplemental
project guidance "cannot redefine role identity, topology, authority, skills,
model, effort, tool permissions, or repository boundaries." Under this change a
project *can* set the model and the reasoning level, so that sentence becomes
false on two counts as written.

It is amended rather than dropped, because the two things it conflates are
genuinely different: `pyproject.toml` is pilot-authored configuration read by the
launcher before any agent starts, while a project's `AGENTS.md` is in-band text
arriving inside a model's context, where an injected instruction is
indistinguishable from a legitimate one. The amended contract keeps the ban on
guidance text redefining runtime and says the model and reasoning level were
already resolved from configuration and profile.

## Risks / Trade-offs

- **Removing `--backend` breaks every existing invocation and script** → It is a
  deliberate breaking change with a mechanical migration, spelled out in the
  removal's Migration note. There is no deprecation window: keeping a
  run-wide flag alongside per-agent selection would create two sources of truth
  for the same value, which is the problem being solved.

- **Testing gets harder: the e2e and orchestrator tests select a backend by flag
  today** → They gain a fixture project whose `pyproject.toml` carries the
  selection. This is more setup per test, but it exercises the real resolution
  path rather than a bypass, and the `--backend-command` test hook survives as a
  per-backend override.

- **`tests/test_runtime_profiles.py:93-113` mutates profile TOML by exact string
  replacement** → Those tests break wholesale and need rewriting against the new
  loader signature. Unavoidable; the loader's interface is changing.

- **A mixed-backend run has more failure surface than a single-backend one** →
  Role-scoped failure and recovery already work per role and are unaffected.
  Whole-backend failure is deferred and keeps today's fatal behaviour, which is
  conservative rather than silently degraded.

- **OpenCode model values cannot be validated against a closed set** → Codex and
  Claude validate against `_CODEX_MODELS` and `_CLAUDE_MODELS`; OpenCode's
  provider and model space is open, so it gets shape validation only. The
  asymmetry is real and is stated in the spec rather than hidden, so a typo in an
  OpenCode model surfaces as a backend error at open time rather than a
  validation error before it.

- **Reasoning levels are not one set across backends** → Codex admits
  `_EFFORTS` (`low` through `ultra`) and Claude admits only `_CLAUDE_EFFORTS`
  (`low`, `medium`, `high`). The grammar is uniform but validation is per
  backend, so `claude:sonnet:ultra` is rejected while `codex:...:ultra` is not.
  That is the existing profile-loader behaviour rather than something new; the
  grammar simply makes it reachable from a project.

- **OpenCode may not be able to enforce a reasoning level at all** → Whether a
  reasoning control exists is provider-dependent there, and the shop's standing
  rule is to reject a control a backend cannot enforce rather than accept and
  ignore it. If verification shows no enforceable control, the four-segment
  OpenCode form is rejected and OpenCode selections stay at three segments. The
  spec is written to hold either way; the implementation task settles which.

- **The exact wire format for a model and reasoning level in OpenCode's
  `prompt_async` body is unverified** → Confirm both against current OpenCode
  documentation before implementing `_prompt()`; do not infer them from the
  config file's `provider/model` string form.

## Migration Plan

1. Land the reader, resolution, and multi-backend orchestrator with `--backend`
   still accepted as an override, so the suite stays green while call sites move.
2. Convert tests and fixture projects to project-declared selection.
3. Remove `--backend`, `RuntimeProfile.backend`, and the `backend=` parameter.
4. Update `README.md`, `skills/running-the-shop/SKILL.md`, and
   `docs/architecture-overview.md`.

Steps 1–3 are sequenced only to keep the suite runnable; the flag must not
survive into the final commit. Rollback is reverting the cycle, since no
persistent state or artifact is created by this change.

## Open Questions

- **What does whole-backend failure mean on a mixed-backend floor?** Today
  `backend_failed` raises and ends the run (`floor/orchestrator.py:263-264`).
  With several backends open, killing every role because one adapter died is
  probably wrong, but leaving a permanently dead role on an open floor is a state
  the broker cannot express. The natural extension is demoting `backend_failed`
  to `role_failed` for every role on that backend so the existing recovery path
  re-opens them, but that changes ratified recovery behaviour. Deferred by the
  pilot; this change preserves the current fatal behaviour exactly.
