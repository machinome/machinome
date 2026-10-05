Upgrading from Machinome 0.7 to 0.8
===================================

Machinome 0.8 removes and renames without aliases: a former spelling fails
at the line that uses it, naming what to write instead. These are all of
its breaking changes, and what to change for each.

#. **Install the extras your parts use.** A bare ``pip install machinome``
   carries no CAD kernel, no SolidPython and no manifold3d. Name the extra of
   each node type and engine your project uses, or ``all``; see
   :ref:`upgrade-extras` and :doc:`/start/install`.
#. **Import every node name from its module.** The root of
   ``machinome.node`` exports nothing; each of its twenty-one former names
   is imported from the module that defines it, and a star import from the
   root binds nothing. See :ref:`upgrade-modules`.
#. **Rename the adapters' addresses.** ``machinome.node.adapters`` is
   dissolved: ``machinome.node.adapters.<x>`` is ``machinome.node.<x>``,
   for example ``from machinome.node.step import StepAssembly``.
#. **Rename the engine flags and the test variable.** ``machinome test
   --exact`` and ``--faceted`` are ``--brep`` and ``--mesh``;
   ``SOLID_TEST_KERNEL`` is refused whenever it is set, and the run's engine
   is ``SOLID_TEST_ENGINE``, ``brep`` or ``mesh``. See :ref:`upgrade-engines`.
#. **Import the B-rep operations and the engines' seams from the engine
   package.** ``machinome.exact`` and ``machinome.mesh_engine``
   are removed; ``intersect_shapes``, ``fuse_shapes``, ``placed_shape``,
   ``solid_count`` and ``solid_volume`` are ``machinome.engine.brep``'s, under
   the same names and signatures. See :ref:`upgrade-engines`.
#. **Wrap a node's shape where you use CadQuery's API on it.** ``shape()``
   and the B-rep operations return the kernel's own ``TopoDS_Shape`` instead
   of a CadQuery ``Shape``; a project that calls CadQuery's methods on one
   wraps it, ``cadquery.Shape.cast(node.shape())``. Passing it to an
   assertion or an operation needs nothing.
#. **Rename the B-rep leaf base and its flag.** ``ExactLeafNode`` at
   ``machinome.node.exact_leaf`` is ``BrepLeafNode`` at
   ``machinome.node.brep_leaf``, and a node's ``exact`` flag is ``brep``.
#. **Declare leaf contract 3 in a leaf package.** A node type written
   outside machinome may state the leaf contract it was written against as
   ``leaf_contract = 3`` in its class body; a class declaring another number
   is refused naming both. The hooks of ``SheetLeafNode`` (``profile_faces``,
   ``lies_on_xy_plane``, ``extrude``, ``write_dxf(face, path)``) and of
   ``FlexibleNode`` (``shape_parameters``, ``shape_spec``,
   ``snapshot_mesh``, ``snapshot_stl``, ``snapshot_shape``) lose their
   leading underscore, and ``write_dxf`` writes to the path it is given.
#. **Install the OpenSCAD family's extras and use its addresses.**
   ``Solid2Node`` needs ``machinome[solid2]``, ``OpenScadNode`` and the
   OpenSCAD renderer of ``machinome snapshot`` need ``machinome[openscad]``;
   the SCAD members belong to the family's leaf base, ``as_scad`` is
   ``present``, and ``machinome.openscad`` is ``machinome.node.openscad.binary``.
   See :ref:`upgrade-openscad`.
#. **Read SCAD text where it is written now.** A build writes the ``.scad``
   of an OpenSCAD-family part only, and removes the others an earlier build
   left; the SCAD text of any node is ``scad_code(node)`` from
   ``machinome.node.openscad.writer``. ``assemble()``, ``present()`` and
   ``artifact_import()`` return machinome's presentation description,
   ``Rotation.scad()`` and ``Translation.scad()`` are removed, and
   ``Builder`` takes no ``scad_output``.
#. **Import the symbolic value from the expression graph.**
   ``machinome.scad_expression`` is removed; its names
   (``get_animation_time``, ``GraphValue``, ...) are imported from
   ``machinome.expression_graph``. A symbolic value is machinome's own type,
   not a SolidPython class, and asking it for its truth raises
   ``SymbolicTruthError``, an ``Exception``. Read the animation time as
   ``self.time`` inside ``simulate()``: SolidPython's own values, such as
   ``solid2.get_animation_time()``, are expressions only in a process that
   imported ``machinome.node.solid2``. ``scad_expression`` in
   ``machinome.core.expressions`` is ``closed_expression``, and
   ``OPENSCAD_FOV`` in ``machinome.core.camera`` is ``DEFAULT_FOV``.
#. **Expect new projects to import per module.** ``machinome new`` and
   ``machinome import-step`` write ``from machinome.node.<module> import
   <name>`` lines, and ``machinome new`` scaffolds a ``Solid2Node`` where
   SolidPython is installed, a ``CadQueryNode`` where only CadQuery is, and
   refuses naming both extras with neither.
#. **Expect one recomputation.** Nothing is to be run by hand. Every
   project's kept verdicts (``_build/.verdicts``) recompute once, so the
   first ``machinome test`` after the upgrade costs what a first run costs;
   the STL of every mesh fusion is written again once, to the same bytes,
   because its recorded recipe is renamed; and a part whose module was
   rewritten, or whose class is one of the leaf classes itself, rebuilds
   once, to the same bytes, because its module is part of its recipe.

No published document changes: exports keep document versions 1 to 13, and
a 0.7 viewer reads a 0.8 export.

.. _upgrade-extras:

Install the extras your parts use
---------------------------------

