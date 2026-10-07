
.. _api-reference:

=================
API Reference
=================

Production assets
=================

``Production[Model]`` from ``machinome.production.profile`` binds independent
production choices to an existing model. Several profiles can consume the
same instance without selecting a current profile on the model or changing
its simulation. Import each name from its defining module; neither
``machinome`` nor ``machinome.production`` reexports these names.

A partial calculator profile can delegate its actual crank assembly and
source explicitly named fasteners. The following example omits the model
modules and the two attributed Markdown instruction files that the author
supplies beside the profile module:

.. code-block:: python

   from machinome.model import Reference
   from machinome.components import Standard
   from machinome.production.profile import Production
   from machinome.production.item import Item
   from machinome.production.process import Printed, Sourced
   from machinome.production.instruction import Step, Markdown
   from models.calculator import Calculator, CrankAssembly

   class CrankProduction(Production[CrankAssembly]):
       pin = Item(Reference(CrankAssembly, ("crank_handle_pin",)), Printed())
       screw = Item(
           Reference(CrankAssembly, ("crank_handle_1", "crank_handle_pin_screw")),
           Printed(),
       )
       finish = Step(screw, instructions=Markdown("file-and-thread-pin.md"))

   class CalculatorProduction(Production[Calculator]):
       crank = CrankProduction(Reference(Calculator, ("main_drive", "crank")))
       limitations = Step(crank, instructions=Markdown("draft-limitations.md"))

   model = Calculator()
   production = CalculatorProduction(model)
   production.findings
   production.crank.bom
   production.export("draft-calculator")

The child consumes the existing assembly with its actual resolved parameters.
No default crank is constructed. ``parameters`` exposes the bound scope's
read-only parameter mapping. References select actual active occurrences;
lists and repetitions expand in model order, a zero repetition contributes
nothing, and an omitted named target is an explicit finding. A nonempty tuple
of references selects named siblings. Repeated child bindings are tuples,
including a one-member repetition. Their members' declaration paths carry the
member's index at every count, as ``kids-0/nut``. Concrete profile inheritance
is refused.

``Item(target, process, *, mass=None)`` comes from
``machinome.production.item``. An instance field returns a read-only
``BoundItem`` with ``target_paths``, ``process``, ``mass_basis`` and
``declaration_path``. Select a compatible model class itself for the bound
root. ``Printed(material=None)``, ``Cut(stock)`` and
``Sourced(requirement, *, offer=None)`` come from
``machinome.production.process``. Unspecified printed material stays unknown;
infill, finishing and wire bending are maker instructions. They do not become
an invented polymer, mass multiplier or purchased finished spring.

``Material(name, *, density_kg_m3=None)`` is defined in
``machinome.production.material`` and
``Sheet(material, *, thickness_mm)`` in ``machinome.production.stock``.
Density and thickness, when supplied, must be finite and positive.
Cut requires a declared sheet part with matching thickness and nominal-DXF
capability. ``stock`` reports finished-part count and an unknown purchased
sheet quantity; it performs no nesting or kerf compensation.

``Standard(name, *, designation, grade=None)`` and
``Product(manufacturer, part_number, *, conforms_to=())`` are neutral
records in ``machinome.components``. ``Offer(product, supplier, sku,
*, url=None)`` from ``machinome.production.sourcing`` identifies a distinct
supplier listing. Its product must match the Product requirement or explicitly
assert conformance to the Standard requirement. These records do no supplier
search and make no certification claim.

``Step(*subjects, instructions=Markdown(path))`` and ``Markdown(path)``
come from ``machinome.production.instruction``. Subjects are Item or child
declarations belonging to that profile. Paths resolve beside the declaring
module, with canonical traversal and symlink escape refused. Child steps
precede parent steps, preserving declaration order and model subject paths.
Version-one text accepts plain Markdown, external HTTP/HTTPS links and
same-document fragments. Unsupported local links, images, reference
dependencies and raw HTML dependencies are refused. An HTML tag is a dependency
when its element embeds or loads content or an attribute names a resource;
other text, such as ``a<b``, is not. Text in code spans and fenced code blocks
is not read for dependencies. A missing instruction file refuses requested
steps or export without producing a partial bundle.

``MeasuredMass(grams, *, evidence)`` and ``SolidMass()`` are defined in
``machinome.production.mass``. Measured grams apply per occurrence and require
local evidence. ``SolidMass`` explicitly requests a homogeneous-solid
calculation: positive watertight volume in mm³ times density in kg/m³ divided
by 1,000,000 gives grams. Missing density, invalid volume and flexible volume
stay unknown. The model's simulation and support assumptions do not change.

Read ``bom``, ``stock``, ``steps``, ``mass`` and ``findings`` directly; there
is no evaluate call. Construction performs no geometry work. Structural
findings, instructions and sourced BOMs need no geometry. Manufactured BOM
grouping requests canonical geometry content, with complete process/material,
mass declaration and every directly applicable Step fingerprint. Different
materials or finishing instructions remain separate. Sourced grouping uses
the requirement and chosen offer rather than the visual mesh.

