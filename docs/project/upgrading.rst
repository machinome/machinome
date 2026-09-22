Upgrading from solid-node 0.6 to Machinome 0.7
==================================================

Machinome 0.7 continues solid-node 0.6.0 with the same Git history.
The framework and the GitHub organisation were renamed because
`solid-node` could be mistaken for a node in Tim Berners-Lee's Solid
project, and LibreSolid for a libre edition of it. **Source code for
machines** describes this project's purpose.

Change the names together
--------------------------

There is no ``solid_node`` import shim or ``solid`` command alias.

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Former name
     - Machinome 0.7
   * - Distribution ``solid-node``
     - ``machinome``
   * - Python imports ``solid_node.*``
     - ``machinome.*``
   * - Command ``solid``
     - ``machinome``
   * - Manifest ``[tool.solid-node]``
     - ``[tool.machinome]``, including nested model tables
   * - Environment ``SOLID_NODE_*``
     - ``MACHINOME_*``, including settings in ``.env``
   * - Repository ``LibreSolid/solid-node``
     - ``machinome/machinome``
   * - Documentation ``solid-node.readthedocs.io``
     - ``machinome.readthedocs.io``
   * - Viewer ``solid-node-viewer`` / ``solid_node_viewer``
     - ``machinome-viewer`` / ``machinome_viewer`` (command matches distribution)
   * - Viewer entry point ``solid_node.viewer``
     - ``machinome.viewer``
   * - Mechanics ``solid-mechanics`` / ``solid_mechanics``
     - ``machinome-mechanics`` / ``machinome_mechanics``
   * - Sphinx ``solid_node.sphinx`` / ``.. solid-node::``
     - ``machinome.sphinx`` / ``.. machinome::``
   * - Browser ``SolidNodeWidget`` / ``solid-widget.js``
     - ``MachinomeViewer`` / ``machinome-viewer.js``
   * - DOM/API ``data-solid-widget`` / ``solidNodeViewerApi``
     - ``data-machinome-widget`` / ``machinomeViewerApi``

Update requirements, scripts, CI, imports, configuration and embedding
hosts as one migration. Recognised old manifest tables and environment
names fail with migration messages. New documents use
``format: "machinome-export"``; the matching viewer still reads committed
``solid-node-export`` documents. The rename alone does not change a
document's schema version. Historical release records retain the old names.

The prefix migration applies to former ``SOLID_NODE_*`` settings.
The current implementation still reads ``SOLID_BUILD_DIR``,
``SOLID_TEST_KERNEL``, ``SOLID_TEST_VOLUME_EPSILON`` and
``SOLID_TEST_PLACEMENT_QUANTUM`` under those names; do not mechanically
rename them. See :doc:`/reference/cli` for the complete environment table.

Update port imports
--------------------

Ports and time declarations live in ``machinome.motion.ports``, not
``machinome.node``. Parameter kinds live in ``machinome.parameters``:

.. code-block:: python

   from machinome.node import AssemblyNode, CadQueryNode
   from machinome.parameters import Length, Count
   from machinome.motion.ports import RotationalPort, TranslationalPort, Time
   from machinome.motion.joints import Revolute, Prismatic
   from machinome.simulation import Driver, State, Instruction, Sim

Constructor-based nodes and direct ``rotate()`` / ``translate()``
motion remain supported. Adopt typed parameters and declared children
incrementally; keep CAD construction in each leaf's ``render()``.
See :doc:`/concepts/values`.

Separate rest from motion
---------------------------

Create children and place them at rest in ``render()``. Put runtime
bindings and transformations in ``simulate()``. A legacy ``render()``
that reads time, drivers or ports remains supported but warns and reruns
per binding. Do not recreate children or accumulate transforms in
``simulate()``.

A class-body joint uses the declaring body's own frame; a joint declared
where a parent places a child uses that parent's frame. Preview projects
using the earlier joint semantics must recheck axes and anchors.
See :doc:`/concepts/joints`.

Choose the simulation your machine needs
-----------------------------------------

An undeclared timeline remains normalized from 0 to 1.
``Time(loop=seconds)`` gives it a duration; ``set_keyframe()`` and
testing decorators then take seconds, while ``snapshot --time``
still takes a timeline fraction.

``Time.running()`` opts into a simulation that integrates movement
and retains coordinate history. Use movement requests, not direct
position assignment, to operate it. ``Time.elapsed()`` declares
non-wrapping seconds without selecting running mechanics.

Declaring a ``State`` anywhere in the tree selects a clocked machine:
``Sim(machine)`` accepts requests without ``dt``, and committing
relations write memory at events. Add ``Time.elapsed()`` when those
events need a clock. A state is not a user input; instructions and
``set_state`` cannot write it. Clocked instructions name exactly one
driver, and their duration controls the viewer's drawing of the request.
See :doc:`/concepts/execution-models` for the separate execution models
and their limits.

Install a matching viewer
--------------------------

The independent AGPL-3.0-only viewer is installed through the ``viewer``
extra. It is required by ordinary ``machinome develop``.
``--no-web`` retains the watch-and-build loop. OpenSCAD remains a
modelling backend and snapshot renderer; ``develop --openscad`` is no
longer an interactive-viewer option.

The matching viewer is |viewer_version|, API |viewer_api|, reading
document schemas |document_versions|. Check ``machinome viewer`` for the
installed package, API and ``documentVersions``. A clocked machine
requires schema 8; running models require 5, 6, 7 or 9 according to the
laws they carry (explicit ``Play`` requires 9). Hosts must update their bundle and the renamed
JavaScript/DOM surface together. See :doc:`/concepts/publishing`.

The ``mechanics`` extra selects the independent
``machinome-mechanics`` |mechanics_version| package. Projects using the unreleased
``machinome.mechanisms`` helpers must change those imports to
``machinome_mechanics``; names, signatures and formulas are preserved.
The framework does not re-export the helpers. The `Machinome Mechanics
manual <https://machinome-mechanics.readthedocs.io/en/latest/>`_ covers
installation, migration, coordinate conventions and every helper.
The ``studio`` extra names
Machinome Studio, which remains experimental and unpublished and cannot
be installed from an index.

Verify your project
---------------------

Run ``machinome models``, build every named model, rerun mechanical
and scenario tests, inspect representative poses, and regenerate exports.
A state-only test does not establish geometric fit.

Start with a clean virtual environment so an old ``solid`` executable
or old viewer cannot mask a missed rename. For users coming from 0.5,
reinstallation is also required by the OCCT dependency transition
introduced in 0.6; source must then be migrated to the 0.7 names above.
