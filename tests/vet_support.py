# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Shared helpers for the `machinome vet` tests.

The fixture projects under `tests/vet_projects/` are read by vet as bytes
and are never imported: pytest ignores the directory (`conftest.py`), and
nothing here puts a fixture on `sys.path`.
"""

import os
import shutil
import tempfile

FIXTURES = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'vet_projects')


def fixture_root(name):
    return os.path.join(FIXTURES, name)


def run_vet(name_or_root, reference=None, tests=False):
    """The `Report` of vetting a fixture project (by name) or a root."""
    from machinome.vet import vet
    root = (name_or_root if os.path.isabs(name_or_root)
            else fixture_root(name_or_root))
    return vet(origin=root, reference=reference, tests=tests)


def model_report(report, name=None):
    """One model's report: the only one, or the one called `name`."""
    if name is None:
        (only,) = report.models
        return only
    return next(model for model in report.models if model.name == name)


def findings(report, name=None):
    """A model's findings as a set of `(path, line, kind, name)`."""
    return {(finding.path, finding.line, finding.kind, finding.name)
            for finding in model_report(report, name).findings}


def kinds(report, name=None):
    return {finding.kind for finding in model_report(report, name).findings}


def line_of(root, relative, text):
    """The 1-based line of the first line in a fixture file holding
    `text`."""
    root = root if os.path.isabs(root) else fixture_root(root)
    with open(os.path.join(root, relative), encoding='utf-8',
              errors='replace') as stream:
        for number, line in enumerate(stream, 1):
            if text in line:
                return number
    raise AssertionError(f'{text!r} is not in {relative}')


def copy_fixture(test, name):
    """A temporary copy of a fixture project, removed after `test`.

    Returns `(outside, root)`: a scratch directory outside the copy, and
    the copy's real root, for fixtures whose symbolic links the test
    creates rather than the repository carrying them.
    """
    scratch = os.path.realpath(tempfile.mkdtemp(prefix='machinome-vet-'))
    test.addCleanup(shutil.rmtree, scratch, ignore_errors=True)
    outside = os.path.join(scratch, 'outside')
    os.makedirs(outside)
    root = os.path.join(scratch, 'project')
    shutil.copytree(fixture_root(name), root, symlinks=True)
    return outside, root
