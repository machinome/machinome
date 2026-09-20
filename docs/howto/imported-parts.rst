Reuse a vendor STEP or an STL
=============================

Plenty of the parts a machine needs are not yours to model: a bought
bearing published as STEP, a bracket someone shared as an STL, a whole
vendor assembly. Two leaf kinds bring such files into a project as
ordinary parts, and one command scaffolds an assembly from a STEP
document's structure.

.. _stl-import:

A part from an STL
------------------

Commit the ``.stl`` beside the module that declares it, and name it:

.. code-block:: python

    from machinome.node import StlNode

    class Bracket(StlNode):

        stl_source = 'bracket.stl'

That is the whole declaration for a well-behaved file. ``render()`` is
not an extension point; the part is the mesh. The node materializes its
own artifact from the file, and that artifact is what the assembly, a
fusion, the viewer, the export and the tests all see. Two things make it
stale, and both are tracked: the file, and the module that declares the
node, because ``adjust()`` below can change the geometry.

Watertight, or knowingly not
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A mesh with holes in its surface encloses nothing, so an open mesh fails
the build naming the file and the defect, and no artifact is written:

.. code-block:: text

    Bracket: /home/me/rc-car/parts/bracket.stl is not watertight --
    3 open edges leave the surface unclosed, so the mesh encloses no
    solid. Repair the mesh, or declare `require_watertight = False` on
    Bracket to admit it knowingly.

Nothing is repaired for you. If the mesh is known to be open and wanted
anyway, say so with ``require_watertight = False``. The flag governs
admission only; it never changes geometry.

A body from a pack
~~~~~~~~~~~~~~~~~~

A print pack holds several parts in one file. Declare which body the
node is:

.. code-block:: python

    class Wheel(StlNode):

        stl_source = 'pack.stl'
        body = 0

``body`` indexes the file's connected components, ordered by centroid
(x, then y, then z), which reads roughly as plate order. A node that
omits it on a multi-body file fails with the pack's inventory, one line
per body with its centroid, bounds and volume, so the failure is the
discovery tool. Extraction keeps the file's coordinates; placing the
body is the assembly's job.

Correcting a mesh
~~~~~~~~~~~~~~~~~

Downloaded meshes arrive in inches, upside down, or far from the origin.
Corrections are code: implement ``adjust()``, which receives the selected
body as a `trimesh <https://trimesh.org/>`_ mesh and returns the
corrected one.

.. code-block:: python

    class Bracket(StlNode):

        stl_source = 'bracket.stl'

        def adjust(self, mesh):
            mesh.apply_scale(25.4)
            mesh.apply_translation(-mesh.centroid)
            return mesh

Whatever the hook returns is what the artifact holds, and what the
watertight gate judges.

What a mesh costs
~~~~~~~~~~~~~~~~~

An ``StlNode`` is faceted, and it makes any fusion holding it faceted:
the fusion routes through OpenSCAD and CGAL, which needs the ``openscad``
binary and can take minutes on a dense mesh. Assembling imported parts
without fusing them costs nothing extra. Mesh-only is the doctrine for
imported STLs: a mesh is not a boundary representation, and rebuilding
one from triangles guesses at intent. Model the part in a CAD backend if
you need it exact.

.. _step-import:

A part from a STEP document
---------------------------

STEP is what every CAD package and every vendor publishes, and a STEP
product is a boundary representation the moment it is read. ``StepNode``
is exact: ``shape()``, the ``.brep`` artifact, exact fusion, the spatial
assertions and tessellation precision all come for free, with no
external tool.

.. code-block:: python

    from machinome.node import StepNode

    class Bracket(StepNode):

        step_source = 'vendor/bracket.step'

Selecting a product
~~~~~~~~~~~~~~~~~~~

A STEP document is a tree of named products. ``part`` names the one this
node is:

.. code-block:: python

    class Gearbox(StepNode):

        step_source = 'vendor/gearbox.step'
        part = 'Output_Shaft'

A file with exactly one candidate product, one part alone or one part
wrapped in an assembly root, needs no ``part``. A document with several
candidates and no ``part``, or a ``part`` the document does not have,
fails with the document's inventory: one line per product with its kind,
occurrence count, solid count, bounds and volume. A sub-assembly is a
selectable product too, arriving with its components at their internal
placements.

Exporters often give several distinct products one generic name.
Naming a shared name fails describing every match with an index;
declare ``part_index`` beside ``part`` to choose, 1-based, in document
order.

The part arrives in its own frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A selected product's geometry is its own, unplaced shape, never an
occurrence's located copy. Placing it is your assembly's job, with the
same operations as any node. To take the placements from the document
itself, see ``import-step`` below.

Correcting and admitting
~~~~~~~~~~~~~~~~~~~~~~~~

``adjust()`` receives the selected product as a CadQuery ``Shape`` and
returns the corrected one. A product that holds no solid after
``adjust``, faces only, fails the build naming what it does hold; there
is no admission flag, because a face-only B-rep would break every fusion
and volume assertion. If a vendor published bare surfaces, sew them
knowingly:

.. code-block:: python

    from machinome.node.adapters.step import solids_from_faces

    class Battery(StepNode):

        step_source = 'vendor/robot.step'
        part = 'Battery'

        def adjust(self, shape):
            return solids_from_faces(shape, tolerance=0.05)

``solids_from_faces`` sews within the tolerance and wraps each closed
shell in a solid. It does not guarantee the shells close or that the
tolerance is right for this file. A subclass that declares no ``color``
takes the product's colour from the document, converted from linear RGB
to the sRGB hex the project writes everywhere else.

Reading a document is the expensive part, fourteen to seventeen seconds
measured on a 35 MB vendor assembly. A document is read at most once per
file per process and shared by every node selecting from it; a node whose
artifacts are current never triggers a read.

.. _tessellation-precision:

Tessellation precision
~~~~~~~~~~~~~~~~~~~~~~

Every exact leaf writes its STL by tessellating its solid, and may
declare how finely:

.. code-block:: python

    class OutputShaft(StepNode):

        step_source = 'vendor/actuator.step'
        part = 'Output_Shaft'
        angular_deflection = 0.5

``linear_deflection`` (mm, default 0.1) bounds the distance between the
mesh and the surface; ``angular_deflection`` (radians, default 0.1)
bounds the angle between adjacent facet normals. Vendor geometry is
fillets and threads, and 0.1 radian over such a part costs an order of
magnitude for surface a viewer cannot see: the shaft above measured
19.9 MB at the default and 1.8 MB at 0.5. Only the mesh changes; the
``.brep`` and ``shape()`` are identical whatever is declared. A coarser
mesh moves faceted-kernel verdicts and changes the printed-piece id, and
never touches the exact kernel. A fusion declares its own precision and
does not inherit a child's.

Scaffold an assembly from a STEP document
-----------------------------------------

.. code-block:: bash

    $ machinome import-step vendor/robot.step --into robot --model robot

reads the document's assembly structure and writes two files of
project-owned source: ``parts.py``, one ``StepNode`` subclass per part
product, and ``assembly.py``, one ``AssemblyNode`` per assembly product,
declaring one child per occurrence and a ``render()`` that places each at
the document's own transform. Every generated class is a product, never
a name, so a shared name gets a ``part_index``. The generated model is a
machine at rest: no driver, no ``simulate()``. Which joints move is a
design decision you make in the source the command hands you.

The command never overwrites, refuses a document with a mirrored or
scaled placement, and prints the manifest line to add rather than editing
``pyproject.toml``. :doc:`/reference/cli` has its options.
