## MODIFIED Requirements

### Requirement: One answer about the bundle across framework channels

Every framework channel that needs the web viewer (the viewer report, static
export, documentation embedding, the development viewer, the web snapshot and
the films) SHALL resolve it through the one seam, `machinome.viewer`, at its
address `machinome.viewer.web`, and SHALL name the same remedy when it is
absent: installing the `viewer` extra. Documentation embedding SHALL continue
to resolve the bundle without loading the CAD runtime.

#### Scenario: Export and documentation embedding disagree about nothing

- **WHEN** the viewer is absent and an export and a documentation build each
  report it
- **THEN** both name the same remedy

#### Scenario: A documentation build stays free of the CAD runtime

- **WHEN** a documentation build completes an export that was made without
  viewer files
- **THEN** it copies the bundle the web viewer names without importing the
  framework's CAD runtime

### Requirement: The framework resolves the Machinome viewer

The `viewer` extra SHALL install `machinome-viewer`, the repository's
distribution whose Python package is `machinome.viewer.web`, the web provider
of the seam `machinome.viewer`, and the framework SHALL find it by importing
that address and nothing else: it SHALL read no entry point to find a viewer,
and the distribution SHALL declare none in the group `machinome.viewer`. The
framework SHALL serve, capture and embed through the provider's operations in
its own process and SHALL run no program of the viewer's. Absence and
compatibility errors SHALL name `pip install "machinome[viewer]"` as the
remedy. The viewer's console script `machinome-viewer describe|serve|capture`
and `python -m machinome.viewer.web` SHALL keep printing what they print.

#### Scenario: A host asks an installation for its viewer

- **WHEN** `machinome viewer` runs with `machinome-viewer` installed
- **THEN** it reports the installed bundle through the web viewer's provider,
  the same object `machinome-viewer describe` prints

#### Scenario: Interactive development lacks the viewer

- **WHEN** `machinome develop` runs without `machinome-viewer`
- **THEN** it fails naming `pip install "machinome[viewer]"`

#### Scenario: The framework runs the viewer at its address

- **WHEN** `machinome develop` serves or `machinome snapshot --viewer web`
  captures
- **THEN** the work is done by `machinome.viewer.web` in the command's own
  process, no `python -m machinome.viewer.web` process is run, and no module
  named `machinome_viewer` is imported

#### Scenario: No entry point is read

- **WHEN** the installed distributions' entry points are listed
- **THEN** none is in the group `machinome.viewer`, and every channel still
  finds the web viewer

## REMOVED Requirements

### Requirement: The framework finds the installed viewer through its entry point

**Reason**: The entry point existed so the framework could find a viewer it
did not import, across a licence boundary the one licence removed (ADR-068,
ADR-188). The viewer is the web provider of the seam at a known address since
change `viewer-seam` (ADR-194).
**Migration**: The framework imports `machinome.viewer.web` through
`machinome.viewer.viewer('web')`; a host reads `machinome viewer`'s report,
unchanged, instead of the entry point.

### Requirement: The framework uses the viewer only as a process

**Reason**: The process boundary served the same licence difference. The web
viewer serves in a thread its provider owns and captures in the command's
process (change `viewer-seam`, ADR-194).
**Migration**: None for a maker: `machinome develop` and `machinome snapshot
--viewer web` do what they did; `machinome-viewer serve|capture` keep working
for a host that runs them.
