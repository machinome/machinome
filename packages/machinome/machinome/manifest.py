# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""What a project's manifest declares, read without the geometry stack.

Manifest discovery and the validated model declaration live here rather
than in `machinome.core.loader` because the loader imports the node base,
and with it numpy and its family, and every module under
`machinome.core` runs the package `__init__`, which imports the loader.
`machinome vet` and the source adapters' containment check need a
project's root and its models and nothing else, so this module imports
only the standard library.

`machinome.core.loader` imports every name here and re-exports it, so
`loader.ProjectManifestError is manifest.ProjectManifestError`; the
loader turns a `Declaration` into its `Project` by adding each model's
build directory.
"""

import os
import re
import tomllib
from dataclasses import dataclass

__all__ = [
    'Declaration', 'MODEL_NAME', 'ProjectManifestError', 'declared_viewer',
    'project_root', 'read_declaration', 'reference_origin',
]


class ProjectManifestError(Exception):
    pass


#: A declared model name: one word, so it can never be read as a qualifier
#: (which carries a `.` or a `:`) or as a path.
MODEL_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')


@dataclass(frozen=True)
class Declaration:
    """The models a manifest declares, validated, and nothing built.

    `models` holds `(name, reference)` pairs in declaration order; `name`
    is None for the single `model` of a manifest without a `models`
    table. `default` is the declared name `model` selects beside a
    `models` table, or None; a single-model manifest's one model is its
    default and `default` stays None, because that model has no name.
    """

    root: str
    manifest: str
    models: tuple
    default: str | None
    #: Whether the manifest declares its models by name.
    named: bool
    #: The viewer the project names under `[tool.machinome] viewer`, or
    #: None (OpenSpec change `viewer-seam`).
    viewer: str | None = None


def _find_manifest(origin=None):
    origin = os.path.realpath(origin or os.getcwd())
    directory = origin if os.path.isdir(origin) else os.path.dirname(origin)
    while True:
        manifest = os.path.join(directory, 'pyproject.toml')
        try:
            with open(manifest, 'rb') as stream:
                config = tomllib.load(stream)
            tools = config.get('tool', {})
            machinome = tools.get('machinome')
            if machinome is not None:
                return directory, manifest, machinome
            if 'solid-node' in tools:
                raise ProjectManifestError(
                    f"{manifest} uses [tool.solid-node]; Machinome 0.7 uses "
                    "[tool.machinome] (and [tool.machinome.models])")
        except FileNotFoundError:
            pass
        parent = os.path.dirname(directory)
        if parent == directory:
            raise ProjectManifestError(
                "No pyproject.toml with [tool.machinome] found above "
                f"{origin}")
        directory = parent


def project_root(origin=None):
    return _find_manifest(origin)[0]


def _viewer(manifest, declaration):
    """The viewer a manifest names, or None; a value that is not a string
    is refused naming the key. Which names a viewer is the seam's
    (`machinome.viewer`) to answer."""
    named = declaration.get('viewer')
    if named is not None and not isinstance(named, str):
        raise ProjectManifestError(
            f"{manifest} sets [tool.machinome] viewer = {named!r}; a viewer "
            f"is named by a string, such as \"web\"")
    return named


def reference_origin(reference):
    """Where a command looks for the project a reference belongs to: the
    file the reference names, when it names one that exists, else None,
    the working directory."""
    if not reference:
        return None
    path = reference.split(':', 1)[0]
    return os.path.abspath(path) if os.path.exists(path) else None


def declared_viewer(origin=None):
    """The viewer the nearest project above `origin` names, or None when
    it names none or no project is found there."""
    try:
        _root, manifest, declaration = _find_manifest(origin)
    except ProjectManifestError:
        return None
    return _viewer(manifest, declaration)


def read_declaration(origin=None):
    """The nearest Machinome project above `origin`, as a `Declaration`.

    Reads the manifest and looks at the project root's directories; never
    imports project code.
    """
    root, manifest, declaration = _find_manifest(origin)
    viewer = _viewer(manifest, declaration)
    table = declaration.get('models')
    model = declaration.get('model')
    if table is None:
        if not isinstance(model, str) or not model:
            raise ProjectManifestError(
                f"{manifest} has [tool.machinome] but no model reference")
        return Declaration(root, manifest, ((None, model),), None, False,
                           viewer)

    if not isinstance(table, dict) or not table:
        raise ProjectManifestError(
            f"{manifest} declares [tool.machinome.models] with no models")
    models = []
    for name, reference in table.items():
        if not MODEL_NAME.match(name):
            raise ProjectManifestError(
                f"{manifest} declares the model name {name!r}; a name is one "
                f"word of letters, digits, underscores and hyphens")
        if not isinstance(reference, str) or ':' not in reference:
            raise ProjectManifestError(
                f"{manifest} declares model {name!r} as {reference!r}; a "
                f"model is a reference of the form package.module:Class")
        if os.path.isdir(os.path.join(root, name)):
            raise ProjectManifestError(
                f"{manifest} declares a model named {name!r}, but {name}/ is "
                f"a directory at the project root and its artifacts would "
                f"mirror into the model's build directory; rename the model")
        models.append((name, reference))
    if model is not None and not any(name == model for name, _ in models):
        raise ProjectManifestError(
            f"{manifest} sets model = {model!r}, which must name one of "
            f"the declared models: {', '.join(name for name, _ in models)}")
    return Declaration(root, manifest, tuple(models), model, True, viewer)
