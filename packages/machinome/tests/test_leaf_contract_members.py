# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The declared leaf contract agrees with itself (OpenSpec change
`leaf-contract`, capability `leaf-contract`).

The members each leaf base declares are written in three places: the
spec's first requirement, the base's docstring ("Declared members:") and
the API reference. This reads all three and the code, and requires them
to agree: every declared member exists, is public, is listed in its
base's docstring and is documented in `docs/reference/api.rst`.
"""

import os
import re
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import patch

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
SPEC = os.path.join(REPO_DIR, 'openspec', 'specs', 'leaf-contract', 'spec.md')
DELTA = os.path.join(REPO_DIR, 'openspec', 'changes', 'brep-mesh',
                     'specs', 'leaf-contract', 'spec.md')
API = os.path.join(REPO_DIR, 'docs', 'reference', 'api.rst')

BASES = ('LeafNode', 'BrepLeafNode', 'SheetLeafNode', 'FlexibleNode')


def _spec_text():
    """The change in progress's delta while it exists, the synced spec
    once the change is archived."""
    with open(DELTA if os.path.exists(DELTA) else SPEC) as handle:
        return handle.read()


def _requirement(text):
    """The text of the spec's first requirement."""
    start = text.index('### Requirement: The leaf bases are declared')
    end = text.index('#### Scenario', start)
    return text[start:end]


def spec_members():
    """`{base: set of member names}` and the instance attributes, from
    the spec's first requirement."""
    requirement = _requirement(_spec_text())
    members = {}
    for base in BASES:
        match = re.search(rf'^- `{base}`: (.*?)(?:;|\.)\n(?=- `|\n|`)',
                          requirement, re.S | re.M)
        members[base] = set(re.findall(r'`(\w+)`', match.group(1)))
    instance = re.search(r'\n(`files`.*?) are instance attributes',
                         requirement, re.S)
    return members, set(re.findall(r'`(\w+)`', instance.group(1)))


def qualified_members():
    """`{name: module}` for every declared member the spec qualifies with
    the module that defines it, as `` `StlRenderStart` (`machinome.node.
    base`) ``: a name declared at that module rather than on the base."""
    return dict(re.findall(r'`(\w+)` \(`([\w.]+)`\)',
                           _requirement(_spec_text())))


def docstring_members(cls):
    """The names listed in the "Declared members:" paragraph of `cls`'s
    own docstring, or None when it has none."""
    doc = cls.__doc__ or ''
    match = re.search(r'Declared members:(.*?)(?:\n\s*\n|\Z)', doc, re.S)
    if match is None:
        return None
    return set(re.findall(r'`(\w+)`', match.group(1)))


def documented_members(base):
    """The members `docs/reference/api.rst` documents on the autoclass of
    `base`: its `:members:` option and the directives nested under it."""
    with open(API) as handle:
        lines = handle.read().split('\n')
    for index, line in enumerate(lines):
        if re.match(rf'\.\. autoclass:: [\w.]*\b{base}$', line.strip()) \
                and not line.startswith(' '):
            break
    else:
        return set()
    documented = set()
    continuing = False
    for line in lines[index + 1:]:
        if line and not line.startswith(' '):
            break
        option = re.match(r'\s+:members:\s*(.*)', line)
        if option or (continuing and line.strip() and not re.match(
                r'\s+(:|\.\.)', line)):
            text = option.group(1) if option else line
            documented.update(name.strip() for name in text.split(',')
                              if name.strip())
            continuing = True
            continue
        continuing = False
        nested = re.match(
            r'\s+\.\. (?:auto)?(?:attribute|method|property|data)'
            r'::\s+(\w+)', line)
        if nested:
            documented.add(nested.group(1))
    return documented


class _Instances:
    """One instance of a stand-in of each base, built in a temporary
    build directory, for the members that are instance attributes."""

    def __init__(self, test):
        build_dir = tempfile.mkdtemp(prefix='leaf-contract-members-')
        test.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        with patch.dict(os.environ, {'SOLID_BUILD_DIR': build_dir}):
            from tests.contract_package.exact_stand_in import NativeSolid
            from tests.contract_package.faceted_project import Cube
            from tests.flexible_project.spring import Spring
            from tests.sheet_project.frame_panel import FramePanel
            self.by_base = {'LeafNode': Cube(),
                            'BrepLeafNode': NativeSolid(),
                            'SheetLeafNode': FramePanel(),
                            'FlexibleNode': Spring()}


def _bases():
    from machinome.node.brep_leaf import BrepLeafNode
    from machinome.node.flexible import FlexibleNode
    from machinome.node.leaf import LeafNode
    from machinome.node.sheet_leaf import SheetLeafNode
    return {'LeafNode': LeafNode, 'BrepLeafNode': BrepLeafNode,
            'SheetLeafNode': SheetLeafNode, 'FlexibleNode': FlexibleNode}


class DeclaredMembersTest(TestCase):

    def setUp(self):
        self.members, self.instance_attributes = spec_members()
        self.bases = _bases()

    def test_the_spec_declares_members_for_all_four_bases(self):
        for base in BASES:
            with self.subTest(base=base):
                self.assertTrue(self.members[base])

    def test_every_declared_member_is_public(self):
        for base, names in self.members.items():
            for name in names:
                with self.subTest(base=base, member=name):
                    self.assertFalse(name.startswith('_'))

    def test_every_declared_member_exists(self):
        import importlib
        instances = _Instances(self).by_base
        qualified = qualified_members()
        for base, names in self.members.items():
            for name in names:
                with self.subTest(base=base, member=name):
                    if name in qualified:
                        self.assertTrue(hasattr(
                            importlib.import_module(qualified[name]), name))
                    elif name in self.instance_attributes:
                        self.assertTrue(hasattr(instances[base], name))
                    else:
                        self.assertTrue(hasattr(self.bases[base], name))

    def test_each_docstring_lists_exactly_its_declared_members(self):
        for base, cls in self.bases.items():
            with self.subTest(base=base):
                self.assertEqual(docstring_members(cls), self.members[base])

    def test_each_docstring_names_the_capability_and_no_base_is_internal(self):
        for base, cls in self.bases.items():
            with self.subTest(base=base):
                self.assertIn('declared extension point', cls.__doc__)
                self.assertIn('leaf-contract', cls.__doc__)
                self.assertNotIn('framework-internal', cls.__doc__)

    def test_the_api_reference_documents_every_declared_member(self):
        qualified = qualified_members()
        with open(API) as handle:
            reference = handle.read()
        for base, names in self.members.items():
            documented = documented_members(base)
            for name in names:
                with self.subTest(base=base, member=name):
                    if name in qualified:
                        self.assertRegex(
                            reference, rf'\.\. auto(?:exception|class):: '
                            rf'{re.escape(qualified[name])}\.{name}\b')
                    else:
                        self.assertIn(name, documented)
