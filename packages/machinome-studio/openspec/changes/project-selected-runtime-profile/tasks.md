## 1. Reading the profile from the project (red first)

- [ ] 1.1 Write failing tests in `tests/test_project_runtime_selection.py` that
      `read_project_runtime()` returns the declared `profile` value, returns none
      for a project with no key, no `[tool.solid-node-studio]` table, no
      `pyproject.toml`, and no project directory at all, and still rejects an
      unknown key beside `profile` and `agents`.
- [ ] 1.2 Write failing tests that a non-string `profile` value and a value that
      is not lowercase kebab-case — including one containing `/`, `..`, or an
      uppercase letter — are rejected with an error naming the project file and
      the value.
- [ ] 1.3 Add `profile` to the accepted key set and to `ProjectRuntimeSelection`
      in `floor/preparation.py`, validating shape only and resolving nothing
      against the filesystem. Turn 1.1 and 1.2 green.

## 2. Precedence and the new default (red first)

- [ ] 2.1 Write failing tests in `tests/test_runtime_profiles.py` for the
      precedence chain: the option wins over a declared profile, a declared
      profile wins over the default, and the default is `fordesmac` when neither
      is present.
- [ ] 2.2 Write failing tests that a well-formed but unresolvable declared
      profile fails with an error naming the project file and the value rather
      than falling back to the default, and that the same declaration is
      tolerated when `--profile` supplies a profile that does resolve.
- [ ] 2.3 Change `load_profile()`'s default from `builder` to `fordesmac` in
      `floor/profiles.py` and carry the origin of the resolved name so a
      project-supplied failure can be reported against the project file. Turn
      2.1 and 2.2 green.

## 3. Both entry points

- [ ] 3.1 Write failing tests in `tests/test_orchestrator.py` and
      `tests/test_floor_entrypoint.py` that `python -m floor.orchestrator` and
      `python -m floor` resolve the profile identically for the same project,
      with and without the option.
- [ ] 3.2 Apply the precedence chain at the single resolution point each entry
      point already has, between `read_project_runtime()` and `load_profile()`.
      Turn 3.1 green.
- [ ] 3.3 Write and satisfy a failing test that a run whose profile comes from
      the project performs no project side effect before the profile fails to
      validate — extend the existing ordering test rather than adding a parallel
      one.

## 4. Roster tolerance under an override

- [ ] 4.1 Write and satisfy a failing test that a project declaring `fordesmac`
      with specialist agent selections, opened with `--profile builder`, opens
      `builder`, ignores the specialist keys, and reports them.

## 5. Scaffolding stays silent

- [ ] 5.1 Write and satisfy a failing test that a project the launcher scaffolds
      contains no `profile` key and no `[tool.solid-node-studio]` table.

## 6. Documentation and decision record

- [ ] 6.1 Write ADR 0019 amending 0011 and 0017: the precedence chain, the
      retention of `--profile` with its bootstrapping and roster-choice
      reasoning, the shape-always/resolution-when-used split, the default change
      as its own decision, and tool-and-permission layering as out of scope.
- [ ] 6.2 Add ADR 0019 to `docs/adrs/README.md`, preserving chronological order.
- [ ] 6.3 Update `skills/running-the-shop/SKILL.md`: `--profile` overrides a
      project-declared profile, `fordesmac` is the default, and the project's
      `pyproject.toml` carries `profile` beside `[tool.solid-node-studio.agents]`.
- [ ] 6.4 Update `README.md`, `AGENTS.md` (the shop-floor lane's instruction to
      select a profile explicitly), and the profile section of
      `docs/architecture-overview.md` to the new resolution rules.
- [ ] 6.5 Check `tests/test_development_protocols.py` and
      `tests/test_product_identity.py` for assertions on the documented default
      and update them with the docs.

## 7. Completion

- [ ] 7.1 Run the full suite and record the result in the change.
- [ ] 7.2 Open a floor for a scratch project both ways — bare, and with
      `--profile builder` against a `fordesmac` declaration — and confirm the
      roster the browser shows in each case.
- [ ] 7.3 Sync the two delta specs into `openspec/specs/`, archive the change,
      and commit the implementation record.
