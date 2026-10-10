## 1. Red Identity Contract

- [x] 1.1 Add failing installed-metadata tests for distribution `machinome`, version 0.7.0, repository URL and `viewer`, `mechanics`, `studio` extras.
- [x] 1.2 Add failing import and CLI tests for `machinome`, absence of shipped `solid_node`/`solid` aliases, and `MACHINOME_*` runtime names.
- [x] 1.3 Add failing project-manifest tests for `[tool.machinome]` and actionable rejection of `[tool.solid-node]`.
- [x] 1.4 Add failing export/viewer tests for `machinome-export`, `machinome.viewer`, `machinome-viewer` commands and remedies.

## 2. Source And Runtime Rename

- [x] 2.1 Rename the `solid_node/` source package to `machinome/` and update internal imports, dynamic module names, resources and package discovery.
- [x] 2.2 Rename the console entry point, subprocess launches, command help and runtime environment/configuration from solid-node names to Machinome names.
- [x] 2.3 Rename project manifest parsing/templates and provide explicit former-table migration errors.
- [x] 2.4 Rename emitted format, Sphinx directive/resources and viewer lookup/process integration while preserving numerical document versions.
- [x] 2.5 Add the three optional-product extras without making them default runtime dependencies.

## 3. Tests, Fixtures And Tools

- [x] 3.1 Rename current test imports, fixtures, example projects, scripts, Make/tox/CI configuration and source-path assertions.
- [x] 3.2 Regenerate committed current exports with `machinome-export` and retain explicit legacy-format fixtures for viewer compatibility.
- [x] 3.3 Update distribution checks to inspect and execute wheel and sdist installs under the Machinome names.
- [x] 3.4 Add a tracked-reference audit that classifies every remaining former name as historical evidence or intentional compatibility input.

## 4. Current Records And Release Narrative

- [x] 4.1 Update README, Sphinx pages, API reference, examples, status, roadmap and contributor guidance to the Machinome surface.
- [x] 4.2 Add the 0.7.0 changelog entry, release note, term definition, reason for the rename and complete 0.6 migration map.
- [x] 4.3 Add the accepted rename ADR, update the ADR index and rewrite current architecture synthesis to Machinome while preserving historical ADR bodies.
- [x] 4.4 Update current baseline spec terminology and links consistently without rewriting archived changes or earlier release records.

## 5. Validation And Completion

- [x] 5.1 Run focused red/green identity, manifest, document and viewer-integration tests.
- [x] 5.2 Run the full framework suite, lint, documentation build and source reference audit.
- [x] 5.3 Build wheel and sdist, install each outside the repository, and smoke import, CLI, build, extras metadata and package contents.
- [x] 5.4 Run paired validation against the renamed viewer, mechanics and studio callers.
- [x] 5.5 Sync specs, archive the change, run final validation and leave the branch exactly two commits ahead of its base.
