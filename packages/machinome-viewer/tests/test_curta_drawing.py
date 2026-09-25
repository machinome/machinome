# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The MEASUREMENT: the Curta's own 'Turn crank', drawn and timed.

This is not a contract and nothing here is committed to this repository.
The Curta lives in the pilot's own workspace
(`projects/Calculators/Curta-Type-I-3x`) and publishes two builds beside
each other:

* `_build/clocked_curta/viewer.json` -- a **version 8** document, 23
  drivers, 18 states, 39 committing relations, 35 bounds,
  `clocked.clock: "time"`, and the single instruction
  `'Turn crank': by crank_rotation 360 over 2 s`, which this cycle
  PLAYS;
* `_build/fast_curta/viewer.json` -- a **version 4** posed document, 8
  drivers, 7 instructions, `'Turn crank': targets crank_turns 1 over
  6 s`, which the posed `Ramp` has always animated.

What is recorded is frames per second and the per-frame cost of a
drawing on each, on the same hardware in the same session, so the claim
"a clocked stroke can be WATCHED" is a number rather than an opinion.
The two per-frame costs are NOT the same work -- a clocked pose binds a
bank of 41 values against a posed document's 8 drivers -- and the test
asserts only that more than one distinct pose was drawn: a drawing that
renders once is the bug this cycle exists to remove.

Nothing is copied into this repository: the harness serves a temporary
directory of SYMLINKS to the build's own files. Where the build is
absent the test SKIPS with its reason, because this repository depends
on nothing outside itself.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, skipUnless

from tests.support import needs_bundle, needs_playwright, serve_directory
from machinome_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

ROOT = Path(__file__).resolve().parent.parent

#: Where this harness writes its screenshots. NOT in the repository:
#: these are measurement artefacts, and a measurement is not a contract.
SHOTS = Path(os.environ.get(
    'MACHINOME_CURTA_SHOTS', Path(tempfile.gettempdir()) / 'curta-drawing'))

#: Where the Curta's builds are, in the workspace this repository is
#: developed in. `MACHINOME_CURTA_BUILDS` overrides it for a checkout
#: somewhere else.
CURTA_BUILDS = Path(os.environ.get(
    'MACHINOME_CURTA_BUILDS',
    ROOT.parents[2] / 'projects' / 'Calculators' / 'Curta-Type-I-3x'
    / '_build'))

CLOCKED_CURTA = CURTA_BUILDS / 'clocked_curta'
FAST_CURTA = CURTA_BUILDS / 'fast_curta'

has_curta = (CLOCKED_CURTA / 'viewer.json').is_file() \
    and (FAST_CURTA / 'viewer.json').is_file()
needs_curta = skipUnless(
    has_curta, f'the Curta\'s own builds are not at {CURTA_BUILDS}')

HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>curta drawing harness</title>
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