``bom`` is a tuple of ``BomLine`` records. Each line retains status, quantity,
occurrence paths, declaration paths, source paths and finding codes, plus its
typed process, material, requirement, offer and optional geometry identity.
Unassigned candidates appear separately with quantity one and no invented
identity; invalid recipes retain their requested process but no usable
process; absent targets have quantity zero. Delegation reserves its subtree.
Sourcing a whole assembly replaces its internals with one purchased item.
Overlapping owners remain inspectable in ``findings`` and refuse the other
reports, with ``ProductionConflictError``, of every binding whose scope holds
an occurrence they both claim; the root's scope holds every occurrence.

``MassSummary`` exposes ``known_grams``, ``complete``, ``unknown_occurrences``
and a tuple of per-occurrence ``MassBasis`` records. A known subtotal is not
a complete total. Unassigned and invalid candidates remain in the denominator;
a valid sourced assembly replaces the descendants' weight with its own basis.
Report records and mappings are immutable. The report types, ``Finding``,
``ResolvedStep`` and ``ExportResult`` are defined in
``machinome.production.results``; errors are defined in
``machinome.production.errors``.

``Finding.check_status`` describes only the structural check represented by
that finding. Its ``checked`` value does not establish an unrequested geometry
or mass check; export explicitly requests those checks.

``export(destination)`` atomically creates a new portable directory and
refuses an existing nonempty destination. ``production.json`` is the
authoritative version-one ``machinome-production`` manifest, accompanied by
``bom.csv``, ``stock.csv`` and ``instructions.md``. Explicitly consumed files
live under ``files/<sha256>/<basename>``; selected Printed STL and Cut nominal
DXF files live under ``artifacts/<sha256>.<extension>``. Facts and copied bytes
describe the same pinned artifacts. Every export is a draft; coverage
completeness does not certify fabrication readiness.

Model consumption
-----------------

``machinome.model.ModelSnapshot(model)`` exposes immutable ``occurrences``,
``select(reference, *, scope=None)``, ``geometry(occurrence)`` and
``copy_artifact(occurrence, kind, destination)``. Occurrences distinguish
assemblies, rigid pieces, rigid features and flexible pieces. Markings and
frames add no production item; fusion ingredients are features of one piece.
Each occurrence retains its root-relative path (``.`` for the root), model
type, resolved parameters, source paths and declared sheet facts.
``GeometryFacts`` retains full canonical content identity separately from
artifact byte SHA-256, extents, volume and watertightness.

``Reference(model_type, path)`` takes a tuple of public attribute names and
supports constructor-created children without rewriting the model.
``is_reference`` and ``reference_path`` adapt supported declarations;
``empty_selection`` and ``selection_is_many`` distinguish absent targets
from repetition shape. ``validate``, ``observe_input``, read-only
``input_hashes`` and ``executed_code_provenance`` support a shared root/child
input generation, without an extra author lifecycle.

Rest-only structural reading preserves the running state and refuses
stateful legacy rendering. Directly constructed models carry
``unverified-direct-binding`` provenance: observing current source bytes
cannot prove what Python imported earlier. Models loaded through the sealed
source-generation loader retain verified provenance. A source, instruction,
evidence or consumed artifact replacement invalidates the whole shared
production with ``ProductionInputChangedError``; reload code and bind a fresh
model rather than combining old facts with new bytes.

Nodes
=========

Each node class is imported from its module, the address beside it below;
the root of ``machinome.node`` exports nothing. The parameters they declare
come from ``machinome.parameters``. A project is a
tree of nodes: leaf nodes generate solids with an underlying modelling
library, internal nodes combine their children.

Common node API
-------------------

.. autoclass:: machinome.node.base.AbstractBaseNode

   .. method:: render()

      ``render()`` builds the node at rest. A purely declarative
      composition may omit it when no additional placement is needed.
      Leaf nodes return an object of the underlying modelling library;
      internal nodes return a list of child node instances (or, on a
      declarative class, nothing), after placing the parts that do not
      move. It reads no driver, no time and no port — an assembly's
      ``render()`` that read none runs once per instance; one that does
      read keeps re-running per binding and warns once per class. What
      moves belongs to :meth:`AssemblyNode.simulate`.

   .. method:: rotate(angle, axis)

      Rotate this node by ``angle`` degrees around the vector ``axis``
      (a list of three numbers, e.g. ``[0, 0, 1]``). Applied in
      ``render()`` it is rest placement and persists; applied in
      ``simulate()`` it is motion — composed inside the rest placement,
      stated absolutely for its instant, and dropped before the assembly
      simulates again. Both apply in the viewer and to the mesh used by
      tests. Returns the node itself, so calls can be chained. In
      ``simulate()``, ``angle`` may be an expression involving
      :attr:`AssemblyNode.time` or any declared driver.

   .. method:: translate(translation)

      Translate this node by the vector ``translation``, a list of three
      numbers, e.g. ``.translate([100, 0, 0])``. Chains like
      :meth:`rotate`, and the node itself is returned.

   .. attribute:: name

      The node's name, used in viewer and test failure messages. Defaults
      to the class name; can be overridden with the ``name`` keyword
      argument of the constructor.

   .. automethod:: set_keyframe

   .. automethod:: clear_keyframe

   .. automethod:: assemble

   .. autoproperty:: mtime

