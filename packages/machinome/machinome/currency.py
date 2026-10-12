# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Source-set metadata currency with content verification beneath it.

Artifact mtime equality remains part of currency (ADR-006), but one maximum
cannot reveal that an older contributing source changed. A compact fingerprint
of every tracked source's metadata therefore guards the settled path. Matching
the artifact stamp and recorded fingerprint requires only stat calls and one
small sidecar read; source contents and Python structure stay unopened.

It fails constantly for a reason that has nothing to do with the model. A
clone, a branch switch, a stash pop, a `git restore`, a copy, an agent or
a formatter rewriting a file with identical bytes -- all of them stamp a
source with the time it was written and none of them change what it says.
Measured on a 22-part CadQuery project, rewriting every source mtime with
zero content change turned a 6.05 s settled rebuild into 35.66 s of
re-deriving geometry that was already on disk and provably identical.

So when the stamp or fingerprint disagrees, the build asks the question those
metadata were standing in for: are the sources that produced this artifact the
sources that are here now? The digest below answers it over `node.files` -- the
exact set `mtime_ns` is the maximum of -- as a sorted sequence of
(project-relative path, sha256 of bytes). Project-RELATIVE because the
case this exists for is a project that moved: a fresh clone in a new
directory must recognise its own artifacts.

ADR-006 considered content hashing as a replacement for metadata checks and
rejected it on cost. Hashing remains confined to fingerprint or timestamp
misses, where a full render would otherwise run.

The direction of failure is the whole safety argument. A digest match is
a strictly stronger claim than the mtime equality it stands behind -- it
says the bytes are identical, not merely that a number matches -- so this
can only ever spare a rebuild that would have reproduced the same
artifact. Everything else says "not current": a mismatch, a missing
record, an unreadable source, a sidecar that was swept. A stale model
reported as fresh is the one failure the system cannot survive, and every
uncertain path here resolves toward rebuilding.

