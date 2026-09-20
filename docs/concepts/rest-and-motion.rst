Rest and motion
===============

An assembly has two lifecycle methods, and the split between them is
what the framework knows about your machine.

``render()`` builds the machine **at rest**. It declares presence with
``omit()`` and places every part that does not move: a bearing cap on
its saddle, a clamp on its rail, a motor bolted to a frame. It reads no
driver, no ``self.time`` and no port, and the framework runs it **once
per instance**. The children it returns and the operations it applies
are the instance's, kept for good. A declarative node's ``render()`` may
return nothing (the children are the declared ones, in declaration
order, minus any it omitted), or return a list and the framework builds
exactly that list. A pure grouping node needs no ``render()`` at all.

``simulate()`` **moves** it. The framework runs it after ``render()`` on
every instant, under symbolic ``$t`` in the build and the viewer, under
plain numbers in tests, snapshots and a stepped simulation, and it is the
one place drivers, time and ports are read and bound. Every operation it
applies is motion: stated absolutely for its instant, dropped before the
next run, and composed **inside** the part's rest placement.

.. code-block:: python

    class Block(AssemblyNode):

        clearance = Length(0.3, min=0)

        frame = BlockFrame(clearance=clearance)
        caps = MainBearingCap(clearance=clearance).repeat(5)
        crank = Crankshaft()

        angle = Driver(default=0.0, range=(0.0, 720.0), unit='deg')

        def render(self):
            for cap, x in zip(self.caps, BEARING_CENTERS):
                cap.translate([x, 0, 0])
            self.crank.translate([0, 0, CRANK_HEIGHT])

        def simulate(self):
            self.crank.rotate(self.angle, [1, 0, 0])

The crank turns about its own axis at rest height: the rotation from
``simulate()`` is applied first, then the translation from ``render()``
carries it to its seat. A part that does not move needs no
``simulate()``. ``super().simulate()`` chains as ``super().render()``
does.

Operations
----------

``rotate(angle, axis)`` and ``translate([x, y, z])`` append an operation
to the node, return the node, and chain. A node's own operations apply
before its ancestors'. In ``render()`` they are rest placement and
persist; in ``simulate()`` they are motion, swept before the assembly
simulates again, so you always compute motion from the current inputs
alone with no accumulated state to undo. Two different assemblies may
drive one node (a wheel spun by its axle and steered by the steering
assembly) without disturbing each other's operations.

Do not confuse the node method ``translate([x, y, z])`` with a modelling
library's own ``translate`` used inside a leaf's ``render()``: the
primitive shapes the part, the node method positions it in an assembly.

How motion composes
-------------------

On one node, innermost first:

1. the joints the class declares, in declaration order, the first
   declared closest to the body;
2. every ``rotate()`` and ``translate()`` the ``simulate()`` applied, in
   call order;
3. the rest placement ``render()`` applied.

:doc:`joints` states the joint rules; the point here is that a joint's
line is the body's own and a hand-written motion composes outside the
whole joint block.

Ports and relations in the phase
--------------------------------

Ports are bound in ``simulate()`` too, by ``self.connect(source, sink)``
or by assignment (``unit.crank = self.crank + phase``), because a binding
made in ``render()`` would be made once and never follow the drivers. The
framework runs a parent's ``simulate()`` before it descends into the
children, so a child reads in its own ``simulate()`` what its parent
bound. Relations written in the class body are solved at the end of the
assembly's simulate phase, after the author's ``simulate()`` has bound
whatever it binds (:doc:`relations`).

A coordinate is cleared with the motion it caused: at the start of an
assembly's phase, before its own ``simulate()`` runs, every coordinate
that assembly bound during its previous phase is dropped, the author's
own bindings included. A rest-default guard, ``if self.turn.value is
None: self.turn = 0``, therefore finds the coordinate unbound on every
run and rebinds and re-places the body every time. A binding made
outside any phase, in ``__init__`` or a test, is never recorded and
never cleared.

The legacy form
---------------

The rule is enforced by what a method reads, not by its name. A
``render()`` that reads a driver, ``self.time`` or a port keeps working
as it did before the split: it re-runs on every instant and its
operations are swept, and the build prints once per class:

.. code-block:: text

    FutureWarning: SimpleClock.render() read time 'time'. Reading
    drivers, time or ports in render(), or binding a port there, is
    deprecated: render() builds the machine at rest and the framework
    runs it once per instance. Move the read or binding and the
    operations it feeds into simulate(), which runs on every instant.
    Until then SimpleClock re-renders per binding as before.

The class it names is migrated by moving the read and the operations it
feeds:

.. code-block:: python

    class SimpleClock(AssemblyNode):      # before

        def render(self):
            self.pointer.rotate(-360 * self.time, [0, 0, 1])
            return [self.base, self.pointer]

    class SimpleClock(AssemblyNode):      # after

        def render(self):
            return [self.base, self.pointer]

        def simulate(self):
            self.pointer.rotate(-360 * self.time, [0, 0, 1])

The decision is made on the first run of an instance's ``render()``, so a
``render()`` that reads a driver only under some condition is judged by
what that first run did. Placement applied in ``__init__`` still works
and composes after the motion; it is no longer recommended, and
``render()`` is where a rest placement reads best.

Freezing an instant
-------------------

``set_state(**values)`` binds named driver values for one instant and
propagates them down the tree; entries merge into the current snapshot.
``set_keyframe(t)`` is ``set_state`` with the single global entry
``time``, and ``clear_keyframe()`` releases the tree back to symbolic
expressions. A dotted id is passed as a mapping,
``set_state(**{'x_axis.position': 40.0})``, and reaches only that
subtree; a bare name propagates flat and is exactly right while only one
driver in the tree bears it, and fails naming both the moment two do. A
name no declaration backs is rejected listing what is declared. Under a
running root a bound name may also be a joint coordinate's qualified id,
which is the run's own binding path.
