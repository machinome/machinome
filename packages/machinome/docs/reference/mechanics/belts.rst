Belt pitch geometry
===================

Import from ``machinome_mechanics`` or ``machinome_mechanics.belts``.
Pitch geometry describes the belt's pitch line, not the tooth tips or the
surface of a plain idler. Use one length unit consistently.

.. py:currentmodule:: machinome_mechanics

.. py:function:: pulley_pitch_radius(teeth, pitch)

   Return ``teeth * pitch / (2*pi)``: the radius whose circumference holds
   ``teeth`` linear tooth pitches. ``teeth`` is the tooth count;
   ``pitch`` is the distance along the pitch line between successive teeth.
   The returned radius uses the unit of ``pitch``.

   This scalar length is independent of a mounting frame; no angle zero,
   rotational sign or branch choice applies. Physical inputs are a positive
   integral count and positive pitch. The function does not validate or round
   them: zero, negative and fractional values retain ordinary arithmetic.
   Supported raw symbolic count or pitch expressions use the same formula.
   No dimensional declaration-token contract is added.

   Thor's GT2 pulleys use 2 mm pitch; Open Robot Actuator's AT3 pulleys use
   3 mm pitch. Printer models that fit a loop's pitch can pass that fitted
   value. Their tooth-tip/flank offsets remain outside this helper.

.. doctest::

   >>> from math import isclose, tau
   >>> from machinome_mechanics import pulley_pitch_radius, rolling_travel
   >>> radius = pulley_pitch_radius(117, 2)
   >>> isclose(tau * radius, 234)
   True
   >>> isclose(rolling_travel(360 / 117, radius), 2)
   True
   >>> round(pulley_pitch_radius(10, 3), 6)
   4.774648
   >>> round(pulley_pitch_radius(20, 2) - 0.254, 6)
   6.112198
