# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome vet`: does a project stay inside the machinome universe?

Vet reads the bytes of a project's files and the universe declaration
shipped beside this module, and nothing else. It never imports, compiles
or runs project code, never imports a kernel, and never looks at what the
machine has installed, so its verdict is a property of the project and of
the framework version the declaration names.

It is a static check of what a project declares, not a sandbox, and it
does not hold against an author who sets out to evade it. The runtime
that lacks a capability is the sandbox.
"""

import os
import tomllib
from dataclasses import dataclass

#: The declaration, shipped as package data beside this module.
DECLARATION = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'universe.toml')


def _beneath(name, prefix):
    return name == prefix or name.startswith(prefix + '.')


@dataclass(frozen=True, eq=False)
class Universe:
    """The universe declaration, as data. Every list is a tuple in the
    order the declaration gives it."""

    name: str
    version: str
    contract: tuple
    contract_deny: tuple
    kernels: tuple
    kernel_deny: tuple
    deny_methods: tuple
    stdlib: tuple
    #: A restricted member and the dotted prefixes it admits.
    restricted: dict
    tests: tuple
    dynamic_builtins: tuple
    dynamic_modules: tuple
    import_system: tuple
    dunders: tuple
    denied_builtins: tuple
    open_name: str
    write_modes: tuple
    write_methods: tuple
    source_attributes: tuple
    refused_sources: tuple

    def member(self, name, tests=False):
        """Whether dotted `name` is inside the universe: equal to or
        beneath a member of a tier, by whole components, and within a
        restricted member's allowed prefixes. The tests tier counts only
        with `tests`. The denylists are not consulted: a denied name is
        a member reached for something the universe forbids."""
        tiers = (*self.contract, *self.kernels, *self.stdlib,
                 *(self.tests if tests else ()))
        if not any(_beneath(name, member) for member in tiers):
            return False
        parts = name.split('.')
        allowed = self.restricted.get(parts[0])
        return (allowed is None or len(parts) == 1
                or any(_beneath(name, prefix) for prefix in allowed))


def load_universe(path=DECLARATION):
    """Read the universe declaration."""
    with open(path, 'rb') as stream:
        data = tomllib.load(stream)
    routes, writes = data['routes'], data['writes']
    return Universe(
        name=data['universe']['name'],
        version=data['universe']['version'],
        contract=tuple(data['contract']['members']),
        contract_deny=tuple(data['contract']['deny']),
        kernels=tuple(data['kernels']['members']),
        kernel_deny=tuple(data['kernels']['deny']),
        deny_methods=tuple(data['kernels']['deny_methods']),
        stdlib=tuple(data['stdlib']['members']),
        restricted={member: tuple(prefixes) for member, prefixes
                    in data['stdlib'].get('restricted', {}).items()},
        tests=tuple(data['tests']['members']),
        dynamic_builtins=tuple(routes['dynamic_builtins']),
        dynamic_modules=tuple(routes['dynamic_modules']),
        import_system=tuple(routes['import_system']),
        dunders=tuple(routes['dunders']),
        denied_builtins=tuple(routes['denied_builtins']),
        open_name=writes['open'],
        write_modes=tuple(writes['write_modes']),
        write_methods=tuple(writes['methods']),
        source_attributes=tuple(data['sources']['attributes']),
        refused_sources=tuple(data['sources']['refused']),
    )


class CannotVet(Exception):
    """Vet cannot run: the reference is not one it can vet."""


@dataclass(frozen=True)
class Finding:
    """One finding: where, what kind, and the offending name. `path` is
    relative to the project root; `line` is None when the finding has
    none."""

    path: str
    line: int | None
    kind: str
    name: str


@dataclass(frozen=True)
class ModelReport:
    """One model's verdict, the files vetted for it, and its findings,
    sorted by path, then line, then kind and name."""

    name: str | None
    reference: str
    pure: bool
    files: tuple
    findings: tuple


@dataclass(frozen=True)
class Report:
    universe: Universe
    root: str
    scope: str
    models: tuple

    @property
    def pure(self):
        return all(model.pure for model in self.models)


def _sort_key(finding):
    path, line, kind, name = finding
    return (path, -1 if line is None else line, kind, name)


def _targets(declaration, reference, cwd):
    """The `(name, reference)` pairs to vet: every declared model when
    `reference` is None, else the one model or node it names."""
    from machinome.manifest import MODEL_NAME

    from .resolve import reference_parts
    if reference is None:
        return declaration.models
    target, class_name, is_path = reference_parts(reference, cwd)
    if os.path.isdir(target if os.path.isabs(target)
                     else os.path.join(cwd, target)):
        raise CannotVet(
            'A directory is not a node reference; use a declared model '
            'name, package.module:Class, path/to/file.py, or '
            'path/to/file.py:Class')
    declared = dict(declaration.models) if declaration.named else {}
    if (not is_path and class_name is None and MODEL_NAME.match(target)
            and target in declared):
        return ((target, declared[target]),)
    return ((None, reference),)


def vet(origin=None, reference=None, tests=False):
    """Vet the project above `origin` (the working directory by default):
    every model it declares, or the one `reference` names, and with
    `tests` the companion tests of every vetted module too.

    Raises `machinome.manifest.ProjectManifestError` when there is no
    manifest or it is malformed, and `CannotVet` for a directory
    reference; returns a `Report` otherwise.
    """
    from machinome.manifest import read_declaration

    from .assertions import UNRESOLVED_REFERENCE
    from .resolve import Resolver

    cwd = os.getcwd()
    declaration = read_declaration(origin)
    targets = _targets(declaration, reference, cwd)
    universe = load_universe()
    resolver = Resolver(declaration.root, universe)
    shadowing = resolver.shadowing()
    manifest = resolver.relative(os.path.realpath(declaration.manifest))
    models = []
    for name, target in targets:
        entry = resolver.entry(target, cwd)
        if entry is None:
            raised = {(manifest, None, UNRESOLVED_REFERENCE, target)}
            files = ()
        else:
            closure = resolver.closure(entry, tests)
            raised = set(closure.findings)
            files = tuple(sorted(resolver.relative(path)
                                 for path in closure.files))
        raised |= shadowing
        found = tuple(Finding(*finding)
                      for finding in sorted(raised, key=_sort_key))
        models.append(ModelReport(name, target, not found, files, found))
    return Report(universe, resolver.root, 'tests' if tests else 'models',
                  tuple(models))


#: What every text report says first, after the universe it names.
PREAMBLE = ('Vet statically checks what this project declares; it is not a '
            'sandbox, and it\n'
            'does not hold against an author who sets out to evade it.\n')


def render_text(report):
    """The report for people: the preamble, one line per model with its
    verdict and one indented line per finding, then the project's."""
    def verdict(pure):
        return 'pure' if pure else 'not pure'

    lines = [f'machinome vet: universe {report.universe.name} '
             f'{report.universe.version}\n', PREAMBLE, '\n']
    for model in report.models:
        lines.append(f'{model.name or model.reference}  '
                     f'{verdict(model.pure)}\n')
        for finding in model.findings:
            where = (finding.path if finding.line is None
                     else f'{finding.path}:{finding.line}')
            lines.append(f'  {where}  {finding.kind}  {finding.name}\n')
    lines.append(f'project  {verdict(report.pure)}\n')
    return ''.join(lines)


def report_object(report):
    """The report as the one JSON object hosts read, keys in the
    specification's order."""
    return {
        'universe': {'name': report.universe.name,
                     'version': report.universe.version},
        'root': report.root,
        'scope': report.scope,
        'pure': report.pure,
        'models': [{
            'name': model.name,
            'reference': model.reference,
            'pure': model.pure,
            'files': list(model.files),
            'findings': [{'path': finding.path, 'line': finding.line,
                          'kind': finding.kind, 'name': finding.name}
                         for finding in model.findings],
        } for model in report.models],
    }


def render_json(report):
    import json
    return json.dumps(report_object(report), sort_keys=False) + '\n'
