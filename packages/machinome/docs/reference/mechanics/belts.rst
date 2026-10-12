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

   GT2 pulleys use 2 mm pitch; AT3 pulleys use 3 mm pitch. A printer model
   that fits a loop's pitch can pass that fitted value. Tooth-tip and flank
   offsets remain outside this helper.

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

   A project that records a belt-back or counterclockwise marker maps it to
   -1 before calling. Loop topology, wrap measurement, pitch-line offsets and
   diagnostic wrappers remain project responsibilities.

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

.. py:function:: belt_path_metrics(centres, radii, senses=None)

   Measure a closed pitch path through ordered circles in the caller's XY
   plane. Pass parallel sequences of centers, nonnegative radii and literal
   senses (+1 clockwise, -1 counterclockwise); omitted senses are all +1.
   Centers and radii use one length unit. There must be at least two circles
   and all sequence lengths must match, otherwise ``ValueError`` is raised.
   Consecutive circles, including last to first, use the same tangent branch
   and geometric domain as :py:func:`belt_tangent_points`.

   The result is an ordinary dictionary. All sequence fields are tuples:

   * ``spans[i]`` is ``(start_xy, unit_direction_xy, length)`` leaving circle i.
   * ``wrap_angles[i]`` is the arrival-to-departure wrap about circle i in
     degrees, following its chosen sense, reduced to [0,360).
   * ``arc_lengths[i]`` is ``radii[i] * wrap_angles[i] * pi/180``.
   * ``stations`` gives the starts of the 2N traversal elements, ordered
     span 0, arc about circle 1, span 1, ..., arc about circle 0.
   * ``length`` is the total of all straight spans and circular arcs.

   Distance zero is departure from circle 0, not its arrival. In particular,
   the first arc in traversal is ``arc_lengths[1]``. A project that lists
   arcs after spans rotates the circle-indexed arc tuple when adapting it.

   Coincident tangent directions give zero wrap, not a full turn. A zero
   radius gives zero arc length; zero-radius circles and limiting zero-length
   spans still have defined directions. Invalid geometry propagates its
   square-root or division error. Supported raw deferred coordinates/radii
   retain the same formula; topology and senses are static. No declared
   dimension-token or arbitrary symbolic-engine contract is added.

   This measures the route supplied; it does not choose routing, check
   self-intersections, generate a mesh, fit tooth count or add mounting phase.
   Project turn markers and any full-turn-at-zero policy remain the
   project's responsibilities.

.. doctest::

   >>> from machinome_mechanics import belt_path_metrics
   >>> path = belt_path_metrics(((0, 0), (10, 0)), (2, 2))
   >>> path['wrap_angles']
   (180.0, 180.0)
   >>> tuple(round(s, 6) for s in path['stations'])
   (0, 10.0, 16.283185, 26.283185)
   >>> round(path['length'], 6)
   32.566371
   >>> straight_idler = belt_path_metrics(((0, 0), (10, 0), (20, 0)), (2, 2, 2))
   >>> straight_idler['wrap_angles']
   (180.0, 0.0, 180.0)

.. py:function:: belt_pulley_angle(belt_position, pitch_radius, contact_angle, contact_station=0.0, sense=1)

   Return ``contact_angle - sense * rolling_angle(belt_position -
   contact_station, pitch_radius)``: a pulley angle referenced to a belt
   contact, not just rotation from an arbitrary zero.

   ``belt_position`` and ``contact_station`` are lengths measured from the
   same origin along the oriented belt path. ``pitch_radius`` uses the same
   length unit. ``contact_angle`` and the result are degrees from +X,
   counterclockwise about +Z in the caller's belt plane. When position equals
   station, the pulley's reference tooth points at ``contact_angle``.

   ``sense`` has the same meaning as in :py:func:`belt_path_metrics`: +1 for
   clockwise traversal, -1 counterclockwise. Advancing clockwise belt material
   decreases the returned angle; the reverse bend increases it. This is not
   the handedness of the machine's mounting axis. The caller applies any tooth
   reference and mounting offset after choosing a consistent contact reference.

   A pulley measured mid-route supplies its tangent phase and station; a
   first-circle contact has station zero. A pulley the belt wraps backwards
   uses -1, with its clamp and pulley stations expressed in the same path
   coordinate. Clamp-axis projections, fitted radii, phase normalization and
   tooth profiles stay in the project.

   The result is signed and unwrapped, including multiple revolutions.
   Physical pitch radius is positive. Negative radii preserve arithmetic;
   zero numeric radius raises ``ZeroDivisionError``. No domain clamp, tooth
   fit, slip or route inference is performed. Supported deferred operands use
   the same arithmetic; there is no new dimensional declaration-token face.

.. doctest::

   >>> from math import pi
   >>> from machinome_mechanics import belt_pulley_angle
   >>> belt_pulley_angle(10, 2, 90, contact_station=10)
   90.0
   >>> round(belt_pulley_angle(10 + pi, 2, 90, 10), 6)
   0.0
   >>> round(belt_pulley_angle(10 + pi, 2, 90, 10, sense=-1), 6)
   180.0
   >>> round(belt_pulley_angle(10 + 4*pi, 2, 90, 10), 6)
   -270.0
   >>> round(belt_pulley_angle(10 + 4*pi, 2, 90, 10, sense=-1), 6)
   450.0
