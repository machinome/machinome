# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The acceptance: the Curta's CARRIAGE running in a real browser.

`tests/fixtures/carriage/viewer.json` is the framework's own
`tests/carriage_project/machine.py:CurtaCarriage`, exported verbatim from
a throwaway copy of machinome at `0b0f02a` -- a **version 7** document
whose nine law edges hold ONE BLOCK of seven, and which this viewer
refused by name until this cycle.

What this proves is the mechanism: four number dials ride on the
CARRIAGE and three carry levers belong to the FIXED frame, so the same
lever is tripped by dial `s` and advances dial `s + 1`, where `s` is the
carriage position the maker chose. At any one position the active
dependencies are a chain; their UNION over the working positions is a
cycle, and the union is what the compiled program orders. The published
order of that block's members is a LISTING, not an execution order.

Nothing here poses anything; everything is driven by the document's own
declared drivers, at the framework's own `dt = 0.02`.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from tests.support import (
    CARRIAGE, needs_bundle, needs_playwright, serve_directory,
)
from machinome_viewer.bundle import bundle_path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None

#: Where the inspected screenshots are written, so the evidence is a file
#: on disk rather than a claim.
SHOTS = Path(__file__).parent / '_shots'

#: The framework's own step for this machine.
DT = 0.02

DIALS = ('dial0.turn', 'dial1.turn', 'dial2.turn', 'dial3.turn')
LEVERS = ('lever0.travel', 'lever1.travel', 'lever2.travel')

#: The run's own agreement window, which the document publishes.
AGREEMENT = 1e-9


def model_paths(node):
    """Every model path a document's tree names, in tree order."""
    found = [node['model']] if node.get('model') else []
    for child in node.get('children') or []:
        found.extend(model_paths(child))
    return found


def agrees(actual, expected):
    """The run's own agreement rule, verbatim."""
    return abs(actual - expected) <= AGREEMENT * max(
        1.0, abs(actual), abs(expected))


class CarriageFixtureTest(TestCase):
    """The committed `carriage` fixture is complete on disk and is the
    document the README says it is.

    A missing mesh must fail as a missing mesh here rather than as a
    blank canvas in a browser test later.
    """

    def setUp(self):
        self.document = json.loads((CARRIAGE / 'viewer.json').read_text())

    def test_every_model_path_resolves_beside_the_document(self):
        paths = model_paths(self.document['root'])
        missing = [path for path in sorted(set(paths))
                   if not (CARRIAGE / path).is_file()]
        self.assertEqual(missing, [], 'the fixture names meshes it lacks')
        self.assertEqual(len(set(paths)), 2)

    def test_the_document_is_the_framework_s_own_machine(self):
        self.assertEqual((CARRIAGE / 'viewer.json').stat().st_size, 32790)
        self.assertEqual(self.document['version'], 7)
        self.assertEqual(sorted(self.document['drivers']),
                         ['clearing', 'crank', 'lift', 'position', 'reset'])
        program = self.document['program']
        self.assertTrue(program['identity'].startswith('917094ae'))
        self.assertEqual(len(program['coordinates']), 14)
        for entry in program['coordinates'].values():
            self.assertEqual(entry['initial'], 0.0)
        self.assertEqual(len(self.document['bindings']), 35)
        self.assertEqual(program['intermediates'], [])
        self.assertEqual(len(program['edges']), 9)

    def test_the_seat_span_reads_another_coordinate_on_both_sides(self):
        span = self.document['program']['spans']['seat']
        for side in ('low', 'high'):
            self.assertIsInstance(span[side], dict)
            self.assertIn('expression', span[side])
        # Both sides read `hoist`, through the bindings table or plainly:
        # the INTERLOCK is a bound that reads the lift.
        bindings = {one['name']: one['expression']
                    for one in self.document['bindings']}

        def reads(text, seen=()):
            found = set()
            for name in text.replace('(', ' ').replace(')', ' ').split():
                if name in bindings and name not in seen:
                    found |= reads(bindings[name], (*seen, name))
                else:
                    found.add(name)
            return found

        for side in ('low', 'high'):
            self.assertIn('hoist', reads(span[side]['expression']))

    def test_seven_of_its_nine_law_edges_form_ONE_block(self):
        """The block, re-derived from the published edges exactly as a
        consumer must: no key carries it."""
        edges = self.document['program']['edges']
        determiner = {}
        for index, edge in enumerate(edges):
            for key in edge.get('gives', ()):
                determiner[key] = index
        after = []
        for edge in edges:
            own = set(edge.get('gives', ()))
            after.append({determiner[key] for key in edge.get('needs', ())
                          if key in determiner and key not in own})
        members = set()
        for start in range(len(edges)):
            seen, pending = set(), list(after[start])
            while pending:
                node = pending.pop()
                if node in seen:
                    continue
                seen.add(node)
                pending.extend(after[node])
            if start in seen:
                members.add(start)
        self.assertEqual(sorted(members), [2, 3, 4, 5, 6, 7, 8])
        gives = sorted(key for index in members
                       for key in edges[index]['gives'])
        self.assertEqual(gives, sorted([*DIALS, *LEVERS]))
        # Each member carries a SELF-READ and each is published affine.
        for index in members:
            edge = edges[index]
            self.assertEqual(edge['kind'], 'law')
            self.assertEqual(len(edge['gives']), 1)
            self.assertEqual(set(edge['needs']) & set(edge['gives']),
                             set(edge['gives']))
            self.assertEqual(edge['affine'], [True])
        # And the two that are NOT in it are the lift and the carriage.
        self.assertEqual(edges[0]['gives'], ['hoist'])
        self.assertEqual(edges[1]['gives'], ['seat'])


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>curta carriage harness</title>
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

