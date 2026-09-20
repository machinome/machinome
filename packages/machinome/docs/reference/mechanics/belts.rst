Belt geometry
=============

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

.. py:function:: belt_tangent_points(centre_a, radius_a, centre_b, radius_b, sense_a=1, sense_b=1)

   Return ``(point_a, point_b)``, the two tangent contacts in traversal
   order from circle A to circle B. Each center and point is an ``(x, y)``
   pair in the caller's right-handed XY plane. Nonnegative physical radii and
   coordinates use one length unit; there is no angular phase or zero.

   ``sense_a`` and ``sense_b`` are caller-chosen literal signs: +1 for
   clockwise belt traversal around that circle, -1 for counterclockwise.
   Equal senses select an external tangent; different senses select an
   internal tangent, as for a belt running backwards around an idler.
   With equal radii and B to the right of A, default senses choose the upper
   tangent, traveled to the right. Reverse the route by swapping the circles
   and negating both senses. Do not pass project-specific turn strings here.

   The normal satisfies two constraints: its length is one and its dot
   product with B-A is ``sense_a*radius_a - sense_b*radius_b``. The helper
   chooses the branch obtained by adding the counterclockwise perpendicular
   component to that projection. Each point is its center plus the signed
   radius times that normal.

   Centers must differ. The center separation must be at least the absolute
   signed-radius difference; at equality the contacts coincide, which is a
   zero-length limiting span. Zero radius reduces that contact to its center.
   Impossible numeric configurations propagate square-root domain or division
   errors. No tolerance clamp, radius/sense validator or invented pose is added.
   Symbolic coordinates and radii retain the same formula and runtime domain
   behavior; this is not a dimensional declaration-token contract.

   Thor maps its truthy belt-back marker to -1; printer timing modules map
   their counterclockwise marker to -1. Loop topology, wrap measurement,
   pitch-line offsets and diagnostic wrappers remain project responsibilities.

.. doctest::

   >>> from machinome_mechanics import belt_tangent_points
   >>> belt_tangent_points((0, 0), 2, (10, 0), 2)
   ((0.0, 2.0), (10.0, 2.0))
   >>> a, b = belt_tangent_points((0, 0), 2, (10, 0), 3, 1, -1)
   >>> tuple(round(x, 6) for x in a)
   (1.0, 1.732051)
   >>> tuple(round(x, 6) for x in b)
   (8.5, -2.598076)
   >>> belt_tangent_points((10, 0), 2, (0, 0), 2, -1, -1)
   ((10.0, 2.0), (0.0, 2.0))
