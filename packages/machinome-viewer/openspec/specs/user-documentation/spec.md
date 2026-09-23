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

### Requirement: The manual distinguishes profile-contact source capability from the recorded baseline

After the viewer implements document version 13 and API 26, its owning compatibility and running reference surfaces SHALL describe the pointwise convex-profile predicate as a numeric value inside an ordinary running Bound, not as continuous collision certification or a new host operation. The recorded 0.7.0/API-26/document-1–13 baseline SHALL remain accurate. Its recorded release section SHALL name API 26 and document version 13. A source-derived API/document substitution SHALL NOT silently rewrite a sentence about that 0.7.0 baseline; the manual SHALL distinguish its recorded facts from current-source `describe` capability without asserting a push or upload not established by repository evidence. Reader-facing pages SHALL not name the originating project or workspace paths. The reference SHALL state that a producer-supplied finite profile table is required, that the predicate treats touching as contact, and that malformed or numerically unrepresentable placements refuse rather than imply clearance.

#### Scenario: A reader checks the recorded profile-contact capability
- **WHEN** a reader checks compatibility and running-reference pages built from source with API 27
- **THEN** the pages explain the version-13 pointwise predicate and its numeric-Bound scope, while the recorded 0.7.0 release remains API 26/document 1–13 and current-source API 27 is not presented as a new publication

#### Scenario: A reader asks whether one evaluation proves a full motion safe
- **WHEN** a reader reads the running reference's profile-contact description
- **THEN** it does not claim continuous swept contact, installed-print completeness, collision volume, or a clearance epsilon

### Requirement: The manual distinguishes post-release selected-joint handles from the recorded release

The viewer's owning compatibility and host-reference surfaces SHALL identify
API 27 as current-source capability for separately named Turn handles on one
part when the selected joints differ, while the 0.7.0 release record remains
API 26 and document versions 1–13 remain unchanged. The changelog SHALL
record the post-release correction in an Unreleased section, and source
examples of `describe` SHALL match the current source. Reader-facing pages
SHALL not name the originating project or imply a push or upload.

#### Scenario: A host checks which viewer can operate a two-joint part

- **WHEN** a host reads compatibility or the controls reference after this
  source change
- **THEN** it learns that API 27 presents one named handle per selected
  joint on a shared part, API 26 can refuse that valid table, and document
  version 13 alone does not imply the new gesture capability

#### Scenario: A reader checks the recorded release

- **WHEN** a reader checks the 0.7.0 release note and manual home
- **THEN** they still see the recorded API 26 release, not a retroactive
  API 27 publication claim
