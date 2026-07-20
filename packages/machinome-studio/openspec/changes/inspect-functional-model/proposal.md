## Why

The shop floor currently has no functional-model inspection, and importing a
project model into the long-lived floor process would leave it holding stale
Python module state as the machinist changes the project. Makers need to see
the current model in the browser without restarting the floor or relying on
that unsafe import boundary.

## What Changes

- Build a project's conventional `__init__.py` model through the `solid` CLI
  when the shop floor opens, instead of importing it into the floor service.
- Give a project with no conventional model a clean, explanatory shop-open
  failure rather than starting a floor with no inspectable result.
- Reuse the solid-node frontend widget in the shop workspace and implement its
  model-serving endpoints in floor.
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

- Affects the porter/shop-open flow, `floor` broker, model-serving and HTTP/SSE
  APIs, and the browser artifact view through the solid-node frontend widget.
- Adds an integration boundary to the installed `solid` CLI (`build` and
  `develop`) and the conventional project-root `__init__.py` model location.
- Affects machinist launch configuration so it supplies the broker callback
  without coupling the floor process to project Python modules.
