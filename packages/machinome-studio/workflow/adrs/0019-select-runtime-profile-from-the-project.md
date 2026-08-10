# ADR 0019: Select the runtime profile from the project

**Status:** Accepted

**Date:** 2026-08-09

**Deciders:** Pilot

**Origin:** OpenSpec change `project-selected-runtime-profile`

**Amends:** [ADR 0011](./0011-profile-defined-shop-runtime.md)
and [ADR 0017](./0017-project-selected-per-agent-runtime.md)

## Context

ADR 0011 made the runtime profile a trusted, shop-owned package selected
by `--profile`, with `builder` as the fallback. ADR 0017 then moved backend,
provider, model, and reasoning selection into each project's `pyproject.toml`
so the project durably states how its agents normally run. The profile still
comes only from an invocation, even though its roster is a larger fact about how
the project is worked than any one agent's model.

A project normally uses one roster, but a pilot also has legitimate reasons to
open it under another roster for one run. The launcher must also open a newly
scaffolded project under a non-default roster before that project has a file in
which to declare one. Separately, Fordesmac is now the shop's intended default;
the prior Builder fallback no longer represents the normal operating mode.

## Decision

The shop SHALL accept a `profile` string in the project's
`[tool.solid-node-studio]` table, beside the existing `agents` table. Both floor
entry points SHALL select exactly one profile using this precedence:

1. `--profile <id>` when supplied;
2. the active project's declared `profile`; or
3. the shop default `fordesmac`.

The option remains an intentional one-run override and SHALL NOT modify the
project. A scaffold SHALL remain silent: it SHALL NOT write a profile or a shop
runtime table.

Project parsing SHALL always reject a profile value that is not a string or is
not lowercase kebab-case, even when an option overrides it. Resolution against
the running shop's `profiles/` packages SHALL occur only for the selected
value. Therefore, a well-formed but unavailable project declaration fails with
an error naming its `pyproject.toml` and value when used, but remains tolerable
when a valid option overrides it. The launcher SHALL never replace an
unavailable declared profile with the shop default.

Declaring a profile selects one trusted shop-owned package in its
entirety. Tool policy and Claude permission remain profile-owned and cannot be
selected, widened, narrowed, or authored independently by the project. Whether
topology and policy should eventually be separate packages remains out of scope.

Changing the fallback from `builder` to `fordesmac` is accepted as an
independent decision in this ADR. It would stand even without project-declared
profiles.

## Alternatives considered

### Remove `--profile` and make the project the only source

Rejected. A new scaffold has no shop configuration yet, so its first run could
not select a non-default roster. The option is also useful for a deliberate
one-run roster change, such as opening a normally delegated project under one
Builder for a focused repair.

### Fail when the option and project disagree

Rejected. Disagreement is the override's intended purpose; rejecting it would
retain two sources while removing the useful reason to keep the option.

### Resolve every project declaration even when overridden

Rejected. Shape is intrinsic and must always be valid, but package availability
depends on the current shop install. A valid explicit run should not fail for an
unused declaration that another install may provide.

### Warn whenever an unavailable declaration is overridden

Rejected. It would add noise to every legitimate override. The declaration is
reported as soon as a run actually selects it.

## Consequences

### Positive

- A project's normal roster is durable and travels with its per-agent runtime
  selections.
- Both entry points share one explicit option/project/default precedence chain.
- Missing project-selected packages fail loudly and point to the file the pilot
  must edit.
- One-run roster overrides and first-run bootstrapping remain possible.

### Negative and trade-offs

- **BREAKING.** A bare invocation for a project with no declaration now opens
  four Fordesmac sessions instead of one Builder session.
- A project that declares a profile is less portable to a shop installation
  that does not ship that profile unless the pilot supplies an available
  override.
- A typo in a well-formed project profile can remain undiscovered while every
  run deliberately overrides it.
- Selecting a profile indirectly selects its tool and permission policy because
  those concerns remain packaged together.

### Neutral

- Profile contents, topology validation, prompts, skills, and agent runtime
  resolution remain unchanged.
- Agent selections outside an overridden profile's roster remain ignored and
  reported.
- The framework's `[tool.solid-node]` table is untouched.
