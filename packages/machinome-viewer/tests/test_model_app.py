# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model's own app, shown by the viewer in a real browser (OpenSpec
`show-a-models-own-app`, design Decision 15, B1 to B6).

The model is `tests/fixtures/calculator/`, the framework's clocked
`Calculator` published as a version 8 build, reused verbatim; the app is
`tests/fixtures/calculator-app/`'s, bundled into a temporary copy of that
build with the provider's own `bundle_app`, its record written into the
copy's `viewer.json` as `app`, as the framework's build does. Nothing here
poses the machine: the app plays its declared instructions.

B1 to B5 serve the copy statically; B6 serves it through this package's own
development `Session`, on a port bound free, and tells the open page that a
document naming the app's new files was published, as `machinome develop`
does.
"""

import io
import json
import os
import shutil
import socket
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase

from tests.support import (
    CALCULATOR, FIXTURES, needs_bundle, needs_playwright, serve_directory,
)
from machinome.viewer.web.bundle import bundle_path, index_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover - the bench has Pillow
    Image = None

APP_FIXTURE = FIXTURES / 'calculator-app'
DIGITS = ('w0.digit', 'w1.digit', 'w2.digit', 'w3.digit')
CHROMIUM_ARGS = ['--no-sandbox', '--disable-gpu', '--use-angle=swiftshader']

HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>model app harness</title>
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


def bundle_into(project, build):
    """Bundle the fixture app of `project` into `build` and write its record
    into `build/viewer.json`; answer the record."""
    import machinome.viewer.web as web
    record = web.bundle_app(str(project / 'app' / 'index.tsx'), str(project),
                            str(build))
    write_record(build, {'script': record['script'],
                         **({'stylesheet': record['stylesheet']}
                            if record['stylesheet'] else {})})
    return record


def write_record(build, app, name='viewer.json'):
    """Replace the document's `app` record, atomically, as a build does."""
    path = build / name
    document = json.loads(path.read_text())
    document['app'] = app
    staged = build / f'.{name}.tmp'
    staged.write_text(json.dumps(document))
    os.replace(staged, path)


def drawn(png):
    """Whether a screenshot holds more than one colour: the model drawn."""
    if Image is None:
        return True
    image = Image.open(io.BytesIO(png)).convert('RGB')
    colours = image.getcolors(maxcolors=1 << 16)
    return colours is None or len(colours) > 8


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    assert port != 9010
    return port


class _Browser(TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        base = Path(self.tempdir.name)
        self.project = base / 'project'
        shutil.copytree(APP_FIXTURE, self.project)
        self.build = base / 'build'
        shutil.copytree(CALCULATOR, self.build)
        self.record = bundle_into(self.project, self.build)
        self.errors = []

    @contextmanager
    def browsing(self):
        """A page in headless Chromium, the browser closed before
        Playwright stops."""
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=CHROMIUM_ARGS)
            try:
                page = browser.new_page(viewport={'width': 1000, 'height': 700})
                page.set_default_timeout(120_000)
                page.on('pageerror',
                        lambda error: self.errors.append(str(error)))
                page.on('console', lambda message: self.errors.append(
                    message.text) if message.type == 'error' else None)
                yield page
            finally:
                browser.close()

    def serve_static(self):
        server = serve_directory(self.build)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        return base

    def export(self):
        """The copy completed as `machinome export` writes it."""
        (self.build / 'viewer.json').rename(self.build / 'manifest.json')
        shutil.copy2(bundle_path(), self.build / 'machinome-viewer.js')
        shutil.copy2(index_path(), self.build / 'index.html')

    def harness(self):
        shutil.copy2(bundle_path(), self.build / 'machinome-viewer.js')
        (self.build / 'harness.html').write_text(HARNESS_PAGE)

    def wait_for_app(self, page):
        page.wait_for_selector('.calculator-app .calculator-app-key')

    def digits(self, page):
        return page.evaluate("""() => Object.fromEntries(
          [...document.querySelectorAll('.calculator-app-readout')].map(
            (one) => [one.dataset.readout,
                      Number(one.querySelector('.calculator-app-digit').textContent)]))""")

    def keys_disabled(self, page):
        return page.evaluate("""() => [...document.querySelectorAll(
          '.calculator-app-key')].map((key) => key.disabled)""")

    def press_stroke(self, page):
        """B2: Stroke disables both keys until the drawing lands, then the
        digits read the committed bank."""
        page.click('.calculator-app-key[data-instruction="Set four"]')
        page.wait_for_function("""() => [...document.querySelectorAll(
          '.calculator-app-key')].every((key) => !key.disabled)""")
        page.click('.calculator-app-key[data-instruction="Stroke"]')
        self.assertEqual(self.keys_disabled(page), [True, True])
        started = time.monotonic()
        page.wait_for_function("""() => [...document.querySelectorAll(
          '.calculator-app-key')].every((key) => !key.disabled)""")
        # The instruction is drawn over its declared two seconds.
        self.assertGreater(time.monotonic() - started, 1.0)
        return self.digits(page)


