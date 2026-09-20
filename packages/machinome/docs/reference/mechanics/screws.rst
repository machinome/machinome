Lead screws
===========

Convert screw rotation to axial travel, or find the rotation needed for
a desired travel. Import from ``machinome_mechanics`` or
``machinome_mechanics.screws``.

.. py:currentmodule:: machinome_mechanics

Lead and direction
------------------

**Lead is advance per full turn:** pitch multiplied by the number of
thread starts. A four-start screw with 1 mm pitch has a 4 mm lead.
Passing the pitch alone would make its travel four times too small.

For a right-hand thread, positive rotation by the right-hand rule about
the screw's axis advances the screw in the positive axial direction
relative to its nut. Zero rotation gives zero travel. The returned
travel is a displacement, so add your machine's rest offset afterwards.

screw_travel
------------

.. py:function:: screw_travel(angle, lead)

   Return the screw's advance along its axis relative to its nut.

   :param angle: Screw rotation in degrees; may cover multiple turns.
   :param lead: Axial advance per turn, in the desired length unit.
   :returns: ``lead * angle / 360`` in the lead's length unit, as a number
             or symbolic expression.

.. doctest::

   >>> from machinome_mechanics import screw_travel
   >>> screw_travel(360, 2)
   2.0
   >>> screw_travel(90, 4)
   1.0
   >>> screw_travel(-180, 4)
   -2.0

screw_angle
-----------

.. py:function:: screw_angle(travel, lead)

   Return the screw rotation needed for an axial advance.

   :param travel: Desired screw advance relative to its nut, in the same
                  length unit as ``lead``.
   :param lead: Nonzero axial advance per turn.
   :returns: ``360 * travel / lead`` degrees, as a number or symbolic
             expression.

This is the inverse of :py:func:`screw_travel` when the lead is nonzero.
No angle wrapping is applied.

.. doctest::

   >>> from machinome_mechanics import screw_angle
   >>> screw_angle(1, 2)
   180.0
   >>> screw_angle(screw_travel(810, 4), 4)
   810.0

Moving a nut or reversing the thread
------------------------------------

Keep a positive lead for the geometric advance per turn. Negate the
result when modelling a left-hand thread or the nut's motion relative
to an axially fixed screw. Other sign changes, such as a reversing gear
or lever, belong in your project's law too.

.. doctest::

   >>> rest_position = 20
   >>> motor_angle = 90
   >>> nut_position = rest_position - screw_travel(motor_angle, 4)
   >>> nut_position
   19.0

This is the kind of sign choice needed by the InMoov screw jack and
OpenFlexure column. The Snappy Z-axis uses the inverse conversion to
calculate a screw angle from travel.

``screw_travel`` performs arithmetic even for zero or negative leads;
it does not validate that you described a physical thread. A zero lead
is not invertible: ``screw_angle`` divides by it. Neither function
accounts for backlash, thread compliance or end stops.
