# Changelog

All notable changes to Machinome Viewer. The Python package and the widget
it carries release together and share one version.

## Unreleased

- Viewer API 25 reads document versions 1–12 in current source. Version 12
  executes a retained running `Follow` between two certified moving clearance
  envelopes, preserving a free follower on retreat and stopping at the first
  incompatible interval through its paired dynamic bounds. Older documents
  keep their existing law and `Play` behavior; this source capability has not
  been released with a new package version.
- A determined running Bound may reuse exact standing expression values from
  the previous successful search on the same run when its numeric inputs and
  moving-name set are unchanged. Moving values still run at the first and
  every later prescribed sample. OperatingCurta's pinned first 48 default
  crank ticks used 14.3% less process CPU with bit-identical Bound samples
  and complete bank; a full revolution is not yet interactive at its
  declared two-second duration.
- Certified numeric kink-cut expressions now reuse successful equal-fraction
  probes within one search. Arbitrary callbacks and uncertain or stateful
  graphs retain eager evaluation. On the pinned production OperatingCurta,
  five ordinary 0.1-second viewer ticks used 16.4% less process CPU in a
  controlled pair, with all 768 ordered Bound levels and five full
  214-coordinate bank hashes unchanged. This remains far from an interactive
  two-second full revolution and is not a released capability.

## 0.7.0 — 22 September 2026

The first published release of Machinome Viewer, released with Machinome
0.7.0 and numbered with it. It declares viewer API 24 and reads document
versions 1 through 11. Install both with `pip install "machinome[viewer]"`.

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
  that read other coordinates, `Play` clearance laws, explicit time drives
  and source-timed motion (document versions 5 to 7 and 9 to 11),
  reproducing the framework's conformance corpus bit for bit. A determined
  source keeps its stroke, dwell and landing through the chains and
  selected blocks that read it, so a calculator's carry does not change
  when later result stations join the graph.
- **Clocked machines** (document version 8). One request per gesture, solved
  at once: stops clip the request, events commit in path order, states are
  read-only readouts. A pressed instruction is drawn over its declared
  duration, a handle gesture at the tempo of the instruction naming its
  input, or over a fifth of a second when none does. A declared elapsed
  clock gets play, step and speed.
- **Touching the parts.** A model that declares `Button`, `Turn` or `Slide`
  controls makes those parts pressable and draggable, one request per
  gesture, the part following what the machine commits.
- **Markings.** Digits and other markings a part carries are drawn on its
  surface, so a calculator's dials can be read.

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
  the wrong carry, the viewer declares API 24 and document versions 1 to 11;
  new running exports declare version 11, and their identity carries the
  source-timing generation, so endpoint-era snapshots refuse to restore into
  a re-exported program. Legacy running documents load and run with the
  corrected physics. Re-export is the migration (ADR-072).
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
seconds. A complete browser revolution remains far slower than its declared
two-second drawing duration; that work continues.

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
  `machinome.viewer`, licensed AGPL-3.0-only. The framework, Apache-2.0,
  reaches it only through that entry point and separate processes; neither
  package imports the other. The widget ships inside the Python
  distribution and is not published on npm.
- The version number identifies the distribution; capability is declared by
  `apiVersion` and `documentVersions` alone. Development states 0.1.0 and
  0.2.0 were never published; their detailed history is in
  [workflow/archive/changelog-before-0.7.md](workflow/archive/changelog-before-0.7.md).
