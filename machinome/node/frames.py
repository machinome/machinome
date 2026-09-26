# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Where on a part another part attaches: a named frame.

A machine is parts attached to parts, and the place a part is attached
by is a fact about the PART -- the forearm's elbow bore is where it is
whichever arm holds it. Until this module nothing a part declared could
say so, and every attachment was written twice: once as the placement
the parent's `render()` computes by hand, and once as the joint the
child's class restates about the same pin, with constants shared between
the two only so that the numbers agree. A **frame** is the part's own
statement of one connector::

    from machinome.node.frames import Frame

    class Forearm(AssemblyNode):
        hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))

An origin `at` and a right-handed triad whose third axis is `z`, stated
in the declarer's OWN rest frame -- the frame its own `render()` states
its geometry in, the frame a class-declared joint is read in (ADR-097).
An assembly then relates two frames in one sentence that both places the
child and declares its freedom (`machinome.motion.mates`).

A frame is a fifth thing a class body may declare, in the mould of a
marking (ADR-120), and like a marking what matters most is what it is
NOT: it is not a parameter, not a child, not a port, not a joint and not
a part. It is not a `Declaration`, so it never reaches `identity_values`
or `_build_uniq_id` -- a connector changes no geometry, so adding one
cannot change an artifact key -- and it is not a descriptor, so reading
it off an instance hands back the declaration. Unlike a marking it is
allowed on an ASSEMBLY: an assembly's frames are its connectors to the
assembly above it, and along a robot arm's chain of links nearly every
fixed end is the upper link's own frame.

Each argument follows the joint's argument rule (`resolved_vector` in
`machinome.motion.joints`, reused, not restated): three numbers, tokens
or formulas, or one callable of the realized declarer. A frame is
resolved per instance when its declarer is constructed, right after the
declarer's joints, so a frame that cannot resolve refuses its declarer
whether or not any mate names it.

