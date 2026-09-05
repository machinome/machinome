# Changelog

All notable changes to solid-node-viewer. The Python package and the widget
it carries release together and share one version.

## 0.1.0 — unreleased

The viewer leaves the solid-node framework and becomes this package.

- **Extracted.** The widget, the development app, the development server
  and the headless capture that shipped inside solid-node up to 0.6.0 move
  here with their history. Nothing a browser sees has changed: the bundle
  is still `solid-widget.js`, it still auto-mounts `data-solid-widget`
  containers, still exposes `SolidNodeWidget.mount()`, and still declares
  viewer API 5 reading document versions 1, 2 and 3.
- **Relicensed** under AGPL-3.0-only. The framework stays Apache-2.0 and
  installs this package as its optional `viewer` extra.
- **A process boundary** toward the framework. solid-node locates the
  installed viewer through the `solid_node.viewer` entry point and runs
  the new `solid-node-viewer` console script for everything else:
  `describe` prints the bundle path and API version, `serve --build-dir`
  is the development server `solid develop` launches, and `capture` is
  the headless photograph `solid snapshot --renderer web` requests on a
  staged document. Neither package imports the other.
- **Playwright** moved with the capture: it is the `snapshot` extra of
  this package now, where solid-node's `web-snapshot` extra points.
- **Test fixtures are committed exports** rather than models built at test
  time, so the suite depends on nothing of the framework.
