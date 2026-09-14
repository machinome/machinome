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
from solid_node_viewer.bundle import bundle_path, index_path

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
        self.assertEqual(result['apiVersion'], 9)
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


#: The chrome as a maker meets it. Everything below asks the PAGE for
#: what it shows and presses what it shows: the panel is the only thing
#: under test, and the run it drives is the one the previous change
#: proved.
PANEL = "#host .run-controls"
TRANSPORT = "#host .run-transport"


def readout(page, input_id):
    """What the panel says that input's committed position is."""
    return page.text_content(
        f'{PANEL} .run-input[data-input="{input_id}"] .run-readout-value')


def outcome(page, selector):
    return page.text_content(f'{selector} .run-outcome')


@needs_bundle
@needs_playwright
class DrivenOnScreenTest(TestCase):
    """A maker drives the Pascaline module with the on-screen controls.

    The half `run-in-the-worker` deliberately left out: no host code
    here calls `run()` to MOVE anything. Every movement below is a
    button a person can see, and the numbers that come out are the
    framework's own.
    """

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

    def open(self, page):
        page.goto(self.harness_url)
        page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
        page.evaluate("""async () => {
          window.__viewer = await SolidNodeWidget.mount(
            document.getElementById('host'), 'viewer.json', {});
        }""")
        page.wait_for_selector(PANEL)

    def press_instruction(self, page, name):
        """Press an instruction's button and wait for its own report."""
        button = f'{PANEL} .run-instruction[data-instruction="{name}"]'
        page.click(button)
        page.wait_for_selector(f'{button}:not([aria-busy])', timeout=60_000)
        return page.text_content(
            f'{PANEL} .run-instruction-control[data-instruction="{name}"]'
            ' .run-outcome')

    def test_a_maker_drives_the_module_from_the_panel(self):
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
                self.open(page)

                # What a maker meets: three dials, three instructions, a
                # transport -- and no slider and no timeline anywhere.
                labels = page.eval_on_selector_all(
                    f'{PANEL} .run-input .run-input-name',
                    'nodes => nodes.map(node => node.textContent)')
                self.assertEqual(labels, ['hundreds_entry', 'tens_entry',
                                          'units_entry'])
                units = page.eval_on_selector_all(
                    f'{PANEL} .run-input .run-readout-unit',
                    'nodes => nodes.map(node => node.textContent.trim())')
                self.assertEqual(units, ['digit'] * 3)
                buttons = page.eval_on_selector_all(
                    f'{PANEL} .run-instruction',
                    'nodes => nodes.map(node => node.textContent)')
                self.assertEqual(buttons,
                                 ['Add hundred', 'Add one', 'Add ten'])
                self.assertEqual(
                    page.eval_on_selector_all(
                        f'{PANEL} .run-input .run-nudge',
                        'nodes => nodes.length'), 6)
                self.assertEqual(
                    page.eval_on_selector_all(
                        f'{PANEL} .run-input .run-jog',
                        'nodes => nodes.length'), 6)
                for control in ('.run-play', '.run-step', '.run-speed',
                                '.run-elapsed', '.run-reset'):
                    self.assertEqual(
                        page.eval_on_selector_all(
                            f'{TRANSPORT} {control}', 'nodes => nodes.length'),
                        1, control)
                self.assertEqual(
                    page.eval_on_selector_all(
                        '#host input[type=range]', 'nodes => nodes.length'), 0,
                    'a running document must present no slider')
                self.assertEqual(
                    page.eval_on_selector_all(
                        '#host .animation-controls', 'nodes => nodes.length'),
                    0, 'a running document must present no timeline')
                self.assertEqual(readout(page, 'units_entry'), '0.0000')

                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'pascaline-panel-rest.png'))

                # Watched at ten times real time -- which changes how fast
                # the machine is watched and never how finely it is
                # simulated.
                page.select_option(f'{TRANSPORT} .run-speed', '10')

                reports = []
                for press in range(10):
                    reports.append(self.press_instruction(page, 'Add one'))
                    if press == 3:
                        # Inside the carry window (the source's opens
                        # 3.194 digits into a revolution): the tens drum
                        # is being thrown right now.
                        mid = page.evaluate(
                            '() => window.__viewer.run().state()')
                        page.screenshot(
                            path=str(SHOTS / 'pascaline-panel-mid-carry.png'))

                page.screenshot(
                    path=str(SHOTS / 'pascaline-panel-after-ten.png'))
                state = page.evaluate('() => window.__viewer.run().state()')

                # Ten presses, each reported where it was pressed.
                self.assertEqual(reports, ['completed'] * 10)
                # The readout of the input reads ten units.
                self.assertEqual(readout(page, 'units_entry'), '10.0000')
                self.assertEqual(state['units_entry'], 10)
                # CARRY_THROW: the framework's own number for ten
                # `Add one`, which the module's own test pins.
                self.assertLessEqual(
                    abs(state['tens.drum.turn'] - 65.54),
                    1e-9 * max(1.0, 65.54), state['tens.drum.turn'])
                self.assertGreater(mid['tens.drum.turn'], 0)
                self.assertLess(mid['tens.drum.turn'], 65.54)

                # Pause, then walk the run one step at a time.
                page.click(f'{TRANSPORT} .run-play')
                page.wait_for_function(
                    '() => !window.__viewer.run().running()')
                before = page.evaluate('() => window.__viewer.run().tick()')
                page.click(f'{TRANSPORT} .run-step')
                page.wait_for_function(
                    f'() => window.__viewer.run().tick() === {before + 1}',
                    timeout=30_000)
                self.assertFalse(
                    page.evaluate('() => window.__viewer.run().running()'),
                    'a step must not start the run')

                # A jog, ended by the interaction that started it.
                page.select_option(f'{TRANSPORT} .run-speed', '1')
                jog = page.locator(
                    f'{PANEL} .run-input[data-input="tens_entry"]'
                    ' .run-jog[data-direction="+"]')
                jog.hover()
                page.mouse.down()
                page.wait_for_timeout(700)
                during = float(readout(page, 'tens_entry'))
                # Dragged off the control before releasing: the button
                # captured the pointer on press, so the release still
                # reaches it and the machine still stops.
                page.mouse.move(20, 580)
                page.mouse.up()
                page.wait_for_timeout(500)
                after_release = float(readout(page, 'tens_entry'))
                page.wait_for_timeout(500)
                self.assertGreater(during, 0.05,
                                   'the jog admitted no travel')
                self.assertEqual(float(readout(page, 'tens_entry')),
                                 after_release,
                                 'the machine did not stop on release')
                # The readout is the committed position, to the four
                # decimals it writes.
                self.assertAlmostEqual(
                    page.evaluate(
                        '() => window.__viewer.run().state().tens_entry'),
                    after_release, places=4)

                # Reset returns the machine to where it was mounted. The
                # jog started the run, so it is paused first: reset
                # restores the initial snapshot and leaves the transport
                # exactly as it found it, which is why a running machine
                # would go on ticking from zero.
                page.click(f'{TRANSPORT} .run-play')
                page.wait_for_function(
                    '() => !window.__viewer.run().running()')
                page.click(f'{TRANSPORT} .run-reset')
                page.wait_for_function(
                    '() => window.__viewer.run().tick() === 0',
                    timeout=30_000)
                page.wait_for_timeout(200)
                rest = page.evaluate('() => window.__viewer.run().state()')
                self.assertEqual(readout(page, 'units_entry'), '0.0000')
                self.assertEqual(readout(page, 'tens_entry'), '0.0000')
                self.assertEqual(rest['units_entry'], 0)
                self.assertEqual(rest['tens.drum.turn'], 0)
                self.assertEqual(
                    page.text_content(f'{TRANSPORT} .run-elapsed'), '0:00.00')
                self.assertFalse(
                    page.evaluate('() => window.__viewer.run().running()'),
                    'reset must leave the transport as it found it')
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

    def test_a_jog_ends_when_the_pointer_or_the_page_goes_away(self):
        """The two release paths a pointer cannot show.

        A jog left engaged is the failure that damages trust, so the
        interaction is bounded from five sides. Release and lost capture
        are driven by the pointer in the drive test above; the window
        losing focus and the page ceasing to be displayed are dispatched
        here, because a headless browser will not lose focus on its own.
        """
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
                self.open(page)
                jog = page.locator(
                    f'{PANEL} .run-input[data-input="units_entry"]'
                    ' .run-jog[data-direction="+"]')

                for name, stop in (
                    ('the window losing focus',
                     "() => window.dispatchEvent(new Event('blur'))"),
                    ('the page ceasing to be displayed', """() => {
                       Object.defineProperty(document, 'hidden',
                         { configurable: true, get: () => true });
                       document.dispatchEvent(new Event('visibilitychange'));
                     }"""),
                ):
                    start = float(readout(page, 'units_entry'))
                    jog.hover()
                    page.mouse.down()
                    page.wait_for_timeout(500)
                    page.evaluate(stop)
                    page.wait_for_timeout(300)
                    stopped = float(readout(page, 'units_entry'))
                    page.wait_for_timeout(500)
                    page.mouse.up()
                    self.assertGreater(stopped - start, 0.05,
                                       f'the jog never moved before {name}')
                    self.assertEqual(float(readout(page, 'units_entry')),
                                     stopped,
                                     f'the jog outlived {name}')
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

    def test_a_second_request_on_a_busy_input_is_answered_in_place(self):
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
                self.open(page)
                button = (f'{PANEL} .run-instruction'
                          '[data-instruction="Add one"]')
                control = (f'{PANEL} .run-instruction-control'
                           '[data-instruction="Add one"]')
                page.click(button)
                page.click(button)
                page.wait_for_function(
                    "() => document.querySelector("
                    f"'{control} .run-outcome').textContent"
                    ".includes('already owned')", timeout=30_000)
                self.assertIn('already owned', outcome(page, control))
                page.wait_for_selector(f'{button}:not([aria-busy])',
                                       timeout=60_000)
                # The first movement is untouched: one digit, completed.
                self.assertEqual(
                    page.evaluate(
                        '() => window.__viewer.run().state().units_entry'), 1)
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')


