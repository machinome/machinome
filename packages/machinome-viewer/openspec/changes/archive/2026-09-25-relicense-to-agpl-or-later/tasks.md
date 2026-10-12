## 1. Prove the failure

- [x] 1.1 `tests/test_documentation.py`: the manifests, the banner template,
      every tracked SPDX header and the reader-facing pages grant
      `AGPL-3.0-or-later`; run it red.

## 2. Relicense

- [x] 2.1 Replace `AGPL-3.0-only` with `AGPL-3.0-or-later` in every SPDX
      header, `pyproject.toml`, `package.json`, `package-lock.json`,
      `build.mjs`, `scripts/check-dist`, `README.md`, `context7.json`,
      `docs/index.rst`, `docs/sharing.rst`, the 0.7.0 changelog section,
      `workflow/release-0.7.md` and `openspec/config.yaml`.
- [x] 2.2 Build the bundle from the changed sources and read its banner.

## 3. Record

- [x] 3.1 Tests green; validate, sync the delta, archive, commit.
