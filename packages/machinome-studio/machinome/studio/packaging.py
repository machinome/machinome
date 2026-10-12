# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Setuptools hooks that build the browser surface into the distributions.

A source distribution always carries a freshly built ``static/``, so
installing it needs no npm; a wheel built from a checkout rebuilds a surface
that is missing or older than a source of ``frontend/``. Setuptools imports
this module while it resolves ``cmdclass``, before the package's
dependencies exist, so it imports the standard library and setuptools alone
(change ``join-studio``).
"""

import json
import subprocess
from pathlib import Path

from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

PACKAGE = Path(__file__).parent
FRONTEND = PACKAGE / 'frontend'
SURFACE = PACKAGE / 'static' / 'index.html'


def sources():
    """The frontend's files, its installed dependencies excepted."""
    return (path for path in FRONTEND.rglob('*')
            if path.is_file() and 'node_modules' not in path.parts)


def is_stale():
    """Whether the built surface is absent or older than a frontend source."""
    if not SURFACE.is_file():
        return True
    built = SURFACE.stat().st_mtime
    return any(path.stat().st_mtime > built for path in sources())


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


def build_frontend():
    """Install the frontend's dependencies and build the surface."""
    # Inside the npm workspace `npm ci` writes the root's node_modules, so a
    # symbolic node_modules anywhere from the frontend up is one it would
    # empty (the viewer's guard).
    for level in (FRONTEND, *FRONTEND.resolve().parents):
        if (level / 'node_modules').is_symlink():
            raise RuntimeError(
                f'{level / "node_modules"} is a symlink; refusing npm ci '
                'because it can empty the shared dependency directory. Use a '
                'checkout with private dependencies to build distributions.')
    # At the workspace's root `npm ci` installs every member from the root
    # lock; from a member's directory it would empty the other members'
    # node_modules (change `join-movie`). The surface is built in the
    # frontend's directory, into ../static.
    root = workspace_root(FRONTEND)
    subprocess.check_call(['npm', 'ci', '--no-audit', '--no-fund'],
                          cwd=root if root is not None else FRONTEND)
    subprocess.check_call(['npm', 'run', 'build'], cwd=FRONTEND)


class BuildSourceDistribution(sdist):
    """Build the surface before a source distribution is made."""

    def run(self):
        build_frontend()
        super().run()


class BuildPythonWithFrontend(build_py):
    """Build a missing or stale surface before a wheel is made."""

    def run(self):
        if is_stale():
            build_frontend()
        super().run()
