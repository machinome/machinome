# Changelog

All notable changes to Machinome Viewer. The Python package and the widget
it carries release together and share one version.

## Unreleased

- The viewer reads a document's `layers` and puts every part on its effective
  layers, its own entry's and every entry above it, as a part inherits its
  colour. The handle's `layers()`, `layer(key)` (an unknown key refused by
  name) and `show(layer | null)` show only the parts on one layer or the whole
  machine; a part the layer leaves out is absent for drawing, pressing,
  hovering, `partOnScreen` and framing, and the camera does not move. The
  shown layer composes with the navigator's focus and hidden paths without
  overriding either, is reported by `navigation()` and, per node, by
  `assembly()`, is kept on a republish that still declares it, and marks the
  navigator's rows it leaves out. `useMachine()` answers `layers`. The viewer
  adds no layer control of its own: a model's app makes its buttons. A
  malformed `layers` list refuses the document by name. Viewer API 32;
  document versions 1 through 14.
- A model's own app, named by its document's `app` record, is shown in place
  of the automatic panel, its instruction buttons and its animation bar,
  wherever the panel would be presented: the export page, the development
  page and a host's page mounting with the default options. It is not shown
  under `driverControls: 'none'` or on any on-demand mount, and no file of it
  is requested there. The app fills the viewer's area, places the model's
  picture with `<Viewport/>` and operates the machine through the helper
  `@machinome/viewer/app` (`useMachine()`, `usePlay()`, `useViewer()`); the
  inspector's sidebar stays beside it and the full-screen control stands in
  the picture's corner. An app that cannot be shown is named in a notice over
  the model, with no panel in its place; a malformed record refuses the
  document. A republish keeps an unchanged app and replaces an edited one,
  the picture standing. The web viewer bundles a model's app with its own
  build tool and its own React and React DOM 19.3.0 (the seam's operation
  `bundle`), from a source checkout with its JavaScript dependencies
  installed, and refuses by name elsewhere; the viewer's own bundle carries
  no React. `ViewerHandle.onMachineChange(listener)` tells a page once after
  every accepted change of a clocked machine's committed bank or drawing,
  whoever made it, and `MachineHandle.drawing()` answers whether a transition
  is being drawn. The viewer declares viewer API 31 and reads document
  versions 1 through 14.
- A row of the assembly navigator whose parts all show one colour now
  shows that colour, where a row with children showed only a colour its
  node declared or inherited and was otherwise neutral. A part is every
  node without children beneath the row, shown or hidden, and the node
  itself when it has a model of its own; a row whose parts show different
  colours, or a part with none, shows what it showed before. The assembly
  a host reads is unchanged: a node's `color` is still its own effective
  colour. Viewer API 30 and document versions 1 through 14 are unchanged.
- Viewer API 30 reads document versions 1 through 14. A node's published
  `color: {when, on, off}` selects its existing body's color from the same
  standing state as its pose, including ordinary controls, reset, restore
  and replay. Hover and highlight remain overlays over the latest model
  color, with no geometry replacement or asset fetch for a color change.
  Invalid conditions refuse before any candidate color or transform is
  published; a clocked request keeps its standing bank and events as well.
  Version-14 posed, clocked and running documents retain their execution
  kind by their existing payloads. Earlier documents keep their behavior.
- A loaded document's expressions are no longer parsed again between
  operations, however large the document: a pose, a drawn frame, a clocked
  request or a run tick reuses the graph its load prepared, where a
  document of more than 125,000 expression nodes was prepared again at
  every one. Obsolete expression state is reclaimed where it is created:
  when a document is loaded, refused or replaced, and when a viewer is
  disposed. Viewer API 30 and document versions 1 through 14 are
  unchanged.
- A flexible part reached by a changed input is rebuilt only when one of
  its parameter values moved: a part whose values all stand keeps its
  geometry, with no evaluation by molejo, no upload and no bounds pass,
  where it was rebuilt whenever an input its parameters read changed.
  Viewer API 30 and document versions 1 through 14 are unchanged.
- A pressed instruction or a drawn gesture on a clocked machine's panel
  now draws its transition over its declared duration from its first
  frame, which stands at the transition's origin, where the time the press
  itself took was taken from the motion and a slow press could jump to the
  end. The press judges the transition's end without drawing it and
  renders nothing itself, and a drawn request refused by a flexible part
  leaves every part where it stood. Viewer API 30 and document versions 1
  through 14 are unchanged.
