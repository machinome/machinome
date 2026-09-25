# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The acceptance: the Curta's clearing interface running in a real
browser.

`tests/fixtures/clearing/viewer.json` is the framework's own
`tests/clearing_project/machine.py:CurtaInterface`, exported verbatim --
a **version 6** document whose six law edges each READ THE COORDINATE
THEY DRIVE, and which this viewer refused by name until this cycle.

What this proves is the mechanism: one ring carrying two nine-tooth racks
sweeps past six register dials, and a rack turns a dial only while its
teeth reach it AND the dial is not already standing in its missing-tooth
gap. The gap is what lets the ring go on sweeping past a dial that has
finished while it still clears the dials beyond it -- so a second sweep
moves nothing at all. Nothing here poses anything; everything is driven
by the document's own declared driver.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    CLEARING, needs_bundle, needs_playwright, serve_directory,
)
from machinome_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'

#: The clearing gear's stated clearance, from the machine's own
#: `GAP = 0.5`: each dial is disengaged over a band of this half-width
#: about every multiple of 360, entered from either side.
GAP = 0.5

#: The six dials, and what the fixture rests each of them at.
DIALS = ('result0.turn', 'result1.turn', 'result2.turn',
         'counter0.turn', 'counter1.turn', 'counter2.turn')
REST = {'result0.turn': 36.0, 'result1.turn': 72.0, 'result2.turn': 108.0,
        'counter0.turn': 144.0, 'counter1.turn': 180.0,
        'counter2.turn': 216.0}


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


def disengaged(value):
    """Whether the published gate reads DISENGAGED at `value`, by the
    machine's own arithmetic rather than by a tolerance."""
    import math
    shifted = value + GAP
    return shifted - 360.0 * math.floor(shifted / 360.0) < 2 * GAP


