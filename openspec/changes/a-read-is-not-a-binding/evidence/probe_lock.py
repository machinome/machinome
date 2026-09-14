# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Probe 4: the originating project, on a COPY, in the shape it wanted.

The pin tumbler lock (`projects/Locks/Pin_tumbler_lock`) works the
refusal around by hoisting its five lift relations into the ROOT's body.
This probe runs a COPY of the project -- the project itself is never
written to -- with those five relations moved back into `Plug`, which is
the shape the wart reports, and publishes it the way `solid build` does:
the node is POSED first, then the document is produced.

    cp -a <project> <copy>            # then move the five relations back
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \\
        openspec/changes/a-read-is-not-a-binding/evidence/probe_lock.py \\
        <copy> [candidate-a]

`candidate-a` applies the patch `probe_candidates.py` measures.
"""

import sys

PROJECT = sys.argv[1]
CANDIDATE = len(sys.argv) > 2 and sys.argv[2] == 'candidate-a'
sys.path.insert(0, PROJECT)

from solid_node.core import serializer                        # noqa: E402
from solid_node.core.serializer import symbolic_document      # noqa: E402


def assemblies(node):
    found = [node]
    for child in getattr(node, 'children', ()) or ():
        if getattr(child, '_states', None) is not None:
            found.extend(assemblies(child))
    return found


if CANDIDATE:
    original = serializer._coordinate_publication

    class Restoring:
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

    serializer._coordinate_publication = lambda node: Restoring(
        original(node), [(target, target.__dict__.get('_solver_bound'))
                         for target in assemblies(node)])

from simulation.lock import PinTumblerLock                    # noqa: E402

node = PinTumblerLock()
node.set_state(insertion=-30.0, rotation=0.0)
print('posed')
try:
    with symbolic_document(node) as (declarations, instructions):
        print('  declarations:', sorted(declarations))
    print('PUBLISHED' + (' (candidate A)' if CANDIDATE else ''))
except Exception as error:
    print(f'REFUSED {type(error).__name__}: {error}')
