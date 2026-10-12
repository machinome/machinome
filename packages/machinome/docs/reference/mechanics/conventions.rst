Units, frames and valid poses
=============================

Each helper is a formula over the arguments you give it. It does not
inspect your parts to discover a tooth's phase, a rod's reference frame,
or which side of a linkage you assembled. Those conventions are part of
using the formula correctly.

Degrees and consistent lengths
------------------------------

All input and output angles are **degrees**, including inverse trigonometry.
Positive rotations use the right-hand rule about the stated axis. For a
rotation about +Z, positive is counter-clockwise when viewed from +Z.

All lengths in one calculation must use the same unit. Millimetres are
common in Machinome projects, but a helper does not convert metres to
millimetres or attach a unit to its result. Tooth counts and gear ratios
are dimensionless. Results are floating-point values or symbolic
expressions; use tolerances when comparing computed geometry.

.. doctest::

   >>> from math import isclose
   >>> from machinome_mechanics import crank_pin
   >>> across, along = crank_pin(90, 15)
   >>> isclose(across, -15) and isclose(along, 0, abs_tol=1e-10)
   True

Choose the frame before calling
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 23 77

   * - Family
     - Reference convention
   * - :doc:`Gears <reference/gears>`
     - Both gear angles and the line of centres use one common frame.
       Gap and tooth references use each gear's local frame at zero.
   * - :doc:`Screws <reference/screws>`
     - Travel is the right-hand screw's advance along its axis relative
       to its nut, measured from zero rotation.
   * - :doc:`Cranks <reference/cranks>`
     - Coordinates are ``(across, along)``. The cylinder is the along
       axis; zero crank angle is top dead centre.
   * - :doc:`Deltas <reference/deltas>`
     - Z is vertical. Tower azimuth is measured from +X about +Z.
       Carriage heights share the effector joint plane's height frame.
   * - :doc:`Linkages <reference/linkages>`
     - Points are ``(x, y)`` in the caller's plane. Intersection side
       is left or right when looking from the first centre to the second.

The functions return positions and angles in these frames. Apply your
machine's offsets and rotations afterwards. A bank angle in an engine,
or a motor that turns a screw the other way, belongs in the project law.

Keep numeric and symbolic calculations together
-----------------------------------------------

The helpers compose arithmetic and ``machinome.math``, so they work on
plain numbers and symbolic drivers. Tuple-valued helpers such as
``crank_pin`` return tuples whose components can each be expressions.
Do not turn symbolic results into ``float`` values or pass them through
Python's numeric-only ``math`` functions inside a motion law. Use
``machinome.math`` for further symbolic calculations.

Dimensional parameter declarations are a separate surface. These
helpers do **not** promise to accept class-body ``Angle`` or ``Length``
tokens as dimension-checked formulas. Degree constants such as ``180``
and ``360`` are ordinary numbers. Use resolved numeric dimensions in a
law factory. For a static class-body calculation, ``.value`` is an
explicit escape hatch; see :ref:`declared-parameters`.

Unreachable and degenerate configurations
-----------------------------------------

The formulas do not clamp inputs or find an alternative pose when the
requested one is impossible. For example, a rod cannot span a horizontal
offset greater than its length:

.. doctest::

   >>> from machinome_mechanics import link_rise
   >>> link_rise(5, 6)
   Traceback (most recent call last):
       ...
   ValueError: math domain error

Out-of-range square roots and inverse trigonometry raise numeric domain
errors. Their deferred expressions evaluate to NaN in OpenSCAD and the
browser viewer. Degenerate divisions, such as a zero screw lead or
coincident circle centres, can raise ``ZeroDivisionError`` numerically.
Each reference page states the meaningful domain of its arguments.

Check your dimensions and travel limits in the project, and leave a
margin around singular poses where floating-point roundoff matters.
These helpers do not prove collision clearance, strength or dynamic
behaviour; use the framework's `test assertions
<https://machinome.readthedocs.io/en/latest/reference/assertions.html>`_
for the assembly properties your project needs.