#: The carriage driven by its OWN declared drivers, at the framework's
#: own step: lift, shift, drop, crank -- then shift away and back, then
#: reset, then crank again. Every `step` count is the framework's own.
DRIVE = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json',
                                             { run: { dt: 0.02 } });
  const run = viewer.run();
  if (run === null) return { run: null };
  const crossings = [];
  const stops = [];
  run.onCommit((frame) => {
    for (const one of frame.crossings) crossings.push({ ...one });
    for (const one of frame.stops) stops.push({ ...one });
  });
  const mounted = {
    identity: run.identity(),
    dt: run.dt(),
    tick: run.tick(),
    bank: run.state(),
  };
  const drive = async (input, by, duration, ticks) => {
    const settled = run.move(input, { by, duration });
    await run.step(ticks);
    return (await settled).map((one) => [one.input, one.status,
                                         one.admitted]);
  };
  // 1. lift, shift to position 1, drop, crank by 36.
  await drive('lift', 1.0, 0.1, 5);
  await drive('position', 1.0, 0.2, 10);
  await drive('lift', -1.0, 0.1, 5);
  await drive('crank', 36.0, 0.4, 20);
  const carried = run.state();
  // 2. lift, shift to position 2, drop.
  await drive('lift', 1.0, 0.1, 5);
  await drive('position', 1.0, 0.2, 10);
  await drive('lift', -1.0, 0.1, 5);
  const shifted = run.state();
  // 3. lift, reset, drop.
  await drive('lift', 1.0, 0.1, 5);
  await drive('reset', 1.0, 0.2, 10);
  await drive('lift', -1.0, 0.1, 5);
  const reset = run.state();
  // 4. crank by 36 again: each lever now acts on the wheel it FACES.
  await drive('crank', 36.0, 0.4, 20);
  const again = run.state();
  return {
    mounted, carried, shifted, reset, again, stops,
    crossings: crossings.length,
    apiVersion: viewer.apiVersion,
    runsInWorker: run.runsInWorker,
  };
}"""

#: The INTERLOCK: with the carriage DOWN and a lever standing set, the
#: same shift is refused by the `seat` span that reads the hoist.
INTERLOCK = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'viewer.json',
                                             { run: { dt: 0.02 } });
  const run = viewer.run();
  const stops = [];
  run.onCommit((frame) => {
    for (const one of frame.stops) stops.push({ ...one });
  });
  const drive = async (input, by, duration, ticks) => {
    const settled = run.move(input, { by, duration });
    await run.step(ticks);
    return (await settled).map((one) => [one.input, one.status,
                                         one.admitted]);
  };
  await drive('lift', 1.0, 0.1, 5);
  await drive('position', 1.0, 0.2, 10);
  await drive('lift', -1.0, 0.1, 5);
  await drive('crank', 36.0, 0.4, 20);
  const pending = run.state();
  const outcome = await drive('position', 1.0, 0.2, 10);
  return { pending, outcome, after: run.state(), stops };
}"""

