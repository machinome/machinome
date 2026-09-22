# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The acceptance: a CLOCKED machine cranked in a real browser.

`tests/fixtures/calculator/viewer.json` is the framework's own
`tests/clocked_project/calculator.py:Calculator`, exported verbatim -- a
**version 8** document carrying a compiled `clocked` machine with six
committing relations and THREE BOUNDS, which this viewer refused by name
until this cycle.

What this proves is the mechanism AND the interlocks. A stroke of the
crank adds the operand across four digits with the carry inside the law;
the ring clears them; the ratchet stops a backwards crank on the last
seated tooth; and the off-rest FREEZE holds the selector knob still while
the crank is off rest -- admitting ZERO travel and REPORTING its stop,
which is the difference between an operable machine and a broken control.
Every expectation below is the corpus's own recorded number.

Nothing here poses anything: every value comes from a request on the
document's own declared drivers, through the same `machine()` handle a
host would call.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    CALCULATOR, needs_bundle, needs_playwright, serve_directory,
)
from machinome_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'

#: The four register digits, in the order the stroke carries through
#: them.
DIGITS = ('w0.digit', 'w1.digit', 'w2.digit', 'w3.digit')

#: The document's own identity. NOT the corpus's: see the fixture's
#: README -- `Clocked.described` opens with the class's MODULE PATH, and
#: the two producers import the same class under two of them.
IDENTITY = '979b1a0ef4fe214106f329844ef1c5af789dd18608b5d883eaf22bfdc73ba684'


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


