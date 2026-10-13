# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manual is organised by reader intent, and says where it is going.

These checks pin the shape the user-documentation spec describes: the
navigation sections in order, one tutorial chapter for each stage of the
counter, the release facts defined once, no publication caveat outside
the status page, and every page's declaration of the extras it needs
(change `manual-extras`).
"""

import json
import re
import textwrap
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / 'docs'
# The repository holding the framework's directory (change `monorepo-layout`).
REPOSITORY = Path(__file__).resolve().parents[3]
# The manual's table of extras, beside its extension (change `manual-extras`).
EXTRAS_TABLE = DOCS / '_ext' / 'manual_extras.toml'

CAPTIONS = ['Start', 'Tutorial: a machine that counts', 'How-to guides',
            'How it works', 'Examples', 'Reference', 'Project']

CHAPTERS = ['01-part', '02-input', '03-dimensions', '04-relations',
            '05-buttons', '06-fit', '07-scenario', '08-running',
            '09-clocked', '10-share']

# Phrases that describe an unpublished state. They belong on the status
# page and in release records, never on a page that teaches.
CAVEATS = re.compile(
    r'in preparation|not yet published|awaiting publication|'
    r'release preparation|still unpublished|is unreleased',
    re.IGNORECASE)

ALLOWED_CAVEATS = ('project/status.rst', 'releases/')

# A licence identifier as an SPDX expression spells it: a capitalised name,
# capitalised parts, a version, and a suffix (change `release-0-8-0`). The
# licence of every package of the repository reaches a page only through
# |framework_licence|, so no page spells one, and the README, which Sphinx
# does not build, states it in conf.py's own words (change `join-viewer`).
LICENCE_IDENTIFIER = re.compile(
    r'(?<![\w.-])[A-Z][A-Za-z]*(?:-[A-Z]+)*-\d+\.\d+(?:-or-later|-only|\+)?')

# What the browser viewer's widget declares (change `join-viewer`).
WIDGET = (REPOSITORY / 'packages' / 'machinome-viewer' / 'machinome' / 'viewer'
          / 'web' / 'widget' / 'package.json')

# The real machines are shown on machinome.org; the examples page sends the
# reader there and the manual pins no example repository.
SITE_FOUNDRY = 'https://machinome.org/foundry/'


#: The films' pages (`join-movie`).
FILM_PAGES = ('howto/film-a-movie.rst', 'howto/declare-a-movie.rst',
              'howto/draw-a-movie-stage.rst', 'reference/movie/index.rst',
              'reference/movie/command.rst', 'reference/movie/document.rst',
              'reference/movie/episode.rst')


def documents():
    for rst in sorted(DOCS.rglob('*.rst')):
        relative = rst.relative_to(DOCS).as_posix()
        if relative.startswith('_build'):
            continue
        yield relative, rst.read_text()


class NavigationTest(unittest.TestCase):

    def test_sections_in_order(self):
        index = (DOCS / 'index.rst').read_text()
        captions = re.findall(r':caption:\s*(.+)', index)
        self.assertEqual(captions, CAPTIONS)

    def test_every_chapter_has_a_page_and_a_module(self):
        for chapter in CHAPTERS:
            with self.subTest(chapter=chapter):
                self.assertTrue((DOCS / 'tutorial' / f'{chapter}.rst').is_file())
        modules = sorted(p.stem for p in (DOCS / 'tutorial' / 'counter').glob('c*.py'))
        self.assertEqual(
            [m[:3] for m in modules],
            [f'c{n:02d}' for n in range(1, 10)],
            'one module per chapter that builds a machine; chapter ten '
            'shares the ninth')

    def test_the_examples_are_on_the_site(self):
        page = (DOCS / 'examples.rst').read_text()
        self.assertIn(SITE_FOUNDRY, page)
        for kind in ('posed', 'running', 'clocked'):
            with self.subTest(kind=kind):
                self.assertIn(kind, page)
        self.assertNotIn('.. machinome::', page,
                         'the examples page embeds a model')
        self.assertEqual(sorted(p.name for p in DOCS.glob('example-*.rst')),
                         [], 'an example page exists')
        self.assertFalse((REPOSITORY / '.gitmodules').exists(),
                         'the manual pins a submodule')

    def test_the_freecad_guide_is_a_how_to(self):
        # `join-freecad`: the FreeCAD node package's guide is a how-to, its
        # example imports from the package's address, and it names the
        # runtime it was measured with and the variable that finds it.
        index = (DOCS / 'index.rst').read_text()
        how_to = re.search(r':caption:\s*How-to guides\n\n((?:   \S+\n)+)',
                           index)
        self.assertIsNotNone(how_to, 'index.rst has no How-to toctree')
        self.assertIn('howto/freecad-assemblies', how_to.group(1).split())
        page = (DOCS / 'howto' / 'freecad-assemblies.rst').read_text()
        for spelled in ('from machinome.node.freecad import',
                        'MACHINOME_FREECAD_ROOT', '1.1.4'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, page)

    def test_the_mechanics_helpers_are_a_reference_section_and_a_how_to(self):
        # `join-mechanics`: the mechanics helpers' manual folds in by reader
        # intent, a reference section of a conventions page and the nine
        # formula families, and a how-to.
        index = (DOCS / 'index.rst').read_text()
        for caption, entry in (('How-to guides', 'howto/mechanism-formulas'),
                               ('Reference', 'reference/mechanics/index')):
            with self.subTest(caption=caption):
                toctree = re.search(
                    rf':caption:\s*{caption}\n\n((?:   \S+\n)+)', index)
                self.assertIsNotNone(toctree,
                                     f'index.rst has no {caption} toctree')
                self.assertIn(entry, toctree.group(1).split())
        section = (DOCS / 'reference' / 'mechanics' / 'index.rst').read_text()
        toctree = re.search(r'\.\. toctree::\n(?:   :\S+:.*\n)*\n((?:   \S+\n)+)',
                            section)
        self.assertIsNotNone(toctree, 'the mechanics section has no toctree')
        self.assertEqual(toctree.group(1).split(), [
            'conventions', 'gears', 'screws', 'cranks', 'cams', 'indexing',
            'deltas', 'linkages', 'rolling', 'belts'])

    def test_the_browser_viewer_is_three_how_tos_and_a_reference_section(self):
        # `join-viewer`: the viewer's manual folds in by reader intent, three
        # how-to guides and a reference section.
        index = (DOCS / 'index.rst').read_text()
        for caption, entries in (
                ('How-to guides', ('howto/browser-viewer',
                                   'howto/share-an-export',
                                   'howto/embed-the-viewer')),
                ('Reference', ('reference/viewer/index',))):
            toctree = re.search(
                rf':caption:\s*{caption}\n\n((?:   \S+\n)+)', index)
            self.assertIsNotNone(toctree, f'index.rst has no {caption} toctree')
            for entry in entries:
                with self.subTest(caption=caption, entry=entry):
                    self.assertIn(entry, toctree.group(1).split())
        section = (DOCS / 'reference' / 'viewer' / 'index.rst').read_text()
        toctree = re.search(r'\.\. toctree::\n(?:   :\S+:.*\n)*\n((?:   \S+\n)+)',
                            section)
        self.assertIsNotNone(toctree, 'the viewer section has no toctree')
        self.assertEqual(toctree.group(1).split(), [
            'mount', 'viewer-handle', 'layouts', 'running', 'clocked', 'cli',
            'compatibility', 'troubleshooting'])

    def test_the_skills_guide_is_a_how_to(self):
        # `join-skills`: the skills package's guide is a how-to that installs
        # the skills with the command and names its verbs and options.
        index = (DOCS / 'index.rst').read_text()
        how_to = re.search(r':caption:\s*How-to guides\n\n((?:   \S+\n)+)',
                           index)
        self.assertIsNotNone(how_to, 'index.rst has no How-to toctree')
        self.assertIn('howto/assistant-skills', how_to.group(1).split())
        page = (DOCS / 'howto' / 'assistant-skills.rst').read_text()
        for spelled in ('pip install "machinome[skills]"',
                        'machinome skills install', 'machinome skills update',
                        'machinome skills list', '--tools', '--personal'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, page)

    def test_the_films_are_three_how_tos_and_a_reference_section(self):
        # `join-movie`: the videomaker's manual folds in by reader intent,
        # three how-to guides and a reference section of the command and the
        # two formats.
        index = (DOCS / 'index.rst').read_text()
        for caption, entries in (
                ('How-to guides', ('howto/film-a-movie',
                                   'howto/declare-a-movie',
                                   'howto/draw-a-movie-stage')),
                ('Reference', ('reference/movie/index',))):
            toctree = re.search(
                rf':caption:\s*{caption}\n\n((?:   \S+\n)+)', index)
            self.assertIsNotNone(toctree, f'index.rst has no {caption} toctree')
            for entry in entries:
                with self.subTest(caption=caption, entry=entry):
                    self.assertIn(entry, toctree.group(1).split())
        section = (DOCS / 'reference' / 'movie' / 'index.rst').read_text()
        toctree = re.search(r'\.\. toctree::\n(?:   :\S+:.*\n)*\n((?:   \S+\n)+)',
                            section)
        self.assertIsNotNone(toctree, 'the movie section has no toctree')
        self.assertEqual(toctree.group(1).split(),
                         ['command', 'document', 'episode'])
        page = ' '.join((DOCS / 'howto' / 'film-a-movie.rst').read_text().split())
        for spelled in ('pip install "machinome[movie]"', 'machinome movie setup',
                        'machinome movie setup --remove',
                        'machinome movie check', 'machinome movie preview',
                        'machinome movie render', 'ELEVENLABS_API_KEY'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, page)

    def test_no_page_shows_the_videomaker_s_former_command_lines(self):
        # `join-movie`: a film is made with `machinome movie`, which finds
        # the installed viewer; the changelog's line names the former import.
        # The videomaker's former `--viewer <bundle>` is looked for on the
        # films' pages and on lines of a film's command alone: since
        # `viewer-seam` the snapshot, develop and export commands take a
        # `--viewer` of their own.
        former = ('bin/videomaker.mjs', 'machinome' '_movie')
        for relative, text in documents():
            for spelled in former:
                if relative == 'project/changelog.rst' \
                        and spelled == 'machinome' '_movie':
                    continue
                with self.subTest(document=relative, spelled=spelled):
                    self.assertNotIn(spelled, text)
            films = relative in FILM_PAGES
            for line in text.splitlines():
                if films or 'machinome movie' in line \
                        or 'videomaker' in line:
                    with self.subTest(document=relative, line=line[:60]):
                        self.assertNotIn('--viewer', line)
        changelog = (DOCS / 'project' / 'changelog.rst').read_text()
        self.assertEqual(
            [line for line in changelog.splitlines()
             if 'machinome' '_movie' in line],
            ['  movie is declared with ``machinome.movie`` (formerly '
             '``machinome' '_movie``).'])

    def test_the_studio_is_three_how_tos_and_a_reference_section(self):
        # `join-studio`: the studio's manual folds in by reader intent, three
        # how-to guides and a reference section of what it is, its command,
        # the project configuration, the profiles and troubleshooting.
        index = (DOCS / 'index.rst').read_text()
        for caption, entries in (
                ('How-to guides', ('howto/open-a-studio-project',
                                   'howto/studio-workspace',
                                   'howto/studio-agents')),
                ('Reference', ('reference/studio/index',))):
            toctree = re.search(
                rf':caption:\s*{caption}\n\n((?:   \S+\n)+)', index)
            self.assertIsNotNone(toctree, f'index.rst has no {caption} toctree')
            for entry in entries:
                with self.subTest(caption=caption, entry=entry):
                    self.assertIn(entry, toctree.group(1).split())
        section = (DOCS / 'reference' / 'studio' / 'index.rst').read_text()
        toctree = re.search(r'\.\. toctree::\n(?:   :\S+:.*\n)*\n((?:   \S+\n)+)',
                            section)
        self.assertIsNotNone(toctree, 'the studio section has no toctree')
        self.assertEqual(toctree.group(1).split(),
                         ['command', 'project-configuration', 'profiles',
                          'troubleshooting'])
        page = ' '.join(
            (DOCS / 'howto' / 'open-a-studio-project.rst').read_text().split())
        for spelled in ('pip install "machinome[studio]"',
                        'playwright install chromium',
                        'machinome studio --projects-dir',
                        'npm install -g @fission-ai/openspec'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, page)

    def test_internal_records_are_not_in_the_manual(self):
        for retired in ('expression-graphs.rst', 'flexible-parts.rst',
                        'releases/development-0.7.rst'):
            with self.subTest(retired=retired):
                self.assertFalse((DOCS / retired).exists(), retired)


class KernelExtrasTest(unittest.TestCase):
    """The CAD kernels are extras (OpenSpec changes `lean-install`,
    `mesh-engine` and `brep-mesh`): no page a reader lands on says the
    package carries them, sends a reader to the dissolved adapters package,
    or names an engine by a former name, flag, extra or variable. The
    installation page names every extra and the distribution it installs
    through its rendered list since change `manual-extras`, which
    `tests/test_manual_extras.py` holds for every extra of the manifest."""

    #: The engines' former names (`brep-mesh`), spelled in pieces so this
    #: file's own reading of them is plain.
    FORMER = ('machinome.' 'occt', 'machinome.' 'manifold',
              'exact' '_engine', 'machinome.mesh' '_engine',
              '--' 'faceted', '--' 'exact ', '--' 'exact`',
              'Exact' 'LeafNode', 'machinome[' 'occt]',
              'machinome[' 'manifold]', 'SOLID_TEST_' 'KERNEL')

    #: The FreeCAD node package's module before it joined the repository
    #: (`join-freecad`), the mechanics helpers' module and separate manual
    #: before they joined it (`join-mechanics`), the browser viewer's
    #: separate manual and repository (`join-viewer`), and the studio's
    #: repository, launcher and package before it joined (`join-studio`),
    #: and the viewer's former command, whose verbs are `machinome viewer`'s
    #: (`viewer-command`), spelled in pieces so this file's own reading of
    #: them is plain.
    VIEWER_COMMAND = ('machinome-viewer' ' describe',
                      'machinome-viewer' ' serve',
                      'machinome-viewer' ' capture')
    STALE = ('Everything else comes with the package',
             'machinome.node.adapters', 'machinome' '_freecad',
             'machinome' '_mechanics',
             'machinome-mechanics.readthedocs',
             'machinome-viewer.readthedocs',
             'github.com/machinome/machinome-viewer',
             'github.com/machinome/machinome-studio',
             'machinome-studio --projects-dir', 'python -m floor') + FORMER \
        + VIEWER_COMMAND

    #: The changelog records the dissolution and the released names, and
    #: the upgrading page maps every former name to its new one, the
    #: dissolved adapters' addresses included (change `release-0-8-0`); both
    #: record the mechanics helpers' former module (`join-mechanics`); the
    #: changelog names the studio's former module form (`join-studio`);
    #: both record the viewer's former command (`viewer-command`).
    RECORDS = {'project/changelog.rst': ('machinome.node.adapters',
                                         'machinome' '_mechanics',
                                         'python -m floor') + FORMER
               + VIEWER_COMMAND,
               'project/upgrading.rst': ('machinome.node.adapters',
                                         'machinome' '_mechanics') + FORMER
               + VIEWER_COMMAND}

    def test_no_reader_page_carries_the_kernels_or_the_old_addresses(self):
        pages = list(documents()) + [('README.rst',
                                      (REPO / 'README.rst').read_text())]
        for relative, text in pages:
            for stale in self.STALE:
                if stale in self.RECORDS.get(relative, ()):
                    continue
                with self.subTest(document=relative, stale=stale):
                    self.assertNotIn(stale, text)


class PageExtrasTest(unittest.TestCase):
    """Every page says what it needs (change `manual-extras`, ADR-195).

    Each page but the release notes begins, under its title, with
    `.. needs::` and the extras a reader installs to follow it, or `none`,
    naming extras of the manual's table, `docs/_ext/manual_extras.toml`,
    whose extras are the manifest's a reader installs. A product's
    reference section declares its product's extra, the core's rules and
    records declare `none`, and a teaching page declares at least what its
    code needs. The installation page lists the extras through the
    extension's directive, and its tutorial line names what the tutorial's
    chapters declare. The build refuses the same; these checks fail first.
    """

    #: The extras of the manifest a contributor installs, not a reader.
    CONTRIBUTOR = ('dev', 'docs')

    #: A product's reference section and the extra each of its pages
    #: declares, alone.
    SECTIONS = {'reference/viewer/': 'viewer', 'reference/movie/': 'movie',
                'reference/mechanics/': 'mechanics',
                'reference/studio/': 'studio'}

    #: The core's rules and records, which need the bare framework.
    NONE = ('index.rst', 'why.rst', 'examples.rst', 'start/install.rst',
            'reference/api.rst', 'reference/assertions.rst',
            'reference/cli.rst', 'reference/manuals.rst')
    NONE_SECTIONS = ('concepts/', 'project/')

    #: The pages whose code a reader runs as written.
    TEACHING = ('tutorial/', 'howto/', 'start/first-machine.rst')

    #: The one teaching page held to no derived extra: the guide that
    #: chooses among the node types shows every one of them and names each
    #: one's extra in its table, so its reader installs only the one chosen.
    CHOOSER = 'howto/backends.rst'

    maxDiff = None

    NEEDS = re.compile(r'^\.\. needs::(.*)$', re.M)
    UNDERLINE = re.compile(r'^([=\-~^"\'`#*+_])\1*$')

    #: Where a teaching page shows code: a code directive's body or a
    #: literal block after a paragraph ending `::`, and a file it includes.
    BLOCK = re.compile(
        r'^(?:\.\. (?:code-block|code|doctest|testcode)::.*'
        r'|(?!\.\. ).*::)\n((?:[ \t]*\n|[ \t]+.*\n)+)', re.M)
    INCLUDE = re.compile(r'^\.\. literalinclude:: (\S+)', re.M)
    RELATIVE = re.compile(r'^from \.(\w+) import', re.M)

    @staticmethod
    def pages():
        for relative, text in documents():
            if not relative.startswith('releases/'):
                yield relative, text

    @staticmethod
    def table():
        return tomllib.loads(EXTRAS_TABLE.read_text())

    @classmethod
    def under_title(cls, text):
        """The first non-blank line under the page's title (an overline
        allowed), or None for a page without one."""
        lines = text.split('\n')
        for number, (line, underline) in enumerate(zip(lines, lines[1:])):
            title = line.rstrip()
            if (title and not cls.UNDERLINE.match(title)
                    and cls.UNDERLINE.match(underline)
                    and len(underline) >= len(title)):
                for following in lines[number + 2:]:
                    if following.strip():
                        return following
                return None
        return None

    @classmethod
    def declared(cls, text):
        """The names the declaration under the title gives, as written, or
        None when the first line under the title declares nothing."""
        line = cls.under_title(text)
        found = cls.NEEDS.match(line or '')
        if found is None:
            return None
        return tuple(name.strip() for name in found.group(1).split(','))

    @classmethod
    def declaration(cls, text):
        """The extras the page declares, `()` for `none`."""
        names = cls.declared(text)
        return () if names in (None, ('none',)) else names

    def test_every_page_declares_first_under_its_title(self):
        undeclared = []
        for relative, text in self.pages():
            if (len(self.NEEDS.findall(text)) != 1
                    or self.declared(text) is None):
                undeclared.append(relative)
        self.assertEqual(
            undeclared, [],
            f'{len(undeclared)} pages do not begin, under their title, with '
            'one `.. needs::` and the extras they need, or `none`')

    def test_a_declaration_names_extras_of_the_table(self):
        table = self.table()
        wrong = {}
        for relative, text in self.pages():
            for line in self.NEEDS.findall(text):
                names = [name.strip() for name in line.split(',')]
                if names == ['none']:
                    continue
                unknown = [name for name in names if name not in table]
                if unknown or len(set(names)) != len(names):
                    wrong[relative] = names
        self.assertEqual(wrong, {}, 'a declaration names an extra the '
                         'table lacks, an extra twice, or none with another')

    def test_the_table_is_the_manifest_s(self):
        table = self.table()
        extras = tomllib.loads((REPO / 'pyproject.toml').read_text())[
            'project']['optional-dependencies']
        self.assertEqual(sorted(table),
                         sorted(set(extras) - set(self.CONTRIBUTOR)))
        for name, row in table.items():
            with self.subTest(extra=name):
                self.assertIsInstance(row.get('for'), str)
                self.assertIsInstance(row.get('outside'), list)

    def test_a_product_s_reference_section_declares_its_product(self):
        wrong = {}
        for relative, text in self.pages():
            for section, extra in self.SECTIONS.items():
                if relative.startswith(section) \
                        and self.declared(text) != (extra,):
                    wrong[relative] = self.declared(text)
        self.assertEqual(wrong, {})

    def test_the_core_s_rules_and_records_declare_none(self):
        wrong = {}
        for relative, text in self.pages():
            if relative in self.NONE \
                    or relative.startswith(self.NONE_SECTIONS):
                if self.declared(text) != ('none',):
                    wrong[relative] = self.declared(text)
        self.assertEqual(wrong, {})

    @classmethod
    def module_closure(cls, path, seen):
        """`path` and every module its `from .<module> import` lines reach
        in its directory, each once."""
        if path in seen or not path.is_file():
            return []
        seen.add(path)
        text = path.read_text()
        found = [(path, text)]
        for name in cls.RELATIVE.findall(text):
            found += cls.module_closure(path.parent / f'{name}.py', seen)
        return found

    @classmethod
    def code_of(cls, relative, text):
        """The code a page shows, as (where, code): its blocks, and every
        file it includes with the modules those reach."""
        found = [(relative, ''.join(cls.BLOCK.findall(text)))]
        page = DOCS / relative
        seen = set()
        for target in cls.INCLUDE.findall(text):
            for path, code in cls.module_closure(
                    (page.parent / target).resolve(), seen):
                found.append((path.relative_to(DOCS).as_posix(), code))
        return found

    @staticmethod
    def rules():
        """What code needs: (pattern, extra), the extra None where the
        pattern's group names it."""
        from machinome.node.supported import NODE_TYPES

        command = r'^[ \t]*(?:\$[ \t]*)?machinome {}\b'
        return [
            (re.compile(r'\bmachinome\.node\.({})\b'.format(
                '|'.join(NODE_TYPES))), None),
            (re.compile(r'\bmachinome\.mechanics\b'), 'mechanics'),
            (re.compile(r'\bmachinome\.movie\b'), 'movie'),
            (re.compile(command.format('movie'), re.M), 'movie'),
            (re.compile(command.format('skills'), re.M), 'skills'),
            (re.compile(command.format('studio'), re.M), 'studio'),
            (re.compile(r'\bSvg\('), 'build123d'),
            (re.compile(r'--viewer[ =]web\b'), 'web-snapshot'),
        ]

    @classmethod
    def derived(cls, relative, text):
        """{extra: where} for every extra the page's code needs."""
        needs = {}
        rules = cls.rules()
        for where, code in cls.code_of(relative, text):
            for pattern, extra in rules:
                for found in pattern.finditer(code):
                    needs.setdefault(extra or found.group(1), where)
        return needs

    def test_a_teaching_page_declares_what_its_code_needs(self):
        missing = {}
        for relative, text in self.pages():
            if not relative.startswith(self.TEACHING) \
                    or relative == self.CHOOSER:
                continue
            declared = set(self.declaration(text))
            lacking = {extra: where for extra, where
                       in self.derived(relative, text).items()
                       if extra not in declared}
            if lacking:
                missing[relative] = lacking
        self.assertEqual(
            missing, {}, 'a teaching page does not declare an extra its '
            'code needs ({page: {extra: the file whose code needs it}})')

    def test_the_installation_page_derives_its_list(self):
        page = (DOCS / 'start' / 'install.rst').read_text()
        self.assertTrue('.. _extras:\n\nThe extras\n----------\n' in page,
                        'install.rst has no section "The extras" under the '
                        'label `extras`')
        self.assertEqual(page.count('.. extras::'), 1,
                         'install.rst does not list the extras with one '
                         '`.. extras::`')
        self.assertFalse('list-table' in page,
                         'install.rst keeps a table by hand')

    def test_the_tutorial_s_install_line_names_its_chapters_extras(self):
        page = (DOCS / 'start' / 'install.rst').read_text()
        section = re.search(r'^Install\n-+\n(.*?)(?=^\S[^\n]*\n[-=]+\n|\Z)',
                            page, re.M | re.S)
        self.assertIsNotNone(section, 'install.rst has no Install section')
        line = re.search(r'pip install "machinome\[([^\]]*)\]"',
                         section.group(1))
        self.assertIsNotNone(line, 'the Install section has no install line')
        installed = {name.strip() for name in line.group(1).split(',')}
        declared = set()
        for chapter in CHAPTERS:
            text = (DOCS / 'tutorial' / f'{chapter}.rst').read_text()
            if any(target.startswith('counter/') and target.endswith('.py')
                   for target in self.INCLUDE.findall(text)):
                declared |= set(self.declaration(text))
        self.assertEqual(sorted(installed), sorted(declared),
                         "the tutorial's install line is not the union of "
                         "its chapters' declarations")


