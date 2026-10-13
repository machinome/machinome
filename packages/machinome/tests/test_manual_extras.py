# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manual's own extension, `docs/_ext/manual_extras.py` (change
`manual-extras`, ADR-195).

`.. needs::`, the first thing under a page's title, renders the line that
names what the page needs, or nothing for `none`; `.. extras::` renders the
installation page's list of every extra the framework's manifest declares,
with the distributions it installs, what it is for, what it needs outside
pip and the pages that need it. The build refuses an undeclared page, a
declaration that is wrong or misplaced, and a table of extras that is not
the manifest's.

The tests build small Sphinx projects in a temporary directory with the
extension, its table and the framework's real manifest, and read the
resolved doctrees, where the HTML would split each literal into spans. The
installation page's list holds what the page's source once spelled by hand
(`KernelExtrasTest` before this change): every extra, the distributions
they install, and the movie's and the studio's second steps.
"""

import ast
import inspect
import io
import re
import shutil
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

try:
    from docutils import nodes
    from sphinx.testing.util import SphinxTestApp
    HAS_SPHINX = True
except ImportError:
    HAS_SPHINX = False

REPO = Path(__file__).resolve().parent.parent
EXTENSION = REPO / 'docs' / '_ext'
MODULE = EXTENSION / 'manual_extras.py'
TABLE = EXTENSION / 'manual_extras.toml'
MANIFEST = REPO / 'pyproject.toml'
CONTRIBUTOR = ('dev', 'docs')

CONF = """\
import sys
sys.path.insert(0, {extension!r})
extensions = ['manual_extras']
manual_extras_manifest = {manifest!r}
manual_extras_exempt = ['releases/*']
nitpicky = True
"""

INDEX = """\
Index
=====

.. needs:: none

.. toctree::

{entries}
"""

INSTALL = """\
Install
=======

.. needs:: none

.. _extras:

The extras
----------

.. extras::
"""

FILM = """\
============
Film a movie
============

.. needs:: movie

Make a film.
"""

PARTS = """\
.. _parts:

Model parts
===========

.. needs:: cadquery, viewer

Model a part.
"""

RULE = """\
A rule
======

.. needs:: none

A rule of the framework.
"""


def manifest_extras(path=MANIFEST):
    return tomllib.loads(path.read_text())['project']['optional-dependencies']


def plain(phrase):
    """An inline reST phrase of the table as a doctree's text reads it."""
    phrase = re.sub(r'`([^`<]*?)\s*<[^>]*>`_', r'\1', phrase)
    return phrase.replace('``', '')


def straight(text):
    """`text` with the curly quotes docutils' smart quotes write."""
    return text.translate(str.maketrans('\u2018\u2019\u201c\u201d', "''\"\""))