class CalculatorFixtureTest(TestCase):
    """(9.2) The committed `calculator` fixture is complete on disk.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas a browser test later.
    """

    def setUp(self):
        self.document = json.loads((CALCULATOR / 'viewer.json').read_text())

    def test_every_model_path_resolves_beside_the_document(self):
        paths = model_paths(self.document['root'])
        self.assertEqual(len(set(paths)), 2)
        missing = [path for path in sorted(set(paths))
                   if not (CALCULATOR / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')

    def test_the_document_is_the_framework_s_own_clocked_machine(self):
        self.assertEqual((CALCULATOR / 'viewer.json').stat().st_size, 15158)
        self.assertEqual(self.document['version'], 8)
        self.assertEqual(sorted(self.document['drivers']),
                         ['crank', 'feed', 'operand', 'ring', 'setting'])
        self.assertEqual(sorted(self.document['states']),
                         ['halved', *DIGITS])
        clocked = self.document['clocked']
        self.assertEqual(clocked['identity'], IDENTITY)
        self.assertIsNone(clocked['clock'])
        self.assertEqual(clocked['own'], '_own')
        self.assertEqual(len(clocked['commits']), 6)
        self.assertEqual(len(clocked['bounds']), 3)
        self.assertEqual(
            sorted((one['coordinate'], one['side'])
                   for one in clocked['bounds']),
            [('crank_dial.turn', 'low'), ('knob.travel', 'high'),
             ('knob.travel', 'low')])

    def test_it_declares_exactly_the_two_instructions_this_cycle_plays(self):
        # Re-exported for OpenSpec `play-the-instruction` from a
        # throwaway copy of machinome at `2ab9505`: `'Stroke'` is the
        # Curta's own `'Turn crank'` on a fixture that also carries three
        # bounds, and `'Set four'` is its absolute twin -- the `targets=`
        # form the corpus requires this runtime to reproduce.
        self.assertEqual(self.document['instructions'], {
            'Set four': {'targets': {'operand': 4}, 'duration': 0.5},
            'Stroke': {'by': {'crank': 360.0}, 'duration': 2.0},
        })

    def test_it_carries_no_program_and_no_controls(self):
        # A root publishes ONE machine or the other, and ADR-128 section
        # 14 keeps a `Control` refused under a clocked root, so there is
        # nothing for a part gesture to bind to.
        self.assertNotIn('program', self.document)
        self.assertNotIn('controls', self.document)
        # It DOES publish an ordinary animation cycle: `$t` sweeps while
        # the bank stands (ADR-128 section 10).
        self.assertIn('animation', self.document)
        self.assertEqual(sorted(self.document['animation']),
                         ['fps', 'frames'])


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>clocked calculator harness</title>
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

#: The Curta-shaped machine, cranked through the corpus's own script --
#: each request made through the same `machine()` handle a host uses,
#: and each answer read back off the bank.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const machine = viewer.machine();
  if (machine === null) {
    return { machine: null };
  }
  const shot = () => host.querySelector('canvas').toDataURL();
  const ask = (input, request) => {
    try {
      const answered = machine.move(input, request);
      return { admitted: answered.admitted,
               commits: answered.commits.length,
               stops: answered.stops.map((one) => ({ ...one })),
               bank: machine.state() };
    } catch (error) {
      return { refused: String(error.message), kind: error.kind,
               bank: machine.state() };
    }
  };
  const mounted = {
    identity: machine.identity(),
    clock: machine.clock(),
    order: machine.order(),
    bank: machine.state(),
    run: viewer.run(),
  };
  const restShot = shot();
  const operand = ask('operand', { to: 4 });
  const stroke = ask('crank', { by: 1100 });
  const strokedShot = shot();
  const frozen = ask('setting', { by: 1 });
  const frozenShot = shot();
  const ratchet = ask('crank', { by: -30 });
  const forward = ask('crank', { by: 10 });
  const cleared = ask('ring', { by: 500 });
  const undeclared = ask('handle', { by: 1 });
  const afterRefusal = machine.state();

  // WHAT A REQUEST COSTS, in the page (design section 14, task 10.2).
  // Same host, same document, three runs, numbers printed.
  const timed = {};
  const time = (name, input, request, restore) => {
    const runs = [];
    for (let at = 0; at < 3; at += 1) {
      machine.restore(restore);
      const started = performance.now();
      try { machine.move(input, request); } catch (error) { void error; }
      runs.push(performance.now() - started);
    }
    timed[name] = runs;
  };
  machine.reset();
  machine.move('operand', { to: 4 });
  const atRest = machine.snapshot();
  time('stroke', 'crank', { by: 360 }, atRest);
  machine.restore(atRest);
  machine.move('crank', { by: 1100 });
  const cranked = machine.snapshot();
  time('clip', 'setting', { by: 1 }, cranked);
  machine.restore(cranked);
  machine.move('ring', { by: 500 });
  machine.restore(cranked);
  time('sweep', 'ring', { by: 500 }, cranked);
  // The POSE alone, so a request and a render are never confused with
  // each other (design section 14): `restore` solves nothing and poses
  // everything, which is exactly the render half of a request.
  const posed = [];
  for (let at = 0; at < 3; at += 1) {
    machine.restore(atRest);
    const started = performance.now();
    machine.restore(cranked);
    posed.push(performance.now() - started);
  }
  timed.posed = posed;

  // THE PANEL a maker operates (design section 13). The chrome is pure
  // data and `viewer.ts` renders exactly what it returns, so what is
  // read here is the DOM it produced: a handle per driver, a follow-only
  // readout per state, and the outcome of the last gesture reported
  // where that gesture was made.
  machine.reset();
  machine.move('operand', { to: 4 });
  machine.move('crank', { by: 1100 });
  const panel = host.querySelector('.clocked-controls');
  const rows = (selector) => Array.from(
    panel.querySelectorAll(selector)).map((one) => one.dataset.input
      ?? one.dataset.readout);
  const chrome = {
    present: panel !== null,
    inputs: rows('.clocked-input'),
    readouts: rows('.clocked-readout'),
    sliders: rows('.clocked-slider'),
    // No transport: a clocked machine has no cadence to run or step,
    // and this one declares no CLOCK for one to advance either.
    transport: panel.querySelectorAll('.run-transport').length,
    clockTransport: panel.querySelectorAll('.clocked-transport').length,
    clockPlaying: machine.clockPlaying(),
  };
  // And the handle refuses to run a clock this machine has not got.
  let noClock = null;
  try {
    machine.setClockPlaying(true);
  } catch (error) {
    noClock = String(error.message);
  }
  // A GESTURE at the control, not through the handle: press `+` on the
  // selector while the crank is off rest, and read what the panel says.
  const plus = panel.querySelector('.clocked-plus[data-input="setting"]');
  plus.click();
  // The panel is rebuilt from the layer after every gesture -- it is
  // pure data rendered whole -- so the outcome is read off the CURRENT
  // panel rather than the one the press was made on.
  const held = host.querySelector(
    '.clocked-controls .clocked-outcome[data-input="setting"]').textContent;
  const settingAfter = machine.state().setting;

  return {
    mounted, operand, stroke, frozen, ratchet, forward, cleared,
    undeclared, afterRefusal, timed, chrome, held, settingAfter, noClock,
    apiVersion: viewer.apiVersion,
    // The dials TURNED: the strokes reached the geometry.
    strokesMoved: restShot !== strokedShot,
    // And the knob did NOT: the freeze held it, on screen.
    knobStill: strokedShot === frozenShot,
  };
}"""


@needs_bundle
@needs_playwright
class CalculatorInABrowserTest(TestCase):
    """(9.3) The Curta-shaped clocked machine, mounted, cranked, held by
    its own interlocks and photographed."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'calculator'
        shutil.copytree(CALCULATOR, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((CALCULATOR / 'viewer.json').read_text())

    def test_the_machine_cranks_carries_clears_and_is_held_by_its_stops(self):
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
                # Pixels are evidence: the machine after its strokes, and
                # the knob held by the freeze.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__shot = await MachinomeViewer.mount(
                    host, 'viewer.json', {});
                  const machine = window.__shot.machine();
                  machine.move('operand', { to: 4 });
                  machine.move('crank', { by: 1100 });
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'clocked-calculator-stroked.png'))
                page.evaluate("""async () => {
                  window.__shot.machine().move('setting', { by: 1 });
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'clocked-calculator-frozen.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # 1. It MOUNTED: the refusal this cycle removes is gone, and the
        # handle answers ONE question truthfully -- `machine()` for a
        # version 8 document and `run()` null.
        mounted = result['mounted']
        self.assertIsNotNone(mounted, 'the handle reported no machine')
        self.assertEqual(mounted['identity'],
                         self.document['clocked']['identity'])
        self.assertIsNone(mounted['clock'])
        self.assertIsNone(mounted['run'])
        self.assertEqual(result['apiVersion'], 24)
        # The bank's id order is DERIVED: drivers, then states.
        self.assertEqual(mounted['order'],
                         ['crank', 'feed', 'operand', 'ring', 'setting',
                          'halved', *DIGITS])
        # The page opens at the INITIAL BANK, every digit at zero.
        for digit in DIGITS:
            self.assertEqual(mounted['bank'][digit], 0)
        self.assertEqual(mounted['bank']['crank'], 0)
        self.assertEqual(mounted['bank']['operand'], 1)

        # 2. `operand` to 4 admits 3, on an INTEGER driver standing at 1.
        self.assertEqual(result['operand']['admitted'], 3)
        self.assertEqual(result['operand']['bank']['operand'], 4)

        # 3. A crank request of 1100 degrees fires THREE strokes, and the
        # dials read 2, 1, 0, 0 with the carry visible.
        stroke = result['stroke']
        self.assertEqual(stroke['admitted'], 1100)
        self.assertEqual(stroke['commits'], 3)
        self.assertEqual([stroke['bank'][digit] for digit in DIGITS],
                         [2, 1, 0, 0])
        self.assertTrue(result['strokesMoved'],
                        'the dials did not turn on screen')

        # 4. `setting` by 1, with the crank OFF REST, admits ZERO: the
        # knob does not move on screen and the control reports the
        # freeze's stop by coordinate and side.
        frozen = result['frozen']
        self.assertEqual(frozen['admitted'], 0)
        self.assertEqual(frozen['commits'], 0)
        self.assertEqual(len(frozen['stops']), 1)
        self.assertEqual(frozen['stops'][0]['coordinate'], 'knob.travel')
        self.assertEqual(frozen['stops'][0]['side'], 'high')
        self.assertEqual(frozen['stops'][0]['bound'], 0)
        self.assertEqual(frozen['bank']['setting'], 0)
        self.assertTrue(result['knobStill'],
                        'the knob moved while the freeze held it')

        # 5. A crank request of -30 degrees admits -2, stopped on the
        # last seated tooth of the ratchet.
        ratchet = result['ratchet']
        self.assertEqual(ratchet['admitted'], -2)
        self.assertEqual(len(ratchet['stops']), 1)
        self.assertEqual(ratchet['stops'][0]['coordinate'],
                         'crank_dial.turn')
        self.assertEqual(ratchet['stops'][0]['side'], 'low')
        self.assertEqual(ratchet['stops'][0]['bound'], 1098)
        self.assertEqual(ratchet['bank']['crank'], 1098)
        self.assertEqual(result['forward']['admitted'], 10)
        self.assertEqual(result['forward']['bank']['crank'], 1108)

        # 6. `ring` by 500 degrees clears the four dials back to zero.
        cleared = result['cleared']
        self.assertEqual(cleared['admitted'], 500)
        self.assertEqual([cleared['bank'][digit] for digit in DIGITS],
                         [0, 0, 0, 0])

        # 7. A refused request -- one naming an input this machine does
        # not declare -- leaves every dial where it was.
        self.assertIn('names no declared driver',
                      result['undeclared']['refused'])
        self.assertEqual(result['undeclared']['kind'], 'ValueError')
        self.assertEqual(result['afterRefusal'], cleared['bank'])

        # 8. WHAT A REQUEST COSTS, in the page. Printed, and asserted
        # against ONE FRAME BUDGET: the main-thread decision (design
        # section 3) is falsifiable only here -- a request costing more
        # than 16 ms would stutter a drag.
        timed = result['timed']
        # `stroke`, `clip` and `sweep` are one gesture each, SOLVE AND
        # POSE: the page's own numbers. `posed` is the pose alone.
        for name in ('stroke', 'clip', 'sweep', 'posed'):
            runs = timed[name]
            print(f'  Calculator {name} in the page: '
                  + ' / '.join(f'{one:.2f}' for one in runs) + ' ms')
            self.assertLess(min(runs), 16.0,
                            f'{name} costs more than one frame budget')

        # 9. A MAKER OPERATES IT ON SCREEN: a handle per driver, a
        # follow-only readout per state, no transport, and a gesture an
        # interlock holds REPORTED at the control that made it.
        chrome = result['chrome']
        self.assertTrue(chrome['present'], 'no clocked panel was rendered')
        self.assertEqual(chrome['inputs'],
                         ['crank', 'feed', 'operand', 'ring', 'setting'])
        self.assertEqual(chrome['readouts'], ['halved'])
        # Only `operand` declares a range, so only `operand` has a slider.
        self.assertEqual(chrome['sliders'], ['operand'])
        self.assertEqual(chrome['transport'], 0)
        # A machine that declares no CLOCK is offered no transport at
        # all, and `clockPlaying()` is false for it with no guard
        # (OpenSpec `run-the-clock`, design §7).
        self.assertEqual(chrome['clockTransport'], 0)
        self.assertFalse(chrome['clockPlaying'])
        self.assertIsNotNone(result['noClock'],
                             'a clockless machine accepted setClockPlaying')
        self.assertIn('does not', result['noClock'])
        self.assertIn('clock', result['noClock'])
        self.assertIn('held by knob.travel', result['held'])
        self.assertEqual(result['settingAfter'], 0)

        self.assertTrue((SHOTS / 'clocked-calculator-stroked.png').is_file())
        self.assertTrue((SHOTS / 'clocked-calculator-frozen.png').is_file())

    def test_the_inspector_keeps_clocked_controls_in_a_side_rail(self):
        """The inspector's navigator replaces duplicate chrome navigation."""
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(self.harness_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                result = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  host.style.height = '260px';
                  const mounted = await MachinomeViewer.mountInspector(
                    host, 'viewer.json', { sidebar: 'collapsed' });
                  const panel = host.querySelector('.clocked-controls');
                  const pane = host.querySelector('.machinome-inspector-viewer');
                  const style = getComputedStyle(panel);
                  const shown = (selector) => getComputedStyle(
                    panel.querySelector(selector)).display !== 'none';
                  const descenders = Array.from(
                    panel.querySelectorAll('.clocked-descend'));
                  const answer = {
                    panelWidth: panel.getBoundingClientRect().width,
                    paneWidth: pane.getBoundingClientRect().width,
                    panelHeight: panel.getBoundingClientRect().height,
                    paneHeight: pane.getBoundingClientRect().height,
                    overflow: style.overflow,
                    descenders: descenders.length,
                    visibleDescenders: descenders.filter(
                      (one) => getComputedStyle(one).display !== 'none').length,
                    visibleDescenderSeparators: Array.from(panel.querySelectorAll(
                      '.clocked-descend-separator')).filter(
                        (one) => getComputedStyle(one).display !== 'none').length,
                    resetVisible: shown('.clocked-reset'),
                    inputVisible: shown('.clocked-input'),
                    instructionVisible: shown('.clocked-instruction'),
                    canReset: typeof mounted.viewer.machine().reset === 'function',
                  };
                  panel.scrollTop = panel.scrollHeight - panel.clientHeight;
                  answer.scrollBeforeSlider = panel.scrollTop;
                  const slider = panel.querySelector(
                    '.clocked-slider[data-input="operand"]');
                  slider.value = '4';
                  slider.dispatchEvent(new Event('change', { bubbles: true }));
                  answer.scrollAfterSlider = host.querySelector(
                    '.clocked-controls').scrollTop;
                  mounted.dispose();
                  const plain = await MachinomeViewer.mount(
                    host, 'viewer.json', {});
                  const plainPanel = host.querySelector('.clocked-controls');
                  answer.plainDescenderVisible = getComputedStyle(
                    plainPanel.querySelector('.clocked-descend')).display !== 'none';
                  answer.plainResetVisible = getComputedStyle(
                    plainPanel.querySelector('.clocked-reset')).display !== 'none';
                  plain.dispose();
                  return answer;
                }""")
            finally:
                browser.close()

        self.assertEqual(errors, [])
        self.assertGreater(result['descenders'], 0)
        self.assertEqual(result['visibleDescenders'], 0)
        self.assertEqual(result['visibleDescenderSeparators'], 0)
        self.assertFalse(result['resetVisible'])
        self.assertTrue(result['inputVisible'])
        self.assertTrue(result['instructionVisible'])
        self.assertTrue(result['canReset'])
        self.assertTrue(result['plainDescenderVisible'])
        self.assertTrue(result['plainResetVisible'])
        self.assertGreater(result['scrollBeforeSlider'], 0)
        self.assertEqual(result['scrollAfterSlider'],
                         result['scrollBeforeSlider'])
        self.assertLessEqual(result['panelWidth'], 420)
        self.assertLess(result['panelWidth'], result['paneWidth'] * 0.5)
        self.assertLessEqual(result['panelHeight'], result['paneHeight'])
        self.assertEqual(result['overflow'], 'auto')


#: A DRAWING of the fixture's own `'Stroke'` -- one request, made at the
#: press, and its transition drawn over the declared two seconds
#: (OpenSpec `play-the-instruction`, design §20).
#:
#: Everything here is sampled PER ANIMATION FRAME, because what this
#: cycle claims is a property of frames: the crank's reading rises, the
#: model changes, and the machine's own bank is the SAME bank at every
#: one of them -- the proof that nothing was solved per frame.
PLAY = """async () => {
  const host = document.getElementById('host');
  // WHAT A FRAME COSTS: the viewer's own animation-loop callback, timed
  // from the outside by wrapping `requestAnimationFrame` before the
  // mount. A pose and a render are what a frame of a drawing IS, and
  // nothing else runs in that callback.
  const raw = window.requestAnimationFrame.bind(window);
  const frameCosts = [];
  let timing = false;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    const began = performance.now();
    callback(stamp);
    if (timing) frameCosts.push(performance.now() - began);
  });
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const machine = viewer.machine();
  const panel = () => host.querySelector('.clocked-controls');
  const field = (id) => Number(panel().querySelector(
    `.clocked-value[data-input="${id}"]`).value);
  const readout = (id) => panel().querySelector(
    `.clocked-readout-value[data-readout="${id}"]`).textContent;
  const button = () => panel().querySelector(
    '.clocked-instruction[data-instruction="Stroke"]');
  const outcome = () => panel().querySelector(
    '.clocked-outcome[data-instruction="Stroke"]').textContent;
  const shot = () => host.querySelector('canvas').toDataURL();
  // The test's own waits go through the RAW callback, so waiting for a
  // frame is never counted as the cost of one.
  const frame = () => new Promise((resolve) => raw(() => resolve()));

  // The BUTTON is pressable: no `disabled`, no `aria-disabled`.
  const before = {
    disabled: button().disabled,
    ariaDisabled: button().getAttribute('aria-disabled'),
    ariaBusy: button().getAttribute('aria-busy'),
    outcome: outcome(),
    bank: machine.state(),
  };

  // ---- 1. ONE PRESS, sampled every frame --------------------------
  const start = machine.state();
  timing = true;
  const startedAt = performance.now();
  button().click();
  const busyAtOnce = button().getAttribute('aria-busy');
  const crankAtOnce = field('crank');
  const samples = [];
  let midShot = null;
  for (let at = 0; at < 240; at += 1) {
    await frame();
    samples.push({
      crank: field('crank'),
      bank: machine.state(),
      busy: button().getAttribute('aria-busy'),
    });
    if (at === 30) midShot = shot();
    if (button().getAttribute('aria-busy') === null && at > 2) break;
  }
  const wall = (performance.now() - startedAt) / 1000;
  timing = false;
  const costs = frameCosts.slice();
  const landed = {
    crank: field('crank'),
    bank: machine.state(),
    outcome: outcome(),
    ariaBusy: button().getAttribute('aria-busy'),
  };
  const endShot = shot();

  // ---- 2. The landing IS one `move('crank', {by: 360})` ------------
  machine.reset();
  const byHand = machine.move('crank', { by: 360 });
  const handBank = machine.state();

  // ---- 3. TWO PRESSES in quick succession are TWO strokes ---------
  machine.reset();
  button().click();
  await frame();
  button().click();
  const twice = { crank: machine.state().crank, bank: machine.state() };
  // Let the second drawing finish so nothing is left running.
  for (let at = 0; at < 240; at += 1) {
    await frame();
    if (button().getAttribute('aria-busy') === null) break;
  }
  const afterTwice = { crank: field('crank'), bank: machine.state() };

  // ---- 4. A GESTURE lands a running drawing -----------------------
  machine.reset();
  button().click();
  await frame();
  const midDrawing = field('crank');
  panel().querySelector('.clocked-plus[data-input="feed"]').click();
  // The gesture LANDS the instruction's drawing -- the crank stands at
  // its end -- and STARTS ITS OWN: `feed` reads the transition's ORIGIN
  // although the machine already banks its end (OpenSpec
  // `draw-every-request`).
  const landedByGesture = {
    crank: field('crank'),
    feed: field('feed'),
    busy: button().getAttribute('aria-busy'),
    bank: machine.state(),
  };
  for (let at = 0; at < 60; at += 1) await frame();
  const feedLanded = { feed: field('feed'), bank: machine.state() };

  // ---- 5. A RESTORE during a drawing lands it too -----------------
  machine.reset();
  const rest = machine.snapshot();
  button().click();
  await frame();
  machine.restore(rest);
  const landedByRestore = {
    crank: field('crank'),
    busy: button().getAttribute('aria-busy'),
    bank: machine.state(),
  };

  // ---- 6. A COMMIT is drawn at the frame the fraction reaches it ---
  // `w0.digit` is a state of the `w0` layer, so the panel shows it when
  // that layer is focused; the instruction is played from the handle,
  // which is the same door the button uses.
  machine.reset();
  viewer.setRoot(['w0']);
  const digits = [];
  machine.trigger('Stroke');
  for (let at = 0; at < 240; at += 1) {
    // Sampled BEFORE the next frame, so the first entry is the pose the
    // press itself made and the last is the first frame that reached
    // the commit.
    digits.push(readout('w0.digit'));
    if (digits[digits.length - 1] !== '0') break;
    await frame();
  }
  viewer.setRoot(null);

  // ---- 7. The POSED trigger is refused under a clocked document ----
  let posedTrigger = null;
  try {
    viewer.trigger('Stroke');
  } catch (error) {
    posedTrigger = String(error.message);
  }

  // ---- 8. An unknown instruction is refused, listing the declared --
  machine.reset();
  let unknown = null;
  try {
    machine.trigger('Turn crank');
  } catch (error) {
    unknown = String(error.message);
  }

  return {
    before, busyAtOnce, crankAtOnce, samples, costs, wall, landed,
    byHand: { admitted: byHand.admitted, origin: byHand.origin,
              end: byHand.end, commits: byHand.commits.length,
              bank: handBank },
    twice, afterTwice, midDrawing, landedByGesture, feedLanded,
    landedByRestore,
    digits, posedTrigger, unknown,
    instructions: Object.keys(machine.instructions ? {} : {}),
    moved: midShot !== null && midShot !== endShot,
    apiVersion: viewer.apiVersion,
  };
}"""


@needs_bundle
@needs_playwright
class InstructionDrawnInABrowserTest(TestCase):
    """(7.2) The fixture's own `'Stroke'` PRESSED and WATCHED.

    One request, made once and before the first frame; the transition
    drawn over the declared two seconds; the machine's bank final from
    the press; and every other gesture landing the drawing first.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'calculator'
        shutil.copytree(CALCULATOR, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def test_a_pressed_instruction_is_one_request_drawn_over_its_duration(
            self):
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
                result = page.evaluate(PLAY)
                # PIXELS ARE EVIDENCE: one shot mid-stroke and one at the
                # end of it, of a fresh mount so the shot is of a drawing
                # rather than of whatever the drive left behind.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  // A CLEAN HOST for the shots: the drive above left its
                  // own canvas and panel here, and two panels stacked on
                  // one host make a photograph nobody can read.
                  host.replaceChildren();
                  window.__play = await MachinomeViewer.mount(
                    host, 'viewer.json', {});
                  window.__play.machine().move('operand', { to: 4 });
                  host.querySelector(
                    '.clocked-instruction[data-instruction="Stroke"]')
                    .click();
                }""")
                page.wait_for_timeout(900)
                page.screenshot(
                    path=str(SHOTS / 'clocked-instruction-mid-stroke.png'))
                page.wait_for_timeout(1600)
                page.screenshot(
                    path=str(SHOTS / 'clocked-instruction-landed.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # 1. The button is PRESSABLE, and indicates the moment it is
        # pressed.
        before = result['before']
        self.assertFalse(before['disabled'])
        self.assertIsNone(before['ariaDisabled'])
        self.assertIsNone(before['ariaBusy'])
        self.assertEqual(before['outcome'], '')
        self.assertEqual(result['busyAtOnce'], 'true')

        # 2. The FIRST frame is the transition's ORIGIN, posed in the
        # press's own task: the crank reads 0, not 360, although the
        # machine already stands at 360.
        self.assertEqual(result['crankAtOnce'], 0)

        samples = result['samples']
        self.assertGreater(len(samples), 10,
                           'the transition was not drawn over frames')

        # 3. The crank's reading RISES through the frames and ends at
        # 360.
        readings = [one['crank'] for one in samples]
        self.assertEqual(readings, sorted(readings),
                         'the drawn crank did not rise monotonically')
        self.assertGreater(len(set(readings)), 5,
                           'the drawing produced one pose, not many')
        self.assertEqual(readings[-1], 360)
        self.assertEqual(result['landed']['crank'], 360)
        self.assertIsNone(result['landed']['ariaBusy'])

        # 4. ONE SOLVE: the machine's bank is the SAME bank at every
        # frame of the drawing -- final from the press, and never
        # touched again.
        banks = [one['bank'] for one in samples]
        for bank in banks:
            self.assertEqual(bank, banks[0])
        self.assertEqual(banks[0]['crank'], 360)
        self.assertEqual(banks[0]['w0.digit'], 1)

        # 5. The landing IS one `move('crank', {by: 360})` from the same
        # start, value for value.
        by_hand = result['byHand']
        self.assertEqual(by_hand['admitted'], 360)
        self.assertEqual(by_hand['origin'], 0)
        self.assertEqual(by_hand['end'], 360)
        self.assertEqual(by_hand['commits'], 1)
        self.assertEqual(result['landed']['bank'], by_hand['bank'])
        # And the panel says what the bank says.
        self.assertEqual(result['landed']['crank'],
                         result['landed']['bank']['crank'])
        self.assertIn('moved 360', result['landed']['outcome'])

        # 6. TWO PRESSES are TWO STROKES: the first drawing lands, the
        # second is made from the bank it left, and the crank ends at
        # 720.
        self.assertEqual(result['twice']['crank'], 720)
        self.assertEqual(result['afterTwice']['crank'], 720)
        self.assertEqual(result['afterTwice']['bank']['crank'], 720)
        self.assertEqual(result['afterTwice']['bank']['w0.digit'], 2)

        # 7. A GESTURE on a handle LANDS the drawing and then acts --
        # and its own request is drawn in turn: `feed` reads the
        # transition's ORIGIN while the machine already banks its end,
        # and stands at that end a drawing later.
        self.assertLess(result['midDrawing'], 360)
        self.assertEqual(result['landedByGesture']['crank'], 360)
        self.assertIsNone(result['landedByGesture']['busy'])
        self.assertEqual(result['landedByGesture']['bank']['crank'], 360)
        self.assertEqual(result['landedByGesture']['feed'], 0)
        self.assertEqual(result['landedByGesture']['bank']['feed'], 1)
        self.assertEqual(result['feedLanded']['feed'], 1)
        self.assertEqual(result['feedLanded']['bank']['feed'], 1)

        # 8. And so does a RESTORE: the drawing lands, then the snapshot
        # takes the machine back to rest.
        self.assertEqual(result['landedByRestore']['crank'], 0)
        self.assertIsNone(result['landedByRestore']['busy'])
        self.assertEqual(result['landedByRestore']['bank']['crank'], 0)

        # 9. A COMMIT is drawn at the frame the transition reaches it,
        # and at its old value in every frame before: `'Stroke'` commits
        # at fraction 1.0 -- the corpus's own number -- so the digit
        # reads 0 for the whole stroke and 1 at the end.
        digits = result['digits']
        self.assertGreater(len(digits), 5)
        self.assertEqual(set(digits[:-1]), {'0'})
        self.assertEqual(digits[-1], '1')

        # 10. The POSED trigger is refused under a clocked document,
        # pointing at the machine's own.
        self.assertIsNotNone(result['posedTrigger'])
        self.assertIn("machine().trigger('Stroke')", result['posedTrigger'])
        self.assertIn('DRIVER TABLE', result['posedTrigger'])

        # 11. An unknown name is refused, listing the declared ones.
        self.assertIn('Turn crank', result['unknown'])
        self.assertIn('Set four', result['unknown'])
        self.assertIn('Stroke', result['unknown'])

        # 12. WHAT A FRAME COSTS, in the page. Printed rather than
        # asserted into a budget: a measurement is not a contract, and
        # the number belongs in `evidence.md` whatever it says.
        costs = sorted(result['costs'])
        median = costs[len(costs) // 2]
        fps = len(result['costs']) / result['wall']
        print(f'  calculator drawing: {len(result["costs"])} frames over '
              f'{result["wall"]:.2f} s ({fps:.1f} fps), per-frame pose '
              f'median {median:.2f} ms, worst {costs[-1]:.2f} ms')
        self.assertTrue(result['moved'], 'the model did not move on screen')
        self.assertEqual(result['apiVersion'], 24)

        self.assertTrue(
            (SHOTS / 'clocked-instruction-mid-stroke.png').is_file())
        self.assertTrue((SHOTS / 'clocked-instruction-landed.png').is_file())


#: A GESTURE on a HANDLE, drawn (OpenSpec `draw-every-request`). The
#: pilot's own gesture: the nudge amount set to a whole turn and the plus
#: button pressed, on a machine whose crank declares no range -- which is
#: the Curta's `crank_rotation` shape exactly.
#:
#: Everything is sampled PER ANIMATION FRAME, because the claim is a
#: property of frames: the panel's reading rises from the transition's
#: ORIGIN, the model changes, and the machine's own bank is the SAME bank
#: at every one of them.
GESTURE = """async () => {
  const host = document.getElementById('host');
  const raw = window.requestAnimationFrame.bind(window);
  const frameCosts = [];
  let timing = false;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    const began = performance.now();
    callback(stamp);
    if (timing) frameCosts.push(performance.now() - began);
  });
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  // Kept for the REAL POINTER gesture the harness drives afterwards.
  window.__gesture = viewer;
  const machine = viewer.machine();
  const panel = () => host.querySelector('.clocked-controls');
  const at = (selector) => panel().querySelector(selector);
  const box = (id) => at(`.clocked-value[data-input="${id}"]`);
  const field = (id) => Number(box(id).value);
  const outcome = (id) => at(
    `.clocked-outcome[data-input="${id}"]`).textContent;
  const plus = (id) => at(`.clocked-plus[data-input="${id}"]`);
  const shot = () => host.querySelector('canvas').toDataURL();
  const frame = () => new Promise((resolve) => raw(() => resolve()));
  const setAmount = (id, amount) => {
    const amountBox = at(`.clocked-nudge[data-input="${id}"]`);
    amountBox.value = String(amount);
    amountBox.dispatchEvent(new Event('change'));
  };
  // Sampled BEFORE each frame, so the first entry is the pose the
  // gesture's own task made and the last is a landed one. It stops AT
  // THE LANDING -- the reading reaching the bank the request already
  // stands at -- rather than after a fixed count: a gesture drawn at
  // its input's declared TEMPO can take ten times as many frames as the
  // viewer's own fifth of a second did, so a fixed sample count no
  // longer stands for "landed" (OpenSpec `draw-at-the-declared-tempo`).
  const watch = async (id, frames) => {
    const samples = [];
    for (let n = 0; n < frames; n += 1) {
      samples.push({ value: field(id), bank: machine.state() });
      if (n > 0 && samples[samples.length - 1].value
          === machine.state()[id]) break;
      await frame();
    }
    return samples;
  };

  // ---- 0. The nudge AMOUNT reaches the button only at the next
  // rebuild (a FINDING, recorded rather than worked around silently):
  // the row's buttons carry the amount the panel was BUILT with.
  setAmount('crank', 360);
  plus('crank').click();
  const firstPress = { admitted: outcome('crank'),
                       crank: machine.state().crank };
  for (let n = 0; n < 40; n += 1) await frame();
  at('.clocked-reset').click();
  const rebuilt = { crank: machine.state().crank };

  // ---- 1. ONE NUDGE of a whole turn, sampled every frame ----------
  const start = machine.state();
  timing = true;
  const startedAt = performance.now();
  plus('crank').click();
  const crankAtOnce = field('crank');
  const bankAtOnce = machine.state();
  const nudged = [];
  let midShot = null;
  for (let n = 0; n < 900; n += 1) {
    nudged.push({ value: field('crank'), bank: machine.state() });
    if (n === 3) midShot = shot();
    if (n > 0 && nudged[nudged.length - 1].value === bankAtOnce.crank) break;
    await frame();
  }
  const wall = (performance.now() - startedAt) / 1000;
  timing = false;
  const costs = frameCosts.slice();
  const endShot = shot();
  const landedNudge = { crank: field('crank'), bank: machine.state(),
                        outcome: outcome('crank') };

  // ---- 2. A TYPED value is drawn too: the second stroke, to 720 ----
  box('crank').value = '720';
  box('crank').dispatchEvent(new Event('change'));
  const typedAtOnce = field('crank');
  const typed = await watch('crank', 900);
  const landedTyped = { crank: field('crank'), bank: machine.state() };

  // ---- 3. A field the maker is EDITING is not rewritten ------------
  // A gesture REBUILDS the panel, so a value committed with Enter loses
  // the element it was typed into; the reachable case is a maker whose
  // cursor is in the field WHILE a drawing runs, which is what the
  // guard is for. Both are recorded.
  machine.reset();
  box('crank').focus();
  box('crank').value = '360';
  box('crank').dispatchEvent(new Event('change'));
  const committedFocus = {
    active: document.activeElement === null
      ? null : document.activeElement.className,
    text: box('crank').value,
  };
  await frame();
  const followedAfterCommit = box('crank').value;
  // Long enough to outlast a drawing at the DECLARED tempo (two
  // seconds at sixty frames), where forty frames outlasted a fifth of
  // a second.
  for (let n = 0; n < 200; n += 1) await frame();

  machine.reset();
  plus('crank').click();
  box('crank').focus();
  box('crank').value = '42';
  const edited = [];
  for (let n = 0; n < 12; n += 1) {
    await frame();
    edited.push({ text: box('crank').value,
                  crank: machine.state().crank });
  }
  const editedStill = box('crank').value;
  for (let n = 0; n < 200; n += 1) await frame();

  // ---- 4. A RANGED, WHOLE-NUMBER input: the slider's commit --------
  machine.reset();
  const slider = at('.clocked-slider[data-input="operand"]');
  slider.value = '9';
  slider.dispatchEvent(new Event('change'));
  const operandAtOnce = field('operand');
  const operand = await watch('operand', 40);
  const landedOperand = { operand: field('operand'),
                          bank: machine.state(),
                          thumb: Number(at(
                            '.clocked-slider[data-input="operand"]').value) };

  // ---- 5. The landing IS one move('crank', {by: 360}) by hand ------
  machine.reset();
  const byHand = machine.move('crank', { by: 360 });
  const handBank = machine.state();

  // ---- 6. The HOST's own handle lands at once ----------------------
  machine.reset();
  machine.move('crank', { by: 360 });
  const hostAtOnce = { crank: field('crank'), bank: machine.state() };
  await frame();
  const hostNext = { crank: field('crank'), bank: machine.state() };

  // ---- 7. THE TEMPO the DOCUMENT declares -------------------------
  // (OpenSpec `draw-at-the-declared-tempo`.) Six gestures on ONE page
  // at ONE frame rate, so the numbers are comparable with each other
  // and no absolute this host cannot promise is asserted.
  //
  // This fixture declares `'Set four': targets operand 4 over 0.5 s`
  // and `'Stroke': by crank 360 over 2 s`, and names `feed`, `ring`
  // and `setting` in neither -- one bench carrying every case the rule
  // distinguishes.
  const tempo = {};
  const measure = async (name, id, arm, act) => {
    arm();
    // A reset LANDS anything still running, REBUILDS the panel -- which
    // is how a nudge amount reaches its button -- and puts the bank
    // back where it started.
    machine.reset();
    await frame();
    const from = field(id);
    const startedAt = performance.now();
    act();
    const end = machine.state()[id];
    const poses = new Set();
    let frames = 0;
    while (frames < 900) {
      await frame();
      frames += 1;
      poses.add(field(id));
      if (field(id) === end) break;
    }
    tempo[name] = { frames, wall: (performance.now() - startedAt) / 1000,
                    from, end, landed: field(id), poses: poses.size };
  };
  // The DECLARED travel: the instruction states 360 over two seconds,
  // and the gesture asks for exactly that.
  await measure('declared', 'crank', () => setAmount('crank', 360),
                () => plus('crank').click());
  // A TWELFTH of it, which the rate makes a twelfth of the time.
  await measure('twelfth', 'crank', () => setAmount('crank', 30),
                () => plus('crank').click());
  // TWICE it, typed: twice the stroke at the same rate, uncapped.
  await measure('twice', 'crank', () => {}, () => {
    box('crank').value = '720';
    box('crank').dispatchEvent(new Event('change'));
  });
  // An input named ONLY by a `targets` instruction: a landing states no
  // rate, so this keeps the viewer's own duration.
  await measure('targetsOnly', 'operand', () => setAmount('operand', 8),
                () => plus('operand').click());
  // And an input NO instruction names at all.
  await measure('unnamed', 'feed', () => setAmount('feed', 25),
                () => plus('feed').click());
  // The instruction's own PRESS, unchanged: its declared duration.
  await measure('press', 'crank', () => {},
                () => at('.clocked-instruction[data-instruction="Stroke"]')
                  .click());

  // ---- 8. A gesture an interlock CLIPS is drawn for the travel the
  // MACHINE admitted, at the declared rate -- not for the travel it
  // asked for. The ratchet holds a backwards crank on the last seated
  // tooth (a 6-degree pitch), so a backwards nudge of a WHOLE TURN is
  // admitted only as far as the few degrees left inside that tooth, and
  // the picture is short in exactly that proportion.
  machine.reset();
  setAmount('crank', -360);
  // The amount reaches the button at the next rebuild, and a move
  // through the host's handle rebuilds.
  machine.move('crank', { by: 1103 });
  const clipFrom = machine.state().crank;
  const clipStarted = performance.now();
  plus('crank').click();
  const clipEnd = machine.state().crank;
  let clipFrames = 0;
  while (clipFrames < 900) {
    await frame();
    clipFrames += 1;
    if (field('crank') === clipEnd) break;
  }
  const clipped = { from: clipFrom, end: clipEnd, frames: clipFrames,
                    wall: (performance.now() - clipStarted) / 1000,
                    landed: field('crank'), outcome: outcome('crank') };

  return {
    clipped,
    firstPress, rebuilt, start, crankAtOnce, bankAtOnce, nudged, wall,
    costs, landedNudge, typedAtOnce, typed, landedTyped,
    committedFocus, followedAfterCommit, edited, editedStill,
    operandAtOnce, operand, landedOperand,
    byHand: { admitted: byHand.admitted, origin: byHand.origin,
              end: byHand.end, commits: byHand.commits.length,
              bank: handBank },
    hostAtOnce, hostNext, tempo,
    moved: midShot !== null && midShot !== endShot,
    apiVersion: viewer.apiVersion,
  };
}"""

#: A recorder for the gesture a REAL POINTER makes: the panel's reading
#: of `operand`, once per animation frame, while the harness clicks the
#: slider's track with the browser's own mouse. The row is re-queried
#: every frame because a request rebuilds the panel.
WATCH_TRACK = """() => {
  window.__gesture.machine().reset();
  window.__watch = [];
  const raw = window.requestAnimationFrame.bind(window);
  const read = () => {
    const box = document.querySelector(
      '.clocked-value[data-input="operand"]');
    return box === null ? null : Number(box.value);
  };
  const tick = () => {
    window.__watch.push(read());
    if (window.__watch.length < 45) raw(tick);
  };
  raw(tick);
}"""

#: The PHOTOGRAPH: one nudge, FROZEN part-way. The page's animation loop
#: is given a budget of frames and stops scheduling when it runs out, so
#: the last painted frame stands still for the camera -- a drawing is
#: otherwise over before a screenshot is taken. The budget and the wait
#: are sized to the DECLARED tempo: this nudge of a whole turn is drawn
#: over the two seconds `'Stroke'` declares, roughly 120 frames, where
#: it took a fifth of a second before.
FREEZE = """async (frames) => {
  const host = document.getElementById('host');
  host.replaceChildren();
  // The wrapper is installed for THIS mount only and handed back at the
  // end: a frozen one left in place would stop the next page's loop
  // before it drew anything.
  const previous = window.requestAnimationFrame;
  const raw = previous.bind(window);
  let budget = Infinity;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    if (budget <= 0) return;
    budget -= 1;
    callback(stamp);
  });
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const panel = () => host.querySelector('.clocked-controls');
  const at = (selector) => panel().querySelector(selector);
  viewer.machine().move('operand', { to: 4 });
  const amount = at('.clocked-nudge[data-input="crank"]');
  amount.value = '360';
  amount.dispatchEvent(new Event('change'));
  // The amount reaches the button at the next rebuild, so the reset
  // that follows is what arms this nudge.
  at('.clocked-reset').click();
  viewer.machine().move('operand', { to: 4 });
  budget = frames;
  at('.clocked-plus[data-input="crank"]').click();
  await new Promise((resolve) => setTimeout(resolve, 3000));
  const read = { crank: Number(at('.clocked-value[data-input="crank"]').value),
                 bank: viewer.machine().state() };
  window.requestAnimationFrame = previous;
  return read;
}"""


@needs_bundle
@needs_playwright
class GestureDrawnInABrowserTest(TestCase):
    """(4) EVERY request the clocked panel makes is DRAWN, at the TEMPO
    the document declares for its input.

    The pilot's own gesture -- the nudge amount set to a whole turn and
    the plus button pressed -- a typed value, and a ranged input's
    slider commit, each ONE request made at the gesture and drawn.

    How long each is drawn for is read off the document: this fixture
    declares `'Stroke': by crank 360 over 2 s`, so a gesture of a whole
    turn on `crank` takes those two seconds and a gesture of a twelfth
    of it a twelfth of them, while `operand` (named only by a `targets`
    instruction) and `feed` (named by none) keep the viewer's own fifth
    of a second (OpenSpec `draw-at-the-declared-tempo`).
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'calculator'
        shutil.copytree(CALCULATOR, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def test_a_gesture_on_a_handle_is_one_request_drawn_at_its_tempo(self):
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
                result = page.evaluate(GESTURE)
                # A REAL POINTER on the slider's TRACK, driven by the
                # browser itself rather than by a dispatched event: one
                # request, and drawn like every other.
                page.evaluate(WATCH_TRACK)
                track_box = page.locator(
                    '.clocked-slider[data-input="operand"]').bounding_box()
                page.mouse.click(
                    track_box['x'] + track_box['width'] * 0.95,
                    track_box['y'] + track_box['height'] / 2)
                page.wait_for_timeout(900)
                track = page.evaluate(
                    '() => ({ watch: window.__watch,'
                    ' bank: window.__gesture.machine().state() })')
                # PIXELS ARE EVIDENCE: the nudge FROZEN four frames in,
                # and the same nudge landed.
                frozen = page.evaluate(FREEZE, 30)
                page.screenshot(
                    path=str(SHOTS / 'clocked-gesture-mid-nudge.png'))
                # THREE QUARTERS through the SAME two-second stroke:
                # a second point of one tempo-drawn gesture, which a
                # fifth of a second had no room to hold (task 4.6).
                late = page.evaluate(FREEZE, 90)
                page.screenshot(
                    path=str(SHOTS / 'clocked-gesture-at-tempo.png'))
                landed = page.evaluate(FREEZE, 10_000)
                page.screenshot(
                    path=str(SHOTS / 'clocked-gesture-landed.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # 1. ONE NUDGE of a whole turn is DRAWN: the first frame stands
        # at the transition's ORIGIN although the machine already stands
        # at its end, the reading rises through the frames, and it lands
        # on 360.
        self.assertEqual(result['start']['crank'], 0)
        self.assertEqual(result['crankAtOnce'], 0)
        self.assertEqual(result['bankAtOnce']['crank'], 360)
        readings = [one['value'] for one in result['nudged']]
        self.assertEqual(readings, sorted(readings),
                         'the drawn crank did not rise monotonically')
        self.assertGreater(len(set(readings)), 5,
                           'the gesture drew one pose, not many')
        self.assertEqual(readings[0], 0)
        self.assertEqual(readings[-1], 360)
        self.assertEqual(result['landedNudge']['crank'], 360)
        self.assertIn('moved 360', result['landedNudge']['outcome'])
        self.assertTrue(result['moved'],
                        'the model did not move on screen during the nudge')

        # 2. ONE SOLVE: the bank is the same bank at every frame of the
        # drawing -- final from the gesture, never touched again.
        banks = [one['bank'] for one in result['nudged']]
        for bank in banks:
            self.assertEqual(bank, banks[0])
        self.assertEqual(banks[0]['crank'], 360)
        self.assertEqual(banks[0]['w0.digit'], 1)

        # 3. And the landing IS one `move('crank', {by: 360})` from the
        # same start, value for value.
        by_hand = result['byHand']
        self.assertEqual(by_hand['admitted'], 360)
        self.assertEqual(by_hand['origin'], 0)
        self.assertEqual(by_hand['end'], 360)
        self.assertEqual(result['landedNudge']['bank'], by_hand['bank'])

        # 4. A TYPED value is drawn as well: the second stroke, from 360
        # to 720, with the reading starting at where the input stood.
        self.assertEqual(result['typedAtOnce'], 360)
        typed = [one['value'] for one in result['typed']]
        self.assertEqual(typed, sorted(typed))
        self.assertGreater(len(set(typed)), 5,
                           'the typed value drew one pose, not many')
        self.assertEqual(typed[-1], 720)
        self.assertEqual(result['landedTyped']['bank']['crank'], 720)
        self.assertEqual(result['landedTyped']['bank']['w0.digit'], 2)

        # 5. A field the maker is EDITING is not rewritten by a drawing
        # that runs: the maker's `42` survives every frame while the
        # machine draws the whole turn behind it.
        edited = result['edited']
        self.assertGreater(len(edited), 5)
        self.assertEqual({one['text'] for one in edited}, {'42'})
        self.assertEqual(result['editedStill'], '42')
        self.assertEqual({one['crank'] for one in edited}, {360})

        # 6. A RANGED, whole-number input's slider commit is drawn, and
        # every drawn frame is a WHOLE number that never passes the end.
        self.assertEqual(result['operandAtOnce'], 1)
        operand = [one['value'] for one in result['operand']]
        self.assertEqual(operand, sorted(operand))
        self.assertGreater(len(set(operand)), 2,
                           'the slider commit drew one pose, not many')
        for value in operand:
            self.assertEqual(value, int(value),
                             'a whole-number input was drawn fractional')
            self.assertLessEqual(value, 9)
        self.assertEqual(operand[-1], 9)
        self.assertEqual(result['landedOperand']['bank']['operand'], 9)
        # The thumb follows the drawing too, and stands at the end.
        self.assertEqual(result['landedOperand']['thumb'], 9)

        # 6b. And a REAL POINTER on the track is the same one drawn
        # request: the reading starts where the input stood, rises
        # through whole numbers, and lands on the bank the click made.
        watched = [one for one in track['watch'] if one is not None]
        self.assertGreater(len(watched), 10)
        self.assertEqual(watched[0], 1)
        self.assertEqual(watched, sorted(watched))
        self.assertGreater(len(set(watched)), 2,
                           'the track click drew one pose, not many')
        for value in watched:
            self.assertEqual(value, int(value))
        self.assertGreater(track['bank']['operand'], 1)
        self.assertEqual(watched[-1], track['bank']['operand'])

        # 7. The HOST's own handle is NOT drawn and lands at once: the
        # panel reads the transition's end in the same task.
        self.assertEqual(result['hostAtOnce']['crank'], 360)
        self.assertEqual(result['hostAtOnce']['bank']['crank'], 360)
        self.assertEqual(result['hostNext']['crank'], 360)

        # 8. WHAT A FRAME COSTS, printed rather than asserted into a
        # budget: a measurement is not a contract.
        costs = sorted(result['costs'])
        median = costs[len(costs) // 2]
        fps = len(result['costs']) / result['wall']
        print(f'  calculator gesture: {len(result["costs"])} frames over '
              f'{result["wall"]:.2f} s ({fps:.1f} fps), per-frame pose '
              f'median {median:.2f} ms, worst {costs[-1]:.2f} ms')

        # 9. TWO FINDINGS, recorded rather than worked around. The nudge
        # AMOUNT reaches the button only at the next rebuild of the
        # panel, so the pilot's first press after typing 360 moves the
        # amount the row was built with; and a value committed with the
        # field still focused loses that element to the rebuild, so the
        # focus guard cannot protect it.
        print(f'  the first press after setting the amount moved to '
              f'{result["firstPress"]["crank"]} '
              f'({result["firstPress"]["admitted"]})')
        print('  the element focused when a value was committed became '
              f'{result["committedFocus"]["active"]!r}, the field then '
              f'reading {result["followedAfterCommit"]!r}')

        # 10. THE TEMPO (OpenSpec `draw-at-the-declared-tempo`). Six
        # gestures on one page at one frame rate. The absolutes belong
        # to this host and are PRINTED; what is asserted is the shape
        # the document declares -- a rate, and a fallback where it
        # declares none.
        tempo = result['tempo']
        for name, one in tempo.items():
            print(f'  tempo {name}: {one["frames"]} frames over '
                  f'{one["wall"]:.2f} s, {one["from"]} -> {one["end"]} '
                  f'({one["poses"]} distinct poses)')
        for name, one in tempo.items():
            self.assertEqual(one['landed'], one['end'],
                             f'the {name} gesture never landed')

        # 10a. The gesture asking for exactly the DECLARED travel takes
        # the DECLARED duration -- the two seconds `'Stroke'` states,
        # which is also what pressing `'Stroke'` itself takes. Asserted
        # as a window around the declared number, not as a frame count.
        self.assertEqual(tempo['declared']['end'], 360)
        self.assertGreater(tempo['declared']['wall'], 1.5)
        self.assertLess(tempo['declared']['wall'], 3.5)
        # An order above the fifth of a second a handle used to get, and
        # far more frames than that fifth could hold.
        self.assertGreater(tempo['declared']['frames'], 40)
        self.assertGreater(tempo['declared']['poses'], 40)

        # 10b. A TWELFTH of the declared travel takes a twelfth of the
        # time: a RATE, measured against 10a on the same page rather
        # than against an absolute.
        self.assertEqual(tempo['twelfth']['end'], 30)
        ratio = tempo['twelfth']['wall'] / tempo['declared']['wall']
        print(f'  a twelfth of the travel took {ratio:.3f} of the time')
        self.assertGreater(ratio, 1 / 24)
        self.assertLess(ratio, 1 / 6)

        # 10c. TWICE it takes twice, uncapped.
        self.assertEqual(tempo['twice']['end'], 720)
        twice = tempo['twice']['wall'] / tempo['declared']['wall']
        print(f'  twice the travel took {twice:.3f} of the time')
        self.assertGreater(twice, 1.5)
        self.assertLess(twice, 2.5)

        # 10d. An input named ONLY by a `targets` instruction, and an
        # input NO instruction names, both keep the viewer's own fifth
        # of a second -- measurably shorter than 10a on the same page.
        for name in ('targetsOnly', 'unnamed'):
            self.assertLess(tempo[name]['wall'],
                            tempo['declared']['wall'] / 4,
                            f'{name} was not drawn over the fallback')
            self.assertGreater(tempo[name]['wall'], 0.05)
            # Still DRAWN, not jumped.
            self.assertGreater(tempo[name]['poses'], 2)
        self.assertEqual(tempo['targetsOnly']['end'], 9)
        # And the whole-number rule still holds at every frame of the
        # `targets`-named input's own drawing.
        for value in operand:
            self.assertEqual(value, int(value))

        # 10e. A gesture an interlock CLIPS is drawn for the travel the
        # MACHINE ADMITTED, at the declared rate: the ratchet holds a
        # backwards whole turn on the last seated tooth, so the picture
        # is the few degrees it went and not the 360 it asked for.
        clipped = result['clipped']
        print(f'  clipped: {clipped["from"]} -> {clipped["end"]} in '
              f'{clipped["frames"]} frames over {clipped["wall"]:.3f} s, '
              f'reported {clipped["outcome"]!r}')
        self.assertLess(clipped['end'], clipped['from'])
        self.assertGreater(clipped['end'], clipped['from'] - 360,
                           'the ratchet did not clip the backwards turn')
        self.assertEqual(clipped['landed'], clipped['end'])
        self.assertIn('held by', clipped['outcome'])
        # The declared RATE on the ADMITTED travel: a whole turn takes
        # two seconds, so the handful of degrees the machine admitted
        # takes a hundredth of that -- and nothing like the two seconds
        # the travel ASKED FOR would have taken.
        expected = (tempo['declared']['wall']
                    * abs(clipped['end'] - clipped['from']) / 360)
        print(f'  the clipped gesture took {clipped["wall"]:.3f} s, the '
              f'declared rate on its admitted travel being '
              f'{expected:.3f} s')
        self.assertLess(clipped['wall'], tempo['declared']['wall'] / 10)
        # Within a couple of frames of the rate, the frame being the
        # quantum this harness can measure at all.
        self.assertLess(abs(clipped['wall'] - expected), 4 / 60)

        # 10f. The PRESSED instruction is unchanged: drawn over the
        # duration it DECLARES, the same two seconds.
        self.assertEqual(tempo['press']['end'], 360)
        press = tempo['press']['wall'] / tempo['declared']['wall']
        print(f'  the pressed instruction took {press:.3f} of the '
              f'gesture of the same travel')
        self.assertGreater(press, 0.7)
        self.assertLess(press, 1.4)

        print(f'  frozen mid-nudge at crank {frozen["crank"]}, '
              f'three quarters in at {late["crank"]}, '
              f'landed at {landed["crank"]}')
        self.assertGreater(frozen['crank'], 0)
        self.assertLess(frozen['crank'], 360)
        # TWO points of ONE two-second stroke, which the viewer's own
        # fifth of a second had no room to hold.
        self.assertGreater(late['crank'], frozen['crank'])
        self.assertLess(late['crank'], 360)
        self.assertEqual(landed['crank'], 360)
        self.assertTrue((SHOTS / 'clocked-gesture-mid-nudge.png').is_file())
        self.assertTrue((SHOTS / 'clocked-gesture-at-tempo.png').is_file())
        self.assertTrue((SHOTS / 'clocked-gesture-landed.png').is_file())
        self.assertEqual(result['apiVersion'], 24)
