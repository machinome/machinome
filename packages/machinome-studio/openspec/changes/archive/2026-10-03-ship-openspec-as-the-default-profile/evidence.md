# Evidence: ship-openspec-as-the-default-profile

## Red (tasks 1.1–1.7)

Every test below was run against the unchanged tree: `profiles/builder/` still
in place, `floor/profiles.py` `load_profile`'s default still `"fordesmac"`,
`floor/preparation.py` `_project_listing`'s fallbacks still `"fordesmac"`,
`floor/backends/probe.py` still iterating `("builder", "fordesmac")`, and the
hub sheet still defaulting to no profile with a `Builder` button. Each module
was run with

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m unittest tests.<module> -v
```

from the worktree, after confirming
`PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -c "import floor; print(floor.__file__)"`
printed the worktree's own `floor/__init__.py`.

```
tests.test_runtime_profiles
```
```
FAILED (failures=6, errors=10)
Ran 12 tests in 0.057s
```
Every new or rewritten assertion fails for the intended reason: the default
test (`load_profile(None, shop_root=ROOT).id == "openspec"`) sees `fordesmac`;
the shipped-profiles test's `load_profile("openspec", ...)` raises
`profile openspec: package is unavailable at .../profiles/openspec`; the new
`test_builder_is_no_longer_a_shippable_profile` sees `builder` still load
successfully (`ProfileError not raised`); the every-shipped-profile loop and
every profile-package fixture test (`test_skills_are_profile_allowlisted`,
`test_a_skill_that_cannot_describe_itself_fails_validation`,
`test_builtin_profiles_declare_only_profile_explicit_backends`,
`test_retired_backends_are_rejected`,
`test_invalid_selection_and_unknown_schema_key_fail_with_actionable_errors`,
`test_skill_links_and_prompt_paths_cannot_escape_the_profile`,
`test_selected_backends_reject_controls_their_adapters_cannot_enforce`) fail
the same way, each naming `profiles/openspec` as missing.

```
tests.test_project_runtime_selection
```
```
FAILED (failures=1, errors=6)
Ran 20 tests in 0.221s
```
The new `test_a_project_declaring_builder_is_refused_and_not_opened_under_the_default`
fails because `load_profile(None, ..., selection=declaring "builder")` still
resolves `builder` successfully today (`ProjectRuntimeError not raised`); the
two-roster, changed-profile, created-project and `ProfileRuntimeTableTest`
cases all fail resolving `profiles/openspec` (`package is unavailable`), the
intended reason given the profile has not moved yet.

```
tests.test_project_preparation
```
```
FAILED (failures=1), 1 skipped
Ran 43 tests in 4.744s
```
Only the new fallback test fails, for the intended reason:
`test_a_project_declaring_no_profile_is_listed_under_the_shop_default` sees
`'fordesmac' != 'openspec'`. The one skip (`WorkspaceSolidAcceptanceTest`) is
pre-existing and environmental (no development workspace `machinome`
installation here), unrelated to this change.

```
tests.test_openspec_tools
```
```
FAILED (errors=2)
Ran 18 tests in 26.567s
```
`test_a_profile_may_declare_the_capability_and_unknown_names_still_fail` and
the renamed `test_openspec_declares_the_capability` both fail resolving
`profiles/openspec` (`package is unavailable`).

```
tests.test_role_contracts
```
```
FAILED (errors=2)
Ran 4 tests in 0.002s
```
Both tests that load a profile by ID fail resolving `profiles/openspec`:
`test_runtime_prompts_are_profile_owned_and_runtime_skills_are_allowlisted`
(loop now `("openspec", "fordesmac")`) and
`test_builder_is_direct_and_preserves_disassembled_leaf_first_red` (reads
`profiles/openspec/builder.md`, which does not exist until the `git mv`).

```
tests.test_documentation
```
```
FAILED (failures=1)
Ran 24 tests in 0.436s
```
Only `test_project_configuration_reference_names_the_table` fails, for the
intended reason: `'openspec' not found in` the current
`docs/reference/project-configuration.rst`, which still names only `builder`
and `fordesmac`. `test_profiles_reference_matches_the_shipped_profiles`,
tightened to require a profile's own section heading (name in double
backticks followed by an `=` underline), still passes today because
`docs/reference/profiles.rst` already headings `` ``builder`` `` and
`` ``fordesmac`` `` that way; it is exercised again after the rename, where it
must find `` ``openspec`` `` instead.

```
tests.test_project_open
```
```
FAILED (failures=12, errors=1)
Ran 14 tests in 0.692s
```
Every case fails resolving `profiles/openspec` (`package is unavailable`),
including the new `make_project` default (`profile: str = "openspec"`) and
the explicit `registry.create("", "new_engine", "openspec")` call.

```
tests.test_floor_api
```
```
FAILED (failures=18)
Ran 18 tests in 144.520s
```
The whole module fails in `setUp`: the real `python -m floor` subprocess it
launches against a fixture project declaring `profile = "openspec"` never
reaches `{"status": "open"}` because every project opened under it (default
`_make_project` profile, and the explicit `POST /api/projects` bodies) fails
resolving `profiles/openspec`.

```
tests.test_orchestrator
```
```
FAILED (failures=6, errors=5)
Ran 75 tests in 25.786s
```
`ProfileOrchestratorTest`'s `_resolved_profile("openspec")` calls and
`SessionOpeningTest`'s fixtures (now `profile = "openspec"`, including the
new `test_a_project_declaring_no_profile_opens_exactly_the_agent_builder`,
which opens a bare project and expects the default to resolve) fail the same
way; `test_preparation_and_agent_start_failures_leave_no_partial_session`
fails because the error text it expects ("backend start failed") is
preempted by the earlier, unrelated "profile openspec... unavailable" error.

```
tests.test_broker, tests.test_source_files, tests.test_codex_backend,
tests.test_codex_worker_adversarial, tests.test_codex_git_identity,
tests.test_codex_selection, tests.test_codex_preflight
```
Each of these loads `profiles/openspec` directly (`load_profile("openspec",
...)`) and fails the same way; not run individually here because the whole
suite run below exercises them and shows the same single cause.

```
tests.test_shop_lifecycle_e2e
```
(Chromium via Playwright; frontend installed and built once —
`npm --prefix floor/frontend install && npm --prefix floor/frontend run
build` — to give the harness a bundle to serve, with no source edits yet:
the sheet still shows a `Builder` button, not `OpenSpec`.)
```
FAILED (failures=15, errors=3)
Ran 23 tests in 103.250s
```
`test_project_creation_opens_a_workspace_and_close_returns_to_the_hub` errors
waiting for a button named `OpenSpec` that does not exist yet (the sheet
still offers `Builder`/`Fordesmac`). Every other failing case opens a fixture
project declaring `profile = "openspec"` (the updated `_make_project`
default) and either errors waiting for text `openspec · open` /
`closed · openspec` / `open · openspec`, or fails because the session itself
failed to open (`profile openspec... unavailable`). Five cases pass
unmodified (hub identity, codex backend listing, the plain creation-sheet
smoke test, and two others not touching profile resolution).

## Fixes made while writing the red run

None: every module failed for the behaviour under test on the first run: an
unavailable `profiles/openspec` package, a default still resolving to
`fordesmac`, a still-successful `builder` load, or a manual page still naming
only the old profiles. No test needed correction for an import or fixture
error before its failure was meaningful.

One red test was missed by the section-4 grep and found instead by running
the module: `tests/test_opencode_backend.py`'s
`test_projects_select_opencode_without_profile_manifest_tables` iterates a
tuple `("builder", ["builder"])` into `load_profile(profile_id, ...)` rather
than calling `load_profile("builder", ...)` literally, so the grep in task
4.1 did not find it. After section 2's rename it failed with `profile
builder: package is unavailable`; the tuple's profile id became
`("openspec", ["builder"])` (the agent-id list stays `["builder"]`) and the
module went green.

## Green (sections 2-6 complete)

All four named checks, run from the worktree with the worktree on
`PYTHONPATH` and the workspace venv on `PATH`:

```
python -m unittest discover -s tests -v
```
```
Ran 499 tests in 165.405s
FAILED (failures=1, skipped=1)
```
The one failure, `test_every_tracked_source_file_has_agpl_header` in
`tests/test_license_headers.py`, names `tests/test_frame_precision_contract.py`
as missing an AGPL header. That file is untouched by this change (`git diff
HEAD -- tests/test_frame_precision_contract.py` is empty) and the defect is
already present at the worktree's base commit `51cf5f1`; it is a pre-existing,
unrelated environmental finding, not a regression from this cycle. The one
skip is `WorkspaceSolidAcceptanceTest`, pre-existing and environmental (no
development-workspace `machinome` installation in this sandbox).

```
npm --prefix floor/frontend run test
```
```
> tsc -b --pretty false
```
Clean (no output, no error): the `Run` type's new `work_mode` field and every
`"openspec"` / `"builder"` string the frontend edits touch type-check.

```
npm --prefix floor/frontend run build
```
Succeeds; `floor/static/` regenerated (not staged).

```
scripts/test-e2e
```
(rebuilds the frontend, then runs `tests.test_floor_entrypoint`,
`tests.test_floor_api`, `tests.test_shop_lifecycle_e2e`)
```
Ran 51 tests in 72.966s
OK (skipped=1)
```
The one skip, `test_model_panel_presents_the_viewer_navigator`'s real-bundle
case, is pre-existing and environmental (`SHOP_E2E_VIEWER_BUNDLE` unset, no
`machinome-viewer` installed in this sandbox) — the same skip the fake-bundle
suite does not exercise.

```
python -m sphinx -b html -n -W --keep-going docs docs/_build/html
```
```
build succeeded.
```
No warnings. The built `docs/_build/html/reference/profiles.html` was spot
checked: `openspec` appears 6 times, `fordesmac` 6 times, `Builder` once,
`Fordesmac` once — the renamed section heading and table are present and the
agent names are untouched.

## Pixel evidence

A floor was started from the worktree on an ephemeral port against a
temporary projects directory under the scratchpad (never the pilot's
catalogue, never port 9000/9010), with one bare project declaring no
profile. Captured with Playwright, then the floor was stopped (its whole
process tree):

- `hub-bare-project-card.png` — the bare project's hub card reads
  `closed · openspec · just now`.
- `hub-new-project-sheet.png` — the "New project" sheet opens with
  **OpenSpec** already selected (highlighted), its description "One agent,
  Builder, keeping an OpenSpec design record" legible at the sheet's width,
  and **Fordesmac** ("Four-agent mechanical shop") offered beside it.

Both PNGs are at
`/tmp/claude-1000/-home-asa-devel-machinome/76a82843-caa1-4339-bdf6-b0cac11a6fc1/scratchpad/pixels/`.

## Archiving (task 7.3)

`openspec archive` refuses to sync a `MODIFIED Requirements` block when the
current baseline spec's requirement carries a scenario title absent from the
delta's block, to avoid silently dropping scenario coverage; it has no
scenario-level rename primitive (only the top-level `RENAMED Requirements`
form renames a whole requirement). Three scenarios in this change's spec
deltas had renamed titles — the behaviour they describe did not change, only
the words "Builder"/"OpenSpec" in the title — so the archive aborted three
times naming each:

- `named-project-bootstrap` :: "Every project agent works in the verified
  project root": delta titled its first scenario "The OpenSpec project is
  ready"; baseline has "The Builder project is ready". Reverted the delta's
  title to match baseline; its `WHEN` clause still names the `openspec`
  profile.
- `shop-agent-backend` :: "The backend owns its agent sessions": delta
  titled its first scenario "Backend creates OpenSpec profile sessions";
  baseline has "Backend creates Builder profile sessions". Reverted the
  same way.
- `shop-runtime-profile` :: "The shop ships OpenSpec and Fordesmac profiles"
  (itself a `RENAMED Requirements` target, from "The shop ships Builder and
  Fordesmac profiles"): delta titled its first scenario "OpenSpec topology
  is loaded"; baseline (under the pre-rename header) has "Builder topology
  is loaded". Reverted the same way.

After the third fix, a script-verified scenario-title parity check (every
baseline scenario title, under each `MODIFIED`/renamed-target requirement,
present somewhere in the delta's block) passed clean across all ten spec
deltas, `openspec validate --strict` passed, and `openspec archive
ship-openspec-as-the-default-profile -y` succeeded:

```
Applying changes to openspec/specs/named-project-bootstrap/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/project-runtime-selection/spec.md:
  ~ 2 modified
Applying changes to openspec/specs/shop-agent-backend/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/shop-agent-lifecycle/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/shop-agent-messaging/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/shop-browser-workspace/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/shop-floor-lifecycle/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/shop-project-hub/spec.md:
  ~ 2 modified
Applying changes to openspec/specs/shop-runtime-profile/spec.md:
  ~ 5 modified
  → 1 renamed
Applying changes to openspec/specs/shop-user-conversation/spec.md:
  ~ 2 modified
Totals: + 0, ~ 17, - 0, → 1
Specs updated successfully.
Change 'ship-openspec-as-the-default-profile' archived as
'2026-10-03-ship-openspec-as-the-default-profile'.
```
