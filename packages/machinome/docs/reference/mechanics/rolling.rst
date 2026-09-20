Rolling travel
==============

Convert a wheel's rotation to tangent travel for a rack, belt, roller or
constant-radius drum. Import from ``machinome_mechanics`` or
``machinome_mechanics.rolling``.

.. py:currentmodule:: machinome_mechanics

.. py:function:: rolling_travel(angle, radius)

   Return signed tangent travel from the zero-angle position.

   :param angle: Unwrapped rotation in degrees, positive by the right-hand rule
                 about the wheel axis; numeric or symbolic.
   :param radius: Pitch/contact radius in any consistent length unit.
   :returns: ``angle * radius * pi / 180`` in the radius's length unit.

Positive travel follows the rotating surface's positive tangent. Apply your
machine's mounting sign and reference offset afterwards. Dragon R1 negates
the result for rack displacement; Thor uses the pulley pitch circle to move
its belt. A tooth-tip radius is not a pitch radius.

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
