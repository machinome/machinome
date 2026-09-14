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
    HAS_PIL, HAS_PLAYWRIGHT, SPINNER, needs_bundle, needs_pil,
    needs_playwright, published_build, published_run,
)

if HAS_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright

if HAS_PIL:
    from PIL import Image


class MountOptionsTest(TestCase):
    def test_no_camera_means_the_viewer_frames_the_model(self):
        # The chrome is suppressed: a photograph is of the model, and a
        # panel drawn over the canvas would be in the picture -- opaque
        # pixels the transparent background promises are not there.
        self.assertEqual(mount_options(time=0.25),
                         {'animation': 'external', 'time': 0.25,
                          'driverControls': 'none',
                          'partControls': 'none'})

    def test_a_camera_is_passed_through_verbatim(self):
        self.assertEqual(
            mount_options(view=((1, 2, 3), (0, 0, 0)), up=(0, 0, 1), fov=22.5),
            {'animation': 'external', 'time': 0.0,
             'driverControls': 'none',
             'partControls': 'none',
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


class CanvasPhotographTest(TestCase):
    """How the photograph is taken, which a large model made load-bearing.

    Playwright caps an element screenshot's wait for a stable box at thirty
    seconds whatever timeout it is given, and a model big enough to take
    longer than that to settle never gets photographed. The page screenshot
    clipped to the canvas honours its timeout instead.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.capture = Capture(self.tempdir.name)
        self.box = {'x': 0, 'y': 0, 'width': 320, 'height': 240}
        self.page = Mock()
        self.page.locator.return_value.get_attribute.return_value = None
        self.page.locator.return_value.bounding_box.return_value = self.box
        browser = Mock()
        browser.new_context.return_value.new_page.return_value = self.page
        self.capture.launch = Mock(return_value=browser)
        runtime = Mock()
        runtime.__enter__ = Mock(return_value=runtime)
        runtime.__exit__ = Mock(return_value=False)
        self.capture.playwright = Mock(return_value=Mock(return_value=runtime))

    def test_the_canvas_is_photographed_through_a_clipped_page_screenshot(self):
        output = os.path.join(self.tempdir.name, 'shot.png')

        self.capture.capture(output, (320, 240))

        self.page.locator.return_value.screenshot.assert_not_called()
        self.page.screenshot.assert_called_once()
        arguments = self.page.screenshot.call_args.kwargs
        self.assertEqual(arguments['clip'], self.box)
        self.assertTrue(arguments['omit_background'])
        # Beyond the thirty seconds Playwright waits for a stable element.
        self.assertGreater(arguments['timeout'], 30_000)

    def test_a_page_without_a_canvas_is_named_rather_than_photographed(self):
        self.page.locator.return_value.bounding_box.return_value = None

        with self.assertRaisesRegex(CaptureError, 'canvas'):
            self.capture.capture(os.path.join(self.tempdir.name, 'shot.png'), (320, 240))


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
        # A still photograph is the last place a hover affordance should
        # be able to appear (OpenSpec `drive-the-run-by-touch`, D14).
        self.assertIn('"partControls": "none"', page)

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


@needs_bundle
class RunningStagedDocumentTest(TestCase):
    """What the capture does with a document that carries a program.

    A running document has no animation fraction: it has a REST STATE,
    which is the instant the pose is defined at, and a state a machine
    reached, which is a different picture and is not offered here.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.staging = published_run(Path(self.tempdir.name) / 'staging')
        self.capture = Capture(str(self.staging))
        self.output = os.path.join(self.tempdir.name, 'shot.png')

    def test_an_animation_instant_is_refused_by_name_before_any_browser(self):
        with patch.object(self.capture, 'capture') as browser, \
             patch.object(self.capture, 'add_viewer') as staged:
            with self.assertRaises(CaptureError) as raised:
                self.capture.render(self.output, (320, 240),
                                    mount_options(time=0.5))
        message = str(raised.exception)
        self.assertIn('--time', message)
        self.assertIn('program', message)
        browser.assert_not_called()
        staged.assert_not_called()
        self.assertFalse(os.path.exists(self.output))

    def test_the_default_instant_is_accepted(self):
        with patch.object(self.capture, 'capture') as browser:
            self.capture.render(self.output, (320, 240), mount_options())
        browser.assert_called_once_with(self.output, (320, 240))

    def test_a_document_with_no_program_still_takes_an_instant(self):
        staging = published_build(Path(self.tempdir.name) / 'posed')
        capture = Capture(str(staging))
        with patch.object(capture, 'capture') as browser:
            capture.render(self.output, (320, 240), mount_options(time=0.5))
        browser.assert_called_once()

    def test_a_staging_without_a_document_is_still_named_first(self):
        empty = Capture(tempfile.mkdtemp(dir=self.tempdir.name))
        with self.assertRaisesRegex(CaptureError, 'viewer.json'):
            empty.render(self.output, (320, 240), mount_options(time=0.5))


@needs_bundle
@needs_playwright
class RunningCapturePageTest(TestCase):
    """The page the capture opens, for a document carrying a program."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.staging = published_run(Path(self.tempdir.name) / 'staging')
        self.capture = Capture(str(self.staging))

    def test_the_rest_state_is_photographed_and_no_step_is_taken(self):
        self.capture.add_viewer(mount_options())
        document = json.loads((self.staging / 'viewer.json').read_text())
        with self.capture.serve() as base, sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 320, 'height': 240})
                page.goto(f'{base}/index.html')
                page.wait_for_function(
                    'document.body.dataset.ready || document.body.dataset.error')
                body = page.locator('body')
                self.assertIsNone(body.get_attribute('data-error'))
                # No step of the run was taken to produce the picture.
                self.assertEqual(body.get_attribute('data-tick'), '0')
                self.assertEqual(body.get_attribute('data-clock'), '0')
                state = json.loads(body.get_attribute('data-state'))
                # Every part stands where the program's published rest
                # values put it.
                for identifier, coordinate in \
                        document['program']['coordinates'].items():
                    self.assertEqual(state[identifier], coordinate['initial'],
                                     identifier)
                # And no chrome is in the photograph.
                for selector in ('.run-controls', '.run-transport',
                                 '.driver-controls'):
                    self.assertEqual(
                        page.eval_on_selector_all(selector,
                                                  'nodes => nodes.length'),
                        0, selector)
            finally:
                browser.close()
