Cam follower envelopes
======================

Import from ``machinome_mechanics`` or ``machinome_mechanics.cams``.

.. py:currentmodule:: machinome_mechanics

.. py:function:: harmonic_cam_lift(angle, lift, rise_span=180, return_span=180)

   Return a periodic half-cosine rise and return, followed by a base dwell.

   :param angle: Cam phase in degrees; signed/unwrapped, numeric or symbolic.
   :param lift: Signed **full peak displacement** from the base, not half stroke.
   :param rise_span: Degrees from base to peak, beginning at phase zero.
   :param return_span: Degrees from peak back to base, immediately after rise.
   :returns: Displacement in the same unit as ``lift``.

For ``p = angle - 360*floor(angle/360)``, set
``u = clamp01(p/rise_span)`` and
``v = clamp01((p-rise_span)/return_span)``. The result is
``lift*(cos(180*v)-cos(180*u))/2``, with degree cosine. The remaining part
of the revolution is zero displacement. Negative angles traverse the same
envelope backwards; phase offsets are supplied by subtracting from ``angle``.
The caller chooses the physical axis and mounting sign. Lift can be a length
or a follower rotation; the helper does not infer a mechanism from its units.

.. doctest::

   >>> from machinome_mechanics import harmonic_cam_lift
   >>> [round(harmonic_cam_lift(a, 10), 6) for a in (0, 90, 180, 270, 360)]
   [0.0, 5.0, 10.0, 5.0, 0.0]
   >>> round(harmonic_cam_lift(-90, -10), 6)
   -5.0
   >>> round(harmonic_cam_lift(280, 18, 240, 80), 6)
   9.0
   >>> harmonic_cam_lift(300, 18, 240, 45)
   0.0
   >>> harmonic_cam_lift(90, 10, 0, 180)
   Traceback (most recent call last):
       ...
   ZeroDivisionError: float division by zero

Leonardo's cam hammer uses a 240-degree rise and 80-degree follower return;
its physical cam deliberately returns in 45 degrees to release the follower.
Keep those choices distinct. Deepseek's hydraulic sawmill uses the symmetric
180/180 case with ``lift=2*FEED_THROW``: its named throw is half its full stroke.

Physical spans must be positive and sum to at most 360. The helper does not
validate or repair them: zero numeric spans raise division errors and other
out-of-domain spans retain arithmetic without a physical-envelope guarantee.
The interval clamps implement the rise/return/dwell law, not tolerance repair.
Zero and negative lift retain linear scaling. Supported deferred angle, lift
and span operands use the same expression; class-body declarations retain the
usual :doc:`../conventions` limitation.

This is a displacement law, not a cam profile, dynamic model or certification
that a follower stays in contact. No top dwell, arbitrary period or automatic
phase matching is inferred. Very large floating inputs have ordinary phase
reduction precision limits.
