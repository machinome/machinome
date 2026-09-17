# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""End-to-end tests for the export widget: serve the fixture export over
HTTP, render it in headless chromium and assert on the pixels -- models
load with their colours, and the ?t= URL parameter poses the $t animation.

The mount-interface tests drive a real page with playwright instead,
because a screenshot cannot click a control or read an attribute.
"""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import run
from unittest import TestCase

from solid_node_viewer.bundle import api_version

from .support import (
    CHROME, HAS_PIL, HAS_PLAYWRIGHT, export_marked, export_with_widget,
    needs_bundle, needs_chrome, needs_pil, needs_playwright, serve_directory,
    strip_markings,
)

if HAS_PIL:
    from PIL import Image, ImageChops, ImageFilter
if HAS_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright


@needs_bundle
@needs_chrome
@needs_pil
class WidgetE2ETest(TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.base_url = f'{base}/index.html'

    def screenshot(self, query):
        path = os.path.join(self.tempdir.name, 'shot.png')
        result = run(
            [
                CHROME, '--headless', '--no-sandbox', '--disable-gpu',
                '--use-angle=swiftshader', '--window-size=800,600',
                '--virtual-time-budget=4000', f'--screenshot={path}',
                f'{self.base_url}?{query}',
            ],
            capture_output=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0,
                         f'chromium failed: {result.stderr.decode()[-500:]}')
        image = Image.open(path).convert('RGB')
        os.remove(path)
        # Crop off the control bar: pixel assertions are about the model.
        return image.crop((0, 0, image.width, image.height - 40))

    def count_pixels(self, image, predicate):
        return sum(1 for pixel in image.getdata() if predicate(*pixel))

    def test_models_render_with_their_colors(self):
        image = self.screenshot('t=0&autoplay=0')
        red = self.count_pixels(
            image, lambda r, g, b: r > 100 and r > 1.4 * g and r > 1.4 * b)
        blue = self.count_pixels(
            image, lambda r, g, b: b > 100 and b > 1.4 * r and b > 1.4 * g)
        self.assertGreater(red, 500, 'red hub not visible')
        self.assertGreater(blue, 2000, 'blue blades not visible')

    def test_time_parameter_poses_the_animation(self):
        at_zero = self.screenshot('t=0&autoplay=0')
        at_eighth = self.screenshot('t=0.125&autoplay=0')
        difference = ImageChops.difference(at_zero, at_eighth)
        changed = self.count_pixels(difference, lambda r, g, b: r + g + b > 30)
        self.assertGreater(changed, 2000, 'pose did not change with ?t=')

    def test_full_cycle_returns_to_start(self):
        at_zero = self.screenshot('t=0&autoplay=0')
        at_one = self.screenshot('t=1&autoplay=0')
        difference = ImageChops.difference(at_zero, at_one)
        changed = self.count_pixels(difference, lambda r, g, b: r + g + b > 30)
        self.assertLess(changed, 500, 't=0 and t=1 should render the same pose')


HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      html, body { margin: 0; }
      #host { width: 800px; height: 600px; position: relative; }
      #navHost { width: 300px; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <div id="navHost"></div>
    <script src="solid-widget.js"></script>
  </body>
</html>
"""