Nothing is imported here at module scope but `math`: the argument rule
is reached inside `resolve`, at construction, where the joint module is
already loaded.
"""

import math


__all__ = ['Frame', 'ResolvedFrame', 'declared_frames',
           'resolve_declared_frames']


# How close to an exact 0, 1 or -1 a normalized component has to be
# before it IS that value: the joint's own `_SNAP`, for the same reason
# -- normalizing `(0, 0, 2)` must give the exact `(0, 0, 1)` a reader
# wrote, not residue.
_SNAP = 1e-9

# How nearly parallel `x` may be to `z` before nothing of it is left
# across `z`: a marking's `_PARALLEL_TOLERANCE`.
_PARALLEL_TOLERANCE = 1e-9

#: The instance-dict key a declarer's resolved frames live under.
RESOLVED_KEY = '_frame_arguments'


def _is_frame(value):
    """Whether `value` is a frame declaration: duck-typed on
    `frame_kind`, as a marking is on `marking_kind`, so
    `machinome.node.declarative` can ask without importing this
    module."""
    return getattr(type(value), 'frame_kind', None) == 'frame'


def _snapped(value):
    for exact in (0, 1, -1):
        if abs(value - exact) <= _SNAP:
            return exact
    return value


def _dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def _cross(first, second):
    return (first[1] * second[2] - first[2] * second[1],
            first[2] * second[0] - first[0] * second[2],
            first[0] * second[1] - first[1] * second[0])


def _principal_next(z):
    """The next principal axis after a principal `z`, in right-hand
    order, carrying `z`'s sign -- `+X` for `+Z`, `+Y` for `+X`, `+Z` for
    `+Y`, the negated axis for a negated one -- or None when `z` is not
    along a principal axis. This is exactly where `Wrapped`'s derived
    zero lands for the six principal directions; for every other
    direction a frame refuses to derive one (design decision 2)."""
    nonzero = [index for index, component in enumerate(z) if component != 0]
    if len(nonzero) != 1:
        return None
    index = nonzero[0]
    x = [0, 0, 0]
    x[(index + 1) % 3] = 1 if z[index] > 0 else -1
    return tuple(x)


class ResolvedFrame:
    """A frame resolved against one realized declarer: an origin and
    three unit directions, every component a plain number."""

    __slots__ = ('at', 'x', 'y', 'z')

    def __init__(self, at, x, y, z):
        self.at = at
        self.x = x
        self.y = y
        self.z = z

    def rotation(self):
        """The 3x3 whose COLUMNS are `x`, `y`, `z`, as rows."""
        return [[self.x[row], self.y[row], self.z[row]] for row in range(3)]

    def __repr__(self):
        return (f'<frame at={self.at} x={self.x} y={self.y} '
                f'z={self.z}>')


class Frame:
    """A connector on a part: `Frame(at=(0, 0, 0), z=(0, 0, 1),
    x=None)`, in the declarer's own rest frame.

    `z` is the line a revolute mate turns about unless the mate's
    freedom states one; `x` fixes the attitude around it, and therefore
    the zero of a revolute mate's coordinate -- the frames fix where the
    child rests whatever line the freedom states.
    Neither need be a unit vector. Left out, `x` is the next principal
    axis after a principal `z`; a `z` along no principal axis must state
    its `x`, because a derived one would be a zero nobody can read off
    the declaration.

    An ordinary class attribute, NOT a data descriptor and NOT a
    `Declaration` -- the marking's reasons, restated in
    `machinome.node.markings.Marking`.
    """

    frame_kind = 'frame'

    def __init__(self, at=(0, 0, 0), z=(0, 0, 1), x=None):
        self.at = at
        self.z = z
        self.x = x
        self._name = None
        self.owner = None

    @property
    def name(self):
        """The attribute this frame was declared under."""
        return self._name

    def __set_name__(self, owner, name):
        if self._name is not None and self._name != name:
            raise TypeError(
                f"'{name}' on {owner.__name__} is the frame already named "
                f"'{self._name}': a frame is one connector on one part, so "
                f"it cannot be assigned under two names. Declare a second "
                f"frame.")
        self._name = name
        if self.owner is None:
            self.owner = owner

    def on(self, fixed, freedom=None):
        """This frame, as the MOVING end of a mate: refused at class
        creation, because the frame an assembly states about itself
        cannot move within that assembly. Recorded rather than raised
        here so the refusal can name the mate it would have been
        (`machinome.motion.mates`)."""
        from machinome.motion.mates import state_mate

        return state_mate(self, fixed, freedom)

    ##############################################
    # Resolution

    def _refusal(self, node, argument, detail):
        from machinome.parameters import ParameterError

        return ParameterError(
            f"{type(node).__name__}.{self._name}: frame argument "
            f"{argument} -- {detail}")

    def resolve(self, node):
        """This frame, resolved against the realized `node` that
        declares it: a `ResolvedFrame`, or `ParameterError` naming the
        class, the frame and the argument."""
        from machinome.motion.joints import resolved_vector

        def refusal(argument, detail):
            return self._refusal(node, argument, detail)

        at = resolved_vector(node, self.at, 'at', refusal)
        z = resolved_vector(node, self.z, 'z', refusal)
        length = math.sqrt(_dot(z, z))
        if length < _SNAP:
            raise refusal(
                'z', f'{self.z!r} has no direction: a z of zero length '
                f'states no line')
        z = tuple(_snapped(component / length) for component in z)
        if self.x is None:
            x = _principal_next(z)
            if x is None:
                raise refusal(
                    'x', f'z={self.z!r} lies along no principal axis, so '
                    f'x must be stated: x fixes the attitude about z, and '
                    f'the zero of a revolute mate, and a derived one would '
                    f'be invisible in the declaration. Write x=(...), any '
                    f'direction across z.')
        else:
            stated = resolved_vector(node, self.x, 'x', refusal)
            along = _dot(stated, z)
            across = tuple(component - along * direction
                           for component, direction in zip(stated, z))
            size = math.sqrt(_dot(across, across))
            if size <= _PARALLEL_TOLERANCE * max(
                    1.0, math.sqrt(_dot(stated, stated))):
                raise refusal(
                    'x', f'{self.x!r} is parallel to z={self.z!r}, so it '
                    f'fixes no attitude about it. State an x across z.')
            x = tuple(_snapped(component / size) for component in across)
        y = tuple(_snapped(component) for component in _cross(z, x))
        return ResolvedFrame(at, x, y, z)

    def __repr__(self):
        return (f'<Frame {self._name or ""} at={self.at!r} z={self.z!r} '
                f'x={self.x!r}>')


def declared_frames(node_class):
    """Every frame declared on `node_class`, by attribute, in
    declaration order.

    Walks `reversed(node_class.__mro__)` in the shape of
    `declared_markings`, later classes winning, so a frame is inherited
    like any class attribute -- including from a PLAIN MIXIN -- and a
    subclass assigning `None` to the attribute removes the inherited
    entry.

    Kept on the completed class itself once `NodeMeta` has finished it,
    as `declared_ports` keeps its map: the node constructor asks on
    every construction, and a class that declares no frame must pay one
    dictionary read for it.
    """
    complete = vars(node_class).get('_machinome_declarations_complete',
                                    False)
    if complete:
        cached = vars(node_class).get('_machinome_declared_frames')
        if cached is not None:
            return dict(cached)
    found = {}
    for klass in reversed(node_class.__mro__):
        for attribute, value in vars(klass).items():
            if _is_frame(value):
                found[attribute] = value
            elif value is None and attribute in found:
                del found[attribute]
    if complete:
        setattr(node_class, '_machinome_declared_frames',
                tuple(found.items()))
    return found


def resolve_declared_frames(node):
    """Resolve every frame `node`'s class declares against `node`,
    cached under `_frame_arguments` in its instance dict.

    Called by the node constructor right after
    `resolve_declared_joints`: after the node's parameters and its
    `check()`, before any child is realized -- ADR-088's earliest point
    a value could be wrong -- so a refused declarer has realized
    nothing.
    """
    frames = declared_frames(type(node))
    if not frames:
        return
    resolved = node.__dict__.setdefault(RESOLVED_KEY, {})
    for name, frame in frames.items():
        resolved[name] = frame.resolve(node)
