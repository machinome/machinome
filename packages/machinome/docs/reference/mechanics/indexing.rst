Indexed advance
===============

Import from ``machinome_mechanics`` or ``machinome_mechanics.indexing``.

.. py:currentmodule:: machinome_mechanics

.. py:function:: indexed_advance(angle, increment, stroke, phase_origin=0)

   Accumulate completed turns around a caller-authored within-turn stroke.

   :param angle: Signed, unwrapped input angle in degrees.
   :param increment: Signed output displacement for each completed revolution.
   :param stroke: Pure callable taking one absolute within-turn phase in degrees.
   :param phase_origin: Degree angle at which the turn count changes.
   :returns: Unwrapped displacement, in the shared unit of increment and stroke.

For ``n = floor((angle-phase_origin)/360)``, return
``n*increment + stroke(angle-360*n)``. The stroke is called **exactly once**
at absolute phase in ``[phase_origin, phase_origin+360)``. This is **not**
phase measured from the origin. Negative input uses floor, not truncation
toward zero. The period is fixed at 360 degrees; there is no arbitrary-period
option. The caller supplies the output reference, direction and mounting sign.

.. doctest::

   >>> from machinome_mechanics import indexed_advance
   >>> [indexed_advance(a, 7.5, lambda p: 7.5*p/360) for a in (-90, 0, 180, 810)]
   [-1.875, 0.0, 3.75, 16.875]
   >>> from machinome.math import clamp01
   >>> carry_stroke = lambda p: 36*clamp01((p-325)/34)
   >>> [indexed_advance(a, 36, carry_stroke, 325) for a in (0, 325, 342, 359, 685, 719)]
   [0.0, 0.0, 18.0, 36.0, 36.0, 72.0]

The second example is a mechanical calculator's carry: one 36-degree stroke
from 325 to 359 degrees, followed by a hold. Keeping absolute phase lets the
project retain its segment coordinates. A ratchet-fed sawmill instead
supplies its nonlinear hook-contact stroke with a 7.5-degree tooth increment,
and multiplies the result by its smooth reset **outside** this helper.
Neither contact geometry nor reset policy is inferred.

Continuity is **not guaranteed**. For a continuous seam, the stroke's upper
one-sided limit must equal ``increment + stroke(phase_origin)``. A stroke with
an arbitrary offset retains that offset; zero and negative increments retain
ordinary arithmetic. This deliberately discontinuous example is valid:

.. doctest::

   >>> [indexed_advance(a, 10, lambda p: 0) for a in (359, 360)]
   [0, 10]

Numeric and supported raw deferred operands use the same expression. The
callback must itself be pure and support expression arithmetic for deferred
use: use ``machinome.math`` functions, not numeric-only ``math`` functions or
Python branches on symbolic values. It is called once while constructing the
expression, not re-executed as a Python function at every animation sample.
Exceptions propagate; the helper does not test or repair callbacks. With a
symbolic angle such as ``720 * self.time``, the same call returns a deferred
expression over the stroke's own arithmetic.

The usual :doc:`../conventions` limitation on dimensional class-body values
applies. Very large floating angles retain ordinary phase-reduction precision
limits. This law models displacement, not forces, collision-free engagement,
or a guarantee that a real ratchet advances without slipping.
