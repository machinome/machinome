# user-documentation Specification

## Purpose

Give makers a manual for the studio, organised by what they are trying to
do, whose facts are derived from the package or pinned to it by tests,
whose publication state is stated once, and whose pages carry no
development record, project name or workspace path.
## Requirements
### Requirement: Makers have a studio manual

The studio's manual SHALL be its pages of the Machinome manual, in the
repository's `packages/machinome/docs/`, organised by what a maker is trying
to do: three how-to guides, `howto/open-a-studio-project` (install the
studio, start the hub, open, create and close a project from it),
`howto/studio-workspace` (work in a project's conversation, Model, Code,
Agents and Build areas) and `howto/studio-agents` (the shipped profiles,
their agents, what an agent may do, its backend and the separate Codex
login); and the reference section `reference/studio/`: what the studio is
and runs against with its limits, the command `machinome studio` and its
options, the `[tool.machinome-studio]` table, what each shipped profile
declares, and how to diagnose a project that will not start or open. The
pages SHALL state the version they document as the Machinome manual's own,
describe the interface the maker meets, and send the reader to the
framework's and the viewer's pages of the same manual for what those own,
without restating them.

#### Scenario: A maker arrives at the manual
- **WHEN** a maker opens the studio's section of the Machinome manual
- **THEN** they can identify the studio, the package that installs it and
  its command, find how to install it, open the hub and work in a project,
  and reach the framework's and the viewer's pages

#### Scenario: A maker looks up what a project may configure
- **WHEN** a maker reads the project-configuration reference
- **THEN** it states the `profile` key, the per-agent runtime grammar for
  each selectable backend, the Claude models and reasoning levels the studio
  accepts, what an unnamed agent uses, and what the studio rejects or ignores

#### Scenario: A maker follows a link to a sibling manual
- **WHEN** a studio page refers to the framework's or the viewer's pages
- **THEN** it links them as pages of the same manual, by document, and no
  studio page links a manual by its URL

### Requirement: Release facts are stated once and derived from the source

The Machinome manual's `docs/conf.py` SHALL state, as release facts, the
viewer API the studio requires, the Claude models and reasoning levels it
accepts, the qualified Codex version with its models and reasoning levels,
and the Build inspection volume, each exposed as a substitution and read
from no file of the studio at build time. The studio's documentation test
SHALL compare each with the constant of the studio's source it states. The
version the pages document is the manual's `|release|`, the set's. No studio
page SHALL carry a literal version, API number, model set or volume where a
substitution stands for it.

#### Scenario: The floor raises the viewer API it requires
- **WHEN** `REQUIRED_VIEWER_API` changes in the floor's source and the
  manual's release fact does not
- **THEN** the studio's documentation test fails naming the fact

#### Scenario: A page states a version literally
- **WHEN** a studio page carries a literal studio or framework version, or
  a literal viewer API number
- **THEN** the documentation test fails naming the page

### Requirement: Publication state is stated on the status page only

The Machinome manual's status page SHALL be the one page that describes
whether the studio is published, released or experimental; the studio's
section index states what it runs against and its limits. Every studio
page, the README and the floor's module docstrings SHALL describe the studio
without a publication caveat. The changelog's first section SHALL be
`Unreleased` while no release has been cut, saying what the current source
gives a maker; when a release is cut, that section becomes the release's and
a new `Unreleased` section sits above it.

#### Scenario: A reader checks where the studio stands
- **WHEN** a reader opens the Machinome manual's status page and the
  studio's section index
- **THEN** they state that the studio is the package `machinome-studio` of
  the set, experimental, installed by `machinome[studio]`, the framework and
  viewer it requires, the platform and backends it runs on, and its known
  limits

#### Scenario: A page that teaches carries a caveat
- **WHEN** any studio page, the README or a module docstring says the
  studio is unpublished, unreleased, in preparation or not on a package
  index
- **THEN** the documentation test fails naming the page

### Requirement: Reader-facing pages carry no records, project names or checkouts

Development history, implementation notes, decision records, design
prototypes and product records SHALL NOT be pages of the manual; the working
record, the decision log, the architecture overview, the design reference,
the product records and the spikes SHALL live under the package's
`workflow/`. A reader-facing page SHALL describe a machine by its kind and
SHALL NOT name a project that motivated a behaviour, a project catalogue
path, a development worktree or a sibling checkout.

#### Scenario: The manual is built
- **WHEN** the Machinome manual is built
- **THEN** the studio's eight pages are rendered and none of its
  architecture overview, ADRs, design reference or product records is

#### Scenario: A page names a project
- **WHEN** a reader-facing page names a project from the catalogue the
  studio was developed against, or a path into a worktree or sibling
  checkout
- **THEN** the documentation test fails naming the page

### Requirement: The manual is reproducible and reviewable

The studio's pages SHALL build with the Machinome manual, warning-free in
nitpicky mode, from that manual's `docs/requirements.txt` alone; the package
SHALL carry no manual configuration, no `docs` extra and no Read the Docs
configuration of its own. The command reference SHALL name `machinome
studio` as the way the hub is started, with the module forms `python -m
machinome.studio.orchestrator` and `python -m machinome.studio`, and SHALL
document every option the launcher entry points and the command accept,
other than options they hide from their own help, and the studio
configuration file: where it is looked for, the variable that names another
file, every key it accepts, and the order in which options, environment,
file and defaults are applied. The README SHALL name the package and its
command, say how it is installed and started, and point to the manual.

#### Scenario: The manual is built from a clean checkout
- **WHEN** the Machinome manual's documented build command is run with only
  its documentation requirements installed
- **THEN** a warning-free HTML manual is produced, the studio's pages in it

#### Scenario: A launcher gains an option
- **WHEN** an entry point adds an option that its help shows and the
  command reference does not name it
- **THEN** the documentation test fails naming the option

#### Scenario: The configuration file gains a key
- **WHEN** the studio configuration file accepts a key that the command
  reference does not name
- **THEN** the documentation test fails naming the key

#### Scenario: A page teaches how to start the hub
- **WHEN** a reader-facing page shows how to start the hub
- **THEN** it shows `machinome studio`, never the former console script or
  module
