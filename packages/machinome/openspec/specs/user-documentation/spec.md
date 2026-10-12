# user-documentation Specification

## Purpose
TBD - created by archiving change docs-0-6-narrative. Update Purpose after archive.
## Requirements
### Requirement: Profile contact is documented as a current-source, pointwise capability

The public `machinome.simulation.profile` imports `ConvexProfile` and
`profile_overlap` SHALL have tested docstrings explaining authored finite
convex loops, ordered rigid-XY placement, inclusive pointwise touching,
invalid-arithmetic refusal and the fact that a running `Bound` still samples
its path under the existing stop rule. The 0.7.0 release record SHALL
include the predicate and its version-13 paired-viewer requirement, since
Machinome 0.7.0 shipped them; the status page and changelog SHALL NOT
describe them as current-source or unreleased. The record SHALL NOT imply
a remote push or package-index upload without evidence.

#### Scenario: A reader inspects the current-source API

- **WHEN** a developer imports the two public names and uses `help()`
- **THEN** the import and docstrings identify the numeric predicate, its
  limits and refusal behavior without naming a workspace project

#### Scenario: A reader checks release status

- **WHEN** a reader compares the project status and changelog with the
  0.7 manual and metadata
- **THEN** finite profile contact and the version-13 viewer requirement
  are in the 0.7.0 release record, and the recorded 0.7 version facts
  are stated once in `docs/conf.py`

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

The joints page's passage on a joint declared where a parent declares a
child SHALL say that the joint's values are read where the child finally
rests, after every rest operation the parent applies to it, so that when
one of those operations is conditional a plain value is right for one
branch only and the argument to write is a callable of the realized
parent.

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

#### Scenario: A site joint under a conditional rest placement

- **WHEN** a reader declares a joint where a parent declares a child, and
  the parent's rest placement of that child depends on a condition
- **THEN** the joints page's site passage tells them the values are read
  where the child finally rests, that a plain value is right for one
  branch only, and that a callable of the realized parent is what to write

### Requirement: Viewer and embedding claims are accurate

Embedding and viewer documentation SHALL state, through the shared
substitutions, the viewer API version the widget actually declares and the
document schema versions it accepts, SHALL state what an export contains and
which document version each kind of machine publishes, SHALL show the
simplest host (an iframe of the exported page) and the Sphinx directive, and
SHALL link to the viewer's reference section of the manual for the complete
public mount-handle surface rather than restating it. It SHALL warn hosts that pin their own bundle when
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
- **THEN** the documentation points at the manual's guide to embedding the
  viewer and its browser API reference, and states that values there are in
  native driver units and that declared ranges never clamp

### Requirement: Installation and dependency claims match released packaging

Requirement and installation statements in the documentation SHALL match the
released packaging: dependencies that are conditional in the release (such
as the OpenSCAD binary and the mesh engine on the mesh path) SHALL be
described as conditional with the condition named, hard dependencies (such
as molejo) SHALL NOT be described as optional or unpublished, and an upgrade
that requires reinstalling the environment SHALL be called out where an
existing user would look for it.

#### Scenario: An all-B-rep project

- **WHEN** a reader whose parts are all OCCT-backed reads the quickstart
- **THEN** they learn the OpenSCAD binary is needed only for the
  OpenSCAD-family and mesh paths, not for installing or using the
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
Every export a page embeds SHALL be committed under `docs/_exports/`. The
guide to embedding the viewer SHALL show its working host page from the
built manual: the build SHALL copy the page, the committed export it loads and
the installed viewer's bundle beside the guide, and SHALL take the viewer only
from what `docs/requirements.txt` installs, never from the viewer's source
directory of the repository, whose bundle is not built there.

The Read the Docs configuration SHALL sit beside the manual, at
`packages/machinome/.readthedocs.yaml`, and SHALL name the requirements
file and the Sphinx configuration by their paths from the repository
root, `packages/machinome/docs/requirements.txt` and
`packages/machinome/docs/conf.py`, since Read the Docs reads every path in
it from there. The CI docs job, in the repository's workflow at
`.github/workflows/python-app.yml`, SHALL run from the package directory,
where it installs `docs/requirements.txt` and builds `docs`.

