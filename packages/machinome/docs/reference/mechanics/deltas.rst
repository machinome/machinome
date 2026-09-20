Linear deltas
=============

For a linear delta printer, find each vertical carriage's height and
each rod's orientation from the effector position. Call the helpers
once per tower. Import from ``machinome_mechanics`` or
``machinome_mechanics.deltas``.

.. py:currentmodule:: machinome_mechanics

Frame and effective radius
--------------------------

Z is vertical; the effector moves in XY. ``tower`` is the tower's azimuth
in degrees from +X about +Z. ``plane`` is the height of the effector's
**joint plane**, which may differ from the nozzle-tip height.

``radius`` is the horizontal distance between an effector joint and its
carriage joint **when the effector is centred**. For radially aligned
joints, this is the carriage-joint radius minus the effector-joint
radius. It is not necessarily the radius of the tower structure. This
is the effective ``delta_radius`` convention used by the Kossel project.

For each tower, the helper computes the horizontal vector from carriage
joint to effector joint::

   dx = x - radius * cos(tower)
   dy = y - radius * sin(tower)

All lengths, including XY coordinates and plane height, use the same unit.

delta_carriage
--------------

.. py:function:: delta_carriage(x, y, rod, radius, tower, plane=0.0)

   Return one tower's carriage-joint height.

   :param x: Effector X displacement from its centred position.
   :param y: Effector Y displacement from its centred position.
   :param rod: Rod length between its joints.
   :param radius: Effective horizontal joint separation at the centred pose.
   :param tower: Tower azimuth about +Z, in degrees from +X.
   :param plane: Effector joint-plane Z height, defaulting to zero.
   :returns: ``plane + sqrt(rod**2 - dx**2 - dy**2)``, a number or symbolic
             expression in the supplied length unit and the plane's Z frame.

The positive square root places the carriage above the effector joint
plane. Moving toward a tower reduces the horizontal span, so its
carriage rises. Adding to ``plane`` raises all carriage heights by that
same amount.

.. doctest::

   >>> from machinome_mechanics import delta_carriage
   >>> round(delta_carriage(0, 0, 215, 100, 0), 4)
   190.3287
   >>> round(delta_carriage(10, 0, 215, 100, 0), 4)
   195.2562
   >>> towers = (0, 120, 240)
   >>> [round(delta_carriage(0, 0, 215, 100, a, plane=20), 4) for a in towers]
   [210.3287, 210.3287, 210.3287]

delta_rod
---------

.. py:function:: delta_rod(x, y, rod, radius, tower)

   Return one rod's orientation as ``(tilt, azimuth)``.

   :param x: Effector X displacement from its centred position.
   :param y: Effector Y displacement from its centred position.
   :param rod: Positive rod length between its joints.
   :param radius: Effective horizontal joint separation at the centred pose.
   :param tower: Tower azimuth about +Z, in degrees from +X.
   :returns: ``(asin(sqrt(dx**2 + dy**2) / rod), atan2(dy, dx))`` in
             degrees. Each tuple component may be numeric or symbolic.

``tilt`` measures the rod's lean from vertical. ``azimuth`` points from
the carriage joint toward the effector joint in XY; at a centred pose
it therefore points inward, opposite the tower's outward direction.
``plane`` is unnecessary here because raising the whole joint plane
does not change the rod's lean.

.. doctest::

   >>> from machinome_mechanics import delta_rod
   >>> tuple(round(v, 4) for v in delta_rod(0, 0, 215, 100, 0))
   (27.7177, 180.0)
   >>> tuple(round(v, 4) for v in delta_rod(0, 10, 215, 100, 0))
   (27.868, 174.2894)

Pose the rod with two fixed axes
--------------------------------

For a rod authored along Z, rotate by ``-tilt`` about Y, then by
``azimuth`` about Z, then translate to the chosen joint. When anchoring
at the upper carriage joint, author the rod extending along **-Z**.
When anchoring at the lower effector joint, extend it along **+Z**.

.. code-block:: python

   tilt, azimuth = delta_rod(x, y, rod_length, radius, tower)
   # rod_node has its carriage joint at the origin and extends along -Z.
   rod_node.rotate(-tilt, [0, 1, 0])
   rod_node.rotate(azimuth, [0, 0, 1])
   rod_node.translate(carriage_joint_position)

Use the actual carriage joint's world position for the translation;
``radius`` is the effective separation, not necessarily that joint's
radial coordinate. Two rotations keep the axes constant while their
angles carry driver expressions; a computed symbolic rotation axis is
not supported by the framework.

Valid workspace
---------------

The horizontal span ``sqrt(dx**2 + dy**2)`` must be no larger than the
positive rod length. Equality makes the rod horizontal, a singular
boundary for a working machine. At zero horizontal span the rod is
vertical and its azimuth has no geometric significance. No workspace,
joint-angle, carriage-travel or collision limits are enforced here.
These are inverse kinematics for the stated linear-delta geometry, not
a general solver for arbitrary tower or joint layouts.
