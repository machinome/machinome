=========
Machinome
=========

**Source code for machines**

.. image:: https://github.com/machinome/machinome/actions/workflows/python-app.yml/badge.svg?branch=main
   :target: https://github.com/machinome/machinome/actions/workflows/python-app.yml
   :alt: Build status

.. image:: https://img.shields.io/pypi/v/machinome.svg
   :target: https://pypi.org/project/machinome/
   :alt: PyPI version

.. image:: https://readthedocs.org/projects/machinome/badge/?version=latest
   :target: https://machinome.readthedocs.io/en/latest/
   :alt: Documentation status

Machinome is a Python framework for giving a machine source code.
Describe its parts, the dimensions they share, how they fit together,
what moves, and the relationships that make the whole machine work.
Its geometry, operating behaviour and tests belong to the same project.

A gear ratio connects the gears you see to the movement you test.
An input moves the parts it drives. A spring follows the mechanism
that compresses it. A calculator remembers its digits when the crank
returns to rest. These relationships are explicit in the machine's
source, where they can be inspected, changed and tested.

Supply parts using CadQuery, build123d, OpenSCAD/SolidPython or JSCAD;
reuse STEP and STL designs; derive sheet parts from cutting profiles;
and describe flexible springs, belts and cables with
`molejo <https://molejo.readthedocs.io>`_.
Machinome binds the pieces together through assemblies, shared parameters,
joints, laws, inputs and stored state. Incremental builds give feedback
as you edit. The optional browser viewer lets people operate and explore
the machine, including from an exported static web page.

Machinome is developed empirically from mechanical projects, with
AI-assisted design and implementation. The
`Machinome Foundry <https://github.com/machinome-foundry>`_ organisation
holds simulations of open-source machines built with it, each beside the
design it simulates; the framework, viewer and mechanics packages live
under `machinome <https://github.com/machinome>`_. Simulation and geometric tests
provide evidence about those models; they do not establish that every
design has been manufactured or physically validated.

Version 0.7 and the new name
============================

Machinome 0.7 is the direct continuation of **solid-node 0.6.0**.
The framework and GitHub organisation were renamed to avoid confusion
with Tim Berners-Lee's Solid project: `solid-node` sounded like a Solid
node, and `LibreSolid` like a libre edition of Solid. Machinome has no
affiliation with that project.

Install it with the browser viewer and start a project:

.. code-block:: bash

   pip install "machinome[viewer]"
   machinome new myproject
   cd myproject
   machinome develop

The default template uses SolidPython and needs the OpenSCAD executable;
the manual's first page replaces it with an exact part that needs
nothing else. The
`migration guide <https://machinome.readthedocs.io/en/latest/project/upgrading.html>`_
maps imports, commands, configuration and viewer integration from 0.6.
There is no ``solid_node`` import shim or ``solid`` command alias.

Learn it one machine at a time
==============================

The `tutorial <https://machinome.readthedocs.io/en/latest/tutorial/01-part.html>`_
builds a hand-cranked tally counter from a part to a machine with memory:
an input moving a body through a joint, shared dimensions, relations and
laws, buttons, fit tests proved red first, a stepped scenario, a running
machine with a ratchet, and retained digits written at events.

Real machines built with Machinome, posed, running and clocked, are shown
live on `machinome.org <https://machinome.org/>`_, each beside its design
source and licence.

* `User manual <https://machinome.readthedocs.io/en/latest/>`_
* `0.7 release notes <https://machinome.readthedocs.io/en/latest/releases/release-0.7.html>`_
* `Source repository <https://github.com/machinome/machinome>`_

The framework is **Apache-2.0**. The optional
`Machinome Viewer <https://github.com/machinome/machinome-viewer>`_
is **AGPL-3.0-or-later**, installed through ``viewer``.
Ordinary ``machinome develop`` requires it. Without it, the framework
builds, tests, exports with ``--no-widget``, watches with
``develop --no-web``, and takes fixed-pose OpenSCAD snapshots.

The ``mechanics`` extra installs the independent
``machinome-mechanics`` helpers. The ``studio`` extra is reserved for
Machinome Studio, an experimental, unpublished harness; it cannot yet
resolve from a package index.

Working on Machinome itself
============================

This section is for contributors — humans and coding agents — who modify the
framework in this repository. For *using* machinome in your own mechanical
project, see the documentation above.

Development environment
-----------------------

Requirements: Python >= 3.11. Node.js is not needed: the browser viewer and
its widget live in the separate `machinome-viewer
<https://github.com/machinome/machinome-viewer>`_ repository, and the tests
that need a viewer skip unless that package is installed. `OpenSCAD
<https://openscad.org/>`_ is conditional: put it on the PATH when working on
SolidPython2/Solid2 or raw OpenSCAD nodes, or the default OpenSCAD snapshot
renderer. All-exact projects — CadQuery,
build123d, or the two mixed — build, test, and export without it; use
``machinome snapshot --renderer web`` for snapshots on a machine without OpenSCAD.

`manifold3d <https://pypi.org/project/manifold3d/>`_ is installed by default
and is conditional in the same sense: it decides faceted geometry, so it is
needed whenever an assertion compares a part that has no exact geometry, and
by ``assertAssemblySupported``, whose statics phase reads contact patches off
meshed intersections for every body. An all-exact project's other geometric
assertions are decided by the OCCT kernel and run without it — useful on a
platform with no compiled wheel, such as WebAssembly. A path that needs it
and cannot import it says so by name.

