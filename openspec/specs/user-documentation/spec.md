# user-documentation Specification

## Purpose
TBD - created by archiving change docs-0-6-narrative. Update Purpose after archive.
## Requirements
### Requirement: Profile contact is documented as a current-source, pointwise capability

The public `machinome.simulation.profile` imports `ConvexProfile` and
`profile_overlap` SHALL have tested docstrings explaining authored finite
convex loops, ordered rigid-XY placement, inclusive pointwise touching,
invalid-arithmetic refusal and the fact that a running `Bound` still samples
its path under the existing stop rule. The current-source status and
unreleased changelog SHALL distinguish the new predicate and version-13
paired-viewer requirement from the 0.7 release record and its version-11/12
documents. The record SHALL NOT imply a remote push or package-index upload
without evidence. Teaching pages and release substitutions SHALL not be
silently rewritten to present this current-source capability as published.

#### Scenario: A reader inspects the current-source API

- **WHEN** a developer imports the two public names and uses `help()`
- **THEN** the import and docstrings identify the numeric predicate, its
  limits and refusal behavior without naming a workspace project

#### Scenario: A reader checks release status

- **WHEN** a reader compares the project status and changelog with the
  0.7 manual and metadata
- **THEN** the new contact capability and version-13 viewer dependency are
  explicitly current-source/unreleased, while recorded 0.7 version facts
  remain unchanged without an unsupported publication assertion

### Requirement: Release-current narrative framing

The published user documentation's entry surface — the Sphinx index page,
the "why" page, the start pages, and the README's user-facing section — SHALL
present the framework as the released version defines it: a machine whose
declared inputs move its parts through joints and relations, which can be
posed, run with retained history or operated as a machine with memory,
stepped deterministically in Python and driven by hand in the viewer, whose
parts span the full released leaf taxonomy (the modelling-backend adapters
plus sheet, imported-mesh, imported-STEP and flexible leaves). Entry pages
SHALL NOT present a superseded framing (such as backend aggregation or
`$t`-only animation) as the product's thesis, and the tutorial SHALL NOT
teach timeline animation before drivers.

#### Scenario: First contact with the landing page

- **WHEN** a reader opens the documentation index
- **THEN** its introduction names inputs, joints, relations, simulation,
  memory and the driveable viewer alongside modelling, and its navigation
  offers the tutorial, the how-to guides, the concept pages, the examples and
  the reference

#### Scenario: The "why" page matches the release

- **WHEN** a reader opens the "why machinome" page
- **THEN** every capability it claims exists in the released version, its
  backend list matches the released adapters, and no released leaf kind is
  absent from its story

### Requirement: The public motion surface is documented

The documentation SHALL document the released motion and simulation surface:
driver declaration and attribute reads, `set_state` with instance-qualified
ids, ports and `connect()`, joints and relations, instruction declarations,
controls on parts, the fixed-`dt` simulation loop, running and clocked
simulations, and scenario tests that run under both plain pytest and
`machinome test`. Every name exported by `machinome.simulation` SHALL appear in
at least one published page. Every page that embeds a model SHALL use a
committed export, so the documentation build runs no CAD stack.

#### Scenario: Setting a driver from Python

- **WHEN** a reader looks up how to move a machine from code
- **THEN** the documentation shows `set_state` with a qualified dotted id,
  states that assignment to a driver attribute is rejected, and shows the
  driver being read back as an attribute

#### Scenario: Driving a published model in the browser

- **WHEN** a reader opens the tutorial chapter on instructions
- **THEN** an embedded committed export shows per-driver sliders and
  per-instruction buttons, and the page explains the layer-scoped controls
  and breadcrumb focus

#### Scenario: Deterministic stepping

- **WHEN** a reader needs to test a machine's behavior over time
- **THEN** the documentation shows a `ScenarioTest` building a `Sim` with a
  fixed `dt`, scheduling actions and assertions by tick, and running under
  pytest and `machinome test` unmodified

#### Scenario: Operating a machine with history or memory

- **WHEN** a reader needs a machine that accumulates or remembers
- **THEN** the tutorial shows `Time.running()` with moves, a ratchet stop and
  a control on the part, then `State` with a committing relation and a
  request, and a concept page states what each execution model owns,
  publishes and refuses

### Requirement: Viewer and embedding claims are accurate