- A pose of a document with a large bindings table now computes its
  formulas in one flat pass, only where an input moved, with the same
  values, refusals and messages as before, where every formula the moved
  input fed was walked again node by node. A document with a small table
  or none is evaluated as before. Viewer API 30 and document versions 1
  through 14 are unchanged.
- A flexible part reads its parameters by the expressions it prepared,
  without looking each text up again, and computes a rebuilt part's bounds
  in two passes over its vertices, where three.js's functions made three
  through accessors, with the same values, refusals and bounds as before.
  Viewer API 30 and document versions 1 through 14 are unchanged.
- Parts of one appearance, the kind of material and its colour, are drawn
  with one material, where every part had a material of its own. A hover,
  a highlight and a colour the model chooses point parts at other shared
  materials and back instead of writing them, with the same pictures and
  the same order of drawing as before. Viewer API 30 and document versions
  1 through 14 are unchanged.
- In the continuous render mode a frame in which nothing changed draws
  nothing and re-evaluates nothing, where every frame was drawn: a change
  is still shown by the next frame, and while something moves every frame
  is drawn as before, the frame it stops in included. A resize is drawn in
  the frame in which the canvas is resized instead of leaving that frame
  cleared. A script that read the canvas in a later animation frame of its
  own, relying on the viewer drawing every frame, now finds a picture only
  in frames that changed something; a read in the task of a call that
  draws and a page screenshot are unchanged. The on-demand mode, viewer
  API 30 and document versions 1 through 14 are unchanged.
- Dragging a clocked machine's slider now moves the machine with the
  thumb: one request per animation frame for the latest position, posed
  without a drawing, with the panel written in place so that the slider
  keeps the pointer and the focus, where the machine stood still until
  the release and was then drawn from where it stood. A click on the track
  (now drawn from the press), a key, a typed value and a nudge stay one
  request drawn over its duration, and while a clock's transport plays a
  slider is as before. The row reports the drag's travel since the press;
  the bank a drag leaves is the bank its requests leave, and a host
  reading the bank during a drag sees it follow the thumb. The on-demand
  mode, viewer API 30 and document versions 1 through 14 are unchanged.
- The parts and markings of a viewer that name one model file, and ask for
  it while it is being read, are drawn from one geometry, read and
  uploaded once, where every part parsed the file into a geometry of its
  own; the geometry is freed when the last part holding it is replaced,
  removed or disposed. Two viewers in a page never share a geometry: each
  further viewer holds a copy, freed with it. Which bytes a part is given,
  the requests a page makes, the pictures, the order of drawing, the mount
  handle, viewer API 30 and document versions 1 through 14 are unchanged.
- A part read from a model file no longer holds normals, in the page or in
  the graphics context, which halves the memory and the upload of its
  geometry. Each of its facets is lit from its own plane, as a flexible
  part's is, and the picture is within one step of 255 in a channel of
  the previous one except at pixels reached by a facet seen within about
  a pixel of edge-on or by a triangle of nearly zero area. Markings,
  flexible parts, highlights, picking, the order of drawing, the mount
  handle, viewer API 30 and document versions 1 through 14 are unchanged.

### Showing a machine of thousands of parts

Every entry above but the first was made for one page and measured on it:
an Enigma I of 3,347 drawn parts (2,868 read from 993 model files, 426
flexible parts and 53 markings, 44.8 million triangles), a clocked machine
whose document holds 546,768 expression nodes. One script measured the
viewer as it stood before the first of those changes and as it stands
after the last, each bundled with molejo 0.2.0:

