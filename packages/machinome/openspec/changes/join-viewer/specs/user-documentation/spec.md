## RENAMED Requirements

- FROM: `### Requirement: Viewer users can reach the independent viewer manual`
- TO: `### Requirement: The browser viewer is documented in the manual`

## MODIFIED Requirements

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