@needs_bundle
@needs_playwright
class ViewerMountApiTest(TestCase):
    """The mount interface hosts other than an export page need."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        manifest = json.loads((self.out_dir / 'manifest.json').read_text())
        manifest['drivers'] = {
            'turns': {
                'default': 0.0, 'range': [-55.0, 306.0], 'unit': 'turn',
                'dtype': None, 'scale': None,
            },
        }
        (self.out_dir / 'driven.json').write_text(json.dumps(manifest))
        # A second driven document, distinct from driven.json (whose
        # single-segment 'turns' id three existing assertions read):
        # navigableChildren (controls.ts:131-146) only offers a
        # breadcrumb descend button for an id of at least
        # focus.length + 2 segments, so a root-focused single-segment
        # driver id has nothing to descend into. 'Hub.turns' does --
        # 'Hub' is a real child of the Spinner fixture's root -- which
        # is what the breadcrumb notification test needs to click.
        nested = json.loads((self.out_dir / 'manifest.json').read_text())
        nested['drivers'] = {
            'Hub.turns': {
                'default': 0.0, 'range': [-55.0, 306.0], 'unit': 'turn',
                'dtype': None, 'scale': None,
            },
        }
        (self.out_dir / 'nested-driven.json').write_text(json.dumps(nested))
        (self.out_dir / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def in_page(self, script):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                result = page.evaluate(script)
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
                return result
            finally:
                browser.close()

    def test_dispose_leaves_the_container_empty(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const mounted = host.children.length;
          viewer.dispose();
          return { mounted, after: host.children.length };
        }""")
        self.assertGreater(result['mounted'], 0, 'nothing was mounted')
        self.assertEqual(result['after'], 0, 'dispose() left elements in the container')

    def test_the_bundle_and_mount_handle_report_one_api_version(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          return { bundle: SolidNodeWidget.apiVersion, handle: viewer.apiVersion,
                   run: viewer.run(), machine: viewer.machine() };
        }""")
        self.assertEqual(result['bundle'], api_version())
        self.assertEqual(result['bundle'], result['handle'])
        # OpenSpec `draw-what-a-part-carries`: drawing the markings a
        # document's parts carry is a capability a host may require, so
        # the declared version moves to 14. 13 is skipped deliberately
        # (design D9), the in-flight `slide-and-turn-parts` cycle
        # claiming it. OpenSpec `execute-the-self-read`: executing a
        # version 6 document -- a law that reads the coordinate it
        # drives -- is the next such capability, and unlike `controls`
        # and `markings` it is not additive, so this moves to 15 and the
        # document list moves with it. OpenSpec `execute-the-selection`:
        # executing a version 7 document -- a compiled program some of
        # whose law edges form a BLOCK, ordered per PIECE of a tick from
        # the published edges rather than run in the published listing --
        # is the one after that, and it is not additive either, so this
        # moves to 16 and the document list moves with it again. OpenSpec
        # `execute-the-commit`: executing a version 8 document -- a root
        # that declares a `State`, whose document carries a compiled
        # CLOCKED machine instead of a program -- is the one after that,
        # and it is not additive either, so this moves to 17 and the
        # document list moves with it again. OpenSpec `run-the-clock`:
        # ADVANCING a clocked machine's clock -- the elapsed seconds a
        # build at 17 banks, poses from and refuses every request on --
        # is the one after that, and this moves to 18; the document list
        # does NOT move with it, because no new document shape is read.
        self.assertEqual(result['bundle'], 18)
        # And a document carrying no program has no run and no machine,
        # which is what a host asking one question is answered with.
        self.assertIsNone(result['run'])
        self.assertIsNone(result['machine'])

    def test_the_mount_handle_exposes_and_controls_the_assembly(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const assembly = viewer.assembly();
          const target = assembly.children[0] ?? assembly;
          viewer.setRoot(target.path);
          viewer.setVisible(target.path, false);
          viewer.setVisible(target.path, true);
          let invalid = null;
          try { viewer.setRoot(['missing']); }
          catch (error) { invalid = String(error); }
          return {
            apiVersion: viewer.apiVersion,
            node: { name: assembly.name, path: assembly.path, color: assembly.color,
                    model: assembly.model, children: assembly.children.length },
            invalid,
          };
        }""")
        self.assertEqual(result['apiVersion'], api_version())
        self.assertEqual(result['node']['name'], 'Spinner')
        self.assertEqual(result['node']['path'], [])
        self.assertIsInstance(result['node']['model'], bool)
        self.assertEqual(result['node']['children'], 4)
        self.assertIn('Unknown assembly path: missing', result['invalid'])

    def test_navigation_reads_focus_and_hidden_and_notifies_once_per_source(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const target = viewer.assembly().children[0];
          const initial = viewer.navigation();

          const events = [];
          let consistent = true;
          const unsubscribe = viewer.onAssemblyChange((change) => {
            if (JSON.stringify(change.assembly) !== JSON.stringify(viewer.assembly())
                || JSON.stringify(change.navigation) !== JSON.stringify(viewer.navigation())) {
              consistent = false;
            }
            events.push(change.navigation);
          });

          viewer.setRoot(target.path);
          const afterSetRoot = { count: events.length, navigation: viewer.navigation() };

          viewer.setVisible(target.path, false);
          const afterSetVisible = { count: events.length, navigation: viewer.navigation() };

          await viewer.reload();
          const afterReload = { count: events.length, navigation: viewer.navigation() };

          await viewer.manifestChanged();
          const afterManifestChanged = { count: events.length, navigation: viewer.navigation() };

          unsubscribe();
          viewer.setVisible(target.path, true);
          const afterUnsubscribe = { count: events.length };

          return {
            targetPath: target.path, initial, consistent,
            afterSetRoot, afterSetVisible, afterReload, afterManifestChanged,
            afterUnsubscribe,
          };
        }""")
        self.assertEqual(result['initial'], {'root': None, 'hidden': []})
        self.assertTrue(result['consistent'],
                        'a listener read a snapshot unequal to a fresh read')
        target = result['targetPath']
        self.assertEqual(result['afterSetRoot']['count'], 1)
        self.assertEqual(result['afterSetRoot']['navigation']['root'], target)
        self.assertEqual(result['afterSetVisible']['count'], 2)
        self.assertIn(target, result['afterSetVisible']['navigation']['hidden'])
        self.assertEqual(result['afterReload']['count'], 3,
                         'reload() did not notify exactly once')
        self.assertEqual(result['afterReload']['navigation']['root'], target)
        self.assertEqual(result['afterManifestChanged']['count'], 4,
                         'manifestChanged() did not notify exactly once')
        self.assertEqual(result['afterManifestChanged']['navigation']['root'], target)
        self.assertIn(target, result['afterManifestChanged']['navigation']['hidden'])
        self.assertEqual(result['afterUnsubscribe']['count'], 4,
                         'a cancelled subscription was still notified')

    def test_a_redundant_visibility_call_still_notifies(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const target = viewer.assembly().children[0];
          let count = 0;
          viewer.onAssemblyChange(() => { count += 1; });

          viewer.setVisible(target.path, true);

          return { count, hidden: viewer.navigation().hidden };
        }""")
        self.assertEqual(result['count'], 1,
                         'showing an already-visible node did not notify (design D4)')
        self.assertEqual(result['hidden'], [])

    def test_a_refused_focus_notifies_nobody(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const before = viewer.navigation();
          let count = 0;
          viewer.onAssemblyChange(() => { count += 1; });

          let message = null;
          try { viewer.setRoot(['missing']); }
          catch (error) { message = String(error); }

          return { count, message, before, after: viewer.navigation() };
        }""")
        self.assertIn('Unknown assembly path: missing', result['message'])
        self.assertEqual(result['count'], 0, 'a refused setRoot notified a listener')
        self.assertEqual(result['before'], result['after'])

    def test_cancel_and_dispose_stop_notifications(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const target = viewer.assembly().children[0];

          let cancelledCount = 0;
          const cancel = viewer.onAssemblyChange(() => { cancelledCount += 1; });
          cancel();
          viewer.setRoot(target.path);
          const afterCancel = cancelledCount;

          let disposedCount = 0;
          viewer.onAssemblyChange(() => { disposedCount += 1; });
          viewer.dispose();
          const disposeNotified = disposedCount;

          let cancelAfterDisposeThrew = false;
          try { cancel(); }
          catch { cancelAfterDisposeThrew = true; }

          return { afterCancel, disposeNotified, cancelAfterDisposeThrew };
        }""")
        self.assertEqual(result['afterCancel'], 0,
                         'a cancelled subscription still received a notification')
        self.assertEqual(result['disposeNotified'], 0, 'dispose() itself notified')
        self.assertFalse(result['cancelAfterDisposeThrew'],
                         'the cancel function was not safe to call after dispose()')

    def test_each_explicitly_hidden_path_is_tracked_independently(self):
        # The Spinner fixture is flat (Hub, b0, b1, b2 are siblings under
        # the root), so this proves the WIRING through the handle: each
        # path hidden explicitly stays listed until it is itself shown
        # again, regardless of another path's visibility. The stronger
        # claim design D3 makes -- a node made invisible only because an
        # ANCESTOR is hidden is never itself listed -- needs a nested
        # tree and is pinned at the unit level, against a real
        # parent/child fixture, in assembly.test.ts's 'state' block.
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const assembly = viewer.assembly();
          const first = assembly.children[0];
          const second = assembly.children[1];

          viewer.setVisible(first.path, false);
          viewer.setVisible(second.path, false);
          const bothHidden = viewer.navigation().hidden;

          viewer.setVisible(first.path, true);
          const afterShowingFirst = viewer.navigation().hidden;

          return { firstPath: first.path, secondPath: second.path,
                   bothHidden, afterShowingFirst };
        }""")
        self.assertIn(result['firstPath'], result['bothHidden'])
        self.assertIn(result['secondPath'], result['bothHidden'])
        self.assertNotIn(result['firstPath'], result['afterShowingFirst'])
        self.assertIn(result['secondPath'], result['afterShowingFirst'],
                      'showing one hidden path dropped an unrelated one from the explicit set')

    def test_the_breadcrumb_notifies_a_subscribed_host(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(
            host, 'nested-driven.json', { autoplay: false });
          const events = [];
          viewer.onAssemblyChange((change) => { events.push(change.navigation.root); });

          const descend = host.querySelector('.driver-descend');
          const label = descend ? descend.getAttribute('aria-label') : null;
          descend?.click();

          return { label, events, navigation: viewer.navigation() };
        }""")
        self.assertEqual(result['label'], 'Focus Hub')
        self.assertEqual(result['events'], [['Hub']],
                         'the breadcrumb descend did not notify a subscribed host')
        self.assertEqual(result['navigation']['root'], ['Hub'])

    def test_a_targeted_update_notifies_once_with_reconciled_state(self):
        # Playwright directly, not in_page (which runs one script): a
        # file write has to land BETWEEN two evaluations of the same
        # page, as `solid develop`'s targeted update does.
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                setup = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
                  window.__viewer = viewer;
                  const assembly = viewer.assembly();
                  const focused = assembly.children[0];
                  const hidden = assembly.children[1];
                  viewer.setRoot(focused.path);
                  viewer.setVisible(hidden.path, false);
                  window.__events = [];
                  viewer.onAssemblyChange((change) => {
                    window.__events.push(change.navigation);
                  });
                  return { focusedName: focused.path[0], hiddenName: hidden.path[0] };
                }""")

                # A targeted update that discards the focused root and
                # the hidden path: drop both from the published tree.
                manifest = json.loads((self.out_dir / 'manifest.json').read_text())
                dropped = {setup['focusedName'], setup['hiddenName']}
                manifest['root']['children'] = [
                    child for child in manifest['root']['children']
                    if child['name'] not in dropped
                ]
                (self.out_dir / 'manifest.json').write_text(json.dumps(manifest))

                result = page.evaluate("""async () => {
                  await window.__viewer.manifestChanged();
                  return {
                    count: window.__events.length,
                    navigation: window.__events[window.__events.length - 1],
                  };
                }""")
            finally:
                browser.close()

        self.assertEqual(errors, [], f'uncaught page errors: {errors}')
        self.assertEqual(result['count'], 1,
                         'a targeted update that discards state did not notify exactly once')
        self.assertEqual(result['navigation'], {'root': None, 'hidden': []})

    def test_the_bundle_mounts_a_navigator_from_a_handle(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const navHost = document.getElementById('navHost');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const nav = SolidNodeWidget.mountNavigator(navHost, viewer);
          const rows = [...navHost.querySelectorAll('[role="treeitem"]')];
          const info = rows.map((row) => ({
            role: row.getAttribute('role'),
            label: row.querySelector('.solid-nav-name')?.textContent,
          }));
          nav.dispose();
          return { count: rows.length, info };
        }""")
        self.assertEqual(result['count'], 5, 'root + four children were not all drawn')
        self.assertEqual([item['role'] for item in result['info']], ['treeitem'] * 5)
        self.assertEqual(result['info'][0]['label'], 'Spinner')

    def test_the_navigator_keyboard_drives_the_viewer(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const navHost = document.getElementById('navHost');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const nav = SolidNodeWidget.mountNavigator(navHost, viewer);
          const rows = () => [...navHost.querySelectorAll('.solid-nav-row')];
          const press = (key) => document.activeElement.dispatchEvent(
            new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true }));

          rows().find((row) => row.tabIndex === 0).focus();
          press('ArrowDown');
          const firstChildLabel = document.activeElement.querySelector('.solid-nav-name').textContent;
          press('Enter');
          const rootAfterEnter = viewer.navigation().root;
          press(' ');
          const hiddenAfterSpace = viewer.navigation().hidden;
          press('ArrowLeft');
          const labelAfterLeft = document.activeElement.querySelector('.solid-nav-name').textContent;

          nav.dispose();
          return { firstChildLabel, rootAfterEnter, hiddenAfterSpace, labelAfterLeft };
        }""")
        self.assertEqual(result['rootAfterEnter'], [result['firstChildLabel']])
        self.assertEqual(result['hiddenAfterSpace'], [[result['firstChildLabel']]])
        self.assertEqual(result['labelAfterLeft'], 'Spinner')

    def test_the_breadcrumb_moves_the_navigators_root(self):
        # nested-driven.json (design D9/D4's own fixture, `:134-141`):
        # 'Hub' is a real child of the Spinner root, so the driver
        # chrome's breadcrumb offers a descend button for it.
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const navHost = document.getElementById('navHost');
          const viewer = await SolidNodeWidget.mount(
            host, 'nested-driven.json', { autoplay: false });
          const nav = SolidNodeWidget.mountNavigator(navHost, viewer);

          const descend = host.querySelector('.driver-descend');
          descend?.click();

          const hubRow = [...navHost.querySelectorAll('.solid-nav-row')]
            .find((row) => row.querySelector('.solid-nav-name')?.textContent === 'Hub');
          const outcome = {
            found: hubRow !== undefined,
            selected: hubRow?.getAttribute('aria-selected'),
            root: viewer.navigation().root,
          };
          nav.dispose();
          return outcome;
        }""")
        self.assertTrue(result['found'], 'the navigator has no row for Hub')
        self.assertEqual(result['selected'], 'true',
                         'the breadcrumb descend did not reach the navigator with no host code')
        self.assertEqual(result['root'], ['Hub'])

    def test_a_targeted_update_reconciles_the_navigator(self):
        # Playwright directly, not in_page: a manifest.json write has to
        # land BETWEEN two page evaluations, as `solid develop`'s
        # targeted update does (matching
        # test_a_targeted_update_notifies_once_with_reconciled_state
        # above). The Spinner fixture is flat -- Hub, b0, b1, b2 are all
        # LeafNodes with no children of their own -- so there is no
        # CHILD row to expand and reveal grandchildren of here; this
        # proves the navigator's reconciliation against the only
        # expandable row the fixture has (the document root) instead: it
        # survives the update, a removed child's row is gone, a kept
        # child's row survives, and exactly one row is still the
        # keyboard stop.
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                setup = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  const navHost = document.getElementById('navHost');
                  const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
                  const nav = SolidNodeWidget.mountNavigator(navHost, viewer);
                  window.__viewer = viewer;
                  window.__nav = nav;
                  const names = [...navHost.querySelectorAll('.solid-nav-name')]
                    .map((el) => el.textContent);
                  return { names };
                }""")
                removed_name = setup['names'][1]
                kept_name = setup['names'][2]

                manifest = json.loads((self.out_dir / 'manifest.json').read_text())
                manifest['root']['children'] = [
                    child for child in manifest['root']['children']
                    if child['name'] != removed_name
                ]
                (self.out_dir / 'manifest.json').write_text(json.dumps(manifest))

                result = page.evaluate("""async () => {
                  await window.__viewer.manifestChanged();
                  const navHost = document.getElementById('navHost');
                  const rows = [...navHost.querySelectorAll('.solid-nav-row')];
                  return {
                    names: rows.map((row) => row.querySelector('.solid-nav-name').textContent),
                    rootExpanded: rows[0].getAttribute('aria-expanded'),
                    tabStops: rows.filter((row) => row.tabIndex === 0).length,
                  };
                }""")
            finally:
                browser.close()

        self.assertEqual(errors, [], f'uncaught page errors: {errors}')
        self.assertNotIn(removed_name, result['names'], 'the removed child\'s row survived')
        self.assertIn(kept_name, result['names'], 'a surviving child lost its row')
        self.assertEqual(result['rootExpanded'], 'true', 'the root\'s expansion was not kept')
        self.assertEqual(result['tabStops'], 1, 'the tree lost its single keyboard stop')

    def test_two_navigators_agree_and_dispose_independently(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const navHost = document.getElementById('navHost');
          const navHost2 = document.createElement('div');
          document.body.appendChild(navHost2);
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const navA = SolidNodeWidget.mountNavigator(navHost, viewer);
          const navB = SolidNodeWidget.mountNavigator(navHost2, viewer);

          const firstChip = (root) => root.querySelectorAll('.solid-nav-visibility')[1];
          firstChip(navHost).click();
          const afterHide = {
            a: firstChip(navHost).checked,
            b: firstChip(navHost2).checked,
            styleCount: document.querySelectorAll('#solid-node-navigator-style').length,
          };

          navA.dispose();
          const navHostEmptyAfterDispose = navHost.children.length === 0;

          const secondChip = (root) => root.querySelectorAll('.solid-nav-visibility')[2];
          secondChip(navHost2).click();
          const bStillUpdates = secondChip(navHost2).checked === false;

          navB.dispose();
          return { afterHide, navHostEmptyAfterDispose, bStillUpdates };
        }""")
        self.assertEqual(result['afterHide']['a'], result['afterHide']['b'])
        self.assertFalse(result['afterHide']['a'], 'hiding in one navigator did not reach the other')
        self.assertEqual(result['afterHide']['styleCount'], 1,
                         'two navigators injected more than one stylesheet')
        self.assertTrue(result['navHostEmptyAfterDispose'])
        self.assertTrue(result['bStillUpdates'],
                        'the surviving navigator stopped updating after the other disposed')

    def test_a_captured_view_survives_a_remount(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const first = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const moved = {
            camera: first.view().camera.clone().multiplyScalar(2),
            target: first.view().target.clone(),
          };
          first.dispose();
          const second = await SolidNodeWidget.mount(host, 'manifest.json', { view: moved });
          const got = second.view();
          return {
            want: [moved.camera.x, moved.camera.y, moved.camera.z],
            got: [got.camera.x, got.camera.y, got.camera.z],
          };
        }""")
        for want, got in zip(result['want'], result['got']):
            self.assertAlmostEqual(want, got, places=4, msg='remount did not restore the view')

    def test_reload_keeps_the_maker_looking_where_they_were(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const before = viewer.view();
          const want = [before.camera.x, before.camera.y, before.camera.z];
          await viewer.reload();
          const after = viewer.view();
          return { want, got: [after.camera.x, after.camera.y, after.camera.z] };
        }""")
        for want, got in zip(result['want'], result['got']):
            self.assertAlmostEqual(want, got, places=4, msg='reload() moved the camera')

    def test_manifest_update_keeps_the_canvas_and_camera(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'manifest.json', {});
          const canvas = host.querySelector('canvas');
          const before = viewer.view();
          await viewer.manifestChanged();
          const after = viewer.view();
          return {
            sameCanvas: canvas === host.querySelector('canvas'),
            before: [before.camera.x, before.camera.y, before.camera.z],
            after: [after.camera.x, after.camera.y, after.camera.z],
          };
        }""")
        self.assertTrue(result['sameCanvas'], 'manifest update replaced the canvas')
        for before, after in zip(result['before'], result['after']):
            self.assertAlmostEqual(before, after, places=4, msg='manifest update moved the camera')

    def test_the_host_names_the_canvas(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          await SolidNodeWidget.mount(host, 'manifest.json', {
            className: 'functional-model', role: 'img', ariaLabel: 'Functional model',
          });
          const canvas = host.querySelector('canvas');
          return { className: canvas.className, role: canvas.getAttribute('role'),
                   label: canvas.getAttribute('aria-label') };
        }""")
        self.assertEqual(result['className'], 'functional-model')
        self.assertEqual(result['role'], 'img')
        self.assertEqual(result['label'], 'Functional model')

    def test_a_slider_readout_accepts_an_exact_number(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await SolidNodeWidget.mount(host, 'driven.json',
                                                     { autoplay: false });
          const row = host.querySelector('.driver-control');
          const slider = row.querySelector('input[type=range]');
          const passive = row.querySelector('.driver-readout-value');
          const before = {
            shown: passive.textContent,
            numberInputs: row.querySelectorAll('input[type=number]').length,
          };
          passive.click();
          const exact = row.querySelector('.driver-readout-editor');
          if (exact === null) return { present: false, before };
          const editing = {
            type: exact.type,
            visible: exact.offsetParent !== null,
            selected: exact.selectionStart === 0
              && exact.selectionEnd === exact.value.length,
          };
          exact.value = '25.82';
          exact.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
          const inside = { driver: viewer.driver('turns'),
                           slider: slider.value, unit: row.textContent };
          passive.click();
          exact.value = '400';
          exact.blur();
          passive.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
          exact.value = '';
          exact.blur();
          const afterInvalid = viewer.driver('turns');
          passive.click();
          exact.value = '12';
          exact.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
          return { present: true, inside, outside: viewer.driver('turns'),
                   pinned: slider.value, shown: passive.textContent,
                   passiveVisible: passive.offsetParent !== null,
                   afterInvalid,
                   before, editing,
                   label: exact.getAttribute('aria-label') };
        }""")
        self.assertTrue(result['present'])
        self.assertEqual(result['before']['shown'], '0.0000')
        self.assertEqual(result['before']['numberInputs'], 0)
        self.assertEqual(result['editing']['type'], 'text')
        self.assertTrue(result['editing']['visible'])
        self.assertTrue(result['editing']['selected'])
        self.assertEqual(result['inside']['driver'], 25.82)
        self.assertEqual(result['inside']['slider'], '25.82')
        self.assertIn('turn', result['inside']['unit'])
        self.assertEqual(result['outside'], 400)
        self.assertEqual(result['afterInvalid'], 400)
        self.assertEqual(result['pinned'], '306')
        self.assertEqual(result['shown'], '400.0000')
        self.assertTrue(result['passiveVisible'])
        self.assertIn('exact value', result['label'])

    def test_the_toggle_presentation_starts_collapsed(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          await SolidNodeWidget.mount(host, 'manifest.json', { animation: 'toggle' });
          const toggle = host.querySelector('.timeline-toggle');
          const bar = host.querySelector('.animation-controls');
          const collapsed = { expanded: toggle.getAttribute('aria-expanded'),
                              barVisible: bar.offsetParent !== null };
          toggle.click();
          return { collapsed, expanded: toggle.getAttribute('aria-expanded'),
                   barVisible: bar.offsetParent !== null };
        }""")
        self.assertEqual(result['collapsed']['expanded'], 'false')
        self.assertFalse(result['collapsed']['barVisible'])
        self.assertEqual(result['expanded'], 'true')
        self.assertTrue(result['barVisible'])


