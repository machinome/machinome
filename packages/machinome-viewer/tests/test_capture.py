# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os
import tempfile
import urllib.request
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from machinome_viewer import capture as capture_module
from machinome_viewer.bundle import BundleStale
from machinome_viewer.capture import Capture, CaptureError, mount_options

from .support import (
    HAS_PIL, HAS_PLAYWRIGHT, SPINNER, needs_bundle, needs_pil,
    needs_playwright, published_build, published_marked, published_run,
    strip_markings,
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
        self.assertIn('machinome-viewer[snapshot]', message)
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

    def test_the_bundle_is_made_current_before_it_is_staged(self):
        # ADR-059: a capture photographs the bundle it copies, so copying
        # a stale one photographs an old renderer refusing a correct
        # document -- with no one at a browser to notice.
        with patch.object(capture_module, 'ensure_current') as ensure, \
             patch.object(capture_module.shutil, 'copy2'), \
             patch.object(self.capture, 'write_mount_page'):
            self.capture.add_viewer(mount_options())
        ensure.assert_called_once()

    def test_a_stale_bundle_is_refused_and_nothing_is_staged(self):
        stale = BundleStale('bundle is older than src/viewer.ts: npm ci && npm run build')
        with patch.object(capture_module, 'ensure_current', side_effect=stale), \
             patch.object(capture_module.shutil, 'copy2') as copied:
            with self.assertRaises(CaptureError) as raised:
                self.capture.add_viewer(mount_options())
        self.assertIn('older than', str(raised.exception))
        copied.assert_not_called()

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
        self.assertTrue((self.staging / 'machinome-viewer.js').is_file())
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
            for relative in ('viewer.json', model, 'machinome-viewer.js', 'index.html'):
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

    def test_a_version_six_document_carries_a_program_too(self):
        # `carries_program` is a load-time gate on "does this document
        # carry a program", and a document declaring ANY running version
        # does by definition -- the 6 a law reading the coordinate it
        # drives moves it to included. A test on the number 5 alone
        # would photograph the rest state while claiming another
        # instant.
        from machinome_viewer.capture import carries_program

        self.assertTrue(carries_program({"version": 6}))
        self.assertTrue(carries_program({"version": 5}))
        # Version 7 -- a program carrying a BLOCK -- is now one this
        # build RENDERS, and the floor admits it exactly as it always
        # did: the gate did not move with the version, which is what a
        # floor is for.
        self.assertTrue(carries_program({"version": 7}))
        # A version 8 document carries a compiled CLOCKED machine and no
        # program: a root publishes one or the other, and version 8 is a
        # property of the ROOT'S DECLARATION (OpenSpec
        # `execute-the-commit`, design section 10).
        self.assertFalse(carries_program({"version": 8}))
        self.assertFalse(carries_program({"version": 5, "clocked": {}}))
        self.assertFalse(carries_program({"version": 4}))
        self.assertTrue(carries_program({"version": 4, "program": {}}))
        self.assertFalse(carries_program("not a document"))

    def test_a_clocked_document_honours_a_non_zero_instant(self):
        """(8.1) A version 8 document DOES animate `$t`.

        ADR-128 section 10: a clocked root publishes the ordinary
        `animation` object, so the timeline is presented exactly as it is
        for a version 1-4 document and a geometry that is a formula of
        `$t` animates while the bank STANDS. A clocked staging is
        photographed at its INITIAL BANK, and a non-zero `--time` is
        honoured rather than refused.
        """
        document = json.loads((self.staging / 'viewer.json').read_text())
        document['version'] = 8
        document.pop('program', None)
        document['states'] = {}
        document['clocked'] = {}
        (self.staging / 'viewer.json').write_text(json.dumps(document))
        capture = Capture(str(self.staging))
        with patch.object(capture, 'capture') as browser, \
             patch.object(capture, 'add_viewer'):
            capture.render(self.output, (320, 240), mount_options(time=0.5))
        browser.assert_called_once()

    def test_what_animates_time_is_a_question_of_its_own(self):
        """(8.2) The two questions, split: "does this document carry a
        compiled program" and "does this document animate `$t`"."""
        from machinome_viewer.capture import (animates_time,
                                               carries_clocked,
                                               carries_program)

        self.assertTrue(carries_clocked({"version": 8}))
        self.assertTrue(carries_clocked({"version": 5, "clocked": {}}))
        self.assertFalse(carries_clocked({"version": 7}))
        self.assertFalse(carries_clocked("not a document"))
        # A document carrying a compiled program has no animation cycle;
        # every other document has one, a CLOCKED document included.
        self.assertFalse(animates_time({"version": 5}))
        self.assertFalse(animates_time({"version": 7}))
        self.assertFalse(animates_time({"version": 4, "program": {}}))
        self.assertTrue(animates_time({"version": 4}))
        self.assertTrue(animates_time({"version": 8}))
        self.assertTrue(animates_time({"version": 8, "clocked": {}}))

    def test_an_animation_instant_is_refused_for_a_version_six_document(self):
        document = json.loads((self.staging / 'viewer.json').read_text())
        document['version'] = 6
        (self.staging / 'viewer.json').write_text(json.dumps(document))
        capture = Capture(str(self.staging))
        with patch.object(capture, 'capture') as browser, \
             patch.object(capture, 'add_viewer') as staged:
            with self.assertRaises(CaptureError) as raised:
                capture.render(self.output, (320, 240),
                               mount_options(time=0.5))
        self.assertIn('--time', str(raised.exception))
        browser.assert_not_called()
        staged.assert_not_called()

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


@needs_bundle
@needs_playwright
@needs_pil
class MarkedStagedDocumentTest(TestCase):
    """A staged document whose parts carry markings is photographed WITH
    them (design D10).

    `Capture.serve` serves the WHOLE staging directory, and the framework
    already stages marking artifacts beside the models it copies, so
    `machinome snapshot --renderer web` photographs markings the moment the
    widget draws them -- with no change to `capture.py` and none to
    `mount_options`. That is a claim, and this proves it with a marked
    staging rather than asserting it.

    The probe is `test_widget_e2e.MarkedDocumentPixelsTest`'s: both parts
    of this fixture declare no colour and render through
    `MeshNormalMaterial`, whose `normal * 0.5 + 0.5` output is NEUTRAL
    only where |nx| = |ny| = |nz| -- which a cylinder about z and an
    axis-aligned box never reach -- while both declared marking colours,
    `#FFFFFF` and `#C0C0C0`, are neutral under the scene's near-white
    lights.
    """

    NEUTRAL_SPREAD = 20
    NEUTRAL_FLOOR = 40

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def photograph(self, staging):
        output = os.path.join(self.tempdir.name, f'{staging.name}.png')
        Capture(str(staging)).render(output, (480, 360), mount_options())
        return Image.open(output).convert('RGB')

    def marking_pixels(self, image):
        """Count the pixels showing a marking's own colour."""
        found = 0
        for red, green, blue in image.getdata():
            if (max(red, green, blue) - min(red, green, blue) <= self.NEUTRAL_SPREAD
                    and min(red, green, blue) >= self.NEUTRAL_FLOOR):
                found += 1
        return found

    def test_a_marked_model_is_photographed_with_its_markings(self):
        marked = published_marked(Path(self.tempdir.name) / 'marked')
        twin = published_marked(Path(self.tempdir.name) / 'twin')
        strip_markings(twin / 'viewer.json')

        with_markings = self.marking_pixels(self.photograph(marked))
        without = self.marking_pixels(self.photograph(twin))

        self.assertGreater(with_markings, 500,
                           'the photograph shows no marking')
        self.assertLess(without, 100,
                        'the same staging with its markings removed was '
                        'photographed with one anyway')
