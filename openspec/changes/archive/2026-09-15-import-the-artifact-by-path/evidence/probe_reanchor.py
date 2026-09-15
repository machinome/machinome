# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Feasibility of the proposed mechanism, against the installed solid2.

Two questions the design depends on:

1. Can a framework-emitted artifact import be told apart from a project's
   own `import_stl(...)` inside one assembled tree?
2. Can the path be re-anchored when a node writes its OWN `.scad`, without
   disturbing the tree the parent inlines?

Run:  PYTHONPATH=$PWD python .../evidence/probe_reanchor.py
"""

import copy

from solid2 import import_stl, scad_render, union


class ArtifactImport(import_stl):
    """A framework-emitted import of a build artifact.

    `import_stl.__init__` passes the OpenSCAD call name `'import'` to its
    base, so a subclass renders identically -- the marker is the Python
    type, never the SCAD text.
    """


def reanchor(node, prefix):
    """Point every framework artifact import at `prefix` + its path."""
    if isinstance(node, ArtifactImport):
        node._params['file'] = prefix + node._params['file']
    for child in node._children:
        reanchor(child, prefix)


def main():
    # A str subclass would NOT survive: import_stl normalises its argument
    # with `_Path(file).as_posix()`, which returns a plain str.
    class Marked(str):
        pass

    print('str subclass survives construction:',
          type(import_stl(Marked('sim/a.stl'))._params['file']).__name__
          != 'str')

    tree = union()([
        ArtifactImport('sim/a.stl'),
        import_stl('vendor/x.stl'),
    ])
    print('\n--- as the parent inlines it')
    print(scad_render(tree))

    own = copy.deepcopy(tree)
    reanchor(own, '../')
    print('--- re-anchored for a .scad one directory deeper')
    print(scad_render(own))
    print('--- the tree the parent inlines is untouched')
    print(scad_render(tree))


if __name__ == '__main__':
    main()
