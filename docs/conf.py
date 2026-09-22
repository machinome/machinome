# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Make machinome importable for autodoc without installing it
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Machinome'
copyright = '2023-2026, Luis Henrique Cassis Fagundes'
author = 'Luis Henrique Cassis Fagundes'
release = '0.7.0'
version = '0.7'
html_title = 'Machinome — Source code for machines'

# -- Release facts -----------------------------------------------------------
# The one place the manual states versions and dates. Pages use the
# substitutions below (|release| and |version| are Sphinx's own) so a
# release edits this block and the status page and nothing else.

release_date = '22 September 2026'
viewer_version = '0.7.0'        # the matching machinome-viewer package
viewer_api = '24'               # required source-timed consumer capability
document_versions = '1 to 11'    # supported by the paired corrected viewer
mechanics_version = '0.1.0'     # the matching machinome-mechanics package

rst_prolog = f'''
.. |release_date| replace:: {release_date}
.. |viewer_version| replace:: {viewer_version}
.. |viewer_api| replace:: {viewer_api}
.. |document_versions| replace:: {document_versions}
.. |mechanics_version| replace:: {mechanics_version}
'''

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon',
              'machinome.sphinx']

# Heavy runtime dependencies are mocked so autodoc can import machinome
# on Read the Docs without installing the full CAD stack
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
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'examples/**', 'tutorial/counter/**',
                    'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
