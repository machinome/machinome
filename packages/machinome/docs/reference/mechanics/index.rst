Helper reference
================

Every helper is exported from ``machinome_mechanics``. You can also import
it from the family module listed on its page. All angles are degrees;
lengths use one consistent unit per calculation. See :doc:`../conventions`
for numeric, symbolic and invalid-input behaviour.

.. py:module:: machinome_mechanics
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

.. toctree::
   :maxdepth: 1

   gears
   screws
   cranks
   cams
   indexing
   deltas
   linkages
   rolling
   belts
