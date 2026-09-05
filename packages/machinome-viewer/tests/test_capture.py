# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os
import tempfile
import urllib.request
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from solid_node_viewer import capture as capture_module
from solid_node_viewer.capture import Capture, CaptureError, mount_options

from .support import (
    HAS_PIL, SPINNER, needs_bundle, needs_pil, needs_playwright, published_build,
)

if HAS_PIL:
    from PIL import Image


class MountOptionsTest(TestCase):
    def test_no_camera_means_the_viewer_frames_the_model(self):
        self.assertEqual(mount_options(time=0.25),
                         {'animation': 'external', 'time': 0.25})

    def test_a_camera_is_passed_through_verbatim(self):
        self.assertEqual(
            mount_options(view=((1, 2, 3), (0, 0, 0)), up=(0, 0, 1), fov=22.5),
            {'animation': 'external', 'time': 0.0,
             'view': {'camera': [1, 2, 3], 'target': [0, 0, 0]},
             'up': [0, 0, 1], 'fov': 22.5})


class CaptureFailureTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.capture = Capture(self.tempdir.name)

    def test_root_is_refused_without_disabling_the_sandbox(self):
        with patch('os.geteuid', return_value=0):
            with self.assertRaisesRegex(CaptureError, 'root.*sandbox'):
                self.capture.assert_not_root()

    def test_missing_playwright_names_both_install_steps(self):
        with patch.dict('sys.modules', {'playwright': None, 'playwright.sync_api': None}):
            with self.assertRaises(CaptureError) as raised:
                self.capture.playwright()
        message = str(raised.exception)
        self.assertIn('solid-node-viewer[snapshot]', message)
        self.assertIn('playwright install chromium', message)

    def test_missing_browser_has_an_actionable_install_message(self):
        browser_type = Mock()
        browser_type.launch.side_effect = Exception("Executable doesn't exist")
        with self.assertRaises(CaptureError) as raised:
            self.capture.launch(browser_type)
        self.assertIn('playwright install chromium', str(raised.exception))

    def test_a_missing_bundle_reuses_the_lookup_remedy(self):
        with patch.object(capture_module, 'has_bundle', return_value=False):
            with self.assertRaises(CaptureError) as raised:
                self.capture.add_viewer(mount_options())
        self.assertEqual(str(raised.exception), capture_module.missing_bundle_remedy())

    def test_a_staging_without_a_document_is_refused_before_the_browser(self):
        with patch.object(self.capture, 'capture') as browser:
            with self.assertRaisesRegex(CaptureError, 'viewer.json'):
                self.capture.render('out.png', (10, 10), mount_options())
        browser.assert_not_called()


@needs_bundle
class StagedDocumentTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.staging = published_build(Path(self.tempdir.name) / 'staging')
        self.capture = Capture(str(self.staging))

    def test_the_viewer_is_added_beside_the_document(self):
        self.capture.add_viewer(mount_options(time=0.5, fov=22.5))
        page = (self.staging / 'index.html').read_text()
        self.assertTrue((self.staging / 'solid-widget.js').is_file())
        self.assertIn("mount('#host', 'viewer.json'", page)
        self.assertIn(json.dumps(mount_options(time=0.5, fov=22.5)), page)

    def test_the_server_exposes_document_models_bundle_and_page(self):
        self.capture.add_viewer(mount_options())
        document = json.loads((self.staging / 'viewer.json').read_text())
        model = document['root']['children'][0]['model']
        with self.capture.serve() as url:
            for relative in ('viewer.json', model, 'solid-widget.js', 'index.html'):
                with urllib.request.urlopen(f'{url}/{relative}') as response:
                    self.assertEqual(response.status, 200, relative)


@needs_bundle
@needs_playwright
@needs_pil
class CaptureEndToEndTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.staging = published_build(Path(self.tempdir.name) / 'staging')

    def test_the_photograph_has_a_transparent_border_and_an_opaque_model(self):
        output = os.path.join(self.tempdir.name, 'shot.png')
        Capture(str(self.staging)).render(output, (320, 240), mount_options())
        image = Image.open(output).convert('RGBA')
        alpha = image.getchannel('A')
        border = (
            list(alpha.crop((0, 0, image.width, 1)).getdata())
            + list(alpha.crop((0, image.height - 1, image.width, image.height)).getdata())
            + list(alpha.crop((0, 0, 1, image.height)).getdata())
            + list(alpha.crop((image.width - 1, 0, image.width, image.height)).getdata())
        )
        self.assertEqual(set(border), {0})
        self.assertIn(255, alpha.getdata())
