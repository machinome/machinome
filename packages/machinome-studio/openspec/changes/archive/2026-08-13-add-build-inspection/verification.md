# Verification

## Product evidence

- Package unit and session-route tests prove one canonical STL per distinct
  piece, explicit `README.md` quantities, fixed metadata and byte-identical
  repeat downloads, verified session scoping, and rejection of malformed,
  missing, non-STL, and escaping references.
- Browser acceptance proves the interactive fourth Build rail area, one
  representative WebGL mesh, fixed 250 × 210 × 220 mm volume, explicit
  repeated and single quantities, envelope and watertightness facts, retained
  selection and conversation draft, package download contents, and no
  horizontal overflow at 760 px.
- The initial-build-failure browser scenario remains green after scoping the
  Build failure notice to the visible Build area.

## Commands

- `python -m pytest -q tests/test_build_package.py tests/test_floor_api.py -k build_package`
  — 4 passed, 13 deselected, 5 subtests passed.
- `npm run test` in `floor/frontend/` — TypeScript project build passed.
- `npm run build` in `floor/frontend/` — production Vite bundle passed.
- `/home/asa/devel/solid-node-studio/.venv/bin/python -m pytest -q tests --ignore=tests/test_shop_lifecycle_e2e.py`
  — 236 passed, 1 skipped, 106 subtests passed.
- `/home/asa/devel/solid-node-studio/.venv/bin/python -m pytest -q tests/test_shop_lifecycle_e2e.py`
  — 12 passed, 5 subtests passed.
- `openspec validate --all --strict` — 26 items passed, 0 failed after baseline
  spec sync.
- `git diff --check` — passed.

The non-browser suite emits its existing closed-event-loop subprocess cleanup
warning after completion; it does not fail a test. The frontend install reports
four transitive audit findings (one low, two moderate, one high); this change
does not run an automatic dependency rewrite because that could alter unrelated
locked packages.
