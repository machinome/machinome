## Why

The backend that runs a shop floor is chosen at the command line, applies to
every agent at once, and is unrecorded anywhere after the run ends. A project is
therefore not a durable statement of how it was built: the same
`python -m floor.orchestrator gearbox --profile fordesmac` produces different
work depending on a flag the pilot happened to type, and nothing in the project
says which model machined it.

Model choice is a property of the project, not of the invocation. A maker wants
one project's Designer on a reasoning-heavy model while its Machinist runs
somewhere cheaper, wants that split to survive across sessions and machines, and
wants to read the project's own `pyproject.toml` to know what built it. None of
that is expressible today, and the single `--backend` flag actively prevents the
mixed-backend case.

## What Changes

- **BREAKING** Remove the `--backend` flag from the orchestrator. The backend is
  no longer selectable at the command line by any value, including the current
  `codex` default.
- Read runtime selection from the active project's `pyproject.toml` under a new
  `[tool.solid-node-studio]` table, owned by the shop and distinct from the
  framework's `[tool.solid-node]`.
- Select backend, provider, model, and reasoning level **per agent** as one
  inseparable value, written `backend:model` where the backend has a single
  provider and `backend:provider:model` where it does not, with an optional
  trailing reasoning level in either form. An agent the project does not name
  falls back to Codex with the profile's declared model and effort.
- **BREAKING** Allow one floor to run several backends at once. The orchestrator
  stops owning a single backend instance and instead opens each distinct
  selected backend once, routing every role to the instance that owns it.
- Give OpenCode a provider and model for the first time. It has no profile
  defaults and gains none; a project that names an OpenCode triple gets it, and
  a project that does not keeps today's inherited operator default.
- Keep profile runtime tables as the defaults for Codex and Claude only,
  supplying model and effort for any agent the project does not select, and keep
  tool policy and Claude permission profile-owned and not project-overridable.

Deferred deliberately: what a whole-backend failure means when other backends on
the same floor are healthy. The current fatal behaviour is preserved unchanged.

## Capabilities

### New Capabilities
- `project-runtime-selection`: the `[tool.solid-node-studio]` schema, the
  `backend:provider:model:effort` grammar, per-agent resolution against the
  active profile's roster, defaults for unnamed agents and absent projects, and
  the precedence boundary between pilot-authored project configuration and
  untrusted project guidance text.

### Modified Capabilities
- `shop-agent-backend`: backend selection moves from the `--backend` flag to
  project configuration; session ownership becomes per-agent rather than
  per-run; OpenCode's adapter-owned compatibility defaults narrow to apply only
  when the project names no OpenCode triple.
- `shop-runtime-profile`: profile runtime tables become model and effort
  defaults for Codex and Claude that a project may override, rather than the
  sole authority; profile
  validation no longer resolves a single selected backend; the
  validation-ordering requirement admits a side-effect-free read of project
  configuration before profile validation.
- `shop-floor-lifecycle`: opening scenarios stop naming `--backend`.

## Impact

Code: `floor/orchestrator.py` (flag removal, per-agent backend map across all
fourteen `self.backend` call sites, one event-routing task per backend, close
each backend exactly once), `floor/profiles.py` (`RuntimeProfile.backend` and
the `backend=` parameter removed, the single-`BackendRuntime` collapse replaced
by a per-agent merge, `provider` added to `BackendRuntime`),
`floor/preparation.py` (project configuration reader), `floor/backends/__init__.py`
(per-backend command override), `floor/backends/opencode.py` (send a resolved
model; adjust the project-guidance precedence sentence in the system contract),
`floor/__main__.py` and `floor/app.py` (hardcoded `backend="codex"`).

Docs: `README.md`, `skills/running-the-shop/SKILL.md`,
`docs/architecture-overview.md`. New ADRs for project-owned per-agent runtime
selection and for multi-backend orchestration; ADR 0012 narrowed rather than
superseded.

Tests: `tests/test_runtime_profiles.py` (heaviest — the TOML mutation tests),
`tests/test_orchestrator.py`, `tests/test_opencode_backend.py`,
`tests/test_broker.py`, `tests/test_role_contracts.py`,
`tests/test_shop_lifecycle_e2e.py`.

No change to the broker, browser workspace, role prompts, shop skills, or the
framework.