Leaf nodes
--------------

A leaf produces one solid. Four bases make up the declared leaf contract,
each imported from the module that defines it:
:class:`~machinome.node.leaf.LeafNode`, the base of every leaf and the one
a mesh leaf subclasses; :class:`~machinome.node.brep_leaf.BrepLeafNode`,
for a leaf whose geometry is a B-rep, a boundary representation;
:class:`~machinome.node.sheet_leaf.SheetLeafNode`, for a B-rep leaf cut
from sheet stock; and :class:`~machinome.node.flexible.FlexibleNode`, for a
leaf whose shape follows its bound ports. A node type written outside
machinome subclasses one of them and uses only the members documented with
it here; currency, stamps, source records, the tree, assembly, fusion,
export, the viewer document and the test framework are machinome's. A
subclass never overrides ``assemble``, ``mtime_ns``, ``mtime``,
``source_digest``, ``source_fingerprint``, ``uniq_id``, ``children``,
``time``, nor any member whose name begins with an underscore.

The contract is versioned. :data:`machinome.node.leaf.CONTRACT` is the
version this machinome speaks; a class that declares ``leaf_contract`` in
its own body is compared with it when the class is created, and refused
with a ``TypeError`` naming both numbers when they differ. A class that
declares nothing is not checked.

.. autodata:: machinome.node.leaf.CONTRACT

.. autoclass:: machinome.node.leaf.LeafNode
   :members: render, validate, namespace, present, materialize,
             publish_artifact, get_source_file, source_recipe,
             artifact_import, leaf_contract, time

   .. method:: presentation()

      This node's own presentation description, its artifact imports
      resolving from its own build directory: what a node package writes
      when it writes this node's presentation in its own language.

   .. method:: kept_artifacts()

      The paths of the artifacts beyond the STL, BREP and markings that a
      build keeps for this node while it is in the published tree, by this
      declaration and never by kind. None by default; an OpenSCAD-family
      leaf keeps its ``.scad``.

   .. method:: generate_stl()

      Make the node's STL current. Nothing when it is current, the node is
      not rigid or another process holds its render lock. A leaf whose tool
      runs in a subprocess starts it here and raises
      :exc:`~machinome.node.base.StlRenderStart`; otherwise a rigid leaf
      whose STL is still not current after its materialization is refused
      with :exc:`~machinome.node.base.ArtifactNotProduced`, naming it,
      before any process starts.

   .. attribute:: rigid

      True for a time-invariant solid with a cached STL, in the piece and
      artifact sets: the default. A class attribute.

   .. attribute:: flexible

      True for a leaf whose shape is a function of its bound ports
      (:class:`~machinome.node.flexible.FlexibleNode`); false by default. A
      class attribute.

   .. attribute:: brep

      Whether the node exposes B-rep geometry, a boundary representation,
      through ``shape()``; false by default. A property.

   .. attribute:: optimize

      True, the default, for a presentation to import the leaf's STL;
      false for it to carry what the leaf rendered, in which case the leaf
      is prepared on every build. A class attribute.

   .. method:: base_mesh()

      The node's geometry in its own frame: its cached STL, or, for a
      flexible leaf, its evaluated binding.

   .. method:: declared_markings()

      The markings the node's class declares, by attribute name.

   The core reads every member of this set directly: a leaf declares its
   kind through them, and the core never probes for one.

   .. attribute:: files

      The node's tracked source set: its defining module and that
      module's project-local import closure. A subclass may add files to
      it after the base constructor has run; every artifact's currency is
      computed over it.

   .. attribute:: basepath

      The common stem of every artifact the node owns, under its project's
      build directory, named from its source file and its parameter-hashed
      identity. :meth:`publish_artifact` accepts only paths beginning with
      it.

   .. attribute:: stl_file

      Path of the node's ``.stl`` artifact.

   .. attribute:: local_stl

      The ``.stl`` artifact's name relative to the node's build directory,
      as :meth:`artifact_import` takes it.

   .. attribute:: model

      The node's presentation once assembled, or ``None`` before: the
      object :meth:`present` returned, or machinome's description of it. An
      OpenSCAD-family leaf sets it to its render result before writing its
      ``.scad``.