@needs_bundle
@needs_playwright
class ExportPageTest(_Browser):

    def test_b1_b2_the_export_page_shows_the_app_and_its_keys_play_the_machine(self):
        self.export()
        base = self.serve_static()
        with self.browsing() as page:
            page.goto(f'{base}/index.html')
            self.wait_for_app(page)
            # B1: the app is drawn; no panel, no animation bar of the viewer's.
            self.assertEqual(page.locator('.calculator-app-key').count(), 2)
            self.assertEqual(page.locator('.clocked-controls').count(), 0)
            self.assertEqual(page.locator('.animation-controls').count(), 0)
            # The inspector's sidebar stands beside the app.
            self.assertEqual(page.locator('.machinome-inspector-sidebar').count(), 1)
            self.assertEqual(
                page.evaluate("""() => document.querySelector(
                  '.machinome-inspector-viewer .machinome-app') !== null"""), True)
            self.assertEqual(self.digits(page), dict.fromkeys(DIGITS[::-1], 0))
            # B2.
            digits = self.press_stroke(page)
            self.assertEqual(digits, {'w3.digit': 0, 'w2.digit': 0,
                                      'w1.digit': 0, 'w0.digit': 4})
            picture = page.locator('.calculator-app-picture')
            self.assertTrue(drawn(picture.screenshot()))
        self.assertEqual(self.errors, [])


@needs_bundle
@needs_playwright
class HarnessTest(_Browser):

    def test_b3_the_canvas_follows_the_place_the_app_gives_it(self):
        self.harness()
        base = self.serve_static()
        with self.browsing() as page:
            page.goto(f'{base}/harness.html')
            page.evaluate("""async () => {
              window.viewer = await MachinomeViewer.mount(
                document.getElementById('host'), 'viewer.json', {});
            }""")
            self.wait_for_app(page)
            size = """() => {
              const canvas = document.querySelector('canvas');
              const place = document.querySelector('.calculator-app-picture');
              return { inside: place.contains(canvas),
                       canvas: [canvas.clientWidth, canvas.clientHeight],
                       buffer: [canvas.width, canvas.height],
                       place: [place.clientWidth, place.clientHeight] };
            }"""
            page.wait_for_function("""() => {
              const canvas = document.querySelector('canvas');
              const place = document.querySelector('.calculator-app-picture');
              return canvas.clientHeight === place.clientHeight; }""")
            first = page.evaluate(size)
            self.assertTrue(first['inside'])
            self.assertEqual(first['canvas'], first['place'])
            self.assertEqual(first['canvas'][0], 800)
            self.assertEqual(first['canvas'][1], 600 - 56)
            page.evaluate("""() => {
              const host = document.getElementById('host');
              host.style.width = '600px'; host.style.height = '400px'; }""")
            page.wait_for_function("""() => document.querySelector('canvas')
              .clientHeight === 400 - 56""")
            second = page.evaluate(size)
            self.assertEqual(second['canvas'], [600, 344])
            self.assertEqual(second['place'], [600, 344])
            self.assertEqual(second['buffer'], [600, 344])
        self.assertEqual(self.errors, [])

    def test_b4_a_refusal_record_shows_the_notice_over_the_drawn_model(self):
        write_record(self.build, {'refusal':
                                  "CalculatorApp.app = 'app/index.tsx' names "
                                  'a file that does not exist'})
        self.harness()
        base = self.serve_static()
        with self.browsing() as page:
            page.goto(f'{base}/harness.html')
            page.evaluate("""async () => {
              window.viewer = await MachinomeViewer.mount(
                document.getElementById('host'), 'viewer.json', {});
            }""")
            notice = page.locator('.machinome-app-refusal')
            notice.wait_for()
            self.assertEqual(notice.get_attribute('role'), 'alert')
            self.assertEqual(
                notice.text_content(),
                "This model's app is not shown: CalculatorApp.app = "
                "'app/index.tsx' names a file that does not exist")
            self.assertEqual(page.locator('.clocked-controls').count(), 0)
            self.assertEqual(page.locator('.calculator-app').count(), 0)
            page.wait_for_timeout(500)
            self.assertTrue(drawn(page.locator('canvas').screenshot()))
        self.assertEqual(
            [one for one in self.errors if 'app is not shown' not in one], [])

    def test_b5_a_host_that_suppresses_the_chrome_requests_no_app(self):
        self.harness()
        base = self.serve_static()
        with self.browsing() as page:
            requested = []
            page.on('request', lambda request: requested.append(request.url))
            page.goto(f'{base}/harness.html')
            result = page.evaluate("""async () => {
              const viewer = await MachinomeViewer.mount(
                document.getElementById('host'), 'viewer.json',
                { driverControls: 'none' });
              const machine = viewer.machine();
              machine.move('operand', { to: 4 });
              machine.move('crank', { by: 360 });
              return { app: document.querySelector('.calculator-app') !== null,
                       panel: document.querySelector('.clocked-controls') !== null,
                       bank: machine.state() };
            }""")
            page.wait_for_timeout(500)
        self.assertEqual(result['app'], False)
        self.assertEqual(result['panel'], False)
        self.assertEqual(result['bank']['w0.digit'], 4)
        self.assertEqual([url for url in requested if '/app-' in url], [])
        self.assertEqual(self.errors, [])


