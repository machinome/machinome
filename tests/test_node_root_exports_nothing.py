# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The node package's root exports nothing (OpenSpec change `root-cleanup`,
design.md Decision 6, capability `node-model`): the acceptance gate,
permanent.

Two halves. G1, at run time: the root resolves none of the twenty-one names
it resolved until this change, refuses each with `ImportError` naming the
module that defines it, lists nothing in `__all__`, binds nothing on a star
import, and binds no public name in its namespace but its submodules; the
class names of every row of the table of supported node types are refused
naming `machinome.node.<key>` of their row.

G2, as text: no file under `machinome/` or `tests/`, and no page under
`docs/` (decision records and built output excepted) or `README.rst`, spells
one of the twenty-one names in an import statement from the root (one line,
a parenthesised list or a backslash continuation), the star import from the
root, or a dotted address on the root. A statement composed at run time is
not a literal and passes, which is how this file spells the refusals; its
planted samples are spelled in pieces.
"""

import importlib
import re
import types
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import machinome.node

ROOT = Path(__file__).resolve().parents[1]

#: The twenty-one names `machinome/node/__init__.py` resolved until this
#: change, each with the module that defines it. Written out here rather
#: than read from the package under test.
FORMER = {
    'AssemblyNode': 'machinome.node.assembly',
    'declared_children': 'machinome.node.declarative',
    'FusionNode': 'machinome.node.fusion',
    'CadQueryNode': 'machinome.node.cadquery',
    'Build123dNode': 'machinome.node.build123d',
    'Build123dSheetNode': 'machinome.node.build123d',
    'SheetLeafNode': 'machinome.node.sheet_leaf',
    'FlexibleNode': 'machinome.node.flexible',
    'MolejoNode': 'machinome.node.molejo',
    'Solid2Node': 'machinome.node.solid2',
    'OpenScadNode': 'machinome.node.openscad',
    'JScadNode': 'machinome.node.jscad',
    'StlNode': 'machinome.node.stl',
    'Marking': 'machinome.node.markings',
    'Wrapped': 'machinome.node.markings',
    'Flat': 'machinome.node.markings',
    'Svg': 'machinome.node.markings',
    'Frame': 'machinome.node.frames',
    'StepNode': 'machinome.node.step',
    'property_as_number': 'machinome.node.decorators',
    'StlRenderStart': 'machinome.node.base',
}


def refusal(name, module):
    """design.md Decision 3's sentence, spelled out independently."""
    return (f"module 'machinome.node' has no attribute {name!r}: the root "
            f"of machinome.node exports nothing, and {name!r} is imported "
            f"from its module, {module!r}. Write "
            f"`from {module} import {name}`.")


def import_from_the_root(name):
    """Run the import statement for `name` from the root, composed at run
    time, in a fresh namespace; return that namespace."""
    namespace = {}
    exec(f'from machinome.node import {name}', namespace)
    return namespace


