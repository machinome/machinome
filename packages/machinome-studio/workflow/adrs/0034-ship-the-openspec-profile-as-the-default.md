# ADR 0034: Ship the OpenSpec profile as the default

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** Pilot

**Origin:** OpenSpec change `ship-openspec-as-the-default-profile`

**Amends:** [ADR 0019](./0019-select-runtime-profile-from-the-project.md)
(the shop default) and [ADR 0011](./0011-profile-defined-shop-runtime.md)
(the name of its direct profile)

## Context

ADR 0011 introduced declarative runtime profiles with two shipped packages:
`builder`, one direct agent, and `fordesmac`, a delegated team of four, and
made `builder` the fallback. ADR 0019 moved the selection into the project's
`[tool.machinome-studio]` table and, as an independent decision, changed the
fallback to `fordesmac`, then the intended normal mode. The `--profile`
option it kept was removed later by the change `open-projects-from-hub`; the
selection chain is now the project's declaration, otherwise the shop default.

Since ADR 0019 the direct profile has acquired its discipline: its one agent,
Builder, keeps the project's design in the project's own OpenSpec record,
planning each design change before building it (`builder-spec-discipline`,
ADR 0027). On 3 October 2026 the pilot decided that this is the studio's
normal mode: one shipped discipline, followed by one agent, is how a maker
works; the delegated Fordesmac roster is kept, unchanged, as the evidence of
what delegation costs and gives. A profile named after its agent does not say
what a maker chooses when choosing it; a profile named for its discipline
does.

## Decision

The direct profile SHALL be named `openspec`. Its package moves from
`profiles/builder/` to `profiles/openspec/`, and every use of `builder` that
means the profile becomes `openspec`. Its agent is not renamed: it keeps the
agent ID `builder`, the label `Builder`, the prompt `builder.md` and
`user_agent = "builder"`, as Fordesmac's agents keep theirs.

The shop default SHALL be `openspec`. A project that declares no `profile`
opens under it, and the hub lists such a project under it. The hub's "New
project" sheet SHALL open with OpenSpec chosen, labelled `OpenSpec` with a
one-line description, and SHALL still offer Fordesmac.

The shop SHALL NOT ship `builder` or resolve it to `openspec`. A project that
declares `profile = "builder"` is refused as any unavailable declared profile
is refused under ADR 0019, naming its `pyproject.toml` and the value, and is
never opened under the default. The studio adds no alias, compatibility
path, migration tool or warning for the old name.

`fordesmac` is unchanged. No per-run override is reintroduced. Everything
else ADR 0019 decided stands: the project's declaration governs, shape is
checked on every read, availability when opened, and an unavailable
declaration is never replaced by the default.

This replaces ADR 0019's decision "Changing the fallback from `builder` to
`fordesmac`" and ADR 0011's name for the direct profile; the rest of both
ADRs is unaffected.

## Alternatives considered

### Rename the agent with the profile

Rejected by the pilot. The agent is who the maker talks to; the profile is
the discipline it works under. Fordesmac already separates the two (profile
`fordesmac`; agents Foreman, Designer, Machinist, Librarian). Keeping the
agent ID also keeps every project's `[tool.machinome-studio.agents]`
`builder = ...` selection valid.

### Keep `builder` as an alias of `openspec`

Rejected by the pilot. An alias is a second name for one package that every
later reader has to know about, and the studio is unpublished: the projects
that declare `builder` are the pilot's own and are rewritten by hand.

### Keep `fordesmac` as the default and only rename

Rejected. The decision is that the OpenSpec discipline is the normal mode;
a default that opens four agents for a project that chose nothing contradicts
it.

## Consequences

### Positive

- A project that chooses nothing opens the studio's normal mode: one Builder
  keeping an OpenSpec record.
- The hub's choice says what is chosen: a discipline (OpenSpec) or a roster
  (Fordesmac).
- Agent selections keyed `builder` keep working under the renamed profile.

### Negative and trade-offs

- **BREAKING.** A project that declares `profile = "builder"` is refused
  until its declaration is edited to `openspec`. The studio neither edits it
  nor offers to.
- **BREAKING.** A project with no declaration now opens one Builder session
  instead of four Fordesmac sessions.
- The identifier `openspec` is also the name of the CLI the floor depends on
  (ADR 0027), of the `OpenSpec` capability and of a project's `openspec/`
  record; prose names the profile explicitly where the context is ambiguous.

### Neutral

- The profile's manifest, prompt, skills, tool policy and Claude defaults are
  unchanged by the move.
- `fordesmac`, its prompts and its exclusion from the `OpenSpec` capability
  are unchanged.
