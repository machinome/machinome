# Machinome Mechanics - Mechanical formula helpers for Machinome projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""External registration, internal mesh increments and cycloidal ratios.

A pair is meshed when a tooth of the driven gear points into a gap of
the driver along the line joining their centres. Turn the driver away
from that pose by some angle and the driven follows by the same angle
scaled by the tooth ratio, the other way round. That is the whole of the
law, and it is the whole of what depthing a train decides: an arbor's
own rotation is the only freedom each mesh has.

Frame. Both gears' angles and the line of centres are measured in one
common frame, in degrees, positive by the right-hand rule about the axis
both gears turn on (anticlockwise seen from +Z, which is what a node's
``rotate()`` does). ``line_of_centres`` is the direction from the
driver's centre to the driven's.

The seam: where a tooth sits at zero. Every gear library answers that
differently, so the law takes the answer as two plain angles rather than
reading any gear object:

- ``driver_gap`` -- the direction, in the driver's own frame at angle
  zero, of the centre of one of its gaps.
- ``driven_tooth`` -- the direction, in the driven's own frame at angle
  zero, of the tip of one of its teeth.

They are asymmetric on purpose: a tooth of the driven points into a gap
of the driver, so the driver is described by a gap and the driven by a
tooth. Both default to zero, so a caller with no convention states none.

Two recipes, for the two kinds of gear library met so far:

- A library that centres a tooth on local +X at angle zero (``cq_gears``
  does) puts a gap centre half a tooth pitch round:
  ``driver_gap = 180 / driver_teeth`` and ``driven_tooth = 0``.
- A clock-wheel library that starts its profile at a gap, so the first
  gap runs from zero to ``gap_angle``: a gap centre sits at
  ``gap_angle / 2`` and a tooth tip at ``gap_angle + tooth_angle / 2``
  (both in degrees). A part the library turns over -- to print it, or to
  face a pinion the other way -- mirrors every angle in it, so both
  references are negated. A lantern pinion has no cut profile at all:
  its leaves are trundles standing in holes at multiples of the tooth
  pitch beginning at zero, so its ``driven_tooth`` is zero. Those two
  lines in the caller are the whole of that library's convention; the
  law does not fork.

Getting a reference half a tooth wrong is the one error that looks like
nothing: a wheel's teeth are as wide as its gaps, so the leaves land on
the teeth instead of between them and every number still reads plausibly.

The cycloidal ratio is a separate speed law: a fixed ring constrains a
disk carried by an eccentric input. Disk/output and input increments use
the same positive axis; their ratio is negative when fixed pins outnumber
disk lobes. Eccentric orbit and rest phases stay with the caller.
"""


def meshed_angle(driver_angle, driver_teeth, driven_teeth,
                 line_of_centres=0.0, driver_gap=0.0, driven_tooth=0.0):
    """The angle of the driven gear of an external spur pair.

    ``driven = line + 180 - driven_tooth
    - (driver_teeth / driven_teeth) * (driver_gap + driver_angle - line)``

    At the reference pose -- the driver standing so its referenced gap
    centre points along the line of centres, ``driver_angle = line -
    driver_gap`` -- this is ``line + 180 - driven_tooth``: the driven's
    referenced tooth tip pointing back along the line of centres, into
    that gap. Away from it the driven counter-rotates by the tooth
    ratio.

    See the module docstring for the frame and for the two reference
    angles.
    """
    return (line_of_centres + 180 - driven_tooth
            - (driver_teeth / driven_teeth)
            * (driver_gap + driver_angle - line_of_centres))


def driving_angle(driven_angle, driver_teeth, driven_teeth,
                  line_of_centres=0.0, driver_gap=0.0, driven_tooth=0.0):
    """The driver's angle for a driven gear already placed: the exact
    inverse of :func:`meshed_angle` over the same six arguments.

    Wanted walking a clock train backward from the escape wheel, which
    is the end the escapement fixes.
    """
    return (line_of_centres - driver_gap
            + (driven_teeth / driver_teeth)
            * (line_of_centres + 180 - driven_tooth - driven_angle))


def cycloidal_ratio(lobes, pins):
    """Signed disk/output increment per eccentric-input increment.

    The ring is fixed; ``lobes`` counts disk lobes and ``pins`` counts
    fixed ring pins, not output-transfer pins. Both angle increments use
    the same positive axis and unit, so the returned ratio is dimensionless.
    Reference phases and eccentric-center orbit are not part of this law.

    Physical use assumes positive integer lobes and pins > lobes. Counts
    are not rounded or validated; numeric zero lobes divide by zero.
    Numeric and supported deferred operands share the same arithmetic.
    A printed reducer with 20 lobes and 21 pins reduces disk/output spin
    to -1/20 while its eccentric centre still orbits one-to-one.
    """
    return -(pins - lobes) / lobes


def internal_mesh_angle(ring_angle, ring_teeth, pinion_teeth, carrier_angle=0.0):
    """Return the common-frame pinion increment for an internal ring mesh.

    Angles are signed, unwrapped degrees from a caller-registered pose,
    about the same positive axis in a common nonrotating frame. The
    pinion and ring turn in the same sense relative to the carrier.
    Subtract ``carrier_angle`` from the result for child-local spin.
    Tooth phases, source placements and mounting signs remain caller-owned;
    this is not the registration law supplied by ``meshed_angle``.

    Physical tooth counts are positive integers with ring > pinion.
    Arithmetic is neither coerced nor validated; numeric zero pinion teeth
    raise ZeroDivisionError. Numeric and supported deferred values share
    the same formula, with no wrapping or geometry certification.

    A moving 60-tooth ring over fixed-centre 10-tooth pinions keeps its
    mounting signs in the caller. A planetary stage with a fixed 126-tooth
    ring and 54-tooth planets on a moving carrier takes its local planet
    spin as this common-frame increment minus the carrier increment.
    """
    return carrier_angle + (ring_teeth / pinion_teeth) * (ring_angle - carrier_angle)