Embedding and viewer documentation SHALL state, through the shared
substitutions, the viewer API version the widget actually declares and the
document schema versions it accepts, SHALL state what an export contains and
which document version each kind of machine publishes, SHALL show the
simplest host (an iframe of the exported page) and the Sphinx directive, and
SHALL link to the viewer manual for the complete public mount-handle surface
rather than restating it. It SHALL warn hosts that pin their own bundle when
older viewers cannot detect documents they do not understand. Known
interface limitations (such as poses that can only be preset through `$t`)
SHALL be stated rather than left for the reader to discover.

#### Scenario: A host pins its own bundle copy

- **WHEN** an embedding host reads the embedding page
- **THEN** a prominent warning states that a pre-0.6 viewer silently
  renders only part of a newer document and that a pinned bundle must be
  upgraded with the framework

#### Scenario: A host builds its own control UI

- **WHEN** a host wants programmatic driving without the built-in chrome
- **THEN** the documentation points at the viewer manual's embedding guide
  and API reference, and states that values there are in native driver
  units and that declared ranges never clamp

### Requirement: Installation and dependency claims match released packaging

Requirement and installation statements in the documentation SHALL match the
released packaging: dependencies that are conditional in the release (such
as the OpenSCAD binary and the mesh engine on the faceted path) SHALL be
described as conditional with the condition named, hard dependencies (such
as molejo) SHALL NOT be described as optional or unpublished, and an upgrade
that requires reinstalling the environment SHALL be called out where an
existing user would look for it.

#### Scenario: An all-exact project

- **WHEN** a reader whose parts are all OCCT-backed reads the quickstart
- **THEN** they learn the OpenSCAD binary is needed only for the
  OpenSCAD-family and faceted paths, not for installing or using the
  framework

#### Scenario: Upgrading an existing environment

- **WHEN** a 0.5.x user consults the documentation before upgrading
- **THEN** they find the instruction to reinstall the environment and the
  reason the in-place upgrade fails

### Requirement: The examples page sends readers to machinome.org

The manual's examples section SHALL be one page that embeds no model, builds
no machine and pins no external repository. It SHALL send the reader to the
Foundry on machinome.org, where the simulated machines are shown live beside
their designs, and SHALL say what a reader finds there by kind of machine and
by execution model — a posed, a running and a clocked machine — rather than
by embedding or naming a project. The manual SHALL carry no example page of
its own and no Git submodule; a page that mentions a full machine the
tutorial does not build SHALL point at the site, not at a page of this
manual.

#### Scenario: Reaching the examples

- **WHEN** a reader opens the examples page
- **THEN** it links to the Foundry on machinome.org, embeds no live model,
  and names a posed, a running and a clocked machine as kinds the reader
  finds there

#### Scenario: A page that used to point at an example

- **WHEN** a how-to or concept page refers to a full machine the tutorial
  does not build
- **THEN** it points at the Foundry on machinome.org and not at a page of
  this manual

#### Scenario: No example is pinned

- **WHEN** the repository is cloned
- **THEN** it has no `.gitmodules` and no `docs/example-*.rst` page

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists:
Sphinx, its theme and the published `machinome-viewer` package, which
completes the committed exports with its widget. The Read the Docs
configuration and the CI docs job SHALL both install that file and run
Sphinx, and neither SHALL run `machinome export`, install a system package,
a Node tool or a package from a repository URL, or check out a submodule.
Every export a page embeds SHALL be committed under `docs/_exports/`.

#### Scenario: Read the Docs builds the manual

- **WHEN** Read the Docs builds any version of the manual
- **THEN** its configuration names no build job, no apt package and no Node
  tool, installs `docs/requirements.txt` alone, and the build takes the
  time Sphinx alone takes

#### Scenario: A page embeds an export nobody committed

- **WHEN** a `.. machinome::` directive names a directory outside
  `docs/_exports/`
- **THEN** the suite fails naming the page, before any documentation build

#### Scenario: A build configuration grows a build step

- **WHEN** the Read the Docs configuration or the CI docs job gains an
  export command, a repository install, an apt package, a Node tool or a
  submodule checkout
- **THEN** the suite fails naming the file and the step

#### Scenario: The manual builds from the requirements alone

- **WHEN** a fresh environment installs `docs/requirements.txt` and builds
  the manual with warnings as errors
- **THEN** the build succeeds and every tutorial page shows its committed
  export with the viewer's widget

### Requirement: The release is recorded where readers are sent

The documentation SHALL carry the released version's changelog entry on its
changelog page, a release note under `docs/releases/` for each release that
has one-page announcements, and a status page that reports the released
version as released with its date, with a roadmap that does not list shipped
work as pending. The status page SHALL be the one page that discusses the
publication state of the framework, the viewer and the mechanics packages.

#### Scenario: Following the status page to the changelog

