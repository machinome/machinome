## Why

On 3 October 2026 the pilot decided that the studio's normal mode is one
agent keeping the project's design in an OpenSpec record, and that the
profile carrying that discipline is named for it: `builder` becomes
`openspec` and becomes the shop default. The delegated four-agent
`fordesmac` roster stays, unchanged, as the delegation evidence. Today a
project that declares no profile opens four Fordesmac sessions (ADR 0019),
and the hub's "New project" sheet preselects nothing, so the normal mode is
neither the default nor named for what it is.

## What Changes

- **BREAKING** The profile `builder` is renamed `openspec`:
  `profiles/builder/` becomes `profiles/openspec/` and its identifier
  becomes `openspec` wherever it means the profile. A project that still
  declares `profile = "builder"` is refused the way any unavailable profile
  is refused today, naming its `pyproject.toml` and the value; it is never
  opened under the default. There is no alias, no compatibility path, no
  migration tool and no warning path.
- The profile's one agent is not renamed: it keeps the id `builder`, the
  label `Builder`, the prompt `builder.md` and `user_agent = "builder"`,
  the way Fordesmac's agents keep their names. Agent keys `builder` in a
  project's `[tool.machinome-studio.agents]` table keep working.
- **BREAKING** The shop default becomes `openspec`: a project that declares
  no `profile` opens one Builder session instead of four Fordesmac sessions,
  and the hub lists such a project under `openspec`.
- The hub's "New project" sheet preselects OpenSpec, labelled `OpenSpec`
  with a one-line description of what it is, and still offers Fordesmac.
- `fordesmac` is untouched, prompts included.
- Correction: the Agents area's Session panel reports the profile's real work
  mode (`openspec · direct`, `fordesmac · delegated`) instead of reporting
  every profile as delegated, a defect that would otherwise sit on the new
  default view.
- No `--profile` launcher option is reintroduced; the project's declaration
  and the shop default remain the only two sources.
- ADR 0034 records the decision, amending ADR 0019 (the fallback) and ADR
  0011 (the profile's name). The architecture overview, the operating
  contract, the manual and the changelog are brought to the new state.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-runtime-profile`: the shop default becomes `openspec`; the shipped
  direct profile is `openspec` (with Builder as its agent) and is the one
  declaring the `OpenSpec` capability.
- `project-runtime-selection`: a project declaring no profile opens under
  `openspec`; a project declaring a profile the shop no longer ships, such as
  `builder`, is refused, never replaced by the default; the two-roster
  scenarios name the `openspec` profile.
- `shop-project-hub`: the creation sheet preselects OpenSpec and still
  offers Fordesmac; a project declaring no profile is listed under
  `openspec`.
- `named-project-bootstrap`, `shop-agent-backend`, `shop-agent-lifecycle`,
  `shop-agent-messaging`, `shop-browser-workspace`, `shop-floor-lifecycle`,
  `shop-user-conversation`: scenarios that name `builder` as the profile
  name `openspec`; their Builder-the-agent outcomes are unchanged.

## Impact

Studio only. Code: `floor/profiles.py` (default), `floor/preparation.py`
(hub listing fallback), `floor/backends/probe.py` (profiles whose models are
reported), `floor/app.py` (the run snapshot carries the work mode), the
profile package directory, and the hub sheet and Session panel in
`floor/frontend/src/main.tsx` with its regenerated build. Tests across the
profile, selection, preparation, open, API, role-contract, OpenSpec-tool,
backend, broker, orchestrator, documentation and browser modules. Records:
ADR 0034 with the status lines of ADRs 0011 and 0019 and the ADR index,
`docs/architecture-overview.md`, `AGENTS.md`, `CHANGELOG.md`, the manual
pages that name the profile or the default, and one provisional note under
`workflow/ongoing/`.

Projects outside the repository that declare `profile = "builder"` stop
opening until their declaration is edited to `openspec`; the studio does not
edit them. The mechanical projects catalogue is not touched by this change.
No framework, viewer, shop-skill, publication or push is involved.
