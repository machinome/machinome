## MODIFIED Requirements

### Requirement: The workspace, the bundles, the lint and the manual have a target each

`make sync` SHALL install the uv workspace (`uv sync --python 3.12`), the npm
workspace from its lock (`npm ci`) and the Chromium the installed Playwright
uses, refusing with one line when `uv` or `npm` is not on the PATH.
`make widget` SHALL install the npm workspace from its lock and build every
member's bundle. `make lint` SHALL run black's check and flake8 with a line
length of 89 over the framework's sources and tests and every other package's
`machinome/` from the framework's directory, both always, and fail when
either does. `make docs` SHALL build the browser viewer's bundle, then build
the manual with warnings as errors from an environment of its own at the
root's `.docs-venv/`, made when absent, into which it installs
`packages/machinome/docs/requirements.txt` alone, reading every page, into
`packages/machinome/docs/_build/html`; the manual takes the repository's
viewer, which the framework finds through its seam.

#### Scenario: The manual is built as Read the Docs builds it

- **WHEN** `make docs` runs on a clone after `make sync`
- **THEN** the viewer's bundle is built, the environment the manual builds in
  holds what `packages/machinome/docs/requirements.txt` names and nothing of
  the workspace, the build fails on any warning, and the pages are written to
  `packages/machinome/docs/_build/html`

#### Scenario: The lint reports both tools

- **WHEN** black would reformat a file and flake8 reports a line
- **THEN** `make lint` prints both reports and fails
