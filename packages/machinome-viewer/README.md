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
  of run, pause, step, speed, elapsed time and reset**, **the machine's
  own parts made touchable wherever the document declares controls on
  them — a press submits the instruction a part declares and a drag
  turns it by whole quanta**, and the
  `SolidNodeWidget.mount()` API a host page drives it through;
- the **standalone export page** a `solid export` directory ships with,
  and the **inspector layout** (`SolidNodeWidget.mountInspector`) it can
  select — the viewer beside a collapsible assembly sidebar, composed
  from the widget's own navigator, in one host element;
- the **development server** that `solid develop` launches beside its
  builder, serving a static **development page** this package carries —
  the inspector mounted on the published build, with the reload channel
  and the build-error surface;
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

### The bundle's own navigator

`SolidNodeWidget.mountNavigator(target, viewer, options?)` mounts a
React-free, plain-DOM tree over that same channel — into the sidebar
the inspector layout below composes, a studio panel, or a maker's own
page:

```js
const viewer = await SolidNodeWidget.mount('#host', 'viewer.json', {});
const navigator = SolidNodeWidget.mountNavigator('#navigator', viewer, {
  label: 'Assembly',
  fullAssembly: true,
  className: 'my-panel',
  styles: 'inject',
});
// later
navigator.dispose();
```

It draws the whole published assembly before the call returns — no
notification is needed for the first tree — and redraws itself from
every `onAssemblyChange` payload: a host call, the widget's own
breadcrumb, or a targeted update. It holds no copy of the focused root or
the hidden paths, only its own expansion and keyboard position, so two
navigators mounted on one handle never disagree about what the viewer is
showing. `target` is an element or a selector; a selector matching
nothing is refused, naming it. `options`:

| option | default | what it does |
| --- | --- | --- |
| `label` | `'Assembly'` | the tree's accessible name |
| `fullAssembly` | `true` | show the "show full assembly" affordance while a subtree is focused |
| `className` | — | an extra class on the navigator's root element, for a host's own scoping |
| `styles` | `'inject'` | `'none'` skips the injected stylesheet, for a host serving the class contract below from its own CSS (a page whose Content-Security-Policy forbids inline `<style>`) |

**Keyboard contract**, while focus is on a row: `Up`/`Down` move between
the presented rows; `Right` expands a collapsed parent, or moves into its
first child when it is already expanded; `Left` collapses an expanded
parent, or moves to the parent row otherwise; `Enter` focuses the row's
node in the viewer; `Space` toggles the row's own visibility. The tree is
one stop in the page's tab order; a row's own controls are reachable by
pointer without a separate tab stop.

**The class contract.** Every element the navigator builds carries a
stable class under this prefix — a host may select on it, and the bundle
publishes no other file for it:

| class | element |
| --- | --- |
| `solid-nav` | the navigator root |
| `solid-nav-toolbar` | the row above the tree |
| `solid-nav-full` | the "show full assembly" button |
| `solid-nav-tree` | the `role="tree"` container |
| `solid-nav-row` | a `role="treeitem"`; modifiers `--root`, `--hidden`, `--obscured`, `--leaf` |
| `solid-nav-twisty` | the expand/collapse button |
| `solid-nav-spacer` | the twisty's width on a leaf |
| `solid-nav-visibility` | the visibility checkbox |
| `solid-nav-name` | the node's label |
| `solid-nav-badge` | the `root` marker on the focused row |
| `solid-nav-focus` | the per-row focus button |

**Theming.** The default presentation is neutral — legible on a light or
a dark page — and entirely driven by CSS custom properties declared on
`.solid-nav`, which a host overrides from its own stylesheet, on an
ancestor, or on `:root`, without reaching into the navigator's elements:

| property | default | what it sets |
| --- | --- | --- |
| `--solid-nav-font` | `12px ui-monospace, SFMono-Regular, Menlo, monospace` | row type |
| `--solid-nav-indent` | `15px` | indent per level |
| `--solid-nav-row-padding` | `4px 5px` | row padding |
| `--solid-nav-row-radius` | `5px` | row corner |
| `--solid-nav-row-min-height` | `28px` | row height |
| `--solid-nav-gap` | `6px` | gap between a row's parts |
| `--solid-nav-chip-size` | `12px` | the visibility chip |
| `--solid-nav-fg` | `inherit` | row text |
| `--solid-nav-fg-strong` | `inherit` | hovered / focused-root text |
| `--solid-nav-muted` | `rgba(128,128,128,0.95)` | buttons, badges |
| `--solid-nav-bg` | `transparent` | the navigator's ground |
| `--solid-nav-row-hover-bg` | `rgba(128,128,128,0.18)` | hover |
| `--solid-nav-root-bg` | `rgba(128,128,128,0.22)` | the focused-root row |
| `--solid-nav-root-mark` | `currentColor` | its inset rule |
| `--solid-nav-chip-neutral` | `#9aa0a8` | a colourless visible node |
| `--solid-nav-chip-border` | `rgba(128,128,128,0.8)` | a hidden node's outline |
| `--solid-nav-obscured-opacity` | `0.45` | an obscured node's chip |
| `--solid-nav-focus-ring` | `currentColor` | `:focus-visible` outline |

### The inspector layout

`SolidNodeWidget.mountInspector(target, sourceUrl, options?)` composes,
inside one host element, a collapsible assembly sidebar holding the
bundle's own navigator and the viewer with its own on-screen chrome —
the layout `mountNavigator` above says nothing ships with:

```js
const inspector = await SolidNodeWidget.mountInspector('#host', 'viewer.json', {
  sidebar: 'collapsed',
  navigator: { label: 'Assembly', fullAssembly: true },
  styles: 'inject',
});
inspector.viewer;      // the whole ViewerHandle, exposed rather than wrapped
inspector.navigator;   // the whole NavigatorHandle
inspector.sidebarOpen();
inspector.setSidebar(true);
// later
inspector.dispose();   // disposes the navigator, then the viewer, then empties the target
```

It takes everything `mount` takes, plus:

| option | default | what it does |
| --- | --- | --- |
| `sidebar` | `'collapsed'` | the sidebar's initial state |
| `navigator` | — | the navigator's own options (`label`, `fullAssembly`, `className`, `styles`), passed through untouched; `navigator.styles` defaults to the layout's own `styles` |
| `styles` | `'inject'` | `'none'` skips the layout's injected stylesheet (and defaults the navigator's to `'none'` too) |

The viewer is given a pane of its own inside the target, never the
target itself, so the viewer's own teardown (`replaceChildren()` on its
container) cannot remove the sidebar. Collapsing removes the sidebar
from layout and from assistive technology — it is never an overlay — and
the viewer's pane grows into the space; that resize is entirely the
viewer's own `ResizeObserver`, already installed by `mount()`, so the
layout adds no resize code of its own. A rejected mount (an unreadable
document, an unevaluable technology, an undeclared driver id) leaves the
target empty and rethrows the viewer's own error unchanged — no sidebar
is left around a viewer that never existed. The sidebar remembers
nothing: no `localStorage`, no cookie, no URL rewriting, so a page
reloaded shows exactly the state its own options declare.

**The class contract**, under its own prefix, distinct from the
navigator's:

| class | element |
| --- | --- |
| `solid-inspector` | the layout root, the target's only child |
| `solid-inspector-rail` | always present, in both states; holds the toggle |
| `solid-inspector-toggle` | the disclosure button; `aria-expanded`, `aria-controls` naming the sidebar |
| `solid-inspector-sidebar` | the navigator's host; `hidden` while collapsed |
| `solid-inspector-viewer` | `mount()`'s own container |

**Theming**, CSS custom properties on `.solid-inspector`:

| property | default | what it sets |
| --- | --- | --- |
| `--solid-inspector-sidebar-width` | `260px` | the sidebar's width |
| `--solid-inspector-rail-width` | `32px` | the rail's width |
| `--solid-inspector-bg` | `transparent` | the layout's ground |
| `--solid-inspector-fg` | `inherit` | text |
| `--solid-inspector-border` | `rgba(128,128,128,0.35)` | the rail/sidebar divider |
| `--solid-inspector-toggle-bg` | `rgba(128,128,128,0.12)` | the toggle |
| `--solid-inspector-toggle-hover-bg` | `rgba(128,128,128,0.24)` | the toggle, hovered |
| `--solid-inspector-focus-ring` | `currentColor` | `:focus-visible` outline |

