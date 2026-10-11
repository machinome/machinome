Simulate a native FreeCAD assembly
==================================

A ``FreeCADAssemblyNode`` is one native FreeCAD assembly: one grounded
tree of rigid occurrences joined by fixed and revolute connections, read
by FreeCAD itself in a separate process when the node is constructed.
The project declares no joint, axis, frame, zero or limit; the source
owns them, and the node compiles them into ordinary nodes, joints and
B-rep leaves. A ``FreeCADJoint`` names one of its revolutes so a driver
can move it. FreeCAD's other workbenches, loops, dynamics and inverse
kinematics are outside it.

Set up FreeCAD
--------------

Install the node package:

.. code-block:: bash

    pip install "machinome[freecad]"

That installs no FreeCAD. The runtime the package is measured with is
the official FreeCAD 1.1.4 AppImage for Linux x86-64 (SHA-256
``f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434``,
git build ``4fd3bf320d9566a27e60069fc8387448aaa3a094``), extracted, with
``MACHINOME_FREECAD_ROOT`` set to the extraction's root, the directory
that holds ``AppRun``, ``usr/lib``, ``usr/Mod`` and ``usr/Mod/Assembly``.
Other systems, versions and layouts are untested. Nothing downloads
FreeCAD, guesses an executable from the working directory or falls back
to FreeCAD's interface. Importing the package and declaring a class need
no runtime; constructing an instance does, and without one it is refused
naming ``MACHINOME_FREECAD_ROOT``.

Open trusted documents only. Restoring a FreeCAD document runs the Python
it carries, and the separate process keeps FreeCAD's Python and OCCT
apart from the project's; it is not a sandbox.

Declare the assembly
--------------------

Put the class in an ordinary project, whose ``pyproject.toml`` names it
under ``[tool.machinome]`` as its ``model``:

.. code-block:: python

    from machinome.node.freecad import FreeCADAssemblyNode, FreeCADJoint
    from machinome.motion.ports import Time
    from machinome.simulation import Driver, Sim

    class DumE(FreeCADAssemblyNode):
        freecad_source = "cad/MA_Dum_E_v2_Assembly.FCStd"
        time = Time.running()
        turntable = FreeCADJoint("Joint001")
        turn = Driver(default=0, unit="deg")
        turn.drives(turntable)

    node = DumE()
    sim = Sim(node, dt=0.02)
    command = sim.move("turn", to=150, duration=1.0)
    sim.run(1.0)
    print(command.status, node.turntable.value)

``freecad_source`` is a string or a path-like object. A relative path
resolves from the Python module that declared the attribute, whatever
the working directory and through inheritance. The document must belong
to that module's project, as every source a node declares does. The
source is checked when an instance is constructed, before relations
resolve and before ``Sim`` enumerates or compiles the graph.

FreeCAD resolves the document's external links itself; keep their
relative layout when moving the project. A linked document may sit in a
sibling directory, not only beside the assembly.

Drive a joint
-------------

``FreeCADJoint`` selects an existing revolute by its internal FreeCAD
``Name``, which FreeCAD's property editor shows; the editable ``Label``
is not a selector. It takes nothing else:
``FreeCADJoint("Joint001", axis=..., range=...)`` is refused, since the
source owns those facts.

The alias on an instance is the joint's own coordinate, so
``node.turntable.value`` reads the physical angle in degrees. It adds no
coordinate of its own: two aliases of one Name read the same value, and
the ordinary rule against two writers refuses two drivers commanding it.
Two instances of one class own separate coordinates and node trees.

A driver commands the native coordinate, whose zero is the native zero,
not the pose saved in the document. Revolutes no driver commands keep
their saved native coordinates, through repeated rendering and every
fresh ``Sim``.

Only the limit sides enabled in the document bound the joint; a disabled
side is unbounded, even beside an enabled one. A driver's ``range=`` is
presentation, not a mechanical bound. An initial request outside the
bounds is refused before a running program is compiled. A move that
reaches an enabled stop ends with ``command.status`` ``"blocked"``; one
whose target is admitted ends ``"completed"``. ``sim.state`` holds the
physical coordinates and the drivers' values, and ``sim.stops`` the
stops observed while running.

