# user-documentation Specification

## Purpose

Provide makers and embedding hosts with a complete, accurate, reproducible
user manual for the independent Machinome browser viewer, separate from its
development workflow records.
## Requirements
### Requirement: Makers have a viewer manual

The manual SHALL explain that machinome-viewer is the independent browser viewer
for the Machinome framework, how to install and open it, inspect an assembly,
operate posed, running and clocked models, and capture or share a model. It SHALL
state the released version it documents and the framework release it matches,
install the package from the index through the framework's `viewer` extra, keep
the source build as the contributor's path, and link to the framework's modeling
documentation at the pages that manual currently has. Its pages SHALL contain
user guidance, not development workflow records, decision records or the names
of the projects that motivated a behaviour. Post-release source corrections
SHALL appear in an Unreleased changelog section that names the viewer API and
does not retroactively attribute them to the last published release.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the manual's home page
- **THEN** they can identify the project, find installation and operating
  instructions, and reach the framework manual without reading workflow records

#### Scenario: A maker reads which version they have
- **WHEN** a maker reads the home, installation or compatibility page
- **THEN** each names version 0.7.0, released with Machinome 0.7.0, and none
  describes the package as unreleased

#### Scenario: A reader checks a post-release source correction
- **WHEN** the changelog records a source correction after version 0.7.0
- **THEN** its Unreleased section states the applicable viewer API and keeps
  the historical 0.7.0 release section unchanged

### Requirement: Hosts have a complete public interface reference

The manual SHALL document every public browser mount, its options and returned
handle members, including navigation, drivers, instructions, running and clocked
execution, update and disposal behavior. It SHALL explain units, errors,
compatibility, and all supported command-line operations. Runnable embedding
examples SHALL use the package's own bundle and documents.

#### Scenario: A developer embeds the viewer
- **WHEN** a developer follows the embedding example and looks up a handle member
- **THEN** the example renders a model and the reference states how to call the
  member, its result, and relevant restrictions

### Requirement: The manual is reproducible and reviewable

The repository SHALL provide a Sphinx site using the framework's Read the Docs
theme, with navigation, search, mobile-readable pages, a working interactive
example, and reproducible local and Read the Docs configuration. The site SHALL
build without the framework or CAD backends and report broken documentation as
build failures. Source distributions SHALL carry the documentation sources.

#### Scenario: The documentation is built from a clean checkout
- **WHEN** the documented build prerequisites and commands are followed
- **THEN** a warning-free HTML manual is produced, including its local interactive
  assets, and can be served for review

#### Scenario: A reader uses a narrow screen
- **WHEN** the manual is opened on a mobile-width viewport
- **THEN** its navigation, text and reference content remain usable without
  page-wide horizontal overflow
