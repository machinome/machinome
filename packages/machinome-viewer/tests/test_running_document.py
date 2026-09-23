# machinome-viewer - the browser viewer for machinome models
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
    FIXTURES, TOUCHED, needs_bundle, needs_playwright, published_touched,
    serve_directory,
)
from machinome_viewer.bundle import bundle_path, index_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

PASCALINE = FIXTURES / 'pascaline'

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


class TouchedFixtureTest(TestCase):
    """The committed `touched` fixture is complete on disk.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas three browser tests later.
    """

    def test_every_model_path_resolves_beside_the_document(self):
        document = json.loads((TOUCHED / 'viewer.json').read_text())
        paths = model_paths(document['root'])
        self.assertEqual(len(paths), 42)
        missing = [path for path in sorted(set(paths))
                   if not (TOUCHED / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')
        self.assertEqual(len(set(paths)), 15)

    def test_the_document_is_a_version_5_run_carrying_six_controls(self):
        document = json.loads((TOUCHED / 'viewer.json').read_text())
        self.assertEqual(document['version'], 5)
        self.assertEqual(document['root']['name'], 'Touched')
        self.assertIsNotNone(document.get('program'))
        self.assertEqual(list(document['controls']), [
            'hundreds dial', 'tens dial', 'turn hundreds', 'turn tens',
            'turn units', 'units dial',
        ])

    def test_staging_the_fixture_copies_it_whole(self):
        with tempfile.TemporaryDirectory() as tempdir:
            staged = published_touched(Path(tempdir) / 'touched')
            self.assertTrue((staged / 'viewer.json').is_file())
            document = json.loads((staged / 'viewer.json').read_text())
            for path in set(model_paths(document['root'])):
                self.assertTrue((staged / path).is_file(), path)


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
    <script src="machinome-viewer.js"></script>
  </body>
</html>
"""

#: Ten `Add one`, each stepped for its whole declared second at the
#: viewer's own step size, awaiting the outcome of every one.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
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
    // A document that declares no control answers plainly, rather than
    // with an error or an absent operation (OpenSpec
    // `drive-the-run-by-touch`, design D15).
    controls: viewer.controls(),
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
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        play = json.loads((PASCALINE / 'viewer.json').read_text())
        play['version'] = 9
        play.pop('clocked', None)
        play['drivers']['play_input'] = {
            'default': 0.0, 'range': None, 'unit': None,
            'dtype': None, 'scale': None,
        }
        play['program']['coordinates']['play_input'] = {
            'kind': 'input', 'initial': 0.0, 'domain': None,
        }
        play['program']['coordinates']['play_retained'] = {
            'kind': 'coordinate', 'initial': 0.0,
            'unit': None, 'domain': None,
        }
        play['program']['edges'].append({
            'kind': 'play',
            'needs': ['play_input', 'play_retained'],
            'gives': ['play_retained'],
            'description': 'play_input plays play_retained',
            'stated_by': 'Browser smoke', 'low': -10.0, 'high': 10.0,
        })
        play['program']['sources']['play_input'] = ['play_input']
        play['program']['sources']['play_retained'] = ['play_input']
        (self.out_dir / 'play.json').write_text(json.dumps(play))
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
                    'typeof MachinomeViewer !== "undefined"')
                # The rest pose, photographed before anything is asked of
                # the run: pixels are evidence, and a green suite is not
                # an inspection.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__rest = await MachinomeViewer.mount(
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
        self.assertEqual(result['apiVersion'], 25)
        self.assertEqual(result['controls'], [])
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
        self.assertTrue(result['moved'],
                        'the rendered canvas did not change')
        print(f"\nrunsInWorker={result['runsInWorker']} "
              f"wall={result['wall']:.0f} ms for 2400 ticks "
              f"tens.drum.turn={result['state']['tens.drum.turn']!r}")

    def test_version_nine_play_runs_on_a_real_page(self):
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                result = page.evaluate("""async () => {
                  const viewer = await MachinomeViewer.mount(
                    document.getElementById('host'), 'play.json', {});
                  const run = viewer.run();
                  const settled = run.move(
                    'play_input', {by: 100, duration: 1});
                  await run.step(240);
                  return {state: run.state(), outcome: await settled};
                }""")
            finally:
                browser.close()
        self.assertEqual(errors, [])
        self.assertEqual(result['state']['play_input'], 100)
        self.assertEqual(result['state']['play_retained'], 90)
        self.assertEqual(result['outcome'][0]['status'], 'completed')

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
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((PASCALINE / 'viewer.json').read_text())

    def open(self, page):
        page.goto(self.harness_url)
        page.wait_for_function('typeof MachinomeViewer !== "undefined"')
        page.evaluate("""async () => {
          window.__viewer = await MachinomeViewer.mount(
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
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        # `machinome export` names the document manifest.json; the page the
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
                page.wait_for_selector('#machinome-viewer .run-controls',
                                       timeout=60_000)
                page.wait_for_selector('#machinome-viewer .run-transport')
                self.assertEqual(
                    page.eval_on_selector_all(
                        '#machinome-viewer input[type=range]',
                        'nodes => nodes.length'), 0)
                button = ('#machinome-viewer .run-instruction'
                          '[data-instruction="Add one"]')
                page.click(button)
                page.wait_for_selector(f'{button}:not([aria-busy])',
                                       timeout=60_000)
                self.assertEqual(
                    page.text_content(
                        '#machinome-viewer .run-input[data-input="units_entry"]'
                        ' .run-readout-value'), '1.0000')
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')


@needs_bundle
@needs_playwright
class RepublishedRunTest(TestCase):
    """What `machinome develop`'s targeted document update does to a live run.

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
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
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
                    'typeof MachinomeViewer !== "undefined"')
                page.evaluate("""async () => {
                  window.__viewer = await MachinomeViewer.mount(
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


#: What a maker meets when the document declares controls on its parts
#: (OpenSpec `drive-the-run-by-touch`). Everything below asks the PAGE
#: where the dial is and then sends a real mouse there: no host code
#: calls `run()` to move anything, and the geometry under test is the
#: one the widget computed from the document's own tree.
TOUCHED_PANEL = '#host .run-controls'
LABEL = '#host .part-outcome'
CANVAS = '#host canvas'

#: The dial is a 3.5-pixel stand-in cube, so a press lands essentially
#: ON the joint's axle and a drag has to travel before the in-plane
#: angle is worth anything. These two distances were MEASURED against
#: this fixture and this default camera: 120 px to the left is the first
#: whole quantum (36 degrees of sweep, one digit), and 200 px downward is
#: well past one quantum the other way -- the way the ratchet forbids.
FORWARD_DRAG = (-120, 0)
BLOCKED_DRAG = (0, 200)


@needs_bundle
@needs_playwright
class TouchedByHandTest(TestCase):
    """A maker presses and turns the Pascaline module's own dials.

    The document is `tests/fixtures/touched/viewer.json` -- the module's
    classes published with a `controls` table, verbatim. Its three dials
    each carry a `Button` and a `Turn` at `per_unit -36.0`, and at the
    rest bank `units.input.turn` stands at its own declared stop
    (`high = 36·ceil(turn/36)`, which at rest IS the coordinate's own
    value), so the very first backward quantum is refused travel.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = published_touched(Path(self.tempdir.name) / 'touched')
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((TOUCHED / 'viewer.json').read_text())
        SHOTS.mkdir(exist_ok=True)

    def browser(self, playwright):
        return playwright.chromium.launch(args=[
            '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
        ])

    def open(self, page, options='{}'):
        self.errors = []
        page.on('pageerror', lambda error: self.errors.append(str(error)))
        page.on('console', lambda message: self.errors.append(message.text)
                if message.type == 'error' else None)
        page.goto(self.harness_url)
        page.wait_for_function('typeof MachinomeViewer !== "undefined"')
        page.evaluate("""async (options) => {
          window.__viewer = await MachinomeViewer.mount(
            document.getElementById('host'), 'viewer.json', options);
          window.__out = [];
          window.__viewer.run().onOutcome((one) => window.__out.push(
            [one.status, one.admitted]));
        }""", json.loads(options))
        page.wait_for_selector(TOUCHED_PANEL)
        # One settled frame, so the projection `controls()` reports is
        # the projection a press will meet.
        page.wait_for_timeout(500)

    def controls(self, page):
        listing = page.evaluate('() => window.__viewer.controls()')
        return {one['name']: one for one in listing}, listing

    def drag(self, page, point, travel, steps=10, settle=900):
        """Press at `point` and sweep by `travel`, a step at a time."""
        page.mouse.move(point['x'], point['y'])
        page.mouse.down()
        for step in range(1, steps + 1):
            page.mouse.move(point['x'] + travel[0] * step / steps,
                            point['y'] + travel[1] * step / steps)
            page.wait_for_timeout(30)
        page.wait_for_timeout(settle)

    def test_the_handle_lists_the_controls_the_document_declares(self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page)
                by_name, listing = self.controls(page)

                self.assertEqual([one['name'] for one in listing],
                                 list(self.document['controls']))
                self.assertEqual([one['kind'] for one in listing],
                                 ['button', 'button', 'turn', 'turn',
                                  'turn', 'button'])
                for name, control in by_name.items():
                    declared = self.document['controls'][name]
                    self.assertEqual(control['part'], declared['part'], name)
                    self.assertEqual(control['joint'], declared['joint'], name)
                    self.assertEqual(control['coordinate'],
                                     declared['coordinate'], name)
                    if declared['kind'] == 'button':
                        self.assertEqual(control['instruction'],
                                         declared['instruction'], name)
                        self.assertNotIn('input', control)
                    else:
                        self.assertEqual(control['input'], declared['input'],
                                         name)
                        self.assertEqual(control['perUnit'], -36.0, name)
                    # Every part is on screen, and a press reaches it.
                    self.assertIsNotNone(control['rect'], name)
                    self.assertIsNotNone(control['point'], name)
                    point = control['point']
                    rect = control['rect']
                    self.assertGreaterEqual(point['x'], rect['x'])
                    self.assertLessEqual(point['x'],
                                         rect['x'] + rect['width'])
                    self.assertGreaterEqual(point['y'], rect['y'])
                    self.assertLessEqual(point['y'],
                                         rect['y'] + rect['height'])

                # A part the navigator is not showing reports no
                # position, and is not touchable either.
                page.evaluate("""() => window.__viewer.setVisible(
                  ['units', 'input', 'dial'], false)""")
                page.wait_for_timeout(200)
                hidden, _ = self.controls(page)
                self.assertIsNone(hidden['turn units']['rect'])
                self.assertIsNone(hidden['turn units']['point'])
                self.assertEqual(hidden['turn units']['input'], 'units_entry')
                self.assertIsNotNone(hidden['turn tens']['point'])
                page.mouse.move(by_name['turn units']['point']['x'],
                                by_name['turn units']['point']['y'])
                page.wait_for_timeout(200)
                self.assertEqual(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), '')
                page.evaluate("""() => window.__viewer.setVisible(
                  ['units', 'input', 'dial'], true)""")
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def test_the_listing_answers_whether_or_not_the_affordance_is_shown(self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page, '{"partControls": "none"}')
                by_name, listing = self.controls(page)
                # The full listing, rects and all: what a presentation
                # choice gates is the pixels and the pointer, never the
                # interface.
                self.assertEqual(len(listing), 6)
                self.assertIsNotNone(by_name['turn units']['rect'])
                self.assertIsNotNone(by_name['turn units']['point'])

                # And no part shows a cursor, a highlight or a name.
                point = by_name['units dial']['point']
                page.mouse.move(point['x'], point['y'])
                page.wait_for_timeout(300)
                self.assertEqual(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), '')
                self.assertIsNone(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').getAttribute('title')"))
                before = page.evaluate('() => window.__viewer.view()')
                page.mouse.down()
                page.mouse.move(point['x'] - 120, point['y'])
                page.mouse.up()
                page.wait_for_timeout(300)
                after = page.evaluate('() => window.__viewer.view()')
                self.assertNotEqual(before['camera'], after['camera'],
                                    'pressing a part must move the camera')
                self.assertEqual(page.evaluate('() => window.__out'), [])
                self.assertEqual(
                    page.evaluate('() => window.__viewer.run()'
                                  '.state().units_entry'), 0)
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def test_a_press_on_the_dial_advances_it(self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page)

                # The dial is a 3.5-pixel stand-in cube in the whole
                # model, so the affordance is photographed with the
                # input assembly focused, where a highlight is something
                # a person can see. The pair is the evidence: the same
                # frame with the pointer away and on the dial.
                page.evaluate(
                    "() => window.__viewer.setRoot(['units', 'input'])")
                page.wait_for_timeout(600)
                close, _ = self.controls(page)
                near = close['units dial']['point']
                self.assertIsNotNone(near, 'the dial is not reachable close up')
                page.mouse.move(20, 560)
                page.wait_for_timeout(300)
                page.screenshot(path=str(SHOTS / 'touched-dial-plain.png'))
                page.mouse.move(near['x'], near['y'])
                page.wait_for_timeout(300)
                self.assertEqual(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), 'pointer')
                page.screenshot(path=str(SHOTS / 'touched-dial-hovered.png'))
                page.evaluate('() => window.__viewer.setRoot(null)')
                page.wait_for_timeout(600)

                by_name, _ = self.controls(page)
                point = by_name['units dial']['point']

                # Hover: a pointer cursor and the display names of every
                # control naming this part.
                page.mouse.move(point['x'], point['y'])
                page.wait_for_timeout(300)
                self.assertEqual(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), 'pointer')
                self.assertEqual(
                    page.evaluate(f"() => document.querySelector("
                                  f"'{CANVAS}').getAttribute('title')"),
                    'turn units · units dial')
                page.screenshot(path=str(SHOTS / 'touched-hover.png'))

                button = (f'{TOUCHED_PANEL} .run-instruction'
                          '[data-instruction="Add one"]')
                page.mouse.down()
                page.screenshot(path=str(SHOTS / 'touched-press.png'))
                page.mouse.up()
                page.wait_for_selector(f'{button}:not([aria-busy])',
                                       timeout=60_000)
                page.wait_for_timeout(200)

                # Reported twice through one path: beside the pointer,
                # and on the panel's own button for that instruction.
                self.assertEqual(page.text_content(LABEL), 'completed')
                self.assertEqual(
                    page.text_content(
                        f'{TOUCHED_PANEL} .run-instruction-control'
                        '[data-instruction="Add one"] .run-outcome'),
                    'completed')
                self.assertEqual(
                    page.text_content(
                        f'{TOUCHED_PANEL} .run-input[data-input="units_entry"]'
                        ' .run-readout-value'), '1.0000')
                state = page.evaluate('() => window.__viewer.run().state()')
                self.assertEqual(state['units_entry'], 1)
                self.assertAlmostEqual(state['units.drum.turn'], 36, places=9)
                # Indistinguishable from the panel's own button.
                self.assertEqual(page.evaluate('() => window.__out'),
                                 [['completed', 1]])
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def test_a_drag_against_the_ratchet_reports_blocked_and_leaves_no_backlog(
            self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page)
                by_name, _ = self.controls(page)
                point = by_name['turn units']['point']

                self.drag(page, point, BLOCKED_DRAG)
                page.screenshot(path=str(SHOTS / 'touched-blocked.png'))
                reported = page.evaluate('() => window.__out')
                state = page.evaluate('() => window.__viewer.run().state()')
                self.assertEqual(reported, [['blocked', 0]])
                self.assertEqual(page.text_content(LABEL),
                                 'blocked after 0 digit')
                self.assertEqual(
                    page.text_content(
                        f'{TOUCHED_PANEL} .run-input[data-input="units_entry"]'
                        ' .run-outcome'), 'blocked after 0 digit')
                self.assertEqual(state['units_entry'], 0)
                self.assertEqual(state['units.drum.turn'], 0)

                # Held there, the gesture asks for nothing more: the run
                # goes on ticking and no second outcome arrives.
                tick = page.evaluate('() => window.__viewer.run().tick()')
                for step in range(8):
                    page.mouse.move(point['x'] + step,
                                    point['y'] + BLOCKED_DRAG[1] + step * 6)
                    page.wait_for_timeout(60)
                page.wait_for_timeout(600)
                self.assertGreater(
                    page.evaluate('() => window.__viewer.run().tick()'), tick,
                    'the run did not advance while the drag was held')
                self.assertEqual(page.evaluate('() => window.__out'),
                                 [['blocked', 0]])
                page.mouse.up()
                page.wait_for_timeout(300)
                self.assertEqual(
                    page.evaluate('() => window.__viewer.run()'
                                  '.state().units_entry'), 0)
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def test_a_drag_the_other_way_enters_one_digit(self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page)
                by_name, _ = self.controls(page)
                point = by_name['turn units']['point']

                self.drag(page, point, FORWARD_DRAG)
                page.mouse.up()
                page.wait_for_timeout(400)
                page.screenshot(
                    path=str(SHOTS / 'touched-after-forward-drag.png'))

                # One quantum of sweep, one request, one digit -- and the
                # sweep's sign went through the RATIO: -36 degrees on
                # `per_unit = -36` asks for +1 digit.
                self.assertEqual(page.evaluate('() => window.__out'),
                                 [['completed', 1]])
                state = page.evaluate('() => window.__viewer.run().state()')
                self.assertEqual(state['units_entry'], 1)
                self.assertAlmostEqual(state['units.input.turn'], -36,
                                       places=9)
                self.assertAlmostEqual(state['units.drum.turn'], 36, places=9)
                self.assertEqual(page.text_content(LABEL), 'completed')
                self.assertEqual(
                    page.text_content(
                        f'{TOUCHED_PANEL} .run-input[data-input="units_entry"]'
                        ' .run-readout-value'), '1.0000')
                # The camera never moved while the gesture was engaged.
                self.assertEqual(
                    page.evaluate("() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), '')
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def test_a_part_the_table_does_not_name_moves_the_camera(self):
        with sync_playwright() as playwright:
            browser = self.browser(playwright)
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                self.open(page)
                lid = self.find_lid(page)

                page.mouse.move(lid['x'], lid['y'])
                page.wait_for_timeout(300)
                # Nothing declares the lid, so it is not touchable.
                self.assertEqual(
                    page.evaluate("() => document.querySelector("
                                  f"'{CANVAS}').style.cursor"), '')
                self.assertIsNone(
                    page.evaluate("() => document.querySelector("
                                  f"'{CANVAS}').getAttribute('title')"))

                before = page.evaluate('() => window.__viewer.view()')
                state = page.evaluate('() => window.__viewer.run().state()')
                page.mouse.down()
                for step in range(1, 9):
                    page.mouse.move(lid['x'] - 12 * step, lid['y'] + 6 * step)
                    page.wait_for_timeout(30)
                page.mouse.up()
                page.wait_for_timeout(400)

                after = page.evaluate('() => window.__viewer.view()')
                self.assertNotEqual(
                    before['camera'], after['camera'],
                    'dragging an undeclared part must orbit the camera')
                self.assertEqual(page.evaluate('() => window.__out'), [],
                                 'no request may reach the run')
                self.assertEqual(
                    page.evaluate('() => window.__viewer.run().state()'),
                    state)
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

    def find_lid(self, page):
        """Where a column's lid is drawn, by hiding it and looking at
        which pixels changed. Every stand-in mesh is the same cube, so
        the picture alone cannot say which one is the lid, and no
        control names one.

        The panel and the transport are TRANSLUCENT, so canvas pixels
        change under them too -- and a press there lands on the panel,
        not on the model. Their rectangles are excluded, and the three
        columns are tried in turn until one lid is drawn somewhere a
        pointer actually reaches the canvas."""
        from PIL import Image, ImageChops
        import io
        chrome = page.evaluate("""() => [...document.querySelectorAll(
          '#host .run-controls, #host .run-transport, #host .part-outcome')]
          .map((element) => element.getBoundingClientRect())
          .map((r) => [r.left, r.top, r.right, r.bottom])""")

        def reachable(x, y):
            return not any(left <= x <= right and top <= y <= bottom
                           for left, top, right, bottom in chrome)

        for column in ('units', 'tens', 'hundreds'):
            before = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
            page.evaluate("(column) => window.__viewer.setVisible("
                          "[column, 'lid'], false)", column)
            page.wait_for_timeout(400)
            after = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
            page.evaluate("(column) => window.__viewer.setVisible("
                          "[column, 'lid'], true)", column)
            page.wait_for_timeout(400)
            diff = ImageChops.difference(before, after)
            width = diff.width
            changed = [(index % width, index // width)
                       for index, pixel in enumerate(diff.getdata())
                       if sum(pixel) > 24
                       and reachable(index % width, index // width)]
            if changed:
                middle = changed[len(changed) // 2]
                return {'x': middle[0] + 0.5, 'y': middle[1] + 0.5}
        self.fail('no lid is drawn where a pointer reaches the canvas')