| | Before | After |
|---|---|---|
| At rest for three seconds | 126 frames drawn, 421,722 draw calls, the page's script never idle | no frame drawn, no draw call, under 5 ms of script a second |
| Pressing a key, an instruction drawn over 2 s: the click itself | 5.3 to 6.2 s | 82 to 170 ms |
| frames drawn | 3, of about 2.7 s of script each | 28 to 31, of 70 to 77 ms each |
| the last frame | 10.9 to 11.9 s after the click | 2.00 to 2.08 s after it |
| Closing or opening the case, drawn over 3 s: the click itself | 3.4 to 4.3 s | 8 to 10 ms |
| frames drawn | 19 to 33 | 154 to 170, of 17 to 18 ms each |
| the last frame | 7.6 to 8.5 s after the click | 3.03 to 3.05 s after it |
| The case's slider dragged through eight positions | the machine at the thumb's value at none | at all eight |
| Memory of one open page | 4,097 MiB: the tab 2,087, the graphics process 1,889 | 2,488 MiB: 1,312 and 1,055 |
| its peak while the page loads | 4,468 MiB | 2,714 MiB |
| its peak while `reload()` holds two models | 6,258 MiB | 3,589 MiB |
| From the click that loads the machine to a ready page | 15.1 and 15.7 s | 10.3 and 10.5 s |

Measured in Chromium drawing in software, on a machine with no graphics
card. Draw calls were counted and not executed, so every time is the
page's script alone and none says what a graphics card draws in; memory is
the proportional set size of the browser's processes, and on a card the
graphics process's share is the card's. One run of each build for the
times, with three presses of the key and four moves of the case in it; two
for the load. The parts and the triangles drawn are the same, and so is
the picture of a state, but for the difference the last entry states.
With molejo's source of 21 November 2026, which no release of molejo
holds yet, in place of 0.2.0, a key press draws 45 or 46 frames of about
46 ms each and no other row moves. Not measured: any graphics card, and
any other browser.

## 0.9.0 — 31 October 2026

Released with Machinome 0.9.0 and numbered with it, the first release of
the viewer from the Machinome repository. It still declares viewer API 29
and reads document versions 1 through 13; what changed is where it lives,
how Machinome reaches it and the command that runs it.

- Machinome Viewer is part of the Machinome repository,
  <https://github.com/machinome/machinome>, at
  `packages/machinome-viewer/`, with its history. Its Python package is
  `machinome.viewer.web` (formerly `machinome_viewer`), a portion of the
  `machinome` package, and `python -m machinome.viewer.web` runs its command;
  the `machinome.viewer` entry point, the bundle, viewer API 29 and document
  versions 1 through 13 are unchanged.
  It is numbered with Machinome and requires the matching release, and it
  is licensed as every package of the repository, GPL-2.0-or-later or
  CERN-OHL-S-2.0-or-later, at the recipient's choice; the bundle's banner
  says so. Its manual is part of Machinome's,
  <https://machinome.readthedocs.io>. The widget builds from the
  repository's npm workspace, one `npm ci` at the root; its own lockfile is
  retired.
- A source checkout rebuilds a stale bundle when npm installed the
  widget's dependencies at the workspace root, and packaging refuses a
  symbolic `node_modules` at the workspace root as it refuses one in the
  widget.
- `npm ci` of the widget's build runs at the workspace root, so a second
  member's dependencies survive it.
- The package is the web provider of Machinome's seam of viewers,
  `machinome.viewer`: it declares the contract version it implements and its
  operations, `present`, `capture`, `serve` and `embed`, and Machinome finds
  it at `machinome.viewer.web` and runs it in its own process. The
  `machinome.viewer` entry point is removed; a host reads `machinome viewer`,
  whose report is unchanged. Staging a still
  moved into the package (`stage.py`), and `serve` runs the development
  server in a thread the package owns, whose open pages each rebuild reaches
  as `reload` on their socket, without a reconnect; a taken port is refused
  when serving starts. The capture's remedies say viewer.
- The package installs no command of its own: the `machinome-viewer`
  command is removed, and its verbs are Machinome's `machinome viewer
  describe`, `serve` and `capture`, with the same report, options and
  images, asking the viewer through the seam (`--viewer`, `web` by
  default). `serve` no longer takes `--dev`, `--frontend-port` or
  `--start-frontend`, which did nothing. `python -m machinome.viewer.web`
  runs `machinome viewer`: with no verb it prints the report, where it
  printed its help. The capture takes the camera's eye and target, up
  direction and field of view as given, each left to the viewer when
  absent. Once the server listens, `machinome viewer serve` and `machinome
  develop` print `Serving at http://0.0.0.0:PORT (Ctrl+C to stop)`.

## 0.8.1 — 10 October 2026

