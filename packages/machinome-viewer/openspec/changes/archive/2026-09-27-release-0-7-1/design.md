## Context

The 0.7.0 record was cut on 21 September and folded twice on 23
September by editing this same set of files (`release-the-viewer-as-0-7`,
then the two folds recorded in `workflow/release-0.7.md`). The 0.7.0
distributions on PyPI (uploaded 26 September 2026) carry the sha256 of
the files built from `1e67c83` in `dist/0.7.0-2026-09-25/`; `main` is
`1e67c83`. The GitHub `v0.7.0` tag points at `0761145`, two commits
earlier, without the licence-test and full-screen-button fixes the
published wheel contains; that is the pilot's to move or leave.

## Goals / Non-Goals

**Goals:**
- Every reader-facing record states 0.7.1, released with Machinome 0.7.1
  on 27 September 2026, API 27, document versions 1 to 13.
- The bundle banner carries 0.7.1, so `describe` and the banner agree
  with `pyproject.toml`.
- The changelog tells a reader that 0.7.1 changes nothing in the viewer
  and why a 0.7.0 viewer still reads a 0.7.1 framework's exports.

**Non-Goals:**
- Any widget, server or capture change; any API or document version move.
- Tags, pushes, uploads, Read the Docs.

## Decisions

1. **Renumber, do not re-describe.** The 0.7.1 section is short and
   says the viewer is unchanged; the 0.7.0 section keeps the release
   story. A reader comparing the two packages learns the pairing rule
   from the section, not from a rewritten history.
2. **The bundle is rebuilt where the dependencies are private.** The
   banner reads `package.json`'s version at build time, so the bump makes
   the committed-nothing `dist/` stale; `ensure_current` rebuilds it with
   `npm run build`, which reads `node_modules` and writes only `dist/`.
   `npm ci`, `npm install` and `scripts/check-dist` run only in the
   primary checkout after integration, never through this worktree's
   linked `node_modules` (`workflow/release-0.7.md`).
3. **`package-lock.json`'s own version follows `package.json`.** It still
   says 0.2.0 from before the 0.7.0 cut; `npm ci` accepts the mismatch,
   but the lock file's `version` fields are the package's and are moved
   with it so the two manifests agree.
4. **The test pins the literal.** `test_the_manual_states_the_release`
   pins `'0.7.1 — 27 September 2026'` and `'Machinome 0.7.1'`, as it
   pinned 0.7.0: the date is a fact the test guards, and the next release
   edits it with the record.

## Risks / Trade-offs

- [The upload slips past 27 September] → the date is in `CHANGELOG.md`,
  `docs/index.rst`, `workflow/release-0.7.md` and
  `tests/test_documentation.py`; the workspace checklist names them.
- [A widget test or the packaging test reads the version] → none does;
  the widget suite is run after the bump to prove it.