@unittest.skipUnless(HAS_SPHINX, 'sphinx not installed')
class ManualExtrasTest(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.srcdir = self.root / 'source'
        self.srcdir.mkdir()

    @property
    def table(self):
        return tomllib.loads(TABLE.read_text())

    def build(self, pages, manifest=MANIFEST):
        """Builds `pages` ({docname: source}, an index listing them
        added), returning the warnings and {docname: resolved doctree}."""
        (self.srcdir / 'conf.py').write_text(CONF.format(
            extension=str(EXTENSION), manifest=str(manifest)))
        entries = '\n'.join(f'   {name}' for name in pages)
        (self.srcdir / 'index.rst').write_text(INDEX.format(entries=entries))
        for name, source in pages.items():
            path = self.srcdir / f'{name}.rst'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source)
        warnings = io.StringIO()
        app = SphinxTestApp(srcdir=self.srcdir, builddir=self.root / 'build',
                            status=io.StringIO(), warning=warnings)
        try:
            app.build()
            # The build's tags, which Sphinx 11 requires and earlier
            # releases do not take.
            resolve = app.env.get_and_resolve_doctree
            tags = ({'tags': app.tags} if 'tags' in
                    inspect.signature(resolve).parameters else {})
            doctrees = {name: resolve(name, app.builder, **tags)
                        for name in ['index', *pages]}
        finally:
            app.cleanup()
        return warnings.getvalue(), doctrees

    def declared_project(self):
        return self.build({'start/install': INSTALL, 'howto/film': FILM,
                           'howto/parts': PARTS, 'concepts/rule': RULE})

    @staticmethod
    def text(doctree):
        return ' '.join(doctree.astext().split())

    @staticmethod
    def entries(doctree):
        """{term: definition text} of the installation page's list."""
        found = {}
        for item in doctree.findall(nodes.definition_list_item):
            term = item.next_node(nodes.term).astext()
            found[term] = straight(' '.join(
                item.next_node(nodes.definition).astext().split()))
        return found

    @staticmethod
    def needs_line(doctree):
        """The text of the line under the title, or None."""
        boxes = [node for node in doctree.findall(nodes.container)
                 if 'machinome-needs' in node['classes']]
        return straight(' '.join(boxes[0].astext().split())) if boxes \
            else None

    def reader_extras(self):
        return [name for name in manifest_extras()
                if name not in CONTRIBUTOR]

    def outside(self, *extras):
        """The outside-pip phrases of `extras`, members of an extra that
        names other extras of the framework included, each once."""
        members = {}
        for name, requirements in manifest_extras().items():
            for line in requirements:
                found = re.fullmatch(r'machinome\[([^\]]*)\]', line)
                if found:
                    members[name] = [m.strip()
                                     for m in found.group(1).split(',')]
        phrases = []
        table = self.table
        for name in extras:
            named = sorted(members.get(name, ()), key=list(table).index)
            for member in [name, *named]:
                phrases += table[member]['outside']
        return list(dict.fromkeys(plain(phrase) for phrase in phrases))

    # What it renders.

    def test_a_declared_project_builds_without_a_warning(self):
        warnings, _doctrees = self.declared_project()
        self.assertEqual(warnings, '')

    def test_the_list_names_every_reader_extra_and_what_it_installs(self):
        _warnings, doctrees = self.declared_project()
        entries = self.entries(doctrees['start/install'])
        self.assertEqual(list(entries),
                         [f'machinome[{name}]' for name in self.table])
        for name in self.reader_extras():
            with self.subTest(extra=name):
                entry = entries[f'machinome[{name}]']
                for line in manifest_extras()[name]:
                    found = re.fullmatch(
                        r'([A-Za-z0-9._-]+)(?:\[([^\]]*)\])?.*', line)
                    distribution, extras = found.group(1), found.group(2)
                    if distribution == 'machinome':
                        for member in extras.split(','):
                            self.assertIn(member.strip(), entry)
                    else:
                        self.assertIn(distribution, entry)
                        for extra in (extras or '').split(','):
                            self.assertIn(extra.strip(), entry)
                self.assertIn(plain(self.table[name]['for']), entry)
                for phrase in self.outside(name):
                    self.assertIn(phrase, entry)

    def test_the_list_names_the_second_steps(self):
        # The movie's and the studio's install steps, and FreeCAD's and the
        # jscad command's, which the installation page once wrote out.
        _warnings, doctrees = self.declared_project()
        entries = self.entries(doctrees['start/install'])
        for name, spelled in (
                ('movie', ('machinome movie setup', 'Node 22', 'FFmpeg',
                           'Chromium')),
                ('studio', ('playwright install chromium', 'OpenSpec',
                            'agent backend')),
                ('web-snapshot', ('machinome-viewer', 'snapshot',
                                  'playwright install chromium')),
                ('freecad', ('MACHINOME_FREECAD_ROOT', '1.1.4')),
                ('jscad', ('the jscad command',)),
                ('all', ('cadquery', 'freecad', 'the jscad command'))):
            for phrase in spelled:
                with self.subTest(extra=name, spelled=phrase):
                    self.assertIn(phrase, entries[f'machinome[{name}]'])

    def test_an_aggregate_extra_lists_its_members_steps_in_table_order(self):
        _warnings, doctrees = self.declared_project()
        entry = self.entries(doctrees['start/install'])['machinome[all]']
        self.assertIn('Outside pip: ' + '; '.join(self.outside('all')) + '.',
                      entry)

    def test_the_list_names_the_pages_that_need_each_extra(self):
        _warnings, doctrees = self.declared_project()
        entries = self.entries(doctrees['start/install'])
        self.assertTrue(entries['machinome[movie]'].endswith(
            'Needed by Film a movie.'), entries['machinome[movie]'])
        self.assertTrue(entries['machinome[viewer]'].endswith(
            'Needed by Model parts.'), entries['machinome[viewer]'])
        self.assertNotIn('Needed by', entries['machinome[studio]'])

    def test_the_list_names_the_tutorial_and_a_section_once(self):
        chapter = 'Chapter {n}\n=========\n\n.. needs:: viewer\n'
        section = 'Section {n}\n=========\n\n.. needs:: viewer\n'
        _warnings, doctrees = self.build({
            'start/install': INSTALL,
            'tutorial/01-part': chapter.format(n=1),
            'tutorial/02-input': chapter.format(n=2),
            'reference/viewer/index': 'Viewer\n======\n\n'
                                      '.. needs:: viewer\n',
            'reference/viewer/mount': section.format(n=1),
            'howto/parts': PARTS})
        entries = self.entries(doctrees['start/install'])
        self.assertTrue(entries['machinome[viewer]'].endswith(
            'Needed by Model parts, Viewer and the tutorial.'),
            entries['machinome[viewer]'])
        self.assertTrue(entries['machinome[cadquery]'].endswith(
            'Needed by Model parts.'), entries['machinome[cadquery]'])

    def test_the_movie_page_shows_its_line(self):
        _warnings, doctrees = self.declared_project()
        self.assertEqual(
            self.needs_line(doctrees['howto/film']),
            'Needs pip install "machinome[movie]", and outside pip: '
            + '; '.join(self.outside('movie')) + '.')

    def test_a_line_names_the_extras_in_the_table_s_order(self):
        _warnings, doctrees = self.declared_project()
        names = [name for name in self.table if name in ('viewer',
                                                         'cadquery')]
        self.assertEqual(
            self.needs_line(doctrees['howto/parts']),
            f'Needs pip install "machinome[{",".join(names)}]".')

    def test_the_line_comes_first_and_links_the_list(self):
        _warnings, doctrees = self.declared_project()
        section = doctrees['howto/film'].next_node(nodes.section)
        first = section.children[1]
        self.assertIn('machinome-needs', first['classes'])
        reference = first.next_node(nodes.reference)
        self.assertEqual(reference.astext(), 'Needs')
        self.assertEqual(reference['refuri'], '../start/install.html#extras')

    def test_none_renders_nothing(self):
        _warnings, doctrees = self.declared_project()
        self.assertIsNone(self.needs_line(doctrees['concepts/rule']))
        self.assertNotIn('Needs', self.text(doctrees['concepts/rule']))

    # What it refuses.

    def refused(self, source, name='howto/wrong'):
        warnings, _doctrees = self.build({'start/install': INSTALL,
                                          name: source})
        return warnings

    def test_an_undeclared_page_warns_naming_it(self):
        warnings = self.refused('Wrong\n=====\n\nNo declaration.\n')
        self.assertRegex(warnings, r'howto/wrong(\.rst)?: WARNING: the page '
                                   r'declares no extra')

    def test_a_wrong_declaration_is_an_error_naming_its_page_and_line(self):
        for argument, said in (('viewr', 'viewr is not an extra'),
                               ('none, viewer', 'none is not an extra'),
                               ('viewer, viewer', 'viewer is named twice')):
            with self.subTest(argument=argument):
                warnings = self.refused(
                    f'Wrong\n=====\n\n.. needs:: {argument}\n')
                self.assertRegex(warnings, r'howto/wrong\.rst:4: ERROR: '
                                           rf'needs: {said}')

    def test_a_misplaced_declaration_is_an_error_naming_its_page_and_line(
            self):
        for source, line in (
                ('Wrong\n=====\n\nA paragraph.\n\n.. needs:: viewer\n', 6),
                ('Wrong\n=====\n\n.. needs:: viewer\n\n.. needs:: movie\n',
                 6),
                ('Wrong\n=====\n\nA paragraph.\n\nSection\n-------\n\n'
                 '.. needs:: viewer\n', 9)):
            with self.subTest(line=line):
                warnings = self.refused(source)
                self.assertRegex(warnings,
                                 rf'howto/wrong\.rst:{line}: ERROR: needs: '
                                 'the declaration is the first thing')

    def test_a_manifest_extra_the_table_lacks_warns_naming_both_sets(self):
        manifest = self.root / 'pyproject.toml'
        text = MANIFEST.read_text()
        heading = '[project.optional-dependencies]\n'
        self.assertIn(heading, text)
        manifest.write_text(text.replace(
            heading, heading + 'teleport = ["machinome-teleport"]\n'))
        warnings, _doctrees = self.build({'start/install': INSTALL},
                                         manifest=manifest)
        self.assertIn("WARNING: the manual's table of extras", warnings)
        self.assertIn("'teleport'", warnings)
        self.assertIn("'studio'", warnings)

    def test_a_table_extra_the_manifest_lacks_warns_naming_both_sets(self):
        manifest = self.root / 'pyproject.toml'
        text = MANIFEST.read_text()
        removed = re.sub(r'(?m)^studio = \[\n(?:.*\n)*?\]\n', '', text)
        self.assertNotEqual(removed, text)
        manifest.write_text(removed)
        warnings, _doctrees = self.build({'start/install': INSTALL},
                                         manifest=manifest)
        self.assertIn("WARNING: the manual's table of extras", warnings)
        self.assertIn("'studio'", warnings)

    # What it is made of.

    def test_the_extension_imports_only_sphinx_docutils_and_packaging(self):
        tree = ast.parse(MODULE.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split('.')[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module.split('.')[0])
        allowed = {'sphinx', 'docutils', 'packaging'} \
            | set(sys.stdlib_module_names)
        self.assertEqual(imported - allowed, set())


if __name__ == '__main__':
    unittest.main()
