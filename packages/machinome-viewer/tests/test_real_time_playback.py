# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""Real-time playback from a declared loop (OpenSpec change
``real-time-playback``), driven through a real page with playwright:
the bar's speed control and machine-time readout exist only for a
document whose ``animation`` object carries ``loop``, the handle's
``speed()``/``setSpeed()`` and the control are one door, and a document
without a loop keeps exactly the bar it always had.

The rate itself -- ``loop / speed`` wall seconds a turn -- is decided by
the pure ``playback.ts`` and tested in the widget suite.
"""

import json
import tempfile
from pathlib import Path
from unittest import TestCase

from .support import (
    HAS_PLAYWRIGHT, export_with_widget, needs_bundle, needs_playwright,
    serve_directory,
)
from .test_widget_e2e import HARNESS_PAGE

if HAS_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright


@needs_bundle
@needs_playwright
class RealTimePlaybackTest(TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        # The same spinner, published by a root declaring a twelve-hour
        # time base: the framework adds `loop` beside fps and frames.
        manifest = json.loads((self.out_dir / 'manifest.json').read_text())
        manifest['animation']['loop'] = 43200.0
        (self.out_dir / 'clock.json').write_text(json.dumps(manifest))
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
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                result = page.evaluate(script)
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
                return result
            finally:
                browser.close()

    def test_a_declared_loop_earns_a_speed_control_and_a_readout(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'clock.json',
                                                     { autoplay: false });
          const select = host.querySelector('select.playback-speed');
          const readout = host.querySelector('.machine-time');
          const options = [...select.options].map((o) => o.value);
          const labels = [...select.options].map((o) => o.textContent);
          const before = readout.textContent;
          viewer.setTime(0.5);
          return { speed: viewer.speed(), selected: select.value,
                   label: select.getAttribute('aria-label'),
                   options, labels, before, half: readout.textContent };
        }""")
        self.assertEqual(result['speed'], 1)
        self.assertEqual(result['selected'], '1')
        self.assertEqual(result['label'], 'Playback speed')
        self.assertEqual(result['options'],
                         ['0.1', '0.25', '0.5', '1', '2', '5', '10', '60',
                          '360', '3600'])
        self.assertEqual(result['labels'][3], '×1')
        self.assertEqual(result['before'], '0:00:00')
        self.assertEqual(result['half'], '6:00:00')

    def test_the_control_and_the_handle_are_one_door(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'clock.json',
                                                     { autoplay: false, speed: 720 });
          const select = host.querySelector('select.playback-speed');
          const hostSet = { speed: viewer.speed(), selected: select.value,
                            options: [...select.options].map((o) => o.value) };
          select.value = '60';
          select.dispatchEvent(new Event('change'));
          const fromControl = viewer.speed();
          viewer.setSpeed(3600);
          const fromHandle = select.value;
          let refused = null;
          try { viewer.setSpeed(0); } catch (error) { refused = String(error); }
          return { hostSet, fromControl, fromHandle, refused,
                   kept: viewer.speed() };
        }""")
        self.assertEqual(result['hostSet']['speed'], 720)
        self.assertEqual(result['hostSet']['selected'], '720')
        # A host-set speed the ladder lacks is offered, in order.
        self.assertIn('720', result['hostSet']['options'])
        options = [float(v) for v in result['hostSet']['options']]
        self.assertEqual(options, sorted(options))
        self.assertEqual(result['fromControl'], 60)
        self.assertEqual(result['fromHandle'], '3600')
        self.assertIn('0', result['refused'])
        self.assertEqual(result['kept'], 3600)

    def test_the_timeline_reaches_the_complete_loop(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'clock.json',
                                                     { autoplay: false });
          const slider = host.querySelector('.animation-controls input[type=range]');
          slider.value = slider.max;
          slider.dispatchEvent(new Event('input'));
          return { value: slider.value, step: Number(slider.step),
                   readout: host.querySelector('.machine-time').textContent };
        }""")
        self.assertEqual(result['value'], '359')
        self.assertEqual(result['step'], 1)
        self.assertEqual(result['readout'], '12:00:00')

    def test_a_document_without_a_loop_keeps_the_bar_it_had(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'manifest.json',
                                                     { autoplay: false });
          viewer.setSpeed(720);
          return { select: host.querySelector('select.playback-speed') !== null,
                   readout: host.querySelector('.machine-time') !== null,
                   bar: host.querySelector('.animation-controls').children.length,
                   speed: viewer.speed() };
        }""")
        self.assertFalse(result['select'])
        self.assertFalse(result['readout'])
        self.assertEqual(result['bar'], 2)
        # Accepted and stored, with nothing to apply it to.
        self.assertEqual(result['speed'], 720)
