# Validation and pilot review

Status: pilot approved on 2026-09-20; specifications synchronized and archived
at `openspec/changes/archive/2026-09-20-viewer-documentation-links/`.
Original base/main: `4d747191f8a94cb72fa3a4bef23a9742b91f0acf`.
Original planning commit: `089d488`; rebased planning commit: `650df43`.
Approved integration base: `832d84c47386b9e169a96ae1d138c285fb874e6d`
(the completed mechanics-link cycle).
Worktree: `machinome/WTs/viewer-documentation-links`.
Integration target: framework `main`, explicitly authorized on 2026-09-20.

Four focused link tests failed red against the unchanged manual, then passed
after the navigation, viewer operating and embedding/reference links were added.
Strict Sphinx (`-E -W --keep-going -b html`) passed all 30 pages. The first
attempt reported three missing generated example exports, as expected in a
fresh worktree. Existing exports from the workspace's `docs-0-7` worktree were
then linked read-only under ignored example directories; the clean rebuild
passed. This validates documentation, not a fresh CAD build of those examples.

Browser checks verified four distinct framework-to-viewer targets and five
reverse targets against the local HTML sites, with no page errors. Screenshots
of the changed framework pages are under `_build/`. The companion viewer's
manual has separate desktop/mobile, interactive and reference-example evidence
in its `workflow/documentation-review.md`.

Existing framework embedding coverage remains, with `setView` mentioned and the
clocked behavior clarified: direct moves land immediately, instruction triggers
commit immediately and draw over the declared duration. No runtime, dependency
or architectural decision changed; no ADR is needed.

Preview: <http://localhost:8023/viewer.html> and
<http://localhost:8023/embedding.html>. New viewer manual:
<http://localhost:8022/>. Hosted RTD deployment is not claimed.

The viewer-manual requirement is synchronized into the existing documentation
baseline without changing earlier requirements. Focused checks (4 passed) and
the strict HTML build (30 pages, no warnings) passed again before completion.
That final framework build used the workspace environment with
`PYTHONPATH="$PWD"`; an initial attempt with the viewer's documentation-only
environment failed because the framework's existing autodoc imports require
OCP. The viewer manual itself remains independent of those runtime packages.

The pilot explicitly authorized rebasing this two-commit cycle onto the archived
mechanics-link cycle (`832d84c`) and then fast-forwarding framework `main`,
preserving both sets of documentation additions. The original cycle base above
records its opening state. No push or publication is authorized.

## Combined integration validation

The authorized rebase preserved both two-commit cycles. The single content
conflict was both cycles appending their independent requirement to the same
baseline; both blocks are retained verbatim. Both manual navigation links and
all mechanics guide/API/migration links remain present.

- `pytest tests/test_viewer_documentation_links.py
  tests/test_mechanics_boundary.py tests/test_docs_exports.py -q` with the
  workspace environment and worktree `PYTHONPATH`: **17 passed, 40 subtests
  passed**. An initial command named a nonexistent mechanics-link test module;
  that command collected nothing and is not counted as validation.
- Strict framework Sphinx rebuild: **30 pages, zero warnings**.
- Browser cross-links: **4 framework-to-viewer and 5 viewer-to-framework
  destinations passed**, with no page errors. All four mechanics destinations
  remain reachable in the local mechanics manual.
- Supported strict baseline validation passed. Diff comparison against the
  mechanics cycle confirms its requirements remain intact, and the viewer
  cycle remains exactly two commits ahead of the approved integration base.
- Companion mechanics main `ae7901e`: **31 tests, 24 subtests passed** and a
  strict ten-page HTML build passed after integration. Its two pre-existing
  untracked screenshots are untouched (SHA-256 verified).
- Companion viewer main `c6df93d`: its six documentation checks passed again
  after integration. The fourteen-page desktop/mobile browser review, 201 local
  links and live/reference examples passed immediately before the commit.
- Shop pointer correction `0705d5e` is integrated into shop main.

The completed framework commit contains this evidence and is intended for
fast-forward integration after the mechanics-link commit. Previews/worktrees
are retained; no branch is deleted and no remote is changed.
