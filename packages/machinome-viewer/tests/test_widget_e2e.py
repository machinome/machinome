# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""End-to-end tests for the export widget: serve the fixture export over
HTTP, render it in headless chromium and assert on the pixels -- models
load with their colours, and the ?t= URL parameter poses the $t animation.

The mount-interface tests drive a real page with playwright instead,
because a screenshot cannot click a control or read an attribute.
"""

import json
import os
import tempfile
from pathlib import Path
from subprocess import run
from unittest import TestCase

from solid_node_viewer.bundle import api_version

from .support import (
    CHROME, HAS_PIL, HAS_PLAYWRIGHT, export_with_widget, needs_bundle,
    needs_chrome, needs_pil, needs_playwright, serve_directory,
)

if HAS_PIL:
    from PIL import Image, ImageChops
if HAS_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright


@needs_bundle
@needs_chrome
@needs_pil
class WidgetE2ETest(TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.base_url = f'{base}/index.html'

    def screenshot(self, query):
        path = os.path.join(self.tempdir.name, 'shot.png')
        result = run(
            [
                CHROME, '--headless', '--no-sandbox', '--disable-gpu',
                '--use-angle=swiftshader', '--window-size=800,600',
                '--virtual-time-budget=4000', f'--screenshot={path}',
                f'{self.base_url}?{query}',
            ],
            capture_output=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0,
                         f'chromium failed: {result.stderr.decode()[-500:]}')
        image = Image.open(path).convert('RGB')
        os.remove(path)
        # Crop off the control bar: pixel assertions are about the model.
        return image.crop((0, 0, image.width, image.height - 40))

    def count_pixels(self, image, predicate):
        return sum(1 for pixel in image.getdata() if predicate(*pixel))

    def test_models_render_with_their_colors(self):
        image = self.screenshot('t=0&autoplay=0')
        red = self.count_pixels(
            image, lambda r, g, b: r > 100 and r > 1.4 * g and r > 1.4 * b)
        blue = self.count_pixels(
            image, lambda r, g, b: b > 100 and b > 1.4 * r and b > 1.4 * g)
        self.assertGreater(red, 500, 'red hub not visible')
        self.assertGreater(blue, 2000, 'blue blades not visible')

    def test_time_parameter_poses_the_animation(self):
        at_zero = self.screenshot('t=0&autoplay=0')
        at_eighth = self.screenshot('t=0.125&autoplay=0')
        difference = ImageChops.difference(at_zero, at_eighth)
        changed = self.count_pixels(difference, lambda r, g, b: r + g + b > 30)
        self.assertGreater(changed, 2000, 'pose did not change with ?t=')

    def test_full_cycle_returns_to_start(self):
        at_zero = self.screenshot('t=0&autoplay=0')
        at_one = self.screenshot('t=1&autoplay=0')
        difference = ImageChops.difference(at_zero, at_one)
        changed = self.count_pixels(difference, lambda r, g, b: r + g + b > 30)
        self.assertLess(changed, 500, 't=0 and t=1 should render the same pose')


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      html, body { margin: 0; }
      #host { width: 800px; height: 600px; position: relative; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="solid-widget.js"></script>
  </body>
</html>
"""


