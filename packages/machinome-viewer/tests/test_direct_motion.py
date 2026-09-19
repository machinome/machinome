# SPDX-License-Identifier: AGPL-3.0-only
"""Real pointer input on the reviewed producer's verbatim documents."""
import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from machinome_viewer.bundle import bundle_path
from .support import FIXTURES, needs_bundle, needs_playwright, serve_directory
from .test_widget_e2e import HARNESS_PAGE

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@needs_bundle
@needs_playwright
class DirectMotionTest(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(FIXTURES / 'direct-motion', self.root / 'fixtures')
        shutil.copy2(bundle_path(), self.root / 'machinome-viewer.js')
        (self.root / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.root)
        self.url = server.__enter__() + '/harness.html'
        self.addCleanup(server.__exit__, None, None, None)
        self.playwright = sync_playwright().start()
        self.addCleanup(self.playwright.stop)
        self.browser = self.playwright.chromium.launch(args=[
            '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader'])
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page(viewport={'width': 800, 'height': 600})
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def open(self, fixture, camera, target=(0, 0, 0), up=(0, 0, 1)):
        self.page.goto(self.url)
        self.page.evaluate("""async ([fixture, camera, target, up]) => {
          window.machine = await MachinomeViewer.mount(document.querySelector('#host'),
            `fixtures/${fixture}/manifest.json`, {view: {camera, target}, up});
          window.outcomes = [];
          machine.run().onOutcome(outcome => outcomes.push(outcome));
        }""", [fixture, camera, target, up])
        self.page.wait_for_timeout(200)

    def control(self, name):
        return self.page.evaluate('(name) => machine.controls().find(c => c.name === name)', name)

    def state(self):
        return self.page.evaluate('() => machine.run().state()')

    def drag(self, point, dx, dy):
        self.assertIsNotNone(point)
        self.page.mouse.move(point['x'], point['y'])
        self.page.mouse.down()
        self.page.mouse.move(point['x'] + dx, point['y'] + dy, steps=15)
        self.page.wait_for_timeout(450)
        self.page.mouse.up()
        self.page.wait_for_timeout(250)

    def handles(self, name):
        point = self.control(name)['point']
        self.assertIsNotNone(point)
        self.page.mouse.move(point['x'], point['y'])
        self.page.wait_for_selector('.part-gesture-handle')

    def shot(self, name):
        path = Path(__file__).parent / '_shots'
        path.mkdir(exist_ok=True)
        self.page.screenshot(path=str(path / f'direct-{name}.png'))

    def test_the_selector_slides_on_its_own_rail(self):
        self.open('selector', [50, 0, 0])
        self.drag(self.control('slide selector')['gesturePoint'], 160, 0)
        state = self.state()
        self.assertGreater(state['setting'], 0)
        self.assertAlmostEqual(state['selector.travel'], 6 * state['setting'])
        self.shot('selector')
        self.assertEqual(self.errors, [])

    def test_lifting_does_not_turn_and_clicking_requests_one_revolution(self):
        self.open('crank', [0, -60, 45], [0, 0, 30])
        self.handles('lift crank')
        self.shot('crank-handles')
        self.drag(self.control('lift crank')['gesturePoint'], 0, -160)
        self.assertGreater(self.state()['elevation'], 0)
        self.assertEqual(self.state()['rotation'], 0)
        point = self.control('turn crank')['point']
        self.assertIsNotNone(point)
        self.page.mouse.click(point['x'], point['y'])
        self.page.wait_for_function('machine.run().state().rotation === 1')
        self.assertEqual(self.errors, [])

    def test_an_ambiguous_body_drag_does_not_move_either_freedom(self):
        self.open('crank', [0, -60, 45], [0, 0, 30])
        self.drag(self.control('turn crank')['point'], 120, 60)
        self.assertEqual(self.state()['rotation'], 0)
        self.assertEqual(self.state()['elevation'], 0)
        self.assertEqual(self.page.evaluate('() => outcomes'), [])

    def test_hidden_parts_have_no_reachable_handles(self):
        self.open('crank', [0, -60, 45], [0, 0, 30])
        self.handles('lift crank')
        self.page.evaluate('() => machine.setVisible(["crank"], false)')
        self.page.wait_for_timeout(100)
        self.assertIsNone(self.control('lift crank')['point'])
        self.assertIsNone(self.control('lift crank')['gesturePoint'])
        self.assertEqual(self.page.locator('.part-gesture-handle:visible').count(), 0)

    def test_an_inner_rotation_does_not_rotate_the_outer_sliding_axis(self):
        for angle in (0, 90):
            with self.subTest(angle=angle):
                self.open('tilted', [50, 0, 15], [0, 0, 15])
                if angle:
                    self.page.evaluate('async (angle) => { machine.run().move("angle", '
                                       '{by: angle, duration: 0.1}); machine.run().start(); }', angle)
                    self.page.wait_for_function('machine.run().state().angle === 90')
                self.handles('shift stack')
                self.drag(self.control('shift stack')['gesturePoint'], 100, 0)
                state = self.state()
                self.assertLess(state['reach'], 0)  # A negative published ratio.
                self.assertEqual(state['angle'], angle)
                self.assertAlmostEqual(state['stack.shift'], -2.5 * state['reach'])

    def test_an_ancestor_can_move_during_a_held_turn(self):
        self.open('register', [0, 40, 80], [0, 40, 0], up=[0, 1, 0])
        self.handles('turn marker')
        center = self.control('turn marker')['point']
        start = self.control('turn marker')['gesturePoint']
        self.page.mouse.move(start['x'], start['y'])
        self.page.mouse.down()
        # An independent hand moves the parent through the public run API.
        # The tested turning hand remains actual pointer input, never a bank write.
        self.page.evaluate('() => { machine.run().move("shift", '
                           '{by: 10, duration: 0.1}); machine.run().start(); }')
        self.page.wait_for_function('machine.run().state().shift === 10')
        self.page.mouse.move(start['x'], start['y'])
        self.assertEqual(self.state()['spin'], 0)
        # Radial about the OLD pivot (zero angle there), tangential about the
        # translated one. A frozen pointer-down frame would issue no turn.
        self.page.mouse.move(2 * start['x'] - center['x'],
                             2 * start['y'] - center['y'], steps=10)
        self.page.wait_for_timeout(450)
        self.page.mouse.up()
        self.page.wait_for_timeout(250)
        self.assertNotEqual(self.state()['spin'], 0)
        self.assertEqual(self.state()['shift'], 10)
