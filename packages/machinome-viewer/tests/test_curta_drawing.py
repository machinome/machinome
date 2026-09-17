# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

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

import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, skipUnless

from tests.support import needs_bundle, needs_playwright, serve_directory
from solid_node_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

ROOT = Path(__file__).resolve().parent.parent

#: Where this harness writes its screenshots. NOT in the repository:
#: these are measurement artefacts, and a measurement is not a contract.
SHOTS = Path(os.environ.get(
    'SOLID_NODE_CURTA_SHOTS', Path(tempfile.gettempdir()) / 'curta-drawing'))

#: Where the Curta's builds are, in the workspace this repository is
#: developed in. `SOLID_NODE_CURTA_BUILDS` overrides it for a checkout
#: somewhere else.
CURTA_BUILDS = Path(os.environ.get(
    'SOLID_NODE_CURTA_BUILDS',
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
    <script src="solid-widget.js"></script>
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
  const viewer = await SolidNodeWidget.mount(host, 'viewer.json', {});
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
        shutil.copy2(bundle_path(), out / 'solid-widget.js')
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
                    'typeof SolidNodeWidget !== "undefined"')
                clocked = page.evaluate(PLAY, 'clocked')
                SHOTS.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(SHOTS / 'curta-clocked-landed.png'))
                page.goto(fast_url)
                page.wait_for_function(
                    'typeof SolidNodeWidget !== "undefined"')
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
        self.assertEqual(clocked['apiVersion'], 19)
        # The canvas was not blank: a frame rate measured over an empty
        # scene would flatter this cycle, so the painted size is
        # recorded beside the numbers.
        print(f'  canvas bytes: clocked {clocked["settled"]} settled / '
              f'{clocked["painted"]} landed, posed {fast["settled"]} / '
              f'{fast["painted"]}; shots under {SHOTS}')
