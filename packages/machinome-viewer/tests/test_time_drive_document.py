# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The originating Astrarium fixture, unmodified, in both browser transports."""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from machinome_viewer.bundle import bundle_path
from tests.support import FIXTURES, needs_bundle, needs_playwright, serve_directory
from tests.test_running_document import HARNESS_PAGE, model_paths

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

FIXTURE = FIXTURES / 'astrarium'
SHOTS = Path(__file__).parent / '_shots'


class AstrariumFixtureTest(TestCase):
    def test_fixture_is_complete_and_has_no_synthetic_clock_input(self):
        document = json.loads((FIXTURE / 'viewer.json').read_text())
        self.assertEqual(document['version'], 10)
        self.assertEqual(sorted(document['drivers']), ['enabled', 'wind'])
        self.assertEqual(document['program']['time_drives'], [{'id': '@time:0', 'edge': 0}])
        paths = model_paths(document['root'])
        self.assertEqual(len(paths), 2)
        for path in paths:
            self.assertTrue((FIXTURE / path).is_file(), path)


@needs_bundle
@needs_playwright
class AstrariumBrowserTest(TestCase):
    def test_retained_history_in_worker_and_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / 'astrarium'
            shutil.copytree(FIXTURE, staged)
            shutil.copy2(bundle_path(), staged / 'machinome-viewer.js')
            (staged / 'harness.html').write_text(HARNESS_PAGE)
            SHOTS.mkdir(exist_ok=True)
            with serve_directory(staged) as url, sync_playwright() as playwright:
                browser = playwright.chromium.launch(args=[
                    '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
                ])
                try:
                    for fallback in (False, True):
                        with self.subTest(fallback=fallback):
                            page = browser.new_page(viewport={'width': 800, 'height': 600})
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            if fallback:
                                page.add_init_script("window.Worker = class { constructor() { throw new Error('test CSP refusal'); } };")
                            page.goto(f'{url}/harness.html')
                            page.evaluate("""async () => {
                              window.viewer = await MachinomeViewer.mount(
                                document.getElementById('host'), 'viewer.json', {run: {dt: 0.02}});
                              // Keep the full declared 10 mm weight path in view.
                              viewer.setView({camera: [15, -18, 10], target: [1.5, 0, -4]});
                              window.run = viewer.run();
                            }""")
                            self.assertEqual(page.evaluate('run.running()'), False)
                            self.assertEqual(page.evaluate('run.tick()'), 0)
                            self.assertEqual(page.evaluate('run.runsInWorker'), not fallback)
                            page.wait_for_timeout(100)
                            before = page.locator('canvas').screenshot()
                            mode = 'fallback' if fallback else 'worker'
                            page.screenshot(path=str(SHOTS / f'astrarium-{mode}-rest.png'))
                            result = page.evaluate("""async () => {
                              await run.step(100);
                              return {state: run.state(), time: run.elapsed(), snapshot: await run.snapshot()};
                            }""")
                            self.assertAlmostEqual(result['state']['shaft.turn'], 2)
                            self.assertAlmostEqual(result['state']['weight.drop'], 2)
                            self.assertEqual(result['time'], 2)
                            self.assertEqual(result['snapshot']['commands'], [])
                            page.wait_for_timeout(100)
                            self.assertNotEqual(before, page.locator('canvas').screenshot())
                            page.screenshot(path=str(SHOTS / f'astrarium-{mode}-running.png'))
                            result = page.evaluate("""async () => {
                              const saved = await run.snapshot();
                              await run.move('enabled', {to: 0});
                              await run.step(100);
                              await run.move('wind', {by: 2});
                              const wound = run.state();
                              await run.move('enabled', {to: 1});
                              await run.step(50);
                              const resumed = run.state();
                              await run.step(600);
                              const exhausted = run.state();
                              await run.move('enabled', {to: 0});
                              await run.move('wind', {by: 5});
                              await run.move('enabled', {to: 1});
                              await run.step(50);
                              const restarted = run.state();
                              await run.restore(saved);
                              await run.step(50);
                              const replayed = run.state();
                              await run.reset();
                              return {wound, resumed, exhausted, restarted, replayed,
                                reset: run.state(), time: run.elapsed(), drivers: Object.keys(viewer.drivers())};
                            }""")
                            for key, shaft, drop in [('wound', 2, 0), ('resumed', 3, 1),
                                                      ('exhausted', 12, 10), ('restarted', 13, 6),
                                                      ('replayed', 3, 3), ('reset', 0, 0)]:
                                self.assertAlmostEqual(result[key]['shaft.turn'], shaft)
                                self.assertAlmostEqual(result[key]['weight.drop'], drop)
                            self.assertEqual(result['time'], 0)
                            self.assertEqual(sorted(result['drivers']), ['enabled', 'wind'])
                            self.assertEqual(errors, [])
                            page.evaluate('viewer.dispose()')
                            page.close()
                finally:
                    browser.close()