class TheRootResolvesNothingTest(TestCase):
    """G1."""

    def test_each_former_name_is_refused_at_the_import_line(self):
        for name, module in FORMER.items():
            with self.subTest(name=name):
                with self.assertRaises(ImportError) as raised:
                    import_from_the_root(name)
                self.assertNotIsInstance(raised.exception, AttributeError)
                self.assertEqual(str(raised.exception),
                                 refusal(name, module))

    def test_each_former_name_is_refused_as_an_attribute(self):
        for name, module in FORMER.items():
            with self.subTest(name=name):
                with self.assertRaises(ImportError) as raised:
                    getattr(machinome.node, name)
                self.assertEqual(str(raised.exception),
                                 refusal(name, module))

    def test_hasattr_raises_the_refusal(self):
        for name, module in FORMER.items():
            with self.subTest(name=name):
                with self.assertRaises(ImportError) as raised:
                    hasattr(machinome.node, name)
                self.assertEqual(str(raised.exception),
                                 refusal(name, module))

    def test_each_name_is_imported_from_its_module(self):
        for name, module in FORMER.items():
            with self.subTest(name=name):
                defined = getattr(importlib.import_module(module), name)
                namespace = {}
                exec(f'from {module} import {name}', namespace)
                self.assertIs(namespace[name], defined)

    def test_the_root_lists_nothing(self):
        self.assertEqual(machinome.node.__all__, [])

    def test_the_star_import_binds_nothing(self):
        namespace = {}
        exec('from machinome.node ' 'import *', namespace)
        self.assertEqual(
            sorted(key for key in namespace if key != '__builtins__'), [])

    def test_every_public_name_of_the_namespace_is_a_submodule(self):
        not_submodules = []
        for key, value in vars(machinome.node).items():
            if key.startswith('_'):
                continue
            if not isinstance(value, types.ModuleType) \
                    or value.__name__ != f'machinome.node.{key}':
                not_submodules.append(key)
        self.assertEqual(sorted(not_submodules), [])

    def test_every_class_of_the_table_is_refused_naming_its_row(self):
        from machinome.node.supported import NODE_TYPES

        for key, row in NODE_TYPES.items():
            for name in row.classes:
                with self.subTest(key=key, name=name):
                    with self.assertRaises(ImportError) as raised:
                        import_from_the_root(name)
                    self.assertEqual(
                        str(raised.exception),
                        refusal(name, f'machinome.node.{key}'))

    def test_a_row_added_to_the_table_is_refused_naming_its_module(self):
        from machinome.node.supported import NODE_TYPES, NodeType

        with patch.dict(NODE_TYPES, {'gizmo': NodeType(('GizmoNode',))}):
            with self.assertRaises(ImportError) as raised:
                import_from_the_root('GizmoNode')
        self.assertEqual(str(raised.exception),
                         refusal('GizmoNode', 'machinome.node.gizmo'))

    def test_another_name_is_a_missing_attribute(self):
        for name in ('NoSuchNode', 'NODE_TYPES', 'import_module',
                     'find_spec', 'ExtraUnavailable', 'Length'):
            with self.subTest(name=name):
                with self.assertRaises(AttributeError):
                    getattr(machinome.node, name)

    def test_the_table_lists_the_nine_classes_written_here(self):
        from machinome.node.supported import NODE_TYPES

        listed = {name: f'machinome.node.{key}'
                  for key, row in NODE_TYPES.items() for name in row.classes}
        self.assertEqual(listed, {name: module
                                  for name, module in FORMER.items()
                                  if name in listed})
        self.assertEqual(len(listed), 9)


#: One statement from the root, across lines when parenthesised or
#: continued with a backslash.
IMPORT = re.compile(
    r'from\s+machinome\.node\s+import\s+'
    r'(\([^)]*\)|(?:[^\n\\]|\\\n)*)')
DOTTED = re.compile(
    r'\bmachinome\.node\.(' + '|'.join(sorted(FORMER, key=len, reverse=True))
    + r')\b')
NAME = re.compile(r'[A-Za-z_]\w*|\*')

SKIPPED_PARTS = frozenset(('__pycache__', '.pytest_cache', '_build',
                           '_exports'))


def imported_names(clause):
    """The names one `import` clause lists, aliases and comments dropped."""
    text = clause.strip()
    if text.startswith('('):
        text = text[1:].rsplit(')', 1)[0]
    text = re.sub(r'#[^\n]*', '', text).replace('\\\n', ' ')
    names = []
    for part in text.split(','):
        match = NAME.match(part.strip())
        if match:
            names.append(match.group(0))
    return names


def offences(text):
    """`[(line, spelling), ...]` for every offence in `text`."""
    found = []
    for match in IMPORT.finditer(text):
        line = text.count('\n', 0, match.start()) + 1
        for name in imported_names(match.group(1)):
            if name in FORMER or name == '*':
                found.append((line, f'from machinome.node import {name}'))
    for match in DOTTED.finditer(text):
        line = text.count('\n', 0, match.start()) + 1
        found.append((line, match.group(0)))
    return found


def in_zone(relative):
    """Whether the file at repository-relative path `relative` is read."""
    parts = relative.split('/')
    if SKIPPED_PARTS & set(parts):
        return False
    if relative == 'README.rst':
        return True
    if parts[0] == 'docs':
        return len(parts) > 1 and parts[1] != 'adrs'
    return parts[0] in ('machinome', 'tests')