@needs_bundle
@needs_playwright
class DevelopmentPageTest(_Browser):

    def setUp(self):
        super().setUp()
        from machinome.viewer.web.session import Session
        self.session = Session(self.build, port=free_port()).start()
        self.addCleanup(self.session.stop)
        self.url = f'http://127.0.0.1:{self.session.port}/'

    def test_b1_b2_the_development_page_shows_the_app_beside_the_sidebar(self):
        with self.browsing() as page:
            page.goto(self.url)
            self.wait_for_app(page)
            self.assertEqual(page.locator('.clocked-controls').count(), 0)
            self.assertEqual(page.locator('.animation-controls').count(), 0)
            self.assertEqual(page.locator('.machinome-inspector-sidebar').count(), 1)
            digits = self.press_stroke(page)
            self.assertEqual(digits['w0.digit'], 4)
        self.assertEqual(self.errors, [])

    def test_b6_the_open_development_page_shows_the_edited_app_the_picture_standing(self):
        with self.browsing() as page:
            requested = []
            page.on('request', lambda request: requested.append(request.url))
            page.goto(self.url)
            self.wait_for_app(page)
            page.wait_for_timeout(500)
            page.evaluate("""() => {
              window.__marker = 'the same page';
              window.__canvas = document.querySelector('canvas');
              window.__sheet = document.querySelector(
                'link[rel="stylesheet"][href*="app-"]');
            }""")
            self.assertEqual(
                page.locator('.calculator-app-label').first.text_content(),
                'Window')
            mark = len(requested)
            readout = self.project / 'app' / 'Readout.tsx'
            readout.write_text(readout.read_text().replace(
                '>Window<', '>Register<'))
            record = bundle_into(self.project, self.build)
            self.assertNotEqual(record['script'], self.record['script'])
            self.session.reload()
            page.wait_for_function("""() => {
              const label = document.querySelector('.calculator-app-label');
              return label !== null && label.textContent === 'Register'; }""")
            page.wait_for_timeout(500)
            after = page.evaluate("""() => ({
              marker: window.__marker,
              sameCanvas: document.querySelector('canvas') === window.__canvas,
              oldSheet: window.__sheet === null ? null : window.__sheet.isConnected,
              sheets: [...document.querySelectorAll(
                'link[rel="stylesheet"][href*="app-"]')].length,
              apps: document.querySelectorAll('.calculator-app').length,
              panel: document.querySelector('.clocked-controls') !== null,
            })""")
            self.assertEqual(after['marker'], 'the same page')
            self.assertTrue(after['sameCanvas'])
            self.assertEqual(after['oldSheet'], False)
            self.assertEqual(after['sheets'], 1)
            self.assertEqual(after['apps'], 1)
            self.assertFalse(after['panel'])
            self.assertTrue(drawn(page.locator('canvas').screenshot()))
            fetched = requested[mark:]
            self.assertEqual([url for url in fetched if '/models/' in url], [])
            self.assertIn(f'/build/{record["script"]}',
                          ' '.join(fetched))
        self.assertEqual(self.errors, [])