- **WHEN** a reader follows the status page's link to the changelog
- **THEN** the changelog's top entry is the released version with its date

#### Scenario: Roadmap honesty

- **WHEN** a reader compares the roadmap against the released feature set
- **THEN** no roadmap item is already shipped, and deliberate deferrals
  recorded in the changelog appear as open work

### Requirement: The declarative authoring surface is documented

The documentation SHALL cover the three layers of a value (parameter,
constant, port), the parameter kinds and the dimension algebra including the
`machinome.math` functions, derived formulas, class-body child declarations,
literal lists and `repeat`, a class-body list comprehension over module-level
values, an internal `render()` that positions and returns nothing, `omit()`,
root overrides from Python and from `--set` on the command line, a parameter
without a default, `check()` for guards over several parameters, the
lifecycle split — `render()` builds the machine at rest and places what
does not move, `simulate()` reads drivers, time and ports and moves what
does, motion composing innermost — the deprecation of driver reads in
`render()` with the warning a reader will see, and the two pitfalls:
class-level names are invisible to a class-body comprehension, and
structure that depends on time. It SHALL NOT recommend placement in
`__init__`. It SHALL state that a driver cannot be qualified on a repeated
or list-held child and that ports are the drive path for identical units.
The tutorial's dimensions chapter introduces parameters; the concept pages on
values and on rest and motion, and the how-to guide on repeating a unit and
varying a design, carry the rest.

Every example that declares a parameter SHALL import the kinds from the
dedicated build-parameter module, and every example that declares a port
or a time base SHALL import them from `machinome.motion.ports`. The concept
page on values SHALL state that build parameters come from that module while
node classes come from the node package, ports and the declared time base
from the motion package, and drivers from the simulation package. Every
tutorial chapter, how-to guide, concept page and the API reference SHALL read
drivers and time in `simulate()`, the node-tree, part and CLI pages SHALL
cross-reference the values page, and the changelog SHALL record the lifecycle
with the deprecation.

The API reference SHALL document the build-parameter module: the kinds, the
`Quantity` base a project subclasses, and the enumerator over a class's
declarations, in a section of its own beside the node, port, simulation and
testing sections. Its port section SHALL state `machinome.motion.ports`
as the import path for the port kinds and the time base.

#### Scenario: A reader learns where a kind comes from

- **WHEN** a reader looks up how to declare a parameter
- **THEN** the import line in the example names the build-parameter module,
  and the page says which module answers for parameters, for node classes
  and for drivers

#### Scenario: A reader looks up a kind in the reference

- **WHEN** a reader opens the API reference for `Length` or `Flag`
- **THEN** the reference documents it under the build-parameter module, with
  the module's import path stated in the section

#### Scenario: A reader replaces an `__init__`

- **WHEN** a reader who knows the constructor form looks up how to declare
  a leaf's parameters
- **THEN** the page shows the declared form beside the constructor form it
  replaces, states that identity is derived by the framework, and shows the
  value read back as a plain number in `render()`

#### Scenario: A reader repeats a unit

- **WHEN** a reader needs eight identical parts placed differently
- **THEN** the page shows `repeat` with per-unit placement in `render()`
  through `enumerate` and constants, states that the units share one
  artifact, and warns that a class-body list comprehension cannot see
  class-level names while one over a module-level table declares

#### Scenario: A reader guards two parameters against each other

- **WHEN** a reader has a rule that one declared dimension must exceed
  another
- **THEN** the page shows `check()` raising for the bad pair, states when
  the framework calls it and that a refused instance realizes no child,
  and that it is not called on a class that declares nothing

#### Scenario: A reader places a stationary part

- **WHEN** a reader asks where a once-only placement goes
- **THEN** the page shows it in `render()`, shows the moving part's
  operation in `simulate()`, states that the framework runs `render()`
  once and `simulate()` per instant, and that motion composes inside the
  rest placement

#### Scenario: A reader varies a design from the shell

- **WHEN** a reader wants to build the model at another size
- **THEN** the CLI page shows `--set name=value`, how a value is parsed by
  its kind, and what happens for a parameter with no default

#### Scenario: A reader migrates a render that reads time

- **WHEN** a reader's build prints the deprecation warning
- **THEN** the page shows the warning, the `render()` that caused it, and
  the same class with the read and its operations moved to `simulate()`

#### Scenario: A reader learns where a port comes from

- **WHEN** a reader looks up how to declare a port or a time base
- **THEN** the import line in the example names `machinome.motion.ports`,
  and the page says which module answers for parameters, for node classes,
  for ports and the time base, and for drivers

### Requirement: The viewer's provenance and installation are stated

