## 1. Red Public Identity Contract

- [ ] 1.1 Add failing Python packaging/entry-point/command tests for `machinome-viewer`, `machinome_viewer` and `machinome.viewer`.
- [ ] 1.2 Add failing frontend tests for `MachinomeViewer`, `machinome-viewer.js`, Machinome DOM/CSS names and the incremented viewer API version.
- [ ] 1.3 Add failing loader tests for current `machinome-export`, retained legacy `solid-node-export`, and rejection of other formats.

## 2. Python And Process Rename

- [ ] 2.1 Rename the Python package tree, module invocation, console script, entry point, metadata, repository URLs and diagnostics.
- [ ] 2.2 Preserve the lightweight lookup and process-only framework boundary under the renamed contracts.
- [ ] 2.3 Update package build hooks, describe/serve/capture behavior and Python tests for renamed paths and artifacts.

## 3. Browser Contract Rename

- [ ] 3.1 Rename the bundle, browser global, auto-mount attributes, public class names and CSS custom properties consistently.
- [ ] 3.2 Raise the viewer API version once and update host-facing tests, standalone/development pages and generated source banner.
- [ ] 3.3 Update current fixtures to Machinome format while retaining dedicated immutable legacy-format fixtures.

## 4. Records And Validation

- [ ] 4.1 Update README, changelog current entry, current specs, package docs and contributor commands while preserving historical archives and ADR bodies.
- [ ] 4.2 Add the rename ADR and update current architecture/ADR indexes if implementation confirms the public-contract decision.
- [ ] 4.3 Run frontend unit tests, typecheck, build and browser E2E where available; run the Python suite and reference audit.
- [ ] 4.4 Build and install wheel/sdist and smoke `describe`, `serve`, `capture` where available and package contents.
- [ ] 4.5 Run paired framework validation for current and legacy documents, sync specs, archive and leave the branch clean.
