## 1. Prove the new behaviour red first

Every test below is written against the current tree (with
`profiles/openspec/` in place, the default `openspec` and the agent label
`Builder`) and run to show it fails for the stated reason before any code,
profile or page changes. Run from the worktree with `PYTHONPATH=<worktree>`
and the workspace venv, after confirming
`python -c "import floor; print(floor.__file__)"` prints the worktree.
Record each red run (module, test, failure line) in `evidence.md` in this
change directory.

- [ ] 1.1 `tests/test_runtime_profiles.py`: the default test asserts `load_profile(None, shop_root=ROOT).id == "openspec-builder"`; the shipped-profiles test loads `openspec-builder` and asserts its roster is exactly `[("builder", "OpenSpec Builder")]`, user-facing, direct mode, `user_agent` `builder`; the no-longer-shipped test asserts both `load_profile("openspec", ...)` and `load_profile("builder", ...)` raise the unavailable-package `ProfileError`; the every-shipped-profile loop and every profile-package fixture (`profiles" / "openspec"` copies) use `openspec-builder`.
- [ ] 1.2 `tests/test_project_runtime_selection.py`: a project declaring `profile = "openspec"` is refused with a `ProjectRuntimeError` naming its `pyproject.toml` and the value `'openspec'`, and is not opened under the default (the existing `builder` case stays); the two-roster, changed-profile, created-project and profile-table cases declare and read `openspec-builder` and still key the selection to the agent `builder`.
- [ ] 1.3 `tests/test_project_preparation.py`: the undeclared-profile listing test expects `openspec-builder`; the declared-profile listing and creation tests write and read `openspec-builder`.
- [ ] 1.4 `tests/test_project_open.py`, `tests/test_floor_api.py`, `tests/test_orchestrator.py`: project fixtures, creation requests and hub events use `openspec-builder` (the `make_project` / `_make_project` defaults, `registry.create(..., "openspec-builder")`, the `creating` event, the `session.profile.id` assertions, the `POST /api/projects` bodies and the `profile = "openspec-builder"` pins); every agent manifest posted as `{"role": "builder", "label": "Builder"}` becomes `{"role": "builder", "label": "OpenSpec Builder"}`, since the floor refuses a label that does not match the active profile.
- [ ] 1.5 `tests/test_openspec_tools.py` and `tests/test_role_contracts.py`: the capability and prompt-contract tests load `openspec-builder` and read `profiles/openspec-builder/builder.md`; the Builder prompt test also asserts it contains "You are OpenSpec Builder," and still has frontmatter `name: builder`. The Fordesmac exclusion test is unchanged.
- [ ] 1.6 `tests/test_documentation.py`: the configuration-reference pin requires `openspec-builder` instead of `openspec`. The profiles-reference test is data-driven from `profiles/` and cannot fail before the move; its red is recorded at task 2.6 instead.
- [ ] 1.7 `tests/test_shop_lifecycle_e2e.py`: the creation test asserts the choice button named exactly `OpenSpec Builder` is selected, the description "One agent keeping the project's design in an OpenSpec record" is shown, and Fordesmac is offered; it creates without clicking a profile and waits for `creating · openspec-builder`; the hub waits become `closed · openspec-builder` and `open · openspec-builder`, the workspace title `openspec-builder · open` (exact), the Session panel `openspec-builder · direct`, the session-failure notice `OpenSpec Builder session failed` (exact); the multi-model fixture declares `profile = "openspec-builder"`; every roster fixture `{"role": "builder", "label": "Builder"}` becomes `"OpenSpec Builder"`. (Substring waits on `openspec` would also match `openspec-builder`; every rewritten wait names the full ID so it cannot pass on the old tree.)
- [ ] 1.8 Run the modules above and record each failing for the intended reason (unavailable `profiles/openspec-builder`, default mismatch, `openspec` still loading, label mismatch, missing button or text), not for an import or fixture error. Build the frontend once from the unchanged source to give the browser tests a bundle.

