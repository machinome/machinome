# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The static closure: which project files a model makes Python run.

Its ancestor is the browser-engine prototype's `scripts/walk-imports.py`
(another repository), which resolves dotted and relative imports to
paths from the filesystem alone, and whose rule for a package's own
`__init__.py` is kept here: inside `pkg/__init__.py`, the package a
relative import climbs from is `pkg` itself. Its scope rule is
deliberately reversed. The walker skips imports inside function bodies
and `try`/`except ImportError` blocks, because they are optional for an
install list; vet counts every import statement wherever it sits,
because a function that is never called today can be called tomorrow.

Nothing here imports, compiles or executes a project file. Files are
read as bytes and parsed with `ast.parse`, which honours a PEP 263
coding declaration and a byte-order mark as the interpreter does. The
project root is where the runtime puts it, first on the import path, so
a name that resolves under the root is project code whatever the
universe says, and one that does not is judged by the universe.
"""

import ast
import os

from .assertions import (ESCAPED_MODULE, OUTSIDE_UNIVERSE, SHADOWING,
                         UNPARSEABLE, UNRESOLVED_IMPORT, judge_import,
                         judge_reach, scan)


def reference_parts(reference, cwd):
    """`(target, class_name, is_path)` for a node reference, split as the
    loader splits it, without the loader: a `:` separates the class, and
    a target ending in `.py`, or naming a file under `cwd`, is a path."""
    left, separator, name = reference.rpartition(':')
    target = left if separator else reference
    candidate = target if os.path.isabs(target) else os.path.join(cwd, target)
    is_path = target.endswith('.py') or os.path.isfile(candidate)
    return target, (name if separator else None), is_path


def _within(path, root):
    return os.path.commonpath((path, root)) == root


class Closure:
    """The files one scope of one model makes Python run, and the
    findings raised in them. `files` maps each vetted real path to the
    mode it was judged in."""

    def __init__(self):
        self.files = {}
        self.findings = set()


class Resolver:
    """Resolves and judges the files of one project, once each.

    Every file is parsed at most once per run, however many models
    share it, and judged at most once per mode: the model rules, or the
    model rules with the tests tier added.
    """

    def __init__(self, root, universe):
        self.root = os.path.realpath(root)
        self.universe = universe
        self._parsed = {}
        self._judged = {}

    # Paths -----------------------------------------------------------

    def relative(self, path):
        return os.path.relpath(path, self.root).replace(os.sep, '/')

    def _module_parts(self, path):
        parts = self.relative(path)[:-len('.py')].split('/')
        package = parts[-1] == '__init__'
        return parts, package

    def _top_is_project(self, top):
        base = os.path.join(self.root, top)
        return os.path.isdir(base) or os.path.isfile(base + '.py')

    def locate(self, parts):
        """The files importing `parts` executes, as `(dotted, path)` pairs
        in import order, and whether the whole name was found. Each
        component is a regular package, a module, or a namespace
        directory, tried in the interpreter's order."""
        directory = self.root
        found = []
        for index, component in enumerate(parts):
            dotted = '.'.join(parts[:index + 1])
            base = os.path.join(directory, component)
            init = os.path.join(base, '__init__.py')
            if os.path.isdir(base) and os.path.isfile(init):
                found.append((dotted, init))
                directory = base
            elif os.path.isfile(base + '.py'):
                found.append((dotted, base + '.py'))
                return found, index == len(parts) - 1
            elif os.path.isdir(base):
                directory = base
            else:
                return found, False
        return found, True

    def _package_directory(self, parts):
        """The directory of the project package `parts`, or None when it
        names a module rather than a package."""
        directory = os.path.join(self.root, *parts)
        return directory if os.path.isdir(directory) else None

    # Parsing and judging ---------------------------------------------

    def _parse(self, path):
        if path not in self._parsed:
            with open(path, 'rb') as stream:
                source = stream.read()
            try:
                self._parsed[path] = (ast.parse(source, filename=path), None)
            except SyntaxError as error:
                self._parsed[path] = (None, (error.lineno, error.msg))
            except (ValueError, UnicodeDecodeError) as error:
                self._parsed[path] = (None, (None, str(error)))
        return self._parsed[path]

    def judge(self, path, tests):
        """`(findings, dependencies)` for one file in one mode: its
        findings as `(path, line, kind, name)`, and the project files its
        imports make Python run, as real paths."""
        key = (path, tests)
        if key not in self._judged:
            self._judged[key] = self._judge(path, tests)
        return self._judged[key]

    def _judge(self, path, tests):
        relative = self.relative(path)
        tree, failure = self._parse(path)
        if tree is None:
            line, reason = failure
            return {(relative, line, UNPARSEABLE, reason)}, []
        imports, raised = scan(tree, path, self.root, self.universe)
        findings = {(relative, line, kind, name)
                    for line, kind, name in raised}
        dependencies = []
        for statement in imports:
            for line, kind, name in self._resolve(path, statement, tests,
                                                  dependencies):
                findings.add((relative, line, kind, name))
        return findings, dependencies

    def _add(self, found, line, dependencies, findings):
        """Queue the located project files, refusing one whose real path
        leaves the root."""
        for dotted, candidate in found:
            real = os.path.realpath(candidate)
            if not _within(real, self.root):
                findings.append((line, ESCAPED_MODULE, dotted))
                return False
            dependencies.append(real)
        return True

    def _resolve(self, path, statement, tests, dependencies):
        findings = []
        line = statement.line
        if statement.level:
            # walk-imports.py's rule: a module's parts, with `__init__`
            # kept for a package, lose one component per level, so inside
            # `pkg/__init__.py` one dot is `pkg` itself. A module at the
            # root has no package to climb from.
            parts, _ = self._module_parts(path)
            if statement.level > len(parts) - 1:
                spelled = '.' * statement.level + (statement.module or '')
                return [(line, UNRESOLVED_IMPORT, spelled)]
            module = parts[:-statement.level] + (
                statement.module.split('.') if statement.module else [])
            self._from_project(module, statement, line, dependencies,
                               findings)
            return findings

        if statement.names is None:
            parts = statement.module.split('.')
            if self._top_is_project(parts[0]):
                found, complete = self.locate(parts)
                if self._add(found, line, dependencies, findings) and \
                        not complete:
                    findings.append((line, UNRESOLVED_IMPORT,
                                     statement.module))
                return findings
            return [(line, kind, name) for kind, name in judge_import(
                self.universe, statement.module, tests)]

        parts = statement.module.split('.')
        if self._top_is_project(parts[0]):
            self._from_project(parts, statement, line, dependencies,
                               findings)
            return findings
        findings.extend((line, kind, name) for kind, name in judge_import(
            self.universe, statement.module, tests))
        # Each imported name is judged as a reach beneath the module even
        # when the module itself is outside: `from sys import path` is
        # both `sys` outside the universe and `sys.path`.
        for name in statement.names:
            if name == '*':
                top = parts[0]
                if top in self.universe.restricted:
                    findings.append((line, OUTSIDE_UNIVERSE,
                                     f'{statement.module}.*'))
                continue
            findings.extend(
                (line, kind, reached) for kind, reached in judge_reach(
                    self.universe, f'{statement.module}.{name}'))
        return findings

    def _from_project(self, parts, statement, line, dependencies, findings):
        found, complete = self.locate(parts)
        if not self._add(found, line, dependencies, findings):
            return
        if not complete:
            findings.append((line, UNRESOLVED_IMPORT, '.'.join(parts)))
            return
        for name in statement.names:
            if name == '*':
                directory = self._package_directory(parts)
                if directory is None:
                    continue
                for entry in sorted(os.listdir(directory)):
                    candidate = os.path.join(directory, entry)
                    if entry.endswith('.py') and os.path.isfile(candidate):
                        self._add([('.'.join([*parts, entry[:-3]]),
                                    candidate)], line, dependencies,
                                  findings)
                continue
            child, whole = self.locate([*parts, name])
            if whole and len(child) > len(found):
                self._add(child[len(found):], line, dependencies, findings)

    # Entries and closures -------------------------------------------

    def entry(self, reference, cwd):
        """The files a model reference makes Python run first, or None
        when it names no Python file under the root."""
        target, _, is_path = reference_parts(reference, cwd)
        if is_path:
            path = os.path.realpath(
                target if os.path.isabs(target) else os.path.join(cwd, target))
            if not (path.endswith('.py') and os.path.isfile(path)
                    and _within(path, self.root)):
                return None
            parts, package = self._module_parts(path)
            if package:
                parts = parts[:-1]
            found = self.locate(parts[:-1])[0] if len(parts) > 1 else []
            files = [os.path.realpath(candidate) for _, candidate in found]
            return [*files, path]
        parts = target.split('.')
        if not all(parts) or not self._top_is_project(parts[0]):
            return None
        found, complete = self.locate(parts)
        if not complete or not found:
            return None
        files = [os.path.realpath(candidate) for _, candidate in found]
        if not all(_within(real, self.root) for real in files):
            return None
        if found[-1][0] != target:
            return None
        return files

    def closure(self, entry, tests):
        """Vet one model from its entry files: the model closure, and with
        `tests` the companions of every vetted module and their
        closures, repeated until no file is added."""
        closure = Closure()
        self._walk(entry, False, closure)
        if tests:
            checked = set()
            while True:
                pending = [path for path in sorted(closure.files)
                           if path not in checked]
                if not pending:
                    break
                for path in pending:
                    checked.add(path)
                    companion = self._companion(path)
                    if companion is None or companion in closure.files:
                        continue
                    self._walk([companion], True, closure)
        return closure

    def _companion(self, path):
        directory, filename = os.path.split(path)
        name = 'test.py' if filename == '__init__.py' else f'test_{filename}'
        candidate = os.path.join(directory, name)
        if not os.path.isfile(candidate):
            return None
        return os.path.realpath(candidate)

    def _walk(self, start, tests, closure):
        pending = list(start)
        while pending:
            path = pending.pop()
            if path in closure.files:
                continue
            if not _within(path, self.root):
                closure.findings.add((self.relative(path), None,
                                      ESCAPED_MODULE, self.relative(path)))
                continue
            closure.files[path] = tests
            findings, dependencies = self.judge(path, tests)
            closure.findings.update(findings)
            pending.extend(dependency for dependency in dependencies
                           if dependency not in closure.files)

    def shadowing(self):
        """A root-level module or package named like the top level of a
        universe member, whether or not anything imports it."""
        universe = self.universe
        tops = {member.split('.')[0] for member in (
            *universe.contract, *universe.kernels, *universe.stdlib,
            *universe.tests)}
        findings = set()
        for entry in sorted(os.listdir(self.root)):
            candidate = os.path.join(self.root, entry)
            if entry.endswith('.py') and os.path.isfile(candidate):
                name = entry[:-3]
            elif os.path.isdir(candidate):
                name = entry
            else:
                continue
            if name in tops:
                findings.add((entry, None, SHADOWING, name))
        return findings
