============
Contributing
============

This project is in early stages. Our Discord server: https://discord.gg/7yd6rMCR

Bring a real mechanical use case: the design you are modelling, the
relationship you need to express, or a reproducible mismatch between the
model and the framework's behaviour. A small example and a failing test
make a useful starting point. A simulation of a published design belongs
in the `Machinome Foundry <https://github.com/machinome-foundry>`_, beside
its design, not in the framework; browser-viewer changes belong to the
separate `machinome-viewer <https://github.com/machinome/machinome-viewer>`_
repository.

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

Requirements: Python 3.11 or newer, as ``pyproject.toml`` requires. Node.js
is not needed: the browser viewer and its widget live in the separate
`machinome-viewer <https://github.com/machinome/machinome-viewer>`_
repository, and the tests that need a viewer skip unless that package is
installed. `OpenSCAD <https://openscad.org/>`_ is conditional: put it on the
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

Clone the repository (the tutorial's machine under ``docs/tutorial/`` is
built and tested by the suite; the real machines the manual points to are
on machinome.org, not in this repository)::

    $ git clone https://github.com/machinome/machinome.git
    $ cd machinome

Create a virtualenv and install the package in editable mode with the dev
dependencies, which bring every kernel the suite runs::

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e ".[dev]"

The ``machinome`` CLI entrypoint (``machinome/cli.py``) is now on the PATH of
the virtualenv.

For the layout of the package, and for how to choose between direct pytest
coverage and the meta-project harness when proving a change, read the
`contributor briefing <docs/contributor-briefing.md>`_.

Running tests
-------------

The test suite is pytest, run from the repository root::

    $ make test          # equivalent to: pytest
    $ pytest tests/test_builder_lifecycle.py   # a single file
    $ make lint          # flake8 + black --check
    $ make test-all      # tox across supported Python versions

Notes:

* Rendering tests invoke the real ``openscad`` binary. On a headless machine,
  snapshot-related tests may need ``xvfb-run -a pytest ...``.
* Browser-snapshot tests are mandatory for changes to that renderer. Install
  a matching viewer with its ``snapshot`` extra, then install Chromium and
  run the real capture explicitly::

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
  `contributor briefing <docs/contributor-briefing.md>`_ says when and why.
* The browser viewer's own tests live in the ``machinome-viewer``
  repository. ``tools/generate_parity_fixture.py`` produces, from this
  framework's render results, the parity fixture that repository commits
  beside its expression evaluator.

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

The proposal and completed record belong in this repository's
``openspec/`` directory.

Architecture Decision Records
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Why* the system is the way it is lives in ``docs/adrs/`` (see
`docs/adrs/README.md <docs/adrs/README.md>`_ for the index and the full
discipline):

* One decision per ADR, numbered sequentially, filed under the subsystem it
  affects (NODE, BUILD, IPC, MATH, TEST-FRAMEWORK, VIEWER-WEB, EXPORT).
* Statuses flow ``Proposed`` → ``Accepted``; later ADRs may mark earlier ones
  ``Superseded``. Superseded ADRs stay in the log: they are the history that
  makes current decisions legible.
* When an OpenSpec change carries an architectural shift, its ADR is written
  alongside the change and the architecture synthesis
  (`docs/architecture.md <docs/architecture.md>`_) is updated as part of
  landing it.

Read order for orientation: **architecture synthesis first**
(``docs/architecture.md``), **then the specs** for exact observable behavior
(``openspec/specs/``), **then an ADR** when you need to know why
(``docs/adrs/``). The contributor briefing
(`docs/contributor-briefing.md <docs/contributor-briefing.md>`_) adds
verification guidance: how to choose between direct pytest coverage and the
meta-project harness, and the red-first evidence principle.

Pull requests
-------------

1. Fork the repository on GitHub and clone your fork; create a branch for
   the change.
2. Make the change under the discipline above, with the test that proves
   the failure before the change turns it green.
3. Update the documentation the change touches: the manual under
   ``docs/``, and the changelog's ``Unreleased`` section for anything a
   project can use, in the same change.
4. Check that the lint and the tests pass (``make lint``, ``make test``);
   `GitHub Actions <https://github.com/machinome/machinome/actions>`_ runs
   the suite on every supported Python version.
5. Push the branch to your fork and open a pull request.

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

GitHub Actions will then run the test suite; publish to PyPI with
``make release`` (``twine upload dist/*``).