@needs_bundle
@needs_playwright
class InspectorLayoutE2ETest(TestCase):
    """The standalone export page selects a layout (design D8): the
    shipped `index.html` carries `data-solid-layout="inspector"`, and a
    page written before this capability existed carries no such
    attribute and mounts the plain viewer exactly as it always has."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_with_widget(Path(self.tempdir.name) / 'export')
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.base_url = f'{base}/index.html'
        self.dir_url = base

    @contextmanager
    def open_page(self, url=None):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url or self.base_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                yield page, errors
            finally:
                browser.close()

    def test_the_export_page_mounts_the_inspector(self):
        with self.open_page() as (page, errors):
            page.wait_for_selector('.solid-inspector')
            self.assertEqual(page.locator('.solid-inspector-toggle').count(), 1)
            # Collapsed by default (design D3): the `hidden` attribute is
            # present on the sidebar.
            self.assertIsNotNone(
                page.locator('.solid-inspector-sidebar').get_attribute('hidden'))
            self.assertEqual(errors, [])

    def test_the_toggle_opens_the_sidebar_and_the_canvas_narrows(self):
        with self.open_page() as (page, errors):
            page.wait_for_selector('.solid-inspector-viewer canvas')
            canvas = page.locator('.solid-inspector-viewer canvas')
            before = canvas.bounding_box()['width']

            page.locator('.solid-inspector-toggle').click()
            page.wait_for_selector('.solid-nav-tree [role="treeitem"]')
            self.assertIsNone(
                page.locator('.solid-inspector-sidebar').get_attribute('hidden'))
            # The viewer resizes through its own ResizeObserver, which
            # fires after layout: wait for the canvas to follow the pane
            # rather than reading its width in the same turn as the click.
            narrowed = ("(before) => document.querySelector('.solid-inspector-viewer canvas')"
                        ".getBoundingClientRect().width < before")
            page.wait_for_function(narrowed, arg=before, timeout=5_000)
            opened = canvas.bounding_box()['width']
            self.assertLess(opened, before, 'the canvas did not narrow when the sidebar opened')

            page.locator('.solid-inspector-toggle').click()
            self.assertIsNotNone(
                page.locator('.solid-inspector-sidebar').get_attribute('hidden'))
            restored = ("(before) => Math.abs(document.querySelector('.solid-inspector-viewer canvas')"
                        ".getBoundingClientRect().width - before) <= 2")
            page.wait_for_function(restored, arg=before, timeout=5_000)
            closed = canvas.bounding_box()['width']
            self.assertAlmostEqual(closed, before, delta=2,
                                   msg='the canvas did not return to its width when closed')
            self.assertEqual(errors, [])

    def test_the_query_string_opens_the_sidebar(self):
        with self.open_page(f'{self.base_url}?sidebar=open') as (page, errors):
            page.wait_for_selector('.solid-inspector-sidebar')
            self.assertIsNone(
                page.locator('.solid-inspector-sidebar').get_attribute('hidden'),
                'the sidebar attribute did not override the collapsed default')
            self.assertEqual(errors, [])

    def test_a_page_without_a_layout_attribute_mounts_the_plain_viewer(self):
        # A hand-written page carrying only data-solid-widget -- the
        # compatibility promise every already-published export keeps.
        (self.out_dir / 'plain.html').write_text(
            '<!doctype html><html><body>'
            '<div id="solid-widget" data-solid-widget="manifest.json"></div>'
            '<script src="solid-widget.js"></script></body></html>'
        )
        with self.open_page(f'{self.dir_url}/plain.html') as (page, errors):
            page.wait_for_selector('#solid-widget canvas')
            self.assertEqual(page.locator('.solid-inspector').count(), 0)
            self.assertEqual(errors, [])

    def test_an_unknown_layout_is_refused_by_name(self):
        with self.open_page(f'{self.base_url}?layout=bogus') as (page, errors):
            page.wait_for_function(
                "document.getElementById('solid-widget').textContent"
                ".includes('unknown layout')")
            text = page.locator('#solid-widget').text_content()
            self.assertIn('unknown layout "bogus"', text)



MARKED_HARNESS = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      /* A saturated dark blue behind the canvas. The probes below read
         near-white and NEUTRAL GREY, and a neutral page colour would
         answer both of them everywhere. */
      html, body { margin: 0; background: #08183f; }
      #host { width: 640px; height: 480px; position: relative; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="solid-widget.js"></script>
  </body>
</html>
"""