def scan(root=ROOT):
    """`{zone: {relative path: [(line, spelling), ...]}}`."""
    result = {'machinome': {}, 'tests': {}, 'docs': {}}
    paths = [*(root / 'machinome').rglob('*'), *(root / 'tests').rglob('*'),
             *(root / 'docs').rglob('*'), root / 'README.rst']
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or not in_zone(relative):
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        found = offences(text)
        if found:
            zone = relative.split('/')[0]
            result['docs' if zone == 'README.rst' else zone][relative] = found
    return result


def report(result):
    lines = []
    for zone, found in result.items():
        total = sum(len(hits) for hits in found.values())
        lines.append(f'{zone}: {len(found)} files, {total} offences')
        for relative, hits in sorted(found.items()):
            first = ', '.join(f'{line}: {spelling}'
                              for line, spelling in hits[:2])
            lines.append(f'  {len(hits):3d} {relative} ({first})')
    return '\n'.join(lines)


class TheRuleTest(TestCase):
    """The scan's self-test: every offending form is found, and what
    passes passes."""

    def test_a_one_line_statement_offends_once_per_name(self):
        text = 'from machinome.node ' 'import AssemblyNode, StepNode\n'
        self.assertEqual([spelling for _, spelling in offences(text)],
                         ['from machinome.node ' 'import AssemblyNode',
                          'from machinome.node ' 'import StepNode'])

    def test_a_parenthesised_statement_offends(self):
        text = ('x = 1\nfrom machinome.node ' 'import (\n'
                '    Frame,  # a comment\n    phase,\n)\n')
        self.assertEqual(offences(text),
                         [(2, 'from machinome.node ' 'import Frame')])

    def test_a_continued_statement_offends(self):
        text = 'from machinome.node ' 'import phase, \\\n    Marking\n'
        self.assertEqual(offences(text),
                         [(1, 'from machinome.node ' 'import Marking')])

    def test_an_aliased_name_offends(self):
        text = 'from machinome.node ' 'import Svg as Artwork\n'
        self.assertEqual(len(offences(text)), 1)

    def test_the_star_import_offends(self):
        text = 'from machinome.node ' 'import *\n'
        self.assertEqual(offences(text),
                         [(1, 'from machinome.node ' 'import *')])

    def test_a_dotted_address_offends(self):
        for text in ('.. autoclass:: machinome.node.' 'Solid2Node\n',
                     "patch('machinome.node." "StepNode')\n"):
            with self.subTest(text=text):
                self.assertEqual(len(offences(text)), 1)

    def test_a_statement_in_prose_or_a_string_offends(self):
        text = ('Write ``from machinome.node ' 'import CadQueryNode``.\n'
                "SOURCE = 'from machinome.node " "import StlNode\\n'\n")
        self.assertEqual(len(offences(text)), 2)

    def test_a_submodule_import_passes(self):
        for text in ('from machinome.node ' 'import supported, phase\n',
                     'from machinome.node.' 'step import StepNode\n',
                     'import machinome.node.' 'assembly\n',
                     'machinome.node.' 'stl.StlNode\n',
                     'from machinome.node ' 'import RotationalPort\n'):
            with self.subTest(text=text):
                self.assertEqual(offences(text), [])

    def test_a_composed_statement_passes(self):
        text = "exec(f'from machinome.node " "import {name}')\n"
        self.assertEqual(offences(text), [])

    def test_the_zones(self):
        self.assertTrue(in_zone('machinome/node/base.py'))
        self.assertTrue(in_zone(
            'machinome/manager/templates/project/root/solid2.py'))
        self.assertTrue(in_zone('tests/meta_project/model.py'))
        self.assertTrue(in_zone('docs/reference/api.rst'))
        self.assertTrue(in_zone('README.rst'))
        self.assertFalse(in_zone('docs/adrs/0169-leaf-types.md'))
        self.assertFalse(in_zone('docs/_build/html/index.html'))
        self.assertFalse(in_zone('tests/_build/x.py'))
        self.assertFalse(in_zone('machinome/__pycache__/x.pyc'))
        self.assertFalse(in_zone('openspec/changes/x/design.md'))
        self.assertFalse(in_zone('workflow/ongoing/lean-core.md'))


class NothingSpellsTheRootTest(TestCase):
    """G2."""

    def test_no_file_of_the_three_zones_spells_a_former_root_name(self):
        result = scan()
        self.assertEqual({zone: sorted(found)
                          for zone, found in result.items()},
                         {'machinome': [], 'tests': [], 'docs': []},
                         '\n' + report(result))
