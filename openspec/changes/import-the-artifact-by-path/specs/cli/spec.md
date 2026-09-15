## ADDED Requirements

### Requirement: A snapshot never silently drops geometry OpenSCAD could not open

`solid snapshot --renderer openscad` SHALL fail when OpenSCAD reports that it
could not open a file the design imports: the command SHALL exit non-zero
with an error naming the file OpenSCAD could not open and the `.scad` it was
rendering, and SHALL write no image. OpenSCAD reports such a file as a
warning and exits zero, so a command that only consults the exit status
reports success over a picture that is missing a part — the failure the
maker needs to see is the missing geometry, not the process status.

Every other warning, error or deprecation OpenSCAD reports on either stream
SHALL reach the operator's log at a level a normal run shows, rather than
only the debug stream, so a warning the framework does not classify is still
visible to whoever is looking at the image. OpenSCAD's progress output stays
on the debug stream, as today.

This SHALL NOT change `--renderer web`, which renders from the published
document and opens no `.scad`.

#### Scenario: An unopenable import stops the image

- **WHEN** `solid snapshot` renders a `.scad` whose `import()` names a file
  OpenSCAD cannot open
- **THEN** the command exits non-zero naming that file and the `.scad`, and
  no image file is written

#### Scenario: A clean render still succeeds

- **WHEN** `solid snapshot` renders a design whose imports all resolve
- **THEN** the image is written and the command reports success, exactly as
  before

#### Scenario: Other OpenSCAD output is visible

- **WHEN** OpenSCAD reports a warning that is not an unopenable import
- **THEN** the run logs what OpenSCAD said and the image is still written
