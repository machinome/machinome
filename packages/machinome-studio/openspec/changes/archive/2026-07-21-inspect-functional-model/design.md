## Context

The FastAPI floor is a long-lived broker, while a project model is Python code
that the machinist changes during a run. Importing the model in the broker
would cache the module and makes the visible model stale. The existing browser
workspace has an artifact pane but no functional-model content.

`solid build <project-local-model-path>` now atomically publishes a complete
viewer snapshot and its referenced model files in the normal project `_build`
directory. `solid develop <project-local-model-path> --callback URL` sends an
empty POST after each successful publication and never sends one for a failed
rebuild. Floor consumes those published static files and never executes project
Python.

## Goals / Non-Goals

**Goals:**

- Accept an explicit project-local functional-model path, defaulting to
  `__init__.py` for projects that use it.
- Have the floor use a one-shot solid CLI build before reporting the shop open.
- Keep project Python execution outside the floor process.
- Serve the completed `_build` viewer snapshot and referenced model files in
  the floor artifact area.
- Refresh the visible model after the machinist's development process reports
  a successful change to the broker.
- Let the browser recover using a complete current model state when a refresh
  occurs.
- Deliver the complete established viewer experience from the static build:
  materials, camera fit, orbit interaction, and time-based motion controls.

**Non-Goals:**

- Reuse or change `solid export` or its separate export widget.
- Implement delta/state-patch delivery; a complete state reload is sufficient.
- Browse a project or expose its design process.
- Load or execute a project model inside the floor service.

## Decisions

### The floor owns model lifecycle, not model execution

The porter/floor-open path receives a project-local model path and invokes the
framework-provided one-shot build command as a subprocess from the project
root. The framework
command must either produce the serving input for the floor or exit cleanly
with a useful missing-model result. The floor stores and serves only the build
result; it does not import the model.

An in-process import was rejected because Python module caching makes an
updated model unreliable without restarting the broker. A persistent child
interpreter was also rejected: it adds lifecycle and isolation concerns while
still creating a long-lived model runtime.

### The published build directory is the cross-repository seam

The porter/floor-open path invokes `solid build <project-local-model-path>`
from the project root. For example, V8 selects `root`, so floor invokes
`solid build root` with the V8 checkout as its working directory.
On success, the framework atomically publishes `viewer.json` and all referenced
model files in the project's normal `_build` directory. Floor serves that
static output to browser clients.

For development, the machinist process runs `solid develop
<project-local-model-path> --callback <floor-callback-url>`. The callback is an
empty POST issued only after the same complete build output has been published;
floor uses it only to notify browsers to reload the current static output. The
callback URL may contain a floor-generated per-run capability for local
validation.

Using existing `solid develop` without a callback was rejected because it
cannot notify the floor deterministically. Polling project files was rejected
because it duplicates framework change detection and cannot establish that a
new model is successfully built.

### Floor never imports or executes project Python

The long-lived floor process serves only completed files from `_build`: the
viewer snapshot and its referenced model files. It SHALL NOT import, execute,
reload, inspect, or serve project Python source. Project Python is executed
only in the short-lived `solid build` subprocesses and the framework-owned
`solid develop` process.

This is a deliberate boundary, not merely a stale-module workaround. It keeps
floor independent of Python module caching and makes the CLI's atomic build
publication the sole source of visible model state. `solid export` and its
separate export widget are outside this architecture and this story.

### Floor owns the browser renderer for the published snapshot

Floor's browser frontend fetches `viewer.json` and the referenced STL files
from floor's static artifact route and renders them client-side. It does not
reuse `solid export` or its widget, and it does not ask the floor backend to
interpret the model. This keeps the renderer scoped to the floor's browser
experience while retaining `_build` as its only model input.

Floor implements its own browser renderer using the established static
widget's rendering contract as the reference implementation; it neither embeds
nor invokes the export widget. The renderer SHALL recreate the published node
tree as nested Three.js groups, recompute each local matrix from its raw
operations for every time change, and compose operations by premultiplying in
their published order. It SHALL use the widget's complete OpenSCAD expression
evaluator, including `$t`, exponentiation, the Math functions, and
degree-based trigonometry; a partial numeric coercion is not an acceptable
viewer implementation.

The renderer SHALL inherit a parent colour when a node has none, use
`MeshStandardMaterial` for an explicit or inherited colour, and use
`MeshNormalMaterial` when no colour is available. It SHALL keep the
OpenSCAD-compatible Z-up camera, fit the complete loaded model bounds, provide
working orbit rotation and zoom, and render on every interaction and animation
frame.

If any published operation references `$t`, Floor SHALL expose a play/pause
control and a 0..1 timeline slider, autoplaying by default and advancing over
the published animation cadence. The slider bar SHALL be hidden by default and
available through a compact persistent Timeline toggle in the model view, so it
does not obscure ordinary inspection. Static models SHALL have no animation
controls. The build snapshot must therefore include the animation `fps` and
`frames` alongside its root tree; Floor cannot infer an animation contract from
project Python or select arbitrary timing values.

Model reload creates a complete replacement renderer tree. It SHALL not allow
late STL loads from a superseded tree to reappear, and it SHALL preserve the
last complete displayed tree if the replacement cannot load. A successful
replacement SHALL retain the maker's camera position, orientation, zoom, and
orbit target; it may fit the camera only for the first successfully loaded
model.

### The broker turns build-ready notifications into SSE refresh events

The broker exposes a local callback endpoint for the framework development
process. Once it accepts a valid build-ready notification, it updates its
model snapshot/reference and publishes a model-changed event on the existing
run SSE stream. The browser responds by fetching the complete current
functional-model state and replacing the artifact view.

Delta payloads are deferred. Full-state reload is robust across an interrupted
browser connection and does not constrain the future framework artifact
representation.

## Risks / Trade-offs

- [A build fails after a previously usable model] → Preserve the last
  successfully built state and surface the failure through the floor rather
  than presenting a partially updated model.
- [Local callback is invoked by an unintended process] → The eventual
  framework/floor protocol must use a per-run, unguessable local capability or
  equivalent validation; exact mechanism is an open framework-interface
  decision.
- [Full reload is expensive for large models] → Start with it as the correctness
  baseline; introduce deltas only when evidence shows they are needed.

## Migration Plan

1. Ratify this shop proposal as the originating-project requirement.
2. Use the implemented CLI build and callback boundary.
3. Implement static `_build` serving, the broker callback/SSE event, and the
   workspace view.
4. Verify initial build, missing-model failure, and a machinist-triggered
   refresh in an isolated project fixture.

Rollback removes the floor integration and retains the existing shop workspace;
no project model is imported or persisted by the floor.

## Open Questions

- How should floor expose a per-run callback capability in its local URL?
