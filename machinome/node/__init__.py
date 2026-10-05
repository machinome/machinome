# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The node package: a package path, refusals, and its submodules.

Every class, function and declaration a project imports from the node
package is imported from the module that defines it, at one address:
`from machinome.node.assembly import AssemblyNode`, `from
machinome.node.step import StepNode`, `from machinome.node.frames import
Frame`. This module exports nothing (OpenSpec change `root-cleanup`,
ADR-181). One address per name is what lets a node package be cut from the
core: cutting it moves a module, and never a second spelling of its names.

Three things are here, and nothing else.

The package path. Each node type is one module directly under this
package, named for it; the table of supported node types
(`machinome.node.supported`) names each one and the classes its module
defines, and this module names none of them itself. A node package cut
from the core installs its module here as a portion of this package's
path (`_namespace_portions`).

The refusals. Until `root-cleanup` this module resolved twenty-one names
a second time, lazily, from the modules that define them. Each of them is
now refused with `ImportError`, at `from machinome.node import <name>` and
at an attribute read alike, with a message naming the module that defines
it and the line to write. The node types' class names are read from the
table, so a row added for a new node type is refused naming its module
with no edit here; the core's own names are `_DEFINED_IN` below, a closed
record of the former exports that no new name ever joins. The lookup is
of the requested name in a mapping, and decides nothing but the words of
the error. Ports and the declared time base answer from
`machinome.motion.ports` (OpenSpec change `motion-package`), and `_MOVED`
refuses them naming it; the dissolved `machinome.node.adapters` package
refuses every spelling beneath it. Build parameters are imported from
`machinome.parameters`, and are a plain missing attribute here.

The submodules. `machinome.node.step`, read after importing only the
package, and `from machinome.node import supported` resolve the
submodule, imported on first read. One that refuses its absent kernel
raises that refusal unmodified; one whose kernel is installed and broken
raises its own import error, with the requested name spliced in.

