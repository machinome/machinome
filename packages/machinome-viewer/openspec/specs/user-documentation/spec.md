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
of the projects that motivated a behaviour. Until a release is uploaded, its
record describes the current source, stating the viewer API and document
versions once from the package's own declarations. A source correction landed
after a release is published SHALL appear in an Unreleased changelog section
that names the viewer API and does not retroactively attribute it to that
published release.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the manual's home page
- **THEN** they can identify the project, find installation and operating
  instructions, and reach the framework manual without reading workflow records

#### Scenario: A maker reads which version they have
- **WHEN** a maker reads the home, installation or compatibility page
- **THEN** each names version 0.7.0, released with Machinome 0.7.0, and none
  describes the package as unreleased

#### Scenario: A reader checks a post-release source correction
- **WHEN** the changelog records a source correction after version 0.7.0 is
  uploaded
- **THEN** its Unreleased section states the applicable viewer API and keeps
  the historical 0.7.0 release section unchanged

#### Scenario: A reader checks an unpublished release record
- **WHEN** the changelog and manual describe a release that is at released
  state but not yet uploaded
- **THEN** they state the current source's viewer API and document versions,
  with no Unreleased section above the release

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

### Requirement: The manual states profile contact as part of the release

The viewer's owning compatibility and running reference surfaces SHALL describe the pointwise convex-profile predicate of document version 13 as a numeric value inside an ordinary running Bound, not as continuous collision certification or a new host operation. The 0.7.0 record SHALL state the release's viewer API and document versions 1–13 once, from the package's declarations, and SHALL name API 26 as the API at which version-13 profile contact arrived. Reader-facing pages SHALL not name the originating project or workspace paths, and SHALL not assert a push or upload not established by repository evidence. The reference SHALL state that a producer-supplied finite profile table is required, that the predicate treats touching as contact, and that malformed or numerically unrepresentable placements refuse rather than imply clearance.

#### Scenario: A reader checks the release's profile-contact capability
- **WHEN** a reader checks the compatibility and running-reference pages
- **THEN** the pages explain the version-13 pointwise predicate and its numeric-Bound scope, and the 0.7.0 record's API and document versions match `describe`

#### Scenario: A reader asks whether one evaluation proves a full motion safe
- **WHEN** a reader reads the running reference's profile-contact description
- **THEN** it does not claim continuous swept contact, installed-print completeness, collision volume, or a clearance epsilon

### Requirement: The manual states selected-joint handles as part of the 0.7.0 release

The viewer's owning compatibility and host-reference surfaces SHALL identify
API 27, the 0.7.0 release, as the API that presents separately named Turn
handles on one part when the selected joints differ, with document versions
1–13 unchanged. The changelog SHALL record the capability in the 0.7.0
section, and examples of `describe` SHALL match the package's declarations.
Reader-facing pages SHALL not name the originating project or imply a push or
upload.

#### Scenario: A host checks which viewer can operate a two-joint part

- **WHEN** a host reads compatibility or the controls reference
- **THEN** it learns that API 27 presents one named handle per selected
  joint on a shared part, API 26 refuses that valid table at load, and
  document version 13 alone does not imply the gesture capability

#### Scenario: A reader checks the release record

- **WHEN** a reader checks the 0.7.0 changelog section and the manual home
- **THEN** they see viewer API 27 and document versions 1–13, with no
  Unreleased section above the release
