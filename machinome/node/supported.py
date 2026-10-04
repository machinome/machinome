# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The table of the node types the core supports.

One row per node type, keyed by the node type's name: the class names the
node root (`machinome.node`) resolves from it, the renderers it contributes
to `machinome snapshot`, and the CLI commands that cannot run without its
module. A node type's address and its extra are not stored, because they are
its name: the module `machinome.node.<key>`, installed by `machinome[<key>]`.

This is the one place the core names a node type by its technology. The node
root's export table, the CLI and the snapshot and `new` commands read it;
nothing else spells a node type's module. Importing it imports no node type:
`load` imports one when a reader asks.

The renderer column is provisional (OpenSpec change `openscad-out`, ADR-179):
viewers become providers behind a seam `machinome.viewer` in the phase's last
cycle, which removes the column. No contract version is checked on a
renderer, and nothing is discovered: a renderer is a row here.
"""

from dataclasses import dataclass
from importlib import import_module

from machinome.extras import ExtraUnavailable


@dataclass(frozen=True)
class NodeType:
    """One supported node type.

    `classes` are the names the node root resolves from its module;
    `renderers` the `(renderer name, 'module.Class')` pairs it contributes
    to `machinome snapshot` (provisional); `commands` the CLI commands that
    need its module.
    """

    classes: tuple
    renderers: tuple = ()
    commands: tuple = ()


NODE_TYPES = {
    'cadquery': NodeType(('CadQueryNode',)),
    'build123d': NodeType(('Build123dNode', 'Build123dSheetNode')),
    'step': NodeType(('StepNode',), commands=('import-step',)),
    'molejo': NodeType(('MolejoNode',)),
    'solid2': NodeType(('Solid2Node',)),
    'openscad': NodeType(('OpenScadNode',), renderers=(
        ('openscad', 'machinome.viewers.openscad.OpenScadRenderer'),)),
    'jscad': NodeType(('JScadNode',)),
    'stl': NodeType(('StlNode',)),
}

#: The renderer `machinome snapshot` uses when none is named.
DEFAULT_RENDERER = 'openscad'


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
        classes = ', '.join(NODE_TYPES[key].classes)
        raise ExtraUnavailable(key, f'the {key} node type ({classes})',
                               address) from None


def renderer(name):
    """An instance of the renderer a node type contributes as `name`.

    Its node type is loaded first, under `load`'s refusals, so an absent
    node type is refused before its renderer's module is imported. A name
    no row contributes raises `KeyError`.
    """
    for key, node_type in NODE_TYPES.items():
        for contributed, location in node_type.renderers:
            if contributed == name:
                load(key)
                module, _, attribute = location.rpartition('.')
                return getattr(import_module(module), attribute)()
    raise KeyError(name)


def needed_by(command):
    """The node type whose module CLI command `command` needs, or None."""
    for key, node_type in NODE_TYPES.items():
        if command in node_type.commands:
            return key
    return None