.. autoexception:: machinome.node.base.StlRenderStart

.. autoexception:: machinome.node.base.ArtifactNotProduced

.. autoclass:: machinome.node.brep_leaf.BrepLeafNode
   :members: shape_from_rendered, brep, shape

   .. attribute:: brep_file

      Path of the node's ``.brep`` artifact, its B-rep geometry.

   .. attribute:: linear_deflection

      The maximum distance, in millimetres, between this node's ``.stl``
      artifact and the surface it approximates (OCCT's own
      ``theLinDeflection``). Declared as a class attribute, like
      :attr:`~machinome.node.sheet_leaf.SheetLeafNode.thickness`; defaults
      to ``0.1``. See :ref:`tessellation-precision`.

   .. attribute:: angular_deflection

      The maximum angle, in radians, between the normals of two
      adjacent facets of this node's ``.stl`` artifact (OCCT's own
      ``theAngDeflection``). Defaults to ``0.1``. See
      :ref:`tessellation-precision`.

The OpenSCAD node family is the package ``machinome.node.openscad``
(``OpenScadNode``, its leaf base, its writer and its binary contract), with
``Solid2Node`` at ``machinome.node.solid2`` over it; SolidPython is its
kernel, installed by ``machinome[openscad]`` and ``machinome[solid2]``.

.. autoclass:: machinome.node.openscad.leaf.ScadLeafNode
   :members: present, materialize, kept_artifacts, generate_stl,
             generate_scad, stl_builder_command_for

   .. attribute:: fn

      Number of facets used to approximate curved surfaces, applied as
      OpenSCAD's ``$fn`` to the leaf's ``.scad``. The OCCT-backed leaves
      (``CadQueryNode``, ``Build123dNode``, the sheet leaves,
      ``MolejoNode``) export high-resolution STLs on their own. Default is
      ``None``, which keeps OpenSCAD's coarse default.

   .. attribute:: scad_file

      Path of the leaf's ``.scad``, beside its STL: written by its
      materialization and kept by the build.

   .. attribute:: scad_code

      The leaf's own SCAD text.

.. autofunction:: machinome.node.openscad.writer.scad_text

.. autofunction:: machinome.node.openscad.writer.scad_code

.. autofunction:: machinome.node.openscad.writer.generate_scad

.. autoclass:: machinome.node.solid2.Solid2Node
   :members: as_number

.. autoclass:: machinome.node.cadquery.CadQueryNode

.. autoclass:: machinome.node.build123d.Build123dNode

.. autoclass:: machinome.node.sheet_leaf.SheetLeafNode
   :members: profile, profile_faces, lies_on_xy_plane, extrude, write_dxf,
             render, validated_profile

   .. attribute:: thickness

      Thickness of the stock the part is cut from. Required and positive,
      declared as a class attribute or passed as a ``thickness=``
      constructor argument.

   .. attribute:: dxf_file

      Path of the node's nominal cut file, written beside its ``.stl``
      and ``.brep``.

.. autoclass:: machinome.node.build123d.Build123dSheetNode
   :members: profile

.. autoclass:: machinome.node.openscad.OpenScadNode
   :members: __init__

   .. attribute:: scad_source

      Path of the OpenScad source file, relative to the directory of the
      python file declaring the node. A path that resolves outside the
      project is refused when the node is constructed.

   .. attribute:: module_name

      Name of the module to call inside :attr:`scad_source`. Defaults to
      the file name without the ``.scad`` extension.

.. autoclass:: machinome.node.jscad.JScadNode

   .. attribute:: jscad_source

      Path of the JScad source file, relative to the directory of the
      python file declaring the node. The file must export a ``main``
      function. A path that resolves outside the project is refused when
      the node is constructed.

.. autoclass:: machinome.node.stl.StlNode

   .. method:: adjust(mesh)

      Optional hook correcting the selected body in code: receives a
      `trimesh <https://trimesh.org/>`_ mesh, returns the corrected
      one. Whatever it returns is what the artifact holds — and what
      the watertight gate judges.

   .. attribute:: stl_source

      Path of the ``.stl``, relative to the directory of the
      python file declaring the node. A path that resolves outside the
      project is refused when the node is constructed.

   .. attribute:: require_watertight

      ``True`` by default: a mesh that does not enclose a solid fails
      at build, naming the defect. Set to ``False`` to admit an open
      mesh knowingly; the flag never changes geometry.

   .. attribute:: body

      0-based index selecting one connected component of a multi-body
      file. A multi-body file with no ``body`` fails with a per-body
      inventory of centroid, bounds and volume.

.. autoclass:: machinome.node.step.StepNode

   A B-rep part selected from a STEP document. See :doc:`/howto/imported-parts`
   for source paths, product selection and `adjust()`.

.. autoclass:: machinome.node.flexible.FlexibleNode
   :members: tech, shape_parameters, shape_spec, snapshot_mesh, snapshot_stl,
             snapshot_shape, brep

