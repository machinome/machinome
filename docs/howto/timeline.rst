Animate on a timeline
=====================

A driver is the input a person moves. Some machines also have a motion
that is simply *a function of time*: a clock's hands, an engine on a
stand turning at a steady speed, a demonstration that plays by itself.
That is the animation timeline, and ``self.time`` is its driver.

``self.time``
-------------

On an assembly, ``simulate()`` may read ``self.time``. With no time base
declared it is a number between 0 and 1 that loops in the viewer, and
symbolic in the build, so the expression travels to the browser
unevaluated:

.. code-block:: python

    class SimpleClock(AssemblyNode):

        base = ClockBase()
        pointer = Pointer()

        def simulate(self):
            self.pointer.rotate(-360 * self.time, [0, 0, 1])

The angle is negative because a positive rotation about Z is
counter-clockwise, and clocks run clockwise. Scrub the viewer to 0.25 and
the pointer has turned a quarter turn.

``time`` is one driver among the others, and one expression may mix it
with a declared driver. Under a stepped simulation the same
``self.time`` reads the simulation clock in seconds
(:doc:`/concepts/execution-models`).

Give the loop a duration
------------------------

The timeline says nothing about how long one turn of it is. A machine
modelled in real time declares that on its root:

.. code-block:: python

    from machinome.motion.ports import Time

    class WallClock(AssemblyNode):

        time = Time(loop=12 * 3600)

        def simulate(self):
            self.movement.seconds = self.time

``loop`` is the span of machine time, in seconds, that one turn of the
timeline covers. From then on ``self.time`` reads seconds everywhere: in
``simulate()``, in every assembly below the root, in tests and in
snapshots. The published document carries the loop, and the viewer plays
it at real time with a speed control; a twelve-hour clock at ×720 turns
its hour hand once a minute.

Declare ``Time`` only as ``time``, only on the root: descendants read the
root's base, and a declaration on a linked descendant is refused. The
other two spellings, ``Time.running()`` and ``Time.elapsed()``, select
the other execution models and are not timelines; under
``Time.running()`` the clock may drive a relation directly,
``time.drives(shaft.turn, ratio=6)``, which is retained motion rather than
a pose over a timeline (:doc:`/concepts/running`).

Motion without a branch
-----------------------

In the viewer there is no value to branch on, so a law over time is
arithmetic, and ``machinome.math`` carries the arithmetic that expresses
a mechanism without an ``if``. Every function there has three faces: it
computes on plain numbers, defers as an expression when a value is
symbolic, and checks dimensions when a value is a declared parameter.
Python's ``math`` would fail on the symbolic face and works in radians;
all angles in Machinome are degrees.

* ``sin``, ``cos``, ``tan``, ``asin``, ``acos``, ``atan``, ``atan2``,
  ``sqrt``: OpenSCAD's degree-based trigonometry.
* ``abs``, ``floor``, ``ceil``, ``sign``, ``min``, ``max``: the builtins
  OpenSCAD and JavaScript agree on.
* ``clamp(x, low, high)`` and ``clamp01(x)``: a value held within bounds,
  which is how a part stops at a stop.
* ``ramp(x, start, end)``: 0 before ``start``, 1 after ``end``, straight
  between, so a stage of a timeline is one term.
* ``lerp(a, b, u)``: ``a`` at 0, ``b`` at 1, unclamped.
* ``wrap(angle)``: an angle folded into (-180, 180]; ``wrap(value,
  period)`` for anything else that repeats.
* ``piecewise(x, points)``: linear interpolation through measured
  waypoints, held flat past each end.
* ``bump(u)``: a smooth 0-1-0 pulse over ``u`` in [0, 1].

A cam that dwells and then lifts, over a measured profile:

.. code-block:: python

    from machinome.math import piecewise

    PROFILE = [(0.0, 0.0), (90.0, 0.0), (150.0, 12.0), (210.0, 0.0)]

    class Valve(AssemblyNode):

        def simulate(self):
            angle = 360 * self.time
            self.stem.translate([0, 0, piecewise(angle, PROFILE)])

There is deliberately no ``round`` and no ``mod``: OpenSCAD, JavaScript
and Python round halves three different ways, and OpenSCAD spells modulo
as an operator with a different sign rule. ``floor(x + 0.5)`` is the
half-up every runtime agrees on, and ``wrap`` is built on ``ceil``.

Points, not just numbers: ``polar(radius, angle)``, ``turn(point, angle,
about=...)`` and ``rotate_x``, ``rotate_y``, ``rotate_z`` turn points with
the same three faces, so a point turned by a driver-derived angle
survives the viewer. A rotation's *axis* is a constant and cannot carry a
symbol; a rod leaning about a direction the effector's position decides
is two rotations about constant axes, which is what the delta helper in
`Machinome Mechanics <https://machinome-mechanics.readthedocs.io/en/latest/>`_
returns.

Freezing an instant
-------------------

``set_keyframe(t)`` pins an assembly and everything below it to one
instant: ``self.time`` becomes the number ``t`` and meshes resolve
numerically. That is what tests and single-instant renders do.
``clear_keyframe()`` releases it back to symbolic time. Nothing
accumulates however often you freeze and release, and rest placement is
untouched.

.. code-block:: python

    clock.set_keyframe(0.25)
    pose = clock.pointer.mesh
    clock.clear_keyframe()

``machinome export`` never freezes, so an export always carries the
animation. To show one instant of an exported model, use the page's
``?t=`` and ``?autoplay=0`` options rather than publishing a frozen
document.

Testing along the timeline
--------------------------

``@testing_steps(n)`` runs a test at ``n`` instants of the timeline and
``@testing_instant(t)`` at one, so a clearance that must hold through a
turn is one decorated assertion:

.. code-block:: python

    from machinome.test import TestCase, testing_steps

    class SimpleClockTest(TestCase):

        @testing_steps(16)
        def test_pin_runs_free_in_pointer(self):
            self.assertNotIntersecting(self.node.pointer, self.node.pin)

Under a declared loop the decorators take seconds; their defaults do not
follow the declaration, so a sweep over a declared root states the span
it covers. A machine driven by inputs rather than by time is swept with a
scenario instead (:doc:`/tutorial/07-scenario`).
