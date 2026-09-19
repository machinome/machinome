# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The set of project files a node's source really depends on.

A node used to track only the file it was defined in, which is wrong
whenever geometry comes from somewhere else: v8-engine's crankshaft.py
and cylinder_unit.py both take dimensions from kinematics.py, a module
that defines no node. Editing it changed the model and moved no tracked
mtime, so every artifact still reported up to date.

The closure below is deliberately an over-approximation. An extra file
in the set costs an unnecessary rebuild; a missing one serves a stale
model, which is the worse failure, so every ambiguity resolves toward
including the file.
"""

import ast
import errno
import os
import sys
from importlib.util import resolve_name

from machinome.source_generation import observation_key


# The framework is a library, not project source. It normally lives in
# site-packages, well outside any project, but when the framework tests
# itself the checkout IS the working directory -- so exclude it by path
# rather than relying on where it happens to be installed.
FRAMEWORK_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Per-file import lists, keyed on complete observable identity so an edited or
# atomically replaced file is re-parsed even when size and mtime are restored.
# A miss evicts the superseded entry, like the other per-source caches.
_import_cache = {}


class MissingSourceFile(FileNotFoundError):
    """A declared source file that is not there, raised at construction.

    A plain `FileNotFoundError(message)` renders correctly with
    `str(error)`, but assigning `.filename` on it afterwards (to let
    reload-repair watching, builder.py's `_on_reload_exception`, find the
    exact path to watch) breaks that rendering: `OSError.__str__` switches
    to "[Errno N] strerror: filename" the moment `.filename` is set at
    all, regardless of how it got there, and neither errno nor strerror
    were supplied, so the message becomes "[Errno None] None: '<path>'".
    Building the standard `(errno, strerror, filename)` triple through the
    constructor keeps `errno`, `strerror` and `filename` as the normal
    `OSError` attributes builder.py already reads, while `__str__` is
    overridden back to the one-sentence message alone.
    """
    def __init__(self, message, path):
        super().__init__(errno.ENOENT, message, path)

    def __str__(self):
        return self.strerror


def require_source_file(klass, attribute, declared, path):
    """Refuse a leaf whose declared source file is not there.

    Called by each source-bound adapter (`StlNode`, `StepNode`,
    `JScadNode`, `OpenScadNode`) immediately after it resolves its
    declared attribute into an absolute `path`, before `super().__init__`
    reads anything from it. `klass` is the constructing subclass;
    `attribute` and `declared` are the class attribute's name and the
    value it was declared with -- both needed because `path` alone
    cannot say which of a leaf's several possible source attributes to
    fix.

    Raises `FileNotFoundError` when `path` does not exist -- the same
    exception `AbstractBaseNode.mtime_ns` already raises for a source
    that vanishes after construction, so both failures read as one
    family. Raises `ValueError` when `path` exists but is not a regular
    file, matching the other admission refusals these adapters already
    raise for a missing declaration. Returns `None` when `path` is a
    file, so a caller can call this and move on.
    """
    if os.path.isfile(path):
        return None

    module = sys.modules[klass.__module__]
    wrapper = os.path.realpath(module.__file__)
    where = (f'{klass.__name__} declares {attribute} = {declared!r}, '
             f'resolved against {wrapper}, but {path} ')

    if os.path.exists(path):
        error = ValueError(where + 'is not a file.')
        # Assigned after construction, not passed to the constructor:
        # ValueError.__str__ reads only .args, so this is inert for the
        # message and only gives reload-repair watching (builder.py's
        # _on_reload_exception) the exact foreign path this refusal names.
        error.filename = path
        raise error

    raise MissingSourceFile(
        where + 'does not exist. Create or fetch the file, or correct '
        'the declaration.', path)


def source_closure(src):
    """Every project file the node defined in `src` depends on.

    Returns `src` itself together with the project-local modules it
    imports, transitively. The spelling of `src` is preserved: callers
    compare it against node.src.
    """
    # Local import avoids the loader -> node.base -> sources import cycle.
    from machinome.core.loader import project_root
    root = project_root(src)
    start = os.path.realpath(src)

    found = {start}
    pending = [start]
    while pending:
        for path in _project_imports(pending.pop(), root):
            if path not in found:
                found.add(path)
                pending.append(path)

    found.discard(start)
    return {src} | found


def _project_imports(path, root):
    try:
        key = observation_key(path)
    except OSError:
        key = (os.path.realpath(path), None)
    cached = _import_cache.get(key)
    if cached is None:
        for stale in [k for k in _import_cache if k[0] == path]:
            del _import_cache[stale]
        cached = _import_cache[key] = _parse_project_imports(path, root)
    return cached


def _parse_project_imports(path, root):
    if not path.endswith('.py'):
        # A JScadNode's source file is its .js; nothing to parse.
        return frozenset()

    try:
        with open(path, 'rb') as fh:
            tree = ast.parse(fh.read(), filename=path)
    except (OSError, SyntaxError):
        # A file the builder is about to fail on anyway. Tracking
        # nothing extra here leaves today's behaviour untouched.
        return frozenset()

    package = _package_of(path)

    names = set()
    for statement in ast.walk(tree):
        if isinstance(statement, ast.Import):
            names.update(alias.name for alias in statement.names)
        elif isinstance(statement, ast.ImportFrom):
            names.update(_import_from_targets(statement, package))

    return frozenset(
        found for found in (_project_file(name, root) for name in names)
        if found is not None
    )


# The package of every loaded module's file, keyed on the module set it
# was built from -- the same shape as _import_cache above, and for the
# same reason: what is cached is a view of something mutable, so the key
# is what makes a stale view unusable rather than invisible.
#
# The answer _package_of gives is a property of neither the number of
# files a project has nor the number of modules the interpreter happens
# to have imported, but asking used to cost the product of the two:
# every call rescanned sys.modules and realpath'd each module's
# __file__. On Metamaquina2, 135 calls over ~1800 modules spent 341 169
# realpath calls and 3.46 million lstat syscalls, and load_node took
# 15.3 s against 2.7 s indexed.
#
# The stamp is the exact set of module names rather than
# len(sys.modules), which cannot tell a module removed and another
# imported from nothing having happened -- and the loader does remove
# them, evicting a name that belongs to a different project. A package
# answered from a superseded module set would change which files a node
# tracks, the one failure ADR-006's mtime caching cannot survive: it
# makes a stale artifact report itself current. Taking the stamp costs
# ~30 us a call against the 10.6 s of syscalls it removes.
_package_index = {}


def _package_of(path):
    """The package a file was imported as, needed to resolve its
    relative imports. Taken from the interpreter, which has already
    done the resolution correctly."""
    return _loaded_as(path)[0]


def _loaded_as(path):
    """The (package, module name) a real path was imported as, or
    (None, None) if no loaded module came from it."""
    stamp = frozenset(sys.modules)
    index = _package_index.get(stamp)
    if index is None:
        _package_index.clear()
        index = _package_index[stamp] = _index_loaded_modules()
    return index.get(path, (None, None))


def _index_loaded_modules():
    index = {}
    for name, module in list(sys.modules.items()):
        filename = getattr(module, '__file__', None)
        if not filename:
            continue
        # setdefault, never assignment. Two modules can resolve to one
        # real path, and the scan this replaces returned the first one
        # sys.modules offered; assigning would silently hand a file to
        # the last importer instead.
        index.setdefault(os.path.realpath(filename),
                         (getattr(module, '__package__', None) or None, name))
    return index


def source_scope(src, klass):
    """What `klass`, defined in `src`, can see of its own file: the
    entry the content-verified digest scopes that file by.

    A node's own source may define other node classes. Those are not part
    of what this node's geometry depends on -- unless the rest of the file
    refers to them, which the digest checks -- so the scope names the one
    class this node is, and the digest keeps everything else in the file
    but its siblings' bodies. A source that is not Python has no classes
    to scope by and is digested whole.
    """
    if not src.endswith('.py'):
        return {}
    return {os.path.realpath(src): frozenset({klass.__name__})}


def node_classes_in(path):
    """The node classes the module at real path `path` defines at its
    top level, by name -- or None when the interpreter cannot say.

    Answered from the imported module, not from the source: which bases
    make a class a node is not reliably readable from the text, and the
    module is already imported by the time any node asks. None is
    'unknown', which the digest treats as 'remove nothing'.
    """
    # Local imports avoid the loader -> node.base -> sources cycle.
    from machinome.core.loader import _defined_classes
    from machinome.node.base import AbstractBaseNode
    _, name = _loaded_as(path)
    module = sys.modules.get(name) if name else None
    if module is None:
        return None
    return frozenset(
        klass_name
        for klass_name, _ in _defined_classes(path, module, AbstractBaseNode))


def _import_from_targets(statement, package):
    """Module names a `from ... import ...` statement can refer to."""
    module = statement.module or ''

    if statement.level:
        if package is None:
            return ()
        try:
            base = resolve_name('.' * statement.level + module, package)
        except (ImportError, ValueError):
            return ()
    else:
        base = module

    if not base:
        return ()

    # An imported name may itself be a submodule (`from pkg import mod`),
    # so offer both readings and let sys.modules decide.
    return [base] + [f'{base}.{alias.name}' for alias in statement.names]


def _project_file(name, root):
    """The project file a module name resolves to, or None if it is not
    one the node should track."""
    module = sys.modules.get(name)
    if module is None:
        return None

    filename = getattr(module, '__file__', None)
    if not filename:
        return None

    path = os.path.realpath(filename)

    # A package __init__ is, in the conventional layout, the root
    # assembly's own source: it imports every node in the project.
    # Python executes it to resolve any relative import, so following
    # it would put every node's source in every node's set and one edit
    # would invalidate everything. The cost is that a constant reached
    # through the package rather than through a named module is not
    # tracked -- that import is a child depending on its parent, the
    # one direction the tree's upward aggregation cannot express.
    if os.path.basename(path) == '__init__.py':
        return None

    if not path.startswith(root + os.sep):
        return None

    if path == FRAMEWORK_DIR or path.startswith(FRAMEWORK_DIR + os.sep):
        return None

    return path
