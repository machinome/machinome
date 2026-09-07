# Changelog

All notable changes to solid-node-viewer. The Python package and the widget
it carries release together and share one version.

## 0.1.0 — unreleased

The viewer leaves the solid-node framework and becomes this package.

- **A machine whose document shrank by 981× still opens, poses and
  plays.** `share-expression-subtrees` resolved a repeated subexpression
  once per frame, wherever it occurred — but the redundancy was still in
  the *document*: 3DPrintedClocks' grasshopper escapement published 116
  operation expressions built from 30 distinct strings, about seven
  million written subexpressions over 263 distinct ones, 31.6 MB in all.
  The producer now writes each subexpression that repeats exactly once,
  as a named entry in an ordered `bindings` table, and references it by
  bare name everywhere it occurred — the same grasshopper document falls
  from 31,638,555 bytes to 32,227, and this viewer now reads it
  (document version 4). A binding name resolves wherever it is used —
  an operation's expression, a flexible leaf's `params`, or another
  binding — to that entry's value under the same `$t` and driver values,
  and resolves as a binding *before* it is ever judged a driver id: a
  document may name every one of its bindings with an empty `drivers`
  table, and it still loads. Dependence flows *through* a binding
  transitively: an operation whose whole expression is a binding name
  resolving through the table to `$t` is time-dependent exactly as if
  it had been written out in full, gets re-evaluated on time change, and
  makes its document animated — the grasshopper document's own shape,
  where not one of its 116 expressions contains `$t` as text, yet 22 of
  them move the clock. A binding a driver reaches is re-evaluated when
  that driver moves and not otherwise, through as many entries as the
  chain runs, and a republish that changes only what a binding reads —
  an operation whose text stays exactly `_b3` while `_b3`'s own
  expression changes from `$t` to a driver, or back — is followed: the
  document's timeline appears or disappears with it. A table this viewer
  cannot resolve is refused when the document is loaded, naming the
  entry: a malformed array or entry, a duplicate name, an entry naming
  itself or a later entry, a name colliding with a declared driver id,
  or a name reached from anywhere in the document that is neither `$t`,
  nor an entry, nor a declared driver id. No number moves: reading a
  document's expressions through its table resolves to exactly what the
  same expressions resolve to with every reference written out, proven
  bit-identical (`Object.is`) against the flat 31.6 MB document at three
  points in its cycle — the two are the same arithmetic, differently
  written. The committed cross-runtime parity fixture is replaced by the
  framework's regenerated one (451 cases, the 421 already pinned
  unmoved, plus 30 new naming its own 4-entry table), so the corpus now
  pins the table's semantics and not only the evaluator's. The viewer
  API rises to 7: reading a version-4 document is a capability a host
  may require, and there is no other number a host can check before
  mounting one. (OpenSpec change `read-expression-bindings`; ADR-044,
  extending `share-expression-subtrees`'s ADR-043; consumes solid-node's
  `expression-bindings`, ADR-080.)

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
