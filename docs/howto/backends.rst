Choose and mix part backends
============================

A leaf node is one part, built by one modelling technology. Every kind
below produces the same box with a hole, and every kind takes part in an
assembly, a fusion, a test and an export the same way. Choose by what you
already know and by what the part needs; a project may mix them freely.

.. list-table::
   :header-rows: 1
   :widths: 22 30 12 36

   * - Class
     - You write
     - Exact
     - Needs
   * - ``CadQueryNode``
     - ``render()`` returning a ``Workplane``
     - yes
     - nothing
   * - ``Build123dNode``
     - ``render()`` returning a ``Part``, ``Solid``, ``Compound`` or ``BuildPart``
     - yes
     - nothing
   * - ``Build123dSheetNode``
     - ``profile()`` plus ``thickness``
     - yes
     - nothing (:doc:`sheet-parts`)
   * - ``StepNode``
     - ``step_source`` and a product name
     - yes
     - nothing (:doc:`imported-parts`)
   * - ``Solid2Node``
     - ``render()`` returning a SolidPython object
     - no
     - OpenSCAD
   * - ``OpenScadNode``
     - ``scad_source`` naming a module
     - no
     - OpenSCAD
   * - ``JScadNode``
     - ``jscad_source`` exporting ``main``
     - no
     - the ``jscad`` command
   * - ``StlNode``
     - ``stl_source``
     - no
     - nothing (:doc:`imported-parts`)
   * - ``MolejoNode``
     - ``render()`` returning a molejo ``Shape``
     - yes
     - nothing (:doc:`flexible-parts`)

**Exact** parts keep their boundary representation: a ``.brep`` beside
the STL, an exact fusion with other exact parts, and geometric tests
decided by the OCCT kernel with no tolerance. Faceted parts are meshes
from the moment they are built, and a fusion holding one becomes faceted
and routes through OpenSCAD.

CadQuery
--------

.. code-block:: python

    import cadquery as cq
    from machinome.node import CadQueryNode

    class Box(CadQueryNode):

        def render(self):
            wp = cq.Workplane("XY")
            cube = wp.box(50, 50, 50)
            hole = wp.workplane(offset=-50).circle(10).extrude(100)
            return cube.cut(hole)

To keep using CQ-editor on the same file, add a guard that does not
conflict with Machinome:

.. code-block:: python

    if __name__ == '__cq_main__':
        show_object(Box().render())

build123d
---------

Either of build123d's two styles works. Builder mode:

.. code-block:: python

    from build123d import BuildPart, Box, Cylinder, Mode
    from machinome.node import Build123dNode

    class Box(Build123dNode):

        def render(self):
            with BuildPart() as part:
                Box(50, 50, 50)
                Cylinder(radius=10, height=100, mode=Mode.SUBTRACT)
            return part.part

Algebra mode:

.. code-block:: python

    from build123d import Box, Cylinder
    from machinome.node import Build123dNode

    class Box(Build123dNode):

        def render(self):
            return Box(50, 50, 50) - Cylinder(radius=10, height=100)

Returning the builder itself instead of its ``.part`` also works. A leaf
is one part, so ``render()`` must produce a solid; a sketch or a curve is
refused naming the node, rather than failing later in the STL export.

CadQuery and build123d are both OCCT front ends, so a fusion may take
children from either and fuse them exactly.

SolidPython and OpenSCAD
------------------------

``Solid2Node`` wraps SolidPython 2, a Python front end for OpenSCAD:

.. code-block:: python

    from machinome.node import Solid2Node
    from solid2 import cube, cylinder, translate

    class Box(Solid2Node):

        def render(self):
            return translate(-25, -25, 0)(
                cube(50, 50, 50)
            ) - cylinder(r=10, h=100)

``translate`` here is a SolidPython primitive applied inside the part.
Nodes also have a ``translate()`` method of their own, which positions a
part within an assembly; :doc:`/concepts/rest-and-motion` keeps the two
apart.

``OpenScadNode`` wraps one module of an existing ``.scad`` file:

.. code-block:: python

    from machinome.node import OpenScadNode

    class Box(OpenScadNode):

        scad_source = 'demo.scad'

.. code-block:: openscad

    module demo() {
      difference() {
        translate([-25, -25, 0]) cube([50, 50, 50]);
        cylinder(r=10, h=100);
      }
    }

The module is expected to have the file's name unless ``module_name``
says otherwise, and the node's constructor arguments are forwarded to it,
so one ``.scad`` module can back several parametrized nodes:

.. code-block:: python

    class Box(OpenScadNode):

        scad_source = 'shapes.scad'
        module_name = 'box_with_hole'

    box = Box(50, hole_radius=10)

A ``scad_source`` that does not resolve to a file is refused when the node
is constructed, naming the class, the attribute and the resolved path.
:doc:`simulate-existing` shows a whole printer read this way.

Resolution
~~~~~~~~~~

OpenSCAD approximates circles by polygons, and its default is coarse: a
small hole comes out as a hexagon, and a hexagonal hole is tighter than
the circle it stands for. Set ``fn`` on the node to raise the segment
count:

.. code-block:: python

    class Pointer(Solid2Node):

        fn = 256

``fn`` affects only ``Solid2Node`` and ``OpenScadNode``. The OCCT-backed
kinds tessellate their exact geometry themselves, and
:doc:`imported-parts` shows how to set that tessellation's precision.

JSCAD
-----

``JScadNode`` wraps a JavaScript module whose ``main`` returns the
geometry. It needs the ``jscad`` command on the ``PATH`` and its node
dependencies installed in the directory you run ``machinome`` from.

.. code-block:: python

    from machinome.node import JScadNode

    class Box(JScadNode):

        jscad_source = 'demo.js'

.. code-block:: javascript

    const { square, circle } = require('@jscad/modeling').primitives
    const { subtract } = require('@jscad/modeling').booleans
    const { extrudeLinear } = require('@jscad/modeling').extrusions

    function main() {
      const shape = subtract(square({size: 50}), circle({radius: 10}));
      return extrudeLinear({height: 50}, shape);
    }

    module.exports = { main }

Colour
------

Any node may set ``color``, a hex RGB string the viewer and the exports
honour. Anything else is refused.

.. code-block:: python

    class Pointer(CadQueryNode):

        color = '#cc4444'

A ``StepNode`` that declares no colour takes the product's colour from
the document.
