## Why

The shop floor renders functional models with its own copy of the solid-node
viewer: `floor/frontend/src/viewer.ts` reproduces the framework's expression
evaluator, tree composition, materials, lights, and camera fit almost token for
token, adding only a preserved camera, a `dispose()`, and a `Timeline` toggle
(SPRINT-002 brief, F-1). A capability added to the framework's viewer does not
reach the floor, and the floor carries a second three.js in Git to keep the copy
running (F-6).

The framework now ships one reusable viewer with the options the floor needs and
a CLI accessor that reports the installed bundle and its API version
(sprint-002 cycles F2 and F3, framework `sprint-002` @ `5c14acf`). This change
retires the floor's copy and makes the floor a consumer of that bundle, so the
sprint goal — one viewer behind every surface — holds for the shop floor.

## What Changes

- The floor obtains the viewer bundle from the installed framework through its
  CLI, during the existing fail-closed preparation, and serves that bundle to
  the browser from its own static surface. The floor does not import
  `solid_node` (brief D-2, F-11).
- Preparation fails, with the remedy named, when the installed framework
  supplies no viewer bundle or supplies one whose API version is below what the
  floor requires. The shop does not open. There is no degraded in-browser state
  (brief D-5).
- `floor/frontend/src/viewer.ts` is deleted. The React wrapper in
  `floor/frontend/src/main.tsx` keeps its role — mount, preserve camera across a
  rebuild, dispose on unmount — and drives the framework viewer's handle
  instead.
- `three`, `@types/three`, and `jokenizer` leave `floor/frontend/package.json`;
  the committed `floor/static` build is regenerated without the second three.js
  copy (F-6).
- **BREAKING** for a shop run against an older framework: opening a named
  project shop now requires an installed solid-node that ships a compatible
  viewer bundle.
- `tests/fixtures/fake_solid.py` gains the viewer accessor so the shop's tests
  keep exercising the whole framework interface through the fake CLI.
- The floor's viewer snapshot handling accepts the additive `format` field that
  cycle F1 added to `viewer.json`; `shop-skills/solid-node-api/SKILL.md` records
  it, and records that the first build after upgrading the framework can produce
  one ordinary content-hash change the model watcher reports as a model change.

## Capabilities

### New Capabilities

None. This change replaces the mechanism behind an already-ratified behavior and
adds one preparation failure condition to an existing capability.

### Modified Capabilities

- `functional-model-inspection`: the requirement that the floor presents the
  complete static viewer experience currently ends with "It SHALL NOT use the
  separate export widget" — a mechanism inside a behavioral spec, and one this
  change deliberately reverses (brief F-7). It is restated as the outcome the
  maker sees, leaving the renderer's provenance to design and ADR. A new
  requirement covers refusing to open when the installed framework supplies no
  usable viewer.

## Impact

- `floor/preparation.py` — a viewer-accessor stage and the bundle path and API
  version carried on `PreparedProject`.
- `floor/app.py` — a static route serving the framework-supplied bundle;
  `floor/orchestrator.py` and `floor/__main__.py` pass it through.
- `floor/frontend/` — `src/viewer.ts` deleted, `src/main.tsx` rewritten against
  the framework viewer handle, `index.html` loading the bundle, and
  `package.json` losing three dependencies.
- `floor/static/` — regenerated committed assets.
- `tests/fixtures/fake_solid.py`, `tests/test_project_preparation.py`,
  `tests/test_floor_api.py`, and the browser end-to-end tests.
- `openspec/specs/functional-model-inspection/spec.md` and
  `docs/adrs/0004-static-build-artifact-boundary-for-functional-model-inspection.md`,
  whose exclusion of `solid export` and its widget no longer holds.
- `shop-skills/solid-node-api/SKILL.md`.
- Depends on framework cycle `viewer-bundle-delivery`, integrated into
  `solid-node` `sprint-002` @ `5c14acf`.
