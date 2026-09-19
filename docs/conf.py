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
release = '0.7 (in preparation)'
html_title = 'Machinome — Source code for machines'

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
exclude_patterns = ['_build', 'examples/**', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
