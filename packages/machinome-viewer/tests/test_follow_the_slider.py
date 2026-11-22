# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A clocked slider dragged by the browser's own pointer is followed.

OpenSpec `follow-the-slider-as-it-is-dragged`, design Decision 11, B1 to
B5. The built bundle mounts two committed fixtures in headless Chromium
(SwiftShader): `pose-admission`, whose `press` is a float input on [0, 2]
with a `floor` commit writing `count`, and `calculator`, whose `operand` is
a whole-number input on [0, 9]. Playwright's mouse, and touch through the
DevTools protocol's `Input.dispatchTouchEvent`, press and drag the real
slider; a recorder chained on `requestAnimationFrame` reads the thumb, the
field, the machine's bank and the WebGL draw calls each frame. A thumb is
pressed at an end of its track (the input first moved there through the
handle), eight pixels in, where its place does not depend on the thumb's
painted width.

B4 pins the order of events the viewer's rule reads, on a plain range
input of the harness page and on the viewer's own slider: a press on the
track reports `input` before any `pointermove` of its pointer, a dragged
thumb reports a `pointermove` before its first `input`, and a release
reports `pointerup` before `change`. Its Firefox leg runs only where
Playwright's own Firefox is installed at the revision it expects.

What these cannot see: a GPU; a pointer's sub-pixel path; a host page that
styles the slider; what a frame costs.
"""

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase

from machinome.viewer.web.bundle import bundle_path
from tests.support import (
    CALCULATOR, FIXTURES, needs_bundle, needs_playwright, serve_directory,
)

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

POSE_ADMISSION = FIXTURES / 'pose-admission'

HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>follow the slider harness</title>
    <style>
      html, body { margin: 0; background: #101418; }
      #host { width: 800px; height: 600px; position: relative; }
      #plain { display: block; width: 400px; margin: 30px 20px; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <input id="plain" type="range" min="0" max="100" step="any" value="0">
    <script src="machinome-viewer.js"></script>
  </body>
</html>
"""

#: Mount a document, wrap the canvas's draw calls, and start a recorder
#: that reads the thumb, the field, the count readout and the bank after
#: the viewer's own work in every animation frame.
INSTALL = """async ([document_, input]) => {
  const host = document.getElementById('host');
  host.replaceChildren();
  const viewer = await MachinomeViewer.mount(host, document_, {});
  window.__viewer = viewer;
  window.__input = input;
  const canvas = host.querySelector('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  window.__draws = 0;
  for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced',
                      'drawElementsInstanced', 'drawRangeElements']) {
    if (typeof gl[name] !== 'function') continue;
    const original = gl[name].bind(gl);
    gl[name] = (...args) => { window.__draws += 1; return original(...args); };
  }
  const thumb = () => host.querySelector(`.clocked-slider[data-input="${input}"]`);
  const box = () => host.querySelector(`.clocked-value[data-input="${input}"]`);
  const count = () => host.querySelector('.clocked-readout-value[data-readout="count"]');
  window.__thumb = thumb;
  window.__read = () => ({
    thumb: thumb() === null ? null : Number(thumb().value),
    field: box() === null ? null : Number(box().value),
    count: count() === null ? null : Number(count().textContent),
    bank: viewer.machine().state(),
    draws: window.__draws,
    panel: host.querySelector('.clocked-controls') === window.__panel,
    same: thumb() === window.__pressed,
    focused: document.activeElement === window.__pressed && window.__pressed !== undefined,
  });
  window.__frames = [];
  // Where the recording stood when a pointer last went down: the frames
  // after it are the gesture's, whatever the round trip to the page cost.
  window.__downAt = 0;
  window.addEventListener('pointerdown', () => { window.__downAt = window.__frames.length; }, true);
  const raw = window.requestAnimationFrame.bind(window);
  window.__raw = raw;
  const tick = () => { window.__frames.push(window.__read()); raw(tick); };
  raw(tick);
  await new Promise((resolve) => raw(() => raw(resolve)));
}"""

#: Stand the input at `to` through the handle, then mark the slider and
#: the panel that a gesture will press.
STAND = """async (to) => {
  window.__viewer.machine().move(window.__input, { to });
  await new Promise((resolve) => window.__raw(() => window.__raw(resolve)));
  window.__pressed = window.__thumb();
  window.__panel = document.querySelector('.clocked-controls');
}"""

