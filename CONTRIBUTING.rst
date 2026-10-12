============
Contributing
============

This project is in early stages. Our Discord server: https://discord.gg/7yd6rMCR

Bring a real mechanical use case: the design you are modelling, the
relationship you need to express, or a reproducible mismatch between the
model and the framework's behaviour. A small example and a failing test
make a useful starting point. A simulation of a published design belongs
in the `Machinome Foundry <https://github.com/machinome-foundry>`_, beside
its design, not in the framework.

This guide is for contributors, humans and coding agents alike, who modify
the framework in this repository. For *using* Machinome in your own
mechanical project, read the `user manual
<https://machinome.readthedocs.io/en/latest/>`_.

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/machinome/machinome/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Machinome could always use more documentation, whether as part of the
official Machinome docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/machinome/machinome/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Name the machine that needs it: a requirement begins as something a real
  project needs, and the change is validated in that project.

Development environment
-----------------------

Requirements: Python 3.11 or newer, as the framework's
``packages/machinome/pyproject.toml`` requires. Node.js 22 or newer and npm
build and test the two members of the repository's npm workspace, the
browser viewer's widget and the movie package's Node side, installed by one
``npm ci`` at the root, which ``make sync`` and ``make widget`` run, and
which installs each member's direct dependencies beside it, as the root's
``.npmrc`` says; ``machinome movie setup`` is for an installed copy of the
movie package, not for the checkout. The suite and the viewer's tests
photograph through the widget's built bundle, and the viewer's browser tests
need Chromium for the installed Playwright (``playwright install
chromium``, which ``make sync`` runs), as the movie's browser and pipeline
tests do, which need FFmpeg too. The repository's steps are the targets of
the ``Makefile`` at its root, run from there; ``make`` alone lists them. It
finds uv and npm on the PATH and the workspace's commands in ``.venv``, so no
target needs an activated environment. `OpenSCAD <https://openscad.org/>`_ is conditional: put it on the
PATH when working on SolidPython2/Solid2 or raw OpenSCAD nodes, or the
default OpenSCAD snapshot renderer. All-B-rep projects, CadQuery, build123d
or the two mixed, build, test and export without it; use ``machinome
snapshot --renderer web`` for snapshots on a machine without OpenSCAD.

`manifold3d <https://pypi.org/project/manifold3d/>`_, the mesh engine's
kernel, is the ``mesh`` extra (``pip install "machinome[mesh]"``, included
in ``all``) and is conditional in the same sense: it decides mesh geometry,
so it is needed whenever an assertion compares a part that has no B-rep
geometry, by ``machinome test --mesh``, and by
``assertAssemblySupported``, whose statics phase reads contact patches off
meshed intersections for every body. An all-B-rep project's other
geometric assertions are decided by the B-rep engine and run without it,
which is useful on a platform with no compiled wheel, such as WebAssembly.
A path that needs it and cannot import it says so by name, naming the
extra.

Clone the repository (the tutorial's machine under
``packages/machinome/docs/tutorial/`` is built and tested by the suite; the
real machines the manual points to are on machinome.org, not in this
repository)::

    $ git clone https://github.com/machinome/machinome.git
    $ cd machinome

From the clone's root, ``make sync`` installs the workspace from its locks:
``uv sync --python 3.12``, which installs every package under ``packages/``
editable, the framework with its dev dependencies, every kernel the suite
runs, into ``.venv``; ``npm ci``, the npm workspace's dependencies; and the
Chromium the installed Playwright uses::

    $ make sync

or, without uv, create a virtualenv and install every package under
``packages/`` editable in compat mode, the framework with its dev
dependencies::

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install --config-settings editable_mode=compat \
        -e packages/machinome-engine-brep -e packages/machinome-engine-mesh \
        -e packages/machinome-node-cadquery -e packages/machinome-node-build123d \
        -e packages/machinome-node-step -e packages/machinome-node-molejo \
        -e packages/machinome-node-openscad -e packages/machinome-node-solid2 \
        -e packages/machinome-node-jscad -e packages/machinome-node-stl \
        -e packages/machinome-node-freecad \
        -e packages/machinome-viewer \
        -e packages/machinome-mechanics \
        -e packages/machinome-skills \
        -e packages/machinome-movie \
        -e "packages/machinome[dev]"

