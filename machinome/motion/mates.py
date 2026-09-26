# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Two frames related in one sentence: a mate.

A robot arm's elbow is one physical pin, and without a mate it is
stated three times: a rest placement in the upper arm's `render()`, a
joint in the forearm's class read in the forearm's own frame, and
constants shared between the two only so that the numbers agree. An
assembly CAD design states it once -- a connector on each side and how
they meet -- and so does a mate::

    class UpperArm(AssemblyNode):
        elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))

        forearm = Forearm()          # declares hinge = Frame(...)

        elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135)))

The frame that speaks MOVES. The moving end is a frame declared by a
child the assembly declares directly; the fixed end is a frame of the
assembly itself, written by its bare name, or of another directly
declared child that does not move. The freedom is a `Revolute`; by
default the moving frame's `z` is the line it turns about and the
frame's origin its anchor. A design's connectors are ATTACHMENT frames,
though, and the line a part turns about need not be the connector's `z`
nor pass through its origin, so the freedom may state its own line,
`Revolute(axis=(x, y, z), at=(x, y, z))`, in three numbers each, read in
the moving child's own frame; each it leaves out, the frame supplies.
The frames still fix where the child rests, and so the zero of its
coordinate; the freedom fixes only the line (ADR-148).

A mate compiles, at realization, to three things the framework already
has and invents no fourth (ADR-147):

