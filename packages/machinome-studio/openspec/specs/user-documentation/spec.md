# user-documentation Specification

## Purpose

Give makers a manual for the studio, organised by what they are trying to
do, whose facts are derived from the package or pinned to it by tests,
whose publication state is stated once, and whose pages carry no
development record, project name or workspace path.
## Requirements
### Requirement: Makers have a studio manual

The repository SHALL carry a manual under `docs/`, organised by what a
maker is trying to do: install the studio and open the hub; open, create and
close a project from the hub; work in a project's conversation, Model, Code,
Agents and Build areas; understand the shipped profiles, their agents and
what an agent may do; configure a project's runtime; and diagnose a project
that will not start or open. It SHALL carry a reference for the launcher
commands and their options, for the `[tool.machinome-studio]` table, and for
what each shipped profile declares, and a status page. It SHALL state the
version it documents from the package's own declaration and the framework
version the studio runs against. The manual SHALL describe the interface the
maker meets and SHALL send the reader to the framework's and the viewer's
manuals for what those own, at pages that exist in them, without restating
them.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the manual's home page
- **THEN** they can identify the studio and its version, find how to install
  it, open the hub and work in a project, and reach the framework and viewer
  manuals

#### Scenario: A maker looks up what a project may configure
- **WHEN** a maker reads the project-configuration reference
- **THEN** it states the `profile` key, the per-agent runtime grammar for
  each selectable backend, the Claude models and reasoning levels the studio
  accepts, what an unnamed agent uses, and what the studio rejects or ignores

#### Scenario: A maker follows a link to a sibling manual
- **WHEN** a page links to the framework's or the viewer's manual
- **THEN** the target is one of the pages the repository's documentation
  test lists, each verified to exist in that manual's built HTML

### Requirement: Release facts are stated once and derived from the source

`docs/conf.py` SHALL read the studio's version from `pyproject.toml`, and
SHALL read the required viewer API, the accepted Claude models and reasoning
levels, and the Build inspection volume from the floor's own source without
importing it, exposing each as a substitution. The framework version the
studio runs against SHALL be stated in that same block and nowhere else. No
reader-facing page SHALL carry a literal version, API number, model set or
volume where a substitution stands for it, and the tests SHALL compare each
derived value with the constant it derives from.

#### Scenario: The floor raises the viewer API it requires
- **WHEN** `REQUIRED_VIEWER_API` changes in the floor's source
- **THEN** the manual states the new value on its next build without any
  page being edited

#### Scenario: A page states a version literally
- **WHEN** a reader-facing page carries a literal studio or framework
  version, or a literal viewer API number
- **THEN** the documentation test fails naming the page

### Requirement: Publication state is stated on the status page only

The project status page SHALL be the one reader-facing page that describes
whether the studio is published, released or experimental, what it runs
against, its limits and its direction. Every other manual page, the README,
the changelog and the floor's module docstrings SHALL describe the studio
without a publication caveat. The changelog's first section SHALL be
`Unreleased` while no release has been cut, saying what the current source
gives a maker; when a release is cut, that section becomes the release's and
a new `Unreleased` section sits above it.

#### Scenario: A reader checks where the studio stands
- **WHEN** a reader opens the status page
- **THEN** it states the version, that the studio is installed from a clone
  of its repository, the framework and viewer it requires, the platform and
  backends it runs on, its known limits and its direction

#### Scenario: A page that teaches carries a caveat
- **WHEN** any reader-facing page other than the status page says the
  studio is unpublished, unreleased, in preparation or not on a package
  index
- **THEN** the documentation test fails naming the page

### Requirement: Reader-facing pages carry no records, project names or checkouts

Development history, implementation notes, decision records, design
prototypes and product records SHALL NOT be pages of the manual; the working
record SHALL live under `workflow/` and the Markdown records that the
operating contract names under `docs/` SHALL be excluded from the build. A
reader-facing page SHALL describe a machine by its kind and SHALL NOT name a
project that motivated a behaviour, a project catalogue path, a development
worktree or a sibling checkout.

#### Scenario: The manual is built
- **WHEN** the manual is built
- **THEN** only the `.rst` pages are rendered, the architecture overview,
  ADRs, design reference and product records are not, and no development
  history remains under `docs/`

#### Scenario: A page names a project
- **WHEN** a reader-facing page names a project from the catalogue the
  studio was developed against, or a path into a worktree or sibling
  checkout
- **THEN** the documentation test fails naming the page

### Requirement: The manual is reproducible and reviewable

The manual SHALL build with Sphinx and the Read the Docs theme, warning-free
in nitpicky mode, from `docs/requirements.txt` alone, without the floor's
runtime dependencies, the framework, the viewer or a CAD tool. The `docs`
extra of the package SHALL be identical to `docs/requirements.txt`, and
`.readthedocs.yaml` SHALL build the same way with warnings as failures and
no extra build step. Every option the launcher entry points accept, other
than options they hide from their own help, SHALL be documented in the
command reference. The README SHALL name the studio and its version, say how
it is installed and opened, and point to the manual and the status page.

#### Scenario: The manual is built from a clean checkout
- **WHEN** the documented build command is run with only the documentation
  requirements installed
- **THEN** a warning-free HTML manual is produced

#### Scenario: A launcher gains an option
- **WHEN** an entry point adds an option that its help shows and the
  command reference does not name it
- **THEN** the documentation test fails naming the option