## 2. Rename the profile, its default and its agent's label

- [ ] 2.1 `git mv profiles/openspec profiles/openspec-builder`. Confirm the two skill symlinks still resolve to `shop-skills/machinome` and `shop-skills/machinome-api`.
- [ ] 2.2 `profiles/openspec-builder/profile.toml`: `label = "OpenSpec Builder"`; every other line unchanged (`user_agent = "builder"`, `id = "builder"`, `prompt = "builder.md"`, the Claude table).
- [ ] 2.3 `profiles/openspec-builder/builder.md`: the self-introduction becomes "You are OpenSpec Builder, the sole standing agent for the active project."; the frontmatter `description` becomes "OpenSpec Builder: direct mechanical-product builder for one active machinome project."; `name: builder`, `skills:` and the rest of the prompt unchanged.
- [ ] 2.4 `floor/profiles.py`: `load_profile(..., default="openspec-builder")`. `floor/preparation.py` `_project_listing`: both fallbacks `"openspec-builder"`. `floor/backends/probe.py` `_configured_models`: iterate `("openspec-builder", "fordesmac")`. Add no alias, special case or warning for `openspec` or `builder`.
- [ ] 2.5 `grep -rnw openspec floor/ --include=*.py` and confirm every remaining hit means the CLI, the record or the capability, not the profile; `grep -rn '"Builder"' floor/` finds nothing.
- [ ] 2.6 Before touching the manual, run `tests.test_documentation` and record `test_profiles_reference_matches_the_shipped_profiles` failing for the intended reason (no ``` ``openspec-builder`` ``` section heading, or no `OpenSpec Builder` in the agent's row window).

## 3. The hub sheet

- [ ] 3.1 `floor/frontend/src/main.tsx` `Hub`: profile state typed `"openspec-builder" | "fordesmac" | ""` and initialised to `"openspec-builder"`; the provisional-card fallback becomes `"openspec-builder"`.
- [ ] 3.2 The chooser iterates `["openspec-builder", "fordesmac"]`, labels them `OpenSpec Builder` and `Fordesmac`, and describes OpenSpec Builder as "One agent keeping the project's design in an OpenSpec record" while Fordesmac keeps "Four-agent mechanical shop". Keep the client guard and the server's required `profile` field.
- [ ] 3.3 Rebuild the frontend (`floor/static/`, never staged) and inspect in the browser: the sheet with OpenSpec Builder selected on open and its description legible at the sheet's width; a bare project's hub card (`closed · openspec-builder`); a workspace whose conversation, roster and Agents-area title show `OpenSpec Builder` without truncation at the narrow width the Agents e2e uses.

## 4. Follow the rename through the remaining tests

- [ ] 4.1 Replace the profile `"openspec"` with `"openspec-builder"` wherever it names the profile, and the agent label `"Builder"` with `"OpenSpec Builder"` wherever it is the agent's label, in `tests/test_broker.py` and `tests/test_source_files.py` (`manifest("builder", "OpenSpec Builder")`), `tests/test_codex_backend.py`, `tests/test_codex_worker_adversarial.py`, `tests/test_codex_git_identity.py` (the `RoleContext` profile and label arguments), `tests/test_codex_selection.py`, `tests/test_codex_preflight.py`, and `tests/test_opencode_backend.py` (the `OpenCodeSelectionTest` tuple, and the synthetic `ProfileAgent` label, `profile_id` and `user_agent_label`, whose `profile_id="builder"` is a leftover of the first rename). `role="builder"`, `open_role("builder", ...)`, agent keys, `--role builder` and every `openspec` meaning the CLI, the record or the capability stay. `tests/test_project_runtime_selection.py`'s invalid-ID tuple keeps `"Builder"`: it is a malformed ID, not a label.
- [ ] 4.2 `grep -rnE '"openspec"|profiles" / "openspec"|profile = \\?"openspec"|"label": "Builder"|"Builder"\)' tests/` and confirm every remaining hit means the CLI, the record, the capability or a malformed ID; then run every module touched in sections 1 and 4 green.

## 5. Manual

Under the workspace's `write-the-manual` skill.

- [ ] 5.1 `docs/reference/profiles.rst`: the direct profile's section heading becomes ``` ``openspec-builder`` ``` and the agent row's label `OpenSpec Builder` (agent ``` ``builder`` ```).
- [ ] 5.2 `docs/reference/project-configuration.rst`: the `profile` entry names ``` ``openspec-builder`` ``` and ``` ``fordesmac`` ``` as the shipped names and ``` ``openspec-builder`` ``` as the default; a name the studio does not ship makes the project unopenable, and the studio does not substitute the default. The page names no former profile name: remove its existing "including the former ``` ``builder`` ```" clause.
- [ ] 5.3 `docs/working-with-agents.rst`: a project recording no profile opens under ``` ``openspec-builder`` ```; the section heading becomes "OpenSpec Builder" and introduces ``` ``openspec-builder`` ``` as one agent, **OpenSpec Builder**, with "Builder" as its short name in the paragraphs that follow; "under ``` ``openspec`` ```, the ``` ``openspec/`` ``` record" becomes "under ``` ``openspec-builder`` ```, ...".
- [ ] 5.4 `docs/the-floor.rst` ("**OpenSpec Builder** under ``` ``openspec-builder`` ```") and `docs/opening-a-project.rst` ("``` ``openspec-builder`` ``` when it declares none"); the CLI mentions on those pages stay.
- [ ] 5.5 Build strictly (`python -m sphinx -b html -n -W --keep-going docs docs/_build/html`), read the changed pages in the built HTML, and confirm no other page, README or docstring names `openspec` as a profile.

## 6. Records

- [ ] 6.1 Promote `adr-0034.md` over `docs/adrs/0034-ship-the-openspec-profile-as-the-default.md` (same path). In `docs/adrs/README.md`, row 0034's title becomes "Ship the OpenSpec Builder profile as the default", link and status unchanged. ADRs 0011 and 0019 already name 0034 in their status lines and are not edited.
- [ ] 6.2 Rewrite `docs/architecture-overview.md` § Profile-defined runtime in place: the fallback sentence names `openspec-builder`; the `OpenSpec` capability sentence says only the `openspec-builder` profile declares it, for its agent; the table row becomes `` `openspec-builder` | direct | OpenSpec Builder | OpenSpec Builder ``. Sentences about Builder the agent keep the short name.
- [ ] 6.3 `AGENTS.md`: "`openspec-builder` (the default) and `fordesmac` are the profiles today".
- [ ] 6.4 `CHANGELOG.md` under `## Unreleased`: rewrite the "Two profiles" bullet with `openspec-builder`, the shop default, one agent — OpenSpec Builder — keeping the project's design in an OpenSpec record it owns, and `fordesmac`; rewrite its **Breaking** note: a project declaring no profile now opens under `openspec-builder` instead of `fordesmac`, and a project declaring the former `builder` or `openspec` name is refused, naming its `pyproject.toml` and the value, until its declaration names `openspec-builder`, with no alias or migration path. The Session-panel correction's example becomes `openspec-builder`.
- [ ] 6.5 `workflow/ongoing/reconstructions-in-the-studio.md`: "the openspec profile" becomes "the openspec-builder profile"; the uses naming the agent stay.

## 7. Validate and close the cycle

- [ ] 7.1 Run the whole Python suite, `npm --prefix floor/frontend run test` and `scripts/test-e2e` from the worktree with the worktree on `PYTHONPATH`; report environmental failures honestly.
- [ ] 7.2 `openspec validate name-the-profile-openspec-builder --strict`; confirm every scenario title in the ten deltas is byte-identical to the baseline; sync the deltas into `openspec/specs/`, archive the change, and create the implementation commit. Integration, push and the catalogue's project declarations are the pilot's and the reviewer's, outside this change.
