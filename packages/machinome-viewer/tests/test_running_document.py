# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The acceptance: the Pascaline module running in a real browser.

`tests/fixtures/pascaline/viewer.json` is the module's own published
build, verbatim -- a version 5 document carrying the compiled mechanical
program. What this proves is the sentence the whole cycle exists for:
ten `Add one` leave the tens drum where TEN of them left it, which no
absolute pose could ever show, and the bank that says so reaches the
geometry on the page.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    FIXTURES, needs_bundle, needs_playwright, serve_directory,
)
from solid_node_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

PASCALINE = FIXTURES / 'pascaline'

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'

HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>running document harness</title>
    <style>
      html, body { margin: 0; height: 100%; background: #101418; }
      #host { width: 800px; height: 600px; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="solid-widget.js"></script>
  </body>
</html>
"""

#: Ten `Add one`, each stepped for its whole declared second at the
#: viewer's own step size, awaiting the outcome of every one.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await SolidNodeWidget.mount(host, 'viewer.json', {});
  const run = viewer.run();
  if (run === null) {
    return { run: null };
  }
  const rest = run.state();
  const restShot = host.querySelector('canvas').toDataURL();
  const started = performance.now();
  const outcomes = [];
  for (let press = 0; press < 10; press += 1) {
    const settled = run.trigger('Add one');
    await run.step(240);
    outcomes.push(await settled);
  }
  const wall = performance.now() - started;
  const drivenShot = host.querySelector('canvas').toDataURL();
  return {
    identity: run.identity(),
    dt: run.dt(),
    runsInWorker: run.runsInWorker,
    restTick: 0,
    tick: run.tick(),
    elapsed: run.elapsed(),
    rest,
    state: run.state(),
    outcomes: outcomes.flat().map((one) => [one.status, one.admitted]),
    moved: restShot !== drivenShot,
    wall,
    apiVersion: viewer.apiVersion,
  };
}"""


@needs_bundle
@needs_playwright
class RunningDocumentTest(TestCase):
    """A version 5 document, mounted, run and photographed."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'pascaline'
        shutil.copytree(PASCALINE, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'solid-widget.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((PASCALINE / 'viewer.json').read_text())

    def test_ten_add_ones_accumulate_the_carry_on_the_page(self):
        SHOTS.mkdir(exist_ok=True)
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(self.harness_url)
                page.wait_for_function(
                    'typeof SolidNodeWidget !== "undefined"')
                # The rest pose, photographed before anything is asked of
                # the run: pixels are evidence, and a green suite is not
                # an inspection.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__rest = await SolidNodeWidget.mount(
                    host, 'viewer.json', {});
                }""")
                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'pascaline-at-rest.png'))
                page.evaluate('() => { window.__rest.dispose(); }')
                result = page.evaluate(DRIVE)
                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'pascaline-after-ten.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        self.assertIsNotNone(result.get('identity'),
                             'the handle reported no run')
        self.assertEqual(result['identity'],
                         self.document['program']['identity'])
        self.assertEqual(result['apiVersion'], 8)
        self.assertAlmostEqual(result['dt'], 1 / 240, places=12)

        # The rest bank, before any tick.
        self.assertEqual(result['rest']['tens.drum.turn'], 0)
        self.assertEqual(result['rest']['units.drum.turn'], 0)

        # Ten instructions, each a whole declared second at 1/240.
        self.assertEqual(result['tick'], 2400)
        self.assertAlmostEqual(result['elapsed'], 10.0, places=9)
        self.assertEqual(result['state']['units_entry'], 10)
        self.assertAlmostEqual(result['state']['units.drum.turn'], 360,
                               places=9)
        # CARRY_THROW: the framework's own number for ten `Add one`, which
        # the module's `test_the_second_carry_is_cumulative` pins.
        self.assertLessEqual(
            abs(result['state']['tens.drum.turn'] - 65.54),
            1e-9 * max(1.0, 65.54),
            result['state']['tens.drum.turn'])

        # Every instruction retired completed, having admitted its digit.
        self.assertEqual([status for status, _ in result['outcomes']],
                         ['completed'] * 10)

        # And the bank provably reached the geometry: the canvas the
        # widget drew at rest is not the canvas it drew after.
        self.assertTrue(result['moved'],
                        'the rendered canvas did not change')

        print(f"\nrunsInWorker={result['runsInWorker']} "
              f"wall={result['wall']:.0f} ms for 2400 ticks "
              f"tens.drum.turn={result['state']['tens.drum.turn']!r}")
