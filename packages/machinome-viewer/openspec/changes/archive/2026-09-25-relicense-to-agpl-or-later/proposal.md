## Why

The pilot decided on 25 September 2026, before publishing 0.7.0, that the
viewer is licensed under the GNU Affero General Public License, version 3
or any later version, not version 3 only. Every SPDX header, both package
manifests, the bundle banner, the README, the manual, the changelog and the
release record say `AGPL-3.0-only`.

## What Changes

- Every SPDX header in the repository, `pyproject.toml`, the widget's
  `package.json` and lock file, the bundle banner `build.mjs` writes,
  `scripts/check-dist`'s banner assertion, the README, `context7.json`, the
  manual's index and sharing pages, the 0.7.0 changelog section, the 0.7
  release record and the OpenSpec context declare `AGPL-3.0-or-later`.
- `tests/test_documentation.py` pins it: the two manifests and the banner
  agree, every tracked file with an SPDX line grants or-later, and no
  reader-facing page says only.
- The `LICENSE` text is unchanged: it is the AGPL version 3 text as
  published; the "or later" grant is the SPDX expression the files carry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-distribution`: the distribution and the bundle banner declare
  `AGPL-3.0-or-later`.

## Impact

149 files' SPDX headers; `pyproject.toml`; `machinome_viewer/widget/package.json`,
`package-lock.json`, `build.mjs`; `scripts/check-dist`; `README.md`;
`CHANGELOG.md`; `context7.json`; `docs/index.rst`; `docs/sharing.rst`;
`workflow/release-0.7.md`; `openspec/config.yaml`;
`tests/test_documentation.py`. The pushed `v0.7.0` tag does not carry this
and is re-cut by the pilot; the framework's, the shop's and the site's
statements of the viewer's licence change in their own repositories.
