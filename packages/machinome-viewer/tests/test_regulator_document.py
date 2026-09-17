# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The acceptance: an ELAPSED clocked machine RUN in a real browser.

`tests/fixtures/regulator/viewer.json` is the framework's own
`tests/clocked_project/pendulum.py:Regulator`, exported verbatim -- a
**version 8** document whose machine declares a CLOCK. A bob swings by
`12 * sin(360 * time / 2)`, a formula of the BANK and not of `$t`, and a
count beside it is committed twice a period, at the swing's own extremes.

What this proves is the TRANSPORT: play advances the clock one request
per rendered frame, the model moves and the count climbs; pause holds the
bank; a step advances by exactly what it says; reset returns the whole
bank to its published defaults with the clock at zero and stops the
transport. Cycle 5 refused every one of those requests by name.

Nothing here poses anything: every value comes from a request on the
document's own clock, through the same `machine()` handle a host would
call and the same panel a maker would press.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    REGULATOR, needs_bundle, needs_playwright, serve_directory,
)
from solid_node_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

#: Where the two inspected screenshots are written, so the evidence is a
#: file on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'

#: The document's own identity. NOT the corpus's: see the fixture's
#: README -- `Clocked.described` opens with the class's MODULE PATH, and
#: the two producers import the same class under two of them (ADR-062's
#: finding F2).
IDENTITY = '281dfdc2e4e32c0c86f195c2896faed54c6ea534e9557027890f61f132505814'


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


