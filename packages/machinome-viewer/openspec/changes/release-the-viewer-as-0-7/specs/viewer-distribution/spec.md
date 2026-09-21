## MODIFIED Requirements

### Requirement: Installed viewer support includes retained time drives

The shipped bundle and package description SHALL consistently report viewer API
23 and supported document versions 1 through 10 after retained time-drive
execution is implemented and verified. The package, its widget and the bundle
banner SHALL all carry version 0.7.0, the version released with Machinome
0.7.0; the version number identifies the distribution and does not declare a
capability, which `apiVersion` and `documentVersions` alone declare.

API 23 supersedes earlier numeric capability declarations, including "A
play-capable distribution advertises its capability", without changing their
single-source declaration, bundle-currency or legacy-compatibility guarantees.

#### Scenario: A producer discovers matching browser support

- **WHEN** a producer asks the installed viewer for its supported versions
- **THEN** it receives API 23 and v1–10 support matching the actual bundle,
  and its version-10 Astrarium document can load and run

#### Scenario: The release pair is legible

- **WHEN** a maker runs `machinome-viewer describe` or reads the bundle banner
- **THEN** both report version 0.7.0 beside API 23 and document versions 1
  through 10, matching `pyproject.toml` and the widget's `package.json`
