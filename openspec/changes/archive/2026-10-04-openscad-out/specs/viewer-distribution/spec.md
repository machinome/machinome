## MODIFIED Requirements

### Requirement: The viewer is an optional extra

The framework SHALL declare the `viewer` extra, installing the
`machinome-viewer` distribution, and the `web-snapshot` extra, installing
`machinome-viewer[snapshot]`. The framework's own dependencies SHALL NOT
include the viewer, and every framework operation that does not open, embed
or photograph through the browser viewer SHALL work in an installation
without it. Interactive development through `machinome develop` SHALL require the
viewer extra unless the caller explicitly selects the `--no-web` watch loop.

#### Scenario: A plain installation retains non-viewer operations

- **WHEN** `pip install machinome` runs without the extra, with the extras
  the project's parts need
- **THEN** building, testing, exporting without the widget, snapshotting
  through OpenSCAD with the `openscad` extra, and developing with `--no-web`
  work, while ordinary `machinome develop` fails naming the viewer extra

#### Scenario: The extra brings the interactive viewer

- **WHEN** `pip install "machinome[viewer]"` runs
- **THEN** `machinome viewer` reports the installed bundle and `machinome develop`
  opens the browser viewer by default