Both builds SHALL treat warnings as errors, and the manual's Sphinx
configuration SHALL make every build nitpicky, so that a cross-reference
whose target the manual does not document, written in a page or in a
docstring the manual renders, fails the build that Read the Docs and the
CI docs job run.

#### Scenario: Read the Docs builds the manual

- **WHEN** Read the Docs builds any version of the manual
- **THEN** its configuration names no build job, no apt package and no Node
  tool, installs `packages/machinome/docs/requirements.txt` alone, and the
  build takes the time Sphinx alone takes

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

#### Scenario: A reference names nothing the manual documents

- **WHEN** a page or a rendered docstring cross-references a target the
  manual does not document, such as a class named without its module
  where the current module does not hold it, or a docstring line napoleon
  reads as a type
- **THEN** the CI docs job's command, `python -m sphinx -b html -W docs
  <out>`, fails naming the reference, with no `-n` on its command line,
  and the suite fails if the manual's configuration stops being nitpicky

#### Scenario: The configuration names the manual from the repository root

- **WHEN** the suite reads `packages/machinome/.readthedocs.yaml`
- **THEN** its one install entry is the requirements file
  `packages/machinome/docs/requirements.txt` and its Sphinx configuration
  is `packages/machinome/docs/conf.py`, and the suite fails naming the path
  if either names the manual from the package directory instead

#### Scenario: The embedding guide's host page runs from the built manual

- **WHEN** the manual is built from `docs/requirements.txt` and the guide to
  embedding the viewer is opened in a browser
- **THEN** its example loads the committed spinner export with the installed
  viewer's bundle, both copied beside the page by the build, and the
  framework's lookup answers the installed viewer even though the
  repository's viewer source lies beside the framework's directory

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
node classes come from their own modules under the node package
(`machinome.node.assembly`, `machinome.node.cadquery`, ...), ports and the
declared time base from the motion package, and drivers from the simulation
package. Every
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
the browser viewer SHALL state that the viewer is the package
`machinome-viewer` of the Machinome repository, released and licensed with
the framework, installed with `pip install "machinome[viewer]"` and reached
only as a separate process. It SHALL state that interactive
`machinome develop` requires that package, while a plain framework installation
can build, test, export without the widget, run `machinome develop --no-web`, and
snapshot through OpenSCAD with the `openscad` extra. Web-viewer operations SHALL name the extra as their
remedy. No page SHALL describe the viewer as licensed differently from the
framework. Building the viewer's widget from source with Node and npm SHALL be
the contributor guide's, not a reader page's.

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
  that every package of the repository carries the framework's licence

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
- **THEN** they are pointed at the viewer's directory of the repository,
  `packages/machinome-viewer/`, and at the contributor guide for the Node
  setup, and no reader page tells them to run npm

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

### Requirement: Explicit frame direction precision is documented narrowly

Public Frame and ResolvedFrame docstrings and the frame/readout explanation in
`docs/concepts/joints.rst` SHALL state that explicitly supplying BOTH x and z
retains full normalized/projected/cross-product direction precision without
component snap. They SHALL distinguish explicit default z from omitted z,
state that omitted x (including None) and explicit x with omitted z retain
existing snapped/default behavior, and retain principal inference and named
degeneracy refusals. They SHALL state that resolved_frames returns the same
cached basis mates use, not a separately altered display basis, and SHALL NOT
imply that final mate rotation/axis snap or Joint axis snapping changes.

`docs/project/changelog.rst` SHALL record the numeric contract in the
section of the release that ships it, Machinome 0.7.1, and not in the
0.7.0 section. Reader-facing explanations SHALL use mechanical kinds
rather than originating project names, and SHALL introduce no precision
flag or new signature.

#### Scenario: A reader supplies an exact attachment triad

- **WHEN** a reader consults Frame help and the frame/readout manual passage
- **THEN** they learn the both-explicit precision rule, unchanged projection
  and refusal behavior, same actual resolved basis and unchanged final snap

#### Scenario: A reader omits the default z

- **WHEN** a reader compares Frame(x=...) with Frame(z=(0,0,1), x=...)
- **THEN** the documentation explains that only the latter supplies both
  directions explicitly and that the former keeps the old snapped path

#### Scenario: A reader checks the change's publication state

- **WHEN** a reader reads the changelog
- **THEN** the precision change is in the 0.7.1 section and the 0.7.0
  section does not mention it

### Requirement: The 0.7.1 release is recorded

The release record of Machinome 0.7.1 SHALL remain as released below
every later release. The changelog SHALL keep the `Machinome 0.7.1`
section, dated `Released on 27/Sep/2026`, naming frames and mates
(`Frame`, `.on(`, `Revolute`, `Prismatic`, `resolved_frames`),
`machinome vet` and the corrections, and sending the reader to the
concept and reference pages that teach them; `HISTORY.rst` SHALL keep its
`Machinome 0.7.1 (2026-09-27)` entry; the 0.7 release note SHALL keep its
dated 0.7.1 section. A release fact SHALL be rendered by its
substitution: no `|release|`-style reference sits inside inline markup,
where reStructuredText leaves it literal.

#### Scenario: A reader looks for 0.7.1 after a later release

- **WHEN** a reader reads the changelog and the history after 0.8.0
- **THEN** the 0.7.1 section and entry sit below the later release's,
  unchanged, with their date

#### Scenario: A reader opens the status page

- **WHEN** a reader opens the built status page
- **THEN** its first sentence states the version and the date as numbers,
  not as `|release|` and `|release_date|` (the 0.7.0 manual on Read the
  Docs shows them literally, inside a bold sentence)

#### Scenario: A reader looks for frames and mates in the release

- **WHEN** a reader reads the 0.7.1 changelog section
- **THEN** it names frames, the mate sentence and its freedoms, the
  read of frames and mates, `machinome vet` and each correction, and
  sends the reader to the concept and reference pages that teach them

### Requirement: The 0.8.0 release is recorded

The release facts of Machinome 0.8.0 SHALL agree wherever they are
stated. `pyproject.toml`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `setup.cfg`'s bumpversion table and
`docs/conf.py`'s `release` SHALL all state the released version, and the
tests SHALL hold them to the version `pyproject.toml` states rather than
to a literal. `docs/conf.py`'s release block SHALL be the one place the
manual states the release date, the matching viewer's version and API,
the document versions, the mechanics version and the framework's
licence; a page SHALL state each through its substitution
(`|release_date|`, `|viewer_version|`, `|viewer_api|`,
`|document_versions|`, `|mechanics_version|`, `|framework_licence|`),
never as a literal.

The framework's licence SHALL be stated as GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice, as the current fact
and nothing more: no comparison with any other licence, no position on
derivative works, no exception and no reason. The framework's licence
SHALL reach a page only through the one fact in `docs/conf.py`,
`|framework_licence|`, and `README.rst` SHALL state the same words. No
`.rst` page under `docs/` other than the historical release notes under
`docs/releases/` SHALL spell a licence identifier literally;
`README.rst` SHALL spell no licence identifier but the exact words of
`docs/conf.py`'s `framework_licence`. The browser viewer SHALL be stated as
a package of the repository under the same licence (change `join-viewer`).

The changelog SHALL keep a `Machinome 0.8.0` section, dated
`Released on 05/Oct/2026`, below any later release's; it SHALL open with
what a maker gets, state the licence first, and list every breaking
change of 0.8 in one line each with a link to the upgrading page.
`HISTORY.rst` SHALL keep the entry `Machinome 0.8.0 (2026-10-05)`.
`docs/releases/release-0.8.rst` SHALL be the release note of the 0.8
line, its title naming 0.8 and dated 5 October 2026, reached from the
changelog. The upgrading page SHALL keep a part for upgrading from 0.7 to
0.8 that lists every breaking change of 0.8 and, for each, what to
change, above the 0.6 to 0.7 material, which stays intact; no section of
it SHALL be marked unreleased or speak of "the next release".

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader reads the changelog and the history after a later
  release
- **THEN** the 0.8.0 section and history entry still state 0.8.0,
  released on 5 October 2026, below the later release's

#### Scenario: A version file is left behind

- **WHEN** one of the files that state the version is moved and another
  is not
- **THEN** the release-records test fails naming the file that disagrees
  with `pyproject.toml`

#### Scenario: A reader looks up the licence

- **WHEN** a reader reads the installation page, the "why" page, the
  status page or the README
- **THEN** each states the framework's licence as GPL-2.0-or-later or
  CERN-OHL-S-2.0-or-later, the manual's pages through the one fact in
  `docs/conf.py`, and the viewer as a package of the repository under it

#### Scenario: A page spells a licence literally

- **WHEN** a page under `docs/` other than a historical release note
  spells a licence identifier, or the README spells one other than the
  framework's current words
- **THEN** the documentation tests fail naming the page

#### Scenario: A 0.7 user upgrades

- **WHEN** a 0.7 user opens the upgrading page
- **THEN** its 0.7 to 0.8 part lists every breaking change of 0.8, the
  install's extras, the import paths, the engines' names, the OpenSCAD
  family, a node's shape, the leaf contract, the symbolic value and the
  removed modules among them, each with what to change

#### Scenario: A reader follows the release note

- **WHEN** a reader opens the changelog
- **THEN** its table of contents reaches the 0.8 release note, which is
  dated 5 October 2026 and sends the reader to the upgrading page

### Requirement: The comparison engines are documented

The how-to guide on running tests fast SHALL explain that a test run
compares on one of two engines: the B-rep engine,
the default and the one a release or CI run uses, and the mesh engine,
which answers every geometric question on the parts' meshes at tessellation
precision and is the one a developer selects for a fast loop. It SHALL state
how the engine is selected (`--brep` / `--mesh`, else
`SOLID_TEST_ENGINE`, else `brep`), that
 a checkout's ignored `.env` is where a
developer records the mesh choice so CI inherits nothing, what the volume
epsilon absorbs and that it exists only for the mesh engine, and that a
mesh run labels itself.

The same guide SHALL also explain the run's placement quantum: that the
verdict memo asks whether two comparisons are the same question, that the
relative placement deciding that is quantised to a grid so the float noise of
composing one rigid motion by two routes does not split a question in two,
that the quantum is selected by `--placement-quantum`, else
`SOLID_TEST_PLACEMENT_QUANTUM`, else the documented default, that `0` restores
the exact-bytes key, that it applies under both engines, and that it is a
statement about arithmetic noise and must stay far below the smallest
clearance the suite judges. It SHALL state that a run at a non-default quantum
says so on its summary line.

The same guide SHALL also explain the verdict store. It SHALL say:

- that every verdict a run decides is kept under the project's build
  directory, and served to a later run that asks the same question of the
  same state;
- that the state is the content of the compared parts' artifacts, a flexible
  part's bound values and specification, and the pair's quantised relative
  placement, so a rebuild reproducing the same artifacts or a moved project
  still reuses it;
- that a change to the framework or to an installed geometry kernel starts
  it afresh on its own;
- that it never changes a verdict;
- that `--no-verdict-store` or `SOLID_TEST_VERDICT_STORE=off` runs without
  it, and that such a run says so;
- that deleting the `.verdicts` directory is always safe.

The CLI page SHALL list the options under `machinome test` (`--brep`,
`--mesh`, `--volume-epsilon`, `--placement-quantum`, and `--verdict-store` /
`--no-verdict-store`) and the four environment variables. The changelog SHALL
record the capability.

#### Scenario: A developer learns how to run fast

- **WHEN** a reader whose suite is slow on B-rep solids reads the guide
- **THEN** they find the mesh engine, the `.env` line that selects it for
  their checkout, and the statement that CI keeps the B-rep engine

#### Scenario: A reader looks up the flags

- **WHEN** a reader looks up `machinome test` on the CLI page
- **THEN** they find `--brep`, `--mesh`, `--volume-epsilon`,
  `--placement-quantum`, `--verdict-store` / `--no-verdict-store`, and the four
  environment variables with their precedence

#### Scenario: A reader learns what the placement quantum decides

- **WHEN** a reader whose sweep re-runs booleans on parts that move together
  reads the guide
- **THEN** they find what the quantum merges, its default, that `0` restores
  the exact key, and that it is not a tolerance on any assertion

#### Scenario: A reader learns why a second run is fast

- **WHEN** a reader whose second test run finished in seconds, where the first
  took minutes, reads the guide
- **THEN** they find that verdicts are kept between runs and keyed on the
  state of their parts, that no verdict changes because of it, how to run
  without the store, and that the `.verdicts` directory may be deleted at any
  time

### Requirement: The manual imports every name from its module

The node package's root resolves no name (`node-model`, "The node package's
root exports nothing"), so the documentation SHALL show and state one import
path per name, the module that defines it:

- every example a reader is sent to -- the tutorial's modules, the how-to
  guides, the concept pages, the API reference and `README.rst` -- SHALL import
  each node class and declaration from its module, and no page a reader is sent
  to SHALL spell `from machinome.node import <name>` or `machinome.node.<name>`
  for a name the root resolved until the OpenSpec change `root-cleanup`; the
  decision records under `docs/adrs/` keep the names they used;
- the API reference SHALL document each node class under its module address
  and SHALL NOT say that node classes are importable from `machinome.node`;
- the upgrading page SHALL state that the root exports nothing and that nothing
  aliases a former spelling, show the refusal a former spelling meets, and map
  each of the twenty-one names to its module;
- the installation page SHALL list the extra of every node type of the table of
  supported node types, `machinome[jscad]` and `machinome[stl]` among them, with
  what each installs, and the how-to guide on choosing a part backend SHALL list
  every node class with its module and the extra that installs it;
- the changelog SHALL record the change in the section of the release that
  ships it, Machinome 0.8.0.

#### Scenario: A reader copies an example

- **WHEN** a reader copies the import block of any example in the manual into a
  project
- **THEN** every node name in it is imported from its module, and the project
  imports it

#### Scenario: A reader looks up a node class in the reference

- **WHEN** a reader opens the API reference for `CadQueryNode`, `StlNode` or
  `AssemblyNode`
- **THEN** the class is documented as `machinome.node.cadquery.CadQueryNode`,
  `machinome.node.stl.StlNode` and `machinome.node.assembly.AssemblyNode`, and
  the section states that each class is imported from its module

#### Scenario: A reader upgrades a project that imports from the root

- **WHEN** a reader whose project writes `from machinome.node import
  AssemblyNode, CadQueryNode` reads the upgrading page
- **THEN** they find that the root exports nothing, the error their import line
  meets, and the module of each of the twenty-one names

#### Scenario: A reader picks the extra of a node type

- **WHEN** a reader looks up what to install for `JScadNode` or `StlNode`
- **THEN** the installation page names `machinome[jscad]` and `machinome[stl]`,
  says that neither installs anything beyond the package, and that `JScadNode`
  needs the `jscad` command, which no extra installs

### Requirement: The README describes the package

`README.rst`, the landing page of the framework's directory
`packages/machinome/` and the distribution's long description, SHALL present Machinome as it is, to a reader who does not
know it: what the framework is and what belongs in a machine's source; what
that source looks like, as Python the suite builds; what the framework does
with it (incremental builds, tests, simulation, the browser viewer and
static exports); how to install it and name the extras its parts need; where
the manual, the tutorial, the changelog and the upgrading page are; the
framework's licence in the exact words of `docs/conf.py`'s
`framework_licence`; and where contributors go.

The README's sections SHALL be exactly these, in this order: *Machinome*
(the title), *A machine's source*, *What the framework does*, *Install*,
*Documentation*, *Licence*, *Contributing*. The README SHALL be at most
1500 words, so that an addition is a trade for something already there.

The README SHALL NOT carry a release narrative: no heading SHALL name a
version, and no sentence SHALL state a version of Machinome or of its
former name. The current version, its date, what a release changed and the
lineage of the name SHALL stay in the changelog, the release notes, the
status page, the upgrading page and `HISTORY.rst`, which the README links.

The README SHALL contain at least one Python code block, and every Python
code block in it SHALL be the verbatim text, or a verbatim contiguous part,
of a module under `docs/tutorial/counter/` that the suite builds: a
chapter's module, or a module of the tutorial project declared as a model
for the README. The example SHALL place every moving part by a frame on a
frame, a mate stated in the assembly, and SHALL NOT place a part in
`render()`: no Python block of the README SHALL contain `translate(`, and
one SHALL state a mate with `.on(`.

The README shows and the manual teaches. The prose around the example
SHALL name each declaration of the block in one clause, in the same voice
for every one of them, SHALL define no term and SHALL state no mechanism;
the manual page that explains a thing is linked, not restated. A change to
the README SHALL edit the fact it changes, in place; it SHALL add no
section and no paragraph, and the README SHALL carry no account of a change
made to it, of why its text is as it is, or of the reasoning of whoever
changed it.

The repository's own landing page is the root `README.md`: it SHALL show
what the repository holds, one line for each package under `packages/`
linking its directory, and the licence every package carries, and SHALL
carry no version, no release narrative and no account of a change.

Guidance for contributors — the development environment, how to run the
tests and the spec-first discipline — SHALL live in `CONTRIBUTING.rst`,
which the README links; the README SHALL NOT restate it, and the layout of
the package SHALL stay in the contributor briefing.

#### Scenario: A reader lands on the README

- **WHEN** a reader who has never heard of Machinome opens the README on
  PyPI or in the framework's directory on GitHub
- **THEN** they read what Machinome is, see a machine's source as code the
  suite builds, and find the install line, the manual and the licence,
  without meeting a section named after a version

#### Scenario: A release passes

- **WHEN** a release moves the version, the date and the changelog
- **THEN** the README needs no edit, and a heading or a sentence naming a
  version of Machinome in it fails the documentation tests

#### Scenario: A section is added

- **WHEN** a change adds a section to the README, renames one or reorders
  them
- **THEN** the documentation tests fail naming the headings found

#### Scenario: The README grows

- **WHEN** a change leaves the README longer than 1500 words
- **THEN** the documentation tests fail naming the count

#### Scenario: An agent is asked to change the example

- **WHEN** a change replaces or corrects the README's example
- **THEN** the prose around it names the new declarations at the altitude
  of the others, the page keeps its sections and its size, and nothing in
  it says that the example was changed or why

#### Scenario: The example drifts from the tutorial

- **WHEN** a Python code block in the README is not the verbatim text of a
  tutorial module, or the README has no Python code block
- **THEN** the documentation tests fail naming the block

#### Scenario: The example places a part by hand

- **WHEN** a Python code block in the README places a part with
  `translate(`, or no block states a mate with `.on(`
- **THEN** the documentation tests fail naming the block

#### Scenario: A contributor looks for how to run the suite

- **WHEN** a contributor opens `CONTRIBUTING.rst`
- **THEN** it states the development install, how to run the tests and the
  lint, the browser-snapshot opt-in and the spec-first discipline, and
  points to the contributor briefing for the layout of the package

#### Scenario: A reader opens the repository

- **WHEN** a reader opens the repository's root on GitHub
- **THEN** the root `README.md` names each package under `packages/` with
  one line and a link to its directory, and states the licence, and the
  layout test fails if a package directory is not linked or the licence
  words differ from the manual's `framework_licence`

### Requirement: The 0.8.1 release is recorded

The release facts of Machinome 0.8.1 SHALL agree wherever they are
stated, by the same rules as 0.8.0's: the five version files hold the
version `pyproject.toml` states, and `docs/conf.py`'s release block states
the release date, 10 October 2026, the matching viewer 0.8.1, viewer API
29 and document versions 1 to 13. The `viewer` and `web-snapshot` extras
SHALL require the compatible release of `machinome-viewer` 0.8.1,
`~=0.8.1`, since the viewer joined the set (change `join-viewer`). The
changelog's first
release section SHALL be `Machinome 0.8.1`, dated `Released on
10/Oct/2026`, with no `Unreleased` section, opening with what a maker gets
and sending a reader to the upgrading page for the changes a project may
have to follow. `HISTORY.rst`'s top release entry SHALL be
`Machinome 0.8.1 (2026-10-10)`; work landed after it SHALL be recorded as
it lands in one `Unreleased` section above that entry, and the word SHALL
appear nowhere else above it. `docs/releases/release-0.8.rst` SHALL end
with a section naming 0.8.1 and dated 10 October 2026. `context7.json`
SHALL state 0.8.1, its date and the matching viewer 0.8.1, API 29. The
upgrading page SHALL open with a part for upgrading from 0.8.0 to 0.8.1,
above the 0.7 to 0.8 part, which stays intact.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.8.1, released on 10 October 2026, and the
  changelog's first release section is the 0.8.1 section

#### Scenario: Work lands after the release

- **WHEN** a change landed after 0.8.1 writes its entry in `HISTORY.rst`
- **THEN** the entry sits in one `Unreleased` section above
  `Machinome 0.8.1 (2026-10-10)`, the release's entry is unchanged, and a
  second `Unreleased` section, or the word anywhere else above the
  release's entry, fails the release-records test

#### Scenario: A 0.8.0 user upgrades

- **WHEN** a 0.8.0 user opens the upgrading page
- **THEN** its first part names each change since 0.8.0 a project may
  have to follow, with what to change

#### Scenario: A maker installs the viewer extra

- **WHEN** a maker installs `machinome[viewer]` 0.8.1
- **THEN** the requirement names `machinome-viewer~=0.8.1`, the viewer
  the manual declares as matching

### Requirement: A native FreeCAD assembly is documented as a how-to

The manual SHALL carry a how-to guide, `howto/freecad-assemblies`, listed in
the how-to section of the navigation, that tells a reader how to simulate a
native FreeCAD assembly: the install line `pip install "machinome[freecad]"`;
the FreeCAD runtime the package was measured with, FreeCAD 1.1.4 for Linux
x86-64, extracted from its official AppImage and named by
`MACHINOME_FREECAD_ROOT`, which no extra installs; that only trusted documents
may be opened, since FreeCAD runs the Python a document carries; the
declaration, with `FreeCADAssemblyNode`, `freecad_source` and `FreeCADJoint`
imported from `machinome.node.freecad`; how a source path resolves; selection
by native internal Name; what the adapter reads (native zero, enabled limits)
and what it refuses (the supported graph, the constraint tolerances, saved-pose
drift); and that a changed source needs a fresh model and a fresh `Sim`.

The installation page SHALL list `machinome[freecad]` with the distribution it
installs and say that FreeCAD itself is found through
`MACHINOME_FREECAD_ROOT`; the how-to guide on choosing a part backend SHALL list
`FreeCADAssemblyNode` with `machinome.node.freecad` and `machinome[freecad]`;
the API reference SHALL document `FreeCADAssemblyNode` and `FreeCADJoint`
under `machinome.node.freecad`. No page a reader is sent to SHALL spell the
module `machinome_freecad`, and none SHALL link the package's archived working
record.

#### Scenario: A reader with a FreeCAD assembly looks for the task

- **WHEN** a reader opens the how-to section of the navigation
- **THEN** it lists the FreeCAD guide, whose example imports
  `FreeCADAssemblyNode` and `FreeCADJoint` from `machinome.node.freecad` and
  which names `MACHINOME_FREECAD_ROOT` and FreeCAD 1.1.4

#### Scenario: A reader picks the FreeCAD extra

- **WHEN** a reader looks up what to install for `FreeCADAssemblyNode`
- **THEN** the installation page names `machinome[freecad]` and
  `machinome-node-freecad` and says that FreeCAD is found through
  `MACHINOME_FREECAD_ROOT`, and the backends guide lists the class with its
  module and that extra

#### Scenario: No page spells the former module

- **WHEN** every page of the manual and the framework's README are read
- **THEN** none spells `machinome_freecad`

### Requirement: The mechanics helpers are documented in the manual

The framework manual SHALL document the mechanics helpers, the package
`machinome.mechanics` of the distribution machinome-mechanics, installed by the
`mechanics` extra: a reference section, `reference/mechanics/`, listed in the
reference part of the navigation, whose index names the distribution, its
version through the `|mechanics_version|` substitution, its install line and
its import, and lists every helper, followed by a conventions page and one
page per formula family stating each helper's signature, frame, zero, sign and
domain with an example; and a how-to guide, `howto/mechanism-formulas`, listed
in the how-to part of the navigation, that installs the helpers, calculates a
pose and connects a helper to a driver through a relation law, explaining
resolved parameters, deferred symbolic inputs and the limit on dimensional
class-body formulas. The installation guide, the helper API reference, the
motion-law guidance and the sibling-manuals page SHALL link those pages
inside the manual. No page SHALL link a separate mechanics manual, and none
SHALL spell the module `machinome_mechanics` but the changelog and the
upgrading page, which record the rename and the 0.7 migration. Every example
of those pages that can run SHALL be run by the mechanics package's tests
against the installed framework, while the manual's own build SHALL import no
runtime package.

#### Scenario: Find a helper from the framework

- **WHEN** a framework user looks for a gear, screw, crank, delta or linkage helper
- **THEN** the manual's reference section lists "Mechanics helpers", whose
  pages give each helper's signature and conventions
- **AND** states that helpers are imported from `machinome.mechanics`

#### Scenario: Follow a motion-law or migration guide

- **WHEN** a reader wants to reuse a mechanical formula or migrate the former
  framework helper imports
- **THEN** they can follow a link inside the manual to the mechanics pages for
  examples and conventions without needing internal workflow records

#### Scenario: The helpers' examples run

- **WHEN** the mechanics package's tests run on a synced workspace
- **THEN** every `>>>` example of the mechanics reference pages and of the
  how-to guide runs against the installed helpers and framework with the
  examples' project on the path, and none fails

#### Scenario: No page sends a reader to the separate manual

- **WHEN** the manual's pages and the framework's README are read
- **THEN** none links `machinome-mechanics.readthedocs.io`, and only the
  changelog, which records the rename, and the upgrading page's 0.7 section
  spell `machinome_mechanics`

### Requirement: The browser viewer is documented in the manual

The framework manual SHALL document the browser viewer, the package of the
distribution machinome-viewer installed by the `viewer` extra: three how-to
guides listed in the how-to part of the navigation, `howto/browser-viewer`
(inspect and operate a posed, running or clocked machine), `howto/share-an-export`
(publish an export, link a presentation, take a still) and
`howto/embed-the-viewer` (a working host page, its source included, and the
layouts); and a reference section, `reference/viewer/`, listed in the
reference part of the navigation, whose index names the distribution, its
install line, the viewer API through `|viewer_api|` and the document versions
through `|document_versions|`, followed by the mount, the viewer handle, the
layouts, running and clocked machines, the `machinome-viewer` command,
compatibility and troubleshooting. Every public mount, option and handle
member of the widget SHALL have its entry in that section, and every option of
the command its line. The framework's viewer, embedding, sharing and
installation pages and the sibling-manuals page SHALL link those pages inside
the manual, and no page SHALL link a separate viewer manual.

#### Scenario: A maker needs to operate the viewer
- **WHEN** a maker reads the framework's viewer page
- **THEN** they can follow a link inside the manual to the guide to operating
  a machine in the viewer

#### Scenario: A host needs a browser API detail
- **WHEN** a host reads the framework's embedding page
- **THEN** they can follow a link inside the manual to the viewer's complete
  API reference and the working embedding example

#### Scenario: The viewer's reference is complete

- **WHEN** the widget's tests run from the repository
- **THEN** each public member of the viewer's handles and options and each
  mount of `MachinomeViewer` has its entry in the pages under
  `reference/viewer/`, and the viewer's tests find every option of the
  `machinome-viewer` command in its reference page and the `describe`
  example's version, API and document versions equal to the package's

#### Scenario: No page sends a reader to the separate viewer manual

- **WHEN** the manual's pages and the framework's README are read
- **THEN** none links `machinome-viewer.readthedocs.io`, and the release
  facts' viewer API and document versions equal the widget's declaration