@needs_bundle
@needs_playwright
@needs_pil
class MarkedDocumentPixelsTest(TestCase):
    """The markings a part carries, on screen.

    Pixels are the evidence, and the fixture is built for it: the `dial`
    and the `plate` declare NO colour, so both render through
    `MeshNormalMaterial`, whose output is `normal * 0.5 + 0.5`. Two
    probes follow from that, and the part provably trips neither.

    **Near-white.** A unit normal cannot exceed 0.577 in all three
    components at once, so the brightest GREY the part can show is 201 --
    and an antialiased edge cannot beat it either, an averaged pair of
    unit normals being no longer than a unit normal. `#FFFFFF` decals
    pass it.

    **Neutral grey.** `normal * 0.5 + 0.5` is neutral only where
    |nx| = |ny| = |nz|, which a cylinder about z (whose normals are
    (cos, sin, 0) and (0, 0, +-1)) and an axis-aligned box never reach.
    Both declared marking colours -- `#FFFFFF` and `#C0C0C0` -- ARE
    neutral under the scene's near-white lights, at any brightness.

    NOTE, and a choice for the pilot. The ratified design D12 probes all
    four of its steps with near-white alone. Measured here, that does not
    hold for two of them, and the two probes above are this
    implementation's answer:

      * a `#FFFFFF` surface in this scene never renders brighter than
        213 in its darkest channel, and the DIAL's decal -- whose
        normals are horizontal, while the one directional light shines
        from (1, -1, 2) -- never passes 180. Near-white cannot see the
        turning decal at all, at any camera angle (measured over a
        12 x 3 sweep of azimuth and elevation);
      * the fixture's `band` decal is `#C0C0C0` by declaration, so
        near-white cannot see it either, and "every non-near-white pixel
        is unchanged" is false wherever it is drawn.

    Neutral grey answers both, with a proof of the same kind D12's own
    is. It is a deviation from the ratified test design and is recorded
    rather than taken silently.
    """

    #: `(0.577 * 0.5 + 0.5) * 255 = 201`: the ceiling the part's own
    #: material cannot pass in all three channels at once. The probe sits
    #: just above it.
    NEAR_WHITE = 205
    #: How far from neutral a pixel may be and still read as a marking's
    #: own colour, and how dark before it is background or shadow rather
    #: than a decal.
    NEUTRAL_SPREAD = 20
    NEUTRAL_FLOOR = 40

    #: The whole bench, at a FIXED camera. The document's own fit box
    #: includes its decals (design D8 -- the `band` lies at radius 12.0
    #: on a plate whose box is +-10.0), so a marked document and its
    #: unmarked twin do not frame alike; pinning the view is what makes
    #: "every pixel that is not the decal is unchanged" a question about
    #: the decal rather than about the framing.
    BENCH_VIEW = {'camera': [-55.1, 55.1, 55.0], 'target': [0.0, 0.0, 10.0]}
    #: The dial alone. The azimuth is chosen so that part of the artwork
    #: faces the camera at `angle = 0` AND part of it does at
    #: `angle = 180`: the artwork covers 12 to 121 degrees of the drum,
    #: and a camera sees a 180-degree window of it.
    DIAL_VIEW = {'camera': [-60.1, 26.7, 43.9], 'target': [0.0, 0.0, 20.0]}

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.out_dir = export_marked(Path(self.tempdir.name) / 'export')
        # The unmarked twin, written by the test and never committed: the
        # same document, one `del` away (design D11).
        strip_markings(self.out_dir / 'manifest.json',
                       self.out_dir / 'unmarked.json')
        (self.out_dir / 'harness.html').write_text(MARKED_HARNESS)
        server = serve_directory(self.out_dir)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    def mount_options(self, view):
        return {'view': view, 'up': [0, 0, 1], 'fov': 35,
                'driverControls': 'none', 'partControls': 'none',
                'animation': 'external'}

    def shots(self, requests):
        """Photograph the canvas once per `(source, view, after)` request,
        in one browser."""
        images = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof SolidNodeWidget !== "undefined"')
                path = os.path.join(self.tempdir.name, 'shot.png')
                for source, view, after in requests:
                    page.evaluate(
                        """async ([source, options, after]) => {
                          const host = document.getElementById('host');
                          host.innerHTML = '';
                          if (window.viewer) { window.viewer.dispose(); }
                          window.viewer = await SolidNodeWidget.mount(
                            host, source, options);
                          if (after) {
                            new Function('viewer', after)(window.viewer);
                          }
                          await new Promise((done) => requestAnimationFrame(
                            () => requestAnimationFrame(done)));
                        }""",
                        [source, self.mount_options(view), after])
                    self.assertEqual(errors, [],
                                     f'uncaught page errors: {errors}')
                    box = page.locator('#host canvas').bounding_box()
                    page.screenshot(path=path, clip=box)
                    images.append(Image.open(path).convert('RGB'))
                    os.remove(path)
            finally:
                browser.close()
        return images

    @staticmethod
    def channels(image):
        red, green, blue = image.split()
        brightest = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        darkest = ImageChops.darker(ImageChops.darker(red, green), blue)
        return brightest, darkest

    def near_white(self, image):
        _, darkest = self.channels(image)
        return darkest.point(
            lambda value: 255 if value >= self.NEAR_WHITE else 0)

    def marking_coloured(self, image):
        """The mask of pixels showing a NEUTRAL colour bright enough to be
        a decal rather than background or shadow."""
        brightest, darkest = self.channels(image)
        spread = ImageChops.difference(brightest, darkest)
        return Image.frombytes('L', image.size, bytes(
            255 if width <= self.NEUTRAL_SPREAD and low >= self.NEUTRAL_FLOOR
            else 0
            for width, low in zip(spread.getdata(), darkest.getdata())))

    @staticmethod
    def changed(first, second, threshold=24):
        bands = ImageChops.difference(first, second).split()
        return ImageChops.lighter(
            ImageChops.lighter(bands[0], bands[1]), bands[2],
        ).point(lambda value: 255 if value > threshold else 0)

    @staticmethod
    def count(mask):
        return sum(1 for value in mask.getdata() if value)

    def centroid(self, mask):
        indices = [index for index, value in enumerate(mask.getdata()) if value]
        self.assertTrue(indices, 'no marking pixels to take a centroid of')
        return (sum(index % mask.width for index in indices) / len(indices),
                sum(index // mask.width for index in indices) / len(indices))

    def test_the_decals_are_drawn_and_the_twin_shows_none(self):
        marked, twin = self.shots([
            ('manifest.json', self.BENCH_VIEW, ''),
            ('unmarked.json', self.BENCH_VIEW, ''),
        ])

        # The two `#FFFFFF` decals, on the probe the part cannot trip.
        self.assertGreater(self.count(self.near_white(marked)), 100,
                           'the white markings were not drawn')
        self.assertEqual(self.count(self.near_white(twin)), 0,
                         'the parts alone showed near-white, which their '
                         'normal material cannot do')
        # And all three, on the probe that sees the silver band too.
        self.assertGreater(self.count(self.marking_coloured(marked)), 2000,
                           'the markings were not drawn')
        self.assertLess(self.count(self.marking_coloured(twin)), 100,
                        'the parts alone showed a marking colour')

    def test_adding_a_decal_changes_only_the_decal(self):
        marked, twin = self.shots([
            ('manifest.json', self.BENCH_VIEW, ''),
            ('unmarked.json', self.BENCH_VIEW, ''),
        ])

        changed = self.changed(marked, twin)
        pixels = marked.width * marked.height
        moved = self.count(changed)
        self.assertGreater(moved, 0, 'the markings changed nothing')
        self.assertLess(moved, 0.03 * pixels,
                        'adding the markings redrew the whole picture')

        # Every changed pixel is a decal pixel, or one the canvas's
        # antialiasing blended along a decal edge -- half decal and half
        # part, which is neither a marking colour nor unchanged, and is
        # still the decal.
        decal = self.marking_coloured(marked).filter(ImageFilter.MaxFilter(5))
        stray = sum(1 for was_changed, is_decal
                    in zip(changed.getdata(), decal.getdata())
                    if was_changed and not is_decal)
        self.assertLess(stray, 0.01 * moved,
                        f'{stray} of {moved} changed pixels were away from '
                        'any marking')

    def test_a_decal_turns_with_the_part_it_is_on(self):
        # The plate is hidden so the marking pixels are the DIAL's digits
        # alone: the plate's own decals never move.
        hide = "viewer.setVisible(['plate'], false);"
        at_zero, turned, twin = self.shots([
            ('manifest.json', self.DIAL_VIEW, hide),
            ('manifest.json', self.DIAL_VIEW,
             hide + "viewer.setDriver('angle', 180);"),
            ('unmarked.json', self.DIAL_VIEW, hide),
        ])

        first = self.marking_coloured(at_zero)
        second = self.marking_coloured(turned)
        self.assertLess(self.count(self.marking_coloured(twin)), 100,
                        'the bare dial showed a marking colour')
        self.assertGreater(self.count(first), 500,
                           'the dial showed no digits at angle 0')
        self.assertGreater(self.count(second), 500,
                           'the dial showed no digits at angle 180')

        # The whole claim of "the producer publishes no placement": the
        # part's own operations carried the decal, and the viewer
        # computed nothing.
        before = self.centroid(first)
        after = self.centroid(second)
        travelled = ((after[0] - before[0]) ** 2
                     + (after[1] - before[1]) ** 2) ** 0.5
        self.assertGreater(travelled, 50,
                           f'the digits did not turn with the dial: {before} '
                           f'-> {after}')
