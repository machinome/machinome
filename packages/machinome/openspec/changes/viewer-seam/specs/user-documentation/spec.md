## MODIFIED Requirements

### Requirement: The viewer's provenance and installation are stated

Every documentation page that installs, opens, embeds or photographs through
the browser viewer SHALL state that the viewer is the package
`machinome-viewer` of the Machinome repository, released and licensed with
the framework, installed with `pip install "machinome[viewer]"` and reached
through the framework's seam of viewers as the viewer named `web`, in the
framework's own process. It SHALL state that interactive
`machinome develop` requires that package, while a plain framework installation
can build, test, export without the widget, run `machinome develop --no-web`, and
take a still through the OpenSCAD viewer with the `openscad` or
`viewer-openscad` extra. Web-viewer operations SHALL name the extra as their
remedy. No page SHALL describe the viewer as licensed differently from the
framework, as found through an entry point, or as run as a separate process.
Building the viewer's widget from source with Node and npm SHALL be the
contributor guide's, not a reader page's.

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
- **THEN** the documentation says those node types and the OpenSCAD viewer of
  `machinome snapshot`, which takes a still and does not serve, remain
  supported, without calling OpenSCAD an interactive machinome viewer

#### Scenario: A contributor looks for the viewer source

- **WHEN** a contributor reads the viewer or contributing pages
- **THEN** they are pointed at the viewer's directory of the repository,
  `packages/machinome-viewer/`, and at the contributor guide for the Node
  setup, and no reader page tells them to run npm

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists,
Sphinx and its theme, and the repository's own browser viewer with its bundle
built: the manual's configuration SHALL put the viewer's directory of the
repository on its path with the framework's and the other packages', and the
widget's bundle SHALL be built with npm from the root's lock before Sphinx
runs, because the framework finds the viewer through its seam at
`machinome.viewer.web` and a published viewer is hidden behind the framework's
source directory. The Read the Docs configuration and the CI docs job, through
the root Makefile's `docs` target, SHALL both install that file, build the
bundle and run Sphinx; Node SHALL be the one tool either installs beyond
Python, and neither SHALL run `machinome export`, install a system package or
a package from a repository URL, or check out a submodule. Every export a page
embeds SHALL be committed under `docs/_exports/`. The guide to embedding the
viewer SHALL show its working host page from the built manual: the build SHALL
copy the page, the committed export it loads and the bundle the web viewer
names beside the guide.

The Read the Docs configuration SHALL sit beside the manual, at
`packages/machinome/.readthedocs.yaml`, and SHALL name the requirements
file and the Sphinx configuration by their paths from the repository
root, `packages/machinome/docs/requirements.txt` and
`packages/machinome/docs/conf.py`, since Read the Docs reads every path in
it from there; its one build job SHALL install the npm workspace from the
root's lock and build the viewer's widget. The CI docs job, in the
repository's workflow at `.github/workflows/python-app.yml`, SHALL install
Node and run `make docs` at the repository root, whose recipe builds the
viewer's bundle, installs `packages/machinome/docs/requirements.txt` alone
into an environment of its own, `.docs-venv/` at the root, and builds `docs`
from the package directory into `docs/_build/html`.

Both builds SHALL treat warnings as errors, and the manual's Sphinx
configuration SHALL make every build nitpicky, so that a cross-reference
whose target the manual does not document, written in a page or in a
docstring the manual renders, fails the build that Read the Docs and the
CI docs job run.

#### Scenario: Read the Docs builds the manual

- **WHEN** Read the Docs builds any version of the manual
- **THEN** its configuration names Node 22, one job that installs the npm
  workspace and builds the viewer's widget, no apt package, and installs
  `packages/machinome/docs/requirements.txt` alone

#### Scenario: A page embeds an export nobody committed

- **WHEN** a `.. machinome::` directive names a directory outside
  `docs/_exports/`
- **THEN** the suite fails naming the page, before any documentation build

#### Scenario: A build configuration grows a build step

- **WHEN** the Read the Docs configuration, the CI docs job or the
  Makefile's `docs` target gains an export command, a repository install, an
  apt package, a Node step other than building the viewer's widget from the
  root's lock, or a submodule checkout
- **THEN** the suite fails naming the file and the step

#### Scenario: The manual builds from the requirements alone

- **WHEN** a fresh environment installs `docs/requirements.txt`, the viewer's
  bundle is built, and the manual is built with warnings as errors
- **THEN** the build succeeds and every tutorial page shows its committed
  export with the viewer's widget

#### Scenario: A reference names nothing the manual documents

- **WHEN** a page or a rendered docstring cross-references a target the
  manual does not document, such as a class named without its module
  where the current module does not hold it, or a docstring line napoleon
  reads as a type
- **THEN** the build the CI docs job runs through `make docs`, `python -m
  sphinx -b html -W -E docs docs/_build/html`, fails naming the reference,
  with no `-n` on its command line,
  and the suite fails if the manual's configuration stops being nitpicky

#### Scenario: The configuration names the manual from the repository root

- **WHEN** the suite reads `packages/machinome/.readthedocs.yaml`
- **THEN** its one install entry is the requirements file
  `packages/machinome/docs/requirements.txt` and its Sphinx configuration
  is `packages/machinome/docs/conf.py`, and the suite fails naming the path
  if either names the manual from the package directory instead

#### Scenario: The embedding guide's host page runs from the built manual

- **WHEN** the manual is built and the guide to embedding the viewer is
  opened in a browser
- **THEN** its example loads the committed spinner export with the bundle the
  web viewer names, both copied beside the page by the build

#### Scenario: The manual without a built bundle

- **WHEN** the manual is built with warnings as errors and the viewer's
  bundle has not been built
- **THEN** the build fails with the warning naming the missing bundle and how
  to build it

## ADDED Requirements

### Requirement: The viewers are documented as chosen by name

The manual SHALL document the two viewers and how a command chooses one: the
reference of `machinome snapshot`, `machinome develop` and `machinome export`
SHALL name `--viewer` and its default, and say that `--renderer` is refused
naming it; a how-to SHALL show a still through each viewer, the options each
honours, and the project's `viewer` key under `[tool.machinome]`; the
installation page SHALL list the `viewer-openscad` extra and say that the
`openscad` and `solid2` extras install the OpenSCAD viewer; the upgrading page
SHALL hold a section for Machinome 0.8 to 0.9 that says `--renderer` is
`--viewer`, names the project key, the `viewer-openscad` extra, and the
removed entry point with `machinome viewer` as what a host reads instead. No
current page SHALL spell `--renderer` but to say it is refused, and the
released records SHALL keep what they said.

#### Scenario: A reader takes a transparent still

- **WHEN** a reader follows the tutorial's "Photograph" section
- **THEN** its commands spell `--viewer web` and run as written

#### Scenario: A reader upgrading from 0.8

- **WHEN** a reader opens the upgrading page
- **THEN** its 0.9 section names `--viewer` in place of `--renderer`, the
  project's `viewer` key and the `viewer-openscad` extra

#### Scenario: A current page spells the former flag

- **WHEN** a current page of the manual, outside the release records and the
  changelog's released sections, spells `--renderer` other than to say it is
  refused
- **THEN** the suite fails naming the page
