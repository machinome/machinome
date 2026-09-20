
.. _api-reference:

=================
API Reference
=================

Nodes
=========

All node classes are importable from ``machinome.node``; the parameters
they declare come from ``machinome.parameters``. A project is a
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

   .. attribute:: fn

      Number of facets used to approximate curved surfaces, applied as
      OpenSCAD's ``$fn`` to the generated code. Only meaningful for
      OpenSCAD-based nodes (``Solid2Node``, ``OpenScadNode``); the
      OCCT-backed leaves (``CadQueryNode``, ``Build123dNode``, the
      sheet leaves, ``MolejoNode``) export high-resolution STLs on
      their own. Default is ``None``, which keeps OpenSCAD's coarse
      default.

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

.. autoclass:: machinome.node.leaf.LeafNode
   :members: time

.. autoclass:: machinome.node.exact_leaf.ExactLeafNode
   :members: exact, shape

   .. attribute:: linear_deflection

      The maximum distance, in millimetres, between this node's ``.stl``
      artifact and the surface it approximates (OCCT's own
      ``theLinDeflection``). Declared as a class attribute, like
      :attr:`~machinome.node.SheetLeafNode.thickness`; defaults to
      ``0.1``. See :ref:`tessellation-precision`.

   .. attribute:: angular_deflection

      The maximum angle, in radians, between the normals of two
      adjacent facets of this node's ``.stl`` artifact (OCCT's own
      ``theAngDeflection``). Defaults to ``0.1``. See
      :ref:`tessellation-precision`.

.. autoclass:: machinome.node.Solid2Node
   :members: as_number

.. autoclass:: machinome.node.CadQueryNode

.. autoclass:: machinome.node.Build123dNode

.. autoclass:: machinome.node.SheetLeafNode
   :members: profile, render, validated_profile

   .. attribute:: thickness

      Thickness of the stock the part is cut from. Required and positive,
      declared as a class attribute or passed as a ``thickness=``
      constructor argument.

   .. attribute:: dxf_file

      Path of the node's nominal cut file, written beside its ``.stl``
      and ``.brep``.

.. autoclass:: machinome.node.Build123dSheetNode
   :members: profile

.. autoclass:: machinome.node.OpenScadNode
   :members: __init__

   .. attribute:: scad_source

      Path of the OpenScad source file, relative to the directory of the
      python file declaring the node.

   .. attribute:: module_name

      Name of the module to call inside :attr:`scad_source`. Defaults to
      the file name without the ``.scad`` extension.

.. autoclass:: machinome.node.JScadNode

   .. attribute:: jscad_source

      Path of the JScad source file, relative to the directory of the
      python file declaring the node. The file must export a ``main``
      function.

.. autoclass:: machinome.node.StlNode

   .. method:: adjust(mesh)

      Optional hook correcting the selected body in code: receives a
      `trimesh <https://trimesh.org/>`_ mesh, returns the corrected
      one. Whatever it returns is what the artifact holds — and what
      the watertight gate judges.

   .. attribute:: stl_source

      Path of the ``.stl``, relative to the directory of the
      python file declaring the node.

   .. attribute:: require_watertight

      ``True`` by default: a mesh that does not enclose a solid fails
      at build, naming the defect. Set to ``False`` to admit an open
      mesh knowingly; the flag never changes geometry.

   .. attribute:: body

      0-based index selecting one connected component of a multi-body
      file. A multi-body file with no ``body`` fails with a per-body
      inventory of centroid, bounds and volume.

.. autoclass:: machinome.node.StepNode

   An exact part selected from a STEP document. See :doc:`leaf-nodes`
   for source paths, product selection and `adjust()`.

.. autoclass:: machinome.node.FlexibleNode

.. autoclass:: machinome.node.MolejoNode
   :members: shape_tolerance

Internal nodes
------------------

.. autoclass:: machinome.node.internal.InternalNode
   :members: connect

.. autoclass:: machinome.node.AssemblyNode
   :members: simulate, set_state, set_keyframe, clear_keyframe, time

.. autoclass:: machinome.motion.ports.Time