Each CAD kernel and node family is an extra named for the last component of
the module that needs it: ``machinome[cadquery]``, ``[build123d]``,
``[step]``, ``[molejo]``, ``[brep]``, ``[mesh]``, ``[openscad]``,
``[solid2]``, ``[jscad]``, ``[stl]`` and ``[all]``. Without its extra,
importing a module refuses with the line that installs it, for example::

    ModuleNotFoundError: machinome.node.cadquery (CadQueryNode) needs
    cadquery, which is not installed; install it with
    'pip install "machinome[cadquery]"'

The mesh engine, ``machinome[mesh]``, is needed by a project that compares a
part without B-rep geometry, runs ``machinome test --mesh``, calls
``assertAssemblySupported``, fuses meshes, or imports manifold3d or calls
``trimesh.boolean`` itself; each of those refuses naming the extra without
it, and ``machinome test`` on the mesh engine refuses at its start. A
project that imports ``cadquery`` or ``build123d`` in its own modules needs
the extra of that name. ``machinome import-step`` needs ``machinome[step]``.

.. _upgrade-openscad:

Install the OpenSCAD family's extras
------------------------------------

SolidPython is no longer a required dependency: ``Solid2Node`` needs
``pip install "machinome[solid2]"``, and ``OpenScadNode`` and the OpenSCAD
renderer of ``machinome snapshot`` need ``pip install "machinome[openscad]"``
(``machinome[solid2]`` includes it, and ``machinome[all]`` installs both).
Without the extra, importing the node type refuses with the line that
installs it, and ``machinome snapshot`` with its default renderer exits 1
before loading the model, naming the extra and ``--renderer web``.

``OpenScadNode`` is ``machinome.node.openscad.OpenScadNode`` and
``Solid2Node`` ``machinome.node.solid2.Solid2Node``. The OpenSCAD binary
helpers ``require_openscad``, ``openscad_binary`` and ``OpenScadUnavailable``
are imported from ``machinome.node.openscad.binary`` where they were
``machinome.openscad``'s, and the SCAD writer is
``machinome.node.openscad.writer``. A node's SCAD members (``scad_file``,
``scad_code``, ``generate_scad``, ``fn``) belong to the family's leaf base,
``machinome.node.openscad.leaf.ScadLeafNode``; a node's presentation hook is
``present``. A project leaf that presented its render as SCAD by overriding
``as_scad``, rather than subclassing ``Solid2Node``, is no longer handed to
OpenSCAD: it is refused for producing no STL, naming it. Subclass
``Solid2Node`` instead.

.. _upgrade-engines:

Use the engines' names
----------------------

Machinome 0.8 names the two engines for the representation each consumes:
the **B-rep engine**, over boundary representations, and the **mesh
engine**, over triangle meshes. The words *exact* and *faceted* leave every
address, flag and value; nothing aliases a former name.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Machinome 0.7
     - Machinome 0.8
   * - ``machinome test --exact`` / ``--faceted``
     - ``machinome test --brep`` / ``--mesh``
   * - ``SOLID_TEST_KERNEL=exact`` / ``=faceted``
     - ``SOLID_TEST_ENGINE=brep`` / ``=mesh``
   * - ``machinome.exact`` (``intersect_shapes``, ``fuse_shapes``,
       ``placed_shape``, ``solid_count``, ``solid_volume``)
     - ``machinome.engine.brep``
   * - ``machinome.exact`` (``ExactCommonInconsistency``,
       ``ExactCommonVerificationError``)
     - ``machinome.engine`` (``BrepCommonInconsistency``,
       ``BrepCommonVerificationError``)
   * - ``machinome.mesh_engine`` (``mesh_engine``, ``require_mesh_engine``,
       ``MeshEngineUnavailable``)
     - ``machinome.engine``, the same names
   * - ``machinome.node.exact_leaf.ExactLeafNode``
     - ``machinome.node.brep_leaf.BrepLeafNode``
   * - a node's ``exact`` flag
     - ``brep``

A former flag is refused as an unrecognised argument. ``SOLID_TEST_KERNEL``
is not read and not ignored: when it is set to anything, ``machinome test``
exits before it builds, naming ``SOLID_TEST_ENGINE``, so rename the line in
every checkout's ``.env`` (the file is not tracked, so a search of the
repository does not find it) and in any CI job that exports it. A
``SOLID_TEST_ENGINE`` set to ``exact`` or ``faceted`` is refused naming the
two accepted values.

``shape()`` and the operations of ``machinome.engine.brep`` return the
kernel's own ``TopoDS_Shape``. Where a project calls CadQuery's methods on
one (``translate``, ``Solids``, ``Volume``, ``BoundingBox``...), wrap it
first, ``cadquery.Shape.cast(node.shape())``; passing it to an assertion or
to an engine operation needs nothing.

.. _upgrade-modules:

Import every name from its module
---------------------------------

Machinome 0.8 gives every name of the node package one address, the module
that defines it. The package's root, ``machinome.node``, exports nothing: a
class, function or declaration is imported from its module, and nothing
aliases a former spelling. Importing one of the names below from the root,
or reading it as an attribute of the root, fails at that line with an
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
``SOLID_TEST_ENGINE`` since 0.8 (see above). See :doc:`/reference/cli` for
the complete environment table.

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

Verify your project
---------------------

Run ``machinome models``, build every named model, rerun mechanical
and scenario tests, inspect representative poses, and regenerate exports.
A state-only test does not establish geometric fit.

Start with a clean virtual environment so an old ``solid`` executable
or old viewer cannot mask a missed rename. For users coming from 0.5,
reinstallation is also required by the OCCT dependency transition
introduced in 0.6; source must then be migrated to the 0.7 names above.
