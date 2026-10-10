## ADDED Requirements

### Requirement: The manual states the 0.8.1 release

machinome-viewer 0.8.1 SHALL be stated as released with Machinome 0.8.1 on
10 October 2026 and numbered with it: the published 0.8.0 renumbered, with
no change to the widget, the server or the capture, declaring viewer API 29
and document versions 1 through 13. The changelog's first release section
SHALL be `0.8.1 — 10 October 2026` and say so; the manual's home note, the
installation and compatibility pages, the `describe` example, the README
and `context7.json` SHALL state 0.8.1, released with Machinome 0.8.1.

#### Scenario: A maker checks the 0.8.1 release they installed

- **WHEN** a maker runs `machinome-viewer describe`, reads the bundle banner
  and opens the manual's home page
- **THEN** each reports version 0.8.1 with viewer API 29 and document
  versions 1 through 13, and the home page says it was released on
  10 October 2026 together with Machinome 0.8.1

#### Scenario: A reader compares 0.8.1 with 0.8.0

- **WHEN** a reader reads the 0.8.1 changelog section
- **THEN** it says the viewer is the published 0.8.0 renumbered with
  Machinome 0.8.1, with API 29 and document versions 1 to 13 unchanged

## MODIFIED Requirements

### Requirement: Makers have a viewer manual

The manual SHALL explain that machinome-viewer is the independent browser viewer
for the Machinome framework, how to install and open it, inspect an assembly,
operate posed, running and clocked models, and capture or share a model. It SHALL
state the released version it documents and the framework release it matches,
install the package from the index through the framework's `viewer` extra, keep
the source build as the contributor's path, and link to the framework's modeling
documentation at the pages that manual currently has. Its pages SHALL contain
user guidance, not development workflow records, decision records or the names
of the projects that motivated a behaviour. Until a release is uploaded, its
record describes the current source, stating the viewer API and document
versions once from the package's own declarations. A source correction landed
after a release is published SHALL appear in an Unreleased changelog section
that names the viewer API and does not retroactively attribute it to that
published release. A release that renumbers a published source without
changing it SHALL say so in its changelog section. An earlier release's
section SHALL remain as released below the sections of later releases.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the manual's home page
- **THEN** they can identify the project, find installation and operating
  instructions, and reach the framework manual without reading workflow records

#### Scenario: A maker reads which version they have
- **WHEN** a maker reads the home, installation or compatibility page
- **THEN** each names version 0.8.1, released with Machinome 0.8.1, and none
  describes the package as unreleased

#### Scenario: A reader checks a post-release source correction
- **WHEN** the changelog records a source correction after a version is
  uploaded
- **THEN** its Unreleased section states the applicable viewer API and keeps
  the historical release sections unchanged

#### Scenario: A reader checks an unpublished release record
- **WHEN** the changelog and manual describe a release that is at released
  state but not yet uploaded
- **THEN** they state the current source's viewer API and document versions,
  with no Unreleased section above the release

#### Scenario: A reader compares 0.7.1 with 0.7.0
- **WHEN** a reader reads the 0.7.1 changelog section
- **THEN** it says the viewer is the published 0.7.0 renumbered with
  Machinome 0.7.1, with API 27 and document versions 1 to 13 unchanged, and
  it remains as released below the sections of later releases

### Requirement: The manual states the 0.8.0 release

machinome-viewer 0.8.0 SHALL be recorded as released with Machinome 0.8.0
on 5 October 2026 and numbered with it, declaring viewer API 29 and
document versions 1 through 13. The version SHALL live in
`pyproject.toml`, the package's `__version__`, the widget's `package.json`,
both `version` fields of its lock file and the built bundle's banner; the
API and the document versions SHALL live in the widget's `package.json`
alone. The reader-facing statements of the current release's facts — the
changelog's first release section, the manual's home note, the
installation and compatibility pages, the `describe` example, the README
and `context7.json` — SHALL agree with those declarations, each either
reading them through the manual's substitutions or compared with them by a
test. The 0.8.0 changelog section SHALL say what a host and a maker get in
it, name API 28 and API 29 where they arrived and say the document
versions do not move, and SHALL remain as released below the sections of
later releases. No Unreleased section SHALL stand above the latest
release's section, no reader-facing page SHALL describe the package as
unreleased, and no page SHALL call API 28 or API 29 unpublished. Every
reader-facing sentence about licensing SHALL name only the viewer's
AGPL-3.0-or-later grant and say the framework is licensed separately,
without naming the framework's licence.

#### Scenario: A maker checks the release they installed

- **WHEN** a maker runs `machinome-viewer describe`, reads the bundle banner
  and opens the manual's home page
- **THEN** each reports the latest release's version with viewer API 29
  and document versions 1 through 13, matching `pyproject.toml` and the
  widget's `package.json`, and the 0.8.0 changelog section still says it
  was released on 5 October 2026 together with Machinome 0.8.0

#### Scenario: A reader compares 0.8.0 with 0.7.1

- **WHEN** a reader reads the 0.8.0 changelog section
- **THEN** it says what a host and a maker gain over 0.7.1, which of it
  arrived at API 28 and which at API 29, that a bundle reporting API 27 has
  none of it, and that a 0.7 viewer reads a 0.8 export while this viewer
  reads every 0.7 export

#### Scenario: A reader looks for the licences

- **WHEN** a reader reads the licensing sentence of the README, the
  manual's home or sharing page, the changelog or `context7.json`
- **THEN** it names AGPL-3.0-or-later as the viewer's licence and says the
  framework is licensed separately, naming no other licence