#: Play `'Turn crank'` on whichever document is served, and time the
#: viewer's own animation-loop callback from the outside.
PLAY = """async (kind) => {
  const host = document.getElementById('host');
  const raw = window.requestAnimationFrame.bind(window);
  const costs = [];
  let timing = false;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    const began = performance.now();
    callback(stamp);
    if (timing) costs.push(performance.now() - began);
  });
  const frame = () => new Promise((resolve) => raw(() => resolve()));
  const mountedAt = performance.now();
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const mount = performance.now() - mountedAt;
  // 54 MB of meshes arrive after the mount resolves, so the timed phase
  // waits for the scene to settle: a frame rate measured over an empty
  // canvas would flatter this cycle.
  await new Promise((resolve) => setTimeout(resolve, 3000));
  const settled = host.querySelector('canvas').toDataURL().length;
  const machine = viewer.machine();
  const readings = [];
  const read = () => {
    if (kind === 'clocked') {
      const field = host.querySelector(
        '.clocked-value[data-input="crank_rotation"]');
      return field === null ? null : Number(field.value);
    }
    return viewer.driver('crank_turns');
  };

  // IDLE FIRST, on the same page: frames with NO drawing running, so
  // what a frame of a drawing costs can be told from what a frame of
  // this page costs. The difference is the POSE.
  timing = true;
  const idleAt = performance.now();
  for (let at = 0; at < 20; at += 1) await frame();
  const idleWall = (performance.now() - idleAt) / 1000;
  const idle = costs.splice(0, costs.length);
  timing = false;

  const solvedAt = performance.now();
  if (kind === 'clocked') {
    machine.trigger('Turn crank');
  }
  const solve = performance.now() - solvedAt;
  timing = true;
  const startedAt = performance.now();
  if (kind !== 'clocked') {
    viewer.trigger('Turn crank');
  }
  // The clocked build declares 2 s and the posed one 6 s; both are
  // watched to their own end, at 60 Hz plus a margin.
  const limit = kind === 'clocked' ? 2 : 6;
  for (let at = 0; at < 60 * (limit + 1); at += 1) {
    readings.push(read());
    await frame();
    if ((performance.now() - startedAt) / 1000 > limit + 0.5) break;
  }
  const wall = (performance.now() - startedAt) / 1000;
  timing = false;
  readings.push(read());
  return {
    mount, solve, wall, costs, readings, settled, idle, idleWall,
    painted: host.querySelector('canvas').toDataURL().length,
    distinct: new Set(readings).size,
    bank: machine === null ? null : machine.state(),
    apiVersion: viewer.apiVersion,
  };
}"""


#: The PILOT'S OWN GESTURE, on the Curta's own clocked build: the nudge
#: amount set to a whole turn of `crank_rotation` and the plus button
#: pressed, then the same stroke typed into the field, then the declared
#: `'Turn crank'` for comparison -- all three in ONE session on one page,
#: so the numbers are comparable.
#:
#: `crank_rotation` publishes `range: null`, so its row has no slider at
#: all: a number field, `-`, `+` and the amount box. That is the row the
#: project's own record tells a maker to operate
#: (`simulation/docs/clocked-curta-2026-09-17.md:42`).
GESTURE = """async (amount) => {
  const host = document.getElementById('host');
  const raw = window.requestAnimationFrame.bind(window);
  const costs = [];
  let timing = false;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    const began = performance.now();
    callback(stamp);
    if (timing) costs.push(performance.now() - began);
  });
  const frame = () => new Promise((resolve) => raw(() => resolve()));
  const mountedAt = performance.now();
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  const mount = performance.now() - mountedAt;
  // 54 MB of meshes arrive after the mount resolves, so the timed phase
  // waits for the scene to settle.
  await new Promise((resolve) => setTimeout(resolve, 3000));
  const settled = host.querySelector('canvas').toDataURL().length;
  const machine = viewer.machine();
  const panel = () => host.querySelector('.clocked-controls');
  const at = (selector) => panel().querySelector(selector);
  const box = () => at('.clocked-value[data-input="crank_rotation"]');
  const field = () => Number(box().value);

  // The nudge AMOUNT reaches the row's buttons only at the next rebuild
  // of the panel, so the reset that follows is what ARMS this gesture.
  const amountBox = at('.clocked-nudge[data-input="crank_rotation"]');
  amountBox.value = String(amount);
  amountBox.dispatchEvent(new Event('change'));
  at('.clocked-reset').click();

  // IDLE FIRST, on the same page: frames with NO drawing running, so
  // what a frame of a drawing costs can be told from what a frame of
  // this page costs.
  timing = true;
  const idleAt = performance.now();
  for (let n = 0; n < 12; n += 1) await frame();
  const idleWall = (performance.now() - idleAt) / 1000;
  const idle = costs.splice(0, costs.length);
  timing = false;

  // Watched UNTIL IT LANDS -- the reading reaching the bank the request
  // already stands at -- with `seconds` as a cap and not a window. A
  // gesture is now drawn at the TEMPO the document declares (OpenSpec
  // `draw-at-the-declared-tempo`): this build's `'Turn crank': by
  // crank_rotation 360 over 2 s` makes a nudge of a whole turn a
  // two-second drawing where it was a fifth of a second, so a fixed
  // one-second window would stop half-way through the picture.
  const watch = async (gesture, seconds) => {
    const readings = [];
    const solvedAt = performance.now();
    gesture();
    const solve = performance.now() - solvedAt;
    const atOnce = field();
    const end = machine.state().crank_rotation;
    timing = true;
    const startedAt = performance.now();
    while ((performance.now() - startedAt) / 1000 < seconds) {
      readings.push(field());
      await frame();
      if (field() === end) break;
    }
    const wall = (performance.now() - startedAt) / 1000;
    timing = false;
    readings.push(field());
    return { readings, atOnce, wall, solve, end,
             distinct: new Set(readings).size,
             costs: costs.splice(0, costs.length), bank: machine.state() };
  };

  const nudged = await watch(() => {
    at('.clocked-plus[data-input="crank_rotation"]').click();
  }, 8.0);
  const typed = await watch(() => {
    box().value = String(amount * 2);
    box().dispatchEvent(new Event('change'));
  }, 8.0);
  const declared = await watch(() => {
    machine.trigger('Turn crank');
  }, 8.0);

  // A TWELFTH of the declared travel, on the same page: the rate the
  // document states, on a gesture nobody declared.
  const smallBox = at('.clocked-nudge[data-input="crank_rotation"]');
  smallBox.value = '30';
  smallBox.dispatchEvent(new Event('change'));
  at('.clocked-reset').click();
  const small = await watch(() => {
    at('.clocked-plus[data-input="crank_rotation"]').click();
  }, 8.0);

  return { mount, settled, idle, idleWall, nudged, typed, declared, small,
           painted: host.querySelector('canvas').toDataURL().length,
           apiVersion: viewer.apiVersion };
}"""

