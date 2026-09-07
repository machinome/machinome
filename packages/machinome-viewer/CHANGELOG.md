# Changelog

All notable changes to solid-node-viewer. The Python package and the widget
it carries release together and share one version.

## 0.1.0 — unreleased

The viewer leaves the solid-node framework and becomes this package.

- **A document that repeats itself now animates.** A producer that builds
  an expression by string concatenation — solid2's `OpenSCADConstant` —
  pastes a reused value's full text again on every reuse, and a machine
  whose motion nests those reuses can publish an expression corpus far
  larger than its geometry: 3DPrintedClocks' `wall_clock_53_grasshopper`
  carries 31.6 MB of expressions, 4.28 million parsed nodes, over just
  293 *distinct* subexpressions. The widget no longer walks a parse tree
  on every frame; it interns each parsed expression once into a shared,
  hash-consed table — a repeated subexpression, however many operations
  or however many times one expression repeats it, is resolved once per
  animation frame — and drops the parse tree the moment it is interned.
  Measured on that document: 6,247,876 parsed-node visits per animated
  frame fall to 255 node resolutions; sixty animated frames fall from
  roughly 30 seconds to 29 milliseconds; the parse trees this viewer
  used to retain for the life of the page, 723 MB, fall to a table of a
  few hundred interned nodes. Loading grows by about 16% (an
  interning walk on top of parsing, ~8.9 s against ~7.65 s for this
  document) in exchange for that per-frame win. The numbers themselves
  do not move: every evaluator, tree, flexible-part and cross-runtime
  parity test in the suite passes unedited against the shipped module,
  and OpenSCAD semantics — degree trig, `^` as exponentiation with the
  unary-minus rule, `mod`, `ln`, `log(base, value)` — carry onto the
  shared table unchanged. An expression form the shared evaluation
  cannot support — an inline function, which nothing the producer emits
  carries — is refused when the document is loaded rather than met
  inside a frame. The viewer API stays at 6: nothing on the mount
  options or the handle changes, and the resolution/table-size counts
  this change adds are a widget-source export for its own tests, not a
  capability a host can require. (OpenSpec change
  `share-expression-subtrees`; ADR-043.)

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
