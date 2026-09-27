## 1. Red first

- [ ] 1.1 Repoint `tests/test_documentation.py::test_the_manual_states_the_release` to `0.7.1 — 27 September 2026`, `Machinome 0.7.1` and version 0.7.1; run it and record the failure on the current tree.

## 2. Version

- [ ] 2.1 Move the version to 0.7.1 in `pyproject.toml`, `machinome_viewer/__init__.py`, `machinome_viewer/widget/package.json` and both `version` fields of `package-lock.json`; rebuild the bundle through `ensure_current` (`npm run build`, never `npm ci`, in this worktree) and check the banner says `machinome-viewer 0.7.1 - viewer API 27`.

## 3. Records

- [ ] 3.1 Add the `0.7.1 — 27 September 2026` section to `CHANGELOG.md` above `0.7.0`: released with Machinome 0.7.1 and numbered with it; the published 0.7.0 source renumbered; API 27 and document versions 1 through 13 unchanged; a 0.7.0 viewer reads a 0.7.1 export because frames and mates compile to what the document already carries.
- [ ] 3.2 Update `docs/index.rst`, `docs/installation.rst`, `docs/compatibility.rst` (the "three version numbers" bullet), `docs/reference/cli.rst`'s `describe` example, `README.md` and `context7.json` to 0.7.1 and its date; leave "API 27, the 0.7.0 release" on the compatibility page, which is when the API arrived.
- [ ] 3.3 Add the dated 0.7.1 note to `workflow/release-0.7.md`.

## 4. Green and checked

- [ ] 4.1 Run the Python suite and the widget suite; build the manual with warnings as errors and read the home page as a reader.
- [ ] 4.2 Sync the spec deltas, archive the change with its evidence, and commit the completed state; state that `scripts/check-dist`, the tag, the push and the upload are made from the primary checkout after integration.
