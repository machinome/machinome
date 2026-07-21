## 1. Framework build boundary

- [x] 1.1 Establish `solid build` publication of `_build` viewer artifacts and `solid develop --callback` build-ready notification in the linked solid-node change.
- [x] 1.2 Verify the framework contract against a project using the default
  `__init__.py` path, a project selecting `root`, and a missing selected model.
- [x] 1.3 Extend the published `viewer.json` build contract with versioned
  animation `fps` and `frames`, and validate that it is atomically published
  with the model tree without loading project Python in Floor.

## 2. Floor model boundary

- [x] 2.1 Implement the floor CLI adapter and static `_build` serving boundary without importing, executing, reloading, inspecting, or serving project Python.
- [x] 2.2 Make the porter/shop-open flow build the selected project-local model before announcing an open browser location, with clean build-failure reporting.
- [x] 2.3 Add broker storage and a locally validated callback endpoint that accepts only a successfully built model update.

## 3. Complete browser renderer

- [x] 3.1 Replace the provisional Floor viewer with a Floor-owned renderer
  derived from the established static viewer contract: nested groups, full
  OpenSCAD expression evaluation, correct premultiplied transforms, and
  stale-load-safe replacement trees.
- [x] 3.2 Match established viewer appearance and framing: inherited colours,
  normal material for uncoloured meshes, Z-up fitted camera, lighting, and
  working orbit rotate/zoom behavior.
- [x] 3.3 Implement animated-model play/pause and timeline controls from the
  published `fps`/`frames`, hidden by default behind a compact Timeline toggle,
  with no controls for static models.
- [x] 3.4 Publish the model-change notification through the run SSE stream and
  replace the complete renderer tree only after a successful static reload;
  preserve the preceding complete tree on failure and retain the maker's
  camera/orbit state across a successful replacement.

## 4. Evidence

- [x] 4.1 Add red-first floor tests for initial build, missing model, no in-process project import, and callback-driven refresh.
- [x] 4.2 Add browser end-to-end evidence for actual rendered geometry,
  orbiting and zooming, colour inheritance and normal materials, animated
  playback/timeline, static-model control omission, and callback replacement
  without stale meshes.
- [x] 4.3 Validate V8 as the acceptance project: inspect its materialled,
  interactive, animated build from `root` and run the relevant Python,
  frontend, browser, and framework suites.
