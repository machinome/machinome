# User manual review — 2026-09-20

Status: pilot approved the site and directed sync/archive on 2026-09-20.
Specifications are synchronized and the change is archived at
`openspec/changes/archive/2026-09-20-user-documentation/`.
Integration, push and publication remain separate actions.

## Identity

- Mechanics repository: `machinome-mechanics`, branch `user-documentation`.
- Base/main: `7b8d5bba4b47df88d1e5c459ef4badc9f7593d19`.
- Pre-ratified planning commit: `d703c6e`.
- Worktree: `/home/asa/devel/machinome-studio/WTs/mechanics-user-docs`.
- Companion framework change: `mechanics-documentation-links`, planning commit
  `1fd0e22`, based on `4d747191f8a94cb72fa3a4bef23a9742b91f0acf`.

The completed-change commit contains the approved implementation and archive.
The primary checkouts remain unchanged. There is no runtime formula change.

## Evidence

Linux / Python 3.12.3; Sphinx 9.1.0; sphinx_rtd_theme 3.1.0.

- Red: the original Sphinx build failed for missing `docs/conf.py`; the new
  reference coverage test failed with zero entries for twelve public exports.
- Strict mechanics HTML build: all ten pages, zero warnings, with `-n -W`.
- Repeated the HTML build in `/tmp/mechanics-docs-env-q3FwP2`, a fresh venv
  containing only `docs/requirements.txt` dependencies. Confirmed no installed
  `machinome` or `machinome_mechanics` runtime using isolated Python. No CAD
  tools, remote framework install or mocks are needed to render the manual.
- Sphinx doctest build against the actual workspace framework: **79 checks,
  zero failures**. The downloadable model files and project manifest are the
  actual files used by the examples. Initial tests exposed the need for those
  source files and manifest; the user guide now supplies them explicitly.
- Package suite: **31 passed, 24 subtests passed**, including public signature
  coverage, numeric/symbolic parity and motion/declarative integration.
- `python scripts/check-dist`: wheel and sdist built, strict metadata checks
  passed, each installed outside the checkout and passed numeric/symbolic
  smoke checks. The source manifest includes all manual sources, example
  files, assets, `.readthedocs.yaml` and moved workflow records, and excludes
  `docs/_build`.
- The three old `docs/*.md` files are byte-identical after moving to `workflow/`.
- Browser: all ten pages at **1440×1000 and 390×844**, with no page overflow or
  broken images. Corrected the RTD theme's narrow-screen parameter-list grid.
  Mobile navigation, browser-side search and **78 internal page/fragment
  targets** pass, with no browser errors. Inspected landing and reference
  screenshots, including the coordinate diagrams.
- The framework manual builds all thirty pages with `-W`, zero warnings.
  Its four new mechanics URL targets resolve to pages in the local companion
  build. See that change's validation record for the example-export provenance.
- Both OpenSpec changes pass strict validation; `git diff --check` passes.

Reproduction commands are in [documentation maintenance](documentation.md).
The local browser check and screenshots are ignored artifacts under
`_build/review_site.py` and `_build/review/` in this worktree.

## Preview and completion

- Mechanics: <http://localhost:8020/> (loopback preview, PID 2228510 at handoff).
- Framework: <http://localhost:8021/api-reference.html#mechanics-helpers>
  (loopback preview, PID 2228603 at handoff).

The preview processes serve the built directories in their respective worktrees.
The intended public RTD address is configured; no hosted build or RTD account
connection has been exercised. See `documentation.md` for the one-time setup.

Following pilot approval, each repository's own change was synchronized and
archived. The mechanics baseline provenance path now points to
`workflow/extraction.md`. Historical archived paths remain historical.
Framework architecture is unchanged and needs no new ADR.