### The standalone page's layout selection

`widget/index.html`'s published container attribute,
`data-solid-widget`, gains a sibling that chooses between the plain
viewer and the inspector — on the same container, and as a query-string
twin that overrides it:

| source | value | effect |
| --- | --- | --- |
| no attribute, no query | — | `mount()` — unchanged from every page written before this capability existed |
| `data-solid-layout="inspector"` | | `mountInspector()` |
| `?layout=inspector` / `?layout=viewer` | | overrides the attribute |
| `data-solid-sidebar="open"` \| `"collapsed"` | | the inspector's initial sidebar |
| `?sidebar=open` \| `?sidebar=collapsed` | | overrides the attribute |

An unrecognised layout value is written into the element by name
(`solid-widget: unknown layout "<value>"`), never silently ignored. The
page this package ships selects the inspector, collapsed.

No layout ships for a mount whose host wants neither: `mount()` and
`mountNavigator()` still compose nothing for you, and the studio keeps
its own layout on this same bundle.

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

## Touching the machine

A running document may also declare **controls on its parts**: a
`controls` table beside `instructions`, published by the framework from
the model's own `Button(part, instruction)` and `Turn(part, input)`
declarations, carrying for each the part and the joint as node-name
paths, the instruction it submits or the input it moves with the ratio
the framework measured, the coordinate that joint poses, and that
joint's axis and origin in its own frame. The viewer cannot infer any of
it — one coordinate is often reached by two inputs, and plenty of posed
parts are parts nobody may turn — so the binding is a declaration, and
this is the viewer reading it.

A part the table names becomes touchable. On hover it takes a pointer
cursor, a light highlight and the display names of every control naming
it; every other part orbits the camera exactly as before. A part the
assembly navigation has hidden or focused out is not touchable, and a
part standing in front of one is not reached through.

- A **press** — pointer down and up without travelling more than a few
  pixels — submits that part's declared instruction. It is the same
  `run().trigger(...)` the panel's button makes, and indistinguishable to
  the run, to its listeners and to a readback.
- A **drag** turns the part about the joint the control names. Each time
  the swept angle crosses one **quantum** — the input's current nudge
  amount converted through the published ratio, one digit = 36° on a
  Pascaline dial — one `move(input, {by, duration})` is issued, at most
  one at a time because the run gives an input one owner. The part
  **follows commits, never the pointer**: nothing here writes a
  coordinate, so the pointer may run ahead while the machine catches up,
  and a machine that will not move does not move. A request that does not
  complete leaves no remainder to be executed later, so a drag against a
  stop reports blocked and repeats nothing while it is held there.

Either way the outcome is reported twice through one path: beside the
pointer, in the same words the panel writes, and at the panel's own
control for that instruction or input. A press or a drag into a paused
run starts it, exactly as a press on the panel does.

A `controls` table this viewer cannot resolve is refused when the
document loads, naming the document, the control and what is wrong,
before anything is rendered — a part or joint that does not resolve in
the document's own tree, a joint that is not the part or one of its
ancestors, an instruction, input or coordinate absent from the table it
must belong to, a ratio that is missing, not finite or zero, an axis or
origin that is not three finite numbers, a joint whose own operations do
not begin with that coordinate's rotation (optionally preceded by
translations), two controls of one kind on one part, or a table on a
document that carries no program.

```js
const viewer = await SolidNodeWidget.mount('#host', 'viewer.json', {
  partControls: 'inline',   // 'none' suppresses the affordance
});
viewer.controls();
// [{ name: 'turn units', kind: 'turn', part: ['units', 'input', 'dial'],
//    input: 'units_entry', perUnit: -36, joint: ['units', 'input'],
//    coordinate: 'units.input.turn',
//    rect: { x, y, width, height }, point: { x, y } }, …]
```

`controls()` lists what the document declares, with each part's current
on-screen rectangle and a point at which a press actually reaches it —
found by casting, because the centre of a dial's rectangle is its axle —
both in viewport CSS pixels, and both `null` for a part that is hidden,
off screen or reached nowhere. A document that declares no control
answers `[]`.