Every documentation page that installs, opens, embeds or photographs through
the browser viewer SHALL state that the viewer is the separate
`machinome-viewer` package, licensed AGPL-3.0-only, installed with
`pip install "machinome[viewer]"`. It SHALL state that interactive
`machinome develop` requires that package, while a plain framework installation
can build, test, export without the widget, run `machinome develop --no-web`, and
snapshot through OpenSCAD. Web-viewer operations SHALL name the extra as their
remedy. The README's installation section SHALL make the licence difference
visible before a reader installs the extra. Text that tells a reader to build
the viewer with npm inside the framework SHALL NOT remain.

The v0.7 release material SHALL explain that OpenSCAD was machinome's first
reliable viewer, that the browser viewer progressively became the faithful
machine surface as simulation gained drivers, instructions and flexible
motion, and that maintaining the less capable OpenSCAD GUI now obstructs that
roadmap. It SHALL distinguish removal of the GUI viewer and fallback from the
retained `OpenScadNode`, `Solid2Node`, SCAD-output, legacy-evaluation, and
OpenSCAD snapshot-renderer capabilities.

#### Scenario: A reader installs the framework

- **WHEN** a reader follows the README or quickstart installation steps
- **THEN** they see that the `viewer` extra supplies the sole interactive
  development viewer, that the plain install has no interactive viewer, and
  that the packages have different licences

#### Scenario: A reader migrates from the OpenSCAD viewer

- **WHEN** a v0.7 reader previously used `machinome develop --openscad` or relied
  on its fallback
- **THEN** the release material explains why it was removed and directs them
  to `machinome[viewer]` with ordinary `machinome develop`, or to `--no-web` for
  a viewerless watch loop

#### Scenario: A reader distinguishes modelling from viewing

- **WHEN** a reader authors OpenSCAD or SolidPython geometry after the viewer
  removal
- **THEN** the documentation says those node types and the fixed-pose OpenSCAD
  snapshot renderer remain supported, without calling OpenSCAD an interactive
  machinome viewer

#### Scenario: A contributor looks for the viewer source

- **WHEN** a contributor reads the viewer or contributing pages
- **THEN** they are pointed at the machinome-viewer repository and find no
  instruction to run npm inside machinome

### Requirement: The comparison kernels are documented

The how-to guide on running tests fast SHALL explain that a test run
compares on one of two kernels: the exact boundary-representation kernel,
the default and the one a release or CI run uses, and the faceted kernel,
which answers every geometric question on the parts' meshes at tessellation
precision and is the one a developer selects for a fast loop. It SHALL state
how the kernel is selected (`--exact` / `--faceted`, else
`SOLID_TEST_KERNEL`, else exact), that a checkout's ignored `.env` is where a
developer records the faceted choice so CI inherits nothing, what the volume
epsilon absorbs and that it exists only for the faceted kernel, and that a
faceted run labels itself.

The same guide SHALL also explain the run's placement quantum: that the
verdict memo asks whether two comparisons are the same question, that the
relative placement deciding that is quantised to a grid so the float noise of
composing one rigid motion by two routes does not split a question in two,
that the quantum is selected by `--placement-quantum`, else
`SOLID_TEST_PLACEMENT_QUANTUM`, else the documented default, that `0` restores
the exact-bytes key, that it applies under both kernels, and that it is a
statement about arithmetic noise and must stay far below the smallest
clearance the suite judges. It SHALL state that a run at a non-default quantum
says so on its summary line.

The CLI page SHALL list the four options under `machinome test` and the three
environment variables. The changelog SHALL record the capability.

#### Scenario: A developer learns how to run fast

- **WHEN** a reader whose suite is slow on exact solids reads the guide
- **THEN** they find the faceted kernel, the `.env` line that selects it for
  their checkout, and the statement that CI keeps the exact kernel

#### Scenario: A reader looks up the flags

- **WHEN** a reader looks up `machinome test` on the CLI page
- **THEN** they find `--exact`, `--faceted`, `--volume-epsilon`,
  `--placement-quantum`, and the three environment variables with their
  precedence

#### Scenario: A reader learns what the placement quantum decides

- **WHEN** a reader whose sweep re-runs booleans on parts that move together
  reads the guide
- **THEN** they find what the quantum merges, its default, that `0` restores
  the exact key, and that it is not a tolerance on any assertion

### Requirement: Current documentation presents Machinome and its lineage

