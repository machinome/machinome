Fuse parts into one piece
=========================

Sometimes several nodes describe one piece. A knob can be modelled as a
shaft plus a grip, two simple solids that are easier to write and read
separately, but it is a single rigid part, printed in one go. A
``FusionNode`` fuses its children into one solid.

.. code-block:: python

    from machinome.node import FusionNode

    from .knob_shaft import KnobShaft
    from .knob_grip import KnobGrip

    class Knob(FusionNode):

        shaft = KnobShaft()
        grip = KnobGrip()

Declare the children as above, or return a child list from ``render()``.
An empty assembly is allowed; an empty fusion is refused, because it
cannot keep its promise of a physical piece.

A fusion is rigid, so it has no ``self.time`` and reads no driver;
animate it from the assembly that holds it. For the same reason a fusion
refuses a flexible child outright, naming both nodes: a part whose shape
follows machine state cannot be baked into one rigid piece. Children may
be created in ``render()``, since they need no identity across renders.

What a fusion is made of
------------------------

A fusion is computed on the strongest representation its children share.

**Exact children fuse exactly.** When every child is OCCT-backed
(``CadQueryNode``, ``Build123dNode``, ``StepNode``, the sheet leaves), the
fusion is performed by the OCCT kernel on true solids: the result is
itself exact, persists a ``.brep`` beside its STL, and geometric
assertions against it are answered by the kernel. The children need not
share one backend.

**One faceted child makes the fusion faceted.** A ``Solid2Node``,
``OpenScadNode``, ``JScadNode`` or ``StlNode`` child routes the whole
fusion through OpenSCAD and CGAL, which needs the ``openscad`` binary and
answers questions on tessellated geometry. On a dense imported mesh that
can take minutes. When a fused part matters to exact assertions, author
its children on an OCCT backend.

.. _fusion-tessellation-precision:

Tessellation precision
----------------------

An exact fusion may declare ``linear_deflection`` and
``angular_deflection`` for the solid it fuses, as any exact leaf may
(:doc:`imported-parts`). A fusion does not inherit a declaration from its
children: the fused solid is a different shape from any of them, and
asking which child's precision should win has no defensible answer. Each
declaration shapes only the artifact of the node that declares it.

Fusions in assemblies
---------------------

A fusion takes part in the node tree like any other node, and this is
where fusing pays off: the whole knob is placed, turned and tested as one
part.

.. code-block:: python

    from machinome.node import AssemblyNode
    from machinome.simulation import Driver

    class VolumeControl(AssemblyNode):

        level = Driver(default=0.0, range=(0.0, 270.0), unit='deg')

        panel = Panel()
        knob = Knob()

        def simulate(self):
            self.knob.rotate(self.level, [0, 0, 1])

For whole-model tests a fusion is one **printed solid**: the assertions
that walk a tree stop at it and never compare its ingredients against
each other (:doc:`/concepts/node-tree`).

A file that defines two node classes is ambiguous to a bare path
reference; name the class you mean, ``panel_and_knob.py:VolumeControl``,
or declare it as a model (:doc:`several-models`).
