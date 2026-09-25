# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

import ast
import inspect
import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from machinome_viewer import bundle


class BundleLookupTest(TestCase):

    def test_the_lookup_imports_only_the_standard_library(self):
        tree = ast.parse(inspect.getsource(bundle))
        imports = {node.names[0].name for node in ast.walk(tree)
                   if isinstance(node, ast.Import)}
        froms = {node.module for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {'json'})
        # `machinome_viewer.currency` joins the set with ADR-059: the
        # lookup makes the bundle current before it reads the declaration.
        # That module imports only the standard library too, which
        # `tests/test_currency.py` asserts of it directly, so the promise
        # this test exists for -- resolving the entry point costs no
        # browser bundle and no web framework -- is unchanged.
        self.assertTrue(froms <= {'pathlib', 'importlib.metadata',
                                  'machinome_viewer',
                                  'machinome_viewer.currency'},
                        froms)

    def test_declares_api_version_fifteen(self):
        # OpenSpec `draw-what-a-part-carries`, design D9: drawing a
        # document's markings is a capability a host may require, so the
        # declared version moves to 14. 13 is skipped deliberately --
        # the in-flight `slide-and-turn-parts` cycle claims it.
        # OpenSpec `execute-the-self-read`, design D6: executing a
        # version 6 document -- a law that reads the coordinate it
        # drives -- is the next such capability, and unlike `controls`
        # and `markings` it is NOT additive, so the document list moves
        # with it.
        # Executing a version 7 document -- a compiled program some of
        # whose law edges form a BLOCK, ordered per PIECE of a tick from
        # the published edges rather than run in the published listing --
        # is the one after that, and it is not additive either.
        # Executing a version 8 document -- a root that declares a
        # `State`, whose document carries a compiled CLOCKED machine
        # instead of a program -- is the one after that (OpenSpec
        # `execute-the-commit`), and it is not additive either.
        # Advancing that machine's CLOCK (OpenSpec `run-the-clock`) is
        # the one after that, and PLAYING one of its declared
        # INSTRUCTIONS -- one request solved before the first frame and
        # its transition drawn over the declared duration, where a build
        # at 18 lists the same button and refuses it (OpenSpec
        # `play-the-instruction`) -- is the one after that.
        self.assertEqual(bundle.api_version(), 27)

    def test_declares_the_document_versions_this_build_reads(self):
        self.assertEqual(bundle.document_versions(),
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    def test_the_released_floor_does_not_move_with_the_build(self):
        # `RELEASED_DOCUMENT_VERSIONS` is what a viewer that PREDATES
        # the declaration is entitled to be assumed to read. It is
        # a floor for builds without the key, not a mirror of this one.
        self.assertEqual(bundle.RELEASED_DOCUMENT_VERSIONS, [1, 2, 3, 4])
        self.assertNotEqual(bundle.RELEASED_DOCUMENT_VERSIONS,
                            bundle.document_versions())

    def test_describe_reports_the_packages_own_document_versions(self):
        # `describe()` reads the package's ONE declaration, so a
        # framework asking this build what it renders is told the list
        # the bundle actually refuses by -- version 7 included.
        described = bundle.describe()
        self.assertEqual(described['documentVersions'],
                         bundle.document_versions())
        self.assertEqual(described['documentVersions'],
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        self.assertEqual(described['apiVersion'], bundle.api_version())

    def test_paths_and_remedy_share_one_source(self):
        self.assertTrue(str(bundle.bundle_path()).endswith('widget/dist/machinome-viewer.js'))
        self.assertTrue(str(bundle.index_path()).endswith('widget/index.html'))
        self.assertTrue(str(bundle.develop_page_path()).endswith('widget/develop.html'))
        remedy = bundle.missing_bundle_remedy()
        self.assertIn('npm', remedy)
        self.assertIn('PyPI', remedy)

    def test_api_version_is_read_from_the_package_declaration(self):
        with tempfile.TemporaryDirectory() as root:
            package = os.path.join(root, 'package.json')
            with open(package, 'w') as stream:
                json.dump({'machinomeViewerApi': 7,
                           'machinomeDocumentVersions': [1, 2]}, stream)
            with patch.object(bundle, 'PACKAGE_JSON', package):
                self.assertEqual(bundle.api_version(), 7)
                self.assertEqual(bundle.document_versions(), [1, 2])

    def test_document_versions_fall_back_to_every_released_viewer(self):
        # A consumer that receives no list is entitled to assume the
        # versions every viewer released so far reads.
        with tempfile.TemporaryDirectory() as root:
            package = os.path.join(root, 'package.json')
            with open(package, 'w') as stream:
                json.dump({'machinomeViewerApi': 7}, stream)
            with patch.object(bundle, 'PACKAGE_JSON', package):
                self.assertEqual(bundle.document_versions(), [1, 2, 3, 4])

    def test_the_bundle_carries_the_worker_and_is_one_file(self):
        # OpenSpec `run-in-the-worker`, design D3: the worker entry is
        # bundled INTO the one published artifact, so `machinome export`, the
        # development server and the capture page go on copying one file.
        if not bundle.has_bundle():
            self.skipTest('widget bundle not built (npm run build)')
        built = bundle.bundle_path().read_text()
        self.assertIn('onmessage', built)
        self.assertEqual(
            sorted(p.name for p in bundle.bundle_path().parent.glob('*.js')),
            ['machinome-viewer.js'])

    def test_describe_reports_absolute_existing_paths(self):
        with tempfile.TemporaryDirectory() as root:
            fake = os.path.join(root, 'machinome-viewer.js')
            open(fake, 'w').close()
            with patch.object(bundle, 'bundle_path', return_value=bundle.Path(fake)), \
                 patch.object(bundle, 'api_version', return_value=3), \
                 patch.object(bundle, 'document_versions',
                              return_value=[1, 2, 3]):
                described = bundle.describe()
        self.assertEqual(described['path'], fake)
        self.assertEqual(described['apiVersion'], 3)
        self.assertEqual(described['documentVersions'], [1, 2, 3])
        self.assertTrue(os.path.isabs(described['index']))
        self.assertEqual(described['version'], bundle.version())

    def test_describe_refuses_a_missing_bundle_with_the_remedy(self):
        with patch.object(bundle, 'has_bundle', return_value=False):
            with self.assertRaises(bundle.BundleMissing) as raised:
                bundle.describe()
        self.assertEqual(str(raised.exception), bundle.missing_bundle_remedy())