.. autoclass:: machinome.node.molejo.MolejoNode
   :members: shape_tolerance

The two engines
------------------

Two engines do the geometry, each named for the representation it
consumes: the **B-rep engine**, over boundary representations, and the
**mesh engine**, over triangle meshes. Each is a module of the engine
package, ``machinome.engine.brep`` (installed by ``machinome[brep]``) and
``machinome.engine.mesh`` (installed by ``machinome[mesh]``), and the
package's own module holds the two seams that resolve them on first use.
A project rarely calls them: nodes, fusion and the assertions do. Which
engine a test run compares on is chosen by the run
(:doc:`/howto/fast-tests`).

.. py:function:: machinome.engine.brep_engine()

   The B-rep engine's module, resolved once per process, or ``None`` when
   it is not installed.

.. py:function:: machinome.engine.require_brep_engine(needed_by, reason)

   The B-rep engine's module, or ``BrepEngineUnavailable`` naming
   ``needed_by``, ``reason`` and ``pip install "machinome[brep]"``.

.. py:function:: machinome.engine.mesh_engine()

   The mesh engine's module, resolved once per process, or ``None`` when
   it is not installed.

.. py:function:: machinome.engine.require_mesh_engine(needed_by, reason)

   The mesh engine's module, or ``MeshEngineUnavailable`` naming
   ``needed_by``, ``reason`` and ``pip install "machinome[mesh]"``.

The B-rep engine's operations a project may call directly are
``intersect_shapes``, ``fuse_shapes``, ``placed_shape``, ``solid_count``
and ``solid_volume``, from ``machinome.engine.brep``; see
:doc:`assertions` for ``intersect_shapes`` and the two errors it raises,
``BrepCommonInconsistency`` and ``BrepCommonVerificationError``, which
``machinome.engine`` defines.

Internal nodes
------------------

.. autoclass:: machinome.node.internal.InternalNode
   :members: connect

.. autoclass:: machinome.node.assembly.AssemblyNode
   :members: simulate, set_state, set_keyframe, clear_keyframe, time

.. autoclass:: machinome.motion.ports.Time

.. autoclass:: machinome.node.fusion.FusionNode
   :members: time

   .. attribute:: linear_deflection

      The tessellation precision of this fusion's own fused solid, not
      inherited from its children. See
      :ref:`fusion-tessellation-precision`.

   .. attribute:: angular_deflection

      As above.

Parameters
==============

The knobs that decide what machine gets built, importable from
``machinome.parameters`` and from nowhere else. A parameter is declared
as a class attribute, is fixed for the life of an instance, enters the
node's build identity, and reads back inside ``render()`` as a plain
number. Contrast :class:`~machinome.simulation.Driver`, which is a
runtime input and changes every instant. See :doc:`Values </concepts/values>`.

.. autoclass:: machinome.parameters.Length

.. autoclass:: machinome.parameters.Angle

.. autoclass:: machinome.parameters.Count

.. autoclass:: machinome.parameters.Ratio

.. autoclass:: machinome.parameters.Scalar

.. autoclass:: machinome.parameters.Flag

.. autoclass:: machinome.parameters.Quantity

.. autofunction:: machinome.parameters.declared_parameters

.. autofunction:: machinome.node.declarative.declared_children

Ports
=========

Domain-typed connection points between nodes, importable from
``machinome.motion.ports``. A port is declared as a class attribute; the
parent assembly binds it every ``simulate()`` with
:meth:`~machinome.node.internal.InternalNode.connect`. See
:doc:`Relations </concepts/relations>`.

.. autoclass:: machinome.motion.ports.Port

.. autoclass:: machinome.motion.ports.RotationalPort

.. autoclass:: machinome.motion.ports.TranslationalPort

.. autoclass:: machinome.motion.ports.SignalPort

.. autofunction:: machinome.motion.ports.declared_ports

.. autofunction:: machinome.motion.ports.get_coordinate

.. autoclass:: machinome.motion.ports.RunBinder

.. autofunction:: machinome.motion.ports.set_coordinate

Joints
==========

The joint declarations, importable from
``machinome.motion.joints``. A joint is declared as a class attribute of
the node it moves and states where that node may move in its own frame.
A joint supplied at a child's declaration site instead uses the declaring
parent's frame. Reading a one-coordinate joint gives a port,
and binding that coordinate places the body. Two of the three
one-coordinate pairs turn or
slide the body; the third, ``Orbit``, CARRIES it round a line without
turning it, and derives the radius and the phase of that circle rather
than accepting them. ``Free`` is the one that is not a pair at all: the
six freedoms of a body with no parent to be jointed to, owning SIX
coordinates reached as ``chassis.pose.roll`` and reported by the port
enumerator under those dotted names. Several joints on one class compose
in declaration
order, first declared innermost, and a joint owning several coordinates
occupies one position in that order like any other. See
:doc:`Relations </concepts/relations>`.

