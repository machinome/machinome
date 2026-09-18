## ADDED Requirements

### Requirement: The framework resolves the Machinome viewer

The `viewer` extra SHALL install `machinome-viewer`, and the framework SHALL
locate it through the `machinome.viewer` entry point group. Beyond that lookup,
the framework SHALL use it only through
`python -m machinome_viewer describe|serve|capture` in the running
interpreter. Absence and compatibility errors SHALL name
`pip install "machinome[viewer]"` as the remedy. The framework SHALL import no
viewer rendering, serving, or capture code.

#### Scenario: A host asks an installation for its viewer

- **WHEN** `machinome viewer` runs with `machinome-viewer` installed
- **THEN** it reports the installed bundle through the `machinome.viewer`
  entry point

#### Scenario: Interactive development lacks the viewer

- **WHEN** `machinome develop` runs without `machinome-viewer`
- **THEN** it fails naming `pip install "machinome[viewer]"`