Released with Machinome 0.8.1 and numbered with it. The viewer is the
published 0.8.0 renumbered: nothing in the widget, the server or the
capture changes, it still declares viewer API 29 and reads document
versions 1 through 13, and `pip install "machinome[viewer]"` installs the
pair. Machinome 0.8.1 corrects the framework without moving the document,
so a 0.8.0 viewer reads a 0.8.1 export too.

## 0.8.0 — 5 October 2026

Released with Machinome 0.8.0 and numbered with it. It declares viewer API
29 and reads document versions 1 through 13. Install both with
`pip install "machinome[viewer]"`. The document format does not move: a
0.7 viewer reads a 0.8 export, and this viewer reads every 0.7 export.

### What a host gets

- **Where a part stands on screen.** `partOnScreen(path)` gives, for any
  assembly path, a part or a subassembly, the screen rectangle of its
  visible geometry and a visible point on it, in viewport CSS pixels, or
  null when nothing of it is in view; `project(world)` gives the screen
  position of any world point. Both read the current pose and camera and
  draw nothing, and `controls()` answers from the same computation. API 28
  (`track-a-part-on-screen`).
- **A part highlighted.** `highlight(paths, options)` tints the named parts
  and keeps, dims or ghosts every other part, draws before it returns, and
  gives back a function that puts every part back exactly. One highlight
  stands at a time; it survives a reload and the targeted updates, and a
  part inside a ghosted housing is still found on screen. API 28
  (`highlight-a-part`).
- **Up and field of view per view call.** `setView(view)` takes an
  optional up direction and vertical field of view beside the camera and
  target; what is omitted keeps its value, and `view()` reports all four.
  The adopted up and field of view persist through `setRoot()`, `reload()`
  and the targeted updates, and orbiting by pointer turns about the adopted
  up. An invalid up or field of view is refused by name before anything
  changes. API 28 (`move-up-and-field-of-view`).
- **A clocked machine captured on demand.** `renderMode: 'on-demand'` mounts
  a clocked (version 8) document, with or without declared instructions,
  under the same four options that mode already required.
  `machine().move`, `restore` and `reset` pose the model and draw it before
  they return, and `setView(viewer.view())` redraws without changing the
  view, so a host poses a machine request by request and captures each
  frame with no frame loop running. `machine().trigger` and
  `machine().setClockPlaying(true)` draw over wall-clock seconds and are
  refused there, naming the mode. A running program stays refused, now with
  a message of its own. No control and no full-screen button is drawn.
  API 29 (`on-demand-clocked`).

### What a maker gets

- **The same picture on every load.** A freshly mounted model draws its
  rigid parts and markings the same way whichever of their files finishes
  downloading first, so two parts sharing a surface no longer change colour
  from one load to the next, and repeated captures of one model at one view
  and pose agree pixel for pixel. Files are still fetched concurrently;
  nothing in the API or the document changes
  (`deterministic-asset-load-order`).
- **A whole printer mounts.** A posed export the size of a complete 3D
  printer, the Voron 2.4's 1,565 parts and 232,347 bindings, now mounts and
  draws. Its expressions are validated in one pass instead of being rebuilt
  for every part, and geometry files are fetched at most four at a time
  across every viewer on the page, so the browser no longer runs out of
  network resources before the model appears. Every refusal of a malformed
  document stands, and nothing in the API or the document changes
  (`mount-voron-export`, ADR-078).

### Compatibility

API 28 brings the screen-position, highlight and per-view up and field of
view members; API 29 the on-demand clocked mount. A host checks
`apiVersion` before relying on them: a bundle reporting 27 has none of
them, and one reporting 28 refuses an on-demand clocked mount.

## 0.7.1 — 27 September 2026

Released with Machinome 0.7.1 and numbered with it. The viewer is the
published 0.7.0 renumbered: nothing in the widget, the server or the
capture changes, it still declares viewer API 27 and reads document
versions 1 through 13, and `pip install "machinome[viewer]"` installs the
pair. Machinome 0.7.1's frames and mates compile to the rest placements,
joints and coordinates the document already carries, so a 0.7.0 viewer
reads a 0.7.1 export too.

## 0.7.0 — 23 September 2026