.. autoclass:: machinome.motion.joints.Revolute

.. autoclass:: machinome.motion.joints.Prismatic

.. autoclass:: machinome.motion.joints.Orbit

.. autoclass:: machinome.motion.joints.Free

.. autoexception:: machinome.motion.joints.JointRangeError

.. autofunction:: machinome.motion.joints.declared_joints

An assembly may add a range to an existing scalar descendant with
``joint_path.constrain(range=(lo, hi))`` or to a moving mate, bare or by
path, with the same verb. A mate target resolves to its generated or referenced child joint.
Contributions intersect, never
replace, the joint's original limits. The method needs no import; see
:ref:`ancestor-joint-constraints` for scope, accepted bounds and refusals.

Frames and mates
====================

A frame is a named connector a node declares on itself, imported from
``machinome.node.frames``; a mate relates two
frames in an assembly's class body, ``<child>.<frame>.on(<frame>,
Revolute(...))`` or ``<child>.<frame>.on(<frame>, Prismatic(...))``, or
``<child>.<frame>.on(<frame>)`` for a part that is held, and needs no
import beyond ``Revolute`` or ``Prismatic``. A built node's
frames are read as numbers with ``resolved_frames``, and a mate's name,
ends and freedom off the class through ``declared_mates``. See
:doc:`Joints </concepts/joints>`.

``<child>.<frame>.on(<frame>, <child>.<joint>)`` instead attaches an
existing scalar ``Revolute`` or ``Prismatic`` of that same direct child.
It preserves the joint's name, order, arguments, scope and binding rules.
The mate handle reads and binds the original child coordinate in every
reference context, including relations, formulas and wiring sources;
it adds no assembly-owned port or coordinate id. ``declared_mates`` reports
the written joint path as its ``freedom``.

A fresh moving mate accepts ``Bound(expression, reads=(...))`` range sides,
whose reads belong to its declaring assembly. It may itself be a Bound
read, a ``constrain(range=...)`` target or the ``coordinate=`` selection
of a ``Turn``, ``Slide`` or ``Button``. Those contracts resolve to the
generated child joint; ordinary relations and bindings keep the mate's
assembly coordinate. An existing-joint handle uses the original joint and
its original Bound scope instead. A rigid mate accepts none of those coordinate uses.

.. autoclass:: machinome.node.frames.Frame

.. autofunction:: machinome.node.frames.declared_frames

.. autofunction:: machinome.motion.mates.declared_mates

.. autofunction:: machinome.node.frames.resolved_frames

.. autoclass:: machinome.node.frames.ResolvedFrame
   :members: rotation

.. autoclass:: machinome.motion.mates.Mate

Couplings
=============

The relation between two coordinates, importable from
``machinome.motion.couplings``. ``drives`` itself needs no import — it
is on every declaration that can name a coordinate — and this module
holds the law it carries, the errors it refuses with, and the
enumerator. An end may be several coordinates, joined with ``&`` (also
needing no import, and free on every declaration that carries
``drives``) or, on the driven side, written as a tuple. See
:doc:`Relations </concepts/relations>`.

.. autoclass:: machinome.motion.couplings.Affine

.. autoclass:: machinome.motion.couplings.Relation

.. autoclass:: machinome.motion.couplings.DerivedCoordinate

.. autoexception:: machinome.motion.couplings.CouplingError

.. autoexception:: machinome.motion.couplings.UnreachedCoordinate

.. autoexception:: machinome.motion.couplings.DoublyBound

.. autoexception:: machinome.motion.couplings.NotInvertible

.. autoexception:: machinome.motion.couplings.PrematureRead

.. autofunction:: machinome.motion.couplings.declared_relations

Simulation
==============

The stepped simulation layer lives in ``machinome.simulation``. See
:doc:`Relations </concepts/relations>` for drivers and instructions, and
:doc:`Three ways a machine runs </concepts/execution-models>` for the loop and
scenario tests.

.. autoclass:: machinome.simulation.Driver

.. autoclass:: machinome.simulation.Instruction

.. autoclass:: machinome.simulation.Button

.. autoclass:: machinome.simulation.Turn

.. autoclass:: machinome.simulation.Slide

.. autoclass:: machinome.simulation.RampProgram

.. autoclass:: machinome.simulation.Sim
   :members: at, every, trigger, run, state, time, trajectory, crossings,
             stops, running, identity, move, rate, commands, snapshot,
             restore, reset, initial, program, cadence_costs,
             assertion_stats

Running simulation
------------------

Under a root declaring ``Time.running()`` a simulation owns every driver
and every joint coordinate of the linked tree, keeps their history and
moves them by increments. The engine and the compile step below are
imported only when such a simulation is constructed.

