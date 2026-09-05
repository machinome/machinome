## Why

The viewer lived inside the solid-node framework, under Apache-2.0, and the
framework's author held the viewer features worth protecting outside it for
that reason. Making the whole viewer AGPL while keeping the framework Apache
means the viewer must become a work of its own: a separately installed
package the framework reaches only through a process boundary, so that the
framework stays complete and useful on its own and no AGPL code is imported
into an Apache program.

## What Changes

- Found `solid-node-viewer` from the history of `solid_node/viewers` in
  solid-node, laid out as the `solid_node_viewer` package: the widget, the
  development app, the development server and the browser capture. The
  OpenSCAD viewer stays with the framework.
- Relicense every file to AGPL-3.0-only; the bundle banner names the licence,
  version, API version and source repository.
- Add the process boundary the framework uses: the `solid_node.viewer` entry
  point and the `solid-node-viewer describe|serve|capture` console script. The
  server takes its build directory as an argument; the capture takes a staged
  document and camera options as arguments. Neither imports `solid_node`.
- Move Playwright here as the `snapshot` extra.
- Commit an export fixture so the suite depends on nothing of the framework.
- Migrate the viewer-owned baseline specs (`viewer-package`,
  `viewer-assembly-navigation`) verbatim, rewrite `web-viewer` as
  `development-server` and `viewer-distribution` for the new boundary, and
  carve the capture half of `web-snapshot` out as `snapshot-capture`.

## Capabilities

### New Capabilities

- `viewer-distribution`: how the package is delivered and found — built
  frontends in every distribution, the licence banner, the entry point, the
  `describe` command, and the rule that everything else is a process.
- `development-server`: the server `solid develop` launches on a build
  directory; migrated from `web-viewer` with the launch contract added.
- `snapshot-capture`: the transparent photograph of a staged document;
  migrated from the capture half of `web-snapshot` with the staging contract
  added.
- `viewer-package`, `viewer-assembly-navigation`: migrated verbatim from
  solid-node's baseline. Their requirements were ratified there; this change
  records the move, not a behaviour change, so they carry no delta here.

## Impact

Everything in this repository. In solid-node, the paired change
`optional-viewer-package` removes the viewer, adds the `viewer` extra and
consumes the entry point and commands specified here.
