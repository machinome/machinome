# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Installed limits on existing descendant joints, without new coordinates.

Declarations belong to an ancestor; resolved contributions belong to one
instance. Neither changes the joint's declaration or placement. The running
and clocked compilers intersect their bounds; untimed enumeration judges
each available contribution after the ordinary relation fixpoint.
"""

import math

from .joints import Bound, Joint, JointRangeError, declared_joints, _is_number


def _scoped(ref, owner):
    """Recheck an inherited path against the class actually instantiated."""
    from .couplings import PathRef
    from machinome.node.declarative import ChildDeclaration, declared_children

    if not isinstance(ref, PathRef):
        return ref
    root = declared_children(owner).get(ref.root._name)
    if not isinstance(root, ChildDeclaration):
        raise TypeError(f'{owner.__name__}: constraint path {ref.written} '
                        'does not start at one declared child')
    found = PathRef(root, (), root)
    for segment in ref.segments:
        found = getattr(found, segment)
    return found


def _scalar_target(ref):
    from .couplings import BroadcastRef, PathRef

    if (not isinstance(ref, PathRef) or isinstance(ref, BroadcastRef)
            or not isinstance(ref.terminal, Joint)
            or len(ref.terminal.coordinates) != 1):
        raise TypeError(f'constraint target {ref.described()} must name an '
                        'explicit scalar descendant joint, not a node, '
                        'port, input, state, group or broadcast')
    ref.check('driver')
    return ref.terminal


class Constraint:
    """Metadata recorded by `path.joint.constrain(range=(lo, hi))`."""

    def __init__(self, target, span):
        self.target = target
        _scalar_target(target)
        if (not isinstance(span, (tuple, list)) or len(span) != 2
                or all(side is None for side in span)):
            raise TypeError(f'{self.described()}: range must be a (lo, hi) '
                            'pair with at least one bound')
        self.span = tuple(span)

    def described(self):
        return f'constraint on {self.target.described()}'

    def check_declared_on(self, owner, *, inherited=False):
        target = _scoped(self.target, owner) if inherited else self.target
        joint = _scalar_target(target)
        target.check_declared_on(owner, self)
        if (type(joint) is not type(self.target.terminal)
                or joint.unit != self.target.terminal.unit):
            raise TypeError(f'{owner.__name__}: {self.described()} reaches '
                            'an incompatible joint type or unit')
        for bound in self.span:
            if not isinstance(bound, Bound):
                continue
            seen = set()
            for written in bound.reads:
                ref = _scoped(written, owner) if inherited else written
                ref.check_declared_on(owner, self)
                if ref.key() == target.key():
                    raise TypeError(f'{self.described()}: reads its OWN '
                                    'coordinate; drop it from reads=')
                if ref.key() in seen:
                    raise TypeError(f'{self.described()}: reads '
                                    f'{ref.described()} twice')
                seen.add(ref.key())


class Contribution:
    """A resolved range and its scope, not a joint or binder.

    Shares Joint's bound-reader protocol with the existing compiler and
    untimed evaluator. Only the actual joint places or owns the coordinate.
    """

    def __init__(self, declaration, owner):
        from machinome.parameters import evaluate

        declaration.check_declared_on(type(owner), inherited=True)
        target = _scoped(declaration.target, type(owner))
        end = target.resolve(owner)
        self.node = end.node
        self.joint = declared_joints(type(self.node))[target.terminal.name]
        self.name, self.unit = self.joint.name, self.joint.unit
        self.owner, self.declaration = owner, declaration
        self._reads = {}
        values = owner.__dict__.get('_parameters', {})
        span = []
        for bound in declaration.span:
            if bound is None or callable(bound) or isinstance(bound, Bound):
                span.append(bound)
            else:
                value = evaluate(bound, values)
                if not _is_number(value) or not math.isfinite(value):
                    raise TypeError(f'{declaration.described()}: '
                                    f'{value!r} is not a finite numeric bound')
                span.append(value)
        self.span = tuple(span)

    def bound_reads(self, node, side):
        if side not in self._reads:
            bound = self.span[0 if side == 'lower' else 1]
            self._reads[side] = tuple(
                _scoped(ref, type(self.owner)).resolve(self.owner)
                for ref in bound.reads)
        return self._reads[side]

    def _bound_at(self, node, bound, value, side):
        return self.joint._bound_at(node, bound, value, side)

    def check(self):
        from .couplings import _bound_side
        from .ports import clocked_owned, get_coordinate, run_owned
        from machinome.node.qualified import instance_path

        # An omitted/detached target must not become an inert constraint.
        path = '.'.join((*instance_path(self.node, self.owner), self.name))
        slot = get_coordinate(self.node, self.name)
        if run_owned(slot) or clocked_owned(self.node, self.name):
            return
        value = slot._value
        if not _is_number(value):
            return
        reads = {}
        low = _bound_side(self.node, self, self.span[0], value, 'lower', reads)
        high = _bound_side(self.node, self, self.span[1], value, 'upper', reads)
        if (low is None or low <= value) and (high is None or value <= high):
            return
        named = ', '.join(f'{name}={read!r}' for name, read in reads.items())
        raise JointRangeError(
            f'{type(self.owner).__name__}: constraint on {path} evaluates '
            f'to ({low}, {high}) {self.unit or "units"}; {value!r} is '
            f'outside it; reads: {named or "none"}')


def resolve_constraints(owner):
    """Resolve once, after this instance's children have been realized."""
    records = tuple(Contribution(declared, owner)
                    for declared in type(owner)._declared_constraints)
    owner.__dict__['_ancestor_constraints'] = records
    for record in records:
        installed = record.node.__dict__.setdefault('_range_constraints', {})
        installed.setdefault(record.name, []).append(record)
        refuse_empty_intersection(record.node, record.joint)


def refuse_empty_intersection(node, joint):
    """Known numeric stops cannot enclose an empty permitted interval."""
    spans = [joint.arguments(node)[2]]
    spans.extend(record.span for record in
                 node.__dict__.get('_range_constraints', {}).get(joint.name, ()))
    lows = [span[0] for span in spans if span and _is_number(span[0])]
    highs = [span[1] for span in spans if span and _is_number(span[1])]
    if lows and highs and max(lows) > min(highs):
        raise JointRangeError(f'{type(node).__name__}.{joint.name}: constraint '
                              f'intersection ({max(lows)}, {min(highs)}) is empty')