.. autoclass:: machinome.node.FusionNode
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
runtime input and changes every instant. See :doc:`Declaring a machine
<declaring>`.

.. autoclass:: machinome.parameters.Length

.. autoclass:: machinome.parameters.Angle

.. autoclass:: machinome.parameters.Count

.. autoclass:: machinome.parameters.Ratio

.. autoclass:: machinome.parameters.Scalar

.. autoclass:: machinome.parameters.Flag

.. autoclass:: machinome.parameters.Quantity

.. autofunction:: machinome.parameters.declared_parameters

.. autofunction:: machinome.node.declared_children

Ports
=========

Domain-typed connection points between nodes, importable from
``machinome.motion.ports``. A port is declared as a class attribute; the
parent assembly binds it every ``simulate()`` with
:meth:`~machinome.node.internal.InternalNode.connect`. See
:doc:`Driving a machine <driving>`.

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
:doc:`Driving a machine <driving>`.

.. autoclass:: machinome.motion.joints.Revolute

.. autoclass:: machinome.motion.joints.Prismatic

.. autoclass:: machinome.motion.joints.Orbit

.. autoclass:: machinome.motion.joints.Free

.. autoexception:: machinome.motion.joints.JointRangeError

.. autofunction:: machinome.motion.joints.declared_joints

Couplings
=============

The relation between two coordinates, importable from
``machinome.motion.couplings``. ``drives`` itself needs no import — it
is on every declaration that can name a coordinate — and this module
holds the law it carries, the errors it refuses with, and the
enumerator. An end may be several coordinates, joined with ``&`` (also
needing no import, and free on every declaration that carries
``drives``) or, on the driven side, written as a tuple. See
:doc:`Driving a machine <driving>`.

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
:doc:`Driving a machine <driving>` for drivers and instructions, and
:doc:`Simulating and testing scenarios <scenarios>` for the loop and
scenario tests.

.. autoclass:: machinome.simulation.Driver

.. autoclass:: machinome.simulation.Instruction

.. autoclass:: machinome.simulation.Button

.. autoclass:: machinome.simulation.Turn

.. autoclass:: machinome.simulation.Slide

.. autoclass:: machinome.simulation.RampProgram

.. autoclass:: machinome.simulation.Sim
   :members: at, every, trigger, run, state, time, trajectory, crossings,
             stops, running, move, rate, commands, snapshot, restore,
             reset, initial, program, cadence_costs, assertion_stats

Running simulation
------------------

Under a root declaring ``Time.running()`` a simulation owns every driver
and every joint coordinate of the linked tree, keeps their history and
moves them by increments. The engine and the compile step below are
imported only when such a simulation is constructed.

``time.drives(joint, ratio=...)`` and ``(time & inputs).drives(...)``
admit the root's elapsed seconds as an explicit read-only source. Each
time-source relation has an independent stop identity; no clock is added
to the bank or commands. See :doc:`scenarios` for retained-motion semantics
and pause/resume examples.

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
:ref:`Non-linear kinematics <non-linear-kinematics>`.

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

The twelve gear, screw, crank, delta and linkage formulas belong to the
independent `Machinome Mechanics package
<https://machinome-mechanics.readthedocs.io/en/latest/>`_, the mechanics
helpers for this framework. Select it with ``machinome[mechanics]`` and
import from ``machinome_mechanics``. While publication is pending, follow
the manual's `source installation instructions
<https://machinome-mechanics.readthedocs.io/en/latest/getting-started.html>`_.
``machinome.mechanisms`` is no longer a framework API.

The `complete helper reference
<https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html>`_
documents every signature, parameter, return value, coordinate convention
and domain limit, with examples. The functions compose over
``machinome.math`` and accept numeric or symbolic inputs. Use resolved
parameters in relation law factories; the mechanics manual includes a
`worked piston law
<https://machinome-mechanics.readthedocs.io/en/latest/using-with-machinome.html>`_
and explains the limit on dimensional class-body formulas. See
:doc:`driving` for the framework's relation semantics.

Testing
===========

The testing API lives in ``machinome.test``. See
:doc:`Test-driven CAD <testing>` for a walkthrough of both ways of
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
