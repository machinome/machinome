## 1. Found the repository

- [x] 1.1 Split `solid_node/viewers` out of a scratch clone of solid-node with
      `git subtree split`, preserving 79 commits, and pull it into a new
      repository at the workspace root.
- [x] 1.2 Lay the files out as the `solid_node_viewer` package; drop the OpenSCAD
      viewer and the parity generator, which stay with the framework.
- [x] 1.3 Relicense every header and both package manifests to AGPL-3.0-only;
      rewrite the bundle banner to name licence, version, API version and source.

## 2. The process boundary

- [x] 2.1 `bundle.py`: standard-library-only lookup with `describe()` and
      `BundleMissing`; `pyproject.toml` registers it as the `solid_node.viewer`
      entry point and `solid-node-viewer` as a console script.
- [x] 2.2 `server.py`: `WebViewer(build_dir, dev, port, frontend)`; the errors
      file lives beside the document; an unbuilt app answers with its remedy.
- [x] 2.3 `capture.py`: `Capture(staging).render(output, imgsize, options)` adds
      the bundle and mount page to a staged document and photographs it;
      `mount_options()` carries time, view, up and fov.
- [x] 2.4 `cli.py`: `describe`, `serve --build-dir`, `capture STAGING -o PNG`
      with camera options.
- [x] 2.5 `packaging.py`: sdist builds both frontends; wheel builds what is
      missing.

## 3. Tests

- [x] 3.1 Commit `tests/fixtures/spinner`, a widget-less export of the framework's
      spinner project.
- [x] 3.2 Port the bundle, server, capture, widget end-to-end and packaging tests
      to the fixture and the new interfaces; add CLI and version-agreement tests.
- [x] 3.3 Green: 48 Python tests (headless Chromium and Playwright present), 180
      vitest cases, 12 app tests, `tsc --noEmit` clean.

## 4. Records

- [x] 4.1 `openspec init`; migrate `viewer-package` and
      `viewer-assembly-navigation` verbatim; write `development-server`,
      `snapshot-capture` and `viewer-distribution`.
- [x] 4.2 Relocate the viewer-owned ADRs from solid-node into `docs/adrs/`.
- [x] 4.3 README, CHANGELOG, CI workflow, `scripts/check-dist`.
