## MODIFIED Requirements

### Requirement: Viewer command

The system SHALL provide `machinome viewer`, a command that takes no node path.
With no verb it SHALL print one JSON object on standard output with the
absolute path of the installed web viewer's bundle, the absolute path of its
standalone export page, its integer API version, the document versions it reads
and the viewer package version, the report the web viewer gives through the
seam, and SHALL take no option. When the viewer package is not installed it
SHALL print nothing on standard output, name `pip install "machinome[viewer]"`
on standard error, and exit 1.

The command SHALL take the viewer's verbs, each dispatching through the seam
`machinome.viewer` to the viewer named by its `--viewer <name>` option, the web
viewer when none is named, and reading no project manifest, under the
`viewer-seam` capability:

- `machinome viewer describe` SHALL print the chosen viewer's report, for the
  web viewer the same bytes `machinome viewer` prints;
- `machinome viewer serve --build-dir DIR [--port N]` SHALL ask the chosen
  viewer to serve the published build directory `DIR`, on `N`, else
  `MACHINOME_PORT`, else 8000, and SHALL run until interrupted: an interrupt
  from the terminal stops the session and exits 0, and a termination signal
  stops it and ends the process by that signal; a server that cannot listen
  SHALL be one `Error:` line on standard error and exit 1; without
  `--build-dir` the command SHALL exit 2;
- `machinome viewer capture STAGING -o PNG [--imgsize WxH] [--time T] [--view
  EX,EY,EZ,TX,TY,TZ] [--up X,Y,Z] [--fov DEGREES]` SHALL ask the chosen viewer
  to photograph the published document staged in the directory `STAGING` into
  a PNG with a transparent background, the image size defaulting to
  `1920x1080` and the time to 0; the eye and target, the up direction and the
  field of view SHALL reach the viewer as given, each one not given being left
  to the viewer; a time outside [0, 1] SHALL exit 2 before the viewer is asked,
  and a capture the viewer cannot make SHALL be one `Error:` line, exit 1, and
  no image; the staging directory SHALL be left in place.

A verb SHALL be refused by name when the chosen viewer cannot perform it:
`describe` needs a viewer that embeds, `serve` one that serves, and `capture`
one that captures and reads published documents. The refusal SHALL name the
verb, what it needs, the viewer and the viewers that can, print nothing on
standard output, and exit 1; no viewer SHALL be used in place of the one
chosen. A name no viewer answers, an absent viewer and a viewer of another
contract SHALL be refused as the seam refuses them, exit 1.

#### Scenario: Viewer command appears in CLI help

- **WHEN** a user runs `machinome -h`
- **THEN** the command list includes `viewer`

#### Scenario: A consumer reads the installed viewer

- **WHEN** a program runs `machinome viewer` against an installation with
  `machinome-viewer`
- **THEN** it parses one JSON object carrying the bundle path, export page,
  API version and package version, and the command exits 0

#### Scenario: No bundle installed

- **WHEN** a user runs `machinome viewer` in an installation without
  `machinome-viewer`
- **THEN** the command exits 1 and standard error names the extra

#### Scenario: The report is the one the viewer's own command prints

- **WHEN** `machinome viewer`, `machinome viewer describe` and `python -m
  machinome.viewer.web describe` run in one installation
- **THEN** their standard outputs are identical

#### Scenario: The verbs are listed

- **WHEN** a user runs `machinome viewer -h`
- **THEN** the help lists `describe`, `serve` and `capture`, the command exits
  0, and no viewer is imported

#### Scenario: A staged document is photographed

- **WHEN** a user runs `machinome viewer capture STAGING -o still.png
  --view=-80,60,40,0,0,0` on a directory holding a published document and its
  models
- **THEN** the web viewer writes `still.png` from that eye towards that
  target, with its own up direction and field of view, the image the web
  viewer's capture writes for those options, and `STAGING` still exists

#### Scenario: A time outside the cycle

- **WHEN** a user runs `machinome viewer capture STAGING -o still.png --time 2`
- **THEN** the command exits 2 with the line `Error: --time must be between 0.0
  and 1.0, got 2.0` and writes no image

#### Scenario: A verb the viewer cannot perform

- **WHEN** a user runs `machinome viewer serve --viewer openscad --build-dir
  _build`
- **THEN** the command exits 1 naming `machinome viewer serve`, serving, the
  `openscad` viewer and `web`, prints nothing on standard output, and listens
  on no port

#### Scenario: A viewer that reads no document is not asked to photograph one

- **WHEN** a user runs `machinome viewer capture --viewer openscad STAGING -o
  still.png`
- **THEN** the command exits 1 naming `machinome viewer capture`, a published
  document, the `openscad` viewer and `web`, and writes no image

#### Scenario: Serving until interrupted

- **WHEN** a user runs `machinome viewer serve --build-dir _build --port 8791`
  and interrupts it from the terminal once its page has been served
- **THEN** the page, `/_viewer` and `/build/viewer.json` were answered on that
  port, the reload socket greeted with `reload`, and the command exits 0 with
  nothing left listening

#### Scenario: The port is taken

- **WHEN** a user runs `machinome viewer serve --build-dir _build --port 8791`
  while another program listens on that port
- **THEN** the command exits 1 with an `Error:` line, and does not wait

#### Scenario: The verbs read no project

- **WHEN** a user runs `machinome viewer describe` inside a project whose
  manifest declares `viewer = "openscad"` under `[tool.machinome]`
- **THEN** the web viewer's report is printed and the command exits 0
