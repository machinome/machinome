"""When does a source-bound leaf notice that its declared file is absent?

Run from the worktree root:
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/name-the-missing-file/evidence/probe_when.py
"""

import os
import sys
import traceback

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)


def step(label, fn):
    try:
        value = fn()
    except Exception as error:
        print(f'{label}: RAISED {type(error).__name__}: {error}')
        return ('raised', error)
    print(f'{label}: OK -> {value!r}')
    return ('ok', value)


print('--- class definition (importing the module) ---')
outcome = step('import probe_project.parts', lambda: __import__(
    'probe_project.parts', fromlist=['*']) and 'module imported')

from probe_project import parts  # noqa: E402

for name in ('MissingStl', 'MissingStep', 'MissingJscad', 'MissingScad'):
    klass = getattr(parts, name)
    print(f'\n--- {name} ---')
    kind, value = step('  instantiation', klass)
    if kind != 'ok':
        continue
    node = value
    print(f'  node.src = {node.src}')
    print(f'  exists   = {os.path.exists(node.src)}')
    kind, value = step('  node.files', lambda: sorted(node.files))
    kind, value = step('  node.mtime_ns', lambda: node.mtime_ns)
    if kind == 'raised':
        print('  traceback of that failure:')
        traceback.print_exception(
            type(value), value, value.__traceback__, limit=6,
            file=sys.stdout)
