## 1. Evidence baseline

- [ ] 1.1 Record the base: `git -C <bench> log --oneline -4` is the planning commit on top of the line's head holding `join-studio` and `viewer-seam` (the orchestrator fast-forwards the bench before the planning commit); the worktree clean but this change. Start `evidence.md` in this change with it. Confirm the seam landed as this design reads it: `packages/machinome/machinome/viewer/__init__.py` defines `CaptureRequest`, `require` and `ViewerLacks`; `packages/machinome-viewer/machinome/viewer/web/__init__.py` defines `capture`, `serve` and `describe`; `packages/machinome/machinome/manager/viewer.py` prints `require('web', 'embed', 'machinome viewer').describe()`; `packages/machinome-viewer/pyproject.toml` still declares `[project.scripts] machinome-viewer`. If any differs, stop and report.
- [ ] 1.2 Sync the bench venv from the lock: `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12`; record the package count and that `<bench>/.venv/bin/machinome-viewer` exists. Record the base suite count from the seam's archived `evidence.md` (do not rerun it). One pytest process at a time, and none while another bench's suite runs (`pgrep -af "WTs/v0.9-joins-.*[p]ytest"`; wait on the PID).
- [ ] 1.3 The requirements this change modifies, against the landed baseline: for each of `cli` "Viewer command", `cli-startup-cost` "The viewer command loads no geometry stack", `viewer-distribution` "The framework resolves the Machinome viewer", `viewer-seam` "The viewer is chosen by the flag, the project, or the command's default" and "The web viewer runs in the framework's process", `framework-identity` "The framework is the package directory `packages/machinome` of a monorepo" and `user-documentation` "The browser viewer is documented in the manual", compare the text in `openspec/specs/<capability>/spec.md` with the text this change's delta was copied from (the seam's delta at its planning, or the line's spec for `user-documentation`). Where the landed text differs, re-apply this change's edits (design.md Decision 12) to the landed text in the delta, scenario titles kept, and record each difference. `openspec validate viewer-command --strict`.
- [ ] 1.4 Record the lint base: `env -C <bench> make lint 2>&1 | tail -3` and the flake8 line count.
- [ ] 1.5 The originating baselines, with the bench venv at the base, into the scratch directory (never the bench): a copy of `packages/machinome/docs/tutorial`; its carry pose staged by `machinome snapshot --viewer web --drive crank=3580` with a wrapper that copies the staging aside before the web provider's `withdraw` removes it (design.md probe 2's `stage_keep.py`, patched on `machinome.viewer.web.withdraw`); then `machinome-viewer capture` on five fresh copies of the staging with design.md probe 3's five option sets; each image's SHA-256 recorded and each looked at. A copy of `Vibecoded-demos/gear-shift` by `git -C <that repo> archive HEAD`, built with `machinome build`, served by `machinome-viewer serve` and photographed in Chromium with design.md probe 11's script.

## 2. Red first (nothing of the implementation exists yet)