The ``machinome`` CLI entrypoint (``packages/machinome/machinome/cli.py``) is
now on the PATH of the virtualenv. Install the npm workspace's dependencies
and build its bundles from the clone's root (``make sync`` installs the
dependencies and builds no bundle)::

    $ make widget        # npm ci, then every member's bundle

For the layout of the package, and for how to choose between direct pytest
coverage and the meta-project harness when proving a change, read the
`contributor briefing <packages/machinome/docs/contributor-briefing.md>`_.

Running tests
-------------

``make test`` runs the tests of every package that keeps tests of its own,
one after another, stopping at the first that fails; ``make test
PKG=<package>`` runs one package's. From the clone's root::

    $ make test                  # every package with tests
    $ make test PKG=machinome    # the framework's suite
    $ make lint                  # black --check and flake8, as CI runs them
    $ make docs                  # the manual, warnings as errors

``make test PKG=machinome`` builds the viewer's bundle, which the suite
photographs through, then runs pytest from the framework's directory,
``packages/machinome``, where pytest runs a single file and the
``openspec`` command runs::

    $ cd packages/machinome
    $ pytest tests/test_builder_lifecycle.py   # a single file

The extension packages keep no tests of their own: the framework's suite
tests them, and ``make test PKG=machinome-engine-brep`` says so.

The mechanics helpers keep their tests in their own directory: ``make test
PKG=machinome-mechanics`` runs ``python -m pytest`` from
``packages/machinome-mechanics``. The browser viewer keeps its tests in its
own directory: ``make test PKG=machinome-viewer`` runs its widget's type
check, tests and build from the root, by ``--workspace
packages/machinome-viewer/machinome/viewer/web/widget``, then ``python -m
pytest`` from ``packages/machinome-viewer``. The skills package keeps its
tests in its own directory too: ``make test PKG=machinome-skills`` runs
``python -m pytest`` from ``packages/machinome-skills``. The movie package
keeps its tests in its own directory: ``make test PKG=machinome-movie`` runs
``python -m pytest`` from ``packages/machinome-movie``, then its Node suite's
``pure`` and ``stage`` projects, which open no browser, as CI does; its whole
Node suite is ``npm test --workspace
packages/machinome-movie/machinome/movie/js`` from the root, after ``npm
ci`` there; the browser and pipeline tests need Chromium and FFmpeg.

