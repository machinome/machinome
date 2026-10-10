# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

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

Two reads, one for each question. `declared_frames(<Class>)` gives the
DECLARATIONS off the class, arguments as written; `resolved_frames(node)`
gives a realized node's frames as NUMBERS, each a `ResolvedFrame` -- the
resolution its constructor made and its mates compose with. Only an
instance has numbers, because a frame's arguments may read its
parameters or be a function of it; and reading a frame as an attribute
of an instance still gives the declaration.

Only `math` and `functools.wraps` are imported at module scope: the argument rule
is reached inside `resolve`, at construction, where the joint module is
already loaded.
"""

import math
from functools import wraps


__all__ = ['Frame', 'ResolvedFrame', 'declared_frames',
           'resolve_declared_frames', 'resolved_frames']


# On the omitted-direction path, how close to 0, 1 or -1 every component of
# a direction must be before the direction IS that principal axis: the
# joint's own `_SNAP`, for the same reason -- normalizing `(0, 0, 2)` must
# give the exact `(0, 0, 1)` a reader wrote, not residue. A direction
# snaps only as a whole, by the joint's `_snapped_direction`, so it stays
# unit (snap-keeps-the-triad-unit); here `_SNAP` also refuses a
# zero-length `z`.
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
    """A frame resolved against one realized declarer, as
    `resolved_frames(node)` reads it: an origin and three unit
    directions, each a tuple of three plain numbers in the declarer's
    own rest frame.

    - `at`: the origin, three `float` values.
    - `x`, `y`, `z`: a right-handed triad of unit directions -- `z` the
      declared `z` normalized, `x` the declared `x` squared up against
      `z` and normalized (or, left out, the next principal axis after a
      principal `z`), `y` equal to `z` cross `x`, each unit to within
      `1e-12`. Supplying both directions explicitly retains
      normalized/projected/cross-product precision without component
      snap, including an explicit default `z=(0, 0, 1)`. With `z` omitted,
      or `x` omitted or None, each direction snaps as a whole: one whose
      EVERY component is within `1e-9` of `0`, `1` or `-1` IS that
      principal axis, in `int`, so `z=(0, 0, 2)` reads `(0, 0, 1)`; in any
      other direction only a component within `1e-9` of `0` is the `int`
      `0`, so a direction a few millionths off an axis reads as the unit
      direction it is. A joint's axis snaps by the same rule; the final
      mate angle/axis snap is unchanged.
    - `rotation()`: the 3x3 as a list of three rows whose columns are
      `x`, `y` and `z`, the rotation carrying the frame's axes onto the
      declarer's.

    Read it; do not assign to it. The object is the one the node's mates
    compose with, so assigning an attribute would move a mate placed
    afterwards. A project never constructs one.
    """

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


def _record_explicit_z(initializer):
    """Capture presence before defaults fill in, including super().__init__.

    wraps retains the public constructor signature and literal defaults.
    """
    @wraps(initializer)
    def initialize(self, *args, **kwargs):
        initializer(self, *args, **kwargs)
        self._z_explicit = len(args) >= 2 or 'z' in kwargs
    return initialize


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

    Supplying both directions explicitly retains full floating-point precision:
    normalize `z`, project and normalize `x`, then cross `z` with `x`, without
    component snap. An explicit default `z=(0, 0, 1)` counts; `Frame(x=...)`
    with `z` omitted snaps, as does omitted `x` or `x=None`: each direction
    snaps as a whole, exactly a principal axis when every component is
    within `1e-9` of `0`, `1` or `-1`, otherwise only its components within
    `1e-9` of `0` made `0`, so it stays unit. Zero/parallel refusals are
    unchanged. `resolved_frames` reads the same cached basis mates use. A
    joint's axis snaps by the same rule; the final mate angle/axis snap is
    unchanged.

    An ordinary class attribute, NOT a data descriptor and NOT a
    `Declaration` -- the marking's reasons, restated in
    `machinome.node.markings.Marking`.
    """

    frame_kind = 'frame'

    @_record_explicit_z
    def __init__(self, at=(0, 0, 0), z=(0, 0, 1), x=None):
        self.at = at
        self.z = z
        self.x = x
        self._name = None
        self.owner = None

    @property
    def name(self):
        """The attribute this frame was declared under. A mate whose fixed
        end is a frame of the assembly itself, written by its bare name,
        holds this declaration as its `fixed`, so the end reads as
        `mate.fixed.name`."""
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
        from machinome.motion.joints import (_snapped_direction,
                                             resolved_vector)

        def refusal(argument, detail):
            return self._refusal(node, argument, detail)

        at = resolved_vector(node, self.at, 'at', refusal)
        z = resolved_vector(node, self.z, 'z', refusal)
        precise = self._z_explicit and self.x is not None
        direction = tuple if precise else _snapped_direction
        length = math.sqrt(_dot(z, z))
        if length < _SNAP:
            raise refusal(
                'z', f'{self.z!r} has no direction: a z of zero length '
                f'states no line')
        z = direction(component / length for component in z)
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
            x = direction(component / size for component in across)
        y = direction(_cross(z, x))
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

    The constructor's hook, not a read: calling it again resolves again.
    A project reads the resolved frames with `resolved_frames`.

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



def resolved_frames(node):
    """Every frame the realized `node`'s class declares, by name, in
    declaration order, as the numbers it resolved to when `node` was
    constructed: `{name: ResolvedFrame}`.

    The objects are the very ones a mate composes with -- the node's
    single resolution, not a second one -- so a function given as a
    frame argument is not called again. Each read is a new `dict`;
    removing a key from it changes nothing the node or its mates use.
    A node whose class declares no frame reads `{}`, and a frame a
    subclass removed with `None` is not in the mapping.

    It takes an instance because only an instance has numbers: a
    frame's arguments may read the declarer's parameters or be a
    function of it. The declarations themselves, arguments as written,
    are `declared_frames(<Class>)`; reading a frame as an attribute of
    an instance also gives the declaration.

    Raises `TypeError` for a class, for anything that is not a realized
    node (a child declaration read off a class body, a `Frame`, a
    number), and for a node whose frames are not resolved yet -- a read
    made from its own `check()`, or from a function given as one of its
    joint or frame arguments.
    """
    from machinome.node.base import AbstractBaseNode

    if isinstance(node, type):
        raise TypeError(
            f"resolved_frames({node.__name__}) was given a class. A frame "
            f"resolves against the instance that declares it -- its "
            f"arguments may read that instance's parameters or be a "
            f"function of it -- so only a realized node has numbers. Read "
            f"the declarations with declared_frames({node.__name__}), or "
            f"the numbers with resolved_frames({node.__name__}(...)).")
    if not isinstance(node, AbstractBaseNode):
        raise TypeError(
            f"resolved_frames() was given a {type(node).__name__}, and it "
            f"reads a realized node: an instance of a node class, whose "
            f"frames resolved when it was constructed.")
    declared = declared_frames(type(node))
    cached = node.__dict__.get(RESOLVED_KEY, {})
    pending = [name for name in declared if name not in cached]
    if pending:
        raise TypeError(
            f"resolved_frames() was given a {type(node).__name__} whose "
            f"frames are not resolved yet ({', '.join(pending)}). A node's "
            f"frames resolve after its check() and its joints, so they "
            f"cannot be read from check(), or from a function given as one "
            f"of its joint or frame arguments.")
    return {name: cached[name] for name in declared}
