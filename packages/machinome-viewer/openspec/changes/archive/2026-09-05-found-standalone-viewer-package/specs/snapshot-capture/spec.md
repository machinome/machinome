# Snapshot Capture

## ADDED Requirements


### Requirement: A staged document is photographed with a transparent background

The system SHALL provide `solid-node-viewer capture STAGING -o PNG`, where
`STAGING` is a directory holding a `viewer.json` document beside the model
files it names. It SHALL copy the installed bundle and write a mount page
beside the document, serve the directory over a loopback HTTP server, display
the page in headless Chromium and capture the viewer's canvas into `PNG` with
a real alpha channel: every pixel not covered by the model fully transparent
and the model pixels opaque. `--imgsize WxH` (default `1920x1080`) sets the
image size and `--time` (0.0 to 1.0, default 0.0) the animation instant;
`--time` outside the cycle SHALL be refused before any browser starts.

#### Scenario: A host composites a model onto its own surface

- **WHEN** a framework renders a staged document with the capture
- **THEN** the PNG's background pixels are fully transparent and the model
  pixels are opaque, so a host may composite it over any surface without
  removing a background

#### Scenario: A staging without a document

- **WHEN** the capture is asked for a directory holding no `viewer.json`
- **THEN** it fails naming the missing document and starts no browser

### Requirement: A requested camera is honoured, never approximated

The capture SHALL accept `--view ex,ey,ez,tx,ty,tz` (eye and target),
`--up x,y,z` and `--fov DEGREES`, hand them to the viewer's mount options
verbatim, and present the model from that viewpoint at that field of view.
Absent all three, the viewer SHALL frame the whole model itself. A malformed
camera option SHALL be refused by the command line rather than ignored.

#### Scenario: A framework reproduces another renderer's framing

- **WHEN** the capture is given the eye, target, up direction and field of
  view another renderer used
- **THEN** the model is seen from that viewpoint, rolled to that up
  direction, and framed at that field of view

#### Scenario: No camera requested

- **WHEN** no camera option is given
- **THEN** the whole model is framed automatically

### Requirement: What cannot run is named, and nothing is substituted

When the capture cannot run, the command SHALL exit non-zero with an error
identifying what is missing and SHALL write no image. A missing Playwright
SHALL name both the `solid-node-viewer[snapshot]` extra and the
`playwright install chromium` step; a missing browser SHALL name the install
step; a missing bundle SHALL give the same remedy the viewer's lookup gives;
a process running as root SHALL be refused because Chromium cannot be
sandboxed there; a viewer that fails to mount SHALL report the page's error.

#### Scenario: The browser is unavailable

- **WHEN** Playwright or its Chromium is not installed
- **THEN** the command fails naming the package to install and the browser
  download step, and writes no image

#### Scenario: The viewer bundle is unavailable

- **WHEN** the installation has no built bundle
- **THEN** the command fails with the lookup's remedy, and writes no image

#### Scenario: The capture is run by the superuser

- **WHEN** the capture is requested by a process running as root
- **THEN** the command fails explaining that the browser cannot be sandboxed
  as root, and writes no image
