## 1. Red first

- [x] 1.1 Extend `tests/test_documentation.py`: expect `workflow/release-0.7.md`
      and no `release-0.2.md`; refuse "unreleased" in `docs/`, `README.md` and
      the changelog's first section; expect the changelog's first heading to
      name 0.7.0 and 21 September 2026; keep the describe-example version
      cross-check. Run it and record the failures.

## 2. Version

- [x] 2.1 Set 0.7.0 in `pyproject.toml`, `machinome_viewer/__init__.py` and
      `machinome_viewer/widget/package.json`; rebuild the bundle with
      `npm run build` only and confirm its banner.

## 3. Manual

- [x] 3.1 `index.rst`: replace the unreleased note with the release statement.
- [x] 3.2 `installation.rst`: index installation through `machinome[viewer]`
      first, source build as the contributor's path, framework link to
      `start/install.html`.
- [x] 3.3 `compatibility.rst`: release statement; upgrade link to
      `project/upgrading.html`.
- [x] 3.4 `sharing.rst`: export guide link to `tutorial/10-share.html`, CLI
      link to `reference/cli.html`.
- [x] 3.5 `reference/running.rst`: move the stop and time-drive paragraphs into
      a "Stops and time drives" section after "Request motion"; drop the
      project name. `reference/cli.rst`: describe example says 0.7.0.

## 4. Changelog and records

- [x] 4.1 `CHANGELOG.md`: a `0.7.0 — 21 September 2026` user-facing section;
      move the 0.2.0 and 0.1.0 development sections verbatim to
      `workflow/archive/changelog-before-0.7.md` with a pointer.
- [x] 4.2 Rename `workflow/release-0.2.md` to `workflow/release-0.7.md` and
      restate it for 0.7.0, API 23, documents 1–10; update `README.md`,
      `workflow/README.md` and `workflow/documentation.md` pointers and the
      unreleased-notice instruction.

## 5. Validate and close

- [x] 5.1 Strict Sphinx build, `tests/test_documentation.py`, the widget test
      suite, the Python suite, and the browser docs check; record evidence in
      `evidence.md`.
- [x] 5.2 Sync the two modified requirements into the baseline specs, archive
      the change, commit.
