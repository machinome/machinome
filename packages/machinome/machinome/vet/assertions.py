# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The rules vet applies to one parsed file, and the universe's judgement
of a dotted name.

`scan` walks a module's syntax tree once. It records the module's import
statements for the resolver (assertion 1, the closure) and raises the
findings of assertion 2 (no dynamic route and no write) and assertion 3
(declared sources stay home), which depend on the file alone.

`judge_import` and `judge_reach` are the universe's word on a name that
does not resolve under the project root: the first for a module an
import statement names, the second for a dotted name a file reaches
beneath a module it imported -- `from numpy import load`, or `np.load`
after `import numpy as np`.

What these rules prove, and what they do not: they are sound against
every ordinary spelling of a route, and not against an author who sets
out to evade them. `getattr(np, 'lo' + 'ad')`, a dunder assembled at run
time, a local rebinding (`p = os`) or an alias through a data structure
all pass. A name the file binds itself is the project's, not a
built-in's, wherever it is bound, so a file that binds `eval` and also
calls the built-in passes. Vet is a static check, not a sandbox.
"""

import ast
import os
from dataclasses import dataclass

#: The finding kinds. Every finding vet raises is one of these sixteen.
OUTSIDE_UNIVERSE = 'outside-universe'
KERNEL_IO = 'kernel-io'
FRAMEWORK_INTERNAL = 'framework-internal'
FILE_WRITE = 'file-write'
DYNAMIC_ROUTE = 'dynamic-route'
IMPORT_SYSTEM = 'import-system'
DENIED_DUNDER = 'denied-dunder'
DENIED_BUILTIN = 'denied-builtin'
SHADOWING = 'shadowing'
UNPARSEABLE = 'unparseable'
UNRESOLVED_IMPORT = 'unresolved-import'
ESCAPED_MODULE = 'escaped-module'
UNRESOLVED_REFERENCE = 'unresolved-reference'
SOURCE_ABSOLUTE = 'source-absolute'
SOURCE_ESCAPES = 'source-escapes'
JSCAD_SOURCE = 'jscad-source'

KINDS = (
    OUTSIDE_UNIVERSE, KERNEL_IO, FRAMEWORK_INTERNAL, FILE_WRITE,
    DYNAMIC_ROUTE, IMPORT_SYSTEM, DENIED_DUNDER, DENIED_BUILTIN, SHADOWING,
    UNPARSEABLE, UNRESOLVED_IMPORT, ESCAPED_MODULE, UNRESOLVED_REFERENCE,
    SOURCE_ABSOLUTE, SOURCE_ESCAPES, JSCAD_SOURCE,
)


def beneath(name, prefix):
    """Whether dotted `name` equals `prefix` or lies beneath it, by whole
    components: `xml.etree.ElementTree` is beneath `xml.etree`, and
    `xmlx` is not beneath `xml`."""
    return name == prefix or name.startswith(prefix + '.')


def _first(name, prefixes):
    return next((prefix for prefix in prefixes if beneath(name, prefix)),
                None)


def _restriction(universe, name):
    """The finding for a restricted member reached beyond its allowed
    prefixes, or None. `os.environ.get` is reported as `os.environ`."""
    parts = name.split('.')
    allowed = universe.restricted.get(parts[0])
    if allowed is None or len(parts) == 1 or _first(name, allowed):
        return None
    return (OUTSIDE_UNIVERSE, '.'.join(parts[:2]))


def _member_rules(universe, name):
    """What the contract and kernel denylists, and the restrictions, say
    of a name beneath a member: a list of `(kind, name)`."""
    if _first(name, universe.contract):
        denied = _first(name, universe.contract_deny)
        return [(FRAMEWORK_INTERNAL, denied)] if denied else []
    if _first(name, universe.kernels):
        denied = _first(name, universe.kernel_deny)
        return [(KERNEL_IO, denied)] if denied else []
    restricted = _restriction(universe, name)
    return [restricted] if restricted else []


def judge_import(universe, name, tests=False):
    """The universe's judgement of an imported module `name` that does not
    resolve under the project root, as a list of `(kind, name)`.

    `tests` adds the tests tier, for a file reached only through a
    companion test.
    """
    dynamic = _first(name, universe.dynamic_modules)
    if dynamic:
        return [(DYNAMIC_ROUTE, dynamic)]
    if (_first(name, universe.contract) or _first(name, universe.kernels)
            or _first(name, universe.stdlib)):
        return _member_rules(universe, name)
    if tests and _first(name, universe.tests):
        return []
    return [(OUTSIDE_UNIVERSE, name)]


def judge_reach(universe, name):
    """The judgement of a dotted name reached beneath an imported module,
    by `from p import n` or by an attribute chain on an import-bound
    name. Only the import-system names, the denylists and the
    restrictions apply here: whether the module itself may be imported
    was judged at its import."""
    system = _first(name, universe.import_system)
    if system:
        return [(IMPORT_SYSTEM, system)]
    return _member_rules(universe, name)


@dataclass(frozen=True)
class ImportStatement:
    """One import statement, as the resolver needs it.

    `module` is the dotted module an `import` names, or the `from` part
    of a `from ... import` (None for `from . import n`); `names` is None
    for an `import`, otherwise the imported names (`('*',)` for a star).
    """

    line: int
    module: str | None
    level: int
    names: tuple | None


def _write_mode(call, position):
    """Whether an `open` call's mode, the positional argument at
    `position` or the `mode=` keyword, may write. No mode reads; a
    literal mode reads when it holds none of the write characters; any
    other mode cannot be judged and is a write."""
    mode = None
    for keyword in call.keywords:
        if keyword.arg == 'mode':
            mode = keyword.value
        elif keyword.arg is None:
            return True
    positional = call.args
    if any(isinstance(argument, ast.Starred) for argument in positional):
        return True
    if mode is None and len(positional) > position:
        mode = positional[position]
    if mode is None:
        return False
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return mode.value
    return True


class _Scanner(ast.NodeVisitor):

    def __init__(self, universe, path, root, bindings, bound):
        self.universe = universe
        self.path = path
        self.root = root
        self.bindings = bindings
        self.bound = bound
        self.findings = []
        self.imports = []
        self._callees = set()
        self._inner = set()

    def raise_(self, node, kind, name):
        self.findings.append((getattr(node, 'lineno', None), kind, name))

    # Imports ---------------------------------------------------------

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(
                ImportStatement(node.lineno, alias.name, 0, None))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imports.append(ImportStatement(
            node.lineno, node.module, node.level,
            tuple(alias.name for alias in node.names)))
        self.generic_visit(node)

    # Names -----------------------------------------------------------

    def visit_Call(self, node):
        self._callees.add(id(node.func))
        routes = self.universe
        func = node.func
        if (isinstance(func, ast.Name) and func.id == routes.open_name
                and func.id not in self.bound):
            self._judge_open(node, 1)
        elif isinstance(func, ast.Attribute) and func.attr == routes.open_name:
            self._judge_open(node, 0)
        self.generic_visit(node)

    def _judge_open(self, call, position):
        mode = _write_mode(call, position)
        if mode is True or (isinstance(mode, str) and any(
                character in mode
                for character in self.universe.write_modes)):
            self.raise_(call, FILE_WRITE, self.universe.open_name)

    def visit_Name(self, node):
        universe = self.universe
        name = node.id
        bound = self.bindings.get(name)
        if bound is None and name in self.bound:
            # The file binds this name itself: it is the project's, not
            # the built-in's.
            pass
        elif bound is None:
            if name in universe.dynamic_builtins:
                self.raise_(node, DYNAMIC_ROUTE, name)
            elif name in universe.denied_builtins:
                self.raise_(node, DENIED_BUILTIN, name)
            elif (name == universe.open_name
                  and id(node) not in self._callees):
                self.raise_(node, FILE_WRITE, name)
        else:
            system = _first(bound, universe.import_system)
            if system:
                self.raise_(node, IMPORT_SYSTEM, system)
        if name in universe.dunders:
            self.raise_(node, DENIED_DUNDER, name)

    def visit_Attribute(self, node):
        universe = self.universe
        attribute = node.attr
        if attribute in universe.dunders:
            self.raise_(node, DENIED_DUNDER, attribute)
        if attribute in universe.write_methods:
            self.raise_(node, FILE_WRITE, attribute)

        chain = [attribute]
        value = node.value
        while isinstance(value, ast.Attribute):
            self._inner.add(id(value))
            chain.append(value.attr)
            value = value.value
        bound = (self.bindings.get(value.id)
                 if isinstance(value, ast.Name) else None)
        if bound is None:
            if (attribute in universe.deny_methods
                    and attribute not in universe.write_methods):
                self.raise_(node, KERNEL_IO, attribute)
        elif id(node) not in self._inner:
            reached = '.'.join([bound, *reversed(chain)])
            for kind, name in judge_reach(universe, reached):
                self.raise_(node, kind, name)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value in self.universe.dunders:
            self.raise_(node, DENIED_DUNDER, node.value)

    # Sources ---------------------------------------------------------

    def visit_Assign(self, node):
        for target in node.targets:
            self._judge_source(target, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self._judge_source(node.target, node.value)
        self.generic_visit(node)

    def _judge_source(self, target, value):
        if isinstance(target, ast.Name):
            attribute = target.id
        elif isinstance(target, ast.Attribute):
            attribute = target.attr
        else:
            return
        is_none = isinstance(value, ast.Constant) and value.value is None
        if attribute in self.universe.refused_sources:
            if not is_none:
                self.raise_(target, JSCAD_SOURCE, attribute)
            return
        if attribute not in self.universe.source_attributes:
            return
        if not (isinstance(value, ast.Constant)
                and isinstance(value.value, str)):
            # None, or a computed value: a read inside the project, which
            # the adapters contain at construction.
            return
        declared = value.value
        if os.path.isabs(declared):
            self.raise_(target, SOURCE_ABSOLUTE, attribute)
            return
        # The adapters' own arithmetic: the declaring module's directory,
        # joined and resolved through every symbolic link. The file need
        # not exist, and it is never opened.
        resolved = os.path.realpath(
            os.path.join(os.path.dirname(self.path), declared))
        if os.path.commonpath((resolved, self.root)) != self.root:
            self.raise_(target, SOURCE_ESCAPES, attribute)


def import_bindings(tree):
    """Every name an import statement binds anywhere in the file, mapped
    to the dotted name it stands for. Relative imports bind project
    names; they are recorded with a leading dot so no universe rule ever
    matches them."""
    bindings = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    bindings[alias.asname] = alias.name
                else:
                    top = alias.name.split('.')[0]
                    bindings[top] = top
        elif isinstance(node, ast.ImportFrom):
            base = '.' * node.level + (node.module or '')
            for alias in node.names:
                if alias.name == '*':
                    continue
                separator = '' if base.endswith('.') else '.'
                bindings[alias.asname or alias.name] = (
                    f'{base}{separator}{alias.name}')
    return bindings


def bound_names(tree):
    """Every name the file binds anywhere, in any scope: an assignment
    target of any form, a `def` or `class`, a parameter, a `for`, `with`,
    `except` or comprehension target, a `match` capture, or an import.

    Such a name is the project's, not a built-in's, so the built-in rules
    (`dynamic-route`, `denied-builtin`, `open`) do not apply to it. Scope
    is not tracked: a file that binds `eval` somewhere and also calls the
    built-in elsewhere is not caught, which only an author setting out to
    evade vet would write."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(
                node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            names.add(node.rest)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name != '*':
                    names.add(alias.asname or alias.name.split('.')[0])
    return names


def scan(tree, path, root, universe):
    """The import statements of a parsed module, and the findings of
    assertions 2 and 3 in it, as `(imports, findings)`; each finding is
    `(line, kind, name)`.

    `path` and `root` are real paths: a relative source literal is
    resolved against `path`'s directory and must stay under `root`.
    """
    scanner = _Scanner(universe, path, root, import_bindings(tree),
                       bound_names(tree))
    scanner.visit(tree)
    return scanner.imports, scanner.findings