1. the moving child's REST PLACEMENT -- `P_owner . F_fixed .
   F_moving^-1` as one rotation then one translation, ordinary
   operations appended after the author's `render()` returns
   (`apply_mates`, called from `machinome.node.assembly._rest`);
2. a revolute JOINT of the moving child's class, whose axis and anchor
   are the ones the freedom states, else the moving frame's `z` and `at`
   as DECLARED, installed by
   `_specialize` -- ADR-098's mechanism -- under the mate's name, so it
   takes a slot after every joint the child's own class declares;
3. a rotational COORDINATE of the assembly under the mate's name --
   this object, a `Coordinate` owning one port -- which relations,
   drivers and bindings see as an ordinary coordinate and which reaches
   the child's joint through a wiring (ADR-088), the one wiring whose
   unbound source is not refused: an unbound mate rests, as an unbound
   joint does.

A `Mate` is deliberately NOT a `Joint`: `declared_joints` enumerates by
`isinstance(value, Joint)` and `clear_solved` finds a coordinate's joint
the same way, and a mate moves no body of the assembly that declares it.

Module scope imports `machinome.motion.ports` and nothing else, as
`joints` and `couplings` do. The arithmetic is pure Python on 3x3 lists;
the one `matrix()` read of a fixed child's rest placement happens inside
a live render, where the geometry stack is loaded anyway.
"""

import math

from machinome.motion.ports import Coordinate, RotationalPort, bind


__all__ = ['FrameRef', 'Mate', 'apply_mates', 'declared_mates']


# A rotation angle or axis component this close to a whole number IS
# that number (design decision 4): axis-angle extraction leaves residue
# -- `120.00000000000001` degrees, `(0, 0.7071067811865476,
# 0.7071067811865475)` -- that would otherwise be published.
_SNAP = 1e-9


def _is_frame(value):
    return getattr(type(value), 'frame_kind', None) == 'frame'


def _is_mate(value):
    return getattr(type(value), 'mate_kind', None) == 'mate'


class FrameReadError(AttributeError):
    """A class body read an attribute through a frame reference."""


class FrameRef:
    """A frame of a child declaration, named in a class body: a PLACE,
    like a path reference to a port, never the frame's resolved numbers,
    which belong to a realized instance.

    Shares `PathRef`'s shape -- `(root, segments, frame)` -- and its
    list-held and repeat facts, which the mate statement refuses by
    name; reading one is never refused merely for being written. It is
    not a coordinate: `drives`, arithmetic and any further attribute
    read through it are refused, naming the path.
    """

    frame_kind = 'reference'

    def __init__(self, root, segments, frame, repeat=None):
        self.root = root
        self.segments = tuple(segments)
        self.frame = frame
        self.repeat = repeat

    @property
    def written(self):
        head = self.root._name or f'<{self.root.node_class.__name__} in a list>'
        return '.'.join((head,) + self.segments)

    @property
    def depth(self):
        """How many children the path steps through: 1 for
        `<child>.<frame>`."""
        return len(self.segments)

    def on(self, fixed, freedom=None):
        """Mate this frame, which MOVES, onto `fixed`, with `freedom`."""
        return state_mate(self, fixed, freedom)

    def drives(self, *_args, **_kwargs):
        raise TypeError(_not_a_coordinate(self.written))

    def _refuse_arithmetic(self, *_args, **_kwargs):
        raise TypeError(_not_a_coordinate(self.written))

    __add__ = __radd__ = __sub__ = __rsub__ = _refuse_arithmetic
    __mul__ = __rmul__ = __truediv__ = __neg__ = _refuse_arithmetic
    __and__ = __rand__ = __float__ = _refuse_arithmetic

    def __getattr__(self, attribute):
        if attribute.startswith('_'):
            raise AttributeError(attribute)
        raise FrameReadError(
            f"cannot read '{attribute}' through {self.written}: that path "
            f"names a frame -- a connector, not a coordinate or a child -- "
            f"and a frame has no parts. A frame is an end of a mate: "
            f"{self.written}.on(<fixed frame>, Revolute(...)).")

    def __repr__(self):
        return f'<frame {self.written}>'


def _not_a_coordinate(written):
    return (f"'{written}' is a frame: a connector, not a coordinate. A "
            f"frame is an end of a mate, "
            f"{written}.on(<fixed frame>, Revolute(...)), and the mate's "
            f"name is the coordinate a relation names.")


##############################################
# The statement

def state_mate(moving, fixed, freedom):
    """`moving.on(fixed, freedom)`: build the mate and record it on the
    executing class body, through the channel a relation is recorded
    through (ADR-089). Nothing is refused here that needs the mate's
    NAME, which only the assignment gives it: every refusal is made when
    the class is created (`declare_mates`), naming the class, the mate
    and the reason.

    Two facts are only knowable NOW, while the body runs, and are
    recorded for that later judgement: whether `freedom` was already
    bound to a name in this body (a fresh `Revolute(...)` never is), and
    that a mate claimed it -- so a freedom ALSO assigned in the body is
    refused by the mate, by name, rather than by the axis-less joint
    refusal of `Joint.__set_name__`.
    """
    from machinome.node.declarative import _in_current_body, record_mate

    in_body = freedom is not None and _in_current_body(freedom)
    if freedom is not None and hasattr(freedom, '_mate_freedom'):
        freedom._mate_freedom = True
    mate = Mate(moving, fixed, freedom, freedom_in_body=in_body)
    record_mate(mate)
    return mate


class Mate(Coordinate):
    """`moving.on(fixed, freedom)`: the declaration, and -- with a
    freedom -- the rotational coordinate it owns on the assembly.

    A data descriptor, like a joint, so reading it on an instance yields
    the bound port slot and assigning to it binds; a `Coordinate`, so
    `drives` and the arithmetic of a derived coordinate treat it as one.
    It owns its port as `coordinate` and `coordinates`, which is what
    makes `declared_ports` report it with no change there and a relation
    end resolve it.
    """

    mate_kind = 'mate'
    # Named by the declaring namespace the moment it is assigned, as a
    # relation is, so a refusal raised while the body still runs can say
    # which mate it means.
    _names_in_body = True
    _name = None
    owner = None
    # The flag the mate's wiring carries: an unbound source leaves the
    # child's joint unbound instead of being refused (design decision 6).
    rests_unbound = True

    def __init__(self, moving, fixed, freedom, freedom_in_body=False):
        self.moving = moving
        self.fixed = fixed
        self.freedom = freedom
        self.freedom_in_body = freedom_in_body
        unit = getattr(freedom, 'unit', None) or 'deg'
        self.coordinate = RotationalPort(unit=unit)
        self.coordinates = {None: self.coordinate}
        #: The joint this mate installs on the moving child, once the
        #: assembly's class exists.
        self.joint = None

    @property
    def name(self):
        return self._name

    def __set_name__(self, owner, name):
        for klass in owner.__mro__[1:]:
            existing = vars(klass).get(name, _MISSING)
            if existing is _MISSING or _is_mate(existing):
                continue
            raise TypeError(
                f"mate '{name}' on {owner.__name__} would shadow "
                f"{klass.__name__}.{name}, which a read of the mate's "
                f"coordinate would then hide for good. A mate's coordinate "
                f"is read as an attribute of the assembly, so its name has "
                f"to be free there: rename the mate.")
        self._name = name
        self.owner = owner
        self.coordinate.name = name
        self.coordinate.owner = owner
        self.coordinates = {name: self.coordinate}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.coordinate.__get__(instance)

    def __set__(self, instance, value):
        bind(self.coordinate.__get__(instance), value)

    def described(self):
        fixed = (self.fixed.written if isinstance(self.fixed, FrameRef)
                 else getattr(self.fixed, 'name', None) or repr(self.fixed))
        moving = (self.moving.written if isinstance(self.moving, FrameRef)
                  else getattr(self.moving, 'name', None)
                  or repr(self.moving))
        return f'{moving}.on({fixed}, ...)'

    def __repr__(self):
        return f"<mate {self._name or ''}: {self.described()}>"


_MISSING = object()


##############################################
# Enumeration

def declared_mates(node_class):
    """Every mate declared on `node_class`, by name, in declaration
    order: a base's before a subclass's. Read off the class, so nothing
    is instantiated."""
    return {mate.name: mate
            for mate in getattr(node_class, '_declared_mates', ())}


##############################################
# Class creation

def _named(cls_name, mate):
    """How a refusal names a mate: `Class.mate`, or the statement when
    it was never assigned."""
    if mate.name:
        return f'{cls_name}.{mate.name}'
    return f'{cls_name}: the unnamed mate {mate.described()}'


def declare_mates(cls, name, own):
    """Validate every mate `cls` carries and record its own ones.

    Called from `NodeMeta.__new__` BEFORE the class's relations are
    checked, because a relation in the same body may name a mate. `own`
    is what this class body stated, in order; inherited mates are read
    off the bases and re-checked against this class's children, since a
    subclass may have replaced the child a mate was written against.
    """
    from machinome.node.assembly import AssemblyNode

    inherited = []
    for base in reversed(cls.__mro__[1:]):
        for mate in base.__dict__.get('_own_mates', ()):
            if not any(mate is seen for seen in inherited):
                inherited.append(mate)

    if own and not issubclass(cls, AssemblyNode):
        raise TypeError(
            f"{_named(name, own[0])} is a mate, and {name} is not an "
            f"AssemblyNode. A mate places one child against a frame and "
            f"gives it a freedom, so it is stated on the assembly that "
            f"holds both frames.")

    for mate in inherited:
        _check_still_declared(cls, name, mate)

    placed = {}
    for mate in inherited:
        placed[id(mate.moving.root)] = mate
    for mate in own:
        _check_freedom(name, mate)
        if mate.name is None:
            raise TypeError(
                f"{_named(name, mate)} is never assigned. A mate with a "
                f"freedom owns a coordinate, and the coordinate is named "
                f"after the mate: write <name> = {mate.described()}.")
        _check_moving(cls, name, mate)
        earlier = placed.get(id(mate.moving.root))
        if earlier is not None:
            raise TypeError(
                f"{name}: the mates '{earlier.name}' and '{mate.name}' both "
                f"move '{mate.moving.root._name}'. A child is placed by one "
                f"mate; a second mate on a placed child closes a loop, "
                f"which this version does not solve.")
        placed[id(mate.moving.root)] = mate
    for mate in own:
        _check_fixed(cls, name, mate, placed)
        _check_child_name(name, mate)
    for mate in own:
        _install(cls, name, mate)

    cls._own_mates = tuple(own)
    cls._declared_mates = tuple(inherited) + tuple(own)


def _check_still_declared(cls, name, mate):
    from machinome.node.declarative import declared_children

    from machinome.node.frames import declared_frames

    if _is_frame(mate.fixed) and not any(
            mate.fixed is mine for mine in declared_frames(cls).values()):
        raise TypeError(
            f"{name}.{mate.name}: the mate {mate.name} inherited from "
            f"{mate.owner.__name__} is fixed on the frame "
            f"'{mate.fixed.name}', which {name} no longer declares. "
            f"Restate the mate in {name}.")
    children = declared_children(cls)
    for end in (mate.moving, mate.fixed):
        if not isinstance(end, FrameRef):
            continue
        if children.get(end.root._name) is not end.root:
            raise TypeError(
                f"{name}.{mate.name}: the mate {mate.name} inherited from "
                f"{mate.owner.__name__} names '{end.root._name}', and "
                f"{name} declares '{end.root._name}' anew. The mate was "
                f"written against {mate.owner.__name__}'s child, which "
                f"{name} no longer declares; restate the mate in {name}.")


def _check_freedom(name, mate):
    """The freedom a mate accepts in this version: a fresh `Revolute`
    whose stated line, if any, is three numbers with a direction, and
    whose range is independent of any declarer."""
    from machinome.motion.joints import Bound, Revolute

    freedom = mate.freedom
    where = _named(name, mate)
    if freedom is None:
        raise TypeError(
            f"{where} states no freedom. The rigid mate -- a child "
            f"placed by two frames with no freedom at all -- is not "
            f"provided in this version (deferred, OpenSpec change "
            f"place-parts-by-mate); a mate's freedom is a Revolute: "
            f"...on(<fixed>, Revolute(range=(lo, hi))).")
    if not isinstance(freedom, Revolute):
        raise TypeError(
            f"{where} has the freedom {type(freedom).__name__}, and a mate "
            f"accepts a Revolute only in this version: Prismatic, Orbit "
            f"and Free are not mate freedoms yet. Write "
            f"Revolute(range=(lo, hi), unit='deg').")
    if mate.freedom_in_body or freedom.owner is not None:
        declared = (f'on {freedom.owner.__name__}' if freedom.owner
                    is not None else 'in this class body')
        raise TypeError(
            f"{where}: its freedom is already declared {declared}. A "
            f"mate's freedom becomes a joint of the child it moves, so it "
            f"is written fresh in the statement: "
            f"...on(<fixed>, Revolute(range=(lo, hi))).")
    if freedom.axis is not None:
        _check_stated(where, 'axis', freedom.axis)
    if freedom.anchor_written:
        _check_stated(where, 'at', freedom.at)
    declared = freedom.range
    if declared is None:
        return
    reason = None
    if callable(declared):
        reason = ('is a callable of the node, which would be resolved '
                  'against the moving child')
    elif (isinstance(declared, (str, bytes))
          or not hasattr(declared, '__len__') or len(declared) != 2):
        reason = 'is not a plain (lo, hi) pair'
    else:
        for bound in declared:
            if bound is None or _is_number(bound):
                continue
            if isinstance(bound, Bound):
                if bound.reads:
                    reason = (f'has a bound reading other coordinates '
                              f'({bound.described()})')
                    break
                continue
            if callable(bound) and not hasattr(bound, 'dimension'):
                continue
            reason = (f'has the bound {bound!r}, which is not a number, '
                      f'None or a function of the coordinate itself')
            break
    if reason is not None:
        raise TypeError(
            f"{where}: its freedom's range {declared!r} {reason}. The "
            f"range of a mate's freedom is written in the assembly and "
            f"resolved on the child it moves, so it is admitted only as "
            f"numbers, None, or functions of the coordinate's own value.")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_stated(where, argument, value):
    """A line a freedom states: three numbers, and an axis with a
    direction (state-the-mate-line, design decision 5).

    The installed joint resolves its arguments against the moving CHILD,
    and a parameter token resolves by NAME, so a token or formula
    written in the assembly would silently read the child's parameter of
    the same name, and a callable would be called with the child. The
    values are numbers, so a zero-length axis -- below the joint's own
    `1e-9` threshold -- is known here, where the refusal can name the
    mate, rather than at realization.
    """
    reason = None
    if hasattr(value, 'dimension'):
        reason = ('is a parameter token or a formula, which would resolve '
                  "against the moving child's parameters of the same name")
    elif callable(value):
        reason = ('is a callable of the node, which would be called with '
                  'the moving child')
    elif isinstance(value, (str, bytes)) or not hasattr(value, '__len__'):
        reason = 'is not a sequence of three numbers'
    elif len(value) != 3:
        reason = f'has {len(value)} components, not three'
    else:
        for component in value:
            if _is_number(component):
                continue
            if isinstance(component, bool):
                reason = f'holds {component!r}, a bool, not a number'
            elif hasattr(component, 'dimension'):
                reason = (f'holds {component!r}, a parameter token or a '
                          f'formula, which would resolve against the moving '
                          f"child's parameter of the same name")
            else:
                reason = f'holds {component!r}, which is not a number'
            break
    if reason is not None:
        raise TypeError(
            f"{where}: its freedom's {argument} {value!r} {reason}. A line "
            f"a mate's freedom states is written in the assembly and read "
            f"in the moving child's frame, so it is three numbers: "
            f"{argument}=(x, y, z).")
    if argument == 'axis' and math.sqrt(
            sum(component ** 2 for component in value)) < _SNAP:
        raise TypeError(
            f"{where}: its freedom's axis {value!r} has zero length, and an "
            f"axis of zero length states no line to turn about. State the "
            f"direction of the line, or leave axis out to turn about the "
            f"moving frame's z.")


def _check_end_shape(name, mate, end, role):
    """A list-held, repeated or deeper-than-one-child frame reference at
    either end, refused by name."""
    where = _named(name, mate)
    if end.root._name is None:
        raise TypeError(
            f"{where}: its {role} end {end.written} is reached through a "
            f"child held in a list. A list-held child is named "
            f"'<attribute>-<index>' and its children one by one, so it "
            f"cannot be an end of a mate; hold the "
            f"{end.root.node_class.__name__} on its own attribute.")
    if end.repeat is not None:
        raise TypeError(
            f"{where}: its {role} end {end.written} passes through "
            f"'{end.repeat._name}', declared with .repeat(). A mate places "
            f"ONE child against ONE frame, and a repeat realizes many; "
            f"declare the children individually, or state the mate inside "
            f"the repeated class.")
    if end.depth > 1:
        raise TypeError(
            f"{where}: its {role} end {end.written} is reached through "
            f"more than one child. In this version both ends of a mate "
            f"are frames of a child the assembly declares directly (or, "
            f"for the fixed end, of the assembly itself): a grandchild's "
            f"placement is its own parent's, decided after this "
            f"assembly's. State the mate in "
            f"{end.root.node_class.__name__}, or declare the frame on "
            f"'{end.root._name}'.")


def _check_moving(cls, name, mate):
    from machinome.node.declarative import declared_children

    where = _named(name, mate)
    moving = mate.moving
    if _is_frame(moving):
        raise TypeError(
            f"{where}: its moving end is {name}'s own frame "
            f"'{moving.name}'. The frame that speaks is the one that "
            f"MOVES, and the assembly's own frame cannot move within it: "
            f"the moving end is a frame declared by a directly declared "
            f"child, <child>.<frame>.on({moving.name}, Revolute(...)).")
    if not isinstance(moving, FrameRef):
        raise TypeError(
            f"{where}: its moving end {moving!r} is not a frame; the "
            f"moving end is a frame declared by a directly declared "
            f"child.")
    _check_end_shape(name, mate, moving, 'moving')
    child = moving.root._name
    if declared_children(cls).get(child) is not moving.root:
        raise TypeError(
            f"{where}: its moving end {moving.written} names '{child}', "
            f"which is not a child {name} declares.")
    if vars(cls).get(child) is not moving.root:
        owner = next((klass.__name__ for klass in cls.__mro__[1:]
                      if vars(klass).get(child) is moving.root), 'a base')
        raise TypeError(
            f"{where}: its moving end {moving.written} is a child "
            f"{owner} declares, and {name} inherits it. A mate gives the "
            f"child it moves a joint of its own, on the declaration "
            f"{owner} shares with every other subclass; state the mate in "
            f"{owner}, or redeclare '{child}' in {name}.")


def _check_fixed(cls, name, mate, placed):
    from machinome.motion.joints import declared_joints
    from machinome.node.declarative import declared_children
    from machinome.node.frames import declared_frames

    where = _named(name, mate)
    fixed = mate.fixed
    if _is_frame(fixed):
        if not any(fixed is mine for mine in declared_frames(cls).values()):
            raise TypeError(
                f"{where}: its fixed end {fixed!r} is not a frame {name} "
                f"declares. A fixed end is a frame of the assembly, "
                f"written by its bare name, or <child>.<frame>.")
        return
    if not isinstance(fixed, FrameRef):
        raise TypeError(
            f"{where}: its fixed end {fixed!r} is not a frame. A fixed end "
            f"is a frame of the assembly, written by its bare name, or "
            f"<child>.<frame> of a child that does not move.")
    _check_end_shape(name, mate, fixed, 'fixed')
    child = fixed.root._name
    if declared_children(cls).get(child) is not fixed.root:
        raise TypeError(
            f"{where}: its fixed end {fixed.written} names '{child}', "
            f"which is not a child {name} declares.")
    if fixed.root is mate.moving.root:
        raise TypeError(
            f"{where}: both ends are frames of '{child}'. A mate places a "
            f"child against a frame it does not carry.")
    mover = placed.get(id(fixed.root))
    joints = declared_joints(fixed.root.node_class)
    if mover is not None or joints:
        because = (f"the mate '{mover.name}' moves it" if mover is not None
                   else f"its class declares the joint(s) "
                        f"{', '.join(joints)}")
        raise TypeError(
            f"{where}: its fixed end {fixed.written} is on '{child}', which "
            f"can move within {name} -- {because}. A mated child is placed "
            f"against the fixed child's REST placement, and siblings do "
            f"not carry each other, so '{mate.moving.root._name}' would "
            f"rest against '{child}''s rest placement and not follow it. "
            f"Mate onto a frame of {name} itself, or of a child that does "
            f"not move.")


def _check_child_name(name, mate):
    """The mate's name becomes a joint of the moving child's class, so
    it must be free there."""
    from machinome.parameters import _RESERVED

    node_class = mate.moving.root.node_class
    if mate.name in _RESERVED:
        existing = f"the node attribute '{mate.name}' every node carries"
    else:
        existing = None
        for klass in node_class.__mro__:
            found = vars(klass).get(mate.name, _MISSING)
            if found is _MISSING:
                continue
            existing = f'{klass.__name__}.{mate.name} ({_kind_of(found)})'
            break
    if existing is not None:
        raise TypeError(
            f"{name}.{mate.name}: the mate gives "
            f"'{mate.moving.root._name}' a joint named '{mate.name}', and "
            f"{node_class.__name__} already answers to that name: "
            f"{existing}. The joint is read as an attribute of the child, "
            f"so its name has to be free there: rename the mate.")


def _kind_of(value):
    from machinome.motion.joints import Joint
    from machinome.parameters import Declaration

    if isinstance(value, Joint):
        return 'a joint'
    if isinstance(value, Declaration):
        return 'a declared parameter'
    if _is_frame(value):
        return 'a frame'
    if _is_mate(value):
        return 'a mate'
    if callable(value):
        return 'a method'
    return f'{type(value).__name__}'



##############################################
# Class creation: what a mate installs

def _install(cls, name, mate):
    """Give the moving child's declaration the mate's joint and the
    wiring that binds it (design decisions 5 and 6).

    The joint is a `Revolute` whose axis is the freedom's stated `axis`,
    else the moving frame's `z`, and whose anchor is the freedom's
    written `at`, else the moving frame's `at` -- each passed straight
    through, the frame's exactly as DECLARED (a tuple, tokens, formulas
    or a callable of the node), the freedom's as the three numbers
    `_check_stated` admitted. Both are in the child's own rest frame, so
    the joint resolves against the child in `resolve_declared_joints`
    like any class-declared joint, with nothing carried or inverted
    (ADR-097). A left-out `at` is told from a written `(0, 0, 0)` by
    identity (`Revolute.anchor_written`): the written one is the CHILD's
    origin, not the frame's.
    It goes on the child by `_specialize`, ADR-098's mechanism: the
    child keeps its name, identity and artifacts, and the joint -- new
    on the child -- takes the slot after every joint the child's class
    declares (ADR-093).

    The wiring hands the assembly's coordinate to that joint (ADR-088):
    one binder, one address, and relations see only the assembly's port.
    """
    from machinome.motion.joints import Revolute
    from machinome.node.declarative import _specialize

    frame = mate.moving.frame
    freedom = mate.freedom
    joint = Revolute(
        axis=freedom.axis if freedom.axis is not None else frame.z,
        at=freedom.at if freedom.anchor_written else frame.at,
        range=freedom.range, unit=freedom.unit)
    joint.installed_by = mate
    declaration = mate.moving.root
    declaration.node_class = _specialize(declaration.node_class,
                                         {mate.name: joint})
    declaration.wiring[mate.name] = mate
    mate.joint = joint


##############################################
# Realization: the rest placement

def _rotation_of(matrix):
    """The rotation part of a 4x4 (any nested sequence), as rows."""
    return [[float(matrix[row][column]) for column in range(3)]
            for row in range(3)]


def _multiply(first, second):
    return [[sum(first[row][k] * second[k][column] for k in range(3))
             for column in range(3)] for row in range(3)]


def _apply(rotation, vector):
    return tuple(sum(rotation[row][k] * vector[k] for k in range(3))
                 for row in range(3))


def _transposed(rotation):
    return [[rotation[column][row] for column in range(3)]
            for row in range(3)]


def _snapped(value):
    nearest = round(value)
    if abs(value - nearest) <= _SNAP:
        return int(nearest)
    return value


def _axis_angle(rotation):
    """`rotation` as `(angle in degrees, axis)`, or None for the
    identity.

    The angle comes from `atan2(2 sin, 2 cos)`, well conditioned
    everywhere. The axis comes from the antisymmetric part up to 90
    degrees and from the DIAGONAL beyond it, where the antisymmetric
    part shrinks to nothing: `a_i^2 = (R_ii - cos) / (1 - cos)`, signs
    from the symmetric off-diagonal terms and the orientation from the
    antisymmetric part. At exactly 180 degrees the diagonal gives every
    component by the same square root, so a half turn about
    `(0, 1, 1)` reads `(0, sqrt(.5), sqrt(.5))` rather than two
    different last bits.
    """
    trace = rotation[0][0] + rotation[1][1] + rotation[2][2]
    skew = (rotation[2][1] - rotation[1][2],
            rotation[0][2] - rotation[2][0],
            rotation[1][0] - rotation[0][1])
    twice_sine = math.sqrt(sum(component * component for component in skew))
    angle = math.degrees(math.atan2(twice_sine, trace - 1))
    if abs(angle) <= _SNAP:
        return None
    if angle <= 90:
        axis = [component / twice_sine for component in skew]
    else:
        cosine = max(-1.0, min(1.0, (trace - 1) / 2))
        squares = [max(0.0, (rotation[index][index] - cosine)
                       / (1 - cosine)) for index in range(3)]
        largest = max(range(3), key=lambda index: squares[index])
        axis = [math.sqrt(square) for square in squares]
        for index in range(3):
            if index != largest and (rotation[largest][index]
                                     + rotation[index][largest]) < 0:
                axis[index] = -axis[index]
        if sum(a * b for a, b in zip(axis, skew)) < 0:
            axis = [-component for component in axis]
        length = math.sqrt(sum(component * component for component in axis))
        if abs(length - 1) > 1e-12:
            axis = [component / length for component in axis]
    return _snapped(angle), [_snapped(component) for component in axis]


def _rest_placement(child, mate):
    """The fixed child's REST placement as `(rotation rows, translation)`:
    its non-motion operations composed in list order by
    premultiplication through each operation's own `matrix()`, the
    composition `Joint._carry` makes. Refused by name when an operation
    does not evaluate to a number."""
    import numpy as np

    matrix = np.eye(4)
    for operation in child.operations:
        if getattr(operation, '_motion', False):
            continue
        try:
            matrix = operation.matrix() @ matrix
        except (TypeError, ValueError) as failure:
            raise ValueError(
                f"{mate.owner.__name__}.{mate.name}: the mate's fixed end is a frame of "
                f"'{mate.fixed.root._name}', whose rest placement "
                f"{operation.serialized!r} carries a value that is not a "
                f"number ({failure}). The moving child is placed against "
                f"that placement, so it has to be numeric; place "
                f"'{mate.fixed.root._name}' with numbers in render().") \
                from None
    return _rotation_of(matrix), tuple(float(matrix[row][3])
                                       for row in range(3))


def _placement(assembly, mate):
    """`M = P_owner . F_fixed . F_moving^-1`, as `(rotation rows,
    translation)` in the assembly's frame."""
    from machinome.node.frames import RESOLVED_KEY

    child = assembly.__dict__[mate.moving.root._name]
    moving = child.__dict__[RESOLVED_KEY][mate.moving.segments[0]]
    if _is_frame(mate.fixed):
        fixed = assembly.__dict__[RESOLVED_KEY][mate.fixed.name]
        owner_rotation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        owner_translation = (0, 0, 0)
    else:
        holder = assembly.__dict__[mate.fixed.root._name]
        fixed = holder.__dict__[RESOLVED_KEY][mate.fixed.segments[0]]
        owner_rotation, owner_translation = _rest_placement(holder, mate)

    moving_inverse = _transposed(moving.rotation())
    rotation = _multiply(_multiply(owner_rotation, fixed.rotation()),
                         moving_inverse)
    # F_fixed . F_moving^-1 carries the moving origin onto the fixed one;
    # the owner placement then carries both into the assembly's frame.
    local = tuple(fixed_component - carried for fixed_component, carried
                  in zip(fixed.at, _apply(_multiply(fixed.rotation(),
                                                    moving_inverse),
                                          moving.at)))
    translation = tuple(value + offset + 0.0 for value, offset
                        in zip(_apply(owner_rotation, local),
                               owner_translation))
    return child, rotation, translation


def apply_mates(assembly, phase):
    """Place every child a mate of `assembly` moves, at rest.

    Called by `machinome.node.assembly._rest` once the author's
    `render()` has returned and its phase is popped -- once per instance
    for an ordinary render, on every re-run for a legacy one. `phase` is
    that render's phase: an operation it applied to a mated child is a
    second statement of the child's placement, refused naming the
    assembly, the child and the mate.

    The operations are ordinary untagged rest operations, appended after
    whatever the render placed, so they compose OUTSIDE the child's
    joint block exactly as a hand-written rest placement does (ADR-066,
    ADR-093). Each carries `_mate_slot`, the mate's index in
    `declared_mates`, and a re-run first drops every operation carrying
    that mark -- ADR-114's slot-mark rule -- so it never stacks.
    """
    from machinome.node.operations import Rotation, Translation

    for index, mate in enumerate(getattr(type(assembly),
                                         '_declared_mates', ())):
        name = mate.moving.root._name
        child = assembly.__dict__[name]
        for operation in phase.applied:
            if getattr(operation, 'node', None) is child:
                raise ValueError(
                    f"{type(assembly).__name__}.render() places '{name}' "
                    f"({operation.serialized!r}), and the mate "
                    f"'{mate.name}' places it: a placement is stated once. "
                    f"Drop the placement from render(), or the mate.")
        child.operations[:] = [
            operation for operation in child.operations
            if getattr(operation, '_mate_slot', None) != index]
        child, rotation, translation = _placement(assembly, mate)
        operations = []
        turned = _axis_angle(rotation)
        if turned is not None:
            angle, axis = turned
            operations.append(Rotation(angle, axis, child))
        if any(value != 0 for value in translation):
            operations.append(Translation(list(translation), child))
        for operation in operations:
            operation._mate_slot = index
            child.operations.append(operation)


##############################################
# Binding the installed joint by another route

def refused_binding(sink):
    """The refusal of a binding of the joint a mate installed, by any
    route but the mate's own wiring: it names the mate's coordinate as
    the one to bind (design decision 6's single binder)."""
    from machinome.node.assembly import top_of
    from machinome.node.qualified import DriverIdError, instance_path

    mate = sink.mated_by
    parent_class, attribute, keyword = sink.wired_from
    parent = getattr(sink.node, '_parent', None)
    target = f'{parent_class}.{mate.name}'
    if parent is not None:
        root = top_of(parent)
        if root is not parent:
            try:
                target = '.'.join(instance_path(parent, root)
                                  + (mate.name,))
            except DriverIdError:
                pass
    return ValueError(
        f"cannot bind '{keyword}' of {attribute}: it is the joint the mate "
        f"{parent_class}.{mate.name} gives {attribute}, and a mate's joint "
        f"is bound only through the mate's coordinate. Bind {target} "
        f"instead.")
