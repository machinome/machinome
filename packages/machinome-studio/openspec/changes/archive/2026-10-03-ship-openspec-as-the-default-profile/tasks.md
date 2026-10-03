## 1. Prove the new behaviour red first

Every test below is written against the current tree (with `profiles/builder/`
still in place and the default still `fordesmac`) and run to show it fails for
the stated reason before any code changes. Run from the worktree with
`PYTHONPATH=<worktree>` and the workspace venv, after confirming
`python -c "import floor; print(floor.__file__)"` prints the worktree. Record
the red run (module, test, failure line) in the implementation commit message
or a short evidence note in this change directory.

- [x] 1.1 `tests/test_runtime_profiles.py`: the default test asserts `load_profile(None, shop_root=ROOT).id == "openspec"`; the shipped-profiles test loads `openspec` and asserts its roster is exactly `[("builder", "Builder")]`, user-facing, direct mode; a new test asserts `load_profile("builder", shop_root=ROOT)` raises the unavailable-package `ProfileError`; the every-shipped-profile loop iterates `("openspec", "fordesmac")`.
- [x] 1.2 `tests/test_project_runtime_selection.py`: a project declaring `profile = "builder"` is refused with a `ProjectRuntimeError` naming its `pyproject.toml` and the value `'builder'`, and is not opened under `openspec`; the two-roster and changed-profile cases declare `openspec` and still key the selection to the agent `builder`; the created-project case writes and reads `openspec`.
- [x] 1.3 `tests/test_project_preparation.py`: a new listing test asserts a project declaring no profile is listed with profile `openspec` (the fallback is untested today); the declared-profile listing and the creation tests use `openspec`.
- [x] 1.4 `tests/test_project_open.py`, `tests/test_floor_api.py`, `tests/test_orchestrator.py`: project fixtures, creation requests and hub events use the profile `openspec` (default arguments of `make_project` / `_make_project`, `registry.create(..., "openspec")`, the `creating` event, the `session.profile.id` assertion, the `POST /api/projects` bodies and `profile = "openspec"` pins); add one open test for a project with no declaration opening exactly the agent `builder`.
- [x] 1.5 `tests/test_openspec_tools.py` and `tests/test_role_contracts.py`: the OpenSpec-capability and prompt-contract tests load the `openspec` profile and read `profiles/openspec/builder.md`; the Fordesmac exclusion test is unchanged.
- [x] 1.6 `tests/test_documentation.py`: the configuration-reference pin also requires `openspec`; the profiles-reference test requires each shipped profile's section heading (the name in double backticks followed by an `=` underline), not merely the name in double backticks, so a mention of the `openspec` CLI cannot satisfy it.
- [x] 1.7 `tests/test_shop_lifecycle_e2e.py`: the creation test opens the sheet, asserts the OpenSpec choice is labelled `OpenSpec`, carries a description, is selected and that Fordesmac is offered, creates without clicking a profile, and waits for `creating · openspec`, `closed · openspec`, `open · openspec`; the multi-model fixture at the `_make_project` helper declares `profile = "openspec"` and the workspace title wait becomes `openspec · open`. Agent rows, `role="builder"` and the `Builder` label stay.
- [x] 1.8 Run the modules above and record each failing for the intended reason (unavailable profile, default mismatch, missing preselection), not for an import or fixture error.

## 2. Rename the profile and move the default

- [x] 2.1 `git mv profiles/builder profiles/openspec`. Confirm the two skill symlinks still resolve to `shop-skills/machinome` and `shop-skills/machinome-api`, and that `profile.toml` and `builder.md` are byte-identical to before the move (agent `builder`, label `Builder`, prompt `builder.md`, `user_agent = "builder"`).
- [x] 2.2 `floor/profiles.py`: `load_profile(..., default="openspec")`. Add no alias, no special case and no warning for `builder`.
- [x] 2.3 `floor/preparation.py` `_project_listing`: both fallbacks (unreadable project and undeclared profile) become `"openspec"`.
- [x] 2.4 `floor/backends/probe.py` `_configured_models`: iterate `("openspec", "fordesmac")`.
- [x] 2.5 `grep -rnw builder floor/` and confirm every remaining hit means the agent; no remaining `"fordesmac"` default literal outside the probe tuple.

## 3. Preselect OpenSpec in the hub sheet

- [x] 3.1 `floor/frontend/src/main.tsx` `Hub`: profile state typed `"openspec" | "fordesmac" | ""` and initialised to `"openspec"`; the provisional-card fallback for an event without a profile becomes `"openspec"`.
- [x] 3.2 The chooser iterates `["openspec", "fordesmac"]`, labels them `OpenSpec` and `Fordesmac`, and describes OpenSpec as "One agent, Builder, keeping an OpenSpec design record" while Fordesmac keeps "Four-agent mechanical shop". Keep the client guard and the server's required `profile` field.
- [x] 3.3 Session panel, red first: a broker/API test asserts the run snapshot carries `work_mode` (`direct` for `openspec`, `delegated` for `fordesmac`), and the e2e Agents test (whose run fixture is fetched from the live session and so carries `work_mode`) asserts the Session panel of a direct project reads `openspec · direct`; both fail first. Then `floor/app.py` `run()` adds `"work_mode": self.profile.work_mode` beside `profile_id`, the frontend `Run` type gains `work_mode: "direct" | "delegated"`, and the Agents workspace's Session panel renders `{profile_id} · {work_mode}` instead of the literal `delegated`.
- [x] 3.4 Rebuild the frontend (`floor/static/`, never staged) and inspect the sheet's pixels in the browser: OpenSpec shown selected on open, Fordesmac selectable, the description legible at the sheet's width.

