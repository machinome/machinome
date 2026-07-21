## Why

The shop floor currently has no functional-model inspection, and importing a
project model into the long-lived floor process would leave it holding stale
Python module state as the machinist changes the project. Makers need to see
the current model in the browser without restarting the floor or relying on
that unsafe import boundary.

## What Changes

- Build the selected project-local functional model through the `solid` CLI
  when the shop floor opens, instead of importing it into the floor service.
- Give a project whose selected model does not exist a clean, explanatory shop-open
  failure rather than starting a floor with no inspectable result.
- Serve the completed static build artifacts from the project's `_build`
  directory in the shop workspace.
- Render those artifacts with the established solid-node viewer semantics:
  evaluated transform hierarchy, inherited material colours, normal material
  for uncoloured meshes, Z-up camera fitting, orbit interaction, and animated
  timeline controls.
- Start `solid develop` for the machinist with a floor-broker callback so
  source changes cause the browser model view to refresh through SSE.

## Capabilities

### New Capabilities

- `functional-model-inspection`: Builds and presents the current project model
  in the shop floor, including development-time refresh notifications.

### Modified Capabilities

- `shop-browser-workspace`: The artifact area gains an available functional
  model view instead of always reporting that no artifact is selected.
- `shop-floor-lifecycle`: Opening the shop now validates and builds the
  project's model before the service is presented as open.

## Impact

- Affects the porter/shop-open flow, `floor` broker, static artifact serving
  and HTTP/SSE APIs, and the browser artifact view.
- Requires the published build snapshot to carry the animation cadence needed
  to render its raw `$t` operations without a project runtime.
- Adds an integration boundary to the installed `solid` CLI (`build` and
  `develop`) and a selected project-local model path, defaulting to
  `__init__.py`.
- Affects machinist launch configuration so it supplies the broker callback
  without coupling the floor process to project Python modules.
