# solid-node-viewer - the browser viewer for solid-node models
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
from solid_node_viewer.bundle import bundle_path

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
        self.assertEqual((CALCULATOR / 'viewer.json').stat().st_size, 15159)
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
        # throwaway copy of solid-node at `2ab9505`: `'Stroke'` is the
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
    <script src="solid-widget.js"></script>
  </body>
</html>
"""

#: The Curta-shaped machine, cranked through the corpus's own script --
#: each request made through the same `machine()` handle a host uses,
#: and each answer read back off the bank.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await SolidNodeWidget.mount(host, 'viewer.json', {});
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
        shutil.copy2(bundle_path(), self.out_dir / 'solid-widget.js')
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
                    'typeof SolidNodeWidget !== "undefined"')
                result = page.evaluate(DRIVE)
                # Pixels are evidence: the machine after its strokes, and
                # the knob held by the freeze.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__shot = await SolidNodeWidget.mount(
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
        self.assertEqual(result['apiVersion'], 19)
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
  const viewer = await SolidNodeWidget.mount(host, 'viewer.json', {});
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
  const landedByGesture = {
    crank: field('crank'),
    busy: button().getAttribute('aria-busy'),
    bank: machine.state(),
  };

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
    twice, afterTwice, midDrawing, landedByGesture, landedByRestore,
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
        shutil.copy2(bundle_path(), self.out_dir / 'solid-widget.js')
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
                    'typeof SolidNodeWidget !== "undefined"')
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
                  window.__play = await SolidNodeWidget.mount(
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

        # 7. A GESTURE on a handle LANDS the drawing and then acts.
        self.assertLess(result['midDrawing'], 360)
        self.assertEqual(result['landedByGesture']['crank'], 360)
        self.assertIsNone(result['landedByGesture']['busy'])
        self.assertEqual(result['landedByGesture']['bank']['crank'], 360)

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
        self.assertEqual(result['apiVersion'], 19)

        self.assertTrue(
            (SHOTS / 'clocked-instruction-mid-stroke.png').is_file())
        self.assertTrue((SHOTS / 'clocked-instruction-landed.png').is_file())