- [ ] 2.1 `tests/test_manager_viewer.py`: the verbs of design.md Decision 10's first row, the existing three tests rewritten to patch the seam. Run it. Expected red: the verb tests fail on argparse ("invalid choice" or "unrecognized arguments") since `Viewer().add_arguments` registers no verb; the bare-report tests green. Record each reason.
- [ ] 2.2 `tests/test_viewer_seam.py`: `CaptureRequest`'s parts, the `ValueError` when the notation and a part are both given, the web provider's `capture` handing the parts to `mount_options` (its `Capture` patched), absent parts left `None`, the notation resolved by `parse_camera`. Expected red: `TypeError` on the keyword `eye`.
- [ ] 2.3 `tests/test_cli_lazy_imports.py`: `machinome viewer -h` and `machinome viewer capture -h` import no provider; `machinome viewer describe` exits 0 and imports no server, capture, session, staging, `fastapi`, `uvicorn`, `playwright` or CAD library. Expected red: `machinome viewer describe` exits 2.
- [ ] 2.4 `tests/test_machinome_identity.py`: no `packages/*/pyproject.toml` but the core's declares `[project.scripts]`. Expected red: `packages/machinome-viewer/pyproject.toml` declares `machinome-viewer`.
- [ ] 2.5 `tests/test_docs_structure.py`: `CommandReferenceTest.test_the_viewer_command_has_its_section` (the label `viewer-command`, the three verbs as `machinome viewer <verb>`, every option string the command's parser declares, read from `Viewer().add_arguments` on a fresh parser and its subparsers, and `:doc:\`/reference/viewer/cli\``); `STALE` gains the three spellings of the former command, written split so the test file does not match itself, `RECORDS` allowing them on `project/changelog.rst` and `project/upgrading.rst`. Expected red: no section; `reference/viewer/cli.rst`, `compatibility.rst`, `troubleshooting.rst` and `howto/share-an-export.rst` spell the former command.
- [ ] 2.6 The viewer's tests, from `packages/machinome-viewer`: `tests/test_machinome_identity.py` (the manifest declares no `scripts`); `tests/test_cli.py` (design.md Decision 10: `cli.main` runs the framework's command, `main([])` prints the report, `--start-frontend` exits 2, the module entry through the interpreter kept; the describe, capture and serve tests moved to the core's `test_manager_viewer.py` in 2.1); `tests/test_documentation.py` without `test_cli_options_are_all_documented`. Expected red: the scripts table is there; `main([])` prints help; `--start-frontend` is accepted.
- [ ] 2.7 `scripts/check-dist`'s `machinome-viewer` row (design.md Decision 9), edited now: the code asserting no `console_scripts` entry and no `bin/machinome-viewer`, the commands list. Run `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` in the background (about seven minutes), its output under the scratch directory. Expected red: the viewer's smoke fails on the `console_scripts` assertion, the wheel still declaring `machinome-viewer`; record the line. `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [ ] 2.8 Record in `evidence.md` every red of 2.1 to 2.7 with its reason, and the tests that are green at the base and must stay so.

## 3. The seam's request

- [ ] 3.1 `packages/machinome/machinome/viewer/__init__.py`: `CaptureRequest` gains `eye`, `target`, `up` and `fov`, default `None`, and the `__post_init__` refusal of design.md Decision 3; nothing else of the seam changes (`git diff` shows that hunk).
- [ ] 3.2 `packages/machinome-viewer/machinome/viewer/web/__init__.py`: `capture` resolving `camera` with `parse_camera` into the four parts, else taking the parts as given, then `mount_options` with `view` only when the eye is given. `tests/test_viewer_seam.py` green; the snapshot's tests (`tests/test_snapshot.py`, `tests/test_web_viewer_capture.py`) green.

## 4. The command

- [ ] 4.1 `packages/machinome/machinome/manager/viewer.py` as design.md Decisions 1 to 4 state it: the docstring, the verbs and their options (the three parsers moved from the viewer's `cli.py`), `--viewer` on each verb, the dispatch table, the document refusal of `capture`, `--time` checked before the viewer is resolved, the staging never withdrawn, `serve`'s wait with the SIGINT and SIGTERM handling, every refusal on standard error with nothing on standard output; the bare report unchanged. Imports at module level: the standard library alone.
- [ ] 4.2 Run `tests/test_manager_viewer.py`, `tests/test_cli_lazy_imports.py`, `tests/test_cli.py`, `tests/test_viewer_seam.py`: green. The serve test against a bound port: exit 1 within 10 s; if it hangs or exits otherwise, stop and report (the seam's `serve()` does not raise as its Decision 7 requires).
- [ ] 4.3 By hand on the bench venv, from the scratch directory: `machinome viewer`, `machinome viewer describe` and `python -m machinome.viewer.web describe` byte-identical (`cmp`); `machinome viewer -h`; each refusal of design.md probe 5. Record outputs and statuses.

## 5. The console script and the module entry

- [ ] 5.1 `packages/machinome-viewer/pyproject.toml`: the `[project.scripts]` table removed, nothing else (`git diff`). Re-sync the bench venv (`uv sync --python 3.12`; if the editable install keeps the script, `uv sync --reinstall-package machinome-viewer`); `<bench>/.venv/bin/machinome-viewer` no longer exists and `importlib.metadata.distribution('machinome-viewer').entry_points` holds no `console_scripts`; record both.
- [ ] 5.2 `packages/machinome-viewer/machinome/viewer/web/cli.py` reduced to design.md Decision 7's `main`, with its header and a module docstring; `__main__.py`'s code unchanged, its docstring naming the framework's `machinome viewer`; the docstrings of `bundle.py` and `capture.py` naming `machinome viewer`. `git diff` of `__main__.py` shows the docstring alone.
- [ ] 5.3 Run the viewer's suite from `packages/machinome-viewer` (`make test PKG=machinome-viewer`, or its pytest as the contributor guide states): green; the core's `tests/test_machinome_identity.py` green.

## 6. The core of the set

- [ ] 6.1 `context7.json`'s viewer line (design.md Decision 9), in place. The layout gate's tests green. (`scripts/check-dist`'s row is 2.7's; it turns green in 9.4.)

## 7. The manual

- [ ] 7.1 `docs/reference/cli.rst`: the section of design.md Decision 11 between `machinome export` and `machinome models`, and `develop`'s `--debug-builder` line. `test_docs_structure.py`'s section test green.
- [ ] 7.2 `docs/reference/viewer/cli.rst` as Decision 11 states it (kept, retitled "The viewer command", unless the orchestrator's review of Open Questions 5 says otherwise); `reference/viewer/compatibility.rst`, `troubleshooting.rst`, `howto/share-an-export.rst`. The viewer's `test_documentation.py` (the `describe` example) green; `test_docs_structure.py` green.
- [ ] 7.3 `docs/project/upgrading.rst`: the subsection "The viewer's command" in the 0.9 section the seam began.

## 8. The records

- [ ] 8.1 `HISTORY.rst` and `docs/project/changelog.rst`: the `Unreleased` bullet of design.md Decision 14, after the seam's. `test_release_records.py` and `test_profile_documentation.py` green.
- [ ] 8.2 `docs/architecture.md`: the viewer section's sentence on the command (Decision 14).
- [ ] 8.3 `docs/adrs/BUILD/ADR-196-the-viewer-s-verbs-are-the-framework-s-viewer-command.md`, Status Proposed, as Decision 14 outlines it; the status lines of ADR-188 and ADR-194 naming the amendment; the index line in `docs/adrs/README.md`.
- [ ] 8.4 The viewer's own record: `CHANGELOG.md`'s `Unreleased` (the existing bullet's words on the command removed in place, one bullet added); its specs `development-server`, `snapshot-capture`, `user-documentation` and `viewer-distribution` and its `openspec/config.yaml` brought current in place where they state the console script (design.md probe 12's lines); its decision log untouched. `git -C <bench> grep -nE "machinome-viewer (describe|serve|capture)"` outside `archive/`, `releases/`, `workflow/`, the ADRs, the changelogs' released sections and this change: no line; record the command and its output.

## 9. Validation

- [ ] 9.1 The suite on the bench venv, one process (check no other bench's suite runs first): `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q` in the background with its output in the scratch directory. Expected: green; the count against 1.2's base, each new, moved and removed test accounted for. A run that dies with EMFILE is rerun once and reported.
- [ ] 9.2 The viewer's, the movie's and the studio's suites from their directories; `make lint` against 1.4's base.
- [ ] 9.3 `make docs` (warnings as errors), in the arrangement the seam's Decision 13 left; record the exit and the time.
- [ ] 9.4 `make check` (`scripts/check-dist` on the tree and on a clean copy of the tracked files). Expected: every member built and checked as at the base; the viewer row printing its smoke line, its three commands exit 0, and no `machinome-viewer` in the throwaway venv's `bin`; nothing uploaded. Record the archives' counts.

## 10. The originating check

- [ ] 10.1 On a fresh staging of 1.5's carry pose, `machinome viewer capture` with the five option sets of 1.5, each on its own copy of the staging; each image against 1.5's: 0 differing pixels and the SHA-256 equal; each looked at; the staging directories equal after the capture (`diff -rq`).
- [ ] 10.2 `machinome viewer serve` of a fresh build of the gear-shift copy, opened in Chromium with 1.5's script: the page photographed and looked at against 1.5's (the same gearbox, sidebar and camera; the model's own animation may move the gears), SIGINT exit 0; once more with SIGTERM, exit -15; then a port already taken, exit 1 with one `Error:` line. `ss -ltn` and `pgrep -af "[m]achinome viewer serve"` empty after each.
- [ ] 10.3 The studio reads the report: from the bench venv, `machinome.studio.preparation.resolve_viewer_bundle(['<bench>/.venv/bin/machinome'])` returns the bundle path and API 29; record it.
- [ ] 10.4 Record in `evidence.md` every command, count and image of groups 3 to 10.

## 11. Stop for review, then the archive

- [ ] 11.1 Stop before any commit and report to the orchestrator: the reds of group 2, the differences found in 1.3, the counts of 1.2, 5.1, 9.1 to 9.4, the images of 10.1 and 10.2, and anything that departed from the design. Resume only on the orchestrator's message.
- [ ] 11.2 After the review: ADR-196 Accepted; `docs/adrs/README.md` updated.
- [ ] 11.3 Sync the delta specs into `openspec/specs/` (each modified requirement whole, scenario titles kept; the added `viewer-seam` requirement). `openspec validate --specs --strict` green.
- [ ] 11.4 `openspec archive viewer-command` (the archive directory `2026-10-<day>-viewer-command`); `openspec validate --all --strict` green. Leave everything uncommitted for the orchestrator.
- [ ] 11.5 Not the applier's: the implementation commit, the Curta's eleven tools (design.md Decision 13) if the pilot wants them moved, and the integration into `v0.9-joins` are the orchestrator's; the site's intake (three files of its repository) and the workspace contract's line (`workspace-consistency`) are the pilot's to order.
