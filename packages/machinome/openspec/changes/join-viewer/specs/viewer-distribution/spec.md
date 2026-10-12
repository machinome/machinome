## MODIFIED Requirements

### Requirement: The framework resolves the Machinome viewer

The `viewer` extra SHALL install `machinome-viewer`, the repository's
distribution whose Python package is `machinome.viewer.web`, and the
framework SHALL locate it through the `machinome.viewer` entry point group.
Beyond that lookup, the framework SHALL use it only through
`python -m machinome.viewer.web describe|serve|capture` in the running
interpreter, a separate process. Absence and compatibility errors SHALL name
`pip install "machinome[viewer]"` as the remedy. The framework SHALL import no
viewer rendering, serving, or capture code.

#### Scenario: A host asks an installation for its viewer

- **WHEN** `machinome viewer` runs with `machinome-viewer` installed
- **THEN** it reports the installed bundle through the `machinome.viewer`
  entry point

#### Scenario: Interactive development lacks the viewer

- **WHEN** `machinome develop` runs without `machinome-viewer`
- **THEN** it fails naming `pip install "machinome[viewer]"`

#### Scenario: The framework runs the viewer at its address

- **WHEN** `machinome develop` starts the viewer's server or `machinome
  snapshot --renderer web` its capture
- **THEN** the process runs `python -m machinome.viewer.web` with the
  interpreter running the framework, and no module named `machinome_viewer`
  is imported
