# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The producer's version-13 Bound operates through the public browser handle.

Only the one visible stand-in mesh is substituted when staging; the producer's
program and finite profile table are unchanged. This is a viewer capability
gate, not an installed Curta print/contact proof.
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
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None


FIXTURE = Path(__file__).parents[1] / 'machinome_viewer' / 'widget' / 'src' / 'run' / 'profile-overlap-v13.json'
STAND_IN = FIXTURES / 'spinner' / 'models' / 'spinner_project' / 'hub-Hub-d87c9ca31f37.stl'
SHOT = Path(__file__).parent / '_shots' / 'profile-contact-v13.png'

PAGE = """<!doctype html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#101418"><div id="host" style="width:800px;height:600px"></div>
<script src="machinome-viewer.js"></script></body></html>"""


@needs_bundle
@needs_playwright
class ProfileDocumentBrowserTest(TestCase):
    def test_producer_v13_bound_stops_and_replays_through_hosted_widget(self):
        with tempfile.TemporaryDirectory() as tempdir:
            served = Path(tempdir)
            document = json.loads(FIXTURE.read_text())
            document['root']['children'][0]['model'] = 'wheel.stl'
            (served / 'viewer.json').write_text(json.dumps(document))
            shutil.copy2(STAND_IN, served / 'wheel.stl')
            shutil.copy2(bundle_path(), served / 'machinome-viewer.js')
            (served / 'harness.html').write_text(PAGE)
            errors = []
            with serve_directory(served) as base, sync_playwright() as playwright:
                browser = playwright.chromium.launch(args=[
                    '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
                ])
                try:
                    page = browser.new_page(viewport={'width': 800, 'height': 600})
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('console', lambda message: errors.append(message.text)
                            if message.type == 'error' else None)
                    page.goto(f'{base}/harness.html')
                    result = page.evaluate("""async () => {
                      const viewer = await MachinomeViewer.mount(
                        document.getElementById('host'), 'viewer.json', {});
                      const run = viewer.run();
                      run.pause();
                      const initial = await run.snapshot();
                      const first = run.move('crank', { by: 5, duration: 0.1 });
                      await run.step(24);
                      const firstOutcome = await first;
                      const stopped = run.state();
                      await run.restore(initial);
                      const second = run.move('crank', { by: 5, duration: 0.1 });
                      await run.step(24);
                      const secondOutcome = await second;
                      const replay = run.state();
                      return { api: viewer.apiVersion, dt: run.dt(),
                        identity: run.identity(), initial, stopped, replay,
                        firstOutcome, secondOutcome,
                        canvas: document.querySelectorAll('#host canvas').length };
                    }""")
                    SHOT.parent.mkdir(exist_ok=True)
                    page.screenshot(path=str(SHOT), timeout=30000)
                finally:
                    browser.close()

        self.assertEqual(errors, [], errors)
        self.assertEqual(result['api'], 27)
        self.assertAlmostEqual(result['dt'], 1 / 240, places=12)
        self.assertEqual(result['identity'], document['program']['identity'])
        self.assertEqual(result['canvas'], 1)
        self.assertEqual(result['stopped'], result['replay'])
        for field in ('input', 'status', 'admitted'):
            self.assertEqual(result['firstOutcome'][0][field],
                             result['secondOutcome'][0][field])
        self.assertEqual(result['firstOutcome'][0]['status'], 'blocked')
        self.assertAlmostEqual(result['stopped']['crank'], 0.5, places=7)
