## ADDED Requirements

### Requirement: The distribution carries one Machinome viewer identity

The distribution SHALL be named `machinome-viewer`, expose the Python package
`machinome_viewer`, register `machinome.viewer`, and provide
`machinome-viewer describe|serve|capture` plus equivalent
`python -m machinome_viewer` execution. Its source repository SHALL be
`github.com/machinome/machinome-viewer`. The built bundle, standalone page,
source banner, package metadata, diagnostics and remedies SHALL use Machinome
names. It SHALL NOT install solid-node-named Python packages, entry points or
commands.

#### Scenario: The framework resolves the viewer

- **WHEN** Machinome loads the `machinome.viewer` entry point
- **THEN** it receives the installed Machinome bundle description without
  importing rendering, serving, or capture code

#### Scenario: A program asks the command line

- **WHEN** it runs `machinome-viewer describe`
- **THEN** standard output contains the same JSON mapping as the entry point

#### Scenario: A source recipient follows the bundle banner

- **WHEN** a conveyed bundle's source notice is read
- **THEN** it names the AGPL licence, package/API versions, and the
  `machinome/machinome-viewer` repository

### Requirement: The viewer remains an independent process

Machinome SHALL reach the viewer only through `machinome.viewer` lookup and
the `machinome-viewer` process commands. The viewer distribution SHALL NOT
depend on or import the `machinome` Python package.

#### Scenario: The two packages install together

- **WHEN** `pip install "machinome[viewer]"` installs both distributions
- **THEN** each package remains importable without importing the other and all
  serving or capture work crosses the process boundary
