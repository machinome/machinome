# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The table of the node types the core supports.

One row per node type, keyed by the node type's name: the class names its
module defines for a project to import, and the CLI commands that cannot run
without its module. A node type's address and its extra are not stored,
because they are its name: the module `machinome.node.<key>`, installed by
`machinome[<key>]`.

This is the one place the core names a node type by its technology. The node
root's refusals (it exports nothing, and refuses each class name naming its
node type's module), `load`'s message, the CLI and the `new` and
`import-step` commands read it; nothing else spells a node type's module.
Importing it imports no node type: `load` imports one when a reader asks.
The table names no viewer: viewers are providers of the seam
`machinome.viewer` (OpenSpec change `viewer-seam`).
"""

from dataclasses import dataclass
from importlib import import_module

from machinome.extras import ExtraUnavailable


@dataclass(frozen=True)
class NodeType:
    """One supported node type.

    `classes` are the names its module defines for a project to import,
    which the node root refuses naming that module and `load` names in its
    refusal; `commands` the CLI commands that need its module.
    """

    classes: tuple
    commands: tuple = ()


NODE_TYPES = {
    'cadquery': NodeType(('CadQueryNode',)),
    'build123d': NodeType(('Build123dNode', 'Build123dSheetNode')),
    'step': NodeType(('StepNode',), commands=('import-step',)),
    'molejo': NodeType(('MolejoNode',)),
    'solid2': NodeType(('Solid2Node',)),
    'openscad': NodeType(('OpenScadNode',)),
    'jscad': NodeType(('JScadNode',)),
    'stl': NodeType(('StlNode',)),
    'freecad': NodeType(('FreeCADAssemblyNode', 'FreeCADJoint')),
}


def absent(key):
    """The refusal of node type `key` when no installed distribution ships
    its module: it names the node type, its classes, its module and the
    extra that installs it. `load` raises it, and so does the node root's
    last finder at the module's own import."""
    classes = ', '.join(NODE_TYPES[key].classes)
    return ExtraUnavailable(key, f'the {key} node type ({classes})',
                            f'machinome.node.{key}')


def load(key):
    """The module of node type `key`, imported.

    A module that refuses its absent kernel raises its own
    `machinome.extras.ExtraUnavailable`, which passes unmodified. A module
    that cannot be found at all -- a node package that is not installed --
    is refused the same way, naming the node type, its classes and the
    extra that installs it, so a caller answers both with one `except`.
    """
    address = f'machinome.node.{key}'
    try:
        return import_module(address)
    except ExtraUnavailable:
        raise
    except ModuleNotFoundError as error:
        if error.name != address:
            raise
        raise absent(key) from None


def needed_by(command):
    """The node type whose module CLI command `command` needs, or None."""
    for key, node_type in NODE_TYPES.items():
        if command in node_type.commands:
            return key
    return None