What is refused
---------------

A missing selector, or one naming a fixed connection, is refused naming
the source, the selector, its type when it has one, and the moving Names
available. An alias no driver uses is checked too. A reference declared
on another, unrelated model cannot be a target here.

The document must hold exactly one native ``Assembly::AssemblyObject``
with one grounded occurrence, rigid occurrences, and unsuppressed fixed
and revolute connections forming one connected tree without loops. Every
occurrence and every fixed connection is kept: fixed solids stay
separate rather than fused. Which end of a joint is the carrier comes
from the tree rooted at the ground, not from the joint's endpoint order.
Unknown connection objects, other joint types, suppression, loops,
disconnected objects, several groundings, unresolved references,
non-solid shapes and non-rigid scale are refused by name.

FreeCAD must recompute the document and solve the assembly. After the
recompute and again after the solve, every joint's connector markers must
agree within 0.01 mm and 0.001 degree: both joint types need coincident
connector origins; a fixed connection needs the direction cosines
``(Iy·Jx, Iz·Jx, Iz·Jy)`` at zero, which admits identity and the three
half-turn branches and no other relative orientation; a revolute needs
``(Iz·Jx, Iz·Jy)`` at zero, parallel or antiparallel Z axes with free
twist. The tolerance on the raw direction cosines is ``sin(0.001°)``.
These are the conventions of FreeCAD's own solver, not mechanics the
project declares.

The solve must also keep the saved placements within 0.01 mm and 0.001
degree: a source that drifts further is refused rather than quietly
replacing the saved assembly. A solver status of 0 alone is not enough.
A refusal names the source, the assembly, the joint and its endpoints,
the measured residuals and the tolerances. Nothing repairs a source,
changes a constraint or invents a fixed transform: correct the document
in FreeCAD.

After an edit
-------------

After changing the document or a document it links, construct a fresh
model and a fresh ``Sim``; a running simulation is never reinterpreted in
place. Each fresh construction asks FreeCAD to read the document, then
reads it again with everything the first read observed, recomputes,
checks the solve, and refuses a source that changed between the two.
Content digests detect an edit even when the size and modification time
are restored. A snapshot of the result is reused only after that
exchange, and never shares nodes or coordinates between models. Each
fresh model costs two FreeCAD processes: correctness first, not live
synchronisation.

Each occurrence's solid comes from FreeCAD as BREP in its own frame and
is read through the B-rep engine. The occurrence is an ordinary B-rep
leaf, whose artifacts the build writes as for any other part, and the
carrying poses are ordinary operations, so the build, the exports, the
snapshot and the viewer read the assembly like any other. The source's
geometry and the recipe that read it take part in the artifacts'
currency: a model whose document changed is refused when its geometry is
used; rebuild it. A source that changes while a leaf is written leaves
that leaf's previous artifacts restored, or none.

Compare poses
-------------

Every surface a numerical comparison needs is public: ``render()`` gives
a node's children, each node has ``name`` and ``operations``, each
operation has ``matrix()``, and a B-rep leaf has ``shape()``:

.. code-block:: python

    import numpy as np

    def occurrence_poses(node, parent=None, path=()):
        parent = np.eye(4) if parent is None else parent
        rendered = node.render()
        local = np.eye(4)
        for operation in node.operations:
            local = operation.matrix() @ local
        world = parent @ local
        yield path + (node.name,), world
        if isinstance(rendered, (list, tuple)):
            for child in rendered:
                yield from occurrence_poses(child, world, path + (node.name,))

    # Bind operating defaults through Sim first, then inspect poses.
    sim = Sim(node, dt=0.02)
    poses = dict(occurrence_poses(node))

The names are the native occurrence Names, kept through reparenting. A
``solid`` child is a B-rep leaf in its carrier's own frame, and nested
carriers compose parent first. Compare these matrices with a reference
FreeCAD computes independently; do not recover a physical zero or a
limit from the rendered shape alone.
