# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import glob
import os
import sys

# Make machinome importable for autodoc without installing it, with the
# extension packages beside it under packages/, whose modules the core's
# package path admits as portions (machinome._namespace_portions). The
# browser viewer's directory is left out: the manual takes the viewer it
# completes exports with from what docs/requirements.txt installs, and a
# source copy without a built bundle would shadow it (change `join-viewer`).
sys.path[:0] = [os.path.abspath('..'),
                *(path for path in sorted(glob.glob(
                    os.path.abspath('../../machinome-*')))
                  if os.path.basename(path) != 'machinome-viewer')]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Machinome'
copyright = '2023-2026, Luis Henrique Cassis Fagundes'
author = 'Luis Henrique Cassis Fagundes'
release = '0.8.1'
version = '0.8'
html_title = 'Machinome — Source code for machines'

# -- Release facts -----------------------------------------------------------
# The one place the manual states versions and dates. Pages use the
# substitutions below (|release| and |version| are Sphinx's own) so a
# release edits this block and the status page and nothing else.

release_date = '10 October 2026'
# The viewer, numbered with the set (packages/machinome-viewer/pyproject.toml);
# its API and document versions are its widget's, which tests hold them to.
viewer_version = '0.8.1'
viewer_api = '29'               # a clocked machine captured on demand
document_versions = '1 to 13'    # supported by the paired viewer
# The mechanics helpers' own version, packages/machinome-mechanics/pyproject.toml,
# which tests/test_release_records.py holds to it.
mechanics_version = '0.1.0'
framework_licence = 'GPL-2.0-or-later or CERN-OHL-S-2.0-or-later'

rst_prolog = f'''
.. |release_date| replace:: {release_date}
.. |viewer_version| replace:: {viewer_version}
.. |viewer_api| replace:: {viewer_api}
.. |document_versions| replace:: {document_versions}
.. |mechanics_version| replace:: {mechanics_version}
.. |framework_licence| replace:: {framework_licence}
'''

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon',
              'sphinx.ext.doctest', 'machinome.sphinx']

# Every cross-reference must resolve, so a warnings-as-errors build (CI,
# Read the Docs) refuses a link to nothing.
nitpicky = True

# The runtime dependencies are mocked so autodoc can import machinome from
# the source tree with Sphinx, the theme and the viewer installed and
# nothing else: the documentation build runs no CAD stack.
autodoc_mock_imports = [
    'trimesh',
    'numpy',
    'watchdog',
    'cadquery',
    'solid2',
    'manifold3d',
    'build123d',
    'molejo',
    'scipy',
    'rtree',
    'OCP',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'tutorial/counter/**', 'Thumbs.db',
                    '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# The browser viewer's guides: the click-to-load demo and its frame, and the
# viewer's reference entries on narrow screens.
html_js_files = ['viewer-demo.js']
html_css_files = ['viewer-demo.css']


def copy_the_embedding_example(app, exception):
    """The embedding guide's working host page, beside the built guide, with
    the committed spinner export it loads and the installed viewer's bundle
    (change `join-viewer`)."""
    import shutil
    from pathlib import Path

    from machinome.viewers import bundle

    if exception is not None or app.builder.format != 'html':
        return
    source = Path(app.srcdir)
    target = Path(app.outdir) / 'howto' / 'embed-the-viewer'
    shutil.copytree(source / 'howto' / 'embed-the-viewer', target,
                    dirs_exist_ok=True)
    shutil.copytree(source / '_exports' / 'spinner', target / 'spinner',
                    dirs_exist_ok=True)
    shutil.copy2(bundle.bundle_path(), target / 'machinome-viewer.js')


def setup(app):
    app.connect('build-finished', copy_the_embedding_example)