The first published release of Machinome Viewer, released with Machinome
0.7.0 and numbered with it. It declares viewer API 27 and reads document
versions 1 through 13. Install both with `pip install "machinome[viewer]"`.

### What a maker gets

- **A machine in the browser.** Orbit, pan and zoom a published model; open
  the assembly navigator to expand, focus, hide and show parts, by pointer or
  keyboard; collapse it into the inspector's sidebar. The same bundle powers
  the framework's development page, with live reload and a build-error pane
  over the last good model, the self-contained export page, custom embeds and
  headless capture.
- **Posed models.** Sliders and exact-value readouts for declared drivers,
  instruction buttons, and an animation timeline that plays a declared loop
  in real time with a speed control.
- **Running machines.** Movement and rate requests, nudge and jog, named
  instructions, and run, pause, step and reset, executed in a Web Worker in
  fixed ticks. Every request reports its outcome, completed, blocked with the
  travel admitted, refused or cancelled. Snapshot, restore and bounded
  recording. The engine executes what Machinome publishes: laws that read the
  coordinate they drive, blocks whose order a part's position selects, bounds
  that read other coordinates, `Play` clearance laws, explicit time drives,
  source-timed motion, a `Follow` retained between two moving clearance
  surfaces and finite convex-profile contact inside a numeric bound
  (document versions 5 to 7 and 9 to 13), reproducing the
  framework's conformance corpus bit for bit. A determined source keeps its
  stroke, dwell and landing through the chains and selected blocks that
  read it, so a calculator's carry does not change when later result
  stations join the graph. A version 12 `Follow` keeps a free follower
  where a retreating surface left it and stops at the first incompatible
  interval through its paired dynamic bounds, checking the producer's
  certified cuts as well as the uniform samples; unsupported boundary paths
  and contacts too narrow to represent are refused rather than approximated
  (ADR-075). A version 13 document's `profileOverlap` flag, read inside an
  ordinary numeric running Bound, tests pointwise inclusive contact between
  producer-supplied finite convex planar polygons; it does not certify
  continuous motion, installed geometry or collision volume. Invalid
  profiles and unrepresentable placements refuse by name.
- **Clocked machines** (document version 8). One request per gesture, solved
  at once: stops clip the request, events commit in path order, states are
  read-only readouts. A pressed instruction is drawn over its declared
  duration, a handle gesture at the tempo of the instruction naming its
  input, or over a fifth of a second when none does. A declared elapsed
  clock gets play, step and speed.
- **Touching the parts.** A model that declares `Button`, `Turn` or `Slide`
  controls makes those parts pressable and draggable, one request per
  gesture, the part following what the machine commits. Two `Turn` controls
  may name one part when they select different joints: each gets its own
  named drag handle, and a drag on the undecided body requests neither. Two
  turns selecting the same joint still refuse at load. This is API 27; the
  document and its controls are unchanged.
- **Markings.** Digits and other markings a part carries are drawn on its
  surface, so a calculator's dials can be read.
- **Full screen.** A full-screen button, and the `f` key, on a running
  machine's transport bar, on the inline animation timeline, or, for a
  static model, a drivers-only posed model or a clocked machine, as a
  permanent corner overlay. The whole composed layout goes full screen, with
  the model's own page background instead of the browser's black backdrop.
  Escape leaves it, as does the button; absent where the browser or the
  embedding page does not permit full screen, such as an iframe without
  `allowfullscreen`. Never drawn in a headless capture.

### What a host gets

- `MachinomeViewer.mount`, `mountInspector`, `mountNavigator` and
  `mountDevelopment`, each returning a handle with the camera, assembly,
  timeline, driver, instruction, running and clocked operations the manual
  documents, plus `setView` and an on-demand render mode for scripted stills.
  Stable CSS classes and custom properties for the navigator and inspector.
- `machinome-viewer describe|serve|capture`: the version, API and document
  versions as JSON; a development server for a published build; a headless
  PNG capture. A source checkout rebuilds a stale bundle when its build tools
  are present and refuses what it cannot repair.
- One bundle, `machinome-viewer.js`, with the browser global
  `MachinomeViewer` and the `data-machinome-widget` declarative mount. New
  documents are `machinome-export`; historical `solid-node-export` documents
  still load.

### Corrections carried into the release

