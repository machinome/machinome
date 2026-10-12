# ADR 0034: Ship the OpenSpec Builder profile as the default

**Status:** Accepted

**Date:** 2026-10-03

**Revised:** 2026-10-03 (see [Revision](#revision))

**Deciders:** Pilot

**Origin:** OpenSpec change `ship-openspec-as-the-default-profile`, revised
by the OpenSpec change `name-the-profile-openspec-builder`

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
what delegation costs and gives. A profile named after its agent alone does
not say what a maker chooses when choosing it; a profile named for its
discipline and its agent together does.

## Decision

The direct profile SHALL be named `openspec-builder`. Its package lives at
`profiles/openspec-builder/`, and every use of `builder` that meant the
profile becomes `openspec-builder`. Its one agent SHALL be shown to the
maker as `OpenSpec Builder`: that is the agent's display label, and with it
the name the roster, the Agents area and the conversation give the agent,
the name the agent's prompt introduces it by, and the label of the profile's
choice in the hub. The agent's internal identity is unchanged: agent ID
`builder`, prompt `builder.md` with `name: builder`, and
`user_agent = "builder"`, so every project's
`[tool.machinome-studio.agents]` `builder = ...` selection keeps applying.

The shop default SHALL be `openspec-builder`. A project that declares no
`profile` opens under it, and the hub lists such a project under it. The
hub's "New project" sheet SHALL open with OpenSpec Builder chosen, labelled
`OpenSpec Builder` with a one-line description, and SHALL still offer
Fordesmac.

The shop SHALL NOT ship `builder` or `openspec`, nor resolve either to
`openspec-builder`. A project that declares one of them is refused as any
unavailable declared profile is refused under ADR 0019, naming its
`pyproject.toml` and the value, and is never opened under the default. The
studio adds no alias, compatibility path, migration tool or warning for
either former name.

`fordesmac` is unchanged. No per-run override is reintroduced. Everything
else ADR 0019 decided stands: the project's declaration governs, shape is
checked on every read, availability when opened, and an unavailable
declaration is never replaced by the default.

This replaces ADR 0019's decision "Changing the fallback from `builder` to
`fordesmac`" and ADR 0011's name for the direct profile; the rest of both
ADRs is unaffected.

## Alternatives considered

### Name the profile `openspec` and keep the agent's label `Builder`

Adopted first and rejected by the pilot one hour later; see
[Revision](#revision).

### Rename the agent's ID with the profile

Rejected. The ID is internal; the maker never types it, and renaming it
would silently stop every project's `builder = ...` agent selection from
applying. The facing name changes through the label alone.

### Keep `builder` or `openspec` as an alias of `openspec-builder`

Rejected. An alias is a second name for one package that every later
reader has to know about, and the studio is unpublished: the projects that
declare either name are the pilot's own and are rewritten by hand.

### Keep `fordesmac` as the default and only rename

Rejected. The decision is that the OpenSpec discipline is the normal mode;
a default that opens four agents for a project that chose nothing contradicts
it.

## Consequences

### Positive

- A project that chooses nothing opens the studio's normal mode: one agent,
  OpenSpec Builder, keeping an OpenSpec record.
- The maker meets one name for the direct profile and its agent: the hub's
  choice, the roster and the conversation all say `OpenSpec Builder`.
- The profile's package directory no longer reads like an `openspec/`
  record directory.
- Agent selections keyed `builder` keep working under the renamed profile.

### Negative and trade-offs

- **BREAKING.** A project that declares `profile = "builder"` or
  `profile = "openspec"` is refused until its declaration is edited to
  `openspec-builder`. The studio neither edits it nor offers to.
- **BREAKING.** A project with no declaration now opens one OpenSpec Builder
  session instead of four Fordesmac sessions.
- The facing name is longer than "Builder" in narrow places: the roster row,
  the Agents-area title and the conversation attribution.

### Neutral

- The profile's prompt changes only in how the agent introduces itself; its
  skills, tool policy and Claude defaults are unchanged.
- `fordesmac`, its label, its prompts and its exclusion from the `OpenSpec`
  capability are unchanged.

## Revision

**2026-10-03.** As first accepted, this decision named the direct profile
`openspec` (package `profiles/openspec/`) and kept its agent's label
`Builder`, with the hub's choice labelled `OpenSpec`. That name lasted one
hour. The pilot rejected it on the same day for two reasons: a profile
called `openspec` whose maker-facing agent is called "Builder" gives the
maker two names for one choice, and `profiles/openspec/` reads like an
OpenSpec record directory, which in this repository and in every project the
agent works in means something else. In the pilot's words: "Let's call it
openspec-builder and 'OpenSpec Builder' facing name." The decision above is
revised in place accordingly (change `name-the-profile-openspec-builder`):
the profile ID is `openspec-builder`, the agent's label and the hub's choice
are `OpenSpec Builder`, and `openspec` joins `builder` as a former name the
shop refuses. The default, the refusal rule and everything else this ADR
decided are unchanged.