`partControls` is **independent** of `driverControls`: a host that builds
its own instrument panel still wants the dial pressable, and the two
choices gate different pixels. Neither gates an interface — `controls()`
answers and the whole `handle.run()` API is there either way. The
headless capture passes `partControls: 'none'`, because a still
photograph is the last place a hover affordance should appear.

Not in this: no `Slide` (a prismatic drag), no dialling by position, no
keyboard gesture, and nothing anywhere writes a coordinate.

## What a part carries

A rigid part may declare what it **carries on its surface** — the digits
printed round a Curta's result roll, the graduations on a dial, a maker's
mark — and the framework publishes each one as a `markings` entry beside
the part's own `model`: a name, its own surface-mesh artifact, a colour in
`#RRGGBB`, and its own `mtime`. The viewer draws every one of them.

A marking is drawn **in the part's own place**, from the artifact alone.
No placement is published and the viewer computes none: the artifact
already holds the artwork's surface in the part's own frame, so the
part's own operations carry it. A decal therefore goes wherever its part
goes — through a driver, an animation instant, a run's committed bank,
the focused root and hide/show — with no code of its own for any of it.

A marking is drawn **in its own declared colour**, and the colour a part
inherits never reaches it: a part with no colour at all renders through
the normal-based material while its decal renders white, which is what
the framework's own marked fixture publishes.

A marking is drawn **over the surface it lies on**. The artifact carries
no offset, because where the surface is is the part's statement and not
the artwork's; the bias that keeps the decal clear of it is the
**viewer's own rendering constant** — a small world-space lift along the
sheet's own normals, and a minimum polygon offset under it — and says
nothing about where the part's surface is.

A marking is **not a part**. It is no row of the navigator, no node of
the assembly a host reads back, no focus or visibility target of its own,
and in no inventory: a host reading a marked document is given exactly
the nodes, paths, colours and geometry flags the same document without
its markings gives it. It is a region of a part's surface, and it is
hidden, shown and focused only with the part.

A marking **reloads on its own currency**. Its `mtime` is the artifact's,
not the part's, so editing artwork refetches the decal and leaves the
part's mesh alone — and rebuilding the part refetches the part and leaves
the decals alone.

A `markings` list this viewer cannot read is refused when the document
loads, naming the document, the node and the marking, before anything is
rendered — a value that is not a list, an entry that is not an object or
whose name or artifact reference is not a non-empty string, a colour that
is not six hexadecimal digits, one node declaring a name twice, or a
markings list on a node that is not rigid. A viewer that read nine digits
and silently dropped the tenth would show a false register, which is why
the answer is a refusal rather than a partial drawing.

`markings` is additive and gated on no document version: the marked
documents the framework publishes today declare version 2.

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
| 0.2.0 | 16 | 1, 2, 3, 4, 5, 6, 7 |

(13 is skipped deliberately: the in-flight `slide-and-turn-parts`
cycle claims it, and integration reconciles this row.)

## Working on the viewer

```
git clone https://github.com/LibreSolid/solid-node-viewer
cd solid-node-viewer
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/playwright install chromium
(cd solid_node_viewer/widget && npm ci && npm run build)
.venv/bin/python -m pytest
(cd solid_node_viewer/widget && npm run typecheck && npm test)
```

The Python suite skips what its environment cannot run — a headless
Chromium, Playwright, Pillow — and says so per test. The widget suite runs
a producer-generated parity fixture against the shipped expression
evaluator; that fixture is regenerated by the framework's own tool and
copied here, because the numbers in it are the framework's, not ours.

The development page is a static file this package carries
(`solid_node_viewer/widget/develop.html`), served directly by
`solid-node-viewer serve --build-dir <project>/_build` — there is no
second frontend process, no npm dev server and nothing to proxy. The
command still accepts `--dev`, `--start-frontend` and `--frontend-port`,
changing nothing and logging one notice per flag given: a released
solid-node's `solid develop --web-dev` passes `--start-frontend`, and
this keeps it working rather than turning it into an argparse error on a
flag the maker never typed.

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