class RegulatorFixtureTest(TestCase):
    """(6.2) The committed `regulator` fixture is complete on disk.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas a browser test later.
    """

    def setUp(self):
        self.document = json.loads((REGULATOR / 'viewer.json').read_text())

    def test_every_model_path_resolves_beside_the_document(self):
        paths = model_paths(self.document['root'])
        self.assertEqual(len(set(paths)), 1)
        missing = [path for path in sorted(set(paths))
                   if not (REGULATOR / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')

    def test_the_document_is_the_framework_s_own_elapsed_machine(self):
        self.assertEqual((REGULATOR / 'viewer.json').stat().st_size, 2116)
        self.assertEqual(self.document['version'], 8)
        self.assertEqual(sorted(self.document['drivers']), ['engaged'])
        self.assertEqual(sorted(self.document['states']), ['count'])
        clocked = self.document['clocked']
        self.assertEqual(clocked['identity'], IDENTITY)
        # THE FIELD THIS CYCLE EXISTS FOR.
        self.assertEqual(clocked['clock'], 'time')
        self.assertEqual(clocked['own'], '_own')
        self.assertEqual(len(clocked['commits']), 1)
        self.assertEqual(clocked['commits'][0]['at']['level'],
                         '((time + 0.5) / 1.0)')
        # Nothing stops a clock, and this machine declares no stop at all.
        self.assertEqual(clocked['bounds'], [])

    def test_it_carries_no_program_and_no_controls(self):
        self.assertNotIn('program', self.document)
        self.assertNotIn('controls', self.document)
        # It DOES publish an ordinary animation cycle...
        self.assertIn('animation', self.document)
        self.assertEqual(sorted(self.document['animation']),
                         ['fps', 'frames'])

    def test_its_pose_expressions_read_the_free_name_time(self):
        # The bob's placement is an expression over the BANK: `time` is a
        # bank id in seconds, and `$t` -- which nothing here reads -- is
        # the 0..1 animation variable and is never seconds (ADR-128 §10).
        bob = self.document['root']['children'][0]
        expressions = json.dumps(bob['operations'])
        self.assertIn('time', expressions)
        self.assertNotIn('$t', json.dumps(self.document['root']))


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>elapsed clocked regulator harness</title>
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

#: The pendulum, RUN: mounted, played for a wall second, paused, stepped,
#: reset -- every gesture through the panel a maker presses or the handle
#: a host holds, and every answer read back off the bank.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await SolidNodeWidget.mount(host, 'viewer.json', {});
  const machine = viewer.machine();
  if (machine === null) {
    return { machine: null };
  }
  const sleep = (ms) => new Promise((done) => { setTimeout(done, ms); });
  // The renderer keeps no drawing buffer between frames, so a canvas
  // read from a timer returns a CLEARED canvas and every picture would
  // match every other. A picture is taken inside a requestAnimationFrame
  // callback instead -- the widget's own animation loop registered
  // first, so it has already rendered this frame when this runs.
  const shot = () => new Promise((done) => {
    requestAnimationFrame(() => { done(
      host.querySelector('canvas').toDataURL()); });
  });
  const panel = () => host.querySelector('.clocked-controls');
  const at = (selector) => panel().querySelector(selector);
  const readout = () => at('.clocked-elapsed').textContent;

  const mounted = {
    identity: machine.identity(),
    clock: machine.clock(),
    order: machine.order(),
    bank: machine.state(),
    run: viewer.run(),
    playing: machine.clockPlaying(),
  };
  // 1. THE PAGE OPENS AT t = 0, with the transport present and stopped.
  const opened = {
    transport: panel().querySelectorAll('.clocked-transport').length,
    play: at('.clocked-play').textContent,
    step: panel().querySelectorAll('.clocked-step').length,
    speed: panel().querySelectorAll('.clocked-speed').length,
    // NO SCRUB and NO reverse: the clock is one-way by decision.
    scrub: panel().querySelectorAll('.clocked-slider[data-input="time"]')
      .length,
    // And no readout of the clock as a positional handle.
    inputs: Array.from(panel().querySelectorAll('.clocked-input'))
      .map((one) => one.dataset.input),
    readout: readout(),
    // ONE panel, not two: a clocked machine's inputs are moved by
    // REQUESTS, so the posed driver chrome -- which writes a driver
    // straight past the machine, and is anchored at the same corner --
    // must not be built beside the clocked one.
    posed: host.querySelectorAll('.driver-controls').length,
  };
  const restShot = await shot();

  // 2. PLAY for one wall second at x1, from the PANEL, sampling the
  // canvas on the way. The bob's angle is `12 * sin(180 * t)`, which
  // returns to ZERO at every whole second -- so a single picture taken
  // at the end could legitimately match the one at rest. Three samples
  // taken WHILE it swings is the honest evidence that it moved.
  at('.clocked-play').click();
  const startedPlaying = machine.clockPlaying();
  const swinging = [];
  for (let sample = 0; sample < 3; sample += 1) {
    await sleep(250);
    swinging.push(await shot());
  }
  await sleep(250);
  const played = { bank: machine.state(), readout: readout(),
                   label: at('.clocked-play').textContent };
  const playedShot = await shot();

  // 3. PAUSE holds the bank: nothing further is committed.
  at('.clocked-play').click();
  const pausedAt = machine.state();
  const pausedLabel = at('.clocked-play').textContent;
  await sleep(300);
  const heldAt = machine.state();

  // 4. A 2 SECOND STEP advances the clock by exactly two seconds.
  const amount = at('.clocked-step-amount');
  amount.value = '2';
  amount.dispatchEvent(new Event('change'));
  const beforeStep = machine.state();
  at('.clocked-step').click();
  const stepped = machine.state();
  // NO pixel claim is made for the step, and the reason is the
  // machine's: the bob's period is T = 2.0 s, so a step of exactly two
  // seconds returns it to the very angle it left. What the step moves is
  // the CLOCK and the COUNT, asserted off the bank below.
  const steppedShot = await shot();

  // 4b. THE CLOCK'S OWN REQUESTS ARE NEVER DRAWN (OpenSpec
  // `draw-every-request`, design D4). A gesture on a HANDLE is drawn
  // over the viewer's own fifth of a second; a step and a played frame
  // pass a ZERO duration through the same door, because a drawn step
  // would PAUSE the transport that asked for it -- a transport control
  // that stops the transport -- and a drawn played frame would fight
  // itself sixty times a second.
  const readoutBeforeStep = readout();
  at('.clocked-step').click();
  // The readout advances with the step, and the bank by the stated
  // seconds. (What DISCRIMINATES a drawn step is the transport below:
  // the panel is rebuilt before a drawing starts, so the elapsed
  // reading would stand at the end either way.)
  const steppedUndrawn = { readout: readout(), bank: machine.state() };
  at('.clocked-play').click();
  const playingBeforeStep = machine.clockPlaying();
  at('.clocked-step').click();
  const steppedWhilePlaying = { playing: machine.clockPlaying(),
                                bank: machine.state() };
  await sleep(200);
  const stillPlaying = { playing: machine.clockPlaying(),
                         bank: machine.state() };
  at('.clocked-play').click();

  // 5. RESET returns the whole bank to its published defaults, with the
  // clock at zero, and STOPS the transport.
  at('.clocked-play').click();
  const runningBeforeReset = machine.clockPlaying();
  host.querySelector('.clocked-reset').click();
  const afterReset = { bank: machine.state(),
                       playing: machine.clockPlaying(),
                       readout: readout() };
  const resetShot = await shot();

  // 6. THE POSE FOLLOWS THE BANK: two instants, two pictures. The
  // angles are hand-computed -- `12 * sin(180 * 0.25)` is 8.49 degrees
  // and `12 * sin(180 * 0.5)` is the swing's own extreme of 12 -- so
  // these two instants really do stand the bob somewhere else.
  machine.move('time', { to: 0.25 });
  const quarterShot = await shot();
  machine.move('time', { to: 0.5 });
  const halfShot = await shot();

  // 6b. THE READOUT FOLLOWS THE COMMITTED BANK whoever moved it: a
  // host driving the handle directly must not leave the panel showing
  // an instant the machine has left.
  machine.move('time', { to: 5.25 });
  const hostMoved = { bank: machine.state(), readout: readout(),
                      clock: at('.clocked-clock .clocked-readout-value')
                        ?.textContent };

  // 7. A REFUSAL is a refusal and not a stop: time never reverses.
  let backwards = null;
  try {
    machine.move('time', { by: -1 });
  } catch (error) {
    backwards = { message: String(error.message), kind: error.kind };
  }
  const afterRefusal = machine.state();

  // 7b. A REFUSED FRAME PAUSES THE TRANSPORT and reports, ONCE (design
  // §5, task 5.3), rather than repeating a refused request sixty times
  // a second. At a speed this high the per-frame cap is four frames'
  // worth of machine time -- thousands of seconds, thousands of
  // releases -- and the machine refuses a request crossing more
  // surfaces of one relation than its own published `max_crossings`
  // admits. The speed is set through the SAME `setSpeed` the ladder
  // uses, which already accepts a host-set multiplier the ladder lacks.
  machine.reset();
  viewer.setSpeed(100000);
  at('.clocked-play').click();
  const askedToRun = machine.clockPlaying();
  await sleep(400);
  const refused = {
    playing: machine.clockPlaying(),
    bank: machine.state(),
    message: at('.clocked-refusal').textContent,
    hidden: at('.clocked-refusal').hidden,
    label: at('.clocked-play').textContent,
  };
  await sleep(200);
  // Still paused, and the bank still stands: no second refused request.
  const stillRefused = { playing: machine.clockPlaying(),
                         bank: machine.state() };
  viewer.setSpeed(1);
  machine.reset();

  // 8. WHAT A PLAYED FRAME COSTS, in the page (design §9, task 7.2).
  // One frame-sized request at x1 and at x60, SOLVE AND POSE, three runs
  // each, numbers printed and asserted under ONE frame budget.
  machine.reset();
  const rest = machine.snapshot();
  const timed = {};
  const time = (name, by) => {
    const runs = [];
    for (let at = 0; at < 3; at += 1) {
      machine.restore(rest);
      const started = performance.now();
      machine.move('time', { by });
      runs.push(performance.now() - started);
    }
    timed[name] = runs;
  };
  time('frame x1', 1 / 60);
  time('frame x60', 60 / 60);
  time('frame x3600', 3600 / 60);
  // The POSE alone, so a request and a render are never confused:
  // `restore` solves nothing and poses everything.
  machine.move('time', { by: 10 });
  const later = machine.snapshot();
  const posed = [];
  for (let at = 0; at < 3; at += 1) {
    machine.restore(rest);
    const started = performance.now();
    machine.restore(later);
    posed.push(performance.now() - started);
  }
  timed.posed = posed;

  // 9. THE HOST'S OWN PANEL: the chrome suppressed, the whole machine
  // API kept -- the two new verbs included (task 5.5).
  const bare = document.createElement('div');
  bare.style.cssText = 'width:320px;height:240px;';
  document.body.append(bare);
  const headless = await SolidNodeWidget.mount(bare, 'viewer.json', {
    driverControls: 'none',
  });
  const quiet = headless.machine();
  quiet.setClockPlaying(true);
  await sleep(300);
  const hosted = {
    panels: bare.querySelectorAll('.clocked-controls').length,
    transports: bare.querySelectorAll('.clocked-transport').length,
    playing: quiet.clockPlaying(),
    bank: quiet.state(),
  };
  quiet.setClockPlaying(false);

  return {
    mounted, opened, startedPlaying, played, pausedAt, pausedLabel, heldAt,
    hostMoved, askedToRun, refused, stillRefused,
    readoutBeforeStep, steppedUndrawn, playingBeforeStep,
    steppedWhilePlaying, stillPlaying,
    beforeStep, stepped, runningBeforeReset, afterReset, backwards,
    afterRefusal, timed, hosted,
    apiVersion: viewer.apiVersion,
    // The bob SWUNG while the clock ran, and it stands somewhere else at
    // two different instants: the pose really follows the bank.
    played_moved: swinging.some((one) => one !== restShot),
    played_end_shot_differs: restShot !== playedShot,
    stepped_period: playedShot === steppedShot,
    reset_to_rest: resetShot === restShot,
    two_instants_differ: quarterShot !== halfShot,
  };
}"""


@needs_bundle
@needs_playwright
class RegulatorInABrowserTest(TestCase):
    """(6.3) The elapsed clocked machine, mounted, played, paused,
    stepped, reset and photographed."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'regulator'
        shutil.copytree(REGULATOR, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'solid-widget.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = json.loads((REGULATOR / 'viewer.json').read_text())

    def test_a_maker_plays_pauses_steps_and_resets_an_elapsed_machine(self):
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
                # Pixels are evidence: the pendulum at rest, and the
                # pendulum somewhere else with its count standing.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  host.replaceChildren();
                  window.__shot = await SolidNodeWidget.mount(
                    host, 'viewer.json', {});
                }""")
                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'clocked-regulator-rest.png'))
                page.evaluate("""async () => {
                  window.__shot.machine().move('time', { by: 5.25 });
                }""")
                page.wait_for_timeout(500)
                page.screenshot(
                    path=str(SHOTS / 'clocked-regulator-played.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # 1. It MOUNTED, and the handle answers ONE question truthfully.
        mounted = result['mounted']
        self.assertIsNotNone(mounted, 'the handle reported no machine')
        self.assertEqual(mounted['identity'],
                         self.document['clocked']['identity'])
        self.assertEqual(mounted['clock'], 'time')
        self.assertIsNone(mounted['run'])
        self.assertEqual(result['apiVersion'], 19)
        # The bank's id order is DERIVED: drivers, then states, then the
        # clock.
        self.assertEqual(mounted['order'], ['engaged', 'count', 'time'])
        self.assertEqual(mounted['bank'],
                         {'engaged': 1, 'count': 0, 'time': 0})
        self.assertFalse(mounted['playing'])

        # 2. THE TRANSPORT is on screen, stopped, with no scrub and no
        # positional handle for the clock.
        opened = result['opened']
        self.assertEqual(opened['transport'], 1)
        self.assertEqual(opened['play'], 'Play')
        self.assertEqual(opened['step'], 1)
        self.assertEqual(opened['speed'], 1)
        self.assertEqual(opened['scrub'], 0)
        self.assertEqual(opened['inputs'], ['engaged'])
        self.assertEqual(opened['readout'], '0:00.00')
        self.assertEqual(opened['posed'], 0,
                         'a posed driver panel stands beside the clocked one')

        # 3. PLAY for one wall second at x1: the clock advances by about
        # a second and the count follows the machine's own law -- a
        # release at every t = k + 0.5 -- rather than a number this test
        # invented.
        self.assertTrue(result['startedPlaying'])
        played = result['played']
        seconds = played['bank']['time']
        self.assertGreater(seconds, 0.3, 'the clock did not run')
        self.assertLessEqual(seconds, 1.3, 'the clock outran the wall')
        self.assertEqual(played['bank']['count'], int(seconds + 0.5))
        self.assertGreaterEqual(played['bank']['count'], 1)
        self.assertEqual(played['label'], 'Pause')
        self.assertNotEqual(played['readout'], '0:00.00')
        self.assertTrue(result['played_moved'],
                        'the bob did not swing while the clock ran')

        # 4. PAUSE holds the bank: nothing moves for 300 ms more.
        self.assertEqual(result['pausedLabel'], 'Play')
        self.assertEqual(result['heldAt'], result['pausedAt'])

        # 5. A 2 SECOND STEP advances the clock by exactly two seconds,
        # and the count by exactly two releases.
        before, stepped = result['beforeStep'], result['stepped']
        self.assertAlmostEqual(stepped['time'] - before['time'], 2.0,
                               places=12)
        self.assertEqual(stepped['count'] - before['count'], 2)

        # 5b. THE CLOCK'S OWN REQUESTS ARE NEVER DRAWN. A step
        # advances the readout and the bank by the stated seconds, and
        # a step taken WHILE THE TRANSPORT PLAYS leaves it playing --
        # where a drawn request would have stopped it, being the second
        # authority over the pose. (Mutation-checked: routing the step
        # or the played frame through the gesture duration fails these
        # two.)
        self.assertNotEqual(result['steppedUndrawn']['readout'],
                            result['readoutBeforeStep'])
        self.assertAlmostEqual(
            result['steppedUndrawn']['bank']['time'] - stepped['time'],
            2.0, places=12)
        self.assertTrue(result['playingBeforeStep'])
        self.assertTrue(result['steppedWhilePlaying']['playing'],
                        'a step stopped the transport that asked for it')
        self.assertAlmostEqual(
            result['steppedWhilePlaying']['bank']['time']
            - result['steppedUndrawn']['bank']['time'], 2.0, places=1)
        # And a PLAYED FRAME starts none either: 200 ms later the
        # transport is still playing and the clock has advanced.
        self.assertTrue(result['stillPlaying']['playing'],
                        'a played frame stopped the transport')
        self.assertGreater(result['stillPlaying']['bank']['time'],
                           result['steppedWhilePlaying']['bank']['time'])

        # 6. RESET returns the whole bank to its published defaults with
        # the clock at zero, and STOPS the transport.
        self.assertTrue(result['runningBeforeReset'])
        after = result['afterReset']
        self.assertEqual(after['bank'], {'engaged': 1, 'count': 0,
                                         'time': 0})
        self.assertFalse(after['playing'], 'reset left the clock running')
        self.assertEqual(after['readout'], '0:00.00')
        self.assertTrue(result['reset_to_rest'],
                        'the bob did not return to rest on screen')

        # 7. THE POSE FOLLOWS THE BANK: two instants, two pictures.
        self.assertTrue(result['two_instants_differ'],
                        'the bob stands in the same place at two instants')

        # 7b. And so does the READOUT, whoever moved the bank: a host
        # driving the handle directly leaves no stale instant on screen.
        moved = result['hostMoved']
        self.assertEqual(moved['bank']['time'], 5.25)
        self.assertEqual(moved['readout'], '0:05.25')
        self.assertEqual(moved['clock'], '5.2500')

        # 8. TIME NEVER REVERSES: a refusal, not a stop.
        backwards = result['backwards']
        self.assertIsNotNone(backwards, 'a backwards request was admitted')
        self.assertEqual(backwards['kind'], 'ValueError')
        self.assertIn('BACKWARDS', backwards['message'])
        self.assertIn('time', backwards['message'])
        self.assertEqual(result['afterRefusal']['time'], 5.25)

        # 8b. A REFUSED FRAME PAUSES the transport and reports across
        # the panel, once -- rather than repeating a refused request
        # every frame.
        self.assertTrue(result['askedToRun'])
        refused = result['refused']
        self.assertFalse(refused['playing'],
                         'a refused frame left the transport running')
        self.assertEqual(refused['label'], 'Play')
        self.assertFalse(refused['hidden'])
        self.assertIn('paused:', refused['message'])
        self.assertIn('surfaces', refused['message'])
        # A request refused whole commits NOTHING, so the clock stands
        # where the last accepted frame left it.
        self.assertEqual(result['stillRefused']['bank'], refused['bank'])
        self.assertFalse(result['stillRefused']['playing'])

        # 9. WHAT A PLAYED FRAME COSTS, in the page. Printed, and
        # asserted against ONE FRAME BUDGET: the per-frame decision
        # (design §5) is falsifiable only here -- a frame costing more
        # than 16 ms could not hold 60 of them in a second.
        timed = result['timed']
        for name in ('frame x1', 'frame x60', 'frame x3600', 'posed'):
            runs = timed[name]
            print(f'  Regulator {name} in the page: '
                  + ' / '.join(f'{one:.3f}' for one in runs) + ' ms')
            self.assertLess(min(runs), 16.0,
                            f'{name} costs more than one frame budget')

        # 10. A HOST RUNS THE CLOCK FROM ITS OWN PANEL: the chrome
        # suppressed, no transport pixels, and the whole machine API --
        # the two new verbs included -- unchanged.
        hosted = result['hosted']
        self.assertEqual(hosted['panels'], 0)
        self.assertEqual(hosted['transports'], 0)
        self.assertTrue(hosted['playing'])
        self.assertGreater(hosted['bank']['time'], 0.0,
                           'the clock did not advance with the chrome off')

        self.assertTrue((SHOTS / 'clocked-regulator-rest.png').is_file())
        self.assertTrue((SHOTS / 'clocked-regulator-played.png').is_file())