Every current entry page, installation guide, tutorial, API reference, status
page, contributor guide and source link SHALL use Machinome distribution,
import, command, configuration and repository names. The 0.7 changelog and
release note SHALL explain why solid-node was renamed, define *machinome*, and
provide a tested migration from solid-node 0.6.0. Historical release notes and
decision records SHALL retain their original terminology.

#### Scenario: A new user follows the quickstart

- **WHEN** the user follows current installation and first-project guidance
- **THEN** every command and import uses `machinome` and every optional product
  uses its Machinome name

#### Scenario: An existing user migrates

- **WHEN** a solid-node 0.6 user opens the 0.7 migration section
- **THEN** it maps distributions, imports, executable, environment variables,
  project configuration, viewer and mechanics names and states which aliases
  are not provided

### Requirement: Mechanics users can reach the independent helper manual

The framework manual SHALL identify machinome-mechanics as its optional
mechanics helper package and link directly to that package's user documentation
from its guide navigation, helper API reference, motion-law guidance and
migration guidance. It SHALL preserve the separate installation and import
boundary and direct readers to the mechanics manual for complete helper usage
and coordinate conventions.

#### Scenario: Find a helper from the framework

- **WHEN** a framework user looks for a gear, screw, crank, delta or linkage helper
- **THEN** the manual offers a direct link to the mechanics user reference
- **AND** states that helpers are imported from `machinome_mechanics`

#### Scenario: Follow a motion-law or migration guide

- **WHEN** a reader wants to reuse a mechanical formula or migrate the former
  framework helper imports
- **THEN** they can follow a direct link to the mechanics manual for examples
  and conventions without needing internal workflow records

### Requirement: Viewer users can reach the independent viewer manual

The framework manual SHALL link to the machinome-viewer user manual from its
navigation and viewer/embedding entry points. The links SHALL lead makers to
operating guidance and embedding hosts to the complete public reference, while
retaining accurate framework-facing examples, package provenance, licensing
and publication status.

#### Scenario: A maker needs to operate the viewer
- **WHEN** a maker reads the framework's viewer page
- **THEN** they can follow a direct link to the viewer manual's operating guide

#### Scenario: A host needs a browser API detail
- **WHEN** a host reads the framework's embedding page
- **THEN** they can follow a direct link to the viewer's complete API reference
  and working embedding example

### Requirement: One tutorial machine carries the learning path

The manual's tutorial SHALL build one framework-owned machine, chapter by
chapter, in the order the framework describes a machine: a part; an input
moving a body through a joint and a relation; shared dimensions; one
coordinate driving another through a ratio and a law; instructions; fit
contracts proved red first; a stepped scenario; a running machine with a
physical stop and controls on a part; a machine with retained state and
committing relations; sharing the result. A driver and a joint SHALL appear
before any timeline animation. Every chapter's model SHALL be real source in
the repository that the framework suite imports, assembles and builds, and
every companion test a chapter writes SHALL run under `machinome test` in that
suite. Tutorial pages SHALL include their code from those modules and SHALL
embed only committed exports.

#### Scenario: A reader follows the tutorial in order

- **WHEN** a reader opens the tutorial's second chapter
- **THEN** the machine they build declares a `Driver` and a joint and relates
  them, and the viewer shows a slider that moves the part, before `self.time`
  has been introduced

#### Scenario: A chapter's code cannot drift from its page

- **WHEN** a chapter module is changed so that its model no longer builds or
  its companion test no longer passes
- **THEN** the framework suite fails naming the chapter

#### Scenario: A chapter shows a model

- **WHEN** a tutorial page embeds a live model
- **THEN** the export it names is committed under `docs/_exports/` and the
  documentation build needs no CAD stack to render it

### Requirement: The manual is organised by reader intent

The manual's navigation SHALL be organised into a why page, a start section
(installation and a first machine), the tutorial, how-to guides, concept
pages, examples, reference and project pages, with each page serving one of
those purposes. Internal engineering records (change evidence, development
logs, expression-graph publication details) SHALL NOT be reachable from the
navigation. Publication facts — the framework version and release date, the
viewer package version, its API version and the document versions it reads,
the mechanics package version — SHALL be defined once as Sphinx substitutions
and discussed on the status page; tutorial, how-to and concept pages SHALL
NOT carry publication caveats or viewer version gates.

#### Scenario: A reader looks for a job, a rule or a lesson

- **WHEN** a reader opens the navigation
- **THEN** they find a how-to section of task pages, a concept section of
  rule pages and one tutorial, and no page appears in more than one of those
  roles

#### Scenario: The release changes

- **WHEN** a version or publication fact changes
- **THEN** it is edited in one place in `conf.py` and on the status page, and
  no tutorial, how-to or concept page needs to change
