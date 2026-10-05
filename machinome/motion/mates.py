# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

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

The freedom may instead be a `Prismatic`, and the child then SLIDES
along the line rather than turning about it, by the same rules save one:
a `Prismatic` states its `axis`, as it must anywhere, so only a
`Revolute` freedom takes the moving frame's `z` (ADR-151)::

    class Palm(AssemblyNode):
        left_seat = Frame(at=(81.7, 21, 0))
        left_finger = Finger()       # declares origin = Frame()
        left_grip = left_finger.origin.on(
            left_seat, Prismatic(axis=(0, 1, 0), range=(-11, 20)))

Its `at` is taken as a `Revolute` freedom's and places nothing: a
translation along a line is the same wherever the line is taken to pass.

A handed design -- one class per joint, instantiated once per side --
states the freedom per instance: its `axis` and its `range` may each be
ONE FUNCTION of the assembly that states the mate, the node whose class
body writes it, as a function given to that assembly's own frame is
(ADR-150)::

    class Mount(AssemblyNode):
        left = Flag(False)
        pin = Frame(at=lambda node: (0, 62.5 if node.left else -62.5, 0))
        link = Link()
        turn = link.origin.on(pin, Revolute(
            axis=lambda node: (0, 1, 0) if node.left else (0, -1, 0),
            range=lambda node: (-200, 80) if node.left else (-80, 200)))

It is called once per realized assembly, with that assembly, as it
realizes the moving child (`call_freedom_functions`, from
`ChildDeclaration.realize`), and never with the child; its result is
checked by the rules the numbers are checked by and taken as they are,
read in the moving child's own frame. A stated `at` stays three numbers.

A part that is HELD -- bolted, pressed, seated -- has no freedom, and the
freedom is then left out: the RIGID mate (ADR-152)::

    class Shin(AssemblyNode):
        servo_seat = Frame(at=(-0.98, -4, -7), z=(1, 0, 0), x=(0, 0, 1))
        servo = Servo()              # declares ears = Frame(...)
        bolted = servo.ears.on(servo_seat)

It places the child as every mate does and compiles to nothing else: no
joint on the child, whose class stays the declared one, no coordinate on
the assembly, no wiring. The child moves only as the assembly that
declares it moves, so a held part is declared in the class of the part
that holds it; its fixed end follows every fixed end's rule.

A fresh-freedom mate compiles, at realization, to three things the framework already
has and invents no fourth (ADR-147) -- a rigid mate to the first alone:

1. the moving child's REST PLACEMENT -- `P_owner . F_fixed .
   F_moving^-1` as one rotation then one translation, ordinary
   operations appended after the author's `render()` returns
   (`apply_mates`, called from `machinome.node.assembly._rest`);
2. a JOINT of the moving child's class, of the freedom's kind -- a
   `Revolute` or a `Prismatic` -- whose axis and anchor are the ones the
   freedom states, else the moving frame's `z` (a `Revolute` freedom's
   only) and `at` as DECLARED, installed by
   `_specialize` -- ADR-098's mechanism -- under the mate's name, so it
   takes a slot after every joint the child's own class declares; an
   axis or range the freedom states as a function of the assembly is
   what that function returned, resolved with the rest against the
   child when the assembly realizes it (`resolve_freedom_functions`);
3. a COORDINATE of the assembly under the mate's name, of the
   freedom's port kind -- rotational for a `Revolute`, translational for
   a `Prismatic` -- and in its unit: this object, a `Coordinate` owning
   one port, which relations,
   drivers and bindings see as an ordinary coordinate and which reaches
   the child's joint through a wiring (ADR-088), the one wiring whose
   unbound source is not refused: an unbound mate rests, as an unbound
   joint does.

A `Mate` is deliberately NOT a `Joint`: `declared_joints` enumerates by
`isinstance(value, Joint)` and `clear_solved` finds a coordinate's joint
the same way, and a mate moves no body of the assembly that declares it.

An explicit joint path of the same direct moving child is a third mode:
`ones_mount = ones.axle.on(ones_seat, ones.turn)`. It applies only the
rest placement and reuses the original scalar Revolute or Prismatic,
without specialization, renaming, reordering or wiring. The handle reads
and binds the original child coordinate in every reference context;
it owns no assembly coordinate. The original joint's argument scope,
factories, limits and binding rules remain unchanged.

A mate is read off the class, never constructed by a project:
`declared_mates(cls)[name]` gives its `name`, its two ends `moving` and
`fixed` as the class body wrote them, and its `freedom`: a fresh joint
declaration, a `PathRef` to the original child joint, or `None` for a rigid mate.

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


def _is_rigid(value):
    """Whether `value` is a RIGID mate: one that states no freedom, and
    so owns no coordinate (hold-by-mate)."""
    return _is_mate(value) and value.freedom is None


def _reuses_joint(value):
    """A written child-joint reference, not a newly installed freedom."""
    from .couplings import PathRef
    return _is_mate(value) and isinstance(value.freedom, PathRef)


def _owns_no_coordinate(written):
    """The one refusal of a rigid mate named where a coordinate is named:
    a relation's end, a term of a derived coordinate, a wiring source, a
    path from above, or an assignment on an instance (hold-by-mate,
    design decision 4)."""
    return (f"'{written}' is a rigid mate: it states no freedom and owns "
            f"no coordinate. It holds its child where two frames meet and "
            f"gives nothing to drive, bind or read as a value, so it is not "
            f"an end of a relation, a term of a derived coordinate or a "
            f"wiring source. A mate owns a coordinate when it states a "
            f"freedom: ...on(<fixed>, Revolute(...)) or "
            f"...on(<fixed>, Prismatic(...)).")


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
        """The reference as the class body wrote it,
        `'<child>.<frame>'`: `'forearm.hinge'` for the frame `hinge` of
        the child `forearm`."""
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
    fresh freedom -- the coordinate it owns on the assembly: rotational for a
    `Revolute` freedom, translational for a `Prismatic` one, in the
    freedom's unit. With the freedom left out, `moving.on(fixed)`, it is
    a RIGID mate, which holds the child where the two frames meet and
    owns no coordinate. An explicit existing-child joint path as freedom,
    `moving.on(fixed, child.turn)`, instead gives a handle to that same
    scalar Revolute or Prismatic. It owns no assembly coordinate and
    changes none of the original joint's scope, order or binding rules.

    A mate is read OFF THE CLASS, as `declared_mates(cls)[name]` reports
    it; reading one that states a freedom as an attribute of an instance
    gives its coordinate instead (below), and reading a rigid one gives
    the mate itself. A project never constructs one. Its reads:

    - `name`: the attribute the mate is assigned to; for a mate with a
      fresh freedom it is also the name of its coordinate on the assembly
      and of the joint it gives the moving child. An existing-joint handle
      preserves the referenced joint's own name.
    - `moving`: the moving end, a frame reference whose `written` is
      `'<child>.<frame>'` as the class body writes it.
    - `fixed`: the fixed end as the class body writes it -- for a frame
      of another child, a frame reference whose `written` is
      `'<child>.<frame>'`; for a frame of the assembly itself, written by
      its bare name, that `Frame` declaration, whose `name` is its
      attribute. `isinstance(mate.fixed, Frame)` tells the two apart.
    - `freedom`: the `Revolute` or `Prismatic` written in the statement,
      the explicit joint path for an existing-joint handle, or `None` for
      a rigid mate, which states none. A fresh freedom's `axis` is `None` when no axis is stated, which only a
      `Revolute` freedom may do, the three numbers as written, not
      normalized, when numbers are stated, and the function itself, the
      same object, when a function of the assembly is stated.
      `anchor_written` says whether `at` was written: when true, `at` is
      the three numbers as written, in the moving child's own frame,
      `(0, 0, 0)` meaning the child's origin; when false, `at` reads the
      default `(0, 0, 0)` and is NOT the mate's anchor, which is then the
      moving frame's origin. `range` is as written -- a pair, or the
      function itself -- or `None`; `unit` as written, else `'deg'` for a
      `Revolute` and `'mm'` for a `Prismatic`. Reading any of them calls
      no function.

    When `freedom.axis` is not a function, the line the mate turns its
    child about, or slides it along, follows from these reads and the
    moving child's resolved frames
    (`machinome.node.frames.resolved_frames`) alone: `freedom.axis` when
    it is not `None`, else the moving frame's resolved `z`; through `freedom.at` when `anchor_written` is true,
    else through the moving frame's resolved `at`. When it is a
    function, the axis on a built machine is what the function returned
    for that machine's assembly, and no documented read reports it in
    this version; nor does one report a range a function returned.

    A data descriptor, like a joint, so reading it on an instance yields
    the bound port slot and assigning to it binds; a `Coordinate`, so
    `drives` and the arithmetic of a derived coordinate treat it as one.
    A fresh moving mate owns its port as `coordinate` and `coordinates`, which is what
    makes `declared_ports` report it with no change there and a relation
    end resolve it. An existing-joint handle reads and binds the original
    child's coordinate instead; its `coordinate` is `None` and
    `coordinates` empty. A rigid mate owns none -- `coordinate` is `None` and
    `coordinates` empty, so `declared_ports` reports nothing for it --
    and assigning to it on an instance, or naming it as a relation's
    end, a term, a wiring source or by path, is refused naming it.

    A fresh moving mate may name its generated child joint as a Bound read,
    a constrain(range=...) target or an explicit control coordinate.
    Bounds in its freedom read the declaring assembly; its axis and
    anchor keep the moving child's own rest frame. Ordinary relations
    and author bindings keep the mate's assembly coordinate.
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
        if freedom is None or _reuses_joint(self):
            # A rigid mate owns no coordinate: `declared_ports` then
            # reports nothing for it (hold-by-mate, design decision 4).
            self.coordinate = None
            self.coordinates = {}
        else:
            unit = getattr(freedom, 'unit', None) or 'deg'
            self.coordinate = _coordinate_kind(freedom)(unit=unit)
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
        if self.coordinate is None:
            return
        self.coordinate.name = name
        self.coordinate.owner = owner
        self.coordinates = {name: self.coordinate}

    def __get__(self, instance, owner=None):
        if instance is not None and _reuses_joint(self):
            return self.freedom.resolve(instance).slot
        if instance is None or self.coordinate is None:
            return self
        return self.coordinate.__get__(instance)

    def __set__(self, instance, value):
        if _reuses_joint(self):
            end = self.freedom.resolve(instance)
            end.declared.__set__(end.node, value)
            return
        if self.coordinate is None:
            raise AttributeError(
                f"cannot bind {type(instance).__name__}.{self._name}: "
                + _owns_no_coordinate(self._name))
        bind(self.coordinate.__get__(instance), value)

    def constrain(self, *, range):
        from .couplings import coordinate_ref
        return coordinate_ref(self).constrain(range=range)

    def described(self):
        fixed = (self.fixed.written if isinstance(self.fixed, FrameRef)
                 else getattr(self.fixed, 'name', None) or repr(self.fixed))
        moving = (self.moving.written if isinstance(self.moving, FrameRef)
                  else getattr(self.moving, 'name', None)
                  or repr(self.moving))
        if self.freedom is None:
            return f'{moving}.on({fixed})'
        return f'{moving}.on({fixed}, ...)'

    def __repr__(self):
        return f"<mate {self._name or ''}: {self.described()}>"


_MISSING = object()


def _coordinate_kind(freedom):
    """The port kind of a mate's coordinate: the freedom's own --
    `RotationalPort` for a `Revolute`, `TranslationalPort` for a
    `Prismatic` -- or `RotationalPort` for a freedom `_check_freedom`
    refuses when the class is created (the mate exists, unchecked, while
    the body still runs)."""
    from machinome.motion.joints import Prismatic, Revolute

    if isinstance(freedom, (Revolute, Prismatic)):
        return freedom.coordinate_kind
    return RotationalPort


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
        if mate.name is None and mate.freedom is None:
            raise TypeError(
                f"{_named(name, mate)} is never assigned. A mate is known "
                f"by its name: declared_mates reports it under that name, "
                f"and every refusal names it by its name, so a mate that "
                f"holds a part is named as one that frees it: write "
                f"<name> = {mate.described()}.")
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
        if mate.freedom is not None and not _reuses_joint(mate):
            _check_child_name(name, mate)
    for mate in own:
        _install(cls, name, mate)

    cls._own_mates = tuple(own)
    cls._declared_mates = tuple(inherited) + tuple(own)
    for mate in cls._declared_mates:
        if mate.joint is not None and not _reuses_joint(mate):
            mate.joint.check_bound_reads(cls)


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
    """The freedom a mate accepts in this version: none at all, the rigid
    mate (hold-by-mate), which has nothing to check here; or a fresh
    `Revolute` or `Prismatic` (slide-by-mate) whose stated `at`, if any, is three
    numbers; whose stated `axis`, if any, is three numbers with a
    direction or one function of the assembly; and whose range is a
    pair with assembly-scoped Bound reads or one function of the assembly
    (state-the-freedom-per-instance). Both kinds are checked by the same
    rules in the same order; a `Prismatic` states its axis, as it must
    anywhere, so only a `Revolute` freedom reaches here without one.

    A function is only accepted here: it is called, and its result
    checked by the same rules, when the assembly realizes the moving
    child (`call_freedom_functions`)."""
    from machinome.motion.joints import Prismatic, Revolute

    freedom = mate.freedom
    where = _named(name, mate)
    if _reuses_joint(mate):
        from .couplings import BroadcastRef
        ref = freedom
        if (isinstance(ref, BroadcastRef) or not isinstance(mate.moving, FrameRef)
                or ref.root is not mate.moving.root or len(ref.segments) != 1
                or not isinstance(ref.terminal, (Revolute, Prismatic))):
            raise TypeError(
                f'{where}: {ref.described()} must explicitly name an existing '
                'scalar Revolute or Prismatic of the same directly declared '
                'moving child; not another site, node or deeper path.')
        ref.check('end')
        return
    if freedom is None:
        # The rigid mate: nothing to check here (hold-by-mate).
        return
    if not isinstance(freedom, (Revolute, Prismatic)):
        raise TypeError(
            f"{where} has the freedom {type(freedom).__name__}, which is "
            f"neither a Revolute nor a Prismatic: a mate accepts a "
            f"Revolute or a Prismatic in this version, or no freedom at "
            f"all for a part that is held, and Orbit and Free are not "
            f"mate freedoms. Write Revolute(range=(lo, hi), unit='deg') "
            f"to turn the part about a line, Prismatic(axis=(x, y, z), "
            f"range=(lo, hi), unit='mm') to slide it along one, or "
            f"...on(<fixed>) to hold it.")
    slides = isinstance(freedom, Prismatic)
    if mate.freedom_in_body or freedom.owner is not None:
        declared = (f'on {freedom.owner.__name__}' if freedom.owner
                    is not None else 'in this class body')
        written = ('Prismatic(axis=(x, y, z), range=(lo, hi))' if slides
                   else 'Revolute(range=(lo, hi))')
        raise TypeError(
            f"{where}: its freedom is already declared {declared}. A "
            f"mate's freedom becomes a joint of the child it moves, so it "
            f"is written fresh in the statement: "
            f"...on(<fixed>, {written}).")
    if freedom.axis is not None and not _is_function(freedom.axis):
        _check_stated(where, 'axis', freedom.axis, slides=slides)
    if freedom.anchor_written:
        _check_stated(where, 'at', freedom.at, slides=slides)
    declared = freedom.range
    if declared is None or _is_function(declared):
        return
    reason = _range_reason(declared)
    if reason is not None:
        raise TypeError(
            f"{where}: its freedom's range {declared!r} {reason}. The "
            f"range of a mate's freedom is written in the assembly and "
            f"resolved on the child it moves, so it is admitted only as "
            f"numbers, None, or functions of the coordinate's own value.")


def _slides(freedom):
    """Whether a mate's freedom slides the child (a `Prismatic`) rather
    than turning it."""
    from machinome.motion.joints import Prismatic

    return isinstance(freedom, Prismatic)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_function(value):
    """Whether a freedom's argument is ONE FUNCTION of the assembly:
    callable, and neither a parameter token or formula (tested first,
    by `dimension`, as the stated-line rule orders it) nor a `Bound`."""
    from machinome.motion.joints import Bound

    return (callable(value) and not hasattr(value, 'dimension')
            and not isinstance(value, Bound))


def _range_reason(declared):
    """Why `declared` is not a range a mate's freedom takes as a pair --
    a `(lo, hi)` pair whose bounds are numbers, `None`, functions of the
    coordinate's own value or a `Bound` with assembly-scoped reads --
    or None when it is. The one wording of the rule, for a range written
    in the freedom and for one a function of the assembly returned."""
    from machinome.motion.joints import Bound

    if callable(declared):
        return ('is a callable of the node, which would be resolved '
                'against the moving child')
    if (isinstance(declared, (str, bytes))
            or not hasattr(declared, '__len__') or len(declared) != 2):
        return 'is not a plain (lo, hi) pair'
    for bound in declared:
        if bound is None or _is_number(bound):
            continue
        if isinstance(bound, Bound):
            continue
        if callable(bound) and not hasattr(bound, 'dimension'):
            continue
        return (f'has the bound {bound!r}, which is not a number, None or '
                f'a function of the coordinate itself')
    return None


def _stated_reason(value):
    """Why `value` is not three real numbers, or None when it is. The
    one wording of the stated-line rule, for a line written in the
    freedom and for an axis a function of the assembly returned."""
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
    return reason


def _has_no_length(axis):
    """Whether three numbers are shorter than the joint's own `1e-9`."""
    return math.sqrt(sum(component ** 2 for component in axis)) < _SNAP


def _check_stated(where, argument, value, slides=False):
    """A line a freedom states in numbers: three numbers, and an axis
    with a direction (state-the-mate-line, design decision 5).

    The installed joint resolves its arguments against the moving CHILD,
    and a parameter token resolves by NAME, so a token or formula
    written in the assembly would silently read the child's parameter of
    the same name. The values are numbers, so a zero-length axis --
    below the joint's own `1e-9` threshold -- is known here, where the
    refusal can name the mate, rather than at realization.

    A function `axis` never reaches here: it is one function of the
    assembly, called when the assembly realizes the moving child and its
    result checked by these same rules then (`call_freedom_functions`).
    A function `at` is refused here with its own reason: a stated anchor
    is three numbers in this version (state-the-freedom-per-instance,
    design decision 5).

    `slides` is true for a `Prismatic` freedom, whose messages speak of
    a line to slide along; a `Revolute` freedom's are worded as they
    were before a freedom could slide (slide-by-mate).
    """
    if argument == 'at' and _is_function(value):
        left_out = ("take the moving frame's origin" if slides
                    else "turn about the moving frame's origin")
        raise TypeError(
            f"{where}: its freedom's at {value!r} is a function, and a "
            f"stated anchor is three numbers in this version: at=(x, y, "
            f"z), in the moving child's own frame. A freedom's axis and "
            f"range may each be one function of the assembly that states "
            f"the mate, its at may not; leave at out to {left_out}.")
    reason = _stated_reason(value)
    if reason is not None:
        raise TypeError(
            f"{where}: its freedom's {argument} {value!r} {reason}. A line "
            f"a mate's freedom states is written in the assembly and read "
            f"in the moving child's frame, so it is three numbers: "
            f"{argument}=(x, y, z).")
    if argument == 'axis' and _has_no_length(value):
        advice = ('states no line to slide along. State the direction of '
                  'the line.' if slides else
                  "states no line to turn about. State the direction of "
                  "the line, or leave axis out to turn about the moving "
                  "frame's z.")
        raise TypeError(
            f"{where}: its freedom's axis {value!r} has zero length, and an "
            f"axis of zero length {advice}")


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
        if mate.freedom is None:
            raise TypeError(
                f"{where}: its moving end {moving.written} is a child "
                f"{owner} declares, and {name} inherits it. In this "
                f"version a mate is stated in the class that declares the "
                f"child it moves, a rigid mate included; state the mate in "
                f"{owner}, or redeclare '{child}' in {name}.")
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
    if mover is not None and mover.freedom is None and not joints:
        raise TypeError(
            f"{where}: its fixed end {fixed.written} is on '{child}', which "
            f"the rigid mate '{mover.name}' places within {name}. A mated "
            f"child is placed against the fixed child's REST placement, and "
            f"this version orders no mate before another, so "
            f"'{mate.moving.root._name}' would not be placed against where "
            f"'{mover.name}' puts '{child}'. Mate onto a frame of {name} "
            f"itself, or of a child no mate places; a part that holds its "
            f"own fasteners declares them in its own class.")
    if mover is not None or joints:
        # A child a rigid mate places moves only by its class's joints.
        moves = mover is not None and mover.freedom is not None
        because = (f"the mate '{mover.name}' moves it" if moves
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
    wiring that binds it (design decisions 5 and 6) -- or, for a rigid
    mate, nothing: the child keeps its declared class, it gets no
    wiring, and `mate.joint` stays `None` (hold-by-mate, ADR-152).

    The joint is of the freedom's kind -- a `Revolute` for a `Revolute`
    freedom, a `Prismatic` for a `Prismatic` one (slide-by-mate) --
    whose axis is the freedom's stated `axis`, else, for a `Revolute`
    only, the moving frame's `z` (a `Prismatic` always states its
    axis), and whose anchor is the freedom's written `at`, else the
    moving frame's `at` -- each passed straight
    through, the frame's exactly as DECLARED (a tuple, tokens, formulas
    or a callable of the node), the freedom's as the three numbers
    `_check_stated` admitted. Both are in the child's own rest frame, so
    the joint resolves against the child in `resolve_declared_joints`
    like any class-declared joint, with nothing carried or inverted
    (ADR-097). A left-out `at` is told from a written `(0, 0, 0)` by
    identity (`anchor_written`): the written one is the CHILD's origin,
    not the frame's. A `Prismatic`'s anchor moves nothing; it is carried
    as the joint's, as a class-declared slide's is.
    It goes on the child by `_specialize`, ADR-098's mechanism: the
    child keeps its name, identity and artifacts, and the joint -- new
    on the child -- takes the slot after every joint the child's class
    declares (ADR-093).

    A freedom whose `axis` or `range` is a FUNCTION of the assembly is
    passed through the same way, the function itself, and the joint is
    marked `_resolved_by_mate`: the child's own constructor skips it
    (`resolve_declared_joints`), and `ChildDeclaration.realize` resolves
    it instead, against the child, with what the function returned for
    the realized assembly in the function's place
    (`call_freedom_functions`, `resolve_freedom_functions`;
    state-the-freedom-per-instance). A freedom stating numbers or
    nothing installs exactly the joint it installed before, unmarked.

    The wiring hands the assembly's coordinate to that joint (ADR-088):
    one binder, one address, and relations see only the assembly's port.
    """
    from machinome.motion.joints import Prismatic, Revolute
    from machinome.node.declarative import _specialize

    freedom = mate.freedom
    if _reuses_joint(mate):
        # No specialization, mutation, slot or relay wiring is needed.
        mate.joint = freedom.terminal
        return
    if freedom is None:
        # The rigid mate installs nothing: the child keeps its declared
        # class and no wiring, and `mate.joint` stays None
        # (hold-by-mate, design decision 2).
        return
    frame = mate.moving.frame
    kind = Prismatic if _slides(freedom) else Revolute
    axis = freedom.axis
    if axis is None and kind is Revolute:
        axis = frame.z
    joint = kind(
        axis=axis,
        at=freedom.at if freedom.anchor_written else frame.at,
        range=freedom.range, unit=freedom.unit)
    joint.installed_by = mate
    if _is_function(freedom.axis) or _is_function(freedom.range):
        joint._resolved_by_mate = True
    declaration = mate.moving.root
    declaration.node_class = _specialize(declaration.node_class,
                                         {mate.name: joint})
    declaration.wiring[mate.name] = mate
    mate.joint = joint


##############################################
# Realization: a freedom that is a function of the assembly

def _freedom_functions(declaration):
    """The mates whose freedom states a function and whose moving child
    `declaration` declares: at most one, since a child is placed by one
    mate."""
    return [source for source in declaration.wiring.values()
            if _is_mate(source) and source.joint is not None
            and source.joint._resolved_by_mate]


def _function_refusal(assembly, mate, argument, detail):
    from machinome.parameters import ParameterError

    owner = type(assembly).__name__
    if argument == 'axis':
        rule = ("three real numbers with a direction, read in the moving "
                "child's own frame")
    else:
        rule = ("a (lo, hi) pair whose bounds are numbers, None, "
                "functions of the coordinate's own value or a Bound "
                "whose reads belong to the declaring assembly")
    return ParameterError(
        f"{owner}.{mate.name}: its freedom's {argument} function {detail}. "
        f"The function is called with the {owner} that states the mate, "
        f"as it builds '{mate.moving.root._name}', and what it returns is "
        f"taken as the {argument} written in numbers is: {rule}.")


def _result_reason(argument, result, slides=False):
    """Why a function's `result` is not what the numbers form of
    `argument` takes, or None: `_check_stated`'s and `_check_freedom`'s
    rules, worded once. `slides` as for `_check_stated`."""
    if _is_function(result):
        return ('is a function, not three numbers' if argument == 'axis'
                else 'is a function, not a (lo, hi) pair')
    if argument == 'range':
        return _range_reason(result)
    reason = _stated_reason(result)
    if reason is None and _has_no_length(result):
        reason = ('has zero length, and an axis of zero length states no '
                  'line to ' + ('slide along' if slides else 'turn about'))
    return reason


def call_freedom_functions(declaration, assembly):
    """Call each function a mate's freedom states for the child
    `declaration` declares, ONCE, with the realized `assembly` -- the
    node whose class body wrote it -- and check each result by the rules
    the numbers are checked by at class creation.

    Called by `ChildDeclaration.realize` BEFORE the child is
    constructed, in the state a site-declared joint's function sees
    (ADR-098): the assembly's parameters resolved, its `check()` run,
    its joints and frames resolved, every child it declares before this
    one realized, nothing rendered. A function that raises, or whose
    result is not what the numbers form takes, is refused here, naming
    the assembly's class, the mate and the argument, before the child's
    subtree is built.

    Returns `[(mate, {argument: result})]`, for
    `resolve_freedom_functions` once the child exists; empty for every
    declaration whose mate states no function.
    """
    called = []
    for mate in _freedom_functions(declaration):
        results = {}
        for argument in ('axis', 'range'):
            declared = getattr(mate.freedom, argument)
            if not _is_function(declared):
                continue
            try:
                result = declared(assembly)
            except Exception as failure:
                raise _function_refusal(
                    assembly, mate, argument,
                    f'raised {type(failure).__name__}: {failure} when '
                    f'called with this {type(assembly).__name__}') from None
            reason = _result_reason(argument, result,
                                    slides=_slides(mate.freedom))
            if reason is not None:
                raise _function_refusal(
                    assembly, mate, argument,
                    f'returned {result!r} for this '
                    f'{type(assembly).__name__}, which {reason}')
            results[argument] = result
            if argument == 'range':
                try:
                    mate.joint.check_bound_reads(type(assembly), result)
                except TypeError as failure:
                    raise _function_refusal(
                        assembly, mate, argument,
                        f'returned {result!r} with invalid reads: {failure}') from None
        called.append((mate, results))
    return called


def resolve_freedom_functions(child, called):
    """Resolve the joint each mate of `called` gives `child`, against
    the child, with what each function returned in the function's place,
    and cache it where every reader of a joint's arguments looks,
    `_joint_arguments[<mate>]`.

    The joint's own resolution does the rest, exactly as for the numbers
    form: the axis normalized and snapped, the range's bounds handled
    and a numeric range order-checked, and what the moving frame
    supplies -- its declared `z` or `at` -- still resolved against the
    child, the node whose class declared it."""
    import copy

    values = child.__dict__.get('_parameters', {})
    resolved = child.__dict__.setdefault('_joint_arguments', {})
    for mate, results in called:
        joint = copy.copy(mate.joint)
        for argument, result in results.items():
            setattr(joint, argument, result)
        resolved[mate.name] = joint.resolve(child, values)


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
    degrees and from the dominant DIAGONAL beyond it, where the
    antisymmetric part shrinks to nothing. Only the well-conditioned
    dominant component takes a square root; the others follow from
    `R_ij + R_ji = 2 (1 - cos) a_i a_j`, without amplifying diagonal
    cancellation residue. Orientation follows the antisymmetric part.
    Equal diagonal components retain equal magnitudes, so a half turn about
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
        dominant = math.sqrt(squares[largest])
        axis = [0.0] * 3
        axis[largest] = dominant
        for index in range(3):
            if index != largest:
                symmetric = rotation[largest][index] + rotation[index][largest]
                if squares[index] == squares[largest]:
                    # Preserve exact equal-component serialization, rather
                    # than introducing a last-bit difference by division.
                    axis[index] = math.copysign(dominant, symmetric)
                else:
                    axis[index] = symmetric / (2 * (1 - cosine) * dominant)
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
    that mark -- ADR-114's slot-mark rule -- so it never stacks. A rigid
    mate is placed here exactly as a mate with a freedom is: the
    placement never reads the freedom.
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
