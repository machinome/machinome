# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Curta's unchanged CAD-free diagnostic, through both browser transports.

Screenshots show diagnostic state, not project geometry. The existing carriage
browser suite separately checks rendered moving parts against committed banks.
"""
import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from machinome_viewer.bundle import bundle_path
from tests.support import FIXTURES, needs_bundle, needs_playwright, serve_directory

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PAGE = '''<!doctype html><meta charset="utf-8"><title>Curta source timing</title>
<style>body{background:#101418;color:#e2e9ef;font:16px monospace}
#host{width:800px;height:420px}pre{white-space:pre-wrap}</style>
<h2>Curta source-timing diagnostic — no CAD geometry</h2>
<div id="host"></div><pre id="bank"></pre><script src="machinome-viewer.js"></script>'''


@needs_bundle
@needs_playwright
class SourceTimingBrowserTest(TestCase):
    def assert_record(self, actual, expected, field=''):
        if isinstance(expected, (int, float)) and field not in ('tick', 'level'):
            self.assertLessEqual(abs(actual-expected), 1e-9*max(1, abs(actual), abs(expected)), field)
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), field)
            for left, right in zip(actual, expected):
                self.assert_record(left, right, field)
        elif isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), field)
            for key, value in expected.items():
                self.assert_record(actual[key], value, key)
        else:
            self.assertEqual(actual, expected, field)

    def test_full_constrained_carry_in_worker_and_fallback(self):
        fixture = json.loads((FIXTURES / 'source-timing' / 'curta-11-constrained.json').read_text())
        entry = fixture['cases'][0]
        shots = Path(__file__).parent / '_shots'
        shots.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary)
            (staged / 'viewer.json').write_text(json.dumps(entry['document']))
            (staged / 'harness.html').write_text(PAGE)
            shutil.copy2(bundle_path(), staged / 'machinome-viewer.js')
            with serve_directory(staged) as url, sync_playwright() as playwright:
                browser = playwright.chromium.launch(args=[
                    '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader'])
                try:
                    for fallback in (False, True):
                        with self.subTest(fallback=fallback):
                            page = browser.new_page(viewport={'width': 1000, 'height': 800})
                            page.set_default_timeout(300_000)
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            if fallback:
                                page.add_init_script("window.Worker = class { constructor() { throw new Error('test CSP refusal'); } };")
                            page.goto(f'{url}/harness.html')
                            page.evaluate('''async () => {
                              window.viewer = await MachinomeViewer.mount(
                                document.getElementById('host'), 'viewer.json', {run:{dt:.1}});
                              window.run = viewer.run();
                              window.crossings = []; window.stops = [];
                              run.onCommit(frame => {
                                crossings.push(...frame.crossings);
                                stops.push(...frame.stops);
                              });
                            }''')
                            self.assertEqual(page.evaluate('run.runsInWorker'), not fallback)
                            self.assertEqual(page.evaluate('viewer.apiVersion'), 24)
                            for index, row in enumerate(entry['rows']):
                                if index == len(entry['rows'])-1:
                                    page.evaluate('async () => { window.saved = await run.snapshot(); }')
                                result = page.evaluate('''async ({driver,to}) => {
                                  crossings.length=0; stops.length=0;
                                  const commands = await run.move(driver,{to});
                                  return {commands, bank:run.state(),crossings,
                                    stops:stops.map(stop => ({time_drives:[],...stop}))};
                                }''', {'driver': row['driver'], 'to': row['to']})
                                self.assert_record(result['bank'], row['bank'])
                                self.assert_record(result['crossings'], row['crossings'])
                                self.assert_record(result['stops'], row['stops'])
                                self.assertEqual(result['commands'][0]['status'], row['status'])
                                self.assert_record(result['commands'][0]['admitted'], row['admitted'])
                            final = entry['rows'][-1]
                            page.evaluate('''() => {
                              const bank=run.state();
                              document.getElementById('bank').textContent=JSON.stringify({
                                transport:run.runsInWorker?'worker':'fallback',
                                crank:bank.crank_angle,ones:bank['ones.turn'],tens:bank['tens.turn'],
                                firstLever:bank['lever.travel'],tick:run.tick()},null,2);
                            }''')
                            mode = 'fallback' if fallback else 'worker'
                            page.screenshot(path=str(shots / f'curta-source-timing-{mode}.png'))
                            replay = page.evaluate('''async () => {
                              await run.restore(saved);
                              const commands=await run.move('crank_angle',{to:180});
                              return {bank:run.state(),commands};
                            }''')
                            self.assert_record(replay['bank'], final['bank'])
                            self.assertEqual(replay['commands'][0]['status'], 'completed')
                            self.assertEqual(errors, [])
                            page.evaluate('viewer.dispose()')
                            page.close()
                finally:
                    browser.close()