def conf_value(name):
    conf = (DOCS / 'conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


class CommandReferenceTest(unittest.TestCase):
    """The command reference documents the commands packages add
    (`join-skills`, `join-movie`, `join-studio`)."""

    #: The movie command's verbs (`join-movie`).
    MOVIE_VERBS = ('list', 'evaluate', 'watch', 'check', 'speech', 'preview',
                   'render', 'build', 'live', 'review', 'setup')

    def setUp(self):
        self.page = (DOCS / 'reference' / 'cli.rst').read_text()

    def section(self, title):
        found = re.search(
            rf'^{re.escape(title)}\n=+\n(.*?)(?=^[^\n]+\n=+\n|\Z)',
            self.page, re.M | re.S)
        self.assertIsNotNone(found, f'cli.rst has no section {title!r}')
        return found.group(1)

    def test_the_skills_command_has_its_section(self):
        self.assertIn('.. _skills-command:\n\nmachinome skills\n', self.page)
        section = self.section('machinome skills')
        for spelled in ('install', 'update', 'list', '--tools', '--personal',
                        '--force'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, section)

    def test_the_skills_package_is_no_longer_to_add_its_command(self):
        section = ' '.join(self.section('Commands from other packages').split())
        self.assertIn('the skills package ``machinome skills``', section)
        self.assertNotIn('the skills package (``machinome skills``)', section)
        self.assertNotIn('no package adds one yet', section)

    def test_the_movie_command_has_its_section(self):
        self.assertIn('.. _movie-command:\n\nmachinome movie\n', self.page)
        section = self.section('machinome movie')
        for verb in self.MOVIE_VERBS:
            with self.subTest(verb=verb):
                self.assertIn(f'machinome movie {verb}', section)
        for spelled in ('--width', '--fps', '--silent', '--port', '--poll',
                        '--open', '--out', '--interval', '--remove',
                        'MACHINOME_NODE', ':doc:`/reference/movie/command`'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, section)

    def test_the_videomaker_is_no_longer_to_add_its_command(self):
        section = ' '.join(self.section('Commands from other packages').split())
        self.assertIn('The movie package adds ``machinome movie``', section)
        self.assertNotIn('videomaker', section)

    def test_the_studio_command_has_its_section(self):
        self.assertIn('.. _studio-command:\n\nmachinome studio\n', self.page)
        section = self.section('machinome studio')
        for spelled in ('machinome studio [--projects-dir PATH] [--port PORT]',
                        '--projects-dir', '--port', 'FLOOR_PORT',
                        'python -m machinome.studio.orchestrator',
                        'python -m machinome.studio',
                        ':doc:`/reference/studio/command`'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, section)

    def test_the_viewer_command_has_its_section(self):
        """`machinome viewer`: the report, the three verbs and every option
        the command's parser declares, read from the parser itself
        (`viewer-command`)."""
        import argparse
        from machinome.manager.viewer import Viewer

        self.assertIn('.. _viewer-command:\n\nmachinome viewer\n', self.page)
        section = self.section('machinome viewer')
        for spelled in ('machinome viewer describe', 'machinome viewer serve',
                        'machinome viewer capture',
                        'python -m machinome.viewer.web',
                        ':doc:`/reference/viewer/cli`'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, section)
        parser = argparse.ArgumentParser(prog='machinome viewer')
        Viewer().add_arguments(parser)
        (verbs,) = [action for action in parser._actions
                    if isinstance(action, argparse._SubParsersAction)]
        self.assertEqual(sorted(verbs.choices),
                         ['capture', 'describe', 'serve'])
        options = {string for verb in verbs.choices.values()
                   for action in verb._actions
                   for string in action.option_strings
                   if string not in ('-h', '--help')}
        self.assertTrue({'--viewer', '--build-dir', '--port', '--output',
                         '--imgsize', '--time', '--view', '--up', '--fov'}
                        <= options, options)
        for option in sorted(options):
            with self.subTest(option=option):
                self.assertIn(option, section)

    def test_the_studio_is_no_longer_to_add_its_command(self):
        section = ' '.join(self.section('Commands from other packages').split())
        self.assertIn('the studio ``machinome studio``', section)
        self.assertNotIn('is to add its own', section)


class ReleaseFactsTest(unittest.TestCase):

    def test_facts_are_substitutions(self):
        conf = (DOCS / 'conf.py').read_text()
        for name in ('release_date', 'viewer_version', 'viewer_api',
                     'document_versions',
                     'framework_licence'):
            with self.subTest(name=name):
                self.assertIn(f'|{name}|', conf)

    def test_the_viewer_facts_are_the_widget_s(self):
        # `join-viewer`: the viewer API and the document versions the manual
        # states are those the widget of the repository declares.
        widget = json.loads(WIDGET.read_text())
        self.assertEqual(conf_value('viewer_api'),
                         str(widget['machinomeViewerApi']))
        versions = widget['machinomeDocumentVersions']
        self.assertEqual(conf_value('document_versions'),
                         f'{versions[0]} to {versions[-1]}')
        self.assertEqual(versions, list(range(versions[0], versions[-1] + 1)))

    def test_no_caveat_outside_the_status_page(self):
        for relative, text in documents():
            if relative.startswith(ALLOWED_CAVEATS):
                continue
            with self.subTest(document=relative):
                found = CAVEATS.search(text)
                if found is not None:
                    self.fail(f'{relative} says {found.group(0)!r}; '
                              'publication state belongs on the status page')


class LicenceFactTest(unittest.TestCase):
    """The framework's licence is one release fact, stated as it is now
    (change `release-0-8-0`): a page states it through |framework_licence|
    and spells no licence identifier, the browser viewer being a package of
    the repository under the same licence (change `join-viewer`); the
    release notes under `docs/releases/` are history and are not read."""

    def test_no_page_spells_a_licence(self):
        for relative, text in documents():
            if relative.startswith('releases/'):
                continue
            with self.subTest(document=relative):
                spelled = set(LICENCE_IDENTIFIER.findall(text))
                self.assertEqual(spelled, set(),
                                 f'{relative} spells a licence literally; '
                                 'the framework\'s is |framework_licence|')

    def test_the_readme_states_the_framework_licence_of_conf(self):
        licence = conf_value('framework_licence')
        readme = ' '.join((REPO / 'README.rst').read_text().split())
        self.assertTrue(licence in readme,
                        f'README.rst does not state {licence!r}')
        admitted = set(LICENCE_IDENTIFIER.findall(licence))
        self.assertEqual(set(LICENCE_IDENTIFIER.findall(readme)) - admitted,
                         set())


class ReadmeTest(unittest.TestCase):
    """The README describes the package, not its releases (change
    `readme-for-readers`): no heading or sentence of it names a version of
    Machinome, and every Python block in it is the verbatim text of a
    tutorial module the suite builds."""

    README = REPO / 'README.rst'
    COUNTER = DOCS / 'tutorial' / 'counter'

    #: A version of Machinome, or of its former name, stated in prose.
    VERSION = re.compile(
        r'(?:Version|Machinome|machinome|solid-node)\s+\d+\.\d')

    @staticmethod
    def headings(text):
        """The section titles: a line whose next line is one punctuation
        character repeated at least to its length."""
        lines = text.split('\n')
        for line, underline in zip(lines, lines[1:]):
            title = line.strip()
            if (title and underline and len(set(underline)) == 1
                    and underline[0] in '=-~^"\'`#*+_'
                    and len(underline) >= len(line.rstrip())):
                yield title

    @staticmethod
    def python_blocks(text):
        """The dedented body of each `.. code-block:: python` directive."""
        blocks = []
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].strip() != '.. code-block:: python':
                i += 1
                continue
            i += 1
            while i < len(lines) and (not lines[i].strip()
                                      or lines[i].startswith('   :')):
                i += 1
            body = []
            while i < len(lines) and (not lines[i] or lines[i][0] == ' '):
                body.append(lines[i])
                i += 1
            blocks.append(textwrap.dedent('\n'.join(body)).strip('\n'))
        return blocks

    #: The README's sections, in order: the title and six more. A section
    #: added, renamed or reordered fails here by name.
    SECTIONS = ['Machinome', "A machine's source", 'What the framework does',
                'Install', 'Documentation', 'Licence', 'Contributing']

    #: The README's size: an addition is a trade for something already there.
    WORDS = 1500

    def test_the_readme_has_these_sections(self):
        headings = list(self.headings(self.README.read_text()))
        self.assertEqual(headings, self.SECTIONS,
                         'README.rst has sections it is not meant to have; '
                         'a fact is edited in place, a section is never added')

    def test_the_readme_fits(self):
        count = len(self.README.read_text().split())
        self.assertLessEqual(
            count, self.WORDS,
            f'README.rst is {count} words; at most {self.WORDS}, so an '
            'addition is a trade for something already there')

    def test_the_readme_names_no_version(self):
        text = self.README.read_text()
        for heading in self.headings(text):
            with self.subTest(heading=heading):
                self.assertIsNone(
                    re.search(r'\d', heading),
                    f'README.rst has a section named {heading!r}; a release '
                    'is recorded in the changelog, the release notes and the '
                    'status page, not in the README')
        found = self.VERSION.search(' '.join(text.split()))
        if found is not None:
            self.fail(f'README.rst says {found.group(0)!r}; the version of '
                      'Machinome belongs on the status page, in the '
                      'changelog and on the upgrading page, which the '
                      'README links')

    def test_the_readme_example_places_parts_by_mates(self):
        blocks = self.python_blocks(self.README.read_text())
        for number, block in enumerate(blocks, 1):
            with self.subTest(block=number):
                self.assertNotIn(
                    'translate(', block,
                    f'Python block {number} of README.rst places a part by '
                    'hand; the example places its parts by frames and mates '
                    '(concepts/joints, "Frames and mates")')
        self.assertTrue(any('.on(' in block for block in blocks),
                        'no Python block of README.rst states a mate; the '
                        'example places its parts by frames and mates')

    def test_the_readme_example_is_tutorial_source(self):
        blocks = self.python_blocks(self.README.read_text())
        self.assertTrue(blocks, "README.rst shows no Python; a machine's "
                                'source is the thing it describes')
        modules = {p.name: p.read_text() for p in self.COUNTER.glob('*.py')}
        for number, block in enumerate(blocks, 1):
            with self.subTest(block=number):
                self.assertTrue(
                    any(block in module for module in modules.values()),
                    f'Python block {number} of README.rst is not the text '
                    'of a module under docs/tutorial/counter/, which the '
                    f'suite builds:\n{block}')


class UpgradingPageTest(unittest.TestCase):
    """The upgrading page's 0.9 part names every move a 0.8 project makes,
    each with what to write instead (change `release-0-9-0`)."""

    MOVES = ('machinome[stl]', 'machinome[jscad]',
             'machinome' '_mechanics', 'machinome.mechanics',
             'machinome' '_viewer', 'machinome.viewer.web',
             'machinome-mechanics', '``--renderer``', '``--viewer``',
             'machinome[viewer-openscad]', 'machinome-viewer describe',
             'machinome viewer describe', 'machinome.viewer',
             'machinome-studio', 'machinome studio', '``floor``',
             'machinome.studio', 'machinome movie', 'machinome[movie]',
             ':ref:`upgrade-viewer-flag`', ':ref:`upgrade-viewer-command`')

    def test_the_0_9_part_names_every_move(self):
        text = (DOCS / 'project' / 'upgrading.rst').read_text()
        start = text.index('Upgrading from Machinome 0.8 to 0.9\n')
        end = text.index('\nUpgrading from Machinome 0.8.0 to 0.8.1\n')
        part = ' '.join(text[start:end].split())
        for spelled in self.MOVES:
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, part)


if __name__ == '__main__':
    unittest.main()
