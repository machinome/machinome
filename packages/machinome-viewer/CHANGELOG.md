# Changelog

All notable changes to solid-node-viewer. The Python package and the widget
it carries release together and share one version.

## 0.1.0 — unreleased

The viewer leaves the solid-node framework and becomes this package.

- **Real-time playback.** A document whose `animation` object carries
  `loop` — the seconds of machine time one turn of `$t` covers, which
  solid-node publishes when a root declares `time = Time(loop=...)` —
  plays that loop at real time by default: one turn takes `loop / speed`
  wall-clock seconds, with `speed` defaulting to 1. The animation bar
  gains a speed control over a fixed ladder (×0.1 to ×3600) and a readout
  of the machine time at the slider position (`h:mm:ss` for long loops,
  seconds for short ones). The host sets the initial speed through the
  `speed` mount option and reads or changes it through `speed()` and
  `setSpeed()` on the handle. A document without `loop` plays `frames /
  fps` exactly as before, with the bar it always had. The viewer API rises
  to 6, because a host may now require the speed capability. (OpenSpec
  change `real-time-playback`, paired with solid-node's
  `declared-time-base`.)

- **A large model is photographed at last.** `solid-node-viewer capture`
  clips a page screenshot to the canvas instead of photographing the canvas
  element. Playwright caps an element screenshot's wait for a stable box at
  thirty seconds however long a timeout it is given, so a model that takes
  longer than that to settle — a vendor assembly of dozens of pieces on
  software rendering — never produced a picture at all. The clipped page
  screenshot honours its own, generous timeout.

- **Extracted.** The widget, the development app, the development server
  and the headless capture that shipped inside solid-node up to 0.6.0 move
  here with their history. Nothing a browser sees has changed: the bundle
  is still `solid-widget.js`, it still auto-mounts `data-solid-widget`
  containers, still exposes `SolidNodeWidget.mount()`, and still reads
  document versions 1, 2 and 3 (viewer API 5 at extraction; see
  real-time playback above for 6).
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
