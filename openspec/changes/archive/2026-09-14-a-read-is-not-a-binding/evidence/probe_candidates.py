# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Probe 3: two candidate fixes, measured on the reproduction.

Neither is implementation: both are monkey patches applied inside this
probe, to measure whether the design each stands for answers the
failure.

A. The publication puts back what its walk replaced -- including each
   assembly's record of what its own previous phase bound
   (`_solver_bound`), which the publication enumeration overwrites with
   its own (empty, because under a running root the delivery binds the
   coordinates outside the enumeration and every relation records as
   `run`).

C. The enumeration's own fixpoint (`run_deferred`) stamps `_bound_by`
   with the assembly whose relation it solved, so a coordinate it binds
   is as freshness-marked as one an assembly's own attempt bound.

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \\
        openspec/changes/a-read-is-not-a-binding/evidence/probe_candidates.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solid_node.core import serializer                        # noqa: E402
from solid_node.motion import couplings                       # noqa: E402
from solid_node.motion.ports import get_coordinate            # noqa: E402
from solid_node.node import assembly as assembly_module       # noqa: E402

from fixture import Lock, OpaqueLock                          # noqa: E402

WATCHED = (('plug.key', 'insert'), ('plug.p1', 'lift'), ('d1', 'lift'))


def assemblies(node):
    found = [node]
    for child in getattr(node, 'children', ()) or ():
        if getattr(child, '_states', None) is not None:
            found.extend(assemblies(child))
    return found


def show(node, label):
    parts = []
    for path, name in WATCHED:
        owner = node
        for piece in path.split('.'):
            owner = getattr(owner, piece)
        slot = get_coordinate(owner, name)
        parts.append(f'{path}.{name}={slot._value!r}')
    print(f'    {label}: ' + ', '.join(parts))


def publish(node, label):
    try:
        with serializer.symbolic_document(node) as (declarations, _i):
            pass
        print(f'    {label}: PUBLISHED')
        return True
    except Exception as error:
        print(f'    {label}: REFUSED {type(error).__name__}: {error}')
        return False


def posed(cls=Lock):
    node = cls()
    node.set_state(push=1.0)
    return node


# ---------------------------------------------------------------- A

def candidate_a():
    original = serializer._coordinate_publication

    class Restoring:
        """The delivery, plus the assembly-level record `restore` omits."""

        def __init__(self, delivery, saved):
            self.delivery = delivery
            self.saved = saved

        @property
        def binder(self):
            return self.delivery.binder

        def deliver(self, *args, **kwargs):
            return self.delivery.deliver(*args, **kwargs)

        def restore(self):
            self.delivery.restore()
            for target, bound in self.saved:
                if bound is None:
                    target.__dict__.pop('_solver_bound', None)
                else:
                    target.__dict__['_solver_bound'] = bound

    def publication(node):
        return Restoring(original(node),
                         [(target, target.__dict__.get('_solver_bound'))
                          for target in assemblies(node)])

    serializer._coordinate_publication = publication
    try:
        node = posed()
        show(node, 'before')
        ok = publish(node, 'candidate A')
        show(node, 'after')
        opaque = posed(OpaqueLock)
        publish(opaque, 'candidate A, law that does not invert')
        return ok
    finally:
        serializer._coordinate_publication = original


# ---------------------------------------------------------------- C

def candidate_c():
    original = couplings.run_deferred

    def stamping(enumeration):
        changed = True
        while changed:
            changed = False
            for unit in enumeration.deferred:
                for record in unit.records:
                    before = len(unit.bound)
                    step = couplings._step_relation(record, unit.claimed,
                                                    unit.bound)
                    if step:
                        for slot in unit.bound[before:]:
                            slot._bound_by = unit.assembly
                    changed = step or changed
                for formula in unit.derived:
                    changed = couplings._step_derived(
                        unit.assembly, formula, unit.claimed,
                        unit.bound) or changed
                for wiring in unit.wirings:
                    changed = couplings._step_wiring(
                        wiring, unit.bound) or changed
        for unit in enumeration.deferred:
            couplings._refuse(unit.assembly, unit.records, unit.derived,
                              unit.wirings)

    couplings.run_deferred = stamping
    assembly_module.run_deferred = stamping
    try:
        node = posed()
        show(node, 'before')
        ok = publish(node, 'candidate C')
        show(node, 'after')
        return ok
    finally:
        couplings.run_deferred = original
        assembly_module.run_deferred = original


if __name__ == '__main__':
    print('baseline (no patch)')
    node = posed()
    show(node, 'before')
    publish(node, 'baseline')
    opaque = posed(OpaqueLock)
    show(opaque, 'before (law that does not invert)')
    publish(opaque, 'baseline, law that does not invert')
    print()
    print('candidate A: the publication puts back _solver_bound too')
    candidate_a()
    print()
    print('candidate C: run_deferred stamps _bound_by')
    candidate_c()
