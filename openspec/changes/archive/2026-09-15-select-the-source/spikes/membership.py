"""Spike 2b: can block MEMBERSHIP be computed at `Sim` construction,
BEFORE the rest render, off the linked tree's resolved records?

`_units(root)` in program.py is the walk that reads
`node.__dict__['_relations']`. The question is whether those records
exist, with RESOLVED ends, before `Sim._bind_initial` runs its rest
render -- because spike 2 showed the rest render refuses a cycle with no
self-read (DoublyBound / UnreachedCoordinate) long before the compile is
reached.
"""

import sys

from solid_node.simulation.program import _units
from reduced import ShiftedCarry, NoSelfRead

for name, klass in (('self-read cycle', ShiftedCarry),
                    ('no self-read', NoSelfRead)):
    root = klass()
    print(f'--- {name}: freshly constructed, nothing rendered ---')
    try:
        units = list(_units(root))
    except Exception as error:
        print(f'  _units raised {type(error).__name__}: {error}')
        continue
    for assembly, path, records, formulas, wirings in units:
        for record in records:
            try:
                sources = [end.described() for end in record.driver_ends]
                targets = [end.described() for end in record.driven_ends]
                slots = [id(end.slot) for end in record.driven_ends]
            except Exception as error:
                print(f'  record {record}: ends unresolved '
                      f'({type(error).__name__}: {error})')
                continue
            print(f'  {".".join(path) or "<root>"}: {sources} -> {targets} '
                  f'driven slot ids {slots} direction={record.direction!r}')
