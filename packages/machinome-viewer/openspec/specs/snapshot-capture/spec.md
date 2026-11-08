# Snapshot Capture Specification

## Purpose

Transparent PNG rendering of a staged document through the viewer in a
headless browser: what `machinome snapshot --viewer web` has the package
do, in the command's own process, once the package has staged the
photographed node in a directory of its own (`stage.py`, change
`viewer-seam`), and what `machinome viewer capture` does with a directory it
is handed (change `viewer-command`). Migrated from the
capture half of machinome's `web-snapshot` baseline when the viewer became
this package; the staging contract is new.

Code: `machinome/viewer/web/capture.py`, `machinome/viewer/web/stage.py`,
`machinome/viewer/web/__init__.py` (`present`, `capture`, `withdraw`); the
verb is the framework's `machinome/manager/viewer.py`.
## Requirements
### Requirement: A staged document is photographed with a transparent background

The system SHALL photograph, for `machinome viewer capture STAGING -o PNG`, where
`STAGING` is a directory holding a `viewer.json` document beside the model
files it names. It SHALL copy the installed bundle and write a mount page
beside the document, serve the directory over a loopback HTTP server, display
the page in headless Chromium and capture the viewer's canvas into `PNG` with
a real alpha channel: every pixel not covered by the model fully transparent
and the model pixels opaque. `--imgsize WxH` (default `1920x1080`) sets the
image size and `--time` (0.0 to 1.0, default 0.0) the animation instant;
`--time` outside the cycle SHALL be refused before any browser starts.

A staged document carrying a mechanical `program` object SHALL be
photographed at its REST STATE: no step of the run SHALL be taken, and the
program's published clock name SHALL resolve to zero, the instant the rest
state is defined at. A non-zero `--time` on such a document SHALL be
refused by name before any browser starts: a running document publishes no
animation cycle, and honouring an animation instant on one would
photograph the rest state while claiming another. A still of a state the
machine reached is a different picture and is not offered here.

A staged CLOCKED document SHALL be photographed at its INITIAL BANK --
every declared driver and state at its default, and the clock, where it
declares one, at zero -- with no request made. Such a document publishes an
ordinary animation cycle, so a non-zero `--time` SHALL be HONOURED on it
and SHALL NOT be refused: the bank stands while `$t` sweeps, which is the
instant the document itself describes.

A staged document whose parts carry markings SHALL be photographed WITH them:
the marking artifacts are staged beside the models the document names, and the
photograph shows each marking in its own colour on the part that carries it,
exactly as the viewer draws it on screen. A staging that names a marking
artifact it does not hold SHALL refuse to mount and report that failure, rather
than producing a picture with a marking silently absent.

#### Scenario: A host composites a model onto its own surface

- **WHEN** a framework renders a staged document with the capture
- **THEN** the PNG's background pixels are fully transparent and the model
  pixels are opaque, so a host may composite it over any surface without
  removing a background

#### Scenario: A staging without a document

- **WHEN** the capture is asked for a directory holding no `viewer.json`
- **THEN** it fails naming the missing document and starts no browser

#### Scenario: A running document is photographed at rest

- **WHEN** the capture is asked for a staged document carrying a program
- **THEN** the picture shows every part where the program's published rest
  values put it, and no step of the run was taken to produce it

#### Scenario: An animation instant means nothing to a running document

- **WHEN** the capture is asked for a staged document carrying a program
  with a non-zero `--time`
- **THEN** it fails naming the option and saying a running document has no
  animation instant, starts no browser, and writes no image

#### Scenario: A marked model is photographed with its markings

- **WHEN** the capture is asked for a staged document whose part carries a
  marking, staged beside the part's own model
- **THEN** the photograph shows the marking's colour where the marking is and
  the part's where it is not, and the same staging with its markings removed
  produces the picture without it

#### Scenario: A clocked document is photographed at its initial bank

- **WHEN** the capture is asked for a staged document declaring version 8
- **THEN** the picture shows every part where its drivers' and states'
  declared defaults put it, and no request was made to produce it

#### Scenario: An animation instant means something to a clocked document

- **WHEN** the capture is asked for a staged clocked document with a
  non-zero `--time`
- **THEN** it photographs that animation instant with the bank standing,
  rather than refusing the option

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
SHALL name both the `machinome-viewer[snapshot]` extra and the
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

### Requirement: A photograph carries no full-screen control

A capture SHALL NOT photograph the viewer's full-screen control, whatever
the staged document and whether or not the headless browser permits full
screen. The pixels the transparent background promises SHALL stay
transparent where the control would otherwise stand.

#### Scenario: A model without a timeline is photographed

- **WHEN** a staged posed document that does not read `$t` is captured
- **THEN** the capture's page shows no full-screen control and the
  photograph's bottom-right corner is transparent

### Requirement: Eligible stills are captured without a continuing viewer frame loop

For a valid staged posed document without instructions, and for a valid staged clocked document, the capture SHALL use the viewer's existing on-demand rendering mode with external animation, autoplay disabled, no driver controls and no part controls. It SHALL photograph the requested animation instant and the same declared initial or standing pose required by the existing snapshot contract, without issuing a simulation request or starting an animation-frame render loop.

After mount and final viewport/layout settlement, the capture SHALL explicitly draw the viewer's current public view before announcing that the page is ready to photograph. That redraw SHALL preserve camera, target, up, field of view, bank and requested animation instant. The resulting PNG SHALL retain the existing model, markings, transparency and requested dimensions.

A staged running program or a posed document with instructions SHALL retain the existing continuous-mode capture path and its existing rest-state, instant and error behavior. Mode selection SHALL NOT strip program or instruction data, alter model geometry, hide model parts, weaken document validation, or change the caller's supplied option object. Existing malformed-document and unsupported-instant refusals SHALL remain refusals.

#### Scenario: A posed model is photographed at an explicit instant

- **WHEN** a valid posed document without instructions is captured at a requested animation instant
- **THEN** the capture draws that instant without a continuing viewer render loop and produces the same model content, markings, camera and alpha behavior required by the existing contract

#### Scenario: A clocked model is photographed at its initial bank

- **WHEN** a valid clocked document is captured, including one declaring instructions, at a permitted animation instant
- **THEN** the capture draws on demand with the bank at its declared initial values, makes no request, and honors the requested animation instant

#### Scenario: Layout settles after the initial mount

- **WHEN** an eligible capture's viewport settles after the viewer's initial draw
- **THEN** readiness follows an explicit draw of the current public view and the photograph contains the correctly framed model at the requested dimensions rather than a cleared or stale canvas

#### Scenario: A running program keeps its supported capture path

- **WHEN** a staged running program is captured at time zero
- **THEN** capture uses the existing continuous-mode path and photographs the rest state without advancing the run

#### Scenario: A posed document declares instructions

- **WHEN** a valid posed document with instructions is captured
- **THEN** capture uses the existing supported continuous-mode path and retains the instruction data without playing an instruction

#### Scenario: Mode selection does not repair a malformed document

- **WHEN** a malformed staged document or an unsupported running-program instant is supplied
- **THEN** capture preserves the existing refusal, starts no simulation request, and does not change document data or caller options to obtain an image
