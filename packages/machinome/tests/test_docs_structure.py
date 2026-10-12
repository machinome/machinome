# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manual is organised by reader intent, and says where it is going.

These checks pin the shape the user-documentation spec describes: the
navigation sections in order, one tutorial chapter for each stage of the
counter, the release facts defined once, and no publication caveat outside
the status page.
"""

import re
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / 'docs'
# The repository holding the framework's directory (change `monorepo-layout`).
REPOSITORY = Path(__file__).resolve().parents[3]

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

# The viewer grants AGPL-3.0-or-later (25 September 2026). Nothing the manual
# describes is licensed version-3-only, so the spelling is a stale fact.
STALE_GRANT = 'AGPL-3.0-only'

# A licence identifier as an SPDX expression spells it: a capitalised name,
# capitalised parts, a version, and a suffix (change `release-0-8-0`). The
# framework's licence reaches a page only through |framework_licence|, so
# the one identifier a page may spell is the viewer's, and the README, which
# Sphinx does not build, states the framework's in conf.py's own words.
LICENCE_IDENTIFIER = re.compile(
    r'(?<![\w.-])[A-Z][A-Za-z]*(?:-[A-Z]+)*-\d+\.\d+(?:-or-later|-only|\+)?')
VIEWER_LICENCE = 'AGPL-3.0-or-later'

# The real machines are shown on machinome.org; the examples page sends the
# reader there and the manual pins no example repository.
SITE_FOUNDRY = 'https://machinome.org/foundry/'


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

    def test_internal_records_are_not_in_the_manual(self):
        for retired in ('expression-graphs.rst', 'flexible-parts.rst',
                        'releases/development-0.7.rst'):
            with self.subTest(retired=retired):
                self.assertFalse((DOCS / retired).exists(), retired)


class LicenceWordingTest(unittest.TestCase):

    def test_no_page_names_the_old_viewer_grant(self):
        pages = list(documents()) + [('README.rst', (REPO / 'README.rst').read_text())]
        for relative, text in pages:
            with self.subTest(document=relative):
                self.assertNotIn(STALE_GRANT, text)


class KernelExtrasTest(unittest.TestCase):
    """The CAD kernels are extras (OpenSpec changes `lean-install`,
    `mesh-engine` and `brep-mesh`): the installation page names each, and
    no page a reader lands on says the package carries them, sends a reader
    to the dissolved adapters package, or names an engine by a former name,
    flag, extra or variable."""

    EXTRAS = ('brep', 'mesh', 'cadquery', 'build123d', 'step', 'molejo',
              'jscad', 'stl', 'freecad', 'all')

    #: The engines' former names (`brep-mesh`), spelled in pieces so this
    #: file's own reading of them is plain.
    FORMER = ('machinome.' 'occt', 'machinome.' 'manifold',
              'exact' '_engine', 'machinome.mesh' '_engine',
              '--' 'faceted', '--' 'exact ', '--' 'exact`',
              'Exact' 'LeafNode', 'machinome[' 'occt]',
              'machinome[' 'manifold]', 'SOLID_TEST_' 'KERNEL')

    #: The FreeCAD node package's module before it joined the repository
    #: (`join-freecad`), and the mechanics helpers' module and separate
    #: manual before they joined it (`join-mechanics`).
    STALE = ('Everything else comes with the package',
             'machinome.node.adapters', 'machinome' '_freecad',
             'machinome' '_mechanics',
             'machinome-mechanics.readthedocs') + FORMER

    #: The changelog records the dissolution and the released names, and
    #: the upgrading page maps every former name to its new one, the
    #: dissolved adapters' addresses included (change `release-0-8-0`); both
    #: record the mechanics helpers' former module (`join-mechanics`).
    RECORDS = {'project/changelog.rst': ('machinome.node.adapters',
                                         'machinome' '_mechanics') + FORMER,
               'project/upgrading.rst': ('machinome.node.adapters',
                                         'machinome' '_mechanics') + FORMER}

    def test_the_installation_page_names_every_kernel_extra(self):
        page = (DOCS / 'start' / 'install.rst').read_text()
        for extra in self.EXTRAS:
            with self.subTest(extra=extra):
                self.assertIn(f'machinome[{extra}]', page)

    def test_the_installation_page_names_the_extension_distributions(self):
        # `cut-the-engines`: the `brep` and `mesh` extras install the
        # engines' own distributions; `cut-the-brep-nodes`: the `cadquery`,
        # `build123d`, `step` and `molejo` extras the node packages';
        # `cut-the-mesh-nodes`: the `openscad`, `solid2`, `jscad` and `stl`
        # extras theirs; `join-freecad`: the `freecad` extra the FreeCAD node
        # package; `join-mechanics`: the `mechanics` extra the mechanics
        # helpers; `join-skills`: the `skills` extra the skills package.
        page = (DOCS / 'start' / 'install.rst').read_text()
        for distribution in ('machinome-engine-brep', 'machinome-engine-mesh',
                             'machinome-node-cadquery',
                             'machinome-node-build123d',
                             'machinome-node-step', 'machinome-node-molejo',
                             'machinome-node-openscad',
                             'machinome-node-solid2',
                             'machinome-node-jscad', 'machinome-node-stl',
                             'machinome-node-freecad', 'machinome-mechanics',
                             'machinome-skills'):
            with self.subTest(distribution=distribution):
                self.assertIn(distribution, page)

    def test_no_reader_page_carries_the_kernels_or_the_old_addresses(self):
        pages = list(documents()) + [('README.rst',
                                      (REPO / 'README.rst').read_text())]
        for relative, text in pages:
            for stale in self.STALE:
                if stale in self.RECORDS.get(relative, ()):
                    continue
                with self.subTest(document=relative, stale=stale):
                    self.assertNotIn(stale, text)


def conf_value(name):
    conf = (DOCS / 'conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


class CommandReferenceTest(unittest.TestCase):
    """The command reference documents the commands packages add
    (`join-skills`)."""

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
        self.assertIn('The skills package adds ``machinome skills``', section)
        self.assertNotIn('the skills package (``machinome skills``)', section)
        self.assertNotIn('no package adds one yet', section)


class ReleaseFactsTest(unittest.TestCase):

    def test_facts_are_substitutions(self):
        conf = (DOCS / 'conf.py').read_text()
        for name in ('release_date', 'viewer_version', 'viewer_api',
                     'document_versions', 'mechanics_version',
                     'framework_licence'):
            with self.subTest(name=name):
                self.assertIn(f'|{name}|', conf)

    def test_the_mechanics_version_is_the_package_s(self):
        # `join-mechanics`: the mechanics helpers carry their own version,
        # which the manual states once.
        manifest = (REPOSITORY / 'packages' / 'machinome-mechanics'
                    / 'pyproject.toml').read_text()
        version = re.search(r'^version = "([^"]*)"', manifest, flags=re.M)[1]
        self.assertEqual(conf_value('mechanics_version'), version)

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
    and spells no licence identifier but the viewer's; the release notes
    under `docs/releases/` are history and are not read."""

    def test_no_page_spells_a_licence_but_the_viewers(self):
        for relative, text in documents():
            if relative.startswith('releases/'):
                continue
            with self.subTest(document=relative):
                spelled = set(LICENCE_IDENTIFIER.findall(text)) - {VIEWER_LICENCE}
                self.assertEqual(spelled, set(),
                                 f'{relative} spells a licence literally; '
                                 'the framework\'s is |framework_licence|')

    def test_the_readme_states_the_framework_licence_of_conf(self):
        licence = conf_value('framework_licence')
        readme = ' '.join((REPO / 'README.rst').read_text().split())
        self.assertTrue(licence in readme,
                        f'README.rst does not state {licence!r}')
        admitted = {VIEWER_LICENCE, *LICENCE_IDENTIFIER.findall(licence)}
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


if __name__ == '__main__':
    unittest.main()
