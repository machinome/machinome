# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The acceptance: the pin tumbler lock running in a real browser.

`tests/fixtures/lock/viewer.json` is the lock's own published build,
verbatim -- a version 5 document three of whose spans READ OTHER
COORDINATES, and which this viewer refused by name until this cycle.
What this proves is the mechanism: the plug turns only while five pins
stand at the shear line, and the key is captured while the plug stands
turned. Nothing here poses anything; everything is driven by the
document's own declared instructions.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    LOCK, needs_bundle, needs_playwright, published_lock, serve_directory,
)
from machinome_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


class LockFixtureTest(TestCase):
    """The committed `lock` fixture is complete on disk.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas a browser test later.
    """

    def setUp(self):
        self.document = json.loads((LOCK / 'viewer.json').read_text())

    def test_every_model_path_resolves_beside_the_document(self):
        paths = model_paths(self.document['root'])
        self.assertEqual(len(paths), 15)
        self.assertEqual(len(set(paths)), 11)
        missing = [path for path in sorted(set(paths))
                   if not (LOCK / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')

    def test_the_document_is_the_lock_s_own_published_build(self):
        self.assertEqual((LOCK / 'viewer.json').stat().st_size, 26277)
        self.assertEqual(self.document['version'], 5)
        self.assertEqual(self.document['root']['name'], 'PinTumblerLock')
        program = self.document['program']
        self.assertTrue(program['identity'].startswith('b45402a5'))
        self.assertEqual(list(self.document['drivers']),
                         ['insertion', 'rotation'])
        self.assertEqual(self.document['drivers']['insertion']['unit'], 'mm')
        self.assertEqual(self.document['drivers']['insertion']['range'],
                         [-60.0, 0.0])
        self.assertEqual(self.document['drivers']['rotation']['unit'], 'deg')
        self.assertEqual(self.document['drivers']['rotation']['range'],
                         [-90.0, 90.0])
        self.assertEqual(len(self.document['instructions']), 6)
        self.assertEqual(len(program['coordinates']), 16)
        self.assertEqual(len(program['edges']), 14)
        self.assertEqual(len(self.document['bindings']), 23)
        self.assertEqual(len(self.document['pieces']), 11)

    def test_three_of_its_spans_read_other_coordinates(self):
        spans = self.document['program']['spans']
        # The plug reaches the five lifts only THROUGH the bindings.
        for side in ('low', 'high'):
            text = spans['plug.turn'][side]['expression']
            for name in ('_b10', '_b13', '_b16', '_b19', '_b22'):
                self.assertIn(name, text)
            self.assertNotIn('plug.p1.lift', text)
        self.assertIn('plug.turn',
                      spans['plug.key.insert']['low']['expression'])

    def test_staging_the_fixture_copies_it_whole(self):
        with tempfile.TemporaryDirectory() as tempdir:
            staged = published_lock(Path(tempdir) / 'lock')
            self.assertTrue((staged / 'viewer.json').is_file())
            document = json.loads((staged / 'viewer.json').read_text())
            for path in set(model_paths(document['root'])):
                self.assertTrue((staged / path).is_file(), path)


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>pin tumbler lock harness</title>
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

#: The lock driven by its OWN declared instructions, in the order the
#: mechanism has: turn the seated plug, fail to withdraw the captured
#: key, return the plug, withdraw the key, fail to turn the empty plug.
#:
#: Every instruction is stepped for its whole declared duration at the
#: viewer's own step size, awaiting the outcome of each; the stops of
#: every tick are collected off `onCommit`, which is the only place a
#: page can see them.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const run = viewer.run();
  if (run === null) {
    return { run: null };
  }
  const stops = [];
  run.onCommit((frame) => {
    for (const stop of frame.stops) stops.push({ ...stop });
  });
  const mounted = {
    identity: run.identity(),
    dt: run.dt(),
    tick: run.tick(),
    bank: run.state(),
    instructions: Object.keys(viewer.instructions()).sort(),
  };
  const drive = async (name, ticks) => {
    const mark = stops.length;
    const settled = run.trigger(name);
    await run.step(ticks);
    const outcomes = (await settled).map((one) => [
      one.input, one.status, one.admitted]);
    return { name, outcomes, bank: run.state(),
             stops: stops.slice(mark) };
  };
  const steps = [];
  const restShot = host.querySelector('canvas').toDataURL();
  // 1. The key is seated at rest: the plug turns its whole 90.
  steps.push(await drive('Turn the plug', 360));
  const turnedShot = host.querySelector('canvas').toDataURL();
  // 2. The CAPTURE: the key may not come back out of a turned plug.
  steps.push(await drive('Withdraw the key', 576));
  const capturedShot = host.querySelector('canvas').toDataURL();
  // 3. Return the plug, and the key comes out.
  steps.push(await drive('Return the plug', 360));
  steps.push(await drive('Withdraw the key', 576));
  // 4. With the key out, the plug will not turn at all.
  steps.push(await drive('Turn the plug', 360));
  return { mounted, steps, apiVersion: viewer.apiVersion,
           runsInWorker: run.runsInWorker,
           // The plug TURNING reached the geometry; the captured key
           // moved nothing, which is the mechanism, so those two agree.
           turnedMoved: restShot !== turnedShot,
           captureMovedNothing: turnedShot === capturedShot };
}"""


@needs_bundle
@needs_playwright
class LockInABrowserTest(TestCase):
    """The lock's own published document, mounted, run and photographed."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'lock'
        shutil.copytree(LOCK, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((LOCK / 'viewer.json').read_text())

    def test_the_plug_turns_only_when_the_key_is_seated(self):
        SHOTS.mkdir(exist_ok=True)
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.set_default_timeout(180_000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(self.harness_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                result = page.evaluate(DRIVE)
                # The plug turned with the key seated, and the key
                # stopped by the turned plug: pixels are evidence.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__shot = await MachinomeViewer.mount(
                    host, 'viewer.json', {});
                  const run = window.__shot.run();
                  const turn = run.trigger('Turn the plug');
                  await run.step(360);
                  await turn;
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'lock-plug-turned-key-seated.png'))
                page.evaluate("""async () => {
                  const run = window.__shot.run();
                  const out = run.trigger('Withdraw the key');
                  await run.step(576);
                  await out;
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'lock-key-held-by-turned-plug.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # It MOUNTED: the refusal this cycle removes is gone.
        mounted = result['mounted']
        self.assertIsNotNone(result.get('mounted'), 'the handle reported no run')
        self.assertEqual(mounted['identity'],
                         self.document['program']['identity'])
        self.assertEqual(result['apiVersion'], 25)
        self.assertAlmostEqual(mounted['dt'], 1 / 240, places=12)
        # No step taken, at the published rest values.
        self.assertEqual(mounted['tick'], 0)
        self.assertEqual(mounted['bank']['plug.turn'], 0)
        self.assertEqual(mounted['bank']['plug.key.insert'], 0)
        self.assertEqual(mounted['instructions'], [
            'Advance one pin', 'Back one pin', 'Return the plug',
            'Seat the key', 'Turn the plug', 'Withdraw the key',
        ])

        turn, capture, back, out, blocked = result['steps']

        # 1. The key seated: the plug turns its whole 90.
        self.assertEqual(turn['outcomes'], [['rotation', 'completed', 90.0]])
        self.assertAlmostEqual(turn['bank']['plug.turn'], 90.0, places=9)
        self.assertEqual(turn['stops'], [])

        # 2. THE CAPTURE: the key is stopped at once, having admitted
        # nothing, and the plug has not moved.
        self.assertEqual(capture['outcomes'],
                         [['insertion', 'blocked', 0.0]])
        self.assertEqual(capture['bank']['plug.key.insert'], 0)
        self.assertAlmostEqual(capture['bank']['plug.turn'], 90.0, places=9)
        self.assertEqual(len(capture['stops']), 1)
        stop = capture['stops'][0]
        self.assertEqual(stop['coordinate'], 'plug.key.insert')
        self.assertEqual(stop['bound'], 'low')
        # The bound EVALUATED at the committed state, which is where the
        # key already stands -- not the -60 it reads with the plug home.
        self.assertEqual(stop['value'], 0.0)
        self.assertEqual(stop['t'], 0.0)
        self.assertEqual(stop['inputs'], ['insertion'])

        # 3. Return the plug and the key comes out, its whole travel.
        self.assertEqual(back['outcomes'], [['rotation', 'completed', -90.0]])
        self.assertAlmostEqual(back['bank']['plug.turn'], 0.0, places=9)
        self.assertEqual(out['outcomes'], [['insertion', 'completed', -60.0]])
        self.assertAlmostEqual(out['bank']['plug.key.insert'], -60.0, places=9)

        # 4. With the key withdrawn, the plug will not turn at all.
        self.assertEqual(blocked['outcomes'],
                         [['rotation', 'blocked', 0.0]])
        self.assertEqual(blocked['bank']['plug.turn'], 0)
        named = [(one['coordinate'], one['bound'], one['value'], one['t'],
                  tuple(one['inputs'])) for one in blocked['stops']]
        self.assertIn(('plug.turn', 'high', 0.0, 0.0, ('rotation',)), named)

        self.assertTrue(result['turnedMoved'],
                        'turning the plug did not change the canvas')
        self.assertTrue(result['captureMovedNothing'],
                        'the captured key moved something on the canvas')
        print('\nthe lock in a browser: '
              f"runsInWorker={result['runsInWorker']}\n"
              f"  turned:   {turn['bank']['plug.turn']!r} deg, "
              f"{turn['outcomes']}\n"
              f"  captured: insert={capture['bank']['plug.key.insert']!r}, "
              f"{capture['outcomes']}, stop={capture['stops']}\n"
              f"  returned: {back['outcomes']}\n"
              f"  withdrew: insert={out['bank']['plug.key.insert']!r}, "
              f"{out['outcomes']}\n"
              f"  blocked:  turn={blocked['bank']['plug.turn']!r}, "
              f"{blocked['outcomes']}, stops={blocked['stops']}")
