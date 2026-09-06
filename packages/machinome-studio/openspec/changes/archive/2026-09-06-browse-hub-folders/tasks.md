## 1. Entry resolution and folder listing

- [x] 1.1 Write failing tests for `resolve_entry`: a top-level project, a nested project, a model of a multi-model project, an undeclared model name, a dot component, an absolute path, and a path that stops at a repository root before its segments run out
- [x] 1.2 Implement `HubEntry` and `resolve_entry(path, project_home)` in `floor/preparation.py`, walking only inside the working folder and stopping at the first Git repository root
- [x] 1.3 Write failing tests for `list_folder`: a folder holding projects, a folder holding only folders, a directory holding no project at any depth, a multi-model project listed as a folder, a single-model project listed as a project, and a multi-model project's own listing containing only its declared models
- [x] 1.4 Implement `list_folder(project_home, path)` with the bounded "holds a project below it" walk that skips `.git` and `_build`
- [x] 1.5 Give each listing entry its browser value: path, kind, name, and for a folder the count of openable projects it holds

## 2. Model-aware preparation

- [x] 2.1 Write failing tests that preparing an entry naming a declared model resolves that model's `build_dir`, builds with `solid build <model>`, and leaves a sibling model's build directory untouched
- [x] 2.2 Add `model` to `PreparedProject`, resolve the artifact root for the named model, and carry the model into `build_command` and `build_invocation`
- [x] 2.3 Write a failing test that a single-model project's preparation is byte-for-byte the invocation it uses today
- [x] 2.4 Point the watcher's rebuild at the prepared invocation so a model session rebuilds only its own model

## 3. Per-model screenshots

- [x] 3.1 Write failing tests that a named model's screenshot is read, compared and published at `screenshots/<model>.png`, that a sibling's screenshot is untouched, and that a single-model project still uses `screenshot.png`
- [x] 3.2 Take the entry rather than the project root in `screenshot_path`, `screenshot_revision`, `is_safe_screenshot` and `refresh_project_screenshot`, and render the entry's model
- [x] 3.3 Stage the entry's own screenshot path in the scoped `git_commit`, and cover it with a failing-first test

## 4. Sessions keyed by entry

- [x] 4.1 Write failing tests that two models of one repository open as two sessions with their own agents and conversations, that reopening an entry joins its session, and that closing one leaves the other running
- [x] 4.2 Key `SessionRegistry` by entry path, carry the entry on the session, and publish hub events naming the entry path
- [x] 4.3 Give the session's model to its agents through the role context, and default the scoped `solid_build`, `solid_test` and `solid_snapshot` reference to it, with failing-first tests

## 5. HTTP surface

- [x] 5.1 Write failing API tests for `GET /api/entries?folder=`, `POST /api/sessions` with an entry path, `POST /api/projects` with a folder, `GET /api/screenshot?path=&revision=`, `GET /api/sessions/{id}/artifacts/{path}` and `GET /api/sessions/{id}/viewer/solid-widget.js`
- [x] 5.2 Implement those routes and remove the `{name}`-keyed project routes they replace
- [x] 5.3 Scope the hub stream to a folder: snapshot from `?folder=`, and hub events naming the entry path
- [x] 5.4 Write a failing test that an entry path escaping the working folder is refused before any filesystem access outside it

## 6. Hub browser

- [x] 6.1 Route the client on `/folders/<path>` and `/projects/<path>`, parsing multi-segment locations
- [x] 6.2 Render folder cards in the project grid, entering a folder on click, with the same card size as a project card
- [x] 6.3 Render the breadcrumb: the working folder, every folder between, and the one being listed, with ancestors as links and the current folder inert
- [x] 6.4 Create a project into the folder being listed, and hide creation while listing a multi-model project
- [x] 6.5 Subscribe the hub stream to the listed folder, and apply an event only when its entry belongs to that folder
- [x] 6.6 Point the workspace's artifact, viewer and screenshot URLs at the re-keyed routes

## 7. Runtime prompts and validation

- [x] 7.1 Name the session's model in the profile role prompts that talk about building, testing and committing the model
- [x] 7.2 Run the shop test suite and record the result
- [x] 7.3 Open the shop against `projects/`, and confirm in the browser: `sandbox` enters and lists its projects, `3DPrintedClocks` enters and lists both clocks, both clocks open at once, and the breadcrumb returns to the working folder
- [x] 7.4 Record the entry-path and model-session boundary in an ADR, promote it, and update `docs/architecture-overview.md` and `docs/adrs/README.md`
- [x] 7.5 Sync the baseline specs, archive the change, and commit the completed implementation record