Clone the repository (the tutorial's machine under ``docs/tutorial/`` is
built and tested by the suite; the real machines the manual points to are
on machinome.org, not in this repository):

.. code-block:: bash

    $ git clone https://github.com/machinome/machinome.git
    $ cd machinome

Create a virtualenv and install the package in editable mode with the dev
dependencies:

.. code-block:: bash

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e ".[dev]"

The ``machinome`` CLI entrypoint (``machinome/cli.py``) is now on the PATH of
the virtualenv.

Running tests
-------------

The test suite is pytest, run from the repository root:

.. code-block:: bash

    $ make test          # equivalent to: pytest
    $ pytest tests/test_builder_lifecycle.py   # a single file
    $ make lint          # flake8 + black --check
    $ make test-all      # tox across supported Python versions

Notes:

* Rendering tests invoke the real ``openscad`` binary. On a headless machine,
  snapshot-related tests may need ``xvfb-run -a pytest ...``.
* Browser-snapshot tests are mandatory for changes to that renderer. Install
  a matching viewer with its ``snapshot`` extra (from source while it is
  unpublished), then install Chromium and run the real capture explicitly:

  .. code-block:: bash

      $ playwright install chromium
      $ MACHINOME_WEB_SNAPSHOT_E2E=1 pytest tests/test_browser_renderer.py::BrowserSnapshotEndToEndTest

  The ordinary suite leaves this environment variable unset and skips the
  capture, even when the viewer is installed. With the opt-in set, a missing
  viewer or browser is a setup failure. The dedicated CI browser-snapshot job
  installs both dependencies, sets the opt-in, and runs this same test.
* ``tests/meta_project/`` together with ``tests/test_meta.py`` is the
  end-to-end meta-project harness: it runs small real machinome projects —
  both deliberately green and deliberately red fixtures — to prove the
  loading, rendering, and ``machinome test`` subprocess paths. Use it when a
  change touches behavior that direct unit tests cannot establish; see
  `docs/contributor-briefing.md <docs/contributor-briefing.md>`_ for when and
  why.
* The browser viewer's own tests live in the ``machinome-viewer``
  repository. ``tools/generate_parity_fixture.py`` produces, from this
  framework's render results, the parity fixture that repository commits
  beside its expression evaluator.

Where things live
-----------------

* ``machinome/node/`` — the node tree (base, assembly, fusion, leaf, CAD
  backend adapters, operations)
* ``machinome/manager/`` and ``machinome/cli.py`` — the ``machinome`` command:
  develop loop, test, snapshot, new, export
* ``machinome/core/`` — build pipeline, loader, caching
* ``machinome/simulation/`` — drivers, instructions, the stepped ``Sim``
  loop, and ``ScenarioTest``
* ``machinome/test.py`` — mesh-oriented test cases and assertions
* ``machinome/viewers/`` — the OpenSCAD snapshot renderer, the lookup
  of the installed ``machinome-viewer`` package, and the staging half of the
  web snapshot renderer (the photograph itself is the viewer's)
* ``tests/`` — Python test suite
* ``docs/`` — Sphinx documentation, architecture synthesis, ADRs
* ``openspec/`` — OpenSpec change proposals and baseline specs

Development discipline
======================

This repository is developed agentically and follows a strict
spec-first discipline. **Every behavioral change starts as an OpenSpec
change proposal and is ratified before implementation.** Drive-by edits,
unrecorded redesigns, and "fix it first, document it later" are not how
this project moves — this applies equally to human contributors and to
coding agents operating autonomously.

OpenSpec changes
----------------

Behavioral contracts live in ``openspec/specs/``. Changes are proposed,
reviewed, implemented, and archived through the OpenSpec workflow
(`OpenSpec <https://openspec.ai>`_, CLI v1.x; the repo's
``openspec/config.yaml`` carries project context and rules):

1. **Propose** — create a change under ``openspec/changes/<name>/`` with
   ``proposal.md`` (why, what changes, capabilities, impact), ``design.md``
   (how), and ``tasks.md`` (implementation steps). The change describes
   *deltas* against the current specs.
2. **Review** — the proposal is inspected and refined before any code is
   written. Specs describe observable behavior only; no aspirational
   requirements.
3. **Apply** — implement the ratified proposal, task by task, TDD-style:
   red evidence first (a failing test that pins the contract), then the
   smallest change that satisfies it.
4. **Archive** — when the change lands, its spec deltas are merged into
   ``openspec/specs/`` and the change moves to ``openspec/changes/archive/``.

The proposal and completed record belong in this repository's
``openspec/`` directory. See `CONTRIBUTING.rst <CONTRIBUTING.rst>`_
for the contribution workflow.

Architecture Decision Records
-----------------------------

*Why* the system is the way it is lives in ``docs/adrs/`` (see
`docs/adrs/README.md <docs/adrs/README.md>`_ for the index and the full
discipline):

* One decision per ADR, numbered sequentially, filed under the subsystem it
  affects (NODE, BUILD, IPC, MATH, TEST-FRAMEWORK, VIEWER-WEB, EXPORT).
* Statuses flow ``Proposed`` → ``Accepted``; later ADRs may mark earlier ones
  ``Superseded``. Superseded ADRs stay in the log — they are the history that
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

Contributing
============

Bug reports and pull requests are welcome at
https://github.com/machinome/machinome — see
`CONTRIBUTING.rst <CONTRIBUTING.rst>`_ and the development discipline above.
