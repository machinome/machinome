## MODIFIED Requirements

### Requirement: The viewer is an optional extra

The framework SHALL declare the `viewer` extra, installing the
`machinome-viewer` distribution, and the `web-snapshot` extra, installing
`machinome-viewer[snapshot]`. Each extra SHALL require at least the matching
viewer version the manual's release block states (`docs/conf.py`'s
`viewer_version`) and SHALL state no upper bound, and a test SHALL hold
`pyproject.toml`'s two requirements to that one statement. The framework's own
dependencies SHALL NOT include the viewer, and every framework operation that
does not open, embed or photograph through the browser viewer SHALL work in an
installation without it. Interactive development through `machinome develop`
SHALL require the viewer extra unless the caller explicitly selects the
`--no-web` watch loop.

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

#### Scenario: The extras require the matching viewer

- **WHEN** `pyproject.toml`'s `viewer` and `web-snapshot` extras are read
  beside `docs/conf.py`'s `viewer_version`
- **THEN** they are `machinome-viewer>=<viewer_version>` and
  `machinome-viewer[snapshot]>=<viewer_version>`, with no upper bound, and when
  either disagrees the release-records test fails naming that extra
