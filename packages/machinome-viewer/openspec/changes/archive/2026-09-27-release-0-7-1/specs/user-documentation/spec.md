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
changing it SHALL say so in its changelog section.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the manual's home page
- **THEN** they can identify the project, find installation and operating
  instructions, and reach the framework manual without reading workflow records

#### Scenario: A maker reads which version they have
- **WHEN** a maker reads the home, installation or compatibility page
- **THEN** each names version 0.7.1, released with Machinome 0.7.1, and none
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
  Machinome 0.7.1, with API 27 and document versions 1 to 13 unchanged
