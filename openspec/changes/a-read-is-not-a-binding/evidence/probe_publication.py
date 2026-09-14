# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Probe 1: where the false `DoublyBound` is raised, and on what state.

The fixture is `fixture.py`: a running root whose child assembly declares
a relation into its OWN leaf's joint, and whose own body declares a
relation READING that joint and driving another leaf's joint.

Run from the worktree root:

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \\
        openspec/changes/a-read-is-not-a-binding/evidence/probe_publication.py

Traced, in order: every `clear_solved` (with the slots the phase recorded
as its own and what it does to each), every `_step_relation` attempt
(with each end's value, binder and enumeration marker), and the state of
the four coordinates at each stage of `symbolic_document`.
"""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solid_node.core.serializer import symbolic_document      # noqa: E402
from solid_node.motion import couplings                       # noqa: E402
from solid_node.motion.ports import get_coordinate, run_owned  # noqa: E402
from solid_node.node import assembly as assembly_module       # noqa: E402

from fixture import Lock, LockBody                            # noqa: E402

WATCHED = (('plug.key', 'insert'), ('plug.p1', 'lift'), ('d1', 'lift'))

_stage = ['']


def slot_of(node, path, name):
    owner = node
    for part in path.split('.'):
        owner = getattr(owner, part)
    return get_coordinate(owner, name)


def marker(slot):
    return hex(id(slot._enum_marker)) if slot._enum_marker is not None else None


def bound_by(slot):
    return type(slot._bound_by).__name__ if slot._bound_by is not None else None


def state(node, label):
    print(f'-- {label}')
    for path, name in WATCHED:
        slot = slot_of(node, path, name)
        print(f'     {path}.{name}: value={slot._value!r} '
              f'binder={slot.binder!r} run_owned={run_owned(slot)} '
              f'enum={marker(slot)} _bound_by={bound_by(slot)}')


def describe(end):
    if end.slot is None:
        return f'{end.described()} = <driver, always bound>'
    return (f'{end.described()} value={end.slot._value!r} '
            f'binder={end.slot.binder!r} run_owned={run_owned(end.slot)} '
            f'enum={marker(end.slot)} _bound_by={bound_by(end.slot)} '
            f'bound={end.bound()}')


def install():
    step = couplings._step_relation
    clear = couplings.clear_solved
    assembly_clear = assembly_module.clear_solved

    def traced_step(record, claimed, bound):
        print(f'  [{_stage[0]}] attempt {record.described()}')
        for end in record.driver_ends:
            print(f'      driver {describe(end)}')
        for end in record.driven_ends:
            print(f'      driven {describe(end)}')
        try:
            changed = step(record, claimed, bound)
        except Exception as error:
            print(f'      -> RAISED {type(error).__name__}: {error}')
            raise
        print(f'      -> changed={changed} direction={record.direction!r}')
        for end in record.driven_ends:
            print(f'      after  {describe(end)}')
        return changed

    def traced_clear(node):
        recorded = node.__dict__.get('_solver_bound', ())
        names = [f'{getattr(slot.node, "name", slot.node)}.{slot.name}'
                 f'(value={slot._value!r}, run_owned={run_owned(slot)}, '
                 f'enum={marker(slot)})' for slot in recorded]
        print(f'  [{_stage[0]}] clear_solved({type(node).__name__}) '
              f'_solver_bound={names}')
        return clear(node)

    couplings._step_relation = traced_step
    couplings.clear_solved = traced_clear
    assembly_module.clear_solved = traced_clear
    return step, clear, assembly_clear


def restore(saved):
    step, clear, assembly_clear = saved
    couplings._step_relation = step
    couplings.clear_solved = clear
    assembly_module.clear_solved = assembly_clear


def run(label, cls):
    print(f'================ {label} ================')
    node = cls()
    saved = install()
    try:
        _stage[0] = 'numeric pose'
        node.set_state(push=1.0)
        state(node, 'after the numeric pose, before publication')
        _stage[0] = 'publication'
        with symbolic_document(node) as (declarations, instructions):
            state(node, 'inside the publication')
            print('     declarations:', sorted(declarations))
            _stage[0] = 're-render (the finally block)'
        state(node, 'after publication')
        print(f'{label}: PUBLISHED')
    except Exception as error:
        print(f'{label}: REFUSED {type(error).__name__}: {error}')
        traceback.print_exc(limit=8)
    finally:
        restore(saved)
    print()


if __name__ == '__main__':
    run('running root', Lock)
    run('untimed twin', LockBody)