Importing this package imports no backend, no node type's module, and not
`machinome.node.base`: a node type is reached by importing its module,
which imports what it needs and nothing else.
"""

__author__ = """Luis Fagundes"""
__email__ = 'lhfagundes@gmail.com'
__version__ = '0.4.0'

from importlib import import_module as _import_module
from importlib.util import find_spec as _find_spec

from machinome import _namespace_portions
from machinome.extras import ExtraUnavailable as _ExtraUnavailable

# A node package cut from the core installs its module here without this
# package's `__init__.py`; it is found as a portion of this package's path,
# and a second copy of the core never is (see `_namespace_portions`).
__path__ = _namespace_portions(__path__, __name__)

# The core's own names this package resolved until `root-cleanup`, each
# with the submodule that defines it. A closed record: no name joins it,
# because a new name is never a root export. The node types' class names
# are not here; they are the table of supported node types'.
_DEFINED_IN = {
    'AssemblyNode': 'assembly',
    'declared_children': 'declarative',
    'FusionNode': 'fusion',
    'SheetLeafNode': 'sheet_leaf',
    'FlexibleNode': 'flexible',
    'Marking': 'markings',
    'Wrapped': 'markings',
    'Flat': 'markings',
    'Svg': 'markings',
    'Frame': 'frames',
    'property_as_number': 'decorators',
    'StlRenderStart': 'base',
}

# Names, and the two submodules, that used to live here and now answer
# only from `machinome.motion.ports` -- the module that answers "what
# moves, and what drives what". No re-export, no alias, no deprecation
# shim: a project that has not migrated fails at its import line, and
# the message it gets names where the name went.
_MOVED = {
    'Port': 'machinome.motion.ports',
    'RotationalPort': 'machinome.motion.ports',
    'TranslationalPort': 'machinome.motion.ports',
    'SignalPort': 'machinome.motion.ports',
    'declared_ports': 'machinome.motion.ports',
    'Time': 'machinome.motion.ports',
    'ports': 'machinome.motion.ports',
    'timebase': 'machinome.motion.ports',
}

__all__ = []


def _defined_in(name):
    """The module that defines former root name `name`, or None.

    The core's names come from `_DEFINED_IN`; a node type's class names
    from the table of supported node types, read when a name is asked
    for, so this module spells none of them.
    """
    submodule = _DEFINED_IN.get(name)
    if submodule is not None:
        return f'{__name__}.{submodule}'
    if name.startswith('__') and name.endswith('__'):
        return None
    from .supported import NODE_TYPES
    key = {cls: key for key, node_type in NODE_TYPES.items()
           for cls in node_type.classes}.get(name)
    return None if key is None else f'{__name__}.{key}'


def _load(module_name, requested):
    """Import `.module_name`, blaming `requested` if it cannot be.

    A failed deferred import must not reach the caller as a missing
    attribute: `hasattr` and every other lookup that treats an accessor
    as a probe would turn a broken install into "no such name". The
    original error is re-raised -- same class, same `name`, same
    traceback -- with the requested name spliced into its message, so
    the report says both what is broken and what asked for it.

    An extra that is not installed is not a broken install. A leaf module
    whose kernel is an extra refuses its absence at import with
    `ExtraUnavailable`, whose message already names the node types and
    the line that installs the extra; it is raised unmodified, still an
    `ImportError`, so `from machinome.node import step` carries it to the
    import line and `hasattr` raises it.
    """
    try:
        return _import_module(f'.{module_name}', __name__)
    except _ExtraUnavailable:
        raise
    except ImportError as failure:
        blame = (f'{failure} (raised resolving {__name__}.{requested} '
                 f'from .{module_name})')
        # Both, deliberately: `ImportError.__str__` reports `msg` when it
        # is set and falls back to `args` otherwise, so setting only one
        # leaves the other stale for anything that reads it directly.
        failure.msg = blame
        failure.args = (blame, *failure.args[1:])
        raise


def _submodule(name):
    """The submodule called `name`, or None when there is no such file.

    Only an absent submodule may become an `AttributeError`; one that
    exists and fails to import is a broken install and reports itself.
    """
    if name.startswith('__') and name.endswith('__'):
        return None
    try:
        if _find_spec(f'{__name__}.{name}') is None:
            return None
    except (ImportError, ValueError):
        return None
    return _load(name, name)


def __getattr__(name):
    # ImportError, deliberately, not AttributeError, for both refusals
    # below: CPython's `from X import Y` catches an AttributeError raised
    # by module `__getattr__` and DISCARDS its message, substituting its
    # own generic "cannot import name" text -- verified against this
    # interpreter, not assumed. Only an exception that is not an
    # AttributeError survives `hasattr()`'s probe inside the import
    # machinery's fromlist handling and reaches the caller unmodified, so
    # this is the only way `from machinome.node import <name>` can carry a
    # message naming the module to import it from. The same choice
    # already governs a broken backend import (see `_load`): a name that
    # used to resolve and now cannot must not be reported as a plain
    # missing attribute.
    new_home = _MOVED.get(name)
    if new_home is not None:
        raise ImportError(
            f"module {__name__!r} has no attribute {name!r}: ports and "
            f"the declared time base moved to {new_home!r}. Write "
            f"`from {new_home} import {name}`. {__name__} answers what "
            f"has shape; machinome.motion answers what moves.")

    module = _defined_in(name)
    if module is not None:
        raise ImportError(
            f"module {__name__!r} has no attribute {name!r}: the root of "
            f"machinome.node exports nothing, and {name!r} is imported from "
            f"its module, {module!r}. Write `from {module} import {name}`.")

    # Importing a submodule binds it here as a side effect of the import
    # machinery; reading one that has not been imported yet imports it.
    submodule = _submodule(name)
    if submodule is None:
        raise AttributeError(
            f'module {__name__!r} has no attribute {name!r}')
    globals()[name] = submodule
    return submodule


def __dir__():
    return sorted(globals())