``time.drives(joint, ratio=...)`` and ``(time & inputs).drives(...)``
admit the root's elapsed seconds as an explicit read-only source. Each
time-source relation has an independent stop identity; no clock is added
to the bank or commands. See :doc:`/concepts/running` for retained-motion
semantics and pause/resume examples.

.. autoclass:: machinome.simulation.run.Run

.. autoclass:: machinome.simulation.run.Command
   :members: requested, admitted, remaining, rate, cancel

.. autoclass:: machinome.simulation.run.RunSnapshot

.. autoexception:: machinome.simulation.RunConflict

.. autoclass:: machinome.simulation.program.Program
   :members: described, published, published_names

.. autofunction:: machinome.simulation.program.compile_program

.. autofunction:: machinome.simulation.program.program_of

.. autofunction:: machinome.simulation.program.release_tree

.. autofunction:: machinome.simulation.program.qualified_coordinates

.. autoclass:: machinome.simulation.program.JumpPlan

.. autoclass:: machinome.simulation.Crossing

.. autoclass:: machinome.simulation.Stop

For running stops, ``inputs`` contains actual blocked driver IDs.
``time_drives`` is a separate, default-empty tuple of blocked time-drive
IDs. Serialized conformance records omit ``time_drives`` when it is empty.

.. autoexception:: machinome.simulation.UnsupportedLaw

.. autoexception:: machinome.simulation.TooManyCrossings

.. autoclass:: machinome.simulation.ScenarioTest
   :members: simulation, scenario_node

.. autofunction:: machinome.simulation.qualified_drivers

.. autofunction:: machinome.simulation.qualified_instructions

Clocked simulation
------------------

Under a root whose tree declares a ``State`` a simulation holds a BANK of
every driver and every state and moves it on REQUESTS, each a straight
path whose every rising event is solved exactly. There is no ``dt``, and
the executor below is imported only when such a simulation is
constructed.

``sim.trigger(name)`` under such a root is one request — the one the
named instruction states — and returns it.

``sim.identity`` is the machine's identity, the string an export of the
same model carries as ``clocked.identity`` whatever the bank holds, so a
recording made through ``Sim`` can be refused against an export whose
machine differs; under any other root it is refused by name.

.. autoclass:: machinome.simulation.clocked.Clocked
   :members: move, state, commits, stops, snapshot, restore, reset

``initial`` is a ``ClockedSnapshot`` of the initial bank. Restore it
through the simulation's session API to return to that state.
``Sim.trigger(name)`` dispatches the instruction as one clocked request.

.. autoclass:: machinome.simulation.clocked.Request

.. autoclass:: machinome.simulation.clocked.Commit
   :members: relation

.. autoclass:: machinome.simulation.clocked.ClockedSnapshot

.. autoexception:: machinome.simulation.clocked.ClockedError

The conformance corpus
----------------------

``tools/generate_running_corpus.py`` writes ``tests/running-corpus.json``
from the framework's own run: for each of a set of small running roots,
the program-bearing keys of the document it publishes, a script of
commands, and every tick of the run with its bank, crossings, stops and
command outcomes. Every expected value in it is a value the run
PRODUCED, never one recomputed a second way, so a disagreement means the
other runtime drifted. The framework's suite replays it
(``tests/test_running_corpus.py``) and the browser viewer replays its own
committed copy.

The generator refuses to write a corpus that misses any of the features
the export capability lists — each discontinuous primitive, a
multi-source law, a stop inside a tick, an expression bound, a blocked
command, a rate, a snapshot and a restore, both instruction forms, and a
tick carrying both a crossing and a stop — so the corpus's width cannot
narrow by accident.

.. code-block:: bash

    $ PYTHONPATH="$PWD" python tools/generate_running_corpus.py

Explicit time drives have a separate producer corpus,
``tests/time-drive-corpus.json``, generated by
``tools/generate_time_drive_corpus.py`` and replayed by
``tests/test_time_drive_corpus.py``. Its seven scenarios cover autonomous
motion, enable at nonzero time, winding and exhaustion, connected and
independent stops, curved upstream motion, mixed commanded sources, and
snapshot/restore/reset. Expected ticks include elapsed time, bank,
crossings, stop provenance and command outcomes. The legacy corpus stays
unchanged. The independent viewer must consume this new corpus before
claiming version-10 execution support.

Version-10 ``program.time_drives`` is an ordered list of objects such as
``{"id": "@time:0", "edge": 0}``, indexing the flattened published edge
list. Each named edge reads ``time`` in ``needs`` and never writes it in
``gives``; its targets share the drive identity. ``program.sources`` lists
these IDs beside real driver IDs, but time is absent from ``coordinates``,
``intermediates``, ``drivers`` and controls. The mapping participates in
program identity. Programs without time drives omit the field and retain
their previous document versions and bytes.

Expression math
===================