@needs_bundle
@needs_playwright
class RunningExportPageTest(TestCase):
    """A self-contained export of a running model, opened offline.

    The standalone export page needs no change to its HTML to carry
    this: it mounts the same bundle with the same default options, and a
    document that carries a program brings its own chrome.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'export'
        shutil.copytree(PASCALINE, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'solid-widget.js')
        # `solid export` names the document manifest.json; the page the
        # package ships points at it.
        (self.out_dir / 'viewer.json').rename(self.out_dir / 'manifest.json')
        shutil.copy2(index_path(), self.out_dir / 'index.html')
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.page_url = f'{base}/index.html'

    def test_the_export_page_runs_the_machine_from_a_static_directory(self):
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
                page.goto(self.page_url)
                page.wait_for_selector('#solid-widget .run-controls',
                                       timeout=60_000)
                page.wait_for_selector('#solid-widget .run-transport')
                self.assertEqual(
                    page.eval_on_selector_all(
                        '#solid-widget input[type=range]',
                        'nodes => nodes.length'), 0)
                button = ('#solid-widget .run-instruction'
                          '[data-instruction="Add one"]')
                page.click(button)
                page.wait_for_selector(f'{button}:not([aria-busy])',
                                       timeout=60_000)
                self.assertEqual(
                    page.text_content(
                        '#solid-widget .run-input[data-input="units_entry"]'
                        ' .run-readout-value'), '1.0000')
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')


@needs_bundle
@needs_playwright
class RepublishedRunTest(TestCase):
    """What `solid develop`'s targeted document update does to a live run.

    The rule is the workflow design's own: a live update must invalidate
    or explicitly migrate incompatible simulation state, never preserve
    coordinates because strings happened to match. `identity` is the
    digest the framework publishes to answer it.
    """

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
        self.source = self.out_dir / 'viewer.json'
        self.document = json.loads(self.source.read_text())

    def republish(self, document):
        """Write a new build of the document, as a rebuild would."""
        self.source.write_text(json.dumps(document))

    def test_a_rebuild_keeps_or_resets_the_run_by_what_it_published(self):
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
                page.evaluate("""async () => {
                  window.__viewer = await SolidNodeWidget.mount(
                    document.getElementById('host'), 'viewer.json', {});
                }""")
                page.wait_for_selector('#host .run-controls')

                # Drive the machine part way through, then hold it still
                # so the comparison is about the republish and not about
                # the clock.
                button = ('#host .run-instruction'
                          '[data-instruction="Add one"]')
                page.click(button)
                page.wait_for_selector(f'{button}:not([aria-busy])',
                                       timeout=60_000)
                page.click('#host .run-transport .run-play')
                page.wait_for_function(
                    '() => !window.__viewer.run().running()')
                before = page.evaluate("""() => {
                  const run = window.__viewer.run();
                  return { tick: run.tick(), elapsed: run.elapsed(),
                           identity: run.identity(), state: run.state() };
                }""")
                self.assertGreater(before['tick'], 0)

                # A cosmetic edit: another colour, the same mechanism.
                cosmetic = json.loads(json.dumps(self.document))
                cosmetic['root']['children'][0]['color'] = '#ff00ff'
                self.republish(cosmetic)
                page.evaluate(
                    '() => window.__viewer.manifestChanged()')
                kept = page.evaluate("""() => {
                  const run = window.__viewer.run();
                  return { tick: run.tick(), elapsed: run.elapsed(),
                           identity: run.identity(), state: run.state() };
                }""")
                self.assertEqual(kept, before,
                                 'the machine did not stand where it was')
                self.assertIn(
                    'kept', page.text_content('#host .run-notice'))

                # An edit to the mechanism: another identity entirely.
                changed = json.loads(json.dumps(self.document))
                changed['program']['identity'] = 'a-different-mechanism'
                self.republish(changed)
                page.evaluate('() => window.__viewer.manifestChanged()')
                page.wait_for_timeout(200)
                after = page.evaluate("""() => {
                  const run = window.__viewer.run();
                  return { tick: run.tick(), elapsed: run.elapsed(),
                           identity: run.identity(), state: run.state() };
                }""")
                self.assertEqual(after['identity'], 'a-different-mechanism',
                                 'the republished document was not read')
                self.assertEqual(after['tick'], 0)
                self.assertEqual(after['elapsed'], 0)
                self.assertEqual(after['state']['units_entry'], 0)
                self.assertEqual(after['state']['units.drum.turn'], 0)
                self.assertIn('reset', page.text_content('#host .run-notice'))
                self.assertEqual(
                    page.text_content(
                        '#host .run-input[data-input="units_entry"]'
                        ' .run-readout-value'), '0.0000')
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')
