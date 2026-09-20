# Building and publishing the user manual

The user site is `docs/`, using Sphinx and `sphinx-rtd-theme` like the framework
and mechanics manuals. Workflow records belong here, not in the user navigation.

## Local build

From the repository root, with Python 3.12+ and Node.js 22+:

```sh
python -m venv .venv-docs
.venv-docs/bin/python -m pip install -r docs/requirements.txt
npm ci --prefix machinome_viewer/widget --no-audit --no-fund
npm run build --prefix machinome_viewer/widget
.venv-docs/bin/python -m sphinx -n -W --keep-going -b html docs docs/_build/html
python -m http.server 8022 --bind 127.0.0.1 --directory docs/_build/html
```

Open <http://localhost:8022/>. The HTML build imports neither the viewer runtime
nor the framework. Only pinned documentation dependencies are installed into
Python; npm uses the viewer's existing lockfile. Node builds the actual bundled
viewer for the interactive example. It is not a reader-side prerequisite.

Sphinx refuses a missing/stale bundle instead of silently producing a broken
example. It copies the spinner fixture and example source into the built site;
the published page needs no CAD service and makes no external asset requests.
Rebuild the bundle after editing widget source, including its coverage test.

Check reference coverage with `npm test --prefix machinome_viewer/widget` and
repository/build configuration with `python -m pytest tests/test_documentation.py`.
Browser review evidence belongs in `documentation-review.md`.

After building HTML, run `python scripts/check-docs-browser.py` in an environment
with Playwright and Chromium. It checks all local links, desktop/mobile layout,
search, the live spinner and the exact running/clocked reference snippets, and
writes screenshots/report to `_build/docs-review/`.

## Read the Docs

The intended project slug is `machinome-viewer`, serving
<https://machinome-viewer.readthedocs.io/>. Import
`https://github.com/machinome/machinome-viewer` into Read the Docs once, enable the
desired branch/version and repository webhook, and use `.readthedocs.yaml`.
The configuration pins Python 3.12 and Node 22, installs documentation-only
Python requirements, builds the bundle before Sphinx, and fails on warnings.
These use the supported [v2 configuration and build hooks](https://docs.readthedocs.com/platform/stable/config-file/v2.html).

A Git push can trigger subsequent builds only after that account/project setup.
This change creates no hosted project, pushes nothing, and cannot verify an
unconfigured hosting account. If the slug changes, update package URLs and
cross-manual links; `READTHEDOCS_CANONICAL_URL` supplies the canonical build URL.
Keep the current unreleased notice until publication is actually confirmed.