#: The PHOTOGRAPH: one nudge, FROZEN after a stated number of frames.
#: The page's animation loop stops scheduling when its budget runs out,
#: so the last painted frame stands still for the camera -- a drawing of
#: a fifth of a second is otherwise over before a screenshot is taken.
#:
#: `stride` hands the loop its timestamps at a STATED spacing in
#: milliseconds instead of the wall's. This host renders 54 MB of meshes
#: on a software rasteriser at about two frames a second, so a 0.2 s
#: gesture gets ONE frame after its origin and lands in it; a stride of
#: 50 ms shows what the same gesture draws on a page that renders at
#: 20 fps. Nothing in the viewer is changed by it -- the drawing advances
#: on the elapsed seconds the loop reports, whatever reports them.
FREEZE = """async ({frames, stride, wait}) => {
  const host = document.getElementById('host');
  host.replaceChildren();
  const previous = window.requestAnimationFrame;
  const raw = previous.bind(window);
  let budget = Infinity;
  let clock = null;
  window.requestAnimationFrame = (callback) => raw((stamp) => {
    if (budget <= 0) return;
    budget -= 1;
    if (!(stride > 0)) return callback(stamp);
    clock = clock === null ? stamp : clock + stride;
    return callback(clock);
  });
  const viewer = await MachinomeViewer.mount(host, 'viewer.json', {});
  await new Promise((resolve) => setTimeout(resolve, 3000));
  const panel = () => host.querySelector('.clocked-controls');
  const at = (selector) => panel().querySelector(selector);
  const amount = at('.clocked-nudge[data-input="crank_rotation"]');
  amount.value = '360';
  amount.dispatchEvent(new Event('change'));
  at('.clocked-reset').click();
  budget = frames;
  at('.clocked-plus[data-input="crank_rotation"]').click();
  // Waited UNTIL IT LANDS rather than for a fixed 1500 ms: a gesture of
  // a whole turn is now drawn over the two seconds this build declares
  // (OpenSpec `draw-at-the-declared-tempo`), and at this host's frame
  // rate 1500 ms caught the picture part-way through. The FROZEN case
  // never lands -- its budget runs out first -- and waits out the cap.
  const reading = () => Number(
    at('.clocked-value[data-input="crank_rotation"]').value);
  const until = performance.now() + wait;
  while (performance.now() < until) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    if (reading() === viewer.machine().state().crank_rotation) break;
  }
  const read = {
    crank: reading(),
    bank: viewer.machine().state().crank_rotation,
  };
  window.requestAnimationFrame = previous;
  return read;
}"""


