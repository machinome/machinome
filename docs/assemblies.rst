
.. _assemblies:

===============
Combining parts
===============

Parts become a project when they are combined by **internal nodes**.
An internal node declares child nodes instead of returning a CAD solid.
Its `render()` can place those children at rest; if no extra placement
is needed, the declarations are enough. What moves, and the values wired
between parts in a driven machine, belong to the assembly's `simulate()`;
see :doc:`Animating
with time <animation>`.

There are two types of internal nodes:

* **AssemblyNode** — the children are separate parts that can move
  relative to each other. This is the node you'll use the most, and
  the subject of this page.
* **FusionNode** — the children are fused into one rigid, inseparable
  piece. Covered in :doc:`Fusing parts <fusion>`.

Both take part in the node tree the same way: an assembly can contain
leaf nodes, fusions and other assemblies.

We will add one part at a time, then combine them using the 0.7 declarative
API. Later, :doc:`declaring` explains how to pass parameters between
those parts and repeat a unit.

The simple clock
================

Let's make a very simple clock, as a proof of concept, mixing together
CadQuery and SolidPython. This example continues through
:doc:`Animating with time <animation>` and :doc:`Test-driven CAD
<testing>`.

Create a new file `myproject/clock_base.py` and create a `CadQueryNode`:

.. code-block:: python

    import cadquery as cq
    from machinome.node import CadQueryNode

    class ClockBase(CadQueryNode):

        def render(self):
            wp = cq.Workplane("XY")
            return wp.circle(100).extrude(2)

Rendered — the clock base:

.. machinome:: _exports/clock_base
   :height: 360px

Now, a file `myproject/pointer.py` with a `Solid2Node`:

.. code-block:: python

    from machinome.node import Solid2Node
    from solid2 import cube, cylinder, translate

    class Pointer(Solid2Node):

        def render(self):
            return translate(-5, -5, 3)(
                cube(10, 90, 10)
            )

Rendered — the pointer:

.. machinome:: _exports/pointer_plain
   :height: 360px

And at `myproject/myproject.py`, an `AssemblyNode`:

.. code-block:: python

    from machinome.node import AssemblyNode
    from .clock_base import ClockBase
    from .pointer import Pointer

    class SimpleClock(AssemblyNode):

        base = ClockBase()
        pointer = Pointer()

Rendered — base and pointer assembled (still, for now):

.. machinome:: _exports/simple_clock_static
   :height: 360px

Update ``pyproject.toml`` to select the new assembly class:

.. code-block:: toml

    [tool.machinome]
    model = "myproject.myproject:SimpleClock"

If the starter's ``test_myproject.py`` still imports ``Myproject``,
update that import and its ``node`` declaration to ``SimpleClock``
too. We will replace the starter's tests in :doc:`testing`.

Run ``machinome develop`` again. You should see a round clock base with
a pointer. The base occupies Z=0..2; the pointer starts at Z=3, leaving
a 1 mm gap. The pointer points along +Y and its pivot is at the origin.
Those coordinates will matter when we make it turn.

Declarations become instance children
======================================

``base = ClockBase()`` in the class body is a child declaration,
not one shared Python object. Constructing a ``SimpleClock``
creates its own ``self.base`` and ``self.pointer``.
The framework also derives their tree names from those attributes.

Open the tree in the viewer and select ``pointer``. That name
identifies this occurrence of the part; it is separate from the
geometry's build identity. Two pointers can share cached geometry
while occupying different positions.

To place a child without changing its geometry, add a ``render()``
to the assembly and call that child's ``translate()`` or
``rotate()`` there. It may return nothing because the child list
is already declared. Keep time-dependent motion out of this method.

Existing projects may instead create children in ``__init__``
and return them from ``render()``; that form remains supported.
See :doc:`node-tree` for naming and cache rules.

Assemblies declare the machine's inputs
=======================================

The assembly is also where a machine's named inputs live. A **driver**
is a class attribute, read back as an ordinary attribute in
``simulate()``:

.. code-block:: python

    from machinome.simulation import Driver

    class Axis(AssemblyNode):
        # Rail and Carriage are parts supplied by the project.
        rail = Rail()
        carriage = Carriage()

        position = Driver(default=20.0, range=(0.0, 160.0), unit='mm')

        def simulate(self):
            self.carriage.translate([self.position, 0, 0])

The viewer turns drivers into sliders and declared instructions into
buttons, scoped to the assembly layer that declares them: an
assembly's controls appear when *it* is focused, so declare each input
on the assembly the input belongs to — an axis's travel on the axis,
the whole machine's ``Home`` on the machine. An assembly also wires
values between its children with ``connect()``, binding an expression
over its drivers to a child's port. Drivers, qualified ids, ports and
instructions are the subject of :doc:`Driving a machine <driving>`.

Assemblies are testable
=======================

Because an assembly knows its parts and their placements, the
:doc:`test framework <testing>` can interrogate it as a whole: that
parts do not interfere, that they form the connections the design
intends — and, with ``assertAssemblySupported``, that the assembly
actually rests on the ground and balances under gravity instead of
floating where the code put it.

Next, :doc:`animate the pointer <animation>`.
