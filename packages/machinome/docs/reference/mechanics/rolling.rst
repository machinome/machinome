Rolling motion
==============

Convert a wheel's rotation to tangent travel for a rack, belt, roller or
constant-radius drum, or recover rotation from that travel. Import from ``machinome_mechanics`` or
``machinome_mechanics.rolling``.

.. py:currentmodule:: machinome_mechanics

.. py:function:: rolling_travel(angle, radius)

   Return signed tangent travel from the zero-angle position.

   :param angle: Unwrapped rotation in degrees, positive by the right-hand rule
                 about the wheel axis; numeric or symbolic.
   :param radius: Pitch/contact radius in any consistent length unit.
   :returns: ``angle * radius * pi / 180`` in the radius's length unit.

Positive travel follows the rotating surface's positive tangent. Apply your
machine's mounting sign and reference offset afterwards: a rack-and-pinion
steering model negates the result for rack displacement, and a belt drive
uses the pulley pitch circle to move its belt. A tooth-tip radius is not a
pitch radius.

.. doctest::

   >>> from math import pi
   >>> from machinome_mechanics import rolling_travel
   >>> round(rolling_travel(360, 9), 6)
   56.548668
   >>> rolling_travel(90, 20 / pi)
   10.0
   >>> rolling_travel(-720, 0)
   0.0

A physical radius is positive. Zero and negative radii retain arithmetic
behavior. There is no angle wrapping, slip, backlash, drum layering or physical
domain clamping. Resolved numeric parameters and symbolic driver expressions
are supported; dimensioned class-body declarations have the same limitation
as the other helpers.

.. py:function:: rolling_angle(travel, radius)

   Return the inverse conversion: signed, unwrapped rotation in degrees.

   :param travel: Tangent travel from the zero-angle position; numeric or symbolic.
   :param radius: Nonzero pitch/contact radius in the same length unit as travel.
   :returns: ``travel / radius * 180 / pi`` degrees.

Use the same tangent sign as :py:func:`rolling_travel`. Cartesian and delta
printers use this conversion for belt-driven pulleys and plain idlers, with
their own mounting signs and pulley reference phases applied separately. A plain
idler's contact radius need not be a toothed pulley's pitch radius.

.. doctest::

   >>> from machinome_mechanics import rolling_angle
   >>> round(rolling_angle(18 * pi, 9), 6)
   360.0
   >>> round(rolling_angle(-36 * pi, 9), 6)
   -720.0
   >>> round(rolling_angle(rolling_travel(765, 3), 3), 6)
   765.0
   >>> rolling_angle(1, 0)
   Traceback (most recent call last):
       ...
   ZeroDivisionError: division by zero

A zero radius has no inverse: ordinary Python numeric division raises and
symbolic division keeps the expression runtime's own singular behavior. The
helper adds no guard or clamp. Negative radii retain arithmetic sign, although
a physical radius is positive. Phase angles already in radians require only a
degree conversion, not this helper.
