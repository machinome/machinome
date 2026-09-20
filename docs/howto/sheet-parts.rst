Cut parts from sheet
====================

Some parts are not modelled, they are cut. A panel of plywood, MDF or
acrylic is a flat profile in stock of a known thickness, and what a laser
cutter needs is that profile, not a mesh of the finished part.

Author the profile
------------------

A ``Build123dSheetNode`` implements ``profile()`` instead of ``render()``
and declares the ``thickness`` of the stock:

.. code-block:: python

    from build123d import Circle, Rectangle
    from machinome.node import Build123dSheetNode

    class Panel(Build123dSheetNode):

        thickness = 6

        def profile(self):
            return Rectangle(50, 50) - Circle(10)

The node's solid is the profile extruded from the XY plane along +Z by
``thickness``; ``render()`` is not an extension point. The part you see
in the viewer, the STL you test against and the file you cut all come
from one authored profile, so they cannot drift apart.

The profile contract
--------------------

A sheet part is one piece: ``profile()`` must produce exactly one planar
face on the XY plane, a single outer boundary with any holes strictly
inside it. Two disjoint faces (author each piece as its own node), a
solid, a curve or a profile on another plane is refused naming the node,
before any file is written. ``profile()`` may return a ``Sketch``, a bare
``Face`` or the ``BuildSketch`` builder itself:

.. code-block:: python

    def profile(self):
        with BuildSketch() as sketch:
            Rectangle(50, 50)
            Circle(10, mode=Mode.SUBTRACT)
        return sketch

The thickness
-------------

``thickness`` is required and positive. As a class attribute it is a
per-class constant; as a constructor argument it reaches the artifact
key like any parameter, so one class covers a panel in two stocks:

.. code-block:: python

    class Panel(Build123dSheetNode):

        def __init__(self, thickness, **kwargs):
            super().__init__(thickness=thickness, **kwargs)

        def profile(self):
            return Rectangle(120, 80)

    thin = Panel(3)
    thick = Panel(6)

Because the thickness is a declared number, the profile can be derived
from it: a slot that receives a tab of the same stock is ``thickness``
wide plus a fit clearance, written once.

The cut file
------------

Every sheet part writes a DXF of its profile beside its ``.stl`` and
``.brep``, under the same name, whenever a build produces them. The DXF
is nominal: the authored profile at model scale in millimetres, circles
and arcs written as arcs rather than tessellated, so a hole reaches the
cutter as a hole. ``dxf_file`` is its path.

Deliberately not covered: kerf compensation (the ``.brep`` keeps the
exact profile, so an offsetting exporter remains possible), importing a
profile from SVG or DXF, engraving, material and process metadata, and
nesting several parts onto one sheet.

A sheet part is exact. It fuses exactly with CadQuery and build123d
parts, needs no OpenSCAD, and may declare tessellation precision for its
STL as any exact leaf may (:doc:`imported-parts`); the DXF comes from the
nominal profile, not from the tessellation.
