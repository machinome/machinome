# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Probe 2: what a LIVE run does with the same declarations.

Three questions the proposal has to answer:

1. does `Sim` refuse the shape the publication refuses?
2. does the publication refuse it when a LIVE run owns the tree?
3. does a fresh (never posed) tree publish?

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \\
        openspec/changes/a-read-is-not-a-binding/evidence/probe_sim.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solid_node.core.serializer import symbolic_document      # noqa: E402
from solid_node.motion.ports import get_coordinate            # noqa: E402
from solid_node.simulation import Sim                         # noqa: E402

from fixture import Lock                                      # noqa: E402

WATCHED = (('plug.key', 'insert'), ('plug.p1', 'lift'), ('d1', 'lift'))


def show(node, label):
    parts = []
    for path, name in WATCHED:
        owner = node
        for piece in path.split('.'):
            owner = getattr(owner, piece)
        slot = get_coordinate(owner, name)
        parts.append(f'{path}.{name}={slot._value!r}')
    print(f'  {label}: ' + ', '.join(parts))


def publish(node, label):
    try:
        with symbolic_document(node) as (declarations, instructions):
            pass
        print(f'  {label}: PUBLISHED')
    except Exception as error:
        print(f'  {label}: REFUSED {type(error).__name__}: {error}')


print('1. a live run over the shape')
node = Lock()
sim = Sim(node, 0.05)
sim.move('push', to=2.0, duration=0.2)
sim.run(0.4)
show(node, 'after 0.4 s')

print('2. publication while that live run owns the tree')
publish(node, 'publication under a live run')
show(node, 'after the publication')
sim.run(0.1)
show(node, 'after one more tick')

print('3. a tree that was never posed')
publish(Lock(), 'publication of a fresh tree')

print('4. a tree posed by hand, then published (the reproduction)')
posed = Lock()
posed.set_state(push=1.0)
publish(posed, 'publication after a hand pose')