@needs_bundle
@needs_playwright
class ViewerMountApiTest(TestCase):
    """The mount interface hosts other than an export page need."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        manifest = json.loads((self.out_dir / 'manifest.json').read_text())
        manifest['drivers'] = {
            'turns': {
                'default': 0.0, 'range': [-55.0, 306.0], 'unit': 'turn',
                'dtype': None, 'scale': None,
            },
        }
        (self.out_dir / 'driven.json').write_text(json.dumps(manifest))
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def in_page(self, script):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                result = page.evaluate(script)
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
                return result
            finally:
                browser.close()

    def test_dispose_leaves_the_container_empty(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const mounted = host.children.length;
          viewer.dispose();
          return { mounted, after: host.children.length };
        }""")
        self.assertGreater(result['mounted'], 0, 'nothing was mounted')
        self.assertEqual(result['after'], 0, 'dispose() left elements in the container')

    def test_the_bundle_and_mount_handle_report_one_api_version(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          return { bundle: SolidNodeWidget.apiVersion, handle: viewer.apiVersion };
        }""")
        self.assertEqual(result['bundle'], api_version())
        self.assertEqual(result['bundle'], result['handle'])

    def test_the_mount_handle_exposes_and_controls_the_assembly(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const assembly = viewer.assembly();
          const target = assembly.children[0] ?? assembly;
          viewer.setRoot(target.path);
          viewer.setVisible(target.path, false);
          viewer.setVisible(target.path, true);
          let invalid = null;
          try { viewer.setRoot(['missing']); }
          catch (error) { invalid = String(error); }
          return {
            apiVersion: viewer.apiVersion,
            node: { name: assembly.name, path: assembly.path, color: assembly.color,
                    model: assembly.model, children: assembly.children.length },
            invalid,
          };
        }""")
        self.assertEqual(result['apiVersion'], api_version())
        self.assertEqual(result['node']['name'], 'Spinner')
        self.assertEqual(result['node']['path'], [])
        self.assertIsInstance(result['node']['model'], bool)
        self.assertEqual(result['node']['children'], 4)
        self.assertIn('Unknown assembly path: missing', result['invalid'])

    def test_a_captured_view_survives_a_remount(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const first = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const moved = {
            camera: first.view().camera.clone().multiplyScalar(2),
            target: first.view().target.clone(),
          };
          first.dispose();
          const second = await SolidNodeWidget.mount(host, 'manifest.json', { view: moved });
          const got = second.view();
          return {
            want: [moved.camera.x, moved.camera.y, moved.camera.z],
            got: [got.camera.x, got.camera.y, got.camera.z],
          };
        }""")
        for want, got in zip(result['want'], result['got']):
            self.assertAlmostEqual(want, got, places=4, msg='remount did not restore the view')

    def test_reload_keeps_the_maker_looking_where_they_were(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const before = viewer.view();
          const want = [before.camera.x, before.camera.y, before.camera.z];
          await viewer.reload();
          const after = viewer.view();
          return { want, got: [after.camera.x, after.camera.y, after.camera.z] };
        }""")
        for want, got in zip(result['want'], result['got']):
            self.assertAlmostEqual(want, got, places=4, msg='reload() moved the camera')

    def test_manifest_update_keeps_the_canvas_and_camera(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const canvas = host.querySelector('canvas');
          const before = viewer.view();
          await viewer.manifestChanged();
          const after = viewer.view();
          return {
            sameCanvas: canvas === host.querySelector('canvas'),
            before: [before.camera.x, before.camera.y, before.camera.z],
            after: [after.camera.x, after.camera.y, after.camera.z],
          };
        }""")
        self.assertTrue(result['sameCanvas'], 'manifest update replaced the canvas')
        for before, after in zip(result['before'], result['after']):
            self.assertAlmostEqual(before, after, places=4, msg='manifest update moved the camera')

    def test_the_host_names_the_canvas(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          await SolidNodeWidget.mount(host, 'manifest.json', {
            className: 'functional-model', role: 'img', ariaLabel: 'Functional model',
          });
          const canvas = host.querySelector('canvas');
          return { className: canvas.className, role: canvas.getAttribute('role'),
                   label: canvas.getAttribute('aria-label') };
        }""")
        self.assertEqual(result['className'], 'functional-model')
        self.assertEqual(result['role'], 'img')
        self.assertEqual(result['label'], 'Functional model')

    def test_a_slider_readout_accepts_an_exact_number(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'driven.json',
                                                     { autoplay: false });
          const row = host.querySelector('.driver-control');
          const slider = row.querySelector('input[type=range]');
          const exact = row.querySelector('input[type=number]');
          if (exact === null) return { present: false };
          exact.focus();
          exact.value = '25.82';
          exact.dispatchEvent(new Event('input'));
          const inside = { driver: viewer.driver('turns'),
                           slider: slider.value, unit: row.textContent };
          exact.value = '400';
          exact.dispatchEvent(new Event('input'));
          exact.blur();
          return { present: true, inside, outside: viewer.driver('turns'),
                   pinned: slider.value, shown: exact.value,
                   label: exact.getAttribute('aria-label') };
        }""")
        self.assertTrue(result['present'])
        self.assertEqual(result['inside']['driver'], 25.82)
        self.assertEqual(result['inside']['slider'], '25.82')
        self.assertIn('turn', result['inside']['unit'])
        self.assertEqual(result['outside'], 400)
        self.assertEqual(result['pinned'], '306')
        self.assertEqual(result['shown'], '400.0000')
        self.assertIn('exact value', result['label'])

    def test_the_toggle_presentation_starts_collapsed(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          await SolidNodeWidget.mount(host, 'manifest.json', { animation: 'toggle' });
          const toggle = host.querySelector('.timeline-toggle');
          const bar = host.querySelector('.animation-controls');
          const collapsed = { expanded: toggle.getAttribute('aria-expanded'),
                              barVisible: bar.offsetParent !== null };
          toggle.click();
          return { collapsed, expanded: toggle.getAttribute('aria-expanded'),
                   barVisible: bar.offsetParent !== null };
        }""")
        self.assertEqual(result['collapsed']['expanded'], 'false')
        self.assertFalse(result['collapsed']['barVisible'])
        self.assertEqual(result['expanded'], 'true')
        self.assertTrue(result['barVisible'])
