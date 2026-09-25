## Why

The pilot decided on 25 September 2026 that the viewer, `machinome-viewer`,
is licensed under the GNU Affero General Public License version 3 or any
later version (`AGPL-3.0-or-later`), not version 3 only, before publishing
0.7.0. The framework's manual states the viewer's licence on ten pages, in
the README, in a `pyproject.toml` comment, in the architecture page and in
the user-documentation spec, all as `AGPL-3.0-only`.

## What Changes

- Every statement of the viewer's licence in the manual, the README, the
  `pyproject.toml` comment and the architecture page says
  `AGPL-3.0-or-later`. The framework's own licence, Apache-2.0, and the
  release history are untouched.
- `tests/test_docs_structure.py` refuses `AGPL-3.0-only` on any manual page
  and in the README, so the stale grant cannot return.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: the viewer's provenance requirement names the
  viewer's licence as `AGPL-3.0-or-later`.

## Impact

`docs/why.rst`, `docs/start/install.rst`, `docs/concepts/publishing.rst`,
`docs/reference/manuals.rst`, `docs/project/status.rst`,
`docs/project/changelog.rst`, `docs/project/upgrading.rst`,
`docs/releases/release-0.7.rst`, `docs/architecture.md`, `README.rst`,
`pyproject.toml`, `tests/test_docs_structure.py`. The 0.7.0 tag is re-cut
by the pilot on the integrated head. `HISTORY.rst`'s account of the 0.6
release and the decision records keep the grant that held at the time.