## 4. Follow the rename through the remaining tests

- [x] 4.1 Replace the profile argument `"builder"` with `"openspec"` wherever it names the profile and leave every agent use alone, in `tests/test_broker.py`, `tests/test_source_files.py`, `tests/test_opencode_backend.py` (`profile_id=`), `tests/test_codex_backend.py`, `tests/test_codex_worker_adversarial.py`, `tests/test_codex_git_identity.py`, `tests/test_codex_selection.py`, `tests/test_codex_preflight.py`, and any other module `grep -rnE 'load_profile\("builder"|_resolved_profile\("builder"|profiles" / "builder"|profile = \\?"builder' tests/` still finds. `role="builder"`, `open_role("builder", ...)`, `open_thread("builder", ...)`, `manifest("builder", "Builder")`, agent keys and `--role builder` stay. (`tests/test_opencode_backend.py` also needed its `OpenCodeSelectionTest` profile-id loop renamed; the literal grep missed it because the profile id there comes from a tuple iterated into `load_profile(profile_id, ...)`, not a literal `load_profile("builder"` call — found by running the module, not by the grep alone.)
- [x] 4.2 `tests/test_floor_entrypoint.py`'s rejected `--profile builder` argument may stay: the option is what is rejected, not the value.
- [x] 4.3 Run every module touched in sections 1 and 4 green.

## 5. Manual

Under the workspace's `write-the-manual` skill: the profile is named "the
``openspec`` profile" where the CLI or the record could be meant.

- [x] 5.1 `docs/reference/profiles.rst`: the direct profile's section becomes ``openspec`` (agent row unchanged: ``builder``, Builder) and is presented first as the default.
- [x] 5.2 `docs/reference/project-configuration.rst`: the example and the `profile` entry name ``openspec`` and ``fordesmac`` as the shipped names and ``openspec`` as the default; state that a project declaring a name the studio does not ship, including the former ``builder``, is refused and not given the default.
- [x] 5.3 `docs/working-with-agents.rst`: a project recording no profile opens under ``openspec``; the profile section is headed for the profile (OpenSpec) and introduces Builder as its agent; "under ``builder``" in "Where the work is recorded" becomes "under ``openspec``".
- [x] 5.4 `docs/the-floor.rst` ("**Builder** under ``openspec``") and `docs/opening-a-project.rst` ("``openspec`` when it declares none").
- [x] 5.5 Leave `docs/project/status.rst` and `docs/troubleshooting.rst` (they name only Fordesmac's librarian); confirm no other page, README or docstring names `builder` as a profile.

## 6. Records

- [x] 6.1 Promote `adr-0034.md` to `docs/adrs/0034-ship-the-openspec-profile-as-the-default.md` with status Accepted and the acceptance date (the draft keeps its date placeholder until then). In `docs/adrs/README.md`, in the index's own style, row 0011 becomes "Accepted (amended by 0012, 0016, 0017, 0019, 0025, 0032, and 0034)", row 0019 becomes "Accepted (amended by 0034)", and row 0034 is added in chronological order; the status lines inside ADRs 0011 and 0019 gain 0034 in the form each file already uses.
- [x] 6.2 Rewrite `docs/architecture-overview.md` § Profile-defined runtime: the fallback sentence names `openspec`; remove the stale "The option overrides a project declaration for one run without modifying it."; the `OpenSpec` capability paragraph says only the `openspec` profile declares it, for Builder; the profile table lists `openspec | direct | Builder | Builder` first, then `fordesmac`. Builder-the-agent sentences stay.
- [x] 6.3 `AGENTS.md`: "`openspec` (the default) and `fordesmac` are the profiles today"; "the builder's own OpenSpec record" names the agent and stays (capitalised as Builder if the sentence is touched).
- [x] 6.4 `CHANGELOG.md` under `## Unreleased`: rewrite the "Two profiles" bullet with `openspec` as the default (one agent, Builder, keeping the project's design in an OpenSpec record) and `fordesmac`, and add a **Breaking** note: a project declaring no profile now opens under `openspec`, and a project declaring `builder` is refused until its declaration names `openspec`. Add a correction line: the Agents area's Session panel reported every profile as delegated and now shows the profile's own work mode.
- [x] 6.5 `workflow/ongoing/reconstructions-in-the-studio.md`: "the builder profile" (the one use that names the profile) becomes "the openspec profile"; the uses naming the agent stay.

## 7. Validate and close the cycle

- [x] 7.1 Run the whole Python suite and `scripts/test-e2e` from the worktree with the worktree on `PYTHONPATH`; report environmental failures honestly.
- [x] 7.2 Open the hub from the worktree and inspect the sheet and a bare project's card (`openspec`) in the browser.
- [x] 7.3 `openspec validate ship-openspec-as-the-default-profile --strict`, sync the ten spec deltas into `openspec/specs/`, archive the change, and create the implementation commit. Integration, push and the catalogue's project declarations are the pilot's and the reviewer's, outside this change.
