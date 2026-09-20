Gears
=====

Calculate the angular registration of an **external spur-gear pair**.
The driven gear counter-rotates at the tooth-count ratio, with its teeth
registered to the driver's gaps. A separate cycloidal helper gives the
signed disk/output ratio for a fixed ring. These functions describe existing
gear geometry; they do not generate profiles or choose a centre distance.

Import from ``machinome_mechanics`` or ``machinome_mechanics.gears``.

.. py:currentmodule:: machinome_mechanics

Frame and tooth registration
----------------------------

Measure both gear rotations in the same frame about the same positive
axis. In an XY gear train that is +Z, counter-clockwise seen from above.
``line_of_centres`` is the angle from the driver's centre toward the
driven's centre, measured in that frame.

Two local references describe how your CAD library authored the gears:

* ``driver_gap`` is the direction of one gap's centre in the driver at
  zero rotation.
* ``driven_tooth`` is the direction of one tooth tip in the driven gear
  at zero rotation.

At the reference pose, the driver's gap points along the line of centres
and the driven's tooth points back into it. Getting the reference wrong
by half a tooth puts teeth against teeth, even when the speed ratio is
correct. The defaults ``0.0`` assume you authored those references at zero.

meshed_angle
------------

.. py:function:: meshed_angle(driver_angle, driver_teeth, driven_teeth, line_of_centres=0.0, driver_gap=0.0, driven_tooth=0.0)

   Return the driven gear's angle in the common frame.

   :param driver_angle: Driver rotation in degrees.
   :param driver_teeth: Positive tooth count of the driver.
   :param driven_teeth: Positive tooth count of the driven gear.
   :param line_of_centres: Direction from driver to driven, in degrees.
   :param driver_gap: Driver-local gap-centre direction at zero, in degrees.
   :param driven_tooth: Driven-local tooth-tip direction at zero, in degrees.
   :returns: Driven angle in degrees, as a number or symbolic expression.

The formula is::

   line + 180 - driven_tooth
       - (driver_teeth / driven_teeth) * (driver_gap + driver_angle - line)

Here ``line`` means ``line_of_centres``. With the driver standing at
``line - driver_gap``, the driven angle is ``line + 180 - driven_tooth``.
An extra degree on the driver subtracts ``driver_teeth / driven_teeth``
degrees from the driven angle. Angles are not wrapped, so multi-turn
motion stays continuous.

For a 12-tooth driver and a 24-tooth wheel whose profiles both have a
tooth at local +X at zero, the driver's gap lies half a tooth pitch away:

.. doctest::

   >>> from machinome_mechanics import meshed_angle
   >>> meshed_angle(0, 12, 24, driver_gap=180 / 12)
   172.5
   >>> meshed_angle(30, 12, 24, driver_gap=15)
   157.5
   >>> meshed_angle(30, 12, 24, line_of_centres=45, driver_gap=15)
   225.0

driving_angle
-------------

.. py:function:: driving_angle(driven_angle, driver_teeth, driven_teeth, line_of_centres=0.0, driver_gap=0.0, driven_tooth=0.0)

   Return the driver angle that produces a specified driven angle.

   :param driven_angle: Target driven rotation in degrees.
   :param driver_teeth: Positive tooth count of the driver.
   :param driven_teeth: Positive tooth count of the driven gear.
   :param line_of_centres: Direction from driver to driven, in degrees.
   :param driver_gap: Driver-local gap-centre direction at zero, in degrees.
   :param driven_tooth: Driven-local tooth-tip direction at zero, in degrees.
   :returns: Driver angle in degrees, as a number or symbolic expression.

This is the exact algebraic inverse of :py:func:`meshed_angle`. Keep the
same driver/driven roles and references when using it; do not swap the
tooth counts. It is useful when placing a clock train backwards from an
escape wheel whose orientation is fixed by the escapement.

.. doctest::

   >>> from machinome_mechanics import driving_angle
   >>> driven = meshed_angle(10, 60, 8, 30, 3, 22.5)
   >>> driven
   315.0
   >>> driving_angle(driven, 60, 8, 30, 3, 22.5)
   10.0

Adapting a gear library
-----------------------

The ``cq_gears`` profiles used by the gearbox project centre a tooth on
+X at zero: use ``driver_gap=180 / driver_teeth`` and ``driven_tooth=0``.

The ``Gear`` profiles used by 3DPrintedClocks begin with a gap: use
``driver_gap=gap_angle / 2`` and
``driven_tooth=gap_angle + tooth_angle / 2``, in degrees. Mirroring a
profile negates its reference angles. A lantern pinion whose first
trundle is on +X has ``driven_tooth=0``. Read these values from the actual
profile convention used by your project and verify the assembled mesh.

Use positive nonzero tooth counts. Neither function validates counts;
a zero denominator raises numerically. These formulas describe external
meshing only, with no backlash, slip or tooth deformation model.

cycloidal_ratio
---------------

.. py:function:: cycloidal_ratio(lobes, pins)

   Return the signed disk/output angle increment per eccentric-input increment
   for a cycloidal reducer with its ring held stationary.

   :param lobes: Number of lobes on the cycloidal disk.
   :param pins: Number of fixed ring pins, not the pins transferring motion
                from the disk to the output.
   :returns: Dimensionless ``-(pins-lobes)/lobes``, numeric or deferred.

Measure both input and output increments about the same positive axis, using
the same angular unit. Multiplying an input in degrees gives output degrees.
With a fixed ring, the relative mesh identity is
``lobes * (output-input) = pins * (0-input)``. The ratio is negative for the
physical domain ``pins > lobes > 0``: output counter-rotates. It is **not**
the positive reduction magnitude often written as "20:1". The negative sign
alone does not promise an output speed smaller than the input speed.

.. doctest::

   >>> from machinome_mechanics import cycloidal_ratio
   >>> ratio = cycloidal_ratio(20, 21)
   >>> ratio
   -0.05
   >>> 360 * ratio  # One input turn gives a reverse 18-degree increment
   -18.0
   >>> 7200 * ratio  # Multi-turn input is not wrapped
   -360.0
   >>> -7200 * ratio
   360.0

The zero input increment gives zero output increment; any reference pose is
added by the project. CycloidalDrive and OpenCycloid use 20 disk lobes and
21 fixed ring pins, keeping their eccentric-center orbit at input speed and
applying this coefficient only to disk attitude and output spin. Output
transfer pins, source mounting phases and positive instruction ranges remain
project data.

Physical counts are positive integers, but the helper does not coerce or
validate them. Fractional, negative and equal counts retain ordinary
arithmetic; equal nonzero counts return zero without certifying a realizable
reducer. Zero numeric lobes raise ``ZeroDivisionError``. Supported deferred
counts use the same subtraction/division. No moving-ring train, profile
compatibility, backlash, tooth contact or torque model is supplied.
