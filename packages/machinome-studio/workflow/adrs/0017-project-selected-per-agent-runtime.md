# ADR 0017: Select backend, provider, model, and reasoning level per agent from the project

**Status:** Accepted (amended by ADRs 0019 and 0024)

**Date:** 2026-08-09

**Deciders:** Pilot

**Origin:** OpenSpec change `project-selected-agent-runtime`

**Amends:** [ADR 0011](./0011-profile-defined-shop-runtime.md)
and [ADR 0012](./0012-bounded-opencode-compatibility-policy.md)

## Context

ADR 0011 made runtime topology, prompts, skills, and backend policy properties
of a repository-owned profile, validated before any project side effect. ADR
0006 introduced `--backend` as the way to pick which of those declared backend
tables a run would use. Together they place every runtime choice in the shop:
the profile says what the models are, the flag says which column of the table to
read, and the project says nothing at all.

That arrangement has two consequences the pilot no longer accepts. The first is
that a project is not a durable statement of how it was built — the same
launcher command produces different work depending on a flag someone typed, and
nothing in the project records which model machined it. The second is that model
choice is expressed at the wrong granularity: a maker may want one project's
Designer on a reasoning-heavy model and its Machinist somewhere cheaper, which a
single run-wide flag cannot express at all.

There is also a latent modelling error. A model name is only meaningful relative
to a backend and, for OpenCode, a provider; a reasoning level is only meaningful
relative to a model. The current schema splits those across a flag and table
keys, which permits combinations that cannot be executed.

## Decision

Backend, provider, model, and reasoning level SHALL be one inseparable per-agent
value, selected by the active project.

The value SHALL be a single colon-delimited string: `backend:model` where the
backend has one provider, `backend:provider:model` where it does not, with an
optional reasoning level as a final segment in either form. The backend named in
the first segment SHALL determine how the remaining segments are read, so Codex
and Claude admit two or three segments and OpenCode admits three or four. A
backend that cannot enforce a reasoning level SHALL reject a value that names
one. The parts SHALL NOT be declarable separately or in separate files, and a
reasoning level SHALL NOT be declarable as a key of its own.

Selections SHALL live in the project's `pyproject.toml` under
`[tool.solid-node-studio.agents]`, keyed by profile agent ID. That table is
shop-owned and distinct from the framework's `[tool.solid-node]`. The project
file is the record: the shop SHALL NOT write a separate manifest, run log, or
benchmark artifact.

Profiles SHALL continue to declare Codex and Claude runtime tables, which serve
as defaults. An agent the project does not name SHALL open on Codex with its
profile-declared model and effort, and an agent whose selection omits the
reasoning level SHALL keep its profile-declared effort. OpenCode SHALL have no
profile default and SHALL be reachable only by explicit project selection.

Project selection SHALL replace the model, supply the provider, and replace the
reasoning level when it names one. Tool policy and Claude permission SHALL remain
profile-owned and SHALL NOT be project-selectable.

`--backend` SHALL be removed. Runtime selection SHALL NOT be available as a
launcher option or environment variable.

Pilot-authored project *configuration* SHALL be trusted to select runtime.
Project *guidance text*, including a project's root `AGENTS.md` carried as
supplemental session instruction, SHALL NOT redefine runtime, identity,
topology, authority, skills, effort, tool permissions, or repository boundaries.

## Alternatives considered

### Keep `--backend` and add project-level model overrides

Rejected. Two sources of truth for the same value is the problem being solved,
and a run-wide flag cannot express the per-agent split that motivated the
change. A deprecation window was also rejected for the same reason: during it,
the flag and the project file could disagree.

### Declare `backend`, `provider`, `model`, and `effort` as separate keys

Rejected. They are not independently meaningful, and separating them makes
invalid combinations representable — a Claude model under the Codex backend, a
provider for a backend that has one, or a reasoning level a model cannot take. A
single string whose segment count is fixed by the backend makes those states
unrepresentable.

This inverts the reasoning of the archived `profile-defined-shop-runtime`
design, which chose structured TOML over a `claude:sonnet[medium]` string. That
reasoning holds for a *set* of independent controls the loader must check for
completeness. It does not hold for one value with internal structure.

### Mark the reasoning level with a second separator

Rejected as the primary form. `codex:gpt-5.6-terra[high]` needs no backend
lookup to parse, but it introduces a second piece of syntax for what is one
value, and `[medium]` is the exact notation the archived design rejected.
Position is unambiguous for every backend the shop supports, and switching later
is a contained change to the parser and the grammar requirement.

### Move all runtime settings, including tools and permission, into the project

Rejected. The line falls at what a control governs. Model and reasoning level
determine how much thinking a role is given and what it costs, which is a
per-project judgement and the reason this change exists. Tool policy and Claude
permission govern what a role may touch, and the profile is the trusted,
shop-owned profile package that ADR 0011 established to hold exactly that.

### Give OpenCode a profile default like Codex and Claude

Rejected by the pilot. OpenCode's provider and model space is open, so a shipped
default would encode one operator's authenticated configuration into a
shop-owned profile package. Leaving it selection-only keeps ADR 0012's inherited
operator default as the no-configuration behaviour.

## Consequences

### Positive

- A project's `pyproject.toml` states what built it, per agent, durably and
  without a separate artifact — including how hard each role was asked to think.
- One project can run different agents on different models, reasoning levels,
  and backends.
- Invalid backend/provider/model/level combinations are unrepresentable rather
  than caught late.
- OpenCode gains a selectable provider and model for the first time.

### Negative and trade-offs

- **BREAKING.** Every invocation, script, and document using `--backend` must
  move the selection into the project file.
- Profile validation ordering becomes subtler: the launcher must read the
  project's `pyproject.toml` before validating the profile, so ADR 0011's
  "validate before any project side effect" guarantee now depends on that read
  being genuinely side-effect-free.
- Codex and Claude models validate against closed sets; OpenCode models can only
  be shape-checked, so an OpenCode typo surfaces at open time rather than during
  validation.
- The reasoning-level segment is uniform in the grammar but not in its accepted
  values: Codex admits a wider set than Claude, and OpenCode may admit none at
  all. A maker reading the grammar cannot infer which levels a given backend
  takes without the error message telling them.
- A project carrying selections for several profiles' rosters has keys that are
  inert under any one profile. They are reported rather than rejected, because
  rejecting them would bind a project to a single profile.

### Neutral

- Profile topology, prompts, skills, and containment rules are unchanged.
- ADR 0012's compatibility policy remains operative wherever a project selects
  no OpenCode provider and model; it is narrowed, not superseded.
- The framework's `[tool.solid-node]` table is untouched.
