.. _flexible-parts:

Model springs, belts and cables
===============================

Every rigid leaf promises a part that holds still: whatever the machine
does, the geometry is the same solid moved around. A valve spring
compressed by its cam, a timing belt tensioned by an idler, a cable loom
dragged along by a carriage do not work that way. Their shape, not just
their placement, is a function of where the machine is.

A flexible leaf
---------------

A ``MolejoNode`` is that kind of part. Its ``render()`` returns a swept
shape, a closed profile carried along a path, described analytically
with `molejo <https://molejo.readthedocs.io>`_, with the moving
dimensions left as parameters fed through ports:

.. code-block:: python

    from molejo import Circle, Helix, P, Shape
    from machinome.node import MolejoNode
    from machinome.motion.ports import TranslationalPort

    class ValveSpring(MolejoNode):

        height = TranslationalPort(unit='mm')

        def render(self):
            return Shape(
                profile=Circle(radius=2.0),
                path=[Helix(radius=14.0, turns=6.5, height=P.height)],
                path_samples=240,
                profile_samples=16,
            )

``P.height`` is molejo's way of saying "this dimension is a parameter
named ``height``". The wire radius, coil radius and turn count are
numbers, because they describe the spring you would buy; the free height
is left open, because that is the thing the machine moves.

Mind where the shape sits: molejo paths start at the node's origin, so a
helix winds about an axis offset by its coil radius. Place the node, or
author the path, with that in mind.

Feed the parameters through ports
---------------------------------

A flexible part never receives its moving values through its
constructor. It declares one port per shape parameter, under the same
name, and the owning assembly binds them in ``simulate()``:

.. code-block:: python

    from machinome.node import AssemblyNode
    from machinome.simulation import Driver

    FREE_HEIGHT = 46.8

    class Valvetrain(AssemblyNode):

        lift = Driver(default=0.0, range=(0.0, 12.0), unit='mm')

        retainer = Retainer()
        spring = ValveSpring()

        def simulate(self):
            self.spring.height = FREE_HEIGHT - self.lift
            self.retainer.translate([0, 0, FREE_HEIGHT - self.lift])

The port's attribute name is the parameter's name, and the two sets must
match exactly: a parameter with no port, or a port no parameter reads,
fails naming the node and both sets before any geometry is produced. A
port nobody connected fails too; it is never quietly defaulted.

Values through the constructor are the one thing that would not work.
Constructor arguments key a node's build artifacts, so a value that
changes every frame would create a new part every frame. Ports keep the
identity structural: two ``ValveSpring()`` instances are one part,
whatever each is doing. Dimensions that describe a *different* spring, a
thicker wire, another coil count, do belong in the constructor.

Under a running root, bound the mechanical joint that compresses the
spring rather than the spring's height port: a port has no stop of its
own, and the height then follows the joint by a relation
(:doc:`/concepts/running`).

In the viewer and in tests
--------------------------

A flexible part travels into the viewer as its shape specification, not
as a mesh, and the browser evaluates it on the frames the value changed.
A document holding one declares version 3 or above. OpenSCAD has no live
evaluator, so the SCAD output and the OpenSCAD snapshot get a still: the
part evaluated at the bound state.

A flexible part is exact: ``shape()`` gives the OCCT solid for the state
currently bound, so a spring at a given lift answers interference and fit
questions on real boundary geometry. Where the sweep has no closed form,
a helix, a spline, the solid is approximated and ``shape_tolerance``
reports the approximation (``0.0`` when every surface is analytic). On
the exact kernel a flexible comparison costs about thirty times a mesh
comparison; :doc:`fast-tests` is the answer for the development loop.

What a flexible part is not
---------------------------

It cannot be fused: a fusion makes one printed solid of its children,
and a part that deforms is not part of one, so the fusion refuses it
naming both nodes. It is not a printed piece and never appears in the
pieces inventory. And it has no ``time`` of its own: its shape follows
the values its parent binds, and nothing else.

molejo is an ordinary dependency of Machinome, installed with it and
pinned by minor version, because a molejo minor carries the shape
specification version the documents name. A RepRap printer on
machinome.org's Foundry (see :doc:`/examples`) has belts, springs and a
filament path modelled this way.