``make check`` builds every package's sdist and wheel from the tree and from
a clean copy of its tracked files, checks, installs and smokes them outside
the repository, and keeps nothing: run it before a pull request that
touches packaging. ``make clean`` removes what the targets wrote (the docs
environment ``.docs-venv``, the manual's build, the packages' build scratch,
the widget's bundle), never ``.venv``, an npm install or ``dist/``.

Notes:

* Rendering tests invoke the real ``openscad`` binary. On a headless machine,
  snapshot-related tests may need ``xvfb-run -a pytest ...``.
* Browser-snapshot tests are mandatory for changes to that renderer. The
  workspace installs the viewer with its ``snapshot`` extra; build its
  bundle (``make widget``), install Chromium and run the real capture
  explicitly, from ``packages/machinome``::

      $ playwright install chromium
      $ MACHINOME_WEB_SNAPSHOT_E2E=1 pytest tests/test_browser_renderer.py::BrowserSnapshotEndToEndTest

  The ordinary suite leaves this environment variable unset and skips the
  capture, even when the viewer is installed. With the opt-in set, a missing
  viewer or browser is a setup failure. The dedicated CI browser-snapshot job
  installs both dependencies, sets the opt-in, and runs this same test.
* ``tests/meta_project/`` together with ``tests/test_meta.py`` is the
  end-to-end meta-project harness: it runs small real machinome projects,
  both deliberately green and deliberately red fixtures, to prove the
  loading, rendering, and ``machinome test`` subprocess paths. Use it when a
  change touches behavior that direct unit tests cannot establish; the
  `contributor briefing <packages/machinome/docs/contributor-briefing.md>`_
  says when and why.
* ``tools/generate_parity_fixture.py`` produces, from this framework's
  render results, the parity fixture the viewer's widget commits beside its
  expression evaluator.

Development discipline
----------------------

This repository is developed agentically and follows a strict spec-first
discipline. **Every behavioral change starts as an OpenSpec change proposal
and is ratified before implementation.** Drive-by edits, unrecorded
redesigns, and "fix it first, document it later" are not how this project
moves; this applies equally to human contributors and to coding agents
operating autonomously.

OpenSpec changes
~~~~~~~~~~~~~~~~

Behavioral contracts live in ``openspec/specs/``. Changes are proposed,
reviewed, implemented, and archived through the OpenSpec workflow
(`OpenSpec <https://openspec.ai>`_, CLI v1.x; the repo's
``openspec/config.yaml`` carries project context and rules):

1. **Propose**: create a change under ``openspec/changes/<name>/`` with
   ``proposal.md`` (why, what changes, capabilities, impact), ``design.md``
   (how), and ``tasks.md`` (implementation steps). The change describes
   *deltas* against the current specs.
2. **Review**: the proposal is inspected and refined before any code is
   written. Specs describe observable behavior only; no aspirational
   requirements.
3. **Apply**: implement the ratified proposal, task by task, TDD-style:
   red evidence first (a failing test that pins the contract), then the
   smallest change that satisfies it.
4. **Archive**: when the change lands, its spec deltas are merged into
   ``openspec/specs/`` and the change moves to ``openspec/changes/archive/``.

The proposal and completed record belong in the framework's
``packages/machinome/openspec/`` directory, where the ``openspec`` command
runs.

Architecture Decision Records
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Why* the system is the way it is lives in ``docs/adrs/`` (see
`docs/adrs/README.md <packages/machinome/docs/adrs/README.md>`_ for the
index and the full discipline):

* One decision per ADR, numbered sequentially, filed under the subsystem it
  affects (NODE, BUILD, IPC, MATH, TEST-FRAMEWORK, VIEWER-WEB, EXPORT).
* Statuses flow ``Proposed`` → ``Accepted``; later ADRs may mark earlier ones
  ``Superseded``. Superseded ADRs stay in the log: they are the history that
  makes current decisions legible.
* When an OpenSpec change carries an architectural shift, its ADR is written
  alongside the change and the architecture synthesis
  (`docs/architecture.md <packages/machinome/docs/architecture.md>`_) is
  updated as part of landing it.

Read order for orientation: **architecture synthesis first**
(``docs/architecture.md``), **then the specs** for exact observable behavior
(``openspec/specs/``), **then an ADR** when you need to know why
(``docs/adrs/``). The contributor briefing
(`docs/contributor-briefing.md
<packages/machinome/docs/contributor-briefing.md>`_) adds verification
guidance: how to choose between direct pytest coverage and the meta-project
harness, and the red-first evidence principle.

Pull requests
-------------

1. Fork the repository on GitHub and clone your fork; create a branch for
   the change.
2. Make the change under the discipline above, with the test that proves
   the failure before the change turns it green.
3. Update the documentation the change touches: the manual under
   ``packages/machinome/docs/``, and the changelog's ``Unreleased`` section
   for anything a project can use, in the same change.
4. Check that the lint and the tests pass (``make lint``, ``make test``);
   `GitHub Actions <https://github.com/machinome/machinome/actions>`_ runs
   the suite on every supported Python version.
5. Push the branch to your fork and open a pull request.

Deploying
---------

A reminder for the maintainers on how to release the set. Every step is a
target run from the root, and no target uploads what another built:

1. ``make bump VERSION=X.Y.Z`` moves the set's version, declared once as
   ``current_version`` of ``.bumpversion.cfg`` (``make version`` prints it),
   into every copy the configuration names, every pin between the packages
   among them, the root's npm lock and each npm member's own lock, and
   ``uv.lock``, and lists the files it changed. It refuses a tree whose
   tracked files have changes, and it never commits and never tags.
2. Write the release's records (``HISTORY.rst``, the manual's changelog and
   release note) and commit.
3. ``make dist`` builds every package's sdist and wheel from that commit, in
   a copy outside the checkout, checks, installs and smokes them, and keeps
   them in ``dist/vX.Y.Z``. It refuses a checkout that differs from its
   commit and a folder that already holds archives. Read the folder.
4. Tag the commit ``vX.Y.Z`` and push the branch and the tag: GitHub
   Actions runs the tests, builds the archives from the tag with ``make
   dist`` and attaches them to the tag's GitHub release.
5. ``make upload`` uploads ``dist/vX.Y.Z`` to PyPI with twine, and nothing
   else.