- Source timing. An endpoint-era executor handed each downstream block only
  its predecessor's net increment, a straight line that re-timed the Curta's
  carry gate. Determined sources now retain their motion path (ADR-071).
  Because an older viewer reads the corrected payload and silently executes
  the wrong carry, the viewer declared API 24 and document versions 1 to 11,
  raised to API 25 and versions 1 to 12 by `Follow` and to API 26 and
  version 13 by finite profile contact; new running exports declare
  version 11, or 12 with a `Follow`, or 13 with profile contact, and their
  identity carries the
  source-timing generation, so endpoint-era snapshots refuse to restore into
  a re-exported program. Legacy running documents load and run with the
  corrected physics. Re-export is the migration (ADR-072).
- A running `move(to=...)` lands on its exact converted endpoint instead of
  a reconstructed `start + travel` one ULP past it, so a request to an
  inclusive bound completes instead of recording a false stop, and bounds
  are judged against the state that is committed. A running step whose
  already-evaluated law result is non-finite, including a valid start with
  an invalid endpoint, refuses through the existing `law` refusal and banks
  nothing; earlier successful steps of the command stand. Both pair with
  the framework producer's corrections; no document field or API changes.
- A clocked handle gesture is drawn at the tempo of the first `by`
  instruction naming its input, scaled to admitted travel; the 0.2-second
  duration remains when no instruction declares a travel, and pressed
  instructions keep their declared duration (ADR-073).
- `websockets` is a runtime dependency, so a fresh
  `pip install "machinome[viewer]"` gives a `machinome develop` page whose
  live reload connects. The test environment installs `setuptools`, which
  Python 3.12 no longer provides.
- A distribution build refuses to run through a symlinked `node_modules`
  before an install can modify another checkout's dependencies.

### Running a calculator-sized machine

Six measured cycles on the pinned OperatingCurta export, each accepted only
with an identical 213-coordinate bank: expression references survive cache
pressure; unchanged expression nodes are reused across adjacent path pieces
and only the names a followed expression reads are retained for reset; the
finite reclaim trigger rises from 50,000 to 125,000 nodes so a fitting
machine keeps its graph across ticks; a determined constraint bound is
sampled through a search-local moving cone (ADR-074); and coordinates read
by running bounds, including the Curta's self-read anti-reversal pawl,
retain exact motion. The first 48 crank ticks fell from 65.7 to 28.1 seconds
without WebGL, and the first 18-degree tick from 2.13 to 1.08 process-CPU
seconds. Three cycles after the source-timing correction, accepted on the
same terms: a determined running bound reuses the exact standing values of
the previous successful search on the same run when its numeric inputs and
moving names are unchanged (14.3% less process CPU over the first 48
default crank ticks); two bounds that replay one `Follow` prefix share it
at the same sample fraction within a stretch; and certified numeric
kink-cut expressions reuse equal-fraction probes within one search (16.4%
less over five ordinary ticks), with all 768 ordered bound levels and the
214-coordinate bank unchanged. A fourth reuses a cyclic block's previous
successful motion within one running engine when every source holds still
and every numeric input matches bit for bit, rebuilding fresh constant paths
rather than sharing them: each 48-tick reversing-lever gesture fell from
3.2–3.6 to 1.7–2.1 process-CPU seconds, with every bank, admission, crossing
and stop identical. A complete browser revolution remains far
slower than its declared two-second drawing duration; that work continues.

- Moving-contact stops act at their first located contact, so a long request
  stops at the first obstruction rather than a later free window; a landing
  on a moving threshold follows the parts' relative motion; exact following
  contact is certified rather than rounded into a false departure.
- The navigator shows full part names on hover and keeps its scroll and
  keyboard focus while rows are toggled.
- Large control panels stay in a side rail with internal scrolling instead
  of covering the model.

### Identity and licensing

- Package `machinome-viewer`, import `machinome_viewer`, entry point
  `machinome.viewer`. The framework reaches it only through that entry
  point and separate processes; neither package imports the other. The
  widget ships inside the Python distribution and is not published on npm.
- The version number identifies the distribution; capability is declared by
  `apiVersion` and `documentVersions` alone. Development states 0.1.0 and
  0.2.0 were never published; their detailed history is in
  [workflow/archive/changelog-before-0.7.md](workflow/archive/changelog-before-0.7.md).
