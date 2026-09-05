# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""Locate the built viewer without importing anything else.

This module is the whole interface solid-node has to the viewer's files: the
``solid_node.viewer`` entry point resolves to :func:`describe`, and the
``solid-node-viewer describe`` command prints the same answer. It imports
only the standard library so that answering costs no browser bundle, no web
framework and no CAD stack.
"""

import json
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent
WIDGET_DIR = PACKAGE_DIR / 'widget'
APP_DIR = PACKAGE_DIR / 'app'
PACKAGE_JSON = WIDGET_DIR / 'package.json'
BUNDLE_NAME = 'solid-widget.js'
INDEX_NAME = 'index.html'


def bundle_path():
    """Return the installed viewer bundle path."""
    return WIDGET_DIR / 'dist' / BUNDLE_NAME


def index_path():
    """Return the installed standalone export page path."""
    return WIDGET_DIR / INDEX_NAME


def app_build_path():
    """Return the built development app directory."""
    return APP_DIR / 'build'


def has_bundle():
    """Whether this installation includes the built viewer bundle."""
    return bundle_path().is_file()


def api_version():
    """Return the viewer API version declared by the widget package."""
    with open(PACKAGE_JSON) as stream:
        return json.load(stream)['solidNodeViewerApi']


def version():
    """Return the version of this package, read where pip recorded it."""
    from importlib.metadata import PackageNotFoundError, version as installed
    try:
        return installed('solid-node-viewer')
    except PackageNotFoundError:
        from solid_node_viewer import __version__
        return __version__


def missing_bundle_remedy():
    """Explain how to obtain a bundle when this installation has none."""
    return (
        f'Viewer bundle not found at {bundle_path()}. A release of '
        'solid-node-viewer from PyPI carries it; a source checkout builds it '
        f'with: cd {WIDGET_DIR} && npm ci && npm run build.'
    )


class BundleMissing(FileNotFoundError):
    """This installation carries no built bundle."""

    def __init__(self):
        super().__init__(missing_bundle_remedy())


def describe():
    """The installed viewer, as the ``solid_node.viewer`` entry point reports it.

    Returns a JSON-serializable mapping with the absolute ``path`` of the
    bundle, the absolute ``index`` of the standalone export page, the integer
    ``apiVersion`` the widget declares and the package ``version``. Raises
    :class:`BundleMissing` when the installation has no built bundle, so a
    caller never receives a path that does not exist.
    """
    if not has_bundle():
        raise BundleMissing()
    return {
        'path': str(bundle_path().resolve()),
        'index': str(index_path().resolve()),
        'apiVersion': api_version(),
        'version': version(),
    }
