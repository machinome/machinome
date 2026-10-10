"""Where in a declarative model the absent file first bites.

The modules are imported the way `solid build` imports them -- with the
project root on `sys.path`, as `assembly` and `parts` -- so this probe
observes exactly the classes the builder observes.

Run from the worktree root:
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/name-the-missing-file/evidence/probe_declarative.py
"""

import os
import sys

PROJECT = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'probe_project')
sys.path.insert(0, PROJECT)


def step(label, fn):
    try:
        value = fn()
    except Exception as error:
        print(f'{label}: RAISED {type(error).__name__}: {error}')
        return None
    print(f'{label}: OK -> {value!r}')
    return value


print('--- importing the declarative assembly module ---')
import assembly  # noqa: E402
import parts  # noqa: E402
from solid_node.node.declarative import ChildDeclaration  # noqa: E402

held = assembly.Rig.__dict__['part']
print(f'Rig.__dict__["part"] is a {type(held).__name__}; '
      f'is it a ChildDeclaration rather than a node? '
      f'{isinstance(held, ChildDeclaration)}')

print('\n--- instantiating the PARENT (realizes its children) ---')
rig = step('  Rig()', assembly.Rig)
if rig is not None:
    child = step('  rig.part', lambda: rig.part)
    step('  os.path.exists(rig.part.src)', lambda: os.path.exists(child.src))
    step('  rig.mtime_ns', lambda: rig.mtime_ns)

print('\n--- a declared source that IS present but is a directory ---')
for name in ('DirectoryStl', 'DirectoryStep'):
    klass = getattr(parts, name)
    print(f'  {name}:')
    node = step('    instantiation', klass)
    if node is None:
        continue
    step('    os.path.isdir(node.src)', lambda: os.path.isdir(node.src))
    step('    node.mtime_ns', lambda: node.mtime_ns)
