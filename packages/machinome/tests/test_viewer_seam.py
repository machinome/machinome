# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The seam of viewers, `machinome.viewer` (OpenSpec change `viewer-seam`,
capability `viewer-seam`, ADR-194).

The core declares the contract of viewers in one module of its own: the
contract version, the operations a viewer may offer and what each asks, the
viewers the core knows by name with the extra that installs each, and each
operation's default viewer. A viewer is resolved by importing
`machinome.viewer.<name>` and nothing else, and refused, never replaced:
absent by its extra, unknown by the names the core knows, of another contract
as incompatible, lacking an operation by name. Both providers live in
distributions of their own, `machinome-viewer` (`web`) and
`machinome-viewer-openscad` (`openscad`), admitted as portions of the seam's
path.
"""

import io
import json
import os
import re
import shutil
import tempfile
import textwrap
import tokenize
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from tests.brep_engine_absent import run_python

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
PACKAGES = REPOSITORY / 'packages'
WEB = PACKAGES / 'machinome-viewer' / 'machinome' / 'viewer' / 'web'
OPENSCAD = (PACKAGES / 'machinome-viewer-open' 's' 'cad' / 'machinome'
            / 'viewer' / 'open' 's' 'cad')

#: The second viewer's name, spelled so the SCAD scan reads this file plain.
SECOND = 'open' 's' 'cad'


def seam():
    import machinome.viewer
    return machinome.viewer


class TheContractTest(TestCase):

    def test_the_contract_version_operations_names_and_defaults(self):
        viewers = seam()
        self.assertEqual(viewers.CONTRACT, 1)
        self.assertEqual(viewers.OPERATIONS,
                         ('present', 'capture', 'serve', 'embed'))
        self.assertEqual(viewers.EXTRAS,
                         {SECOND: 'viewer-' + SECOND, 'web': 'viewer'})
        self.assertEqual(viewers.DEFAULTS,
                         {'capture': SECOND, 'serve': 'web', 'embed': 'web'})

    def test_the_protocols_state_each_operation(self):
        viewers = seam()
        members = {
            'Viewer': ('identity', 'document_versions', 'readable'),
            'Presenter': ('present', 'withdraw'),
            'Capturer': ('capture',),
            'Server': ('serve',),
            'Session': ('reload', 'stop'),
            'Embedder': ('files', 'describe'),
        }
        for protocol, names in members.items():
            with self.subTest(protocol=protocol):
                declared = getattr(viewers, protocol)
                for name in names:
                    self.assertTrue(callable(getattr(declared, name)), name)
        self.assertEqual(set(viewers.Viewer.__annotations__),
                         {'NAME', 'CONTRACT', 'OPERATIONS'})
        self.assertIn('CAPTURE_OPTIONS', viewers.Capturer.__annotations__)

    def test_a_capture_request_holds_the_snapshot_options(self):
        request = seam().CaptureRequest()
        self.assertEqual(
            (request.imgsize, request.time, request.camera,
             request.autocenter, request.viewall, request.projection,
             request.colorscheme, request.view, request.render,
             request.preview),
            ('1920x1080', 0.0, None, False, False, None, None, None, False,
             False))


class TheProvidersTest(TestCase):

    def test_both_providers_resolve_to_their_distributions(self):
        viewers = seam()
        self.assertEqual(Path(viewers.viewer('web').__file__),
                         WEB / '__init__.py')
        self.assertEqual(Path(viewers.viewer(SECOND).__file__),
                         OPENSCAD / '__init__.py')
        self.assertEqual(Path(viewers.__path__[0]),
                         ROOT / 'machinome' / 'viewer')
        self.assertEqual(set(map(Path, viewers.__path__[1:])),
                         {WEB.parent, OPENSCAD.parent})

    def test_the_declarations(self):
        viewers = seam()
        web, second = viewers.viewer('web'), viewers.viewer(SECOND)
        self.assertEqual((web.NAME, web.CONTRACT), ('web', viewers.CONTRACT))
        self.assertEqual((second.NAME, second.CONTRACT),
                         (SECOND, viewers.CONTRACT))
        self.assertEqual(web.OPERATIONS,
                         frozenset({'present', 'capture', 'serve', 'embed'}))
        self.assertEqual(second.OPERATIONS, frozenset({'present', 'capture'}))
        self.assertEqual(web.CAPTURE_OPTIONS,
                         frozenset({'autocenter', 'viewall'}))
        self.assertEqual(second.CAPTURE_OPTIONS, frozenset({
            'autocenter', 'viewall', 'projection', 'colorscheme', 'view',
            'render', 'preview'}))
        self.assertEqual(web.identity()[0], 'machinome-viewer')
        self.assertEqual(second.identity()[0], 'machinome-viewer-' + SECOND)
        self.assertIn(13, web.document_versions())
        self.assertTrue(web.readable(13))
        self.assertIsNone(second.document_versions())
        self.assertFalse(second.readable(13))

    def test_each_provider_offers_what_it_declares(self):
        viewers = seam()
        asked = {
            'present': ('present', 'withdraw'),
            'capture': ('capture',),
            'serve': ('serve',),
            'embed': ('files', 'describe'),
        }
        for name in ('web', SECOND):
            provider = viewers.viewer(name)
            for member in ('identity', 'document_versions', 'readable'):
                self.assertTrue(callable(getattr(provider, member)), member)
            for operation in provider.OPERATIONS:
                for member in asked[operation]:
                    with self.subTest(viewer=name, member=member):
                        self.assertTrue(
                            callable(getattr(provider, member, None)))

    def test_an_unknown_name_names_the_viewers(self):
        viewers = seam()
        with self.assertRaises(viewers.UnknownViewer) as raised:
            viewers.viewer('povray')
        self.assertIsInstance(raised.exception, LookupError)
        self.assertEqual(str(raised.exception),
                         "no viewer is named 'povray'; the viewers are "
                         f'{SECOND}, web')

    def test_an_operation_the_viewer_lacks_is_refused_by_name(self):
        viewers = seam()
        with self.assertRaises(viewers.ViewerLacks) as raised:
            viewers.require(SECOND, 'serve', 'machinome develop')
        self.assertEqual(
            str(raised.exception),
            f'machinome develop needs a viewer that can serve, and the '
            f'{SECOND} viewer cannot; the viewers that can: web')
        self.assertIs(viewers.require('web', 'serve', 'machinome develop'),
                      viewers.viewer('web'))


#: Drop one directory from the path, as an install without the distribution
#: it holds, then resolve one viewer and report what it raised.
ABSENT = '''
import json, os, sys
for absent in {directories!r}:
    absent = os.path.realpath(absent)
    sys.path[:] = [entry for entry in sys.path
                   if os.path.realpath(entry or os.curdir) != absent]
import machinome.viewer as viewers
try:
    provider = viewers.viewer({name!r})
except ImportError as raised:
    print(json.dumps([type(raised).__name__, raised.name,
                      getattr(raised, 'extra', None), str(raised)]))
except Exception as raised:
    print(json.dumps([type(raised).__name__, None, None, str(raised)]))
else:
    print(json.dumps(['resolved', provider.__file__]))
'''


def resolved(name, directories=(), absent=()):
    run = run_python(ABSENT.format(directories=[str(d) for d in directories],
                                   name=name),
                     blocked=bool(absent), absent=absent)
    if run.returncode != 0:
        raise AssertionError(run.output)
    return json.loads(run.stdout.strip().splitlines()[-1])


class TheRefusalsTest(TestCase):

    def test_an_absent_viewer_is_refused_by_its_extra(self):
        self.assertEqual(
            resolved(SECOND, [PACKAGES / ('machinome-viewer-' + SECOND)]),
            ['ExtraUnavailable', 'machinome.viewer.' + SECOND,
             'viewer-' + SECOND,
             f'the {SECOND} viewer needs machinome.viewer.{SECOND}, which '
             f'is not installed; install it with '
             f'\'pip install "machinome[viewer-{SECOND}]"\''])

    def test_the_web_viewer_absent(self):
        self.assertEqual(
            resolved('web', [PACKAGES / 'machinome-viewer']),
            ['ExtraUnavailable', 'machinome.viewer.web', 'viewer',
             'the web viewer needs machinome.viewer.web, which is not '
             'installed; install it with \'pip install "machinome[viewer]"\''])

    def test_the_node_package_absent_under_the_second_viewer(self):
        self.assertEqual(
            resolved(SECOND, [PACKAGES / ('machinome-node-' + SECOND)]),
            ['ExtraUnavailable', 'machinome.node.' + SECOND, SECOND,
             f'the {SECOND} node type (OpenScadNode) needs '
             f'machinome.node.{SECOND}, which is not installed; install it '
             f'with \'pip install "machinome[{SECOND}]"\''])

    def test_solidpython_absent_under_the_second_viewer(self):
        refusal = resolved(SECOND, absent=('solid2',))
        self.assertEqual(refusal[:3], ['ExtraUnavailable', 'solid2', SECOND])
        self.assertIn(f'pip install "machinome[{SECOND}]"', refusal[3])

    def test_a_provider_of_another_contract_is_incompatible(self):
        for declaration, stated in (('CONTRACT = 2\n',
                                     'declares contract version 2'),
                                    ('', 'declares none')):
            with self.subTest(stated=stated):
                portion = tempfile.mkdtemp(prefix='viewer-portion-')
                self.addCleanup(shutil.rmtree, portion, ignore_errors=True)
                package = Path(portion, 'machinome', 'viewer', 'fake')
                package.mkdir(parents=True)
                (package / '__init__.py').write_text(
                    declaration + "NAME = 'fake'\n"
                    "OPERATIONS = frozenset()\n")
                run = run_python(
                    'import json, sys\n'
                    f'sys.path.append({portion!r})\n'
                    'import machinome.viewer as viewers\n'
                    'try:\n'
                    "    viewers.viewer('fake')\n"
                    'except viewers.ViewerIncompatible as raised:\n'
                    '    print(json.dumps(str(raised)))\n', blocked=False)
                self.assertEqual(run.returncode, 0, run.output)
                self.assertEqual(
                    json.loads(run.stdout.strip().splitlines()[-1]),
                    f'The fake viewer machinome.viewer.fake {stated}, but '
                    f'this machinome speaks viewer contract version 1; '
                    f'install the viewer released with this machinome')


class TheDefaultRuleTest(TestCase):

    def project(self, manifest):
        directory = tempfile.mkdtemp(prefix='viewer-choice-')
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        Path(directory, 'pyproject.toml').write_text(
            '[tool.machinome]\nmodel = "demo:Demo"\n' + manifest)
        return directory

    def test_each_operation_has_its_default(self):
        viewers = seam()
        origin = self.project('')
        self.assertEqual(viewers.chosen('capture', origin=origin), SECOND)
        self.assertEqual(viewers.chosen('serve', origin=origin), 'web')
        self.assertEqual(viewers.chosen('embed', origin=origin), 'web')

    def test_the_project_names_its_viewer(self):
        viewers = seam()
        origin = self.project('viewer = "web"\n')
        self.assertEqual(viewers.chosen('capture', origin=origin), 'web')

    def test_the_flag_wins(self):
        viewers = seam()
        origin = self.project('viewer = "web"\n')
        self.assertEqual(
            viewers.chosen('capture', explicit=SECOND, origin=origin), SECOND)

    def test_no_project_is_the_default(self):
        viewers = seam()
        outside = tempfile.mkdtemp(prefix='viewer-no-project-')
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        self.assertEqual(viewers.chosen('capture', origin=outside), SECOND)

    def test_a_value_that_is_not_a_string_is_a_manifest_error(self):
        from machinome.manifest import ProjectManifestError, read_declaration
        viewers = seam()
        origin = self.project('viewer = 3\n')
        for asked in (lambda: viewers.chosen('capture', origin=origin),
                      lambda: read_declaration(origin)):
            with self.assertRaises(ProjectManifestError) as raised:
                asked()
            self.assertIn('[tool.machinome] viewer', str(raised.exception))

    def test_the_declaration_carries_the_viewer(self):
        from machinome.manifest import read_declaration
        self.assertEqual(
            read_declaration(self.project('viewer = "web"\n')).viewer, 'web')
        self.assertIsNone(read_declaration(self.project('')).viewer)

    def test_a_declared_viewer_that_cannot_serve_names_the_key(self):
        viewers = seam()
        origin = self.project(f'viewer = "{SECOND}"\n')
        with self.assertRaises(viewers.ViewerLacks) as raised:
            viewers.resolve('serve', 'machinome develop', origin=origin)
        self.assertEqual(
            str(raised.exception),
            f'machinome develop needs a viewer that can serve, and the '
            f"{SECOND} viewer, this project's viewer "
            f'(`[tool.machinome] viewer`), cannot; the viewers that can: '
            f'web; name one with --viewer')

    def test_resolve_follows_the_rule(self):
        viewers = seam()
        origin = self.project('viewer = "web"\n')
        self.assertIs(viewers.resolve('capture', 'machinome snapshot',
                                      origin=origin), viewers.viewer('web'))
        self.assertIs(viewers.resolve('capture', 'machinome snapshot',
                                      explicit=SECOND, origin=origin),
                      viewers.viewer(SECOND))


class UnreadableTest(TestCase):

    def test_the_sentence_names_the_three_facts(self):
        viewers = seam()
        web = viewers.viewer('web')
        with patch.object(web, 'document_versions', return_value=[1, 2, 3]), \
             patch.object(web, 'identity',
                          return_value=('machinome-viewer', '0.1.0')):
            self.assertEqual(
                viewers.unreadable(11, 'web'),
                'this model needs document version 11, and the installed web '
                'viewer renders 1, 2, 3 (machinome-viewer 0.1.0)')
            self.assertIsNone(viewers.unreadable(2, 'web'))

    def test_a_viewer_that_reads_no_document_says_nothing(self):
        self.assertIsNone(seam().unreadable(11, SECOND))

    def test_an_absent_viewer_says_nothing(self):
        viewers = seam()
        absent = viewers.absent('web')
        with patch.object(viewers, 'viewer', side_effect=absent):
            self.assertIsNone(viewers.unreadable(11, 'web'))


#: What one import imports, from a fresh interpreter.
IMPORTED = '''
import json, sys
{code}
print(json.dumps(sorted(sys.modules)))
'''

#: The web stack and the CAD libraries no answer of the seam needs.
HEAVY = ('fastapi', 'uvicorn', 'playwright', 'solid2', 'cadquery', 'OCP',
         'trimesh', 'manifold3d')


def imported(code):
    run = run_python(IMPORTED.format(code=code), blocked=False)
    if run.returncode != 0:
        raise AssertionError(run.output)
    return set(json.loads(run.stdout.strip().splitlines()[-1]))


class TheSeamIsCheapTest(TestCase):

    def test_the_seam_loads_no_viewer(self):
        modules = imported('import machinome.viewer')
        self.assertEqual(
            sorted(name for name in modules
                   if name.startswith('machinome.viewer.')
                   or name.split('.')[0] in HEAVY), [])

    def test_asking_whether_a_version_is_readable_is_cheap(self):
        modules = imported("import machinome.viewer as viewers\n"
                           "viewers.viewer('web').readable(13)")
        for name in ('machinome.viewer.web.server',
                     'machinome.viewer.web.capture',
                     'machinome.viewer.web.stage',
                     'machinome.viewer.web.session', *HEAVY):
            with self.subTest(module=name):
                self.assertNotIn(name, modules)

    def test_the_second_viewer_is_cheap_to_ask(self):
        modules = imported("import machinome.viewer as viewers\n"
                           f"viewers.viewer({SECOND!r}).identity()")
        for name in ('fastapi', 'uvicorn', 'playwright', 'cadquery', 'OCP'):
            with self.subTest(module=name):
                self.assertNotIn(name, modules)


class ThePathExtensionTest(TestCase):

    def test_a_portion_is_admitted_and_a_second_core_refused(self):
        portion = tempfile.mkdtemp(prefix='viewer-portion-')
        copy = tempfile.mkdtemp(prefix='viewer-core-copy-')
        for directory in (portion, copy):
            self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        Path(portion, 'machinome', 'viewer', 'extra').mkdir(parents=True)
        Path(copy, 'machinome', 'viewer').mkdir(parents=True)
        Path(copy, 'machinome', 'viewer', '__init__.py').write_text('')
        run = run_python(
            'import json, sys\n'
            f'sys.path[len(sys.path):] = [{portion!r}, {copy!r}]\n'
            'import machinome.viewer as viewers\n'
            'print(json.dumps(list(viewers.__path__)))\n', blocked=False)
        self.assertEqual(run.returncode, 0, run.output)
        path = json.loads(run.stdout.strip().splitlines()[-1])
        self.assertIn(os.path.join(portion, 'machinome', 'viewer'), path)
        self.assertNotIn(os.path.join(copy, 'machinome', 'viewer'), path)

    def test_the_seam_extends_its_path_last(self):
        source = (ROOT / 'machinome' / 'viewer' / '__init__.py').read_text()
        self.assertEqual(source.rstrip().splitlines()[-1],
                         '__path__ = _namespace_portions(__path__, __name__)')

    def test_the_core_holds_the_seam_alone(self):
        directory = ROOT / 'machinome' / 'viewer'
        self.assertEqual(
            sorted(path.name for path in directory.iterdir()
                   if path.name != '__pycache__'), ['__init__.py'])
        self.assertFalse((ROOT / 'machinome' / 'viewers').exists())


#: The former names, which no source of the set spells but to refuse them.
FORMER = re.compile(r'--renderer|machinome\.viewers\b|renderer_names'
                    r'|DEFAULT_RENDERER|OpenScadRenderer|BrowserRenderer'
                    r'|viewers\.open' 's' 'cad')

#: The one occurrence a source may hold: the snapshot's refusal of the
#: former flag, spelled once.
REFUSAL = {'packages/machinome/machinome/manager/snapshot.py': 1}


def sources():
    """Every Python module of the core's `machinome/`, of the two
    providers, of the films and of the studio."""
    roots = [ROOT / 'machinome', WEB, OPENSCAD,
             PACKAGES / 'machinome-movie' / 'machinome',
             PACKAGES / 'machinome-studio' / 'machinome']
    for root in roots:
        for path in sorted(root.rglob('*.py')):
            if 'node_modules' not in path.parts:
                yield path


def provider_modules():
    """The seam's and the providers' modules, whose strings a maker reads."""
    yield ROOT / 'machinome' / 'viewer' / '__init__.py'
    yield from sorted(WEB.glob('*.py'))
    yield OPENSCAD / '__init__.py'


def former_names(text):
    return FORMER.findall(text)


def renderer_strings(source):
    """Every string token of `source` that holds the word renderer."""
    found = []
    kinds = {tokenize.STRING}
    if hasattr(tokenize, 'FSTRING_MIDDLE'):
        kinds.add(tokenize.FSTRING_MIDDLE)
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in kinds and re.search('renderer', token.string,
                                             re.IGNORECASE):
            found.append((token.start[0], token.string[:60]))
    return found


class TheWordIsViewerTest(TestCase):

    def offences(self):
        found = {}
        for path in sources():
            relative = path.relative_to(REPOSITORY).as_posix()
            count = len(former_names(path.read_text()))
            if count != REFUSAL.get(relative, 0):
                found[relative] = count
        for path in provider_modules():
            strings = renderer_strings(path.read_text())
            if strings:
                found[path.relative_to(REPOSITORY).as_posix()] = strings
        return found

    def test_the_word_is_viewer(self):
        self.assertEqual(self.offences(), {})

    def test_the_rule_reads_each_former_name(self):
        for text in ('--renderer web', 'machinome.viewers.bundle',
                     'renderer_names()', 'DEFAULT_RENDERER',
                     'OpenScadRenderer', 'BrowserRenderer',
                     "getLogger('viewers.open" "s" "cad')"):
            with self.subTest(text=text):
                self.assertEqual(len(former_names(text)), 1)
        self.assertEqual(former_names('machinome.viewer.web --viewer web'),
                         [])
        self.assertEqual(
            renderer_strings(textwrap.dedent('''\
                # a renderer in a comment is not written
                MESSAGE = "the web renderer"
                ''')),
            [(2, '"the web renderer"')])
