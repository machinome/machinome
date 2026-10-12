# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Setuptools hooks that build the frontends into the distributions.

A source distribution always carries freshly built frontends, so installing
it needs no npm. A wheel built from a checkout keeps a frontend already
built there only while it is CURRENT with the sources beside it, and
rebuilds one that is missing or stale (ADR-059) -- otherwise a wheel cut
from a checkout whose bundle predates its source ships that bundle, and
`scripts/check-dist` installs and smokes it without noticing.
"""

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


# Setuptools loads this module while resolving ``cmdclass``, before the source
# package is importable in an isolated build environment. Load the sibling
# standard-library-only module by path rather than relying on an installed copy
# of this package (which would be the wrong source of currency rules anyway).
_currency_name = 'machinome.viewer.web.currency'
currency = sys.modules.get(_currency_name)
if currency is None:
    _currency_spec = importlib.util.spec_from_file_location(
        _currency_name, Path(__file__).with_name('currency.py'))
    if _currency_spec is None or _currency_spec.loader is None:  # pragma: no cover
        raise ImportError('cannot load machinome.viewer.web.currency')
    currency = importlib.util.module_from_spec(_currency_spec)
    sys.modules[_currency_name] = currency
    _currency_spec.loader.exec_module(currency)


@dataclass
class Frontend:
    directory: Path
    output: Path

    def output_exists(self):
        return self.output.exists()

    def output_is_stale(self):
        """Whether the built output predates the sources it is built from.

        Asked of `currency`, the same module the lookup, the development
        server and the capture ask, so packaging carries no second opinion
        about what stale means.
        """
        return currency.is_stale(self.directory)


PACKAGE = Path(__file__).parent
WIDGET = Frontend(
    PACKAGE / 'widget',
    PACKAGE / 'widget' / 'dist' / 'machinome-viewer.js',
)
# The bundle is the only built frontend now: the development page is a
# plain file the widget directory already carries (`develop.html`,
# `MANIFEST.in`'s `recursive-include machinome/viewer/web/widget *`), not a
# second npm project to build.
FRONTENDS = (WIDGET,)


def build_frontend(frontend):
    """Build one frontend included in source distributions and wheels."""
    # Inside an npm workspace `npm ci` writes the workspace root's
    # node_modules, so a symbolic node_modules anywhere from the widget up is
    # one `npm ci` would empty (change `join-viewer`).
    directory = Path(frontend.directory)
    for level in (directory, *directory.resolve().parents):
        if (level / 'node_modules').is_symlink():
            raise RuntimeError(
                f'{level / "node_modules"} is a symlink; refusing npm ci '
                'because it can empty the shared dependency directory. Use a '
                'checkout with private dependencies to build distributions.')
    # Inside the workspace, `npm ci` from a member's directory installs that
    # member alone and empties every other member's node_modules, the
    # movie's among them; run at the workspace's root it installs them all
    # (change `join-movie`). The bundle is built in the widget's directory.
    root = workspace_root(directory)
    subprocess.check_call(['npm', 'ci'],
                          cwd=root if root is not None else frontend.directory)
    subprocess.check_call(['npm', 'run', 'build'], cwd=frontend.directory)


def workspace_root(directory):
    """The npm workspace whose root `package.json` names `directory` among
    its `workspaces`, or None."""
    here = Path(directory).resolve()
    for parent in here.parents:
        manifest = parent / 'package.json'
        if not manifest.is_file():
            continue
        try:
            members = json.loads(manifest.read_text()).get('workspaces') or []
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(members, dict):
            members = members.get('packages') or []
        for member in members:
            if any(found.resolve() == here
                   for found in parent.glob(str(member))):
                return parent
    return None


def build_distribution_frontends():
    """Build every frontend for a source distribution."""
    for frontend in FRONTENDS:
        build_frontend(frontend)


def build_stale_frontends():
    """Build frontend artifacts a checkout lacks or has let go stale."""
    for frontend in FRONTENDS:
        if not frontend.output_exists() or frontend.output_is_stale():
            build_frontend(frontend)


class BuildSourceDistribution(sdist):
    """Ensure a source distribution contains freshly built frontends."""

    def run(self):
        build_distribution_frontends()
        super().run()


class BuildPythonWithFrontend(build_py):
    """Build a missing or stale frontend before creating a wheel."""

    def run(self):
        build_stale_frontends()
        super().run()
