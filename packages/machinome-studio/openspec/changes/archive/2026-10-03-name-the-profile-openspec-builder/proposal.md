## Why

One hour after the change `ship-openspec-as-the-default-profile` renamed the
direct profile `builder` to `openspec` and made it the shop default (ADR
0034), the pilot rejected the name on 3 October 2026. A profile called
`openspec` whose maker-facing agent is called "Builder" does not say one
thing: the hub offers "OpenSpec", the conversation answers as "Builder".
And `profiles/openspec/` reads like an OpenSpec record directory, which in
this repository and in every Builder project means something else. The
pilot's direction: "Let's call it openspec-builder and 'OpenSpec Builder'
facing name."

## What Changes

- **BREAKING** The profile `openspec` is renamed `openspec-builder`:
  `profiles/openspec/` becomes `profiles/openspec-builder/`, and every use
  of `openspec` that means the profile becomes `openspec-builder`. A project
  declaring `profile = "openspec"`, or the earlier `builder`, is refused the
  way any profile the shop does not ship is refused, naming its
  `pyproject.toml` and the value; it is never opened under the default.
  There is no alias, compatibility path, migration tool or warning.
- `openspec-builder` is the shop default: a project that declares no
  profile opens under it, and the hub lists such a project under it.
- The maker-facing name of the profile's one agent becomes
  `OpenSpec Builder` everywhere a maker sees it: the agent's display label
  in the profile (so the roster, the Agents area and the conversation
  attribution, which derive from it), the hub's "New project" sheet choice
  (labelled `OpenSpec Builder`, described "One agent keeping the project's
  design in an OpenSpec record"), the agent prompt's self-introduction, the
  manual, the architecture overview and the changelog.
- The agent's internal identity does not change: agent ID `builder`,
  `user_agent = "builder"`, prompt file `builder.md` with frontmatter
  `name: builder`, and the `builder` key of a project's
  `[tool.machinome-studio.agents]` table all keep working. In specs and
  prose "Builder" remains the agent's short name.
- `fordesmac` is untouched: label "Fordesmac", description "Four-agent
  mechanical shop", prompts and roster. No `--profile` option.
- ADR 0034 is revised in place, not superseded: titled "Ship the OpenSpec
  Builder profile as the default", its decision names `openspec-builder`
  and the label `OpenSpec Builder`, and a dated Revision section records
  that the name `openspec` lasted one hour and why it was rejected.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-runtime-profile`: the shop default and the shipped direct profile
  become `openspec-builder`; its agent's display label becomes
  `OpenSpec Builder` (agent ID still `builder`); the shared-skill symlink
  path and the `OpenSpec` capability statement name `openspec-builder`.
- `project-runtime-selection`: a project declaring no profile opens under
  `openspec-builder`; the former names are instances of the existing
  refusal of a profile the shop does not ship; the two-roster and
  changed-profile scenarios name `openspec-builder`.
- `shop-project-hub`: the creation sheet preselects the OpenSpec Builder
  choice, labelled `OpenSpec Builder`, and still offers Fordesmac; a project
  declaring no profile is listed under `openspec-builder`.
- `named-project-bootstrap`, `shop-agent-backend`, `shop-agent-lifecycle`,
  `shop-agent-messaging`, `shop-browser-workspace`, `shop-floor-lifecycle`,
  `shop-user-conversation`: scenarios that name `openspec` as the profile
  name `openspec-builder`; their outcomes for Builder the agent are
  unchanged.

## Impact

Studio only. Code: `floor/profiles.py` (default), `floor/preparation.py`
(the two hub-listing fallbacks), `floor/backends/probe.py` (the shipped
profiles whose models are reported), `floor/frontend/src/main.tsx` (the
sheet's profile state, its listing fallback, its choice values, labels and
description) with its regenerated build, the profile package directory,
its `profile.toml` label and `builder.md`'s self-introduction and
description line. Tests: every module that loads or pins the profile
`openspec`, every assertion or fixture carrying the agent label `Builder`
(the floor refuses a manifest whose label does not match the active
profile), the browser strings, and the documentation pins. Records: ADR
0034 and its index row, `docs/architecture-overview.md`, `AGENTS.md`,
`CHANGELOG.md`, the manual pages that name the profile or its agent, and
one provisional note under `workflow/ongoing/`.

Projects outside the repository that declare `profile = "openspec"` (or
still `builder`) stop opening until their declaration names
`openspec-builder`; the studio does not edit them, and the mechanical
projects catalogue is not touched by this change. No framework, viewer,
shop-skill, publication or push is involved.
