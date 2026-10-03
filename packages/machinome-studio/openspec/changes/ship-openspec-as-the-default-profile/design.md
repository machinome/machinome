## Context

ADR 0011 introduced declarative profiles with `builder` as the fallback. ADR
0019 moved the profile into the project's `[tool.machinome-studio]` table and,
as an independent decision, changed the fallback to `fordesmac`. The change
`open-projects-from-hub` later removed the `--profile` option, so the
selection chain today is: the project's declared `profile`, otherwise the
shop default `fordesmac`. A declared but unavailable profile is refused with
the project file and value; it is never replaced by the default.

Since then the `builder` profile has gained the project's OpenSpec record
(`builder-spec-discipline`, ADR 0027): its one agent plans each design change
in an OpenSpec change, builds it, syncs and archives it. On 3 October 2026 the
pilot decided that this discipline is the studio's normal mode, that the
profile is named for it, and that the delegated Fordesmac roster is kept as
the delegation evidence.

Where the default lives today:

- `floor/profiles.py` `load_profile(..., default="fordesmac")`, used by every
  entry point that opens a session;
- `floor/preparation.py` `_project_listing`, which shows a project declaring
  no profile, and an unreadable project, under `fordesmac`;
- `floor/frontend/src/main.tsx`, whose hub sheet starts with no profile
  selected and whose provisional "creating" card falls back to `fordesmac`
  when the event carries no profile.

`floor/backends/probe.py` iterates over the literal tuple
`("builder", "fordesmac")` to report the models the shipped profiles
configure; it names the profile and must follow the rename.

## Goals / Non-Goals

**Goals:**

- One shipped direct profile named `openspec`, opened for every project that
  declares no profile, preselected in the hub's creation sheet.
- The rename is total for the profile identifier and nil for the agent:
  `builder`/`Builder` keep meaning the agent everywhere.
- A project still declaring `builder` fails exactly as any other unavailable
  profile fails today.

**Non-Goals:**

- No alias from `builder` to `openspec`, no compatibility path, no migration
  command, no deprecation warning.
- No `--profile` option or any other per-run override.
- No change to `fordesmac`, its prompts, or its place as a selectable
  profile.
- No change to the Builder prompt, its skills, tool policy or Claude
  defaults; the profile manifest's contents are unchanged by the move.
- No edit to any project's `pyproject.toml`; the catalogue is the reviewer's
  to rewrite outside this change.

## Decisions

### 1. Rename the directory; the identifier follows from it

A profile's identifier is its directory name under `profiles/`; nothing in
`profile.toml` names the profile. `git mv profiles/builder profiles/openspec`
is therefore the whole rename of the package, preserving history and the two
relative skill symlinks (`../../../shop-skills/...`), which resolve the same
from the new directory. The manifest keeps `user_agent = "builder"` and the
agent `id = "builder"`, `label = "Builder"`, `prompt = "builder.md"`.

Alternative considered: renaming the agent too (`openspec` agent, label
"OpenSpec"). Rejected by the pilot: the agent is a person on the floor, the
profile is the discipline it works under; Fordesmac keeps the same
distinction (profile `fordesmac`, agents Foreman, Designer, ...).

### 2. The default is a single constant change in each place it lives

`load_profile`'s `default` becomes `"openspec"`, and the hub listing's
fallback becomes `"openspec"` in both its branches. The frontend's
provisional-card fallback becomes `"openspec"`. No new configuration surface
is introduced: the default stays a shop fact, not a setting.

Alternative considered: deriving the listing fallback from `load_profile`'s
default so the two cannot drift. Worth noting, but it adds an indirection
this change does not need; the red-first listing test pins the value instead.

### 3. `builder` is refused by the existing unavailable-profile path

After the move, `profiles/builder/` no longer exists, so `_load_profile`
already raises "package is unavailable", and `load_profile` already wraps it
in a `ProjectRuntimeError` naming the project's `pyproject.toml` and the value
`'builder'`. No code is added for the refusal. The baseline specs
state only the general rule (a profile the shop does not ship is refused,
never replaced by the default), with `builder` as one instance of it; the
standing decision against an alias lives in ADR 0034 and in a test asserting
`load_profile("builder")` raises, so a later alias would have to break that
test deliberately. The hub lists such a project
as it lists any project whose declared profile is unavailable today.

### 4. The sheet preselects OpenSpec and keeps Fordesmac

The sheet's profile state starts at `"openspec"` instead of empty, the
choices are `openspec` then `fordesmac`, and the OpenSpec choice is labelled
`OpenSpec` with a one-line description. OpenSpec is described as "One agent,
Builder, keeping an OpenSpec design record"; Fordesmac keeps "Four-agent
mechanical shop". The client-side
"Choose a runtime profile." guard and the server's required `profile` field
stay: the API still requires a profile, and the sheet now always sends one.

### 5. The backend probe follows the shipped profiles

`probe.py`'s tuple becomes `("openspec", "fordesmac")`. Deriving it from the
`profiles/` directory would also work but changes behaviour if a profile is
added; the literal is kept, matching the current code's shape.

### 6. The Session panel reads the work mode from the run

The Agents area's Session panel rendered `{profile_id} · delegated` for every
profile, so the new default view would read "openspec · delegated". The
run snapshot (`floor/app.py`, `run()`) gains the profile's `work_mode` beside
`profile_id`, and the panel renders `{profile_id} · {work_mode}` instead of
asserting a mode. No spec pins the panel's text, so this is a correction, not
a requirement change.

### 7. Records

ADR 0034 (draft beside this design, promoted at implementation) amends ADR
0019's fallback and ADR 0011's profile name. ADR 0011's status becomes
"Accepted (amended by 0012, 0016, 0017, 0019, 0025, 0032, and 0034)"; ADR
0019's becomes "Accepted (amended by 0034)"; the index gains row 0034 and the
two updated status cells. The overview's "Profile-defined runtime" section is
rewritten, not appended to: the fallback sentence, the profile table (with
`openspec` first), and the `OpenSpec` capability sentence ("Only the
`openspec` profile declares it, for Builder"). The same rewrite drops the
stale sentence "The option overrides a project declaration for one run
without modifying it.", which contradicts "The launcher provides no
override." two lines above it.

## Risks / Trade-offs

- [Projects declaring `builder` stop opening] → Intended and accepted by the
  pilot; the refusal names the file and the value, the changelog marks it
  **Breaking**, and the manual's configuration reference lists the shipped
  names. The pilot's own catalogue is rewritten outside this change.
- [A bare project now opens one Builder instead of four Fordesmac sessions]
  → Intended; recorded as **Breaking** in ADR 0034 and the changelog.
- [The identifier `openspec` collides in prose with the `openspec` CLI, the
  `OpenSpec` capability and a project's `openspec/` record] → Manual pages
  name the profile as "the ``openspec`` profile" where the context is
  ambiguous. `tests/test_documentation.py`'s profiles-reference pin, which
  only checks that ``` ``openspec`` ``` occurs on the page, would pass on a
  mention of the CLI alone; it is tightened to require the profile's section
  heading.
- [Many test modules load `load_profile("builder")` as a convenient direct
  profile] → They are mechanical renames of the profile argument only; every
  `role="builder"`, `open_role("builder", ...)`, agent key and broker
  manifest call keeps `builder` because it names the agent.

## Migration Plan

None inside the studio: no alias and no migration tool, by decision. A
project declaring `builder` is edited by hand to `openspec`. Rollback is a
revert of the implementation commit.