def middle(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2] if ordered else float('nan')


def report(name, result):
    costs = sorted(result['costs'])
    median = middle(costs)
    worst = costs[-1] if costs else float('nan')
    fps = len(result['costs']) / result['wall'] if result['wall'] else 0
    idle = middle(result['idle'])
    idle_fps = len(result['idle']) / result['idleWall'] \
        if result['idleWall'] else 0
    print(f'  {name}:')
    print(f'    mounted in {result["mount"] / 1000:.2f} s; '
          f'one solve {result["solve"]:.2f} ms')
    print(f'    IDLE (no drawing): {len(result["idle"])} frames over '
          f'{result["idleWall"]:.2f} s ({idle_fps:.1f} fps), per-frame '
          f'median {idle:.2f} ms')
    print(f'    DRAWING: {len(result["costs"])} frames over '
          f'{result["wall"]:.2f} s ({fps:.1f} fps), per-frame median '
          f'{median:.2f} ms, worst {worst:.2f} ms, '
          f'{result["distinct"]} distinct poses drawn')
    print(f'    the POSE, by difference: {median - idle:+.2f} ms a frame')
    return median, worst, fps


@needs_bundle
@needs_playwright
@needs_curta
class CurtaDrawingTest(TestCase):
    """(7.3) The Curta's own stroke, drawn and measured. SKIPPED where
    the pilot's builds are not on this machine."""

    def serve(self, build):
        """A temporary directory of SYMLINKS to `build`, beside this
        worktree's own bundle and a harness page. Nothing is copied."""
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        out = Path(tempdir.name)
        for entry in build.iterdir():
            (out / entry.name).symlink_to(entry)
        shutil.copy2(bundle_path(), out / 'machinome-viewer.js')
        (out / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(out)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        return f'{base}/harness.html'

    def test_the_stroke_is_drawn_on_both_builds_and_timed(self):
        clocked_url = self.serve(CLOCKED_CURTA)
        fast_url = self.serve(FAST_CURTA)
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                # 952 kB of document and 54 MB of meshes: a long timeout
                # is the honest one.
                page.set_default_timeout(600_000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(clocked_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                clocked = page.evaluate(PLAY, 'clocked')
                SHOTS.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(SHOTS / 'curta-clocked-landed.png'))
                page.goto(fast_url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                fast = page.evaluate(PLAY, 'posed')
                page.screenshot(path=str(SHOTS / 'curta-fast-landed.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')
        report("the CLOCKED Curta's 'Turn crank' (2 s)", clocked)
        report("fast_curta's 'Turn crank' (6 s, posed Ramp)", fast)

        # The one assertion: a drawing that renders ONCE is the bug this
        # cycle exists to remove. Everything else is a measurement, and a
        # measurement is not a contract.
        self.assertGreater(clocked['distinct'], 1,
                           'the clocked stroke drew one pose, not many')
        self.assertGreater(fast['distinct'], 1,
                           'the posed ramp drew one pose, not many')
        # And the machine stands at the transition's end throughout: the
        # bank is FINAL from the press.
        self.assertEqual(clocked['bank']['crank_rotation'], 360)
        self.assertEqual(clocked['apiVersion'], 27)
        # The canvas was not blank: a frame rate measured over an empty
        # scene would flatter this cycle, so the painted size is
        # recorded beside the numbers.
        print(f'  canvas bytes: clocked {clocked["settled"]} settled / '
              f'{clocked["painted"]} landed, posed {fast["settled"]} / '
              f'{fast["painted"]}; shots under {SHOTS}')


def gesture_report(name, result):
    """Print what one gesture drew and cost, and answer in numbers."""
    costs = sorted(result['costs'])
    median = middle(costs)
    fps = len(result['costs']) / result['wall'] if result['wall'] else 0
    print(f'  {name}:')
    print(f'    one solve {result["solve"]:.2f} ms; the panel read '
          f'{result["atOnce"]} on the gesture\'s own frame, the bank '
          f'{result["bank"]["crank_rotation"]}')
    print(f'    {len(result["costs"])} frames over {result["wall"]:.2f} s '
          f'({fps:.1f} fps), per-frame median {median:.2f} ms, '
          f'{result["distinct"]} distinct poses drawn')
    print(f'    readings: {result["readings"]}')
    return median


@needs_bundle
@needs_playwright
@needs_curta
class CurtaGestureTest(TestCase):
    """(5) The PILOT'S OWN GESTURE on the Curta, drawn and measured.

    SKIPPED where the pilot's builds are not on this machine. Nothing is
    copied out of that project: the harness serves a temporary directory
    of SYMLINKS to the build's own files.
    """

    def serve(self, build):
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        out = Path(tempdir.name)
        for entry in build.iterdir():
            (out / entry.name).symlink_to(entry)
        shutil.copy2(bundle_path(), out / 'machinome-viewer.js')
        (out / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(out)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        return f'{base}/harness.html'

    def test_the_pilots_own_nudge_is_drawn_on_the_curta_and_timed(self):
        url = self.serve(CLOCKED_CURTA)
        errors = []
        SHOTS.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800,
                                                  'height': 600})
                page.set_default_timeout(600_000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text)
                        if message.type == 'error' else None)
                page.goto(url)
                page.wait_for_function(
                    'typeof MachinomeViewer !== "undefined"')
                result = page.evaluate(GESTURE, 360)
                frozen = page.evaluate(
                    FREEZE, {'frames': 2, 'stride': 50, 'wait': 1500})
                page.screenshot(path=str(SHOTS / 'curta-nudge-drawing.png'))
                landed = page.evaluate(
                    FREEZE,
                    {'frames': 100_000, 'stride': 0, 'wait': 15_000})
                page.screenshot(path=str(SHOTS / 'curta-nudge-landed.png'))
            finally:
                browser.close()

        self.assertEqual(errors, [], f'the page logged errors: {errors}')

        # THE DOCUMENT AS FOUND, read at run time rather than assumed:
        # this project is the pilot's and republishes on its own clock.
        found = json.loads((CLOCKED_CURTA / 'viewer.json').read_text())
        declared_instructions = found.get('instructions') or {}
        print(f'  the build as found: version {found["version"]}, '
              f'clock {found["clocked"].get("clock")!r}, '
              f'{len(found.get("drivers") or {})} drivers, instructions '
              f'{json.dumps(declared_instructions)}')

        idle = middle(result['idle'])
        idle_fps = len(result['idle']) / result['idleWall'] \
            if result['idleWall'] else 0
        print(f'  mounted in {result["mount"] / 1000:.2f} s; IDLE (no '
              f'drawing): {len(result["idle"])} frames over '
              f'{result["idleWall"]:.2f} s ({idle_fps:.1f} fps), per-frame '
              f'median {idle:.2f} ms')
        stroke = declared_instructions.get('Turn crank') or {}
        tempo = stroke.get('duration')
        travel = (stroke.get('by') or {}).get('crank_rotation')
        nudged = gesture_report(
            f'the NUDGE of 360 deg (the declared tempo: {tempo} s)',
            result['nudged'])
        typed = gesture_report(
            f'the TYPED 720, a travel of 360 (tempo: {tempo} s)',
            result['typed'])
        declared = gesture_report(
            f"the declared 'Turn crank' ({tempo} s)", result['declared'])
        small = gesture_report(
            f'the NUDGE of 30 deg, a twelfth of the declared travel '
            f'(tempo: {tempo / 12 if tempo else None} s)', result['small'])
        print(f'    the POSE, by difference: nudge {nudged - idle:+.2f} ms, '
              f'typed {typed - idle:+.2f} ms, '
              f'declared {declared - idle:+.2f} ms, '
              f'small {small - idle:+.2f} ms a frame')

        # 5.2 ANSWERED IN NUMBERS. A one-tooth advance is TOOTH_PITCH =
        # 11.25 degrees of crank wide (the project's own
        # `simulation/cycle.py:7`), so at the declared tempo it occupies
        # 11.25 / 360 of the drawing's frames. Whether that is more than
        # one frame is a property of the PAGE'S FRAME RATE, not of this
        # cycle, and this host renders 54 MB of meshes on a software
        # rasteriser.
        frames = len(result['nudged']['costs'])
        fps = frames / result['nudged']['wall'] if result['nudged']['wall'] \
            else 0
        passage = frames * 11.25 / 360
        print(f'  THE TOOTH PASSAGE: the nudge of a whole turn drew '
              f'{frames} frames over {result["nudged"]["wall"]:.2f} s '
              f'({fps:.1f} fps), so 11.25 deg of 360 is {passage:.2f} '
              f'frames. At the fifth of a second ADR-065 drew it over, '
              f'the same page would have given the whole turn about '
              f'{max(1, round(fps * 0.2))} frame(s) and the passage '
              f'{fps * 0.2 * 11.25 / 360:.2f} of one.')
        print(f'  At 60 Hz the same tempo is {60 * (tempo or 0):.0f} frames '
              f'a stroke and {60 * (tempo or 0) * 11.25 / 360:.1f} frames a '
              f'passage; what this host managed is bounded by its own '
              f'frame rate and not by the rule.')
        if travel is not None:
            self.assertEqual(travel, result['nudged']['end'],
                             'the nudge did not ask for the declared travel')
        print(f'  canvas bytes: {result["settled"]} settled / '
              f'{result["painted"]} landed; shots under {SHOTS}')
        print(f'  frozen two 50 ms frames in: the panel read '
              f'{frozen["crank"]} with the bank at {frozen["bank"]}; '
              f'landed at {landed["crank"]}')

        # The assertions are the CONTRACT and nothing else: the gesture
        # is ONE request, made at the gesture, and the panel reads the
        # transition's ORIGIN on its own frame while the machine already
        # banks the end. How many frames that transition is drawn over on
        # THIS host is a measurement, and a measurement is not a
        # contract.
        self.assertEqual(result['nudged']['atOnce'], 0)
        self.assertEqual(result['nudged']['bank']['crank_rotation'], 360)
        self.assertEqual(result['nudged']['readings'][-1], 360)
        self.assertEqual(result['typed']['atOnce'], 360)
        self.assertEqual(result['typed']['bank']['crank_rotation'], 720)
        self.assertEqual(result['typed']['readings'][-1], 720)
        self.assertEqual(result['declared']['bank']['crank_rotation'], 1080)
        self.assertGreater(result['declared']['distinct'], 1,
                           'the declared stroke drew one pose, not many')
        # The TWELFTH lands where it was asked, drawn at the same rate.
        self.assertEqual(result['small']['bank']['crank_rotation'], 30)
        self.assertEqual(result['small']['readings'][-1], 30)
        # A gesture of the DECLARED travel and the instruction's own
        # PRESS are two ways of asking for one stroke: on this page they
        # take the same wall time, within a frame of it.
        print(f'  the nudge of the declared travel took '
              f'{result["nudged"]["wall"]:.2f} s and the press '
              f'{result["declared"]["wall"]:.2f} s')
        self.assertLess(
            abs(result['nudged']['wall'] - result['declared']['wall']),
            max(0.75, result['declared']['wall'] / 2))
        # The frozen picture is MID-TRAVEL: the model shows a crank
        # part-way round while the machine already banks the whole turn.
        self.assertGreater(frozen['crank'], 0)
        self.assertLess(frozen['crank'], 360)
        self.assertEqual(frozen['bank'], 360)
        self.assertEqual(landed['crank'], 360)
        self.assertEqual(result['apiVersion'], 27)
        self.assertTrue((SHOTS / 'curta-nudge-drawing.png').is_file())
        self.assertTrue((SHOTS / 'curta-nudge-landed.png').is_file())