#: A RUN-TIME refusal reaching the page: the producer's `BothActive`
#: shape -- two laws each gated `shift >= 0.5`, orderable below the
#: detent and cyclic above it -- driven past its detent.
REFUSAL = """async () => {
  const host = document.getElementById('host');
  const viewer = await MachinomeViewer.mount(host, 'both-active.json',
                                             { run: { dt: 0.5 } });
  const run = viewer.run();
  const line = () => {
    const found = host.querySelector('.run-refusal');
    return found === null
      ? null : { hidden: found.hidden, text: found.textContent };
  };
  const before = run.state();
  // Below the detent the whole tick orders and the crank turns both.
  const settled = run.move('crank', { by: 1.0, duration: 0.5 });
  await run.step(1);
  const first = (await settled).map((one) => [one.input, one.status]);
  const ordered = run.state();
  const tick = run.tick();
  const quiet = line();
  // Driven PAST it, the piece above the detent cannot be ordered.
  run.move('shift', { by: 1.0, duration: 0.5 }).catch(() => undefined);
  let failed = null;
  try {
    await run.step(1);
  } catch (error) {
    failed = String(error);
  }
  return { before, ordered, after: run.state(), first, quiet, failed,
           refusal: line(), tick, tickAfter: run.tick() };
}"""


def both_active_document(models):
    """The producer's `BothActive` shape as a version 7 document.

    Hand written rather than exported, because it is a REFUSAL fixture:
    what it has to be is a document this loader accepts and whose every
    piece above the detent leaves both dependencies active.
    """
    part = {
        'name': 'lower', 'type': 'LeafNode', 'color': None, 'mtime': 0.0,
        'operations': [['r', 'lower.turn', [0, 0, 1]]],
        'model': models,
    }
    higher = {
        **part, 'name': 'higher',
        'operations': [['r', 'higher.turn', [0, 0, 1]],
                       ['t', ['30.0', '0.0', '0.0']]],
    }
    return {
        'format': 'machinome-export',
        'version': 7,
        'animation': {'fps': 30, 'frames': 360},
        'drivers': {
            'crank': {'default': 0.0, 'range': None, 'unit': 'deg',
                      'dtype': None, 'scale': None},
            'shift': {'default': 0.0, 'range': None, 'unit': None,
                      'dtype': None, 'scale': None},
        },
        'instructions': {},
        'root': {
            'name': 'BothActive', 'type': 'AssemblyNode', 'color': None,
            'mtime': 0.0, 'operations': [],
            'children': [part, higher],
        },
        'program': {
            'identity': 'both-active',
            'clock': 'time',
            'coordinates': {
                'crank': {'kind': 'input', 'initial': 0.0, 'domain': None},
                'shift': {'kind': 'input', 'initial': 0.0, 'domain': None},
                'lower.turn': {'kind': 'coordinate', 'initial': 0.0,
                               'unit': 'deg', 'domain': 'rotational'},
                'higher.turn': {'kind': 'coordinate', 'initial': 0.0,
                                'unit': 'deg', 'domain': 'rotational'},
            },
            'intermediates': [],
            'edges': [
                {
                    'kind': 'law',
                    'needs': ['crank', 'shift', 'higher.turn'],
                    'gives': ['lower.turn'],
                    'description':
                        '(crank, shift, higher.turn) drives lower.turn',
                    'stated_by': 'BothActive',
                    'expressions':
                        ['(crank + (higher.turn * (shift >= 0.5)))'],
                    'affine': [True],
                    'plans': [{
                        'skeleton': '(crank + (higher.turn * _j0))',
                        'jumps': [{'name': '_j0', 'primitive': '>=',
                                   'level': '(shift - 0.5)',
                                   'affine': True}],
                    }],
                },
                {
                    'kind': 'law',
                    'needs': ['crank', 'shift', 'lower.turn'],
                    'gives': ['higher.turn'],
                    'description':
                        '(crank, shift, lower.turn) drives higher.turn',
                    'stated_by': 'BothActive',
                    'expressions':
                        ['(crank + (lower.turn * (shift >= 0.5)))'],
                    'affine': [True],
                    'plans': [{
                        'skeleton': '(crank + (lower.turn * _j1))',
                        'jumps': [{'name': '_j1', 'primitive': '>=',
                                   'level': '(shift - 0.5)',
                                   'affine': True}],
                    }],
                },
            ],
            'spans': {},
            'sources': {
                'crank': ['crank'], 'shift': ['shift'],
                'lower.turn': ['crank', 'shift'],
                'higher.turn': ['crank', 'shift'],
            },
            'limits': {
                'crossing_tolerance': 1e-12, 'subdivisions': 64,
                'bisection_rounds': 64, 'max_crossings': 1000,
                'agreement': 1e-9,
            },
        },
    }


