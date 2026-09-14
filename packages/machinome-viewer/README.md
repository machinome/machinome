# solid-node-viewer

The browser viewer for [solid-node](https://github.com/LibreSolid/solid-node)
models, packaged for pip.

solid-node describes a mechanical model as a versioned tree document —
`viewer.json` in a build, `manifest.json` in an export — beside the STL
files it names. This package is everything that turns such a document into
something a person can look at in a browser:

- **`solid-widget.js`**, the embeddable three.js widget: orbit controls,
  client-side `$t` animation — at real time, with a speed control and a
  machine-time readout, when the document declares how long a turn of the
  timeline is — one slider with a passive click-to-edit numeric readout per
  declared driver and one button per declared instruction, molejo flexible
  parts evaluated per frame, **the machine itself run in a Web Worker for
  a document that carries a compiled mechanical program**, **driven on
  screen by nudge, hold-to-jog and instruction controls over a transport
  of run, pause, step, speed, elapsed time and reset**, and the
  `SolidNodeWidget.mount()` API a host page drives it through;
- the **standalone export page** a `solid export` directory ships with;
- the **development server** that `solid develop` launches beside its
  builder to serve a published build to the development app, with the
  reload channel and the build-error surface;
- the **headless capture** behind `solid snapshot --renderer web`, which
  photographs a staged document through the widget with a transparent
  background.

## Installing

Makers do not install this package directly. It arrives as an extra of the
framework:

```
pip install "solid-node[viewer]"
```

With it installed, `solid develop` opens the web viewer by default and
`solid export` and the Sphinx directive ship the widget. Without it, the
framework still works in full with its OpenSCAD viewer; the commands that
need the browser viewer name this extra as the remedy.

The snapshot capture needs a browser as well:

```
pip install "solid-node-viewer[snapshot]"
playwright install chromium
```

## How solid-node reaches it

The framework never imports this package's code. It finds the installed
viewer through one Python entry point, `solid_node.viewer`, which returns
the bundle path, the export page, the declared viewer API version and the
document schema versions this build reads; and it
runs three commands of the `solid-node-viewer` console script (or, as the
framework does it, `python -m solid_node_viewer`) as separate processes:

| Command | Used by |
| --- | --- |
| `solid-node-viewer describe` | the same answer as the entry point, as JSON on standard output |
| `solid-node-viewer serve --build-dir DIR` | `solid develop`, which launches it beside the builder |
| `solid-node-viewer capture STAGING -o PNG` | `solid snapshot --renderer web`, on a staged document |

That process boundary is the licensing boundary. solid-node is Apache-2.0
and stays complete and useful on its own; this viewer is AGPL-3.0-only and
is an optional, separately installed addition to it. Nothing flows from here
back into the framework.

## Reading and moving the assembly

A mount handle's `assembly()` reads the published tree as `AssemblyNode`s,
addressed by root-relative paths of sibling names; `setRoot(path | null)`
focuses a subtree (`null` restores the document root) and
`setVisible(path, visible)` hides or shows one. `navigation()` reads what
is currently focused and hidden — `{ root, hidden }`, a serializable
snapshot the handle does not later modify — and `onAssemblyChange(listener)`
subscribes to every accepted operation that moves that state or
republishes the tree, whatever caused it: a host call, the widget's own
breadcrumb, or a targeted update. It returns a function that cancels the
subscription, and the listener receives the fresh `assembly` and
`navigation` together, so it never has to call back into the handle to
redraw. A listener **observes**: nothing stops it calling `setRoot` or
`setVisible` back into the viewer, but doing so from inside the listener
can loop forever, and a navigator built on this bundle does not.

## Driving a running machine

A document that carries a compiled mechanical program is not posed, it is
**run**, and it gets its own chrome rather than a widened version of the
posed one. Per declared input of the focused layer the widget shows a
follow-only readout of the input's committed position in design units, a
nudge pair asking for a relative movement over a duration, and a
hold-to-jog pair asking for a rate until the interaction ends — on
release, on lost pointer capture, on lost window focus, or when the page
stops being displayed. Per declared instruction it shows one button,
which submits that named instruction whichever form it is declared in.
Every request reports at the control that made it: completed, blocked
with the travel the machine actually admitted, refused with the run's own
reason, or cancelled. Along the bottom runs the transport: run, pause,
step one step of the run, the speed to watch at, the elapsed simulation
time, and reset.

What a running document has **no** control for is a position. A slider
writes a position into a coordinate, and under a run a coordinate is the
output of an integration that carries history — ten `Add one` on a slider
would leave the drum where one did. So there is no slider, and no
timeline: seeking belongs to recorded history. A document of versions 1
to 4 keeps every pixel of the chrome it has always had.

The nudge amount, its duration and the jog rate are editable in the panel
and settable at mount:

```js
SolidNodeWidget.mount('#host', 'viewer.json', {
  run: { nudge: { amount: 1, seconds: 0.2 }, jog: { rate: 1 } },
});
```

They configure the **request** those controls will make; typing in one
moves nothing. `driverControls: 'none'` suppresses this chrome exactly as
it suppresses the posed one, and leaves the whole `handle.run()` API
untouched for a host building its own panel.

## Versions

The package version and the **viewer API version** are different numbers.
The API version is the integer a host checks before mounting — the widget
declares it once in `package.json` as `solidNodeViewerApi`, and every mount
handle and the `SolidNodeWidget` global report it. It rises when the mount
interface changes incompatibly or gains a capability a host may require.
The document schema versions the widget reads are a third number, owned by
the producer; the widget declares the list it reads once in the same
`package.json` as `solidNodeDocumentVersions`, and `describe` reports it as
`documentVersions` beside the API version, so a producer can ask what this
build reads rather than infer it.

| solid-node-viewer | viewer API | reads document versions |
| --- | --- | --- |
| 0.1.0 | 7 | 1, 2, 3, 4 |
| 0.2.0 | 9 | 1, 2, 3, 4, 5 |

## Working on the viewer

```
git clone https://github.com/LibreSolid/solid-node-viewer
cd solid-node-viewer
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/playwright install chromium
(cd solid_node_viewer/widget && npm ci && npm run build)
(cd solid_node_viewer/app && npm ci && npm run build)
.venv/bin/python -m pytest
(cd solid_node_viewer/widget && npm run typecheck && npm test)
```

The Python suite skips what its environment cannot run — a headless
Chromium, Playwright, Pillow — and says so per test. The widget suite runs
a producer-generated parity fixture against the shipped expression
evaluator; that fixture is regenerated by the framework's own tool and
copied here, because the numbers in it are the framework's, not ours.

The development app is a Create React App shell. To work on it with hot
reloading, run `solid-node-viewer serve --build-dir <project>/_build
--start-frontend`, which starts the npm dev server and proxies the page
to it.

`scripts/check-dist` builds the source distribution and the wheel, installs
the wheel into a throwaway environment outside the repository and runs the
`describe` command there. It uploads nothing; publishing is a separate,
explicit decision.

## Status and process

Version 0.1.0 is the viewer exactly as it shipped inside solid-node 0.6.0,
relicensed and repackaged; see `CHANGELOG.md`. Behavioural specs live under
`openspec/specs/`, changes go through `openspec/changes/`, and the decisions
that shaped the viewer — most of them made while it still lived in the
framework — are in `docs/adrs/`.

## Licence

AGPL-3.0-only. See `LICENSE`. The bundle's banner retains the notices of
the libraries it bundles: three.js and jokenizer (MIT) and molejo
(Apache-2.0).
