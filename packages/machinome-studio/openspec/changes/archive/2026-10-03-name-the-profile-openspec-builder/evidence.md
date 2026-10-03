# Evidence: name-the-profile-openspec-builder

## Red (tasks 1.1-1.7)

Every test below was run against the unchanged tree: `profiles/openspec/`
still in place (default `openspec`, agent label `Builder`), `floor/profiles.py`
`load_profile`'s default still `"openspec"`, `floor/preparation.py`
`_project_listing`'s fallbacks still `"openspec"`, `floor/backends/probe.py`
still iterating `("openspec", "fordesmac")`, and the hub sheet still offering
a button named exactly `OpenSpec` (not `OpenSpec Builder`) with the description
"One agent, Builder, keeping an OpenSpec design record". Each module was run
with

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
Ran 12 tests in 0.061s
```
Every new or rewritten assertion fails for the intended reason: the default
test (`load_profile(None, shop_root=ROOT).id == "openspec-builder"`) sees
`openspec`; the shipped-profiles test's `load_profile("openspec-builder",
...)` raises `profile openspec-builder: package is unavailable at
.../profiles/openspec-builder`; the rewritten
`test_openspec_and_builder_are_no_longer_shippable_profiles` sees `openspec`
still load successfully (`ProfileError not raised`, the first assertion); the
every-shipped-profile loop and every profile-package fixture test
(`test_skills_are_profile_allowlisted`,
`test_a_skill_that_cannot_describe_itself_fails_validation`,
`test_builtin_profiles_declare_only_profile_explicit_backends`,
`test_retired_backends_are_rejected`,
`test_invalid_selection_and_unknown_schema_key_fail_with_actionable_errors`,
`test_skill_links_and_prompt_paths_cannot_escape_the_profile`,
`test_selected_backends_reject_controls_their_adapters_cannot_enforce`) fail
the same way, each naming `profiles/openspec-builder` as missing.

```
tests.test_project_runtime_selection
```
```
FAILED (failures=1, errors=6)
Ran 21 tests in 0.266s
```
The new `test_a_project_declaring_openspec_is_refused_and_not_opened_under_the_default`
fails because `load_profile(None, ..., selection=declaring "openspec")` still
resolves `openspec` successfully today (`ProjectRuntimeError not raised`);
the existing `test_a_project_declaring_builder_is_refused_and_not_opened_under_the_default`
still passes unmodified (`builder` was already refused by the prior cycle);
the two-roster, changed-profile, created-project and `ProfileRuntimeTableTest`
cases all fail resolving `profiles/openspec-builder` (`package is
unavailable`), the intended reason given the profile has not moved yet.

```
tests.test_project_preparation
```
```
FAILED (failures=1), 1 skipped
Ran 43 tests in 4.814s
```
Only the new fallback test fails, for the intended reason:
`test_a_project_declaring_no_profile_is_listed_under_the_shop_default` sees
`'openspec' != 'openspec-builder'`. The one skip
(`WorkspaceSolidAcceptanceTest`) is pre-existing and environmental (no
development workspace `machinome` installation here), unrelated to this
change.

```
tests.test_openspec_tools
```
```
FAILED (errors=2)
Ran 18 tests in 26.473s
```
`test_a_profile_may_declare_the_capability_and_unknown_names_still_fail` and
`test_openspec_declares_the_capability` both fail resolving
`profiles/openspec-builder` (`package is unavailable`).

```
tests.test_role_contracts
```
```
FAILED (errors=2)
Ran 4 tests in 0.003s
```
Both tests that load a profile by ID fail resolving `profiles/openspec-builder`:
`test_runtime_prompts_are_profile_owned_and_runtime_skills_are_allowlisted`
(loop now `("openspec-builder", "fordesmac")`) and
`test_builder_is_direct_and_preserves_disassembled_leaf_first_red` (reads
`profiles/openspec-builder/builder.md`, which does not exist until the `git
mv`).

```
tests.test_documentation
```
```
FAILED (failures=1)
Ran 24 tests in 1.999s
```
Only `test_project_configuration_reference_names_the_table` fails, for the
intended reason: `'openspec-builder' not found in` the current
`docs/reference/project-configuration.rst`, which still names only
`openspec` and `fordesmac`. `test_profiles_reference_matches_the_shipped_profiles`
still passes today because `docs/reference/profiles.rst` already headings
`` ``openspec`` `` and `` ``fordesmac`` `` that way; its red is recorded at
task 2.6 instead, as the design and tasks direct.

```
tests.test_project_open
```
```
FAILED (failures=12, errors=1)
Ran 14 tests in 0.744s
```
Every case fails resolving `profiles/openspec-builder` (`package is
unavailable`), including the new `make_project` default (`profile: str =
"openspec-builder"`) and the explicit `registry.create("", "new_engine",
"openspec-builder")` call.

```
tests.test_floor_api
```
```
FAILED (failures=12, errors=1)
Ran 18 tests in 20.632s
```
The whole module fails in `setUp` or per-test opening: every project opened
under the rewritten default/fixtures (`profile = "openspec-builder"`,
including the `POST /api/projects` bodies) fails resolving
`profiles/openspec-builder`. Five cases that do not open a project under the
renamed profile pass unmodified.

```
tests.test_orchestrator
```
```
FAILED (failures=5, errors=5)
Ran 75 tests in 17.895s
```
`ProfileOrchestratorTest`'s `_resolved_profile("openspec-builder")` calls and
`SessionOpeningTest`'s fixtures (now `profile = "openspec-builder"`) fail the
same way; `test_preparation_and_agent_start_failures_leave_no_partial_session`
fails because the error text it expects ("backend start failed") is
preempted by the earlier, unrelated "profile openspec-builder... unavailable"
error.

```
tests.test_shop_lifecycle_e2e
```
(Chromium via Playwright; frontend installed and built once —
`npm --prefix floor/frontend install && npm --prefix floor/frontend run
build` — to give the harness a bundle to serve, with no source edits yet:
the sheet still shows a button named exactly `OpenSpec`, not
`OpenSpec Builder`.)
```
FAILED (failures=15, errors=3)
Ran 23 tests in 103.459s
```
`test_project_creation_opens_a_workspace_and_close_returns_to_the_hub` errors
waiting for a button named `OpenSpec Builder` that does not exist yet (the
sheet still offers a button named exactly `OpenSpec`, which is not a
substring match for the two-word name). Every other failing case opens a
fixture project declaring `profile = "openspec-builder"` (the updated
`_make_project` default) and either errors waiting for text
`openspec-builder · open` / `closed · openspec-builder` /
`open · openspec-builder`, or fails because the session itself failed to open
(`profile openspec-builder... unavailable`). Five cases pass unmodified (hub
identity, codex backend listing, the plain creation-sheet smoke test, the
multi-model card test, and the hub-cards-are-links test — none of them touch
profile resolution or the renamed button/description/text).

## Fixes made while writing the red run

None: every module failed for the behaviour under test on the first run: an
unavailable `profiles/openspec-builder` package, a default still resolving
to `openspec`, a still-successful `openspec` load, a manual page still naming
only the old profile name, or a missing exact-named button/text. No test
needed correction for an import or fixture error before its failure was
meaningful.

## Red recorded after the move (task 2.6)

After `git mv profiles/openspec profiles/openspec-builder` and the label
change (section 2), before touching the manual:

```
tests.test_documentation
```
```
FAILED (failures=3)
Ran 24 tests in 1.500s
```
`test_profiles_reference_matches_the_shipped_profiles` fails twice, for the
intended reason: `docs/reference/profiles.rst` has no `` ``openspec-builder`` ``
section heading (profile subtest) and the `builder` row's 700-character
window does not contain `OpenSpec Builder` (agent subtest, still reading
`Builder`). `test_project_configuration_reference_names_the_table` still
fails as recorded above (the page still names only `openspec`).

## Green (sections 2-6, task 7.1)

After sections 2-6 (the `git mv`, the label and prompt rewrite, the loader
default and fallbacks, the frontend sheet, the manual pages, and the
records), every module touched in sections 1 and 4 was run green
(`tests.test_runtime_profiles`, `tests.test_project_runtime_selection`,
`tests.test_project_preparation`, `tests.test_openspec_tools`,
`tests.test_role_contracts`, `tests.test_documentation`,
`tests.test_broker`, `tests.test_source_files`, `tests.test_codex_backend`,
`tests.test_codex_worker_adversarial`, `tests.test_codex_git_identity`,
`tests.test_codex_selection`, `tests.test_codex_preflight`,
`tests.test_opencode_backend`): 194 tests, all passing (one pre-existing
environmental skip, `WorkspaceSolidAcceptanceTest`).

Then the four named checks (task 7.1), all run from the worktree with the
worktree on `PYTHONPATH` and the workspace venv on `PATH`:

```
python -m unittest discover -s tests -v
```
First run: `Ran 500 tests in 162.855s / FAILED (failures=1, skipped=1)`.
The one failure,
`ClaudeBackendAcceptanceTest.test_first_delivery_reports_last_pending_status_on_readiness_timeout`,
races a 0.05 s MCP-readiness timeout against a 0.2 s injected delay under
full-suite load and is untouched by this change (no `openspec` or `Builder`
text in it). Run alone three times in a row it passed every time
(`Ran 1 test in ~0.27s / OK` each run); a second full-suite run passed
clean: `Ran 500 tests in 162.855s / OK (skipped=1)`. The one skip
(`WorkspaceSolidAcceptanceTest`) is the same pre-existing environmental skip
as every earlier run (no development-workspace `machinome` installation in
this sandbox).

```
npm --prefix floor/frontend run test
```
```
> tsc -b --pretty false
```
Clean (no output, no error): every rewritten profile/label string in
`main.tsx` type-checks.

```
npm --prefix floor/frontend run build
```
Succeeds; `floor/static/` regenerated (not staged).

```
scripts/test-e2e
```
```
Ran 51 tests in 80.757s
OK
```
No skips this run (the real-viewer-bundle case that was a named skip in the
prior cycle's evidence ran green here).

```
python -m sphinx -b html -n -W --keep-going docs docs/_build/html
```
```
build succeeded.
```
No warnings. The five changed pages
(`reference/profiles.html`, `reference/project-configuration.html`,
`working-with-agents.html`, `the-floor.html`, `opening-a-project.html`)
were read in the built HTML: every `openspec-builder` and `OpenSpec Builder`
occurrence is where the plan calls for it; the only remaining bare
`openspec` occurrences are the `openspec` CLI mention on
`opening-a-project.html` and the project's own `openspec/` record mention
on `working-with-agents.html`, both intentionally unchanged.

## Pixel evidence

A floor was started from the worktree on an ephemeral port against a
temporary projects directory under the scratchpad (never the pilot's
catalogue, never port 9000/9010), with one bare project declaring no
profile. Captured with Playwright, then the floor was stopped (its whole
process tree):

- `openspec-builder-hub-bare-project-card.png` — the bare project's hub
  card reads `closed · openspec-builder · just now`.
- `openspec-builder-hub-new-project-sheet.png` — the "New project" sheet
  opens with **OpenSpec Builder** already selected (highlighted), its
  description "One agent keeping the project's design in an OpenSpec
  record" legible at the sheet's width, and **Fordesmac** ("Four-agent
  mechanical shop") offered beside it.

A second floor, with a real project opened (the fake-machinome fixture) and
the agent manifested as `{"role": "builder", "label": "OpenSpec Builder"}`,
was captured at the narrow width (760×900) the Agents e2e test uses:

- `openspec-builder-workspace-narrow-conversation.png` — the workspace
  title reads `openspec-builder · open` (exact); the Model panel's Agents
  list and the conversation's attribution both read `OpenSpec Builder`
  without truncation (the label wraps to two lines in the narrow roster
  list, which is wrapping, not truncation).
- `openspec-builder-workspace-narrow-agents.png` — the Agents area's roster
  row, its header ("OpenSpec Builder · waiting"), the Session panel
  (`openspec-builder · direct`) and the activity footer attribution all
  read `OpenSpec Builder` legibly at the narrow width.

All four PNGs are at
`/tmp/claude-1000/-home-asa-devel-machinome/76a82843-caa1-4339-bdf6-b0cac11a6fc1/scratchpad/pixels/`.

## Closing the cycle (task 7.2)

Not yet run. Reserved for after the reviewer's approval, per the applier's
briefing.