``machinome.math`` is the one expression semantics: OpenSCAD's degree
conventions, computed on plain numbers, deferred as an OpenSCAD
expression when a value is symbolic (animation time or a driver), and
carrying dimension rules when a value is a declared parameter. See
:doc:`/howto/timeline`.

Every function here has all three faces, so one formula serves the
tests, the build and the browser.

Primitives
--------------

The functions the module emits as an OpenSCAD call. Every name it can
emit is listed in ``machinome.math.SYMBOLIC_BUILTINS``, and each is a
builtin OpenSCAD and JavaScript's ``Math`` both carry with the same
semantics.

.. autofunction:: machinome.math.sin
.. autofunction:: machinome.math.cos
.. autofunction:: machinome.math.tan
.. autofunction:: machinome.math.asin
.. autofunction:: machinome.math.acos
.. autofunction:: machinome.math.atan
.. autofunction:: machinome.math.atan2
.. autofunction:: machinome.math.sqrt
.. autofunction:: machinome.math.abs
.. autofunction:: machinome.math.floor
.. autofunction:: machinome.math.ceil
.. autofunction:: machinome.math.sign
.. autofunction:: machinome.math.min
.. autofunction:: machinome.math.max

There is deliberately no ``round`` and no ``mod``: OpenSCAD, JavaScript
and Python round halves three different ways, and OpenSCAD spells
modulo as the ``%`` operator rather than a function. ``floor(x + 0.5)``
is the half-up every runtime agrees on.

Compositions
----------------

Built out of the primitives and ordinary arithmetic, so what they do to
dimensions follows from the primitives' rules rather than from a rule of
their own.

.. autofunction:: machinome.math.clamp
.. autofunction:: machinome.math.clamp01
.. autofunction:: machinome.math.ramp
.. autofunction:: machinome.math.lerp
.. autofunction:: machinome.math.wrap
.. autofunction:: machinome.math.piecewise
.. autofunction:: machinome.math.bump

Vector helpers
------------------

Composition over the scalar functions, so a symbolic component or a
declared formula rides through. Angles are degrees, positive
counter-clockwise, as everywhere else.

.. autofunction:: machinome.math.polar
.. autofunction:: machinome.math.turn
.. autofunction:: machinome.math.rotate_x
.. autofunction:: machinome.math.rotate_y
.. autofunction:: machinome.math.rotate_z

Mechanics helpers
==================

The gear, screw, crank, cam, indexing, delta, linkage, rolling and belt
formulas, twenty-four in all, belong to the independent `Machinome
Mechanics package <https://machinome-mechanics.readthedocs.io/en/latest/>`_,
the mechanics helpers for this framework, released with it as
|mechanics_version|. Select it with ``machinome[mechanics]`` and import
from ``machinome_mechanics``; its `getting started page
<https://machinome-mechanics.readthedocs.io/en/latest/getting-started.html>`_
covers installation and migration. ``machinome.mechanisms`` is no longer
a framework API.

The `complete helper reference
<https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html>`_
documents every signature, parameter, return value, coordinate convention
and domain limit, with examples. The functions compose over
``machinome.math`` and accept numeric or symbolic inputs. Use resolved
parameters in relation law factories; the mechanics manual includes a
`worked piston law
<https://machinome-mechanics.readthedocs.io/en/latest/using-with-machinome.html>`_
and explains the limit on dimensional class-body formulas. See
:doc:`/concepts/relations` for the framework's relation semantics.

Testing
===========

The testing API lives in ``machinome.test``. See
:doc:`the assertion reference <assertions>` for a walkthrough of both ways of
writing tests: mixing ``TestCaseMixin`` into a node class, or writing a
``TestCase`` in a separate file.

.. autoclass:: machinome.test.TestCase
   :members:

   ``assertNoDisconnectedSolids(node)`` checks that every topmost rigid solid
   in a subtree is one connected body. ``assertNoSolidInterference(node)``
   checks that those same printed solids have no positive-volume world-space
   overlap at the runner's current keyframe; exact boundary contact passes and
   there is no public overlap epsilon.
   ``assertAssemblySupported(node, gravity=(0, 0, -1), max_drop=1.0,
   ground=None, supports=None, stability_margin=0.0)`` checks the physical
   inverse over the same selection: that every printed solid is transitively
   held against gravity, proved by dropping it ``max_drop`` into whatever
   holds it, and that the assembly can then stand — that push-only normal
   forces over the contacts detected by that drop and by a symmetric lift
   balance every solid's weight and torque. ``stability_margin`` (mm) shrinks
   each contact patch toward its centroid first, so a balance that lives on a
   patch boundary can be rejected. The older
   ``assertNoPairwiseIntersections`` leaf sweep is deprecated and retained
   only for compatibility.

.. autoclass:: machinome.test.TestCaseMixin

.. autofunction:: machinome.test.testing_steps

.. autofunction:: machinome.test.testing_instant

Decorators
==============

.. autofunction:: machinome.node.decorators.property_as_number
