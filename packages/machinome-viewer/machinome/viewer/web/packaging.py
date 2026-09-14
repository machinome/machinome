# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""Setuptools hooks that build the frontends into the distributions.

A source distribution always carries freshly built frontends, so installing
it needs no npm. A wheel built from a checkout keeps frontends already
built there and builds only what is missing.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess

from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


@dataclass
class Frontend:
    directory: Path
    output: Path

    def output_exists(self):
        return self.output.exists()


PACKAGE = Path(__file__).parent
WIDGET = Frontend(
    PACKAGE / 'widget',
    PACKAGE / 'widget' / 'dist' / 'solid-widget.js',
)
# The bundle is the only built frontend now: the development page is a
# plain file the widget directory already carries (`develop.html`,
# `MANIFEST.in`'s `recursive-include solid_node_viewer/widget *`), not a
# second npm project to build.
FRONTENDS = (WIDGET,)


def build_frontend(frontend):
    """Build one frontend included in source distributions and wheels."""
    subprocess.check_call(['npm', 'ci'], cwd=frontend.directory)
    subprocess.check_call(['npm', 'run', 'build'], cwd=frontend.directory)


def build_distribution_frontends():
    """Build every frontend for a source distribution."""
    for frontend in FRONTENDS:
        build_frontend(frontend)


def build_missing_frontends():
    """Build only frontend artifacts absent from a checkout."""
    for frontend in FRONTENDS:
        if not frontend.output_exists():
            build_frontend(frontend)


class BuildSourceDistribution(sdist):
    """Ensure a source distribution contains freshly built frontends."""

    def run(self):
        build_distribution_frontends()
        super().run()


class BuildPythonWithFrontend(build_py):
    """Build a missing frontend before creating a wheel from the checkout."""

    def run(self):
        build_missing_frontends()
        super().run()
