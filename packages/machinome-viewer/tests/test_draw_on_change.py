# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A continuous viewer draws a frame only when its picture has changed
(OpenSpec `draw-only-when-the-picture-changes`, design Decision 10).

In headless Chromium with SwiftShader, against the built bundle and the
committed fixtures:

- B1: a still page makes no WebGL draw call.
- B2: every kind of change reaches the canvas -- after each, the canvas
  as the page shows it equals the canvas after a forced redraw of the
  same state (`setTime(0)`: no fixture here reads `$t`, so it re-poses
  nothing and draws), and differs from the previous step's where the step
  changes what is seen; and ten frames after each step make no draw call.
- B3: a resize shows the picture in the frame in which the canvas is
  resized: a second resize observer, notified after the viewer's, reads
  the canvas and finds the picture, not the blank canvas of that size.
- B4: a drawn press makes draw calls on every frame until it lands, and
  none in the thirty frames after.

What these cannot see: what a real GPU does; a source not scripted; a
device pixel ratio change; a browser other than headless Chromium that
might not keep a canvas's last picture while nothing is drawn.
"""

import io
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    CALCULATOR, MARKED, REGULATOR, TOUCHED, needs_bundle, needs_pil,
    needs_playwright, serve_directory,
)
from machinome.viewer.web.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover - guarded by needs_pil
    Image = None


def pixels(png):
    """A screenshot's size and pixels, decoded: two encodings of the same
    pixels need not be the same bytes."""
    image = Image.open(io.BytesIO(png)).convert('RGBA')
    return image.size, image.tobytes()

HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>draw on change harness</title>
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

#: What every page script shares: frames, and a count of WebGL draw
#: calls -- the wrap `test_widget_e2e.py`'s
#: `test_reading_positions_draws_no_frame` uses.
PRELUDE = """
window.frames = (count) => new Promise((done) => {
  let left = count;
  const tick = () => { left -= 1; if (left <= 0) done(); else requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
});
window.wrapDraws = () => {
  const canvas = document.querySelector('#host canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  window.draws = 0;
  for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced',
                      'drawElementsInstanced', 'drawRangeElements']) {
    if (typeof gl[name] !== 'function') continue;
    const original = gl[name].bind(gl);
    gl[name] = (...args) => { window.draws += 1; return original(...args); };
  }
};
window.drawsOver = async (count) => {
  const before = window.draws;
  await window.frames(count);
  return window.draws - before;
};
"""

LAUNCH_ARGS = ['--no-sandbox', '--disable-gpu', '--use-angle=swiftshader']


@needs_bundle
@needs_playwright
@needs_pil
class DrawOnChangeInABrowserTest(TestCase):
    """B1 to B4, each in its own page."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        out = Path(self.tempdir.name) / 'site'
        out.mkdir()
        for name, source in (('touched', TOUCHED), ('regulator', REGULATOR),
                             ('marked', MARKED), ('calculator', CALCULATOR)):
            shutil.copytree(source, out / name)
        shutil.copy2(bundle_path(), out / 'machinome-viewer.js')
        (out / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(out)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def open(self, playwright, errors):
        browser = playwright.chromium.launch(args=LAUNCH_ARGS)
        page = browser.new_page(viewport={'width': 1000, 'height': 760})
        page.set_default_timeout(300_000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text)
                if message.type == 'error' else None)
        page.goto(self.harness_url)
        page.wait_for_function('typeof MachinomeViewer !== "undefined"')
        page.evaluate(f'() => {{ {PRELUDE} }}')
        return browser, page

    def mount(self, page, document, options='{}'):
        page.evaluate(f"""async () => {{
          const host = document.getElementById('host');
          window.viewer = await MachinomeViewer.mount(host, '{document}', {options});
          await window.frames(10);
          window.wrapDraws();
        }}""")

    # -- B1 ---------------------------------------------------------------

    def test_b1_a_still_page_makes_no_draw_call(self):
        errors = []
        counts = {}
        with sync_playwright() as playwright:
            for document in ('marked/manifest.json', 'regulator/viewer.json',
                             'touched/viewer.json'):
                browser, page = self.open(playwright, errors)
                try:
                    self.mount(page, document)
                    counts[document] = page.evaluate(
                        '() => window.drawsOver(30)')
                    paused = page.evaluate("""() => ({
                      clock: viewer.machine()?.clockPlaying() ?? false,
                      run: viewer.run()?.running() ?? false })""")
                    self.assertEqual(paused, {'clock': False, 'run': False})
                finally:
                    browser.close()
        print(f'\n  B1 draw calls over thirty still frames: {counts}')
        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        self.assertEqual(counts, {name: 0 for name in counts},
                         'a still page made draw calls')

    # -- B2 ---------------------------------------------------------------

    def run_steps(self, page, steps):
        """Each step, then three frames; the draw calls of ten more; the
        canvas as shown (A); a forced redraw of the same state; the canvas
        again (B)."""
        canvas = page.locator('#host canvas')
        previous = pixels(canvas.screenshot())
        report = []
        for name, act, changes in steps:
            skipped = act(page)
            if skipped:
                report.append({'step': name, 'skipped': skipped})
                continue
            page.evaluate('() => window.frames(3)')
            draws = page.evaluate('() => window.drawsOver(10)')
            shown = pixels(canvas.screenshot())
            page.evaluate('() => { window.viewer.setTime(0); }')
            redrawn = pixels(canvas.screenshot())
            report.append({
                'step': name, 'draws': draws,
                'current': shown == redrawn,
                'changed': shown != previous, 'changes': changes,
            })
            previous = redrawn
        return report

    def check(self, report, errors):
        for line in report:
            print(f'  B2 {line}')
        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        ran = [line for line in report if 'skipped' not in line]
        stale = [line['step'] for line in ran if not line['current']]
        self.assertEqual(stale, [], 'the canvas showed a picture that was not '
                                    'the current one after these steps')
        unseen = [line['step'] for line in ran
                  if line['changes'] and not line['changed']]
        self.assertEqual(unseen, [], 'these steps changed nothing on screen')
        drew = {line['step']: line['draws'] for line in ran if line['draws']}
        self.assertEqual(drew, {}, 'frames after these steps made draw calls')

    def test_b2_every_kind_of_change_reaches_the_canvas_on_touched(self):
        errors = []

        def js(source):
            return lambda page: page.evaluate(f'async () => {{ {source} }}')

        def clear_point(page):
            return page.evaluate("""() => {
              const canvas = document.querySelector('#host canvas');
              const box = canvas.getBoundingClientRect();
              const covered = (x, y) => viewer.controls().some((one) => one.rect
                && x >= one.rect.left - 20 && x <= one.rect.right + 20
                && y >= one.rect.top - 20 && y <= one.rect.bottom + 20);
              for (const [fx, fy] of [[0.9, 0.45], [0.9, 0.2], [0.75, 0.15],
                                      [0.6, 0.12], [0.9, 0.7]]) {
                const x = box.left + fx * box.width, y = box.top + fy * box.height;
                if (document.elementFromPoint(x, y) === canvas && !covered(x, y)) {
                  return { x, y };
                }
              }
              return null;
            }""")

        def drag(page):
            start = clear_point(page)
            if start is None:
                return 'no point of the canvas is clear of every control'
            page.mouse.move(start['x'], start['y'])
            page.mouse.down()
            page.mouse.move(start['x'] - 90, start['y'] + 40, steps=6)
            page.mouse.up()
            return None

        def wheel(page):
            page.mouse.move(500, 300)
            page.mouse.wheel(0, 240)
            return None

        def hover(page):
            point = page.evaluate("""() => viewer.controls()
              .find((one) => one.point !== null)?.point ?? null""")
            if point is None:
                return 'no control is reachable on screen'
            page.mouse.move(point['x'], point['y'])
            page.evaluate('() => window.frames(2)')
            cursor = page.evaluate(
                "() => document.querySelector('#host canvas').style.cursor")
            self.assertEqual(cursor, 'pointer', 'the hover did not reach the dial')
            return None

        def away(page):
            point = clear_point(page)
            if point is None:
                return 'no point of the canvas is clear of every control'
            page.mouse.move(point['x'], point['y'])
            page.evaluate('() => window.frames(2)')
            cursor = page.evaluate(
                "() => document.querySelector('#host canvas').style.cursor")
            self.assertEqual(cursor, '', 'the hover did not end')
            return None

        def full_screen(page):
            page.locator('.machinome-fullscreen').click()
            try:
                page.wait_for_function('document.fullscreenElement !== null',
                                       timeout=5_000)
            except Exception:  # noqa: BLE001 - recorded, not hidden
                return 'headless Chromium did not grant full screen'
            return None

        def leave_full_screen(page):
            if page.evaluate('() => document.fullscreenElement === null'):
                return 'not in full screen'
            page.evaluate('() => document.exitFullscreen()')
            page.wait_for_function('document.fullscreenElement === null',
                                   timeout=5_000)
            return None

        lose = js("""
          const canvas = document.querySelector('#host canvas');
          const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
          const extension = gl.getExtension('WEBGL_lose_context');
          const lost = new Promise((done) => canvas.addEventListener(
            'webglcontextlost', done, { once: true }));
          extension.loseContext();
          await lost;
          await window.frames(3);
          const restored = new Promise((done) => canvas.addEventListener(
            'webglcontextrestored', done, { once: true }));
          extension.restoreContext();
          await restored;
        """)
        steps = [
            ('a mouse drag turns the model', drag, True),
            ('a wheel step', wheel, True),
            ('setView', js("viewer.setView({ camera: [260, -180, 140], target: [0, 0, 0] });"), True),
            ('setRoot', js("viewer.setRoot(['units']);"), True),
            ('setRoot back', js('viewer.setRoot(null);'), True),
            ('setVisible off', js("viewer.setVisible(['tens'], false);"), True),
            ('setVisible on', js("viewer.setVisible(['tens'], true);"), True),
            ('highlight kept', js("window.back = viewer.highlight([['units']], { others: 'keep' });"), True),
            ('its put-back', js('window.back();'), True),
            ('highlight dimmed', js("window.back = viewer.highlight([['units']], { others: 'dim' });"), True),
            ('its put-back', js('window.back();'), True),
            ('highlight ghosted', js("window.back = viewer.highlight([['units']], { others: 'ghost' });"), True),
            ('its put-back', js('window.back();'), True),
            ('a hover on a dial', hover, True),
            ('the pointer moved away', away, True),
            ('the host narrowed', js("document.getElementById('host').style.width = '640px';"), True),
            ('the host restored', js("document.getElementById('host').style.width = '800px';"), True),
            ('reload()', js('await viewer.reload();'), False),
            ('the context lost and restored', lose, False),
            ('run().step(240) after a trigger', js("""
              const run = viewer.run();
              const triggered = run.trigger('Add one').catch(() => undefined);
              await run.step(240);
              await triggered;
            """), True),
            ('full screen', full_screen, True),
            ('full screen left', leave_full_screen, True),
        ]
        with sync_playwright() as playwright:
            browser, page = self.open(playwright, errors)
            try:
                # The panels drawn over the canvas are left out (the
                # handle keeps the whole run and machine API): a screenshot
                # of the canvas's box takes in whatever overlays it, and
                # the overlays are not the picture under test.
                self.mount(page, 'touched/viewer.json', "{ driverControls: 'none' }")
                self.assertFalse(page.evaluate('() => viewer.run().running()'))
                report = self.run_steps(page, steps)
            finally:
                browser.close()
        self.check(report, errors)

    def test_b2_every_kind_of_change_reaches_the_canvas_on_regulator(self):
        errors = []

        def js(source):
            return lambda page: page.evaluate(f'async () => {{ {source} }}')

        steps = [
            ('machine().move', js("window.rest = viewer.machine().snapshot(); "
                                  "viewer.machine().move('time', { to: 0.25 });"), True),
            ('machine().restore', js('viewer.machine().restore(window.rest);'), True),
            ('machine().move again', js("viewer.machine().move('time', { to: 0.75 });"), True),
            ('machine().reset', js('viewer.machine().reset();'), True),
            ('the clock played for half a second and paused', js("""
              viewer.machine().setClockPlaying(true);
              await new Promise((done) => setTimeout(done, 500));
              viewer.machine().setClockPlaying(false);
            """), True),
            ('a wheel step', lambda page: (page.mouse.move(500, 300),
                                           page.mouse.wheel(0, -240), None)[2], True),
        ]
        with sync_playwright() as playwright:
            browser, page = self.open(playwright, errors)
            try:
                self.mount(page, 'regulator/viewer.json', "{ driverControls: 'none' }")
                report = self.run_steps(page, steps)
            finally:
                browser.close()
        self.check(report, errors)

    # -- B3 ---------------------------------------------------------------

    def test_b3_a_resize_shows_the_picture_in_its_own_frame(self):
        errors = []
        with sync_playwright() as playwright:
            browser, page = self.open(playwright, errors)
            try:
                result = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  const reads = [];
                  const blank = (canvas) => {
                    const empty = document.createElement('canvas');
                    empty.width = canvas.width;
                    empty.height = canvas.height;
                    return empty.toDataURL();
                  };
                  window.viewer = await MachinomeViewer.mount(host, 'touched/viewer.json', {});
                  // Made after the mount, so notified after the viewer's
                  // own observer, in the same rendering update.
                  const observer = new ResizeObserver(() => {
                    const canvas = host.querySelector('canvas');
                    const read = canvas.toDataURL();
                    const empty = blank(canvas);
                    viewer.setTime(0);
                    reads.push({ width: canvas.width, blank: read === empty,
                                 current: read === canvas.toDataURL() });
                  });
                  observer.observe(host);
                  await window.frames(5);
                  host.style.width = '640px';
                  await window.frames(5);
                  observer.disconnect();
                  return reads;
                }""")
            finally:
                browser.close()
        print(f'\n  B3 reads inside the resize observer: {result}')
        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        self.assertEqual([read['width'] for read in result], [800, 640])
        self.assertEqual([read['blank'] for read in result], [False, False],
                         'the canvas was blank in the frame it was resized')
        self.assertEqual([read['current'] for read in result], [True, True])

    # -- B4 ---------------------------------------------------------------

    def test_b4_a_press_is_drawn_until_it_lands_and_not_after(self):
        errors = []
        with sync_playwright() as playwright:
            browser, page = self.open(playwright, errors)
            try:
                self.mount(page, 'calculator/viewer.json')
                result = page.evaluate("""async () => {
                  // The panel is rebuilt by the press, so the button is
                  // found again each time it is read.
                  const button = () => document.querySelector(
                    '.clocked-instruction[data-instruction="Stroke"]');
                  const perFrame = [];
                  let last = window.draws;
                  button().click();
                  const pressed = button().getAttribute('aria-busy') === 'true';
                  await new Promise((done) => {
                    const tick = () => {
                      perFrame.push(window.draws - last);
                      last = window.draws;
                      if (button().getAttribute('aria-busy') === 'true'
                          && perFrame.length < 2000) requestAnimationFrame(tick);
                      else done();
                    };
                    requestAnimationFrame(tick);
                  });
                  const after = await window.drawsOver(30);
                  return { pressed, perFrame, after,
                           crank: viewer.machine().state().crank };
                }""")
            finally:
                browser.close()
        frames = result['perFrame']
        print(f"\n  B4 frames from the click to the landing: {len(frames)}, "
              f"draw calls per frame {min(frames)} to {max(frames)}; "
              f"after the landing, thirty frames: {result['after']}")
        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        self.assertTrue(result['pressed'], 'the press started no drawing')
        self.assertEqual(result['crank'], 360)
        self.assertGreater(len(frames), 10)
        self.assertEqual([index for index, count in enumerate(frames) if count == 0],
                         [], 'frames of the drawing made no draw call')
        self.assertEqual(result['after'], 0,
                         'frames after the landing made draw calls')
