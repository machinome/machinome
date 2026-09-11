==========
Solid Node
==========


.. image:: https://img.shields.io/pypi/v/solid-node.svg
        :target: https://pypi.org/project/solid-node/
        :alt: PyPI Version

.. image:: https://readthedocs.org/projects/solid-node/badge/?version=latest
        :target: https://solid-node.readthedocs.io/en/latest/
        :alt: Documentation Status


**Describe a machine, not just its parts.**

Solid Node is a Python framework for designing and simulating machines.
Declare the parts, the dimensions they share, the joints that let them
move, and the relationships that make them work together. Inspect the
assembly, operate its controls, and test mechanical requirements in the
same project.

Keep the CAD tools that suit your design: CadQuery, build123d,
OpenSCAD/SolidPython and JSCAD, alongside imported STEP and STL parts,
sheet profiles, and flexible springs, belts and cables through
`molejo <https://molejo.readthedocs.io>`_. Solid Node supplies the
machine structure, motion, incremental builds, tests and export.

A gear ratio should connect the gears you see to the movement you test.
A parameter change should reach the parts that depend on it. A design
shared on a website should be something a reader can inspect and operate.
Those are the relationships Solid Node is built around.

Learn it one step at a time
===========================

The `tutorial <https://solid-node.readthedocs.io/en/latest/quickstart.html>`_
starts with a part, combines a base and pointer into a simple assembly,
animates it, and adds a pin with tests for its fit. From there, learn
parameters, joints, drivers and scenarios.

For complete machines, explore the three external examples:
`V8 engine <https://solid-node.readthedocs.io/en/latest/example-v8-engine.html>`_,
`Metamaquina 2 <https://solid-node.readthedocs.io/en/latest/example-metamaquina2.html>`_,
and `Clock 01 <https://solid-node.readthedocs.io/en/latest/example-clock-01.html>`_.
Each keeps its design source in its own repository.

* `User manual <https://solid-node.readthedocs.io/en/latest/>`_
* `Migrating from 0.6 <https://solid-node.readthedocs.io/en/latest/upgrading.html>`_

This checkout documents **0.7, in preparation**. The latest published
framework is 0.6.0; the quickstart distinguishes preview installation
from the installation command to use after release.

Solid Node is Apache-2.0. The optional browser viewer is the independent
AGPL-3.0-only `solid-node-viewer
<https://github.com/LibreSolid/solid-node-viewer>`_ package, installed
through the ``viewer`` extra once published. Without it, the
framework uses OpenSCAD as its viewer. Designs retain their own
licences in their external repositories. The framework's tutorial is
Apache-2.0 and contains no source adapted from those projects.

Motion is prescribed kinematics, not a general dynamics simulation.
Geometric tests help establish specific fits, clearances and support
conditions; they do not replace manufacturing review or physical tests.

Working on solid-node itself
============================

This section is for contributors — humans and coding agents — who modify the
framework in this repository. For *using* solid-node in your own mechanical
project, see the documentation above.

Development environment
-----------------------

Requirements: Python >= 3.11. Node.js is not needed: the browser viewer and
its widget live in the separate `solid-node-viewer
<https://github.com/LibreSolid/solid-node-viewer>`_ repository, and the tests
that need a viewer skip unless that package is installed. `OpenSCAD
<https://openscad.org/>`_ is conditional: put it on the PATH when working on
SolidPython2/Solid2 or raw OpenSCAD nodes, faceted fusions, symbolic Solid2
animation values, the ``solid develop --openscad`` viewer, or the default
OpenSCAD snapshot renderer. All-exact projects — CadQuery, build123d, or the
two mixed — build, test, and export without it; use
``solid snapshot --renderer web`` for snapshots on a machine without OpenSCAD.

`manifold3d <https://pypi.org/project/manifold3d/>`_ is installed by default
and is conditional in the same sense: it decides faceted geometry, so it is
needed whenever an assertion compares a part that has no exact geometry, and
by ``assertAssemblySupported``, whose statics phase reads contact patches off
meshed intersections for every body. An all-exact project's other geometric
assertions are decided by the OCCT kernel and run without it — useful on a
platform with no compiled wheel, such as WebAssembly. A path that needs it
and cannot import it says so by name.

Clone with submodules (the docs embed three separately maintained
example machines):

.. code-block:: bash

    $ git clone --recurse-submodules https://github.com/LibreSolid/solid-node.git
    $ cd solid-node

Create a virtualenv and install the package in editable mode with the dev
dependencies:

.. code-block:: bash

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e ".[dev]"

The ``solid`` CLI entrypoint (``solid_node/cli.py``) is now on the PATH of
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
      $ SOLID_NODE_WEB_SNAPSHOT_E2E=1 pytest tests/test_browser_renderer.py::BrowserSnapshotEndToEndTest

  The ordinary suite leaves this environment variable unset and skips the
  capture, even when the viewer is installed. With the opt-in set, a missing
  viewer or browser is a setup failure. The dedicated CI browser-snapshot job
  installs both dependencies, sets the opt-in, and runs this same test.
* ``tests/meta_project/`` together with ``tests/test_meta.py`` is the
  end-to-end meta-project harness: it runs small real solid-node projects —
  both deliberately green and deliberately red fixtures — to prove the
  loading, rendering, and ``solid test`` subprocess paths. Use it when a
  change touches behavior that direct unit tests cannot establish; see
  `docs/contributor-briefing.md <docs/contributor-briefing.md>`_ for when and
  why.
* The browser viewer's own tests live in the ``solid-node-viewer``
  repository. ``tools/generate_parity_fixture.py`` produces, from this
  framework's render results, the parity fixture that repository commits
  beside its expression evaluator.

Where things live
-----------------

* ``solid_node/node/`` — the node tree (base, assembly, fusion, leaf, CAD
  backend adapters, operations)
* ``solid_node/manager/`` and ``solid_node/cli.py`` — the ``solid`` command:
  develop loop, test, snapshot, new, export
* ``solid_node/core/`` — build pipeline, loader, caching
* ``solid_node/simulation/`` — drivers, instructions, the stepped ``Sim``
  loop, and ``ScenarioTest``
* ``solid_node/test.py`` — mesh-oriented test cases and assertions
* ``solid_node/viewers/`` — the OpenSCAD viewer and snapshotter, the lookup
  of the installed ``solid-node-viewer`` package, and the staging half of the
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
https://github.com/LibreSolid/solid-node — see
`CONTRIBUTING.rst <CONTRIBUTING.rst>`_ and the development discipline above.
