# Evidence

## Red

`tests/test_licence.py`, written first and run against 2d209e4:

    314 failed, 3 passed, 1 skipped, 101 subtests passed

Every SPDX header, both manifests, the banner template and the reader-facing
pages said `AGPL-3.0-only`.

## The change

159 tracked files outside `workflow/archive/`, `workflow/adrs/` and
`openspec/changes/` carried the string and now carry `AGPL-3.0-or-later`:
the SPDX headers, `pyproject.toml`, `package.json`, `package-lock.json`,
`build.mjs`, `scripts/check-dist`, `README.md`, `CHANGELOG.md`,
`context7.json`, `docs/index.rst`, `docs/sharing.rst`,
`openspec/config.yaml` and the release record.

## The bundle

Built from the changed sources (`npm run build`, esbuild, 886.6 kB); its
first lines:

    machinome-viewer 0.7.0 - viewer API 27
    Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
    SPDX-License-Identifier: AGPL-3.0-or-later
    Source: https://github.com/machinome/machinome-viewer

## Green

    tests/test_licence.py tests/test_documentation.py tests/test_bundle.py
    tests/test_cli.py: 40 passed, 1 skipped, 412 subtests passed

The manual builds with warnings as errors after the change.
