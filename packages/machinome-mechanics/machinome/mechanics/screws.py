# Machinome Mechanics - Mechanical formula helpers for Machinome projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The lead screw.

One turn of a screw advances it one *lead* along its own axis, and the
law is that proportion and nothing else. What every project got wrong
about it was the sign.

Convention. The screw is a right-hand thread, turned positively by the
right-hand rule about its own axis, and it advances along that axis
relative to its nut by the returned travel. That is the one convention
that follows from the right-hand rule alone, so it is the one the
framework fixes. Everything else -- a left-hand thread, the nut moving
instead of the screw, a lever between the two that inverts, a motor
geared the other way -- is the caller's negation, and it belongs in the
caller where it can be read beside the reason for it. These functions
take no handedness argument.

``lead`` is the axial advance per turn: pitch times starts, never bare
pitch. A four-start 1 mm screw has a lead of 4 mm, and stating it that
way is why a multi-start thread cannot be silently halved.

Three machines that each spell the sign their own way:

- A microscope focus column, where every lever turns a *falling* column
  into positive travel of what the axis moves, so its column travel is
  the negative of this function at the screw's own angle.
- A screw-jack elbow, whose nut winds *down* the screw towards the servo
  as the shaft turns on, so its reach is a rest reach minus this
  function.
- A printer's Z axis commanded in travel, whose screw angle is this
  module's :func:`screw_angle`.
"""


def screw_travel(angle, lead):
    """How far a right-hand screw of ``lead`` per turn advances along
    its own axis, relative to its nut, when turned ``angle`` degrees
    positively about that axis: ``lead * angle / 360``.

    A left-hand thread, or the nut's motion relative to a screw held
    axially, is the caller's minus sign. See the module docstring.
    """
    return lead * angle / 360


def screw_angle(travel, lead):
    """The degrees of positive rotation that buy ``travel`` of advance
    on a right-hand screw of ``lead`` per turn: ``360 * travel / lead``.

    The exact inverse of :func:`screw_travel` for a nonzero lead.
    """
    return 360 * travel / lead
