## MODIFIED Requirements

### Requirement: The films are drawn by the installed viewer

`machinome movie check`, `preview`, `render`, `build` and `live` SHALL give
the Node side the bundle of the browser viewer installed beside the framework,
the path the web viewer names when the seam `machinome.viewer` is asked for
it, as `machinome develop` finds it; the command SHALL take no option naming
a bundle and SHALL NOT read the project's declared viewer, since only the web
viewer draws a film. When no viewer is
installed, or the installed one reports no bundle, those verbs SHALL write one
line with the viewer's remedy and exit 1. `speech` and `review` SHALL run
without a viewer.

#### Scenario: No viewer installed

- **WHEN** `machinome-viewer` is not installed and a user runs `machinome
  movie check film.yaml`
- **THEN** standard error holds "Error: machinome movie check needs the
  browser viewer: " followed by the remedy naming `pip install
  "machinome[viewer]"`, and the command exits 1

#### Scenario: The installed viewer draws the film

- **WHEN** a user runs `machinome movie preview <project> <movie>` with the
  viewer installed
- **THEN** the Node side mounts the bundle the viewer's report names, and a
  film that needs a newer viewer API is refused naming the installed one and
  how to upgrade it