class ClearingFixtureTest(TestCase):
    """The committed `clearing` fixture is complete on disk.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas a browser test later.
    """

    def setUp(self):
        self.document = json.loads((CLEARING / 'viewer.json').read_text())

    def test_every_model_path_resolves_beside_the_document(self):
        paths = model_paths(self.document['root'])
        self.assertEqual(len(paths), 6)
        self.assertEqual(len(set(paths)), 1)
        missing = [path for path in sorted(set(paths))
                   if not (CLEARING / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')

    def test_the_document_is_the_framework_s_own_machine(self):
        self.assertEqual((CLEARING / 'viewer.json').stat().st_size, 16152)
        self.assertEqual(self.document['version'], 6)
        self.assertEqual(list(self.document['drivers']), ['clearing'])
        program = self.document['program']
        self.assertTrue(program['identity'].startswith('7425122f'))
        self.assertEqual(sorted(program['coordinates']),
                         sorted(['clearing', *DIALS]))
        for name, rest in REST.items():
            self.assertEqual(program['coordinates'][name]['initial'], rest)
        self.assertEqual(len(program['edges']), 6)
        self.assertEqual(len(self.document['bindings']), 30)

    def test_every_one_of_its_six_laws_reads_the_end_it_drives(self):
        driven = []
        for edge in self.document['program']['edges']:
            self.assertEqual(edge['kind'], 'law')
            self.assertEqual(len(edge['gives']), 1)
            read = set(edge['needs']) & set(edge['gives'])
            self.assertEqual(read, set(edge['gives']))
            driven.extend(edge['gives'])
            # The `clamp01` station window: the SKELETON is not affine,
            # so every self-read crossing here is a SEARCHED one.
            self.assertEqual(edge['affine'], [False])
        self.assertEqual(sorted(driven), sorted(DIALS))


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>curta clearing harness</title>
    <style>
      html, body { margin: 0; height: 100%; background: #101418; }
      #host { width: 800px; height: 600px; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="machinome-viewer.js"></script>
  </body>
</html>
"""

#: The clearing interface driven by its OWN declared driver: one full
#: sweep of `clearing`, then a second one. The crossings and stops of
#: every tick are collected off `onCommit`, which is the only place a
#: page can see them.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const run = viewer.run();
  if (run === null) {
    return { run: null };
  }
  const crossings = [];
  const stops = [];
  run.onCommit((frame) => {
    for (const one of frame.crossings) crossings.push({ ...one });
    for (const one of frame.stops) stops.push({ ...one });
  });
  const mounted = {
    identity: run.identity(),
    dt: run.dt(),
    tick: run.tick(),
    bank: run.state(),
  };
  const sweep = async (by) => {
    const mark = crossings.length;
    const settled = run.move('clearing', { by, duration: 1.0 });
    await run.step(240);
    const outcomes = (await settled).map((one) => [
      one.input, one.status, one.admitted]);
    return { outcomes, bank: run.state(),
             crossings: crossings.slice(mark) };
  };
  const restShot = host.querySelector('canvas').toDataURL();
  const first = await sweep(1.0);
  const clearedShot = host.querySelector('canvas').toDataURL();
  const second = await sweep(1.0);
  return { mounted, first, second, stops,
           apiVersion: viewer.apiVersion,
           runsInWorker: run.runsInWorker,
           // The dials TURNED: the clearing reached the geometry.
           clearingMoved: restShot !== clearedShot,
           // And the second sweep moved nothing at all, which is the
           // mechanism.
           secondMovedNothing: clearedShot
             === host.querySelector('canvas').toDataURL() };
}"""


@needs_bundle
@needs_playwright
class ClearingInABrowserTest(TestCase):
    """The Curta's clearing interface, mounted, swept and photographed."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'clearing'
        shutil.copytree(CLEARING, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((CLEARING / 'viewer.json').read_text())

    def test_six_dials_clear_to_their_gaps_and_a_second_sweep_moves_none(self):
        SHOTS.mkdir(exist_ok=True)
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                page.set_default_timeout(300_000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(self.harness_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                result = page.evaluate(DRIVE)
                # Pixels are evidence: the six dials at rest, and the six
                # dials cleared.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__shot = await MachinomeViewer.mount(
                    host, 'viewer.json', {});
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'curta-clearing-at-rest.png'))
                page.evaluate("""async () => {
                  const run = window.__shot.run();
                  const settled = run.move(
                    'clearing', { by: 1.0, duration: 1.0 });
                  await run.step(240);
                  await settled;
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'curta-clearing-cleared.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # 1. It MOUNTED: the refusal this cycle removes is gone.
        mounted = result['mounted']
        self.assertIsNotNone(mounted, 'the handle reported no run')
        self.assertEqual(mounted['identity'],
                         self.document['program']['identity'])
        self.assertEqual(result['apiVersion'], 27)
        self.assertAlmostEqual(mounted['dt'], 1 / 240, places=12)
        # No tick taken, at the published rest values.
        self.assertEqual(mounted['tick'], 0)
        self.assertEqual(mounted['bank']['clearing'], 0)
        for name, rest in REST.items():
            self.assertEqual(mounted['bank'][name], rest)

        first, second = result['first'], result['second']

        # 2. One full sweep leaves every dial within the band half-width
        # of a full turn, in the sweep's own direction, at a value the
        # published gate reads DISENGAGED.
        self.assertEqual(first['outcomes'], [['clearing', 'completed', 1.0]])
        for name in DIALS:
            with self.subTest(dial=name):
                value = first['bank'][name]
                self.assertGreater(value, REST[name])
                self.assertLessEqual(abs(value - 360.0), GAP)
                self.assertTrue(disengaged(value),
                                f'{name} ended engaged at {value!r}')
                # The framework's own number for the same machine.
                self.assertEqual(value, 360.0 - GAP)

        # 3. A SECOND sweep moves no dial at all -- bit for bit, not
        # within a tolerance -- while the clearing input completes its
        # whole travel.
        self.assertEqual(second['outcomes'], [['clearing', 'completed', 1.0]])
        self.assertAlmostEqual(second['bank']['clearing'], 2.0, places=12)
        for name in DIALS:
            with self.subTest(dial=name):
                self.assertEqual(second['bank'][name], first['bank'][name])
        self.assertEqual(second['crossings'], [])

        # 4. No stop is recorded, and every crossing names a dial's own
        # coordinate.
        self.assertEqual(result['stops'], [])
        self.assertGreater(len(first['crossings']), 0)
        for one in first['crossings']:
            self.assertIn(one['coordinate'], DIALS)
            self.assertIn(one['primitive'], ('floor', '>=', '<='))

        self.assertTrue(result['clearingMoved'],
                        'clearing the dials did not change the canvas')
        self.assertTrue(result['secondMovedNothing'],
                        'the second sweep moved something on the canvas')
        print('\nthe Curta clearing in a browser: '
              f"runsInWorker={result['runsInWorker']}\n"
              f"  rest:    {mounted['bank']}\n"
              f"  cleared: {first['bank']}\n"
              f"  again:   {second['bank']}\n"
              f"  crossings on the first sweep: "
              f"{len(first['crossings'])}, on the second: "
              f"{len(second['crossings'])}, stops: {len(result['stops'])}")