@needs_bundle
@needs_playwright
class CarriageInABrowserTest(TestCase):
    """The Curta's carriage, mounted, lifted, shifted, dropped and
    cranked."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = Path(self.tempdir.name) / 'carriage'
        shutil.copytree(CARRIAGE, self.out_dir)
        shutil.copy2(bundle_path(), self.out_dir / 'machinome-viewer.js')
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        document = json.loads((CARRIAGE / 'viewer.json').read_text())
        models = model_paths(document['root'])[0]
        (self.out_dir / 'both-active.json').write_text(
            json.dumps(both_active_document(models)))
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'
        self.document = document

    def open(self, browser):
        page = browser.new_page(viewport={'width': 800, 'height': 600})
        page.set_default_timeout(300_000)
        page.on('pageerror', lambda error: self.errors.append(str(error)))
        page.on('console', lambda message: self.errors.append(message.text)
                if message.type == 'error' else None)
        page.goto(self.harness_url)
        page.wait_for_function('typeof MachinomeViewer !== "undefined"')
        return page

    def test_the_carriage_carries_and_a_shift_preserves_every_part(self):
        SHOTS.mkdir(exist_ok=True)
        self.errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = self.open(browser)
                result = page.evaluate(DRIVE)
                # Pixels are evidence: the carriage at rest, and the
                # carriage carried.
                page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  window.__shot = await MachinomeViewer.mount(
                    host, 'viewer.json', { run: { dt: 0.02 } });
                }""")
                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'curta-carriage-at-rest.png'))
                page.evaluate("""async () => {
                  const run = window.__shot.run();
                  const drive = async (input, by, duration, ticks) => {
                    const settled = run.move(input, { by, duration });
                    await run.step(ticks);
                    await settled;
                  };
                  await drive('lift', 1.0, 0.1, 5);
                  await drive('position', 1.0, 0.2, 10);
                  await drive('lift', -1.0, 0.1, 5);
                  await drive('crank', 36.0, 0.4, 20);
                }""")
                page.wait_for_timeout(500)
                page.screenshot(path=str(SHOTS / 'curta-carriage-carried.png'))
            finally:
                browser.close()

        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

        # 1. It MOUNTED: the refusal this cycle removes is gone.
        mounted = result['mounted']
        self.assertIsNotNone(mounted, 'the handle reported no run')
        self.assertEqual(mounted['identity'],
                         self.document['program']['identity'])
        self.assertEqual(result['apiVersion'], 22)
        self.assertAlmostEqual(mounted['dt'], DT, places=12)
        self.assertEqual(mounted['tick'], 0)
        for name in (*DIALS, *LEVERS, 'seat', 'hoist'):
            self.assertEqual(mounted['bank'][name], 0.0)

        # 2. At position one, lever 0 faces dial 1 and advances dial 2;
        # lever 1 faces dial 2 and advances dial 3.
        carried = result['carried']
        self.assertTrue(agrees(carried['dial0.turn'], 36.0), carried)
        self.assertTrue(agrees(carried['dial1.turn'], 36.0), carried)
        self.assertTrue(agrees(carried['dial2.turn'], 72.0), carried)
        self.assertTrue(agrees(carried['dial3.turn'], 72.0), carried)
        self.assertEqual(carried['lever0.travel'], 1.0)
        self.assertEqual(carried['seat'], 20.0)

        # 3. Shifting away changes NOTHING but the carriage -- BIT FOR
        # BIT, every dial and every lever. That is what the walk's
        # parenthesised arithmetic is for: twenty ticks of lifting,
        # shifting and dropping add a TRUE zero to each of them.
        shifted = result['shifted']
        for key, value in carried.items():
            if key in ('position', 'seat', 'hoist', 'lift'):
                continue
            self.assertEqual(shifted[key], value,
                             f'{key}: {shifted[key]!r} != {value!r}')
        self.assertEqual(shifted['seat'], 40.0)

        # 4. The levers stay SET until the reset cam reaches them, which
        # it does only with the carriage lifted. The cam drives each
        # exactly ONTO its own surface, so they rest at the float sum of
        # its ten increments rather than at a literal zero, and a reading
        # taken ON a surface is outside the exact promise.
        reset = result['reset']
        for name in LEVERS[:2]:
            self.assertTrue(agrees(reset[name], 0.0),
                            f'{name}: {reset[name]!r}')
        self.assertTrue(agrees(reset['dial3.turn'], 72.0), reset)

        # 5. And now each lever acts on the wheel it FACES at this
        # position.
        again = result['again']
        self.assertTrue(agrees(again['dial2.turn'], 108.0), again)
        self.assertTrue(agrees(again['dial3.turn'], 144.0), again)
        self.assertTrue(agrees(again['lever2.travel'], 0.0), again)

        self.assertEqual(result['stops'], [])
        self.assertGreater(result['crossings'], 0)
        print('\nthe Curta carriage in a browser: '
              f"runsInWorker={result['runsInWorker']}\n"
              f"  carried: {carried}\n"
              f"  shifted: {shifted}\n"
              f"  reset:   {reset}\n"
              f"  again:   {again}\n"
              f"  crossings: {result['crossings']}, "
              f"stops: {len(result['stops'])}")

    def test_the_interlock_refuses_a_shift_while_a_lever_stands_set(self):
        self.errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = self.open(browser)
                result = page.evaluate(INTERLOCK)
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

        pending, after = result['pending'], result['after']
        self.assertEqual(pending['lever0.travel'], 1.0)
        self.assertEqual(pending['seat'], 20.0)
        # The shift retires BLOCKED with nothing admitted, and the
        # carriage stands where it stood.
        self.assertEqual(result['outcome'],
                         [['position', 'blocked', 0.0]])
        self.assertEqual(after['seat'], 20.0)
        stop = result['stops'][-1]
        self.assertEqual(stop['coordinate'], 'seat')
        self.assertEqual(stop['inputs'], ['position'])
        # Nothing discarded the pending carry and nothing finished it.
        for name in (*DIALS, *LEVERS):
            self.assertEqual(after[name], pending[name], name)

    def test_a_cyclic_piece_refuses_the_tick_in_the_page(self):
        self.errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = self.open(browser)
                result = page.evaluate(REFUSAL)
            finally:
                browser.close()
        self.assertEqual(self.errors, [],
                         f'the page logged errors: {self.errors}')

        # Below the detent the whole tick orders.
        self.assertEqual(result['first'], [['crank', 'completed']])
        self.assertEqual(result['ordered']['lower.turn'], 1.0)
        self.assertEqual(result['ordered']['higher.turn'], 1.0)

        # Nothing was refused while the selection left the cycle
        # breakable.
        self.assertIsNotNone(result['quiet'],
                             'the page built no run chrome to report into')
        self.assertTrue(result['quiet']['hidden'])

        # Driven PAST it the tick is refused, the refusal REACHES THE
        # PAGE, and the bank stands where it stood.
        refusal = result['refusal']
        self.assertFalse(refusal['hidden'], refusal)
        message = refusal['text']
        self.assertIn('form a cycle the run cannot order', message)
        self.assertIn('the selection this piece was read under leaves every '
                      'dependency on this cycle active', message)
        self.assertIn('The tick committed nothing', message)
        self.assertIn('over the piece [0.5, 1] of this tick', message)
        for name in ('lower.turn', 'higher.turn'):
            self.assertEqual(result['after'][name], result['ordered'][name],
                             name)
        # The tick count stands too: a refused tick committed nothing.
        self.assertEqual(result['tickAfter'], result['tick'])
