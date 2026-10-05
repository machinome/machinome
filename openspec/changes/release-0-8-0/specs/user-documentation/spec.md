## ADDED Requirements

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

From 0.8.0 the framework's licence SHALL be stated as GPL-2.0-or-later
or CERN-OHL-S-2.0-or-later, at the recipient's choice, as the current
fact and nothing more: no page or record SHALL name an earlier licence of
the framework or compare with one, or state a position on derivative
works, an exception, a compatibility claim or a reason. Every manual page that states the
framework's licence SHALL use `|framework_licence|`, the only way the
framework's licence reaches a page. No `.rst` page under `docs/` other
than the historical release notes under `docs/releases/` SHALL spell a
licence identifier literally, the one exception being the viewer's
`AGPL-3.0-or-later`; `README.rst` SHALL spell no licence identifier but
`AGPL-3.0-or-later` and the exact words of `docs/conf.py`'s
`framework_licence`, which it SHALL state. The changelog SHALL read as if
it had never carried another licence. The browser viewer SHALL still be
stated as the separate AGPL-3.0-or-later package.

The changelog's first release section SHALL be `Machinome 0.8.0`, dated
`Released on 05/Oct/2026`, with no `Unreleased` section; it SHALL open
with what a maker gets, state the licence first, and list every breaking
change of 0.8 in one line each with a link to the upgrading page.
`HISTORY.rst`'s top entry SHALL be `Machinome 0.8.0 (2026-10-05)`.
`docs/releases/release-0.8.rst` SHALL be the release note, dated, reached
from the changelog. The status page SHALL describe 0.8.0 as released and
describe no work as unreleased. `context7.json` SHALL state 0.8.0, its
date and the matching viewer's version and API as `docs/conf.py` states
them. The upgrading page SHALL open with a part for upgrading from 0.7 to
0.8 that lists every breaking change of 0.8 and, for each, what to
change, above the 0.6 to 0.7 material, which stays intact; no section of
it SHALL be marked unreleased or speak of "the next release".

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.8.0, released on 5 October 2026, and the
  changelog's first release section is the 0.8.0 section

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
  `docs/conf.py`, and the viewer as a separate AGPL-3.0-or-later package

#### Scenario: A page spells a licence literally

- **WHEN** a page under `docs/` other than a historical release note
  spells a licence identifier other than the viewer's, or the README
  spells one other than the viewer's and the framework's current words
- **THEN** the documentation tests fail naming the page

#### Scenario: A 0.7 user upgrades

- **WHEN** a 0.7 user opens the upgrading page
- **THEN** its first part lists every breaking change of 0.8, the
  install's extras, the import paths, the engines' names, the OpenSCAD
  family, a node's shape, the leaf contract, the symbolic value and the
  removed modules among them, each with what to change

#### Scenario: A reader follows the release note

- **WHEN** a reader opens the changelog
- **THEN** its table of contents reaches the 0.8 release note, which is
  dated 5 October 2026 and sends the reader to the upgrading page

## MODIFIED Requirements

### Requirement: The viewer's provenance and installation are stated

Every documentation page that installs, opens, embeds or photographs through
the browser viewer SHALL state that the viewer is the separate
`machinome-viewer` package, licensed AGPL-3.0-or-later, installed with
`pip install "machinome[viewer]"`. It SHALL state that interactive
`machinome develop` requires that package, while a plain framework installation
can build, test, export without the widget, run `machinome develop --no-web`, and
snapshot through OpenSCAD with the `openscad` extra. Web-viewer operations SHALL name the extra as their
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
