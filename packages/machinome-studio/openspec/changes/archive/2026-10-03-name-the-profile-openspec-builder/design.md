## Context

The change `ship-openspec-as-the-default-profile` (archived 3 October 2026,
ADR 0034) renamed the direct profile `builder` to `openspec`, made it the
shop default, and deliberately left its agent alone: agent ID `builder`,
label `Builder`. The hub's creation sheet offered the profile as `OpenSpec`,
described "One agent, Builder, keeping an OpenSpec design record".

The pilot rejected that naming within the hour. From the maker's side it is
two names for one thing: the sheet says "OpenSpec", the roster and the
conversation say "Builder". From the repository's side `profiles/openspec/`
reads like an OpenSpec record directory (`openspec/`), a name this
repository and every project Builder works in already use for something
else. The pilot fixed both: the profile ID is `openspec-builder`, and the
name the maker sees is `OpenSpec Builder`.

Where the profile name lives today (tree at `14fcbf1`):

- `floor/profiles.py` `load_profile(..., default="openspec")`;
- `floor/preparation.py` `_project_listing`, both fallbacks (unreadable
  project, undeclared profile) `"openspec"`;
- `floor/backends/probe.py` `_configured_models`, the literal tuple
  `("openspec", "fordesmac")`;
- `floor/frontend/src/main.tsx` `Hub`: the sheet's profile state
  (`"openspec" | "fordesmac" | ""`, initialised `"openspec"`), the
  provisional card's fallback `event.profile ?? "openspec"`, and the
  chooser's values, labels (`OpenSpec`, `Fordesmac`) and descriptions;
- the package directory `profiles/openspec/`.