The digest's unit is not the file (ADR-006/060): ADR-071 scoped it to the
node's own file, removing the sibling node classes nothing in it names;
`source_digest` (digest-only-what-the-node-names, ADR-186) scopes it to the
node across its WHOLE tracked set -- every top-level definition, in every
tracked Python file, that nothing the node retains ever names is left out,
not only a sibling node class. Every uncertainty keeps more text (design.md
D2-D6): non-definition statements, star imports, decorated non-node
definitions, dunder definitions, a dynamic lookup's own file and its import
closure, a computed `getattr` on a module, a node class that is not a
top-level class statement, and a file a node tracks beyond its own source's
closure are all retained whole. A record says which rule its digest was
taken under (`_recorded_source`'s `rule`): version 2, version 3 and the
legacy digest-only form are ADR-071's rule (verified by
`previous_source_digest`), version 4 is this one; a previous-rule record is
verified once and re-recorded as version 4 (`previous_rule_carries`, D9), and
an older reader refuses a version 4 record it does not recognise and
rebuilds, the same safe rollback ADR-081 recorded.
"""

import ast
import hashlib
import json
import logging
import os
import tempfile
import time

from machinome._artifact import ArtifactChanged, ArtifactSnapshot
from machinome.source_generation import current_census


logger = logging.getLogger('currency')


#: Appended to the artifact's own name, so the record for `part.stl` is
#: `part.stl.sources`. It lives inside the build directory, is never
#: named by `viewer.json`, and changes nothing about what publication
#: means (ADR-030). The suffix deliberately keeps the artifact's own
#: extension in the middle of the name, so a `*.stl` glob -- the build
#: directory is full of them -- does not match a sidecar.
SIDECAR_SUFFIX = '.sources'


# Per-file digests, keyed on the complete observable identity returned by
# `_file_key` so even a same-size edit with restored mtime evicts stale bytes.
# Without
# it a tree's digests are quadratic: an internal node's file set is the
# union of its children's, so the root re-reads every source in the
# project once per node.
_file_digests = {}


def _file_key(path, stat=None, census=None):
    """Metadata identity used only for in-process source caches.

    Change time and file identity are required beside mtime and size: a
    same-size rewrite followed by an mtime restoration must evict the bytes
    cached for the previous file state.
    """
    if census is not None:
        observation = census[path]
        return (observation.path, *observation.metadata)
    stat = stat or os.stat(path)
    return (path, stat.st_dev, stat.st_ino, stat.st_size,
            stat.st_mtime_ns, stat.st_ctime_ns)


def _file_digest(path, census=None):
    if census is not None:
        return census.digest(path)
    stat = os.stat(path)
    key = _file_key(path, stat)
    cached = _file_digests.get(key)
    if cached is None:
        for stale in [k for k in _file_digests if k[0] == path]:
            del _file_digests[stale]
        with open(path, 'rb') as stream:
            cached = _file_digests[key] = hashlib.file_digest(
                stream, 'sha256').hexdigest()
    return cached


# Per-file structure for scoping, keyed like _file_digests: the file's
# lines, and for each top-level statement the node-class span it defines
# (if it is one) and every name and string the statement mentions. None
# when the file cannot be scoped -- unparseable, or the interpreter cannot
# say which of its classes are nodes -- so it is digested whole.
_analyses = {}

# Digests of retained text, keyed on the file key plus the classes kept.
# A tree asks for the same (file, scope) once per node that shares it, so
# without this an internal node's digest re-reads its children's files.
_scoped_digests = {}


def _analysis(path, census=None):
    stat = None if census is not None else os.stat(path)
    key = _file_key(path, stat, census)
    if key not in _analyses:
        for stale in [k for k in _analyses if k[0] == key[0]]:
            del _analyses[stale]
        if census is None:
            with open(path, 'rb') as stream:
                data = stream.read()
        else:
            data = census.read_bytes(path)
        _analyses[key] = _analyse(path, data)
    return _analyses[key]


def _analyse(path, data):
    # Local import avoids the node.base -> currency -> sources cycle.
    from machinome.node.sources import node_classes_in

    try:
        tree = ast.parse(data, filename=path)
    except (SyntaxError, ValueError):
        return None
    node_classes = node_classes_in(path)
    if not node_classes:
        return None

    statements = []
    for statement in tree.body:
        mentions = set()
        for inner in ast.walk(statement):
            if isinstance(inner, ast.Name):
                mentions.add(inner.id)
            elif (isinstance(inner, ast.Constant)
                    and isinstance(inner.value, str)):
                mentions.add(inner.value)
        span = None
        if (isinstance(statement, ast.ClassDef)
                and statement.name in node_classes):
            first = min([statement.lineno]
                        + [d.lineno for d in statement.decorator_list])
            span = (statement.name, first, statement.end_lineno)
        statements.append((span, frozenset(mentions)))

    # bytes.splitlines breaks where the tokenizer does -- \n, \r\n and a
    # lone \r -- so line numbers from the AST index these lines.
    return data.splitlines(keepends=True), statements


def _removed_spans(statements, keep):
    """The (name, first, last) spans of the node classes a node whose
    scope is `keep` does not see.

    Start from every top-level node class not in `keep`; then put back
    any of them the retained statements mention, by identifier or as a
    string, and repeat until the retained text refers to nothing removed.
    A base class, a helper that instantiates a sibling, `getattr(module,
    'Sibling')` -- all of them keep the sibling in. Only a class the rest
    of the file never names is left out.
    """
    removed = {span[0] for span, _ in statements
               if span is not None and span[0] not in keep}
    while removed:
        mentioned = set()
        for span, mentions in statements:
            if span is None or span[0] not in removed:
                mentioned |= mentions
        restored = removed & mentioned
        if not restored:
            break
        removed -= restored
    return [span for span, _ in statements
            if span is not None and span[0] in removed]


def _scoped_digest(path, keep, census=None):
    """The digest of `path` as a node whose scope there is `keep` sees it.

    Identical to `_file_digest` whenever nothing is removed, which is the
    single-class file, the file with no node classes, and every file this
    cannot analyse. That equality is what keeps a digest recorded before
    scoping existed valid under it.
    """
    stat = None if census is not None else os.stat(path)
    key = _file_key(path, stat, census) + (frozenset(keep),)
    cached = _scoped_digests.get(key)
    if cached is None:
        for stale in [k for k in _scoped_digests if k[0] == key[0]]:
            del _scoped_digests[stale]
        analysis = _analysis(path, census)
        removed = _removed_spans(analysis[1], keep) if analysis else []
        if not removed:
            cached = _file_digest(path, census)
        else:
            lines = analysis[0]
            skipped = set()
            for _, first, last in removed:
                skipped.update(range(first - 1, last))
            digest = hashlib.sha256()
            for number, line in enumerate(lines):
                if number not in skipped:
                    digest.update(line)
            cached = digest.hexdigest()
        _scoped_digests[key] = cached
    return cached


def previous_source_digest(files, root, scope=None, census=None):
    """ADR-071's digest: one digest over a node's tracked sources, scoped
    to the node's own file alone, or None if any source is unreadable.

    `files` is the node's own source together with its project-local
    import closure -- the set `node.mtime_ns` is the maximum over -- and
    `root` is the project root every path is expressed against. `scope`
    maps the real path of a source that defines node classes to the names
    of the classes this node depends on there; such a file contributes
    only the text those classes can see (see `_scoped_digest`), so a
    sibling class edited in the same file leaves this digest alone. A
    file with no scope entry contributes its bytes.

    This is ADR-071's rule verbatim, kept unchanged so a record it wrote
    can be verified exactly as it was written (digest-only-what-the-node-
    names, design.md D9): the current rule is `source_digest` below, and
    the reader tells which one a record was taken under
    (`_recorded_source`'s `rule`).

    None is not an error to report: it is the answer "cannot vouch for
    anything", and every caller treats it as not current. A source that
    vanished or cannot be read is a build about to fail on its own terms,
    and until it does, its artifact must not be certified.

    Most of what this reads is a handful of small text files. A leaf whose
    source IS its geometry (an `StlNode`'s mesh, a `JScadNode`'s script)
    is bigger, but it is still bounded by the render this replaces.
    """
    scope = scope or {}
    census = census or current_census()
    try:
        # Keyed on the relative path, so the same file reached under two
        # spellings -- the loader adds the reference it was given beside
        # the closure's own realpath -- is one entry and not two.
        entries = {}
        for path in files:
            real = census.realpath(path) if census is not None \
                else os.path.realpath(path)
            keep = scope.get(real)
            entries[os.path.relpath(real, root)] = (
                _file_digest(path, census) if keep is None
                else _scoped_digest(real, keep, census))
    except OSError as error:
        logger.debug('No source digest: %s', error)
        return None

    digest = hashlib.sha256()
    for relative, content in sorted(entries.items()):
        digest.update(os.fsencode(relative))
        digest.update(b'\0')
        digest.update(content.encode('ascii'))
        digest.update(b'\n')
    return digest.hexdigest()


def previous_rule_carries(files, root, scope, whole, census=None):
    """Whether every span `previous_source_digest` leaves out of a file is
    also left out by `source_digest` (design.md D9).

    A previous-rule record is safe to carry forward under the current
    rule only when this holds: the previous rule leaves out only sibling
    node classes, and when the current fixpoint also leaves each of them
    out, it never reaches a left-out sibling, so it retains identical
    text to the previous rule over identical sources -- which is exactly
    what the recorded digest already proved unchanged.

    `scope` empty answers True trivially: a node with no Python seed
    digests every file whole under both rules (D6), so neither ever
    leaves anything out.
    """
    census = census or current_census()
    if not scope:
        return True
    try:
        current = _retained(files, root, scope, whole or frozenset(), census)
        for path in files:
            if not path.endswith('.py'):
                continue
            real = census.realpath(path) if census is not None \
                else os.path.realpath(path)
            keep = scope.get(real)
            if keep is None:
                continue
            analysis = _analysis(path, census)
            if analysis is None:
                continue
            removed = _removed_spans(analysis[1], keep)
            if not removed:
                continue
            wanted = set(removed)
            old_removed = {index for index, (span, _)
                           in enumerate(analysis[1]) if span in wanted}
            if not old_removed <= current.get(real, frozenset()):
                return False
    except OSError:
        return False
    return True


##############################################
# digest-only-what-the-node-names: the digest covers what the node names
# across its tracked Python files, not only its own file (design.md).
#
# A top-level DEFINITION (a class, a function, a plain-name assignment, an
# import other than a star import) is left out of a node's digest only
# when nothing the node retains ever names it. What the node retains
# starts from its own class statement(s) (the seeds, from `scope`, as
# before) and every top-level statement that is NOT a definition -- it
# grows through every name a retained statement mentions, resolved as
# Python resolves it, until nothing more is named. Every uncertainty
# keeps more text: a star import, a decorated non-node definition, a
# dunder definition, and a statement sharing a line with another are
# never left out; a dynamic lookup (`vars`, `getattr(obj, computed)`, ...)
# keeps a whole file or module; a file this cannot analyse, a node class
# that is not a top-level class statement, and every file a node tracks
# beyond its own source's closure are retained whole.
#
# This is a property of the whole tracked set, not of one file at a time
# (ADR-071's unit), so the entry point is the fixpoint, `_retained`, run
# once per node and consulted while building every file's digest entry.

#: Calls that enumerate a module or namespace dynamically (D4): a file
#: whose retained text reaches one of these keeps its own file and every
#: file in that file's own import closure retained whole.
_DYNAMIC_CALLS = frozenset({
    'globals', 'locals', 'vars', 'dir', 'eval', 'exec', '__import__',
    'import_module', 'getmembers',
})

#: The four attribute-reflection builtins whose first argument, bound to a
#: tracked module with a non-literal second argument, keeps that module
#: whole (D4).
_ATTRIBUTE_CALLS = frozenset({'getattr', 'hasattr', 'setattr', 'delattr'})


def _is_dunder(name):
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


def _plain_names(target):
    """The plain names an assignment target binds, or None when any
    target is not a name, a tuple or a list of them (D1)."""
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        names = set()
        for element in target.elts:
            found = _plain_names(element)
            if found is None:
                return None
            names |= found
        return names
    return None


def _reach_mentions(statement):
    """(bare names, attribute chains, string constants, a dynamic-lookup
    flag, bare names passed as the first argument of a computed
    attribute-reflection call) found anywhere inside one statement.

    An attribute chain is a tuple of the root name followed by every
    attribute name in order (D1); a chain not rooted at a plain name
    contributes each of its attribute names as its own `(None, attr)`
    chain, matched by the catch-all (D3). `ast.walk` visits a chain's
    inner attributes too, which only ever adds more chains -- the safe
    direction every uncertainty here resolves toward.
    """
    bare = set()
    chains = set()
    strings = set()
    dynamic = False
    getattr_targets = set()

    for inner in ast.walk(statement):
        if isinstance(inner, ast.Name):
            bare.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            chain = []
            node = inner
            while isinstance(node, ast.Attribute):
                chain.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                chains.add((node.id,) + tuple(reversed(chain)))
            else:
                for attr in chain:
                    chains.add((None, attr))
            if inner.attr == '__dict__':
                dynamic = True
        elif isinstance(inner, ast.Constant) and isinstance(inner.value, str):
            strings.add(inner.value)
        elif isinstance(inner, ast.Call):
            func = inner.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in _DYNAMIC_CALLS:
                dynamic = True
            if name in _ATTRIBUTE_CALLS and len(inner.args) >= 2:
                first, second = inner.args[0], inner.args[1]
                if (isinstance(first, ast.Name)
                        and not (isinstance(second, ast.Constant)
                                 and isinstance(second.value, str))):
                    getattr_targets.add(first.id)

    return bare, frozenset(chains), strings, dynamic, getattr_targets


def _nested_import_names(statement):
    """Names an `Import`/`ImportFrom` NESTED inside `statement` binds --
    not `statement` itself when it is one at the top level, which is
    already `.names`. Needed so a top-level non-definition statement (an
    `if` or a `try`), always retained, counts the names its own nested
    imports bind even when nothing else in its text spells them
    (design.md's revision after apply evidence, I1): `try: from .defs
    import K` / `except ImportError: pass` binds `K` into the module
    whether or not the `except` arm also spells it, and a star alias
    binds nothing spelled, so it is skipped."""
    found = set()
    for inner in ast.walk(statement):
        if inner is statement:
            continue
        if isinstance(inner, ast.Import):
            for alias in inner.names:
                found.add(alias.asname or alias.name.split('.')[0])
        elif isinstance(inner, ast.ImportFrom):
            for alias in inner.names:
                if alias.name != '*':
                    found.add(alias.asname or alias.name)
    return found


class _Statement:
    """One top-level statement, as `_retained`'s fixpoint needs it."""

    __slots__ = ('first_line', 'end_line', 'removable', 'names',
                 'node_class', 'bare_names', 'attr_chains', 'strings',
                 'dynamic', 'getattr_targets', 'is_import', 'nested_imports')

    def __init__(self, first_line, end_line, removable, names, node_class,
                 bare_names, attr_chains, strings, dynamic, getattr_targets,
                 is_import, nested_imports):
        self.first_line = first_line
        self.end_line = end_line
        self.removable = removable
        self.names = names
        self.node_class = node_class
        self.bare_names = bare_names
        self.attr_chains = attr_chains
        self.strings = strings
        self.dynamic = dynamic
        self.getattr_targets = getattr_targets
        self.is_import = is_import
        self.nested_imports = nested_imports


class _ModuleReach:
    """One file's reach-analysis: its statements in source order, its
    lines (for `_retained_digest`), and the bindings `_retained`'s
    resolution needs (D3): local definitions by name, import bindings
    from every import in the file's text at any depth, star-import
    sources restricted to the top level (and a top-level `if`/`try`), and
    the names bound otherwise anywhere in the file -- the shadowing rule's
    input."""

    __slots__ = ('real', 'statements', 'lines', 'defs', 'import_bindings',
                 'star_sources', 'shadowed')

    def __init__(self, real, statements, lines, defs, import_bindings,
                 star_sources, shadowed):
        self.real = real
        self.statements = statements
        self.lines = lines
        self.defs = defs
        self.import_bindings = import_bindings
        self.star_sources = star_sources
        self.shadowed = shadowed


# Per-file reach analyses, keyed like `_analyses`: evicted whenever the
# same path reappears under a different observable identity.
_reach_analyses = {}


def _reach_analysis(path, census=None):
    stat = None if census is not None else os.stat(path)
    key = _file_key(path, stat, census)
    if key not in _reach_analyses:
        for stale in [k for k in _reach_analyses if k[0] == key[0]]:
            del _reach_analyses[stale]
        if census is None:
            with open(path, 'rb') as stream:
                data = stream.read()
        else:
            data = census.read_bytes(path)
        _reach_analyses[key] = _reach_analyse(path, data)
    return _reach_analyses[key]


def _reach_root(path):
    # Local import avoids the node.base -> currency -> sources cycle.
    from machinome.node.sources import _declaring_root
    return _declaring_root(path)


class _External:
    """Sentinel: the interpreter has loaded this name and can place it,
    but its file is definitely not trackable (outside the project root,
    inside the framework, or with no `__file__`) -- known, not
    ambiguous, and therefore resolved to nothing rather than the
    catch-all (design.md's revision after apply evidence, I3): `import
    numpy`, `from solid2 import cube`, `from machinome.node.frames
    import Frame` each name something real the project does not own, so
    nothing in the project can be what they bind."""

    def __repr__(self):
        return 'EXTERNAL'


#: The one instance; identity-compared, never equal to a path string.
_EXTERNAL = _External()


def _reach_import_target(name, root, path):
    """The tracked path a module `name` (imported by the file at real
    path `path`) resolves to; `_EXTERNAL` when the interpreter has
    loaded it but it is definitely not trackable; `None` when the
    interpreter cannot place it at all -- not loaded, or (the one
    remaining case the catch-all answers for) the importer's own
    package `__init__`, which is tracked nowhere (ADR-033's known gap)."""
    if not root or not name:
        return None
    import sys
    # Local import avoids the node.base -> currency -> sources cycle.
    from machinome.node.sources import FRAMEWORK_DIR
    module = sys.modules.get(name)
    if module is None:
        return None
    filename = getattr(module, '__file__', None)
    if not filename:
        return _EXTERNAL
    real = os.path.realpath(filename)
    if os.path.basename(real) == '__init__.py':
        package = os.path.dirname(real)
        if os.path.commonpath((package, path)) == package:
            return None
    if not real.startswith(root + os.sep):
        return _EXTERNAL
    if real == FRAMEWORK_DIR or real.startswith(FRAMEWORK_DIR + os.sep):
        return _EXTERNAL
    return real


def _reach_top_level_stars(tree, root, path, package):
    """Star-import sources D3 always consults: every star import at the
    top level, or nested only in a top-level `if` or `try` (not in a
    function, a method or a class body)."""
    from importlib.util import resolve_name
    found = []

    def resolve_base(statement):
        base = statement.module or ''
        if statement.level:
            if not package:
                return None
            try:
                base = resolve_name('.' * statement.level + base, package)
            except (ImportError, ValueError):
                return None
        return base or None

    def walk(statements):
        for statement in statements:
            if (isinstance(statement, ast.ImportFrom)
                    and any(alias.name == '*' for alias in statement.names)):
                base = resolve_base(statement)
                target = _reach_import_target(base, root, path) if base else None
                if isinstance(target, str):
                    found.append(target)
            elif isinstance(statement, ast.If):
                walk(statement.body)
                walk(statement.orelse)
            elif isinstance(statement, ast.Try):
                walk(statement.body)
                walk(statement.orelse)
                for handler in statement.handlers:
                    walk(handler.body)
                walk(statement.finalbody)

    walk(tree.body)
    return frozenset(found)


def _reach_shadowed(tree):
    """Names bound anywhere in the file by something other than an
    import of a tracked module: a parameter, an assignment or loop
    target, a `with ... as` or `except ... as` name (D3's shadowing
    rule). Import-bound names are added by `_reach_analyse` itself."""
    shadowed = set()
    for inner in ast.walk(tree):
        if isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Store):
            shadowed.add(inner.id)
        elif isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef,
                                ast.Lambda)):
            arguments = inner.args
            for argument in (arguments.posonlyargs + arguments.args
                             + arguments.kwonlyargs):
                shadowed.add(argument.arg)
            if arguments.vararg:
                shadowed.add(arguments.vararg.arg)
            if arguments.kwarg:
                shadowed.add(arguments.kwarg.arg)
        elif isinstance(inner, ast.ExceptHandler) and inner.name:
            shadowed.add(inner.name)
    return shadowed


def _reach_analyse(path, data):
    """Build one file's `_ModuleReach`, or None when it cannot be parsed
    or no loaded module came from it (D5) -- 'remove nothing', the same
    answer `_analyse` gives for an unparseable file."""
    # Local imports avoid the node.base -> currency -> sources cycle.
    from importlib.util import resolve_name
    from machinome.node.sources import _loaded_as, node_classes_in

    try:
        tree = ast.parse(data, filename=path)
    except (SyntaxError, ValueError):
        return None
    node_classes = node_classes_in(path)
    if node_classes is None:
        return None

    package, _ = _loaded_as(path)
    root = _reach_root(path)

    lines = data.splitlines(keepends=True)
    raw = []
    line_owners = {}
    for statement in tree.body:
        decorators = getattr(statement, 'decorator_list', [])
        first = min([statement.lineno] + [d.lineno for d in decorators])
        last = statement.end_lineno
        raw.append((statement, first, last))
        for number in range(first, last + 1):
            line_owners[number] = line_owners.get(number, 0) + 1

    statements = []
    defs = {}
    for index, (statement, first, last) in enumerate(raw):
        decorated = bool(getattr(statement, 'decorator_list', None))
        shares_line = any(line_owners[number] > 1
                          for number in range(first, last + 1))
        node_class = None
        is_import = False

        if isinstance(statement, ast.ClassDef):
            node_class = statement.name if statement.name in node_classes \
                else None
            names = {statement.name}
            removable = not decorated or statement.name in node_classes
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names = {statement.name}
            removable = not decorated
        elif isinstance(statement, ast.Assign):
            found = set()
            ok = True
            for target in statement.targets:
                plain = _plain_names(target)
                if plain is None:
                    ok = False
                    break
                found |= plain
            names = found if ok else set()
            removable = ok
        elif isinstance(statement, ast.AnnAssign):
            plain = _plain_names(statement.target)
            names = plain or set()
            removable = plain is not None
        elif isinstance(statement, ast.Import):
            is_import = True
            names = {alias.asname or alias.name.split('.')[0]
                     for alias in statement.names}
            removable = True
        elif isinstance(statement, ast.ImportFrom):
            is_import = True
            if any(alias.name == '*' for alias in statement.names):
                names = set()
                removable = False
            else:
                names = {alias.asname or alias.name
                         for alias in statement.names}
                removable = True
        else:
            names = set()
            removable = False

        if removable and (shares_line or any(_is_dunder(n) for n in names)):
            removable = False

        bare, chains, strings, dynamic, getattr_targets = \
            _reach_mentions(statement)
        nested_imports = frozenset(_nested_import_names(statement))

        statements.append(_Statement(
            first_line=first, end_line=last, removable=removable,
            names=frozenset(names), node_class=node_class,
            bare_names=frozenset(bare), attr_chains=chains,
            strings=frozenset(strings), dynamic=dynamic,
            getattr_targets=frozenset(getattr_targets), is_import=is_import,
            nested_imports=nested_imports))

        for name in names:
            defs.setdefault(name, []).append(index)

    import_bindings = {}
    shadowed = _reach_shadowed(tree)

    def bind(bound, binding):
        import_bindings.setdefault(bound, []).append(binding)

    def unfollowable(bound, target_name):
        bind(bound, ('name', None, target_name))
        shadowed.add(bound)

    for inner in ast.walk(tree):
        if isinstance(inner, ast.Import):
            for alias in inner.names:
                bound = alias.asname or alias.name.split('.')[0]
                target_name = alias.name if alias.asname \
                    else alias.name.split('.')[0]
                target = _reach_import_target(target_name, root, path)
                if isinstance(target, str):
                    bind(bound, ('module', target))
                elif target is _EXTERNAL:
                    bind(bound, ('external',))
                else:
                    bind(bound, ('module', None))
                    shadowed.add(bound)
        elif isinstance(inner, ast.ImportFrom):
            base = inner.module or ''
            if inner.level:
                if not package:
                    for alias in inner.names:
                        if alias.name != '*':
                            unfollowable(alias.asname or alias.name,
                                         alias.name)
                    continue
                try:
                    base = resolve_name('.' * inner.level + base, package)
                except (ImportError, ValueError):
                    for alias in inner.names:
                        if alias.name != '*':
                            unfollowable(alias.asname or alias.name,
                                         alias.name)
                    continue
            for alias in inner.names:
                if alias.name == '*':
                    continue
                bound = alias.asname or alias.name
                submodule = _reach_import_target(
                    f'{base}.{alias.name}' if base else alias.name, root, path)
                if isinstance(submodule, str):
                    bind(bound, ('module', submodule))
                    continue
                if submodule is _EXTERNAL:
                    bind(bound, ('external',))
                    continue
                base_path = _reach_import_target(base, root, path) \
                    if base else None
                if isinstance(base_path, str):
                    bind(bound, ('name', base_path, alias.name))
                elif base_path is _EXTERNAL:
                    bind(bound, ('external',))
                else:
                    unfollowable(bound, alias.name)

    star_sources = _reach_top_level_stars(tree, root, path, package)

    return _ModuleReach(
        real=path, statements=tuple(statements), lines=lines, defs=defs,
        import_bindings=import_bindings, star_sources=star_sources,
        shadowed=frozenset(shadowed))


def _global_defs(modules, name):
    """Every top-level definition of exactly `name` in every analysed
    tracked file: the catch-all (D3)."""
    found = set()
    for real, module in modules.items():
        for index in module.defs.get(name, ()):
            found.add((real, index))
    return found


def _resolve_bare(modules, module, name, seen=None):
    """Statements a bare name mentioned in `module` can refer to (D3): its
    own top-level definitions of that name (including the import
    statement that binds it, if any), transitively through `from X
    import name` bindings into tracked module X, and through every
    star-import source of `module`. An unfollowable binding -- a relative
    import whose package is unknown, or a name from an untracked module
    -- falls to the catch-all."""
    seen = seen if seen is not None else set()
    if (module.real, name) in seen:
        return set()
    seen.add((module.real, name))

    found = {(module.real, index) for index in module.defs.get(name, ())}
    catch_all = False
    for binding in module.import_bindings.get(name, ()):
        if binding[0] == 'external':
            # Known, not ambiguous: resolves to nothing beyond this
            # binding's own text (design.md's revision after apply
            # evidence, I3).
            continue
        if binding[0] != 'name':
            continue
        target_path = binding[1]
        target_module = modules.get(target_path) if target_path else None
        if target_module is None:
            catch_all = True
        else:
            found |= _resolve_bare(modules, target_module, binding[2], seen)
    for star_path in module.star_sources:
        star_module = modules.get(star_path)
        if star_module is not None:
            found |= _resolve_bare(modules, star_module, name, seen)
    if catch_all:
        found |= _global_defs(modules, name)
    return found


def _resolve_chain_into(modules, target_path, attrs):
    """Walk `attrs` from the tracked module at `target_path`, through
    submodule bindings, resolving the last unfollowed attribute name as
    a bare name there; every attribute name past that falls to the
    catch-all."""
    found = set()
    current = modules[target_path]
    for index, attr in enumerate(attrs):
        submodule = None
        for binding in current.import_bindings.get(attr, ()):
            if binding[0] == 'module' and binding[1] and binding[1] in modules:
                submodule = binding[1]
                break
        if submodule is not None and index < len(attrs) - 1:
            current = modules[submodule]
            continue
        found |= _resolve_bare(modules, current, attr)
        for rest in attrs[index + 1:]:
            found |= _global_defs(modules, rest)
        break
    return found


def _resolve_chain(modules, module, chain):
    """Statements an attribute chain mentioned in `module` can refer to
    (D3): into every tracked module a tracked import binds the chain's
    root to -- a root bound to two tracked modules (`if X: from . import
    a as m` / `else: from . import b as m`) resolves into both,
    design.md's revision after apply evidence I2 -- walking further
    through submodule bindings, then resolving the last unfollowed
    attribute name as a bare name there; every attribute name past that,
    and every attribute name of a chain not rooted at a tracked module
    binding (including one not rooted at a name at all, D1's
    `_reach_mentions`), falls to the catch-all. A root known to be bound
    to something definitely untrackable (`_EXTERNAL`, I3) and to no
    tracked module resolves to nothing at all -- not the catch-all,
    which is for an AMBIGUOUS root, not a known external one. A root also
    bound in the module otherwise (shadowed) adds the catch-all beside
    the module resolution rather than instead of it."""
    root, *attrs = chain
    if root is None:
        found = set()
        for attr in attrs:
            found |= _global_defs(modules, attr)
        return found

    bindings = module.import_bindings.get(root, ())
    target_paths = [binding[1] for binding in bindings
                    if binding[0] == 'module' and binding[1]
                    and binding[1] in modules]

    if not target_paths:
        if any(binding[0] == 'external' for binding in bindings):
            return set()
        found = set(_resolve_bare(modules, module, root))
        for attr in attrs:
            found |= _global_defs(modules, attr)
        return found

    found = set()
    for target_path in target_paths:
        found |= _resolve_chain_into(modules, target_path, attrs)

    if root in module.shadowed:
        for attr in attrs:
            found |= _global_defs(modules, attr)
    return found


def _module_bindings(module, name, modules):
    """Tracked modules a bare name in `module` is bound to (D4's
    module-`getattr` guard)."""
    targets = []
    for binding in module.import_bindings.get(name, ()):
        if binding[0] == 'module' and binding[1] and binding[1] in modules:
            targets.append(binding[1])
    return targets


def _whole_module_and_stars(real, modules, ensure_whole, seen=None):
    """D4's second rule: a computed module-`getattr` keeps `real` whole
    together with every tracked module it star-imports, transitively."""
    seen = seen if seen is not None else set()
    if real in seen:
        return
    seen.add(real)
    ensure_whole(real)
    module = modules.get(real)
    if module is None:
        return
    for star_path in module.star_sources:
        if star_path in modules:
            _whole_module_and_stars(star_path, modules, ensure_whole, seen)


_retained_cache = {}


def _retained(files, root, scope, whole, census):
    """The fixpoint of D1 and D3 over a node's tracked Python files
    (design.md D1-D6): for every file that is not retained whole, the
    indices of the top-level statements its own closure of mentions never
    names -- the statements `source_digest` leaves out of that file for
    this node. A file retained whole, or one this cannot analyse, has no
    entry: its absence from the result IS 'retain everything'.

    Cached on the file keys of every tracked Python file, the seeds
    (`scope`), and the caller's own whole-file set (`whole`, D6) -- the
    fixpoint it computes from those is otherwise deterministic, and a
    tree asks for the same (files, scope, whole) once per node that
    shares it. Eviction drops only an entry whose file keys differ from
    this call's -- a stale file, somewhere in the same path set -- never
    one that merely belongs to a different node's scope over the same,
    unchanged files (design.md's revision after apply evidence, I5): two
    siblings sharing a 42-file closure used to evict each other's cache
    entry on every call, because eviction keyed on the path set alone.
    """
    reals = []
    file_keys = []
    for path in files:
        if not path.endswith('.py'):
            continue
        real = census.realpath(path) if census is not None \
            else os.path.realpath(path)
        reals.append(real)
        file_keys.append((real, _file_key(path, None, census)))

    scope_key = frozenset(
        (census.realpath(path) if census is not None
         else os.path.realpath(path), frozenset(names))
        for path, names in scope.items())
    path_set = frozenset(reals)
    file_keys_frozen = frozenset(file_keys)
    key = (file_keys_frozen, scope_key, frozenset(whole))
    cached = _retained_cache.get(key)
    if cached is None:
        for stale in [k for k in _retained_cache
                      if frozenset(p for p, _ in k[0]) == path_set
                      and k[0] != file_keys_frozen]:
            del _retained_cache[stale]
        cached = _retained_cache[key] = _compute_retained(
            reals, file_keys_frozen, scope_key, whole, census)
    return cached


def _fixpoint_state(modules, retained=None, whole_set=None, queued_whole=None):
    """A mutable fixpoint in progress over `modules`, and the two
    closures that grow it (`ensure_whole`, `add`), sharing one `state`
    dict so a caller can hand the SAME closures a baseline to continue
    from (design.md's revision after apply evidence, I5) rather than
    restart it."""
    state = {
        'retained': retained if retained is not None else {},
        'whole_set': whole_set if whole_set is not None else set(),
        'queued_whole': queued_whole if queued_whole is not None else set(),
        'pending': [],
    }

    def ensure_whole(real):
        state['whole_set'].add(real)
        if real in state['queued_whole']:
            return
        state['queued_whole'].add(real)
        module = modules.get(real)
        if module is not None:
            for index in range(len(module.statements)):
                state['pending'].append((real, index, True))

    def add(real, index, count_import_binds):
        if real in state['whole_set']:
            return
        indices = state['retained'].setdefault(real, set())
        if index in indices:
            return
        indices.add(index)
        state['pending'].append((real, index, count_import_binds))

    return state, ensure_whole, add


def _drain(modules, state, ensure_whole, add):
    """Resolve every statement in `state['pending']` until nothing more
    is added -- the shared body of the fixpoint, run once to build the
    baseline (I5) and again, from it, once a node's own seeds are in."""
    pending = state['pending']
    while pending:
        real, index, count_import_binds = pending.pop()
        module = modules.get(real)
        if (module is None or real in state['whole_set']
                and real not in state['queued_whole']):
            continue
        statement = module.statements[index]

        if statement.dynamic:
            # Local import avoids the node.base -> currency -> sources cycle.
            from machinome.node.sources import source_closure
            try:
                closure = source_closure(real)
            except OSError:
                closure = (real,)
            for extra in closure:
                ensure_whole(os.path.realpath(extra))

        for name in statement.getattr_targets:
            for target in _module_bindings(module, name, modules):
                _whole_module_and_stars(target, modules, ensure_whole)

        targets = set()
        for name in statement.bare_names:
            targets |= _resolve_bare(modules, module, name)
        for chain in statement.attr_chains:
            targets |= _resolve_chain(modules, module, chain)
        for string in statement.strings:
            targets |= _global_defs(modules, string)
        if count_import_binds:
            # Retained whole, or always retained (never because one
            # specific name resolved to it): its own bound names --
            # including a nested import's, D3's F8 and I1 together --
            # are mentions too.
            names_to_resolve = (statement.names if statement.is_import
                                else frozenset()) | statement.nested_imports
            for name in names_to_resolve:
                targets |= _resolve_bare(modules, module, name)

        for target_real, target_index in targets:
            # Retained because this name was named: its own text joins the
            # digest, but an import's OTHER bound names are not mentions
            # merely because this one was (D3, the reviewer's F8).
            add(target_real, target_index, False)


#: Phase 1 of the fixpoint, shared by every node over the same (tracked
#: files, caller's whole-file set): the always-retained statements, the
#: whole files, and everything they reach. Keyed and evicted like
#: `_retained_cache` (design.md's revision after apply evidence, I5) --
#: the fixpoint is monotone, so continuing it per node from here, rather
#: than recomputing it, gives the same union.
_baseline_cache = {}


def _compute_baseline(reals, file_keys, whole, census):
    path_set = frozenset(reals)
    whole_key = frozenset(whole)
    key = (file_keys, whole_key)
    cached = _baseline_cache.get(key)
    if cached is not None:
        return cached
    for stale in [k for k in _baseline_cache
                  if frozenset(p for p, _ in k[0]) == path_set
                  and k[0] != file_keys]:
        del _baseline_cache[stale]

    modules = {}
    seed_whole = set(whole)
    for real in reals:
        analysis = _reach_analysis(real, census)
        if analysis is None:
            seed_whole.add(real)
        else:
            modules[real] = analysis

    state, ensure_whole, add = _fixpoint_state(modules)
    for real in seed_whole:
        ensure_whole(real)
    for real, module in modules.items():
        if real in state['whole_set']:
            continue
        for index, statement in enumerate(module.statements):
            if not statement.removable:
                add(real, index, True)
    _drain(modules, state, ensure_whole, add)

    result = (modules, state['retained'], state['whole_set'],
              state['queued_whole'])
    _baseline_cache[key] = result
    return result


def _compute_retained(reals, file_keys, scope, whole, census):
    modules, base_retained, base_whole_set, base_queued_whole = \
        _compute_baseline(reals, file_keys, whole, census)

    # Copies: this node's seeds must not grow the shared baseline other
    # nodes of the same files will read from `_baseline_cache` (I5).
    retained = {real: set(indices) for real, indices in base_retained.items()}
    whole_set = set(base_whole_set)
    queued_whole = set(base_queued_whole)
    state, ensure_whole, add = _fixpoint_state(
        modules, retained=retained, whole_set=whole_set,
        queued_whole=queued_whole)

    for real, names in scope:
        module = modules.get(real)
        if module is None:
            ensure_whole(real)
            continue
        found = set()
        for index, statement in enumerate(module.statements):
            if statement.node_class is not None and statement.node_class in names:
                add(real, index, False)
                found.add(statement.node_class)
        if found != set(names):
            ensure_whole(real)

    _drain(modules, state, ensure_whole, add)

    left_out = {}
    for real, module in modules.items():
        if real in state['whole_set']:
            continue
        kept = state['retained'].get(real, set())
        missing = frozenset(range(len(module.statements))) - kept
        if missing:
            left_out[real] = missing
    return left_out


# Digests of retained text under the current rule, keyed like
# `_scoped_digests`: the file key plus the frozenset of left-out
# statement indices.
_retained_digests = {}


def _retained_digest(path, left_out, census=None):
    """The digest of `path` with the statements at `left_out` removed
    (D7): identical to `_file_digest` whenever `left_out` is empty, which
    is what makes a node whose closure leaves nothing out digest byte for
    byte as it did before any of this existed."""
    if not left_out:
        return _file_digest(path, census)
    stat = None if census is not None else os.stat(path)
    key = _file_key(path, stat, census) + (frozenset(left_out),)
    cached = _retained_digests.get(key)
    if cached is None:
        for stale in [k for k in _retained_digests if k[0] == key[0]]:
            del _retained_digests[stale]
        analysis = _reach_analysis(path, census)
        lines = analysis.lines
        skipped = set()
        for index in left_out:
            statement = analysis.statements[index]
            skipped.update(range(statement.first_line - 1, statement.end_line))
        digest = hashlib.sha256()
        for number, line in enumerate(lines):
            if number not in skipped:
                digest.update(line)
        cached = _retained_digests[key] = digest.hexdigest()
    return cached


def source_digest(files, root, scope=None, census=None, whole=None):
    """One digest over a node's tracked sources under the current rule
    (design.md, digest-only-what-the-node-names): each tracked Python
    file contributes its *retained text*, the file with every top-level
    definition nothing the node retains ever names left out, across the
    node's whole tracked set -- not only its own file (ADR-071's unit).

    `files`, `root` and `scope` are as `previous_source_digest` takes
    them; `scope` empty or absent means no Python seed at all, so every
    file is retained whole and this is byte-identical to that function
    (D6, D7) -- the fast, common case needs no fixpoint at all. `whole`
    names files this node's own source closure does not reach but still
    tracks (an StlNode's or StepNode's wrapper module, a file a subclass
    added to `files`, a seedless child's own whole-file set unioned in by
    an internal node) and that are therefore always retained whole too
    (D6).

    None when any tracked source cannot be read, exactly as
    `previous_source_digest`.
    """
    scope = scope or {}
    census = census or current_census()
    try:
        entries = {}
        if not scope:
            for path in files:
                real = census.realpath(path) if census is not None \
                    else os.path.realpath(path)
                entries[os.path.relpath(real, root)] = _file_digest(
                    path, census)
        else:
            left_out = _retained(files, root, scope, whole or frozenset(),
                                 census)
            for path in files:
                real = census.realpath(path) if census is not None \
                    else os.path.realpath(path)
                removed = left_out.get(real)
                entries[os.path.relpath(real, root)] = (
                    _file_digest(path, census) if not removed
                    else _retained_digest(real, removed, census))
    except OSError as error:
        logger.debug('No source digest: %s', error)
        return None

    digest = hashlib.sha256()
    for relative, content in sorted(entries.items()):
        digest.update(os.fsencode(relative))
        digest.update(b'\0')
        digest.update(content.encode('ascii'))
        digest.update(b'\n')
    return digest.hexdigest()


def source_fingerprint(files, root, census=None):
    """Digest the observable metadata state of every tracked source.

    This is the settled-path guard, not proof that contents agree. It reads
    metadata only; a disagreement sends currency to `source_digest`, which is
    the content proof. Paths are project-relative for the same reason as the
    content digest, while filesystem identity deliberately makes a relocated
    project verify its contents once before settling again.
    """
    census = census or current_census()
    if census is not None:
        try:
            return census.fingerprint(files, root)
        except OSError as error:
            logger.debug('No source fingerprint: %s', error)
            return None
    try:
        entries = {}
        for path in files:
            real = os.path.realpath(path)
            stat = os.stat(real)
            entries[os.path.relpath(real, root)] = (
                stat.st_dev, stat.st_ino, stat.st_size,
                stat.st_mtime_ns, stat.st_ctime_ns)
    except OSError as error:
        logger.debug('No source fingerprint: %s', error)
        return None

    fingerprint = hashlib.sha256()
    for relative, metadata in sorted(entries.items()):
        fingerprint.update(os.fsencode(relative))
        fingerprint.update(b'\0')
        fingerprint.update(','.join(map(str, metadata)).encode('ascii'))
        fingerprint.update(b'\n')
    return fingerprint.hexdigest()


def sidecar(artifact):
    """The path of the record vouching for `artifact`."""
    return f'{artifact}{SIDECAR_SUFFIX}'


def describes(name):
    """The artifact a sidecar belongs to, or None if `name` is not one.

    Takes and returns whatever spelling it is given -- a bare name or a
    path -- so a caller can ask about either.

    The sweep needs this: a sidecar is not an artifact of its own and is
    never referenced by the published document, so it lives or dies with
    the file it describes rather than on its own merits.
    """
    if not name.endswith(SIDECAR_SUFFIX):
        return None
    return name[:-len(SIDECAR_SUFFIX)]


def _recorded_source(artifact):
    """Return `(digest, fingerprint, recipe, rule)` from a record.

    `rule` is `'previous'` for a version 2 or 3 record or the legacy
    digest-only form -- ADR-071's rule, the one those versions were ever
    written under -- `'current'` for a version 4 record (this change's
    rule, digest-only-what-the-node-names), and `None` for anything else,
    which certifies nothing and makes the first three `None` too (D8).
    """
    try:
        with open(sidecar(artifact)) as stream:
            content = stream.read().strip()
    except OSError:
        return None, None, None, None
    if not content:
        return None, None, None, None
    if not content.startswith('{'):
        return content, None, None, 'previous'
    try:
        record = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None, None, None, None
    version = record.get('version') if isinstance(record, dict) else None
    if (version not in (2, 3, 4)
            or not isinstance(record.get('digest'), str)
            or not isinstance(record.get('fingerprint'), str)):
        return None, None, None, None
    recipe = record.get('recipe') if version in (3, 4) else None
    if recipe is not None and not isinstance(recipe, str):
        return None, None, None, None
    rule = 'current' if version == 4 else 'previous'
    return record['digest'], record['fingerprint'], recipe, rule


def recorded_digest(artifact):
    """The content digest recorded for `artifact`, or None."""
    return _recorded_source(artifact)[0]


def recorded_fingerprint(artifact):
    """The source-set metadata fingerprint recorded for `artifact`, or None."""
    return _recorded_source(artifact)[1]


def recorded_recipe(artifact):
    """The private producer recipe recorded for `artifact`, or None."""
    return _recorded_source(artifact)[2]


def recorded_rule(artifact):
    """Which digest rule `artifact`'s record was taken under: `'previous'`
    (ADR-071, a version 2 or 3 record or the legacy digest-only form),
    `'current'` (digest-only-what-the-node-names, version 4), or `None`
    for a record that certifies nothing (D8)."""
    return _recorded_source(artifact)[3]


def recorded_transient(artifact):
    """Whether `artifact`'s writer published it as transient: for one
    process's own use, so every successful build removes it with its record
    (`record(..., transient=True)`). False for a record without the mark,
    an unreadable one and none at all."""
    try:
        with open(sidecar(artifact)) as stream:
            record = json.loads(stream.read())
    except (OSError, json.JSONDecodeError, TypeError):
        return False
    return isinstance(record, dict) and record.get('transient') is True


def drop(artifact):
    """Forget whatever was recorded for `artifact`."""
    try:
        os.remove(sidecar(artifact))
    except FileNotFoundError:
        pass
    except OSError as error:
        logger.debug('Could not drop the source record for %s: %s',
                     artifact, error)


def record(artifact, digest, fingerprint=None, recipe=None, transient=False):
    """Vouch for `artifact`, or for nothing when `digest` is None.

    A fingerprint produces the current version 4 record -- `digest` taken
    under this change's rule (digest-only-what-the-node-names, D8).
    Omitting it writes the legacy digest form deliberately retained for
    compatibility and migration tests; such a record cannot take the
    metadata-only path.

    `transient` marks the artifact as published for one process's own use
    (`"transient": true`, in the same version 4 record a fingerprint
    otherwise produces): every successful build removes it, with its
    record (`recorded_transient`). A transient record still carries the
    current rule's digest and reads back as `rule == 'current'`
    (design.md's revision after apply evidence, I4): a version 3
    transient record would read as the previous rule and be compared
    against the wrong digest within the very process that just wrote it.

    An identical record is left untouched.  Once a different record is known,
    the old one is dropped before replacement, so a failure leaves no record
    rather than a claim from a different source state. No record costs a
    rebuild; a wrong one serves a stale model.
    """
    if digest is None:
        drop(artifact)
        return
    directory = os.path.dirname(artifact) or '.'
    path = sidecar(artifact)
    if transient:
        content = {'version': 4, 'digest': digest, 'fingerprint': fingerprint,
                   'transient': True}
        if recipe is not None:
            content['recipe'] = recipe
        desired = (json.dumps(content, sort_keys=True,
                              separators=(',', ':')) + '\n').encode()
    elif fingerprint is None:
        desired = f'{digest}\n'.encode()
    else:
        content = {'version': 4, 'digest': digest, 'fingerprint': fingerprint}
        if recipe is not None:
            content['recipe'] = recipe
        desired = (json.dumps(content, sort_keys=True,
                              separators=(',', ':')) + '\n').encode()
    try:
        with ArtifactSnapshot(path) as existing:
            if existing.read_bytes() == desired:
                return
    except (ArtifactChanged, OSError):
        pass

    # Once a different record is known, preserve the conservative ordering:
    # interruption must leave no record rather than the prior source claim.
    drop(artifact)
    try:
        descriptor, temporary = tempfile.mkstemp(
            prefix=f'.{os.path.basename(path)}.', suffix='.tmp', dir=directory)
        try:
            with os.fdopen(descriptor, 'wb') as output:
                output.write(desired)
            os.replace(temporary, path)
        except Exception:
            if os.path.exists(temporary):
                os.remove(temporary)
            raise
    except OSError as error:
        # The artifact is already published and correct; only the record
        # of what produced it was lost. The next build rebuilds it.
        logger.debug('Could not record the sources of %s: %s', artifact, error)


def publish(temporary, artifact, digest, fingerprint=None, recipe=None,
            transient=False):
    """Move a finished artifact into place with its source record.

    The ordering is the contract: the old record goes BEFORE the new
    artifact appears, and the new record only after it is in place. An
    interruption at any point therefore leaves an artifact with no record
    -- which rebuilds -- and never an artifact carrying a record from the
    source state that produced the previous one, which would certify a
    stale file the moment those sources came back.
    """
    drop(artifact)
    os.replace(temporary, artifact)
    record(artifact, digest, fingerprint, recipe, transient)


def publish_text(path, content, mtime_ns, digest=None, fingerprint=None,
                 transient=False):
    """Publish text at `path`, stamped `mtime_ns` and recorded, replacing
    nothing that already matches (`build-pipeline`, "Unchanged text is not
    replaced").

    When the bytes on disk are already `content`, only the stamp is
    restored, if it differs, and the record refreshed; otherwise the text is
    written to a temporary file in the same directory, stamped, and put in
    place with its record by `publish`. `transient` passes to the record.
    """
    desired = content.encode()
    try:
        with ArtifactSnapshot(path) as existing:
            unchanged = existing.read_bytes() == desired
            existing_mtime_ns = existing.observation.mtime_ns
    except (ArtifactChanged, OSError):
        unchanged = False
        existing_mtime_ns = None

    if unchanged:
        if existing_mtime_ns != mtime_ns:
            restamp(path, mtime_ns)
        record(path, digest, fingerprint, transient=transient)
        return

    directory = os.path.dirname(path) or '.'
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f'.{os.path.basename(path)}.', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(desired)
        os.utime(temporary, ns=(time.time_ns(), mtime_ns))
        publish(temporary, path, digest, fingerprint, transient=transient)
    except Exception:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise


def restamp(artifact, mtime_ns):
    """Give a content-verified artifact the current node mtime, so the
    fast path serves every later build.

    Best effort on purpose. Where the artifact filesystem cannot store the
    exact stamp -- the coarse-resolution case build-pipeline already
    covers -- this will not achieve equality, and that is not a failure:
    the artifact is current on the strength of the digest for this build,
    and the fallback is simply consulted again next time. It must not, and
    does not, loop or reconsider.
    """
    try:
        os.utime(artifact, ns=(time.time_ns(), mtime_ns))
    except OSError as error:
        logger.debug('Could not restamp %s: %s', artifact, error)
