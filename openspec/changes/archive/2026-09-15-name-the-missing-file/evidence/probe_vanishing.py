"""The one fixture in the suite that removes its own source file.

`tests/test_builder_reload_resilience.py:68-78` declares a `JScadNode`
whose `__init__` calls `super().__init__()` and then deletes the file.
This probe reproduces that shape and records the order of events, which
is what decides whether a construction-time check placed inside
`JScadNode.__init__` (before its own `super().__init__()`) would break
that test.
"""

import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
PROJECT = os.path.join(HERE, 'probe_project')
sys.path.insert(0, HERE)

SOURCE = os.path.join(PROJECT, 'vanishing.js')

with open(SOURCE, 'w') as handle:
    handle.write('return cube({size: 1});\n')

from probe_project import parts  # noqa: E402

print(f'before construction: exists = {os.path.exists(SOURCE)}')
node = parts.VanishingJscad()
print(f'constructed OK; after construction: exists = {os.path.exists(SOURCE)}')
try:
    print(f'node.mtime_ns: {node.mtime_ns}')
except Exception as error:
    print(f'node.mtime_ns: RAISED {type(error).__name__}: {error}')