Where the agent's facing name lives: one field, `label = "Builder"` in
`profiles/openspec/profile.toml`. The run snapshot (`floor/app.py`) carries
it as `user_agent.label` and in the roster; the conversation attributes the
agent's messages with it; the Agents area titles the agent, its roster row
and its "<label> session failed" notice with it; the broker's `manifest`
refuses a label that does not match the active profile ("agent label does
not match active profile"). Nothing in `floor/` spells "Builder" literally
except the sheet description. The prompt `builder.md` introduces the agent
as "You are Builder, ...".

## Goals / Non-Goals

**Goals:**

- One shipped direct profile named `openspec-builder`, the shop default,
  preselected in the hub's creation sheet.
- One maker-facing name, `OpenSpec Builder`, for the profile's choice in the
  sheet and for its agent wherever the agent is shown or speaks.
- The agent's internal identity unchanged: ID `builder`, `user_agent =
  "builder"`, `builder.md`, `name: builder`, and every project's
  `[tool.machinome-studio.agents]` `builder = ...` selection.
- A project declaring `openspec` or `builder` fails exactly as any other
  profile the shop does not ship fails today.

**Non-Goals:**

- No alias from `openspec` or `builder`, no compatibility path, no
  migration command, no deprecation warning.
- No `--profile` option or other per-run override.
- No change to `fordesmac`: its label "Fordesmac", its description
  "Four-agent mechanical shop", its prompts and roster.
- No change to the agent's prompt beyond its self-introduction and its
  frontmatter description line; skills, tool policy and Claude defaults are
  unchanged.
- No edit to any project's `pyproject.toml`; the catalogue is rewritten
  outside this change.
- No change to the `OpenSpec` capability's name, the `openspec` CLI, or the
  `openspec/` record of the studio or of a project.

## Decisions

### 1. Rename the directory; the identifier follows from it

A profile's identifier is its directory name under `profiles/`.
`git mv profiles/openspec profiles/openspec-builder` renames the package
with its history, and its two relative skill symlinks
(`../../../shop-skills/...`) resolve the same from the new directory. The
ID is lowercase kebab-case, so it passes the existing profile-ID shape
check with no loader change.

Alternative considered: keep the directory `profiles/openspec/` and change
only the label. Rejected by the pilot: the directory name is the profile
ID a project declares, and the collision with `openspec/` record
directories is half of the defect.

### 2. The facing name is the agent's label; everything shown derives from it

`profile.toml`'s `label` becomes `"OpenSpec Builder"`. The roster, the
Agents area, the conversation attribution and the session-failed notice
all read the label from the run snapshot, so no frontend string changes for
them. The agent ID stays `builder`, so the label is the only field of the
manifest that changes; `user_agent`, `id`, `prompt`, `assigns` and the
Claude table are byte-identical.

Because the broker refuses a manifest whose label differs from the active
profile's, every test fixture that manifests the agent as
`("builder", "Builder")` fails after the change rather than passing on a
stale name; those fixtures become `("builder", "OpenSpec Builder")`.
Synthetic `RoleContext` and `ProfileAgent` values in backend tests carry
the label without the broker checking it; they follow for consistency.

Alternative considered: rename the agent ID to `openspec-builder` too.
Rejected: the ID is internal, and every project's `builder = ...` agent
selection would stop applying.

### 3. The sheet names the choice the way the agent is named

The chooser's values become `["openspec-builder", "fordesmac"]`; the
OpenSpec Builder choice is labelled `OpenSpec Builder` and described "One
agent keeping the project's design in an OpenSpec record"; Fordesmac keeps
its label and description. The sheet's profile state is typed
`"openspec-builder" | "fordesmac" | ""` and starts at `"openspec-builder"`;
the provisional card's fallback becomes `"openspec-builder"`. The client's
"Choose a runtime profile." guard and the server's required `profile` field
stay.

The choice's label is the agent's facing name on purpose: for a direct
profile, the discipline and the one agent who follows it are what the maker
picks, and the pilot wants one name for both. Fordesmac keeps a team name
because its choice is a roster.

### 4. The default and the probe are constant changes

`load_profile`'s default, both `_project_listing` fallbacks and the probe
tuple become `"openspec-builder"`. As in the previous change, no new
configuration surface; the red-first listing and default tests pin the
values.

### 5. The prompt introduces the agent by its facing name

`builder.md` line 7 becomes "You are OpenSpec Builder, the sole standing
agent for the active project." so the agent calls itself what the maker sees.
Its frontmatter `description` (the loader reads only `name` and `skills`) is
updated to
"OpenSpec Builder: direct mechanical-product builder for one active
machinome project."; `name: builder` and `skills:` stay, as the loader
checks `name` against the agent ID. A red-first assertion in
`tests/test_role_contracts.py` pins the self-introduction.

### 6. `openspec` and `builder` are refused by the existing path

After the move, neither `profiles/openspec/` nor `profiles/builder/` exists,
so `_load_profile` raises "package is unavailable" and `load_profile` wraps
it in a `ProjectRuntimeError` naming the project's `pyproject.toml` and the
value. No code is added for either refusal. The spec keeps the general rule
with `builder` as its one example; ADR 0034 records `openspec` and the
decision against an alias; tests assert both names raise.

### 7. Specs: bodies change, titles stay

The OpenSpec CLI cannot sync a `MODIFIED` requirement whose scenario titles
differ from the baseline, and has no scenario-level rename. Every scenario
title in the deltas is therefore byte-identical to the baseline, including
"The OpenSpec project is ready", "Backend creates OpenSpec profile
sessions", "OpenSpec topology is loaded" and "The sheet opens with OpenSpec
chosen", whose words remain true of the renamed profile. Requirement titles
are unchanged too; "The shop ships OpenSpec and Fordesmac profiles" and
"The profile tool vocabulary names an OpenSpec capability" still read
correctly. In requirement and scenario bodies, "Builder" keeps naming the
agent; only the statement of its display label (`OpenSpec Builder`) and of
the sheet's label change.

### 8. Records

ADR 0034 is revised in place, not superseded (decision 5 of the pilot): its
title becomes "Ship the OpenSpec Builder profile as the default", its
decision names `openspec-builder` and the label `OpenSpec Builder`, its
alternatives gain "Keep `openspec` and the label `Builder`", and a dated
Revision section records that `openspec` lasted one hour and why it was
rejected. The draft is `adr-0034.md` beside this design and is promoted over
the existing file at implementation. The file keeps its path,
`0034-ship-the-openspec-profile-as-the-default.md`, so the index link and
any reference to it stay valid; only the index row's title text changes.
The status lines of ADRs 0011 and 0019 already name 0034 and need no edit.

The architecture overview's "Profile-defined runtime" section is rewritten
in place: the fallback sentence, the `OpenSpec` capability sentence ("Only
the `openspec-builder` profile declares it, for its agent Builder") and the
table row (`openspec-builder | direct | OpenSpec Builder | OpenSpec
Builder`). `AGENTS.md` names `openspec-builder` as the default. The
changelog's Unreleased "Two profiles" bullet and its Breaking note are
rewritten for the name that will ship (the hour-long `openspec` was never
released, but it was on `main`, so the note names it beside `builder` as a
refused former name), and the Session-panel correction's example becomes
`openspec-builder`.

## Risks / Trade-offs

- [Projects declaring `openspec` (rewritten from `builder` an hour ago) stop
  opening] → Intended and accepted by the pilot; the refusal names the file
  and the value, the changelog marks it **Breaking**, and the configuration
  reference lists the shipped names. The catalogue is rewritten outside
  this change.
- [Browser tests match text by substring: `closed · openspec` also matches
  `closed · openspec-builder`, and a button named `OpenSpec` also matches
  `OpenSpec Builder`] → The rewritten waits name `openspec-builder` and the
  button is matched exactly as `OpenSpec Builder`, so they fail on the old
  tree and cannot pass on a half-renamed one.
- [The documentation test for the profiles reference is data-driven from
  `profiles/`] → It cannot fail before the `git mv` and the label change;
  its red is the run after the move and before the page follows, recorded as
  such. The configuration-reference pin gains `openspec-builder`, which is
  red on the current page.
- [The facing name is longer than "Builder" in narrow layouts: the roster
  row, the Agents-area title and the conversation attribution] → Inspected
  in the browser at the narrow width the Agents e2e already uses before the
  implementation commit.
- [Prose ambiguity among the `openspec-builder` profile, the `OpenSpec`
  capability, the `openspec` CLI and an `openspec/` record] → The rename
  removes most of it; the manual names the profile in double backticks.

## Migration Plan

None inside the studio: no alias and no migration tool. A project
declaring `openspec` or `builder` is edited by hand to `openspec-builder`.
Rollback is a revert of the implementation commit.
