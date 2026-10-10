## Context

The manual embeds models two ways. The tutorial's six models are committed
exports under `docs/_exports/`, made with `--no-widget`; the Sphinx extension
completes them at build time from the installed `machinome-viewer` package.
The three example machines were exported during the documentation build
from Foundry submodules under `docs/examples/`, which needed the CAD stack,
OpenSCAD, Node (the viewer installed from its repository builds its widget),
the mechanics package and, for the Pascaline, a download. The Read the Docs
build of the `v0.7.0` tag ran 901 s and was cut off inside the third export.

## Decisions

**D1. The examples leave the manual; the page stays and points at the site.**
`examples.rst` keeps its place in the navigation (the structure test pins the
section order, and a reader looking for a real machine still needs a place to
look) and sends the reader to the Foundry on machinome.org, whose pages show
each machine live in the browser beside its design, credits and licences. The
page describes what a reader finds by kind and execution model rather than
deep-linking three project pages: the site owns its roster and its URLs (the
Pascaline module is held there at the time of writing), and the manual links
only to a landing page it can rely on. The GitHub organisation stays
mentioned where the manual talks about source.

**D2. The documentation build installs `docs/requirements.txt` and nothing
else.** A build of the unchanged manual in a fresh virtualenv holding only
Sphinx, `sphinx_rtd_theme` and a `machinome-viewer` 0.7.0 wheel, with `OCP`
added to the mocked imports, produced only the three example-export errors.
So the runtime requirements, the editable install of the framework, the
mechanics package, OpenSCAD and Node all go. `conf.py` reaches the framework
through `sys.path` for autodoc, as it already did.

**D3. The viewer comes from PyPI.** `docs/requirements.txt` lists
`machinome-viewer` unpinned, like the framework's `viewer` extra: the manual
builds against what a reader installs, and any later viewer renders the
document versions the committed exports declare. This replaces the install
from the viewer's repository, which needed Node to build the widget. The
consequence for this release is an order: the viewer is uploaded to PyPI
before the framework's `main` and tag are pushed, or the Read the Docs build
and the CI docs job fail at `pip install` until it is, and are rerun after.

**D4. One rule, pinned by the suite.** `tests/test_docs_exports.py` no longer
reconciles three files that each named exports to build; it requires every
`.. machinome::` directive to name a committed export and both build
configurations to generate nothing: no `export` command, no `pre_build` job,
no apt package, no Node tool, no submodule checkout, no install from a
repository URL, and both installing `docs/requirements.txt`. The GitHub job
keeps building with `-W`.

**D5. Names stay where they teach.** Concept pages that use a Curta's carry
or a printer's belts as analogies keep them; the changelog and release note
keep naming what the release grew on. Pages that linked to an example page
now say what kind of machine the site shows.

**D6. The 0.7.0 record is rewritten, not amended.** The tag is re-cut on the
integrated head, so the 0.7.0 changelog bullet and the release note describe
the manual as it ships: the tutorial's machine in the manual, the real
machines on machinome.org. No `Unreleased` section is opened.

## Risks

- Until `machinome-viewer` 0.7.0 is on PyPI, every documentation build fails
  at the install. Recorded in the release checklist as an ordering step.
- machinome.org hosts the framework manual built from a commit with supplied
  submodule inputs; the next intake runs without inputs and must be redone
  from the new commit, or the site keeps showing the old example pages.
