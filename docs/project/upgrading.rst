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
``SOLID_TEST_VOLUME_EPSILON`` and ``SOLID_TEST_PLACEMENT_QUANTUM`` under
those names; do not mechanically rename them. The run's engine is
``SOLID_TEST_ENGINE`` in the next release (see below). See :doc:`/reference/cli` for the complete environment table.

Update port imports
--------------------

Ports and time declarations live in ``machinome.motion.ports``, not
``machinome.node``. Parameter kinds live in ``machinome.parameters``:

.. code-block:: python

   from machinome.node.assembly import AssemblyNode
   from machinome.node.cadquery import CadQueryNode
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

The independent AGPL-3.0-or-later viewer is installed through the
``viewer`` extra. It is required by ordinary ``machinome develop``.
``--no-web`` retains the watch-and-build loop. OpenSCAD remains a
modelling backend and snapshot renderer; ``develop --openscad`` is no
longer an interactive-viewer option.

The matching viewer is |viewer_version|, API |viewer_api|, reading
document schemas |document_versions|. Check ``machinome viewer`` for the
installed package, API and ``documentVersions``. A clocked machine
requires schema 8; newly exported running models require schema 11 and a
viewer supporting source-timed motion (introduced by API 24); one
carrying a ``Follow`` relation requires schema 12 (introduced by API 25),
and one whose running ``Bound`` uses finite profile contact requires
schema 13 (introduced by API 26). Re-export running models;
endpoint-era snapshots refuse restore into the new semantic identity, so
restart from the initial model state and replay intended commands.
Hosts must update their bundle and the renamed
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

Install the OpenSCAD family's extras (unreleased)
--------------------------------------------------

The next release moves the OpenSCAD node family out of the plain install.
SolidPython is no longer a required dependency: ``Solid2Node`` needs
``pip install "machinome[solid2]"``, and ``OpenScadNode`` and the OpenSCAD
renderer of ``machinome snapshot`` need ``pip install "machinome[openscad]"``
(``machinome[solid2]`` includes it, and ``machinome[all]`` installs both).
Without the extra, importing the node type refuses with the line that
installs it, and ``machinome snapshot`` with its default renderer exits 1
before loading the model, naming the extra and ``--renderer web``.

``OpenScadNode`` is still ``machinome.node.openscad.OpenScadNode`` and
``Solid2Node`` still ``machinome.node.solid2.Solid2Node``; the framework's
internal OpenSCAD seam and engine modules are gone, with no alias (the
:doc:`changelog` names them): the OpenSCAD writer and binary contract are
``machinome.node.openscad.writer`` and ``machinome.node.openscad.binary``. A node's SCAD members (``scad_file``,
``scad_code``, ``generate_scad``, ``fn``) belong to the family's leaf base,
``machinome.node.openscad.leaf.ScadLeafNode``; a node's presentation hook is
``present``. A project leaf that presented its render as SCAD through the
leaf base's former hook, rather than subclassing ``Solid2Node``, is no
longer handed to OpenSCAD: it is refused for producing no STL, naming it.
Subclass ``Solid2Node`` instead. A leaf declaring ``leaf_contract = 1`` is
refused: the leaf contract is version 3 (see below).

Use the engines' new names (unreleased)
----------------------------------------

The next release names the two engines for the representation each
consumes: the **B-rep engine**, over boundary representations, and the
**mesh engine**, over triangle meshes. The words *exact* and *faceted* and
the libraries' names leave every address, flag, extra and value; nothing
aliases a former name.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Former name
     - Next release
   * - ``machinome test --exact`` / ``--faceted``
     - ``machinome test --brep`` / ``--mesh``
   * - ``SOLID_TEST_KERNEL=exact`` / ``=faceted``
     - ``SOLID_TEST_ENGINE=brep`` / ``=mesh``
   * - ``machinome[occt]`` / ``machinome[manifold]``
     - ``machinome[brep]`` / ``machinome[mesh]``
   * - ``machinome.occt.engine`` (``intersect_shapes``, ``fuse_shapes``,
       ``placed_shape``, ``solid_count``, ``solid_volume``)
     - ``machinome.engine.brep``
   * - ``machinome.manifold.engine``
     - ``machinome.engine.mesh``
   * - ``machinome.exact_engine`` (``exact_engine``,
       ``require_exact_engine``, ``ExactEngineUnavailable``,
       ``ExactCommonInconsistency``, ``ExactCommonVerificationError``)
     - ``machinome.engine`` (``brep_engine``, ``require_brep_engine``,
       ``BrepEngineUnavailable``, ``BrepCommonInconsistency``,
       ``BrepCommonVerificationError``)
   * - ``machinome.mesh_engine`` (``mesh_engine``, ``require_mesh_engine``)
     - ``machinome.engine``, the same names
   * - ``machinome.node.exact_leaf.ExactLeafNode``
     - ``machinome.node.brep_leaf.BrepLeafNode``
   * - a node's ``exact`` flag
     - ``brep``
   * - ``machinome.exact_cache`` / ``machinome.exact_artifacts``
     - ``machinome.brep_cache`` / ``machinome.brep_artifacts``

