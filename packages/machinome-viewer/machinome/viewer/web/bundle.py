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

from solid_node_viewer.currency import (
    BUNDLE_NAME, PACKAGE_DIR, WIDGET_DIR, BundleStale, ensure_current,
)

PACKAGE_JSON = WIDGET_DIR / 'package.json'
INDEX_NAME = 'index.html'

#: Re-exported so a caller that handles one broken installation handles
#: both: `BundleMissing` and `BundleStale` are the two ways this package
#: declines to hand out a bundle, and neither ever substitutes one.
__all__ = ['BundleMissing', 'BundleStale', 'api_version', 'bundle_path',
           'describe', 'document_versions', 'has_bundle', 'index_path',
           'missing_bundle_remedy', 'version']


def bundle_path():
    """Return the installed viewer bundle path."""
    return WIDGET_DIR / 'dist' / BUNDLE_NAME


def index_path():
    """Return the installed standalone export page path."""
    return WIDGET_DIR / INDEX_NAME


def develop_page_path():
    """Return the development page path.

    Unlike the export page, this is not a published name -- it is served
    by this package's own server at ``/`` and named nowhere else. It sits
    beside the bundle it is authored against, so its version can never
    drift from it (design D9).
    """
    return WIDGET_DIR / 'develop.html'


def has_bundle():
    """Whether this installation includes the built viewer bundle."""
    return bundle_path().is_file()


#: What every viewer released so far reads. A consumer that receives no
#: ``documentVersions`` is entitled to assume exactly this, so a build
#: whose package predates the declaration still answers truthfully.
RELEASED_DOCUMENT_VERSIONS = [1, 2, 3, 4]


def api_version():
    """Return the viewer API version declared by the widget package."""
    with open(PACKAGE_JSON) as stream:
        return json.load(stream)['solidNodeViewerApi']


def document_versions():
    """Return the document schema versions this build's widget renders.

    Read from the widget package's own single declaration -- the same one
    the bundle is built from -- so the answer a framework reads and the
    versions the bundle actually refuses can never disagree.
    """
    with open(PACKAGE_JSON) as stream:
        declared = json.load(stream).get('solidNodeDocumentVersions')
    return list(declared) if declared else list(RELEASED_DOCUMENT_VERSIONS)


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
    ``apiVersion`` the widget declares, the list of document schema versions
    it renders as ``documentVersions``, and the package ``version``. Raises
    :class:`BundleMissing` when the installation has no built bundle, so a
    caller never receives a path that does not exist.

    In a source checkout the bundle is made current with the sources it is
    built from BEFORE the declaration is read (ADR-059), so the
    ``apiVersion`` and ``documentVersions`` reported are the ones the
    bundle at ``path`` actually carries rather than the ones a later
    edit put in ``package.json``. Raises :class:`BundleStale` when it is
    older and cannot be rebuilt: answering from a stale bundle is how a
    correct document came to be refused by an old renderer.
    """
    if not has_bundle():
        raise BundleMissing()
    ensure_current()
    return {
        'path': str(bundle_path().resolve()),
        'index': str(index_path().resolve()),
        'apiVersion': api_version(),
        'documentVersions': document_versions(),
        'version': version(),
    }
