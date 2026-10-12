## MODIFIED Requirements

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists:
Sphinx, its theme and the published `machinome-viewer` package, which
completes the committed exports with its widget. The Read the Docs
configuration and the CI docs job, through the root Makefile's `docs`
target, SHALL both install that file and run Sphinx, and neither SHALL run `machinome export`, install a system package,
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
`.github/workflows/python-app.yml`, SHALL run `make docs` at the repository
root, whose recipe installs `packages/machinome/docs/requirements.txt` alone
into an environment of its own, `.docs-venv/` at the root, and builds `docs`
from the package directory into `docs/_build/html`.

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

- **WHEN** the Read the Docs configuration, the CI docs job or the
  Makefile's `docs` target gains an export command, a repository install, an apt package, a Node tool or a
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

- **WHEN** the manual is built from `docs/requirements.txt` and the guide to
  embedding the viewer is opened in a browser
- **THEN** its example loads the committed spinner export with the installed
  viewer's bundle, both copied beside the page by the build, and the
  framework's lookup answers the installed viewer even though the
  repository's viewer source lies beside the framework's directory