FRAMES = """(count) => new Promise((resolve) => {
  let seen = 0;
  const step = () => { seen += 1; if (seen >= count) resolve(); else window.__raw(step); };
  window.__raw(step);
})"""

#: Record every event the rule reads, on one element, in order.
LISTEN = """(selector) => {
  const element = document.querySelector(selector);
  const seen = [];
  for (const type of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel',
                      'gotpointercapture', 'lostpointercapture', 'input', 'change']) {
    element.addEventListener(type, (event) => {
      seen.push(event.pointerId === undefined ? type : `${type}#${event.pointerId}`);
    });
  }
  window.__seen = seen;
}"""


def first(events, name, after=0):
    """The index of the first event whose type is `name`, at or after
    `after`, or None."""
    for index in range(after, len(events)):
        if events[index].split('#')[0] == name:
            return index
    return None


@needs_bundle
@needs_playwright
class FollowTheSliderInABrowserTest(TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        root = Path(self.tempdir.name)
        shutil.copytree(POSE_ADMISSION, root / 'pose-admission',
                        ignore=shutil.ignore_patterns('_build', '__pycache__'))
        shutil.copytree(CALCULATOR, root / 'calculator')
        shutil.copy2(bundle_path(), root / 'machinome-viewer.js')
        (root / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(root)
        self.base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)

    @contextmanager
    def page(self, browser_type=None, touch=False):
        """The harness page in a fresh browser, closed on the way out."""
        with sync_playwright() as playwright:
            launcher = getattr(playwright, browser_type or 'chromium')
            args = (['--no-sandbox', '--disable-gpu', '--use-angle=swiftshader']
                    if browser_type is None else [])
            if browser_type is not None and not Path(launcher.executable_path).exists():
                self.skipTest(f"Playwright's {browser_type} is not installed at the revision "
                              f'it expects ({launcher.executable_path} is absent)')
            browser = launcher.launch(args=args)
            try:
                context = browser.new_context(viewport={'width': 800, 'height': 700},
                                              has_touch=touch)
                page = context.new_page()
                page.set_default_timeout(120_000)
                self.errors = []
                page.on('pageerror', lambda error: self.errors.append(str(error)))
                page.on('console', lambda message: self.errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(f'{self.base}/harness.html')
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                yield page
            finally:
                browser.close()

    def mount(self, page, document, input_id):
        page.evaluate(INSTALL, [document, input_id])

    def frames(self, page, count):
        page.evaluate(FRAMES, count)

    def read(self, page):
        return page.evaluate('() => window.__read()')

    def recorded(self, page, since):
        return page.evaluate('(since) => window.__frames.slice(since)', since)

    def mark(self, page):
        return page.evaluate('() => window.__frames.length')

    def track(self, page, input_id):
        box = page.locator(f'.clocked-slider[data-input="{input_id}"]').bounding_box()
        return box['x'] + 8, box['x'] + box['width'] - 8, box['y'] + box['height'] / 2

    def still(self, page, count):
        """What `count` frames changed: (before, after)."""
        before = self.read(page)
        self.frames(page, count)
        return before, self.read(page)

    def assert_still(self, measured, what):
        before, after = measured
        self.assertEqual(after['draws'] - before['draws'], 0, f'{what}: drew')
        for key in ('thumb', 'field', 'count', 'bank'):
            self.assertEqual(after[key], before[key], f'{what}: the {key} moved')

    def test_b1_a_real_pointer_drags_a_float_input_with_a_commit(self):
        with self.page() as page:
            self.mount(page, 'pose-admission/manifest.json', 'press')
            page.evaluate(STAND, 0)
            left, right, y = self.track(page, 'press')
            page.mouse.move(left, y)
            page.mouse.down()
            steps = []
            for step in range(1, 17):
                page.mouse.move(left + (right - left) * step / 16, y)
                self.frames(page, 2)
                steps.append(self.read(page))
            held = self.still(page, 20)
            page.mouse.up()
            released = self.still(page, 30)
            after = self.read(page)
        self.assertEqual(self.errors, [])
        print('\nB1 steps (thumb, bank, count):',
              [(one['thumb'], one['bank']['press'], one['bank']['count']) for one in steps])
        for index, one in enumerate(steps):
            where = f'step {index + 1}'
            self.assertEqual(one['bank']['press'], one['thumb'], f'{where}: the bank is not the thumb')
            self.assertAlmostEqual(one['field'], one['thumb'], places=5, msg=f'{where}: the field')
            self.assertEqual(one['bank']['count'], int(one['thumb']), f'{where}: the commits crossed')
            self.assertEqual(one['count'], one['bank']['count'], f'{where}: the readout')
            self.assertTrue(one['same'], f'{where}: the slider was replaced')
        self.assertGreater(steps[-1]['thumb'], 1.9)
        self.assert_still(held, 'a thumb held still')
        self.assert_still(released, 'after the release')
        self.assertTrue(after['same'], 'the slider pressed was replaced by the release')
        self.assertTrue(after['focused'], 'the slider pressed lost the focus')
        self.assertTrue(after['panel'], 'the panel was replaced')

    def test_b2_a_real_pointer_drags_a_whole_number_input(self):
        with self.page() as page:
            self.mount(page, 'calculator/viewer.json', 'operand')
            page.evaluate(STAND, 0)
            left, right, y = self.track(page, 'operand')
            page.mouse.move(left, y)
            page.mouse.down()
            since = page.evaluate('() => window.__downAt')
            steps = []
            for step in range(1, 17):
                page.mouse.move(left + (right - left) * step / 16, y)
                self.frames(page, 2)
                steps.append(self.read(page))
            page.mouse.up()
            self.frames(page, 5)
            during = self.recorded(page, since)
        self.assertEqual(self.errors, [])
        print('\nB2 steps (thumb, bank):',
              [(one['thumb'], one['bank']['operand']) for one in steps])
        for index, one in enumerate(steps):
            self.assertEqual(one['bank']['operand'], one['thumb'],
                             f'step {index + 1}: the bank is not the thumb')
        self.assertEqual(steps[-1]['thumb'], 9)
        for one in during:
            self.assertEqual(one['bank']['operand'], int(one['bank']['operand']))
            self.assertEqual(one['field'], int(one['field']), 'a fractional reading')
            self.assertEqual(one['thumb'], int(one['thumb']))

    def test_b3_a_track_press_held_is_drawn_from_the_press(self):
        with self.page() as page:
            self.mount(page, 'calculator/viewer.json', 'operand')
            page.evaluate(STAND, 0)
            left, right, y = self.track(page, 'operand')
            page.mouse.move(left + (right - left) * 0.9, y)
            page.mouse.down()
            self.frames(page, 40)
            held = self.recorded(page, page.evaluate('() => window.__downAt'))
            page.mouse.up()
            released = self.still(page, 30)
            after = self.read(page)
        self.assertEqual(self.errors, [])
        pressed = held[-1]['thumb']
        print('\nB3 pressed', pressed, 'field per frame:', [one['field'] for one in held])
        self.assertGreater(pressed, 5)
        self.assertEqual(held[0]['bank']['operand'], pressed,
                         'the bank does not hold the pressed value from the first frame')
        for one in held:
            self.assertEqual(one['bank']['operand'], pressed)
            self.assertEqual(one['thumb'], pressed, 'the thumb left the press point')
        fields = [one['field'] for one in held]
        self.assertEqual(fields[0], 0, 'the reading did not start where the input stood')
        self.assertEqual(fields, sorted(fields))
        self.assertGreater(len(set(fields)), 2, 'the press drew one pose, not many')
        for value in fields:
            self.assertEqual(value, int(value))
        self.assertEqual(fields[-1], pressed)
        self.assert_still(released, 'after the release')
        self.assertEqual(after['bank']['operand'], pressed)
        self.assertEqual(after['thumb'], pressed)
        self.assertTrue(after['same'])

    def b4_orders(self, page):
        """Three gestures on the plain slider and on the viewer's: a
        click on the track, a thumb dragged, and their releases."""
        orders = {}
        for name, selector in (('plain', '#plain'),
                               ('viewer', '.clocked-slider[data-input="press"]')):
            for gesture in ('track', 'thumb'):
                if name == 'plain':
                    page.evaluate("() => { document.querySelector('#plain').value = '0'; }")
                else:
                    page.evaluate(STAND, 0)
                box = page.locator(selector).bounding_box()
                left = box['x'] + 8
                right = box['x'] + box['width'] - 8
                y = box['y'] + box['height'] / 2
                page.evaluate(LISTEN, selector)
                if gesture == 'track':
                    page.mouse.move(left + (right - left) * 0.75, y)
                    page.mouse.down()
                    self.frames(page, 2)
                    page.mouse.move(left + (right - left) * 0.8, y)
                    self.frames(page, 2)
                else:
                    page.mouse.move(left, y)
                    page.mouse.down()
                    self.frames(page, 2)
                    for step in range(1, 5):
                        page.mouse.move(left + (right - left) * step / 8, y)
                        self.frames(page, 2)
                page.mouse.up()
                self.frames(page, 3)
                orders[f'{name} {gesture}'] = page.evaluate('() => window.__seen')
        return orders

    def assert_orders(self, orders):
        for name, events in orders.items():
            down = first(events, 'pointerdown')
            self.assertIsNotNone(down, f'{name}: no pointerdown in {events}')
            moved = first(events, 'pointermove', down)
            changed = first(events, 'input', down)
            self.assertIsNotNone(moved, f'{name}: {events}')
            self.assertIsNotNone(changed, f'{name}: {events}')
            if name.endswith('track'):
                self.assertLess(changed, moved,
                                f'{name}: a track press reported a pointermove before its input: {events}')
            else:
                self.assertLess(moved, changed,
                                f'{name}: a thumb drag reported an input before a pointermove: {events}')
            up = first(events, 'pointerup', down)
            commit = first(events, 'change', down)
            self.assertIsNotNone(up, f'{name}: {events}')
            self.assertIsNotNone(commit, f'{name}: {events}')
            self.assertLess(up, commit, f'{name}: change before pointerup: {events}')

    def test_b4_the_order_of_events_the_rule_reads(self):
        with self.page() as page:
            self.mount(page, 'pose-admission/manifest.json', 'press')
            orders = self.b4_orders(page)
        self.assertEqual(self.errors, [])
        for name, events in orders.items():
            print(f'\nB4 Chromium {name}: {" ".join(events)}')
        self.assert_orders(orders)

    def test_b4_the_order_of_events_in_firefox(self):
        with self.page('firefox') as page:
            self.mount(page, 'pose-admission/manifest.json', 'press')
            orders = self.b4_orders(page)
        self.assertEqual(self.errors, [])
        for name, events in orders.items():
            print(f'\nB4 Firefox {name}: {" ".join(events)}')
        self.assert_orders(orders)

    def test_b5_touch(self):
        with self.page(touch=True) as page:
            client = page.context.new_cdp_session(page)
            self.mount(page, 'pose-admission/manifest.json', 'press')
            page.evaluate(STAND, 0)
            left, right, y = self.track(page, 'press')

            def touch(kind, x=None):
                points = [] if x is None else [{'x': x, 'y': y}]
                client.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': points})

            touch('touchStart', left)
            self.frames(page, 2)
            steps = []
            for step in range(1, 9):
                touch('touchMove', left + (right - left) * step / 8)
                self.frames(page, 2)
                steps.append(self.read(page))
            touch('touchEnd')
            self.frames(page, 3)
            page.evaluate(STAND, 0)
            touch('touchStart', left + (right - left) * 0.75)
            touch('touchEnd')
            self.frames(page, 30)
            tapped = self.recorded(page, page.evaluate('() => window.__downAt'))
        self.assertEqual(self.errors, [])
        print('\nB5 drag (thumb, bank):', [(one['thumb'], one['bank']['press']) for one in steps])
        print('B5 tap field per frame:', [one['field'] for one in tapped])
        for index, one in enumerate(steps):
            self.assertEqual(one['bank']['press'], one['thumb'],
                             f'touch step {index + 1}: the bank is not the thumb')
        self.assertGreater(steps[-1]['thumb'], 1.5)
        fields = [one['field'] for one in tapped]
        end = tapped[-1]['bank']['press']
        self.assertGreater(end, 1)
        self.assertEqual(fields[0], 0, 'the tap was not drawn from where the input stood')
        self.assertEqual(fields, sorted(fields))
        self.assertGreater(len(set(fields)), 2, 'the tap drew one pose, not many')
        self.assertAlmostEqual(fields[-1], end, places=5)
