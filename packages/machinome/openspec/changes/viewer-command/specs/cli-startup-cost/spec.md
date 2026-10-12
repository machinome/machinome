## MODIFIED Requirements

### Requirement: The viewer command loads no geometry stack

The system SHALL answer `machinome viewer` and `machinome viewer describe` from
the web viewer's report, asked through the seam `machinome.viewer`, which
imports the provider `machinome.viewer.web` and the modules its report reads
and nothing else. The invocation SHALL NOT import `cadquery`, `trimesh`,
`solid2`, or any node module, because none of them contributes to the bundle
path or its API version; and it SHALL NOT import the viewer's server, its
capture, its staging, a web framework or a browser driver, because the report
answers without them. The help of `machinome viewer` and of each of its verbs
SHALL import no viewer.

#### Scenario: Reporting the bundle imports no CAD library

- **WHEN** `machinome viewer` runs against an installation with `machinome-viewer`
- **THEN** it prints the same single JSON object with the bundle path, export
  page, integer API version and package version, exits 0, and `cadquery` and
  `trimesh` are absent from the process's imported modules

#### Scenario: Reporting the bundle runs no viewer code

- **WHEN** `machinome viewer` or `machinome viewer describe` runs against an
  installation with `machinome-viewer`
- **THEN** the viewer's server, capture and staging modules, `fastapi`,
  `uvicorn` and `playwright` are absent from the process's imported modules

#### Scenario: The missing-bundle path is unchanged

- **WHEN** `machinome viewer` runs in an installation without `machinome-viewer`
- **THEN** it prints nothing on standard output, names the extra on standard
  error, and exits 1

#### Scenario: A command's help imports no viewer

- **WHEN** `machinome -h`, `machinome snapshot -h`, `machinome develop -h`,
  `machinome viewer -h` or `machinome viewer capture -h` runs
- **THEN** neither `machinome.viewer.web` nor `machinome.viewer.openscad` is
  among the process's imported modules
