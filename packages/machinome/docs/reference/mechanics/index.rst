Mechanics helpers
=================

.. needs:: mechanics

The package provides small Python functions for gears, screws, rolling travel,
slider-cranks, linear deltas and planar linkages. Use them to calculate a
single pose, or put them inside a :doc:`relation law </concepts/relations>` so
the same formula follows a driver through an animation. Numeric and symbolic
inputs share one definition through ``machinome.math``.

Your project supplies dimensions, coordinate frames and assembly geometry.
Machinome supplies the machine model and motion evaluation. The helpers supply
reusable kinematic relationships between them.

The helpers are the package ``machinome-mechanics`` |mechanics_version|,
installed by ``machinome[mechanics]`` and imported from
``machinome.mechanics`` or its family modules; the framework never imports
them. All angles are degrees; lengths use one consistent unit per calculation.
Read :doc:`conventions` before adapting a law to another machine.

.. toctree::
   :maxdepth: 1
   :hidden:

   conventions
   gears
   screws
   cranks
   cams
   indexing
   deltas
   linkages
   rolling
   belts

Find the formula you need
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Mechanism
     - What you can calculate
   * - :doc:`Gears <gears>`
     - External registration, internal mesh increments and cycloidal ratios.
   * - :doc:`Lead screws <screws>`
     - Linear travel from rotation, or the rotation needed for a travel.
   * - :doc:`Slider-cranks <cranks>`
     - Crank-pin position, connecting-rod angle and piston height.
   * - :doc:`Cam followers <cams>`
     - Periodic half-cosine lift, return and base dwell.
   * - :doc:`Indexed advance <indexing>`
     - Signed completed-turn accumulation around a mechanical stroke.
   * - :doc:`Linear deltas <deltas>`
     - Carriage heights and rod orientations for an effector position.
   * - :doc:`Linkages <linkages>`
     - Circle/triangle geometry, link rise, two-link angles and four-bar poses.
   * - :doc:`Rolling motion <rolling>`
     - Rack, belt or drum travel from rotation, and its inverse.
   * - :doc:`Belt geometry <belts>`
     - Pulley pitch radius, tangent contacts, closed path metrics and contact-referenced angle.

Every helper
------------

.. py:module:: machinome.mechanics
   :synopsis: Mechanics helpers for Machinome models.

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Helper
     - Result
   * - :py:func:`meshed_angle`
     - Driven angle for an external spur-gear pair.
   * - :py:func:`driving_angle`
     - Driver angle for the same mesh, solved backwards.
   * - :py:func:`cycloidal_ratio`
     - Signed disk/output increment per eccentric input with a fixed ring.
   * - :py:func:`internal_mesh_angle`
     - Common-frame pinion increment for an internal ring mesh and carrier.
   * - :py:func:`harmonic_cam_lift`
     - Periodic half-cosine rise, return and base dwell from full peak lift.
   * - :py:func:`indexed_advance`
     - Completed-turn increments plus a caller's within-turn stroke.
   * - :py:func:`screw_travel`
     - Axial advance for a screw rotation.
   * - :py:func:`screw_angle`
     - Screw rotation for an axial advance.
   * - :py:func:`crank_pin`
     - Crank pin's ``(across, along)`` position.
   * - :py:func:`crank_rod_angle`
     - Connecting rod's tilt from the cylinder axis.
   * - :py:func:`piston_height`
     - Piston small end's coordinate along the cylinder axis.
   * - :py:func:`delta_carriage`
     - Carriage joint height for one delta tower.
   * - :py:func:`delta_rod`
     - Rod ``(tilt, azimuth)`` for one delta tower.
   * - :py:func:`circle_intersection`
     - A chosen intersection of two circles.
   * - :py:func:`triangle_angle`
     - Triangle angle from three side lengths.
   * - :py:func:`link_rise`
     - Vertical separation from link length and horizontal offset.
   * - :py:func:`two_link_angles`
     - Absolute shoulder and relative elbow for a planar reach.
   * - :py:func:`four_bar_pose`
     - Moving pivots and output bearings for a driven planar four-bar.
   * - :py:func:`rolling_travel`
     - Tangent travel at a constant pitch/contact radius.
   * - :py:func:`rolling_angle`
     - Unwrapped rotation from tangent travel at a constant radius.
   * - :py:func:`pulley_pitch_radius`
     - Pulley pitch radius from tooth count and linear pitch.
   * - :py:func:`belt_tangent_points`
     - Directed contact points for an outer or inner belt tangent.
   * - :py:func:`belt_path_metrics`
     - Closed pitch path spans, wraps, arc lengths and stations.
   * - :py:func:`belt_pulley_angle`
     - Pulley orientation from belt position and a contact reference.