A former flag is refused as an unrecognised argument. ``SOLID_TEST_KERNEL``
is not read and not ignored: when it is set to anything, ``machinome test``
exits before it builds, naming ``SOLID_TEST_ENGINE``, so rename the line in
every checkout's ``.env`` (the file is not tracked, so a search of the
repository does not find it) and in any CI job that exports it. A
``SOLID_TEST_ENGINE`` set to ``exact`` or ``faceted`` is refused naming the
two accepted values. pip warns about an unknown extra and installs nothing
for it, so update a manifest's ``machinome[occt]`` or ``machinome[manifold]``.

A leaf written outside the core subclasses ``BrepLeafNode`` where it
subclassed ``ExactLeafNode``, reads and declares ``brep`` where it read
``exact``, and declares ``leaf_contract = 3`` where it declared a version:
the leaf contract is version 3, and a class declaring 2 is refused naming
both versions.

Two things recompute once, on their own, with nothing to run by hand:
every project's kept verdicts (``_build/.verdicts``), because a verdict's
key names the engine path and the framework's sources changed, so the
first ``machinome test`` after the upgrade costs what a first run costs;
and the STL of every mesh fusion, whose recorded recipe is renamed, which
the next build writes again to the same bytes. B-rep fusions and every
leaf's artifacts are reused.

A source checkout that pulls the change keeps the compiled caches of the
two removed packages, which Python would import as empty packages: run
``git clean -fdX machinome/occt machinome/manifold`` once in it.

Import every name from its module (unreleased)
-----------------------------------------------

The next release gives every name of the node package one address, the
module that defines it. The package's root, ``machinome.node``, exports
nothing: a class, function or declaration is imported from its module, and
nothing aliases a former spelling. Importing one of the names below from the
root, or reading it as an attribute of the root, fails at that line with an
``ImportError`` naming the module and the line to write, for example::

    ImportError: module 'machinome.node' has no attribute 'AssemblyNode':
    the root of machinome.node exports nothing, and 'AssemblyNode' is
    imported from its module, 'machinome.node.assembly'. Write
    `from machinome.node.assembly import AssemblyNode`.

Each name and the module to import it from:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Name
     - Module
   * - ``AssemblyNode``
     - ``machinome.node.assembly``
   * - ``declared_children``
     - ``machinome.node.declarative``
   * - ``FusionNode``
     - ``machinome.node.fusion``
   * - ``CadQueryNode``
     - ``machinome.node.cadquery``
   * - ``Build123dNode``, ``Build123dSheetNode``
     - ``machinome.node.build123d``
   * - ``SheetLeafNode``
     - ``machinome.node.sheet_leaf``
   * - ``FlexibleNode``
     - ``machinome.node.flexible``
   * - ``MolejoNode``
     - ``machinome.node.molejo``
   * - ``Solid2Node``
     - ``machinome.node.solid2``
   * - ``OpenScadNode``
     - ``machinome.node.openscad``
   * - ``JScadNode``
     - ``machinome.node.jscad``
   * - ``StlNode``
     - ``machinome.node.stl``
   * - ``StepNode``
     - ``machinome.node.step``
   * - ``Marking``, ``Wrapped``, ``Flat``, ``Svg``
     - ``machinome.node.markings``
   * - ``Frame``
     - ``machinome.node.frames``
   * - ``property_as_number``
     - ``machinome.node.decorators``
   * - ``StlRenderStart``
     - ``machinome.node.base``

An import line naming several of them becomes one line per module. The
package's submodules are still imported through it (``from machinome.node
import supported``), and a star import from the root binds nothing. The
files ``machinome new`` and ``machinome import-step`` write import from the
modules too.

A rewritten import line changes no artifact byte, but a part's module is
part of its recorded source, so each part whose module was rewritten
rebuilds once, on its next build, to the same bytes; and, as after any
framework upgrade, the project's kept verdicts recompute once. Nothing is to
be run by hand.

Verify your project
---------------------

Run ``machinome models``, build every named model, rerun mechanical
and scenario tests, inspect representative poses, and regenerate exports.
A state-only test does not establish geometric fit.

Start with a clean virtual environment so an old ``solid`` executable
or old viewer cannot mask a missed rename. For users coming from 0.5,
reinstallation is also required by the OCCT dependency transition
introduced in 0.6; source must then be migrated to the 0.7 names above.
