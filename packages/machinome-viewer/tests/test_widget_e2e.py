# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""End-to-end tests for the export widget: serve the fixture export over
HTTP, render it in headless chromium and assert on the pixels -- models
load with their colours, and the ?t= URL parameter poses the $t animation.

The mount-interface tests drive a real page with playwright instead,
because a screenshot cannot click a control or read an attribute.
"""

import io
import json
import math
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import run
from unittest import TestCase

from machinome_viewer.bundle import api_version, bundle_path

from .support import (
    CALCULATOR, CHROME, HAS_PIL, HAS_PLAYWRIGHT, PASCALINE, REGULATOR,
    export_calculator, export_marked,
    export_touched, export_with_widget, needs_bundle, needs_chrome, needs_pil,
    needs_playwright, serve_directory, strip_markings,
)

if HAS_PIL:
    from PIL import Image, ImageChops, ImageFilter
if HAS_PLAYWRIGHT:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
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


SMALL_HOST_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      html, body { margin: 0; }
      #host { width: 200px; height: 150px; position: relative; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="machinome-viewer.js"></script>
  </body>
</html>
"""

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
    <script src="machinome-viewer.js"></script>
  </body>
</html>
"""


# How a film host mounts (OpenSpec `track-a-part-on-screen`): on demand,
# posed from outside, with no chrome of the viewer's own.
FILM_MOUNT = ("{ renderMode: 'on-demand', animation: 'external', autoplay: false, "
              "driverControls: 'none', partControls: 'none' }")
# A view of the spinner from above and to the side: the hub's top face
# and all three blades in frame.
FILM_VIEW = "{ camera: [0, -70, 90], target: [0, 0, 2] }"


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
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                result = page.evaluate(script)
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
                return result
            finally:
                browser.close()

    def test_dispose_leaves_the_container_empty(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
          const mounted = host.children.length;
          viewer.dispose();
          return { mounted, after: host.children.length };
        }""")
        self.assertGreater(result['mounted'], 0, 'nothing was mounted')
        self.assertEqual(result['after'], 0, 'dispose() left elements in the container')

    def test_the_bundle_and_mount_handle_report_one_api_version(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
          return { bundle: MachinomeViewer.apiVersion, handle: viewer.apiVersion,
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
        # OpenSpec `play-the-instruction`: PLAYING a clocked machine's
        # declared instruction -- one request solved before the first
        # frame and its transition drawn over the declared duration,
        # where a build at 18 lists the same button and refuses it -- is
        # the one after that, and this moves to 19; the document list
        # does NOT move with it either. OpenSpec `track-a-part-on-screen`
        # declares 28 once for three film-annotation capabilities -- part
        # and point tracking, highlighting, and a per-view up and field of
        # view -- with the document list unchanged. OpenSpec
        # `on-demand-clocked` declares 29: an on-demand mount of a clocked
        # machine, with the document list unchanged again.
        self.assertEqual(result['bundle'], 29)
        # And a document carrying no program has no run and no machine,
        # which is what a host asking one question is answered with.
        self.assertIsNone(result['run'])
        self.assertIsNone(result['machine'])

    def test_the_mount_handle_exposes_and_controls_the_assembly(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(
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
        # page, as `machinome develop`'s targeted update does.
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                setup = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
          const nav = MachinomeViewer.mountNavigator(navHost, viewer);
          const rows = [...navHost.querySelectorAll('[role="treeitem"]')];
          const info = rows.map((row) => ({
            role: row.getAttribute('role'),
            label: row.querySelector('.machinome-nav-name')?.textContent,
          }));
          nav.dispose();
          return { count: rows.length, info };
        }""")
        self.assertEqual(result['count'], 5, 'root + four children were not all drawn')
        self.assertEqual([item['role'] for item in result['info']], ['treeitem'] * 5)
        self.assertEqual(result['info'][0]['label'], 'Spinner')

    def test_expanding_a_scrolled_tree_keeps_the_clicked_row_in_place(self):
        result = self.in_page("""async () => {
          document.getElementById('host').style.display = 'none';
          const host = document.getElementById('navHost');
          host.style.cssText = 'width:260px;height:240px;overflow:auto';
          const assembly = {
            name: 'Root', path: [], color: null, model: false,
            children: Array.from({length: 24}, (_, i) => ({
              name: `Branch ${i}`, path: [`Branch ${i}`], color: null, model: false,
              children: Array.from({length: 8}, (_, j) => ({
                name: `Part ${i}.${j}`, path: [`Branch ${i}`, `Part ${i}.${j}`],
                color: null, model: true, children: [],
              })),
            })),
          };
          let listener;
          const hidden = new Set();
          const navigation = () => ({root: null, hidden: [...hidden].map(key => JSON.parse(key))});
          const nav = MachinomeViewer.mountNavigator(host, {
            assembly: () => assembly,
            navigation,
            onAssemblyChange: callback => { listener = callback; return () => {}; },
            setVisible: (path, visible) => {
              if (visible) hidden.delete(JSON.stringify(path));
              else hidden.add(JSON.stringify(path));
              listener({assembly, navigation: navigation()});
            },
          });
          const row = (name) => [...host.querySelectorAll('.machinome-nav-row')]
            .find(el => el.querySelector('.machinome-nav-name').textContent === name);
          const click = (name) => {
            const button = row(name).querySelector('.machinome-nav-twisty');
            button.focus();
            button.click();
          };
          const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
          for (const i of [12, 13, 14]) click(`Branch ${i}`);
          host.scrollTop = row('Branch 10').offsetTop - 90;
          await frame();
          const position = () => ({
            scroll: host.scrollTop,
            top: row('Branch 10').getBoundingClientRect().top,
            page: window.scrollY,
          });
          const before = position();
          click('Branch 10');
          await frame();
          const expanded = position();
          const active = document.activeElement.querySelector('.machinome-nav-name')?.textContent;
          const childVisible = row('Part 10.0').getBoundingClientRect().top < host.clientHeight;
          click('Branch 10');
          await frame();
          const collapsed = position();
          const visibility = [];
          for (let i = 0; i < 2; i++) {
            const checkbox = row('Branch 11').querySelector('.machinome-nav-visibility');
            checkbox.focus();
            checkbox.click();
            await frame();
            visibility.push({...position(), checked:
              row('Branch 11').querySelector('.machinome-nav-visibility').checked});
          }
          // Keyboard traversal must still reveal a row reached beyond the viewport.
          row('Branch 10').focus();
          for (let i = 0; i < 15; i++) document.activeElement.dispatchEvent(
            new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));
          await frame();
          const rect = document.activeElement.getBoundingClientRect();
          const viewport = host.getBoundingClientRect();
          const keyboardVisible = rect.top >= viewport.top && rect.bottom <= viewport.bottom;
          nav.dispose();
          return {before, expanded, collapsed, visibility, active, childVisible, keyboardVisible};
        }""")
        self.assertGreater(result['before']['scroll'], 0)
        self.assertEqual(result['expanded'], result['before'])
        self.assertEqual(result['collapsed'], result['before'])
        for state, checked in zip(result['visibility'], [False, True]):
            self.assertEqual(state, {**result['before'], 'checked': checked})
        self.assertEqual(result['active'], 'Branch 10')
        self.assertTrue(result['childVisible'])
        self.assertTrue(result['keyboardVisible'])

    def test_the_navigator_keyboard_drives_the_viewer(self):
        result = self.in_page("""async () => {
          const host = document.getElementById('host');
          const navHost = document.getElementById('navHost');
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
          const nav = MachinomeViewer.mountNavigator(navHost, viewer);
          const rows = () => [...navHost.querySelectorAll('.machinome-nav-row')];
          const press = (key) => document.activeElement.dispatchEvent(
            new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true }));

          rows().find((row) => row.tabIndex === 0).focus();
          press('ArrowDown');
          const firstChildLabel = document.activeElement.querySelector('.machinome-nav-name').textContent;
          press('Enter');
          const rootAfterEnter = viewer.navigation().root;
          press(' ');
          const hiddenAfterSpace = viewer.navigation().hidden;
          press('ArrowLeft');
          const labelAfterLeft = document.activeElement.querySelector('.machinome-nav-name').textContent;

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
          const viewer = await MachinomeViewer.mount(
            host, 'nested-driven.json', { autoplay: false });
          const nav = MachinomeViewer.mountNavigator(navHost, viewer);

          const descend = host.querySelector('.driver-descend');
          descend?.click();

          const hubRow = [...navHost.querySelectorAll('.machinome-nav-row')]
            .find((row) => row.querySelector('.machinome-nav-name')?.textContent === 'Hub');
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
        # land BETWEEN two page evaluations, as `machinome develop`'s
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
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                setup = page.evaluate("""async () => {
                  const host = document.getElementById('host');
                  const navHost = document.getElementById('navHost');
                  const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
                  const nav = MachinomeViewer.mountNavigator(navHost, viewer);
                  window.__viewer = viewer;
                  window.__nav = nav;
                  const names = [...navHost.querySelectorAll('.machinome-nav-name')]
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
                  const rows = [...navHost.querySelectorAll('.machinome-nav-row')];
                  return {
                    names: rows.map((row) => row.querySelector('.machinome-nav-name').textContent),
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
          const navA = MachinomeViewer.mountNavigator(navHost, viewer);
          const navB = MachinomeViewer.mountNavigator(navHost2, viewer);

          const firstChip = (root) => root.querySelectorAll('.machinome-nav-visibility')[1];
          firstChip(navHost).click();
          const afterHide = {
            a: firstChip(navHost).checked,
            b: firstChip(navHost2).checked,
            styleCount: document.querySelectorAll('#machinome-navigator-style').length,
          };

          navA.dispose();
          const navHostEmptyAfterDispose = navHost.children.length === 0;

          const secondChip = (root) => root.querySelectorAll('.machinome-nav-visibility')[2];
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
          const first = await MachinomeViewer.mount(host, 'manifest.json', {});
          const moved = {
            camera: first.view().camera.clone().multiplyScalar(2),
            target: first.view().target.clone(),
          };
          first.dispose();
          const second = await MachinomeViewer.mount(host, 'manifest.json', { view: moved });
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          const viewer = await MachinomeViewer.mount(host, 'manifest.json', {});
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
          await MachinomeViewer.mount(host, 'manifest.json', {
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
          const viewer = await MachinomeViewer.mount(host, 'driven.json',
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
          await MachinomeViewer.mount(host, 'manifest.json', { animation: 'toggle' });
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

    # -- Where a part stands on screen (OpenSpec `track-a-part-on-screen`)
    #
    # A film host mounts on demand, poses with `setTime`/`setView` and asks
    # where a part stands for the frame it last set. The spinner declares
    # no controls, which is exactly the case `controls()` cannot answer.

    @contextmanager
    def harness(self):
        """The harness page, open, with page errors collected and checked."""
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                yield page
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
            finally:
                browser.close()

    def shot(self, page):
        return Image.open(io.BytesIO(page.screenshot())).convert('RGB')

    @needs_pil
    def test_a_part_is_tracked_on_screen_without_declared_controls(self):
        with self.harness() as page:
            first = page.evaluate("""async () => {
              const host = document.getElementById('host');
              window.viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
              viewer.setTime(0);
              viewer.setView(FILM_VIEW);
              const canvas = host.querySelector('canvas').getBoundingClientRect();
              return { controls: viewer.controls().length,
                       hub: viewer.partOnScreen(['Hub']),
                       blade: viewer.partOnScreen(['b0']),
                       canvas: { left: canvas.left, top: canvas.top,
                                 right: canvas.right, bottom: canvas.bottom } };
            }""".replace('FILM_VIEW', FILM_VIEW).replace('FILM', FILM_MOUNT))
            image = self.shot(page)
            later = page.evaluate("""() => {
              viewer.setTime(0.25);
              return viewer.partOnScreen(['b0']);
            }""")
        self.assertEqual(first['controls'], 0, 'the spinner declares no controls')
        hub, canvas = first['hub'], first['canvas']
        self.assertIsNotNone(hub, 'the hub is in view and was not tracked')
        rect, point = hub['rect'], hub['point']
        self.assertGreater(rect['width'], 10)
        self.assertGreater(rect['height'], 10)
        self.assertGreaterEqual(rect['x'], canvas['left'])
        self.assertGreaterEqual(rect['y'], canvas['top'])
        self.assertLessEqual(rect['x'] + rect['width'], canvas['right'])
        self.assertLessEqual(rect['y'] + rect['height'], canvas['bottom'])
        self.assertIsNotNone(point, 'no visible point was found on the hub')
        self.assertTrue(rect['x'] <= point['x'] <= rect['x'] + rect['width'])
        self.assertTrue(rect['y'] <= point['y'] <= rect['y'] + rect['height'])
        # The pixel at the point is the hub's red, not a blade's blue and
        # not the white page behind a transparent canvas.
        r, g, b = image.getpixel((round(point['x']), round(point['y'])))
        self.assertTrue(r > 100 and r > 1.4 * g and r > 1.4 * b,
                        f'the pixel at the hub point is {(r, g, b)}, not the hub')
        # A blade turns with time and its rectangle moves with it.
        before, after = first['blade']['rect'], later['rect']
        moved = max(abs(before[key] - after[key])
                    for key in ('x', 'y', 'width', 'height'))
        self.assertGreater(moved, 5, f'the blade rectangle did not move: {before} {after}')

    def test_a_projected_point_lands_in_its_part(self):
        with self.harness() as page:
            result = page.evaluate("""async () => {
              const host = document.getElementById('host');
              const viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
              viewer.setView(FILM_VIEW);
              const view = viewer.view();
              const behind = view.camera.clone().multiplyScalar(2).sub(view.target);
              return { hub: viewer.partOnScreen(['Hub']).rect,
                       axis: viewer.project([0, 0, 3]),
                       behind: viewer.project([behind.x, behind.y, behind.z]),
                       atCamera: viewer.project([view.camera.x, view.camera.y, view.camera.z]),
                       aside: viewer.project([500, 0, 2]) };
            }""".replace('FILM_VIEW', FILM_VIEW).replace('FILM', FILM_MOUNT))
        hub, axis = result['hub'], result['axis']
        # A point on the hub's own axis, from the fixture's geometry: a
        # cylinder of radius 8 standing on z 0 to 6 about the Z axis.
        self.assertTrue(hub['x'] <= axis['x'] <= hub['x'] + hub['width'], (hub, axis))
        self.assertTrue(hub['y'] <= axis['y'] <= hub['y'] + hub['height'], (hub, axis))
        self.assertIsNone(result['behind'], 'a point behind the camera was mirrored')
        self.assertIsNone(result['atCamera'])
        # In front of the camera and off the canvas: answered, outside it.
        self.assertIsNotNone(result['aside'])
        self.assertGreater(result['aside']['x'], 800)

    def test_part_tracking_answers_nothing_or_refuses(self):
        with self.harness() as page:
            result = page.evaluate("""async () => {
              const host = document.getElementById('host');
              const viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
              viewer.setView(FILM_VIEW);
              const blades = ['b0', 'b1', 'b2'].map(name => viewer.partOnScreen([name]).rect);
              const whole = viewer.partOnScreen([]).rect;
              viewer.setVisible(['b1'], false);
              const hidden = viewer.partOnScreen(['b1']);
              const refusal = (action) => {
                try { action(); return null; } catch (error) { return String(error.message); }
              };
              const refusals = {
                unknown: refusal(() => viewer.partOnScreen(['Nope'])),
                notPath: refusal(() => viewer.partOnScreen('Hub')),
                nonFinite: refusal(() => viewer.project([0, NaN, 0])),
                short: refusal(() => viewer.project([0, 0])),
              };
              viewer.dispose();
              refusals.disposedPart = refusal(() => viewer.partOnScreen(['Hub']));
              refusals.disposedProject = refusal(() => viewer.project([0, 0, 0]));
              return { blades, whole, hidden, refusals };
            }""".replace('FILM_VIEW', FILM_VIEW).replace('FILM', FILM_MOUNT))
        self.assertIsNone(result['hidden'], 'a hidden part was reported on screen')
        whole = result['whole']
        for blade in result['blades']:
            self.assertLessEqual(whole['x'], blade['x'] + 1e-6)
            self.assertLessEqual(whole['y'], blade['y'] + 1e-6)
            self.assertGreaterEqual(whole['x'] + whole['width'],
                                    blade['x'] + blade['width'] - 1e-6)
            self.assertGreaterEqual(whole['y'] + whole['height'],
                                    blade['y'] + blade['height'] - 1e-6)
        refusals = result['refusals']
        self.assertIn('Unknown assembly path: Nope', refusals['unknown'])
        self.assertIn('partOnScreen', refusals['notPath'])
        self.assertEqual(refusals['nonFinite'],
                         'project needs three finite world coordinates')
        self.assertEqual(refusals['short'],
                         'project needs three finite world coordinates')
        self.assertEqual(refusals['disposedPart'],
                         'partOnScreen cannot use a disposed viewer')
        self.assertEqual(refusals['disposedProject'],
                         'project cannot use a disposed viewer')

    def test_reading_positions_draws_no_frame(self):
        with self.harness() as page:
            result = page.evaluate("""async () => {
              const host = document.getElementById('host');
              const viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
              viewer.setView(FILM_VIEW);
              const gl = host.querySelector('canvas').getContext('webgl2')
                || host.querySelector('canvas').getContext('webgl');
              let draws = 0;
              for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced',
                                  'drawElementsInstanced', 'drawRangeElements']) {
                if (typeof gl[name] !== 'function') continue;
                const original = gl[name].bind(gl);
                gl[name] = (...args) => { draws += 1; return original(...args); };
              }
              let notified = 0;
              viewer.onAssemblyChange(() => { notified += 1; });
              // The wrap sees a frame: setTime draws one.
              viewer.setTime(0.1);
              const bySetTime = draws;
              draws = 0;
              const view = viewer.view();
              let started = performance.now();
              for (let index = 0; index < 50; index += 1) viewer.partOnScreen(['Hub']);
              const hubMs = (performance.now() - started) / 50;
              started = performance.now();
              for (let index = 0; index < 50; index += 1) viewer.partOnScreen([]);
              const wholeMs = (performance.now() - started) / 50;
              started = performance.now();
              for (let index = 0; index < 50; index += 1) viewer.project([0, 0, 3]);
              const projectMs = (performance.now() - started) / 50;
              const after = viewer.view();
              return { bySetTime, reads: draws, notified, hubMs, wholeMs, projectMs,
                       unmoved: view.camera.equals(after.camera) && view.target.equals(after.target) };
            }""".replace('FILM_VIEW', FILM_VIEW).replace('FILM', FILM_MOUNT))
        self.assertGreater(result['bySetTime'], 0, 'the draw-call probe saw nothing')
        self.assertEqual(result['reads'], 0, 'reading positions drew a frame')
        self.assertEqual(result['notified'], 0)
        self.assertTrue(result['unmoved'])
        print(f"\npartOnScreen(['Hub']) {result['hubMs']:.3f} ms, partOnScreen([]) "
              f"{result['wholeMs']:.3f} ms, project {result['projectMs']:.4f} ms per call")

    def test_a_declared_control_and_its_part_agree(self):
        export_touched(self.out_dir / 'touched')
        with self.harness() as page:
            result = page.evaluate("""async () => {
              const host = document.getElementById('host');
              const viewer = await MachinomeViewer.mount(host, 'touched/manifest.json',
                                                         { autoplay: false });
              // After a drawn frame: `controls()` reads the camera's
              // matrices as the last render left them (evidence.md,
              // "Out of scope"), while `partOnScreen` updates them itself.
              await new Promise(done => requestAnimationFrame(
                () => requestAnimationFrame(done)));
              return viewer.controls().map(control => ({
                name: control.name, rect: control.rect, point: control.point,
                part: viewer.partOnScreen(control.part),
              }));
            }""")
        self.assertGreater(len(result), 0)
        seen = 0
        for control in result:
            if control['rect'] is None:
                self.assertIsNone(control['part'], control['name'])
                continue
            seen += 1
            self.assertEqual(control['part']['rect'], control['rect'], control['name'])
            self.assertEqual(control['part']['point'], control['point'], control['name'])
        self.assertGreater(seen, 0, 'no declared control was on screen')

    # -- A highlight (OpenSpec `highlight-a-part`) ------------------------

    def patch_mean(self, image, point, radius=2):
        """The mean colour of a small square around a point."""
        x, y = round(point['x']), round(point['y'])
        pixels = [image.getpixel((i, j))
                  for i in range(x - radius, x + radius + 1)
                  for j in range(y - radius, y + radius + 1)]
        return tuple(sum(channel) / len(pixels) for channel in zip(*pixels))

    def mount_film(self, page, view=FILM_VIEW, time=0):
        return page.evaluate("""async () => {
          const host = document.getElementById('host');
          window.viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
          viewer.setTime(TIME);
          viewer.setView(VIEW);
          return { hub: viewer.partOnScreen(['Hub']), b1: viewer.partOnScreen(['b1']) };
        }""".replace('VIEW', view).replace('TIME', str(time)).replace('FILM', FILM_MOUNT))

    @needs_pil
    def test_a_highlighted_part_is_visibly_lifted(self):
        with self.harness() as page:
            where = self.mount_film(page)
            plain = self.shot(page)
            page.evaluate("() => { window.restore = viewer.highlight([['Hub']], { color: '#00ff00' }); }")
            lifted = self.shot(page)
            page.evaluate('() => { window.restore(); window.restore(); }')
            restored = self.shot(page)
        hub, blade = where['hub']['point'], where['b1']['point']
        before, after = self.patch_mean(plain, hub), self.patch_mean(lifted, hub)
        print(f'\nhub under #00ff00: {before} -> {after}')
        self.assertGreater(after[1] - before[1], 60, 'the hub did not move toward green')
        self.assertEqual(self.patch_mean(plain, blade), self.patch_mean(lifted, blade),
                         'a blade changed although the others were kept')
        self.assertIsNone(ImageChops.difference(plain, restored).getbbox(),
                          'restoring did not give back the frame before the highlight')

    @needs_pil
    def test_ghosted_others_are_translucent(self):
        # b0 at t = 0.75 points straight at a camera on -Y: its end face
        # covers the middle of the hub's rectangle.
        view = '{ camera: [2, -80, 2], target: [2, 0, 2] }'
        with self.harness() as page:
            where = self.mount_film(page, view=view, time=0.75)
            plain = self.shot(page)
            rect = where['hub']['rect']
            centre = {'x': rect['x'] + rect['width'] / 2, 'y': rect['y'] + rect['height'] / 2}
            ghosted = page.evaluate("""() => {
              window.restore = viewer.highlight([['Hub']], { others: 'ghost' });
              return viewer.partOnScreen(['Hub']);
            }""")
            shot = self.shot(page)
            after = page.evaluate("() => { window.restore(); return viewer.partOnScreen(['Hub']); }")
        self.assertNotEqual(where['hub']['point'], centre,
                            'the blade does not cover the centre of the hub in this view')
        r, g, b = self.patch_mean(plain, centre)
        self.assertGreater(b, r, f'the centre is not the blade before ghosting: {(r, g, b)}')
        r, g, b = self.patch_mean(shot, centre)
        print(f'\nhub centre through a ghosted blade: {(r, g, b)}')
        self.assertGreater(r, b + 60, f'the hub is not seen through the ghost: {(r, g, b)}')
        self.assertEqual(ghosted['point'], centre, 'the point search did not see through the ghost')
        self.assertEqual(after['point'], where['hub']['point'])
        # A blade elsewhere moves toward the white page behind the canvas.
        blade = where['b1']['point']
        before, ghost = sum(self.patch_mean(plain, blade)), sum(self.patch_mean(shot, blade))
        print(f'blade b1 brightness {before:.0f} -> {ghost:.0f}')
        self.assertGreater(ghost - before, 150, 'a ghosted blade did not turn translucent')

    @needs_pil
    def test_dimmed_others_are_darker(self):
        with self.harness() as page:
            where = self.mount_film(page)
            plain = self.shot(page)
            page.evaluate("() => { window.restore = viewer.highlight([['Hub']], { others: 'dim' }); }")
            dimmed = self.shot(page)
        blade, hub = where['b1']['point'], where['hub']['point']
        before, after = sum(self.patch_mean(plain, blade)), sum(self.patch_mean(dimmed, blade))
        print(f'\nblade b1 brightness {before:.0f} -> {after:.0f} dimmed')
        self.assertLess(after, before * 0.8, 'the others were not dimmed')
        self.assertGreaterEqual(sum(self.patch_mean(dimmed, hub)),
                                sum(self.patch_mean(plain, hub)), 'the highlighted hub darkened')

    @needs_pil
    def test_highlight_refusals_and_hidden_parts(self):
        with self.harness() as page:
            where = self.mount_film(page)
            plain = self.shot(page)
            refusals = page.evaluate("""() => {
              const refusal = (action) => {
                try { action(); return null; } catch (error) { return String(error.message); }
              };
              return {
                none: refusal(() => viewer.highlight([])),
                unknown: refusal(() => viewer.highlight([['Hub'], ['Nope']])),
                colour: refusal(() => viewer.highlight([['Hub']], { color: 'green' })),
                mode: refusal(() => viewer.highlight([['Hub']], { others: 'hide' })),
              };
            }""")
            unchanged = self.shot(page)
            second = page.evaluate("""() => {
              window.restore = viewer.highlight([['Hub']], { color: '#00ff00' });
              try { viewer.highlight([['b0']]); return null; }
              catch (error) { return String(error.message); }
            }""")
            still = page.evaluate("() => viewer.partOnScreen(['Hub'])")
            highlighted = self.shot(page)
            page.evaluate("""() => {
              window.restore();
              viewer.setVisible(['b1'], false);
              window.restore = viewer.highlight([['b1']], { color: '#00ff00' });
            }""")
            hidden = self.shot(page)
            hiddenPart = page.evaluate("() => viewer.partOnScreen(['b1'])")
            navigation = page.evaluate('() => viewer.navigation()')
            page.evaluate("() => viewer.setVisible(['b1'], true)")
            shown = self.shot(page)
        self.assertEqual(refusals['none'], 'highlight needs at least one assembly path')
        self.assertIn('Unknown assembly path: Nope', refusals['unknown'])
        self.assertIn('green', refusals['colour'])
        self.assertIn('hide', refusals['mode'])
        self.assertIsNone(ImageChops.difference(plain, unchanged).getbbox(),
                          'a refused highlight changed the frame')
        self.assertIn('call the function the previous highlight returned', second)
        self.assertIsNotNone(still)
        green = lambda image: sum(1 for r, g, b in image.getdata() if g > 150 and g > r + 60 and g > b + 60)
        self.assertGreater(green(highlighted), 50, 'the first highlight did not stand after the refusal')
        self.assertIsNone(hiddenPart)
        self.assertEqual(navigation['hidden'], [['b1']])
        self.assertEqual(green(hidden), 0, 'a hidden highlighted blade was drawn')
        blade = where['b1']['point']
        r, g, b = self.patch_mean(shown, blade)
        self.assertGreater(g, b, f'the blade shown again is not highlighted: {(r, g, b)}')

    @needs_pil
    def test_highlight_survives_an_in_place_update(self):
        manifest_path = self.out_dir / 'manifest.json'
        with self.harness() as page:
            where = self.mount_film(page)
            plain = self.shot(page)
            page.evaluate("() => { window.restore = viewer.highlight([['Hub']], { color: '#00ff00' }); }")
            # A republish that replaces the hub's mesh: its mtime moves.
            manifest = json.loads(manifest_path.read_text())
            manifest['root']['children'][0]['mtime'] += 1
            manifest_path.write_text(json.dumps(manifest))
            page.evaluate('() => viewer.manifestChanged()')
            updated = self.shot(page)
            page.evaluate('() => window.restore()')
            restored = self.shot(page)
        hub = where['hub']['point']
        before, after = self.patch_mean(plain, hub), self.patch_mean(updated, hub)
        self.assertGreater(after[1] - before[1], 60, 'the highlight did not survive the update')
        self.assertIsNone(ImageChops.difference(plain, restored).getbbox(),
                          'restoring after the update did not give back the frame')

    # -- A scripted view's up and field of view (OpenSpec
    # `move-up-and-field-of-view`) -----------------------------------------

    def model_box(self, image):
        """The bounding box of everything that is not the white page."""
        mask = image.convert('L').point(lambda value: 255 if value < 235 else 0)
        return mask.getbbox()

    @needs_pil
    def test_setview_changes_the_field_of_view(self):
        view = "{ camera: [0, -300, 250], target: [0, 0, 2], fov: FOV }"
        with self.harness() as page:
            self.mount_film(page)
            page.evaluate('() => viewer.setView(VIEW)'.replace('VIEW', view.replace('FOV', '60')))
            wide = self.shot(page)
            read = page.evaluate('() => { viewer.setView(VIEW); return viewer.view().fov; }'
                                 .replace('VIEW', view.replace('FOV', '20')))
            narrow = self.shot(page)
        self.assertEqual(read, 20)
        wide_box, narrow_box = self.model_box(wide), self.model_box(narrow)
        expected = math.tan(math.radians(30)) / math.tan(math.radians(10))
        for axis in (0, 1):
            grown = ((narrow_box[axis + 2] - narrow_box[axis])
                     / (wide_box[axis + 2] - wide_box[axis]))
            print(f'\nextent along axis {axis}: {wide_box} -> {narrow_box}, x{grown:.3f} '
                  f'(tan 30 / tan 10 = {expected:.3f})')
            self.assertAlmostEqual(grown, expected, delta=expected * 0.06)

    @needs_pil
    def test_setview_rolls_to_the_supplied_up(self):
        with self.harness() as page:
            self.mount_film(page)
            first = page.evaluate("""() => {
              viewer.setView({ camera: [0, 0, 120], target: [0, 0, 0], up: [1, 0, 0] });
              return viewer.view().up.toArray();
            }""")
            rolled = self.shot(page)
            second = page.evaluate("""() => {
              viewer.setView({ camera: [0, 0, 120], target: [0, 0, 0], up: [0, 2, 0] });
              return viewer.view().up.toArray();
            }""")
            again = self.shot(page)
        self.assertEqual(first, [1, 0, 0])
        self.assertEqual(second, [0, 2, 0], 'the up read back is not the one supplied')

        def mismatch(a, b):
            difference = ImageChops.difference(a, b).convert('L')
            return sum(difference.getdata()) / (a.width * a.height)
        # A quarter turn about the canvas centre; the spinner is threefold,
        # not fourfold, symmetric, so an unrolled frame cannot pass.
        quarter = min(mismatch(again, rolled.rotate(angle, fillcolor=(255, 255, 255)))
                      for angle in (90, -90))
        unrotated = mismatch(again, rolled)
        print(f'\nroll mismatch: quarter turn {quarter:.3f}, unrotated {unrotated:.3f}')
        self.assertLess(quarter * 5, unrotated, 'the frame did not roll a quarter turn')

    @needs_pil
    def test_setview_refusals_leave_the_frame(self):
        with self.harness() as page:
            self.mount_film(page)
            page.evaluate("() => viewer.setView({ camera: [0, -100, 80], target: [0, 0, 2], up: [0, 0, 1], fov: 40 })")
            before = page.evaluate('() => { const v = viewer.view(); return [v.camera.toArray(), v.target.toArray(), v.up.toArray(), v.fov]; }')
            plain = self.shot(page)
            refusals = page.evaluate("""() => {
              const refusal = (view) => {
                try { viewer.setView(view); return null; } catch (error) { return String(error.message); }
              };
              return [
                refusal({ camera: [0, -100, 80], target: [0, 0, 2], up: [0, 100, -78] }),
                refusal({ camera: [0, -100, 80], target: [0, 0, 2], up: [0, 0, 0] }),
                refusal({ camera: [0, -100, 80], target: [0, 0, 2], fov: 0 }),
                refusal({ camera: [0, -100, 80], target: [0, 0, 2], fov: 180 }),
                refusal({ camera: [0, -100, 80], target: [0, 0, 2], up: [0, NaN, 1] }),
              ];
            }""")
            after = page.evaluate('() => { const v = viewer.view(); return [v.camera.toArray(), v.target.toArray(), v.up.toArray(), v.fov]; }')
            unchanged = self.shot(page)
        self.assertEqual(refusals, [
            'setView up must not be parallel to the view direction',
            'setView up must not be zero',
            'setView fov must be a finite number of degrees between 0 and 180, exclusive',
            'setView fov must be a finite number of degrees between 0 and 180, exclusive',
            'setView up must contain three finite coordinates',
        ])
        self.assertEqual(before, after)
        self.assertIsNone(ImageChops.difference(plain, unchanged).getbbox(),
                          'a refused view changed the frame')

    def test_an_adopted_view_survives_refocus_and_reload(self):
        with self.harness() as page:
            result = page.evaluate("""async () => {
              const host = document.getElementById('host');
              const viewer = await MachinomeViewer.mount(host, 'manifest.json', FILM);
              const read = () => { const v = viewer.view(); return [v.up.toArray(), v.fov]; };
              const mounted = read();
              viewer.setView({ camera: [0, -100, 80], target: [0, 0, 2], up: [0, 1, 0], fov: 30 });
              const adopted = read();
              viewer.setView({ camera: [10, -100, 80], target: [0, 0, 2] });
              const kept = read();
              viewer.setRoot(['Hub']);
              const refocused = read();
              await viewer.reload();
              const reloaded = read();
              await viewer.manifestChanged();
              const updated = read();
              viewer.setRoot(null);
              return { mounted, adopted, kept, refocused, reloaded, updated };
            }""".replace('FILM', FILM_MOUNT))
        self.assertEqual(result['mounted'], [[0, 0, 1], 50])
        self.assertEqual(result['adopted'], [[0, 1, 0], 30])
        for moment in ('kept', 'refocused', 'reloaded', 'updated'):
            self.assertEqual(result[moment], [[0, 1, 0], 30], moment)

    def test_orbit_turns_about_the_adopted_up(self):
        with self.harness() as page:
            page.evaluate("""async () => {
              const host = document.getElementById('host');
              window.viewer = await MachinomeViewer.mount(host, 'manifest.json', { autoplay: false });
              viewer.setView({ camera: [0, -60, 40], target: [0, 0, 2], up: [1, 0, 0] });
            }""")
            angle = """() => {
              const v = viewer.view();
              const offset = v.camera.clone().sub(v.target);
              return { angle: offset.angleTo(v.up), camera: v.camera.toArray(),
                       up: v.up.toArray() };
            }"""
            before = page.evaluate(angle)
            page.mouse.move(400, 250)
            page.mouse.down()
            page.mouse.move(520, 250, steps=12)
            page.mouse.up()
            page.evaluate('() => new Promise(done => requestAnimationFrame(done))')
            after = page.evaluate(angle)
        moved = max(abs(a - b) for a, b in zip(before['camera'], after['camera']))
        self.assertGreater(moved, 5, 'the drag did not orbit the camera')
        self.assertAlmostEqual(before['angle'], after['angle'], delta=1e-6)
        self.assertEqual(after['up'], [1, 0, 0])


@needs_bundle
@needs_playwright
class InspectorLayoutE2ETest(TestCase):
    """The standalone export page selects a layout (design D8): the
    shipped `index.html` carries `data-machinome-layout="inspector"`, and a
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
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                yield page, errors
            finally:
                browser.close()

    def test_the_export_page_mounts_the_inspector(self):
        with self.open_page() as (page, errors):
            page.wait_for_selector('.machinome-inspector')
            self.assertEqual(page.locator('.machinome-inspector-toggle').count(), 1)
            # Collapsed by default (design D3): the `hidden` attribute is
            # present on the sidebar.
            self.assertIsNotNone(
                page.locator('.machinome-inspector-sidebar').get_attribute('hidden'))
            self.assertEqual(errors, [])

    def test_the_toggle_opens_the_sidebar_and_the_canvas_narrows(self):
        with self.open_page() as (page, errors):
            page.wait_for_selector('.machinome-inspector-viewer canvas')
            canvas = page.locator('.machinome-inspector-viewer canvas')
            before = canvas.bounding_box()['width']

            page.locator('.machinome-inspector-toggle').click()
            page.wait_for_selector('.machinome-nav-tree [role="treeitem"]')
            self.assertIsNone(
                page.locator('.machinome-inspector-sidebar').get_attribute('hidden'))
            # The viewer resizes through its own ResizeObserver, which
            # fires after layout: wait for the canvas to follow the pane
            # rather than reading its width in the same turn as the click.
            narrowed = ("(before) => document.querySelector('.machinome-inspector-viewer canvas')"
                        ".getBoundingClientRect().width < before")
            page.wait_for_function(narrowed, arg=before, timeout=5_000)
            opened = canvas.bounding_box()['width']
            self.assertLess(opened, before, 'the canvas did not narrow when the sidebar opened')

            page.locator('.machinome-inspector-toggle').click()
            self.assertIsNotNone(
                page.locator('.machinome-inspector-sidebar').get_attribute('hidden'))
            restored = ("(before) => Math.abs(document.querySelector('.machinome-inspector-viewer canvas')"
                        ".getBoundingClientRect().width - before) <= 2")
            page.wait_for_function(restored, arg=before, timeout=5_000)
            closed = canvas.bounding_box()['width']
            self.assertAlmostEqual(closed, before, delta=2,
                                   msg='the canvas did not return to its width when closed')
            self.assertEqual(errors, [])

    def test_the_query_string_opens_the_sidebar(self):
        with self.open_page(f'{self.base_url}?sidebar=open') as (page, errors):
            page.wait_for_selector('.machinome-inspector-sidebar')
            self.assertIsNone(
                page.locator('.machinome-inspector-sidebar').get_attribute('hidden'),
                'the sidebar attribute did not override the collapsed default')
            self.assertEqual(errors, [])

    def test_a_page_without_a_layout_attribute_mounts_the_plain_viewer(self):
        # A hand-written page carrying only data-machinome-widget -- the
        # compatibility promise every already-published export keeps.
        (self.out_dir / 'plain.html').write_text(
            '<!doctype html><html><body>'
            '<div id="machinome-viewer" data-machinome-widget="manifest.json"></div>'
            '<script src="machinome-viewer.js"></script></body></html>'
        )
        with self.open_page(f'{self.dir_url}/plain.html') as (page, errors):
            page.wait_for_selector('#machinome-viewer canvas')
            self.assertEqual(page.locator('.machinome-inspector').count(), 0)
            self.assertEqual(errors, [])

    def test_an_unknown_layout_is_refused_by_name(self):
        with self.open_page(f'{self.base_url}?layout=bogus') as (page, errors):
            page.wait_for_function(
                "document.getElementById('machinome-viewer').textContent"
                ".includes('unknown layout')")
            text = page.locator('#machinome-viewer').text_content()
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
      /* This bench is drivers-only (no `$t`), so the full-screen control
         is drawn as a permanent corner overlay (OpenSpec `go-fullscreen`,
         design D2), squarely inside the clipped canvas shot below. Hidden
         here for the same reason `WidgetE2ETest.screenshot` crops the
         control bar off its own shots: this bench's pixel assertions are
         about the MODEL. The rule is the manual's own example of the
         host's CSS hook (`docs/reference/layouts.rst`), written exactly
         as documented, so this bench also proves the hook works: while
         the button carried an inline `display`, the rule lost to it and
         the unmarked twin photographed the four corners of the button's
         icon as four near-white pixels (CI run 36125018574). */
      .machinome-fullscreen { display: none; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="machinome-viewer.js"></script>
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
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                path = os.path.join(self.tempdir.name, 'shot.png')
                for source, view, after in requests:
                    page.evaluate(
                        """async ([source, options, after]) => {
                          const host = document.getElementById('host');
                          host.innerHTML = '';
                          if (window.viewer) { window.viewer.dispose(); }
                          window.viewer = await MachinomeViewer.mount(
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


@needs_bundle
@needs_playwright
class FullscreenE2ETest(TestCase):
    """The full-screen control (OpenSpec `go-fullscreen`): placement on
    the control surface each export actually draws (design D2), the `f`
    key and Escape (design D4), the plain-mount root (design D1), and an
    iframe's own fullscreen permission (design D5)."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        root = Path(self.tempdir.name) / 'root'
        spinner = export_with_widget(root / 'spinner')
        export_marked(root / 'marked')
        export_touched(root / 'touched')
        export_calculator(root / 'calculator')
        # Beside the bundle and the document each mounts (their own
        # script tags and this test's sourceUrl are all relative).
        (spinner / 'harness.html').write_text(HARNESS_PAGE)
        (spinner / 'small.html').write_text(SMALL_HOST_PAGE)
        server = serve_directory(root)
        self.base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)

        # A genuinely CROSS-ORIGIN embed. Confirmed empirically against
        # this Chromium (evidence.md): a SAME-origin iframe inherits the
        # Fullscreen API's permission whether or not it carries
        # `allowfullscreen` at all -- the default permissions-policy
        # allowlist is `'self'` -- so exercising what the attribute does
        # needs a different loopback PORT, which is a different origin.
        outer = Path(self.tempdir.name) / 'outer'
        outer.mkdir()
        (outer / 'closed.html').write_text(
            '<!doctype html><html><body>'
            f'<iframe src="{self.base}/spinner/index.html" '
            'style="width:800px;height:600px;border:0"></iframe>'
            '</body></html>')
        (outer / 'open.html').write_text(
            '<!doctype html><html><body>'
            f'<iframe src="{self.base}/spinner/index.html" allowfullscreen '
            'style="width:800px;height:600px;border:0"></iframe>'
            '</body></html>')
        outer_server = serve_directory(outer)
        self.outer_base = outer_server.__enter__()
        self.addCleanup(outer_server.__exit__, None, None, None)

    @contextmanager
    def open_page(self, url, viewport=None):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport=viewport or {'width': 800, 'height': 600})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url)
                yield page, errors
            finally:
                browser.close()

    # -- placement: the bar a model has, or the corner -----------------

    def test_the_button_is_last_on_the_animation_bar(self):
        with self.open_page(f'{self.base}/spinner/index.html') as (page, errors):
            page.wait_for_selector('.machinome-fullscreen')
            self.assertEqual(page.locator('.machinome-fullscreen').count(), 1)
            last = page.eval_on_selector(
                '.animation-controls', 'el => el.lastElementChild.className')
            self.assertEqual(last, 'machinome-fullscreen')
            self.assertEqual(errors, [])

    def test_the_button_is_last_on_the_run_transport(self):
        with self.open_page(f'{self.base}/touched/index.html') as (page, errors):
            page.wait_for_selector('.machinome-fullscreen')
            self.assertEqual(page.locator('.machinome-fullscreen').count(), 1)
            last = page.eval_on_selector(
                '.run-transport', 'el => el.lastElementChild.className')
            self.assertEqual(last, 'machinome-fullscreen')
            self.assertEqual(errors, [])

    def test_the_button_is_in_the_corner_on_a_drivers_only_model(self):
        with self.open_page(f'{self.base}/marked/index.html') as (page, errors):
            page.wait_for_selector('.machinome-fullscreen')
            self.assertEqual(page.locator('.animation-controls').count(), 0)
            self.assertEqual(page.locator('.run-transport').count(), 0)
            self.assertEqual(
                page.locator('.machinome-inspector-viewer > .machinome-fullscreen').count(), 1)
            self.assertEqual(errors, [])

    def test_the_button_is_in_the_corner_on_a_clocked_machine(self):
        with self.open_page(f'{self.base}/calculator/index.html') as (page, errors):
            page.wait_for_selector('.machinome-fullscreen')
            self.assertEqual(page.locator('.animation-controls').count(), 0)
            self.assertEqual(page.locator('.run-transport').count(), 0)
            self.assertEqual(
                page.locator('.machinome-inspector-viewer > .machinome-fullscreen').count(), 1)
            self.assertEqual(errors, [])

    # -- entering and leaving -------------------------------------------

    def test_f_enters_full_screen_on_the_inspector_root_and_the_canvas_fills_the_screen(self):
        with self.open_page(f'{self.base}/spinner/index.html') as (page, errors):
            page.wait_for_selector('canvas')
            before_width = page.locator('canvas').bounding_box()['width']

            page.locator('canvas').click()
            page.keyboard.press('f')
            page.wait_for_function('document.fullscreenElement !== null', timeout=5_000)
            self.assertEqual(
                page.evaluate('document.fullscreenElement.className'),
                'machinome-inspector')
            # The ROOT is the full-screen element and fills the viewport
            # (design D1). The standalone export page already sizes its
            # host to the whole viewport outside full screen too, so no
            # GROWTH is observable here; that proof is
            # `test_a_plain_mount_goes_full_screen_and_the_canvas_grows_to_the_viewport`,
            # against a host that starts smaller than the viewport. The
            # CANVAS shares its pane with the always-DOM rail
            # (inspector.ts design D5), so it fills the viewport's HEIGHT
            # rather than matching its width to the pixel.
            fits = page.evaluate("""() => {
                const root = document.fullscreenElement.getBoundingClientRect();
                const canvas = document.querySelector('canvas').getBoundingClientRect();
                return Math.abs(root.width - window.innerWidth) < 2
                    && Math.abs(root.height - window.innerHeight) < 2
                    && Math.abs(canvas.height - window.innerHeight) < 2;
            }""")
            self.assertTrue(fits, 'the full-screen root did not fill the viewport')
            self.assertAlmostEqual(
                page.locator('canvas').bounding_box()['width'], before_width, delta=2,
                msg='the canvas width unexpectedly changed')
            self.assertEqual(
                page.locator('.machinome-fullscreen').get_attribute('aria-label'),
                'Exit full screen')
            self.assertEqual(errors, [])

    def test_exiting_restores_the_canvas_size_and_the_label(self):
        with self.open_page(f'{self.base}/spinner/index.html') as (page, errors):
            page.wait_for_selector('canvas')
            before = page.locator('canvas').bounding_box()

            page.locator('canvas').click()
            page.keyboard.press('f')
            page.wait_for_function('document.fullscreenElement !== null', timeout=5_000)

            # Whether headless Chromium honours a synthetic Escape as a
            # native full-screen exit is not established up front
            # (design, Risks; recorded in evidence.md). Both branches
            # below prove the same thing the spec asks for: the viewer
            # never intercepts Escape -- it installs no listener for it
            # at all -- and the button follows whatever exit path
            # actually happened.
            page.keyboard.press('Escape')
            try:
                page.wait_for_function('document.fullscreenElement === null', timeout=1_500)
            except PlaywrightTimeoutError:
                page.evaluate('document.exitFullscreen()')
                page.wait_for_function('document.fullscreenElement === null', timeout=5_000)

            restored = ("(before) => {"
                        "const rect = document.querySelector('canvas').getBoundingClientRect();"
                        "return Math.abs(rect.width - before.width) <= 2"
                        "    && Math.abs(rect.height - before.height) <= 2;"
                        "}")
            page.wait_for_function(restored, arg=before, timeout=5_000)
            # `fullscreenElement` clears and the canvas shrinks before the
            # browser dispatches `fullscreenchange`, which is what relabels
            # the button, so the label is awaited rather than read at once
            # (evidence of `highlight-a-part`, "Out of scope": the immediate
            # read raced and lost at the base bundle too).
            page.wait_for_function(
                "document.querySelector('.machinome-fullscreen')"
                ".getAttribute('aria-label') === 'Full screen'", timeout=5_000)
            self.assertEqual(
                page.locator('.machinome-fullscreen').get_attribute('aria-label'),
                'Full screen')
            self.assertEqual(errors, [])

    def test_the_sidebar_toggle_is_reachable_in_full_screen_and_narrows_the_canvas(self):
        with self.open_page(f'{self.base}/spinner/index.html') as (page, errors):
            page.wait_for_selector('canvas')
            page.locator('canvas').click()
            page.keyboard.press('f')
            page.wait_for_function('document.fullscreenElement !== null', timeout=5_000)
            page.wait_for_selector('.machinome-inspector-toggle')

            before = page.locator('canvas').bounding_box()['width']
            page.locator('.machinome-inspector-toggle').click()
            narrowed = ("(before) => document.querySelector('canvas')"
                        ".getBoundingClientRect().width < before")
            page.wait_for_function(narrowed, arg=before, timeout=5_000)
            self.assertEqual(errors, [])

    def test_a_plain_mount_goes_full_screen_and_the_canvas_grows_to_the_viewport(self):
        # A host SMALLER than the viewport (200x150 of 800x600), so
        # entering full screen is an observable GROWTH, unlike the
        # standalone export page above, which already fills the viewport
        # before `f` is ever pressed.
        with self.open_page(f'{self.base}/spinner/small.html') as (page, errors):
            page.wait_for_function('typeof MachinomeViewer !== "undefined"')
            page.evaluate(
                "MachinomeViewer.mount(document.getElementById('host'), "
                "'manifest.json', {})")
            page.wait_for_selector('#host canvas')
            before = page.locator('#host canvas').bounding_box()

            page.locator('#host canvas').click()
            page.keyboard.press('f')
            page.wait_for_function('document.fullscreenElement !== null', timeout=5_000)
            self.assertTrue(page.evaluate(
                "document.fullscreenElement === document.getElementById('host')"))
            grew = page.evaluate("""() => {
                const rect = document.getElementById('host').getBoundingClientRect();
                return Math.abs(rect.width - window.innerWidth) < 2
                    && Math.abs(rect.height - window.innerHeight) < 2;
            }""")
            self.assertTrue(grew, 'the host element did not grow to fill the viewport')
            after = page.locator('#host canvas').bounding_box()
            self.assertGreater(after['width'], before['width'] * 2,
                               'the canvas did not follow the host into full screen')
            self.assertEqual(errors, [])

    # -- the key rule ----------------------------------------------------

    def test_f_in_a_clocked_value_field_does_not_enter_full_screen(self):
        with self.open_page(f'{self.base}/calculator/index.html') as (page, errors):
            page.wait_for_selector('.clocked-value')
            page.locator('.clocked-value').first.click()
            page.keyboard.press('f')
            self.assertIsNone(page.evaluate('document.fullscreenElement'))
            self.assertEqual(errors, [])

    def test_ctrl_f_does_not_enter_full_screen(self):
        with self.open_page(f'{self.base}/spinner/index.html') as (page, errors):
            page.wait_for_selector('canvas')
            page.locator('canvas').click()
            page.keyboard.press('Control+f')
            self.assertIsNone(page.evaluate('document.fullscreenElement'))
            self.assertEqual(errors, [])

    # -- the embedding permission -----------------------------------------

    def test_an_iframe_without_allowfullscreen_hides_the_button_and_ignores_f(self):
        with self.open_page(f'{self.outer_base}/closed.html') as (page, errors):
            page.wait_for_selector('iframe')
            frame = page.frames[1]
            frame.wait_for_selector('canvas')
            self.assertEqual(frame.locator('.machinome-fullscreen').count(), 0)
            frame.locator('canvas').click()
            page.keyboard.press('f')
            self.assertIsNone(frame.evaluate('document.fullscreenElement'))
            self.assertEqual(errors, [])

    def test_an_iframe_with_allowfullscreen_shows_the_button(self):
        with self.open_page(f'{self.outer_base}/open.html') as (page, errors):
            page.wait_for_selector('iframe')
            frame = page.frames[1]
            frame.wait_for_selector('canvas')
            frame.wait_for_selector('.machinome-fullscreen')
            self.assertEqual(frame.locator('.machinome-fullscreen').count(), 1)
            self.assertEqual(errors, [])


# The calculator's bank at the start of a stroke (operand set to 4) and
# the same bank with the crank half a turn and a bit in, the shape of a
# film frame posed mid-stroke: no commit has fired, the crank has moved.
# 190 degrees, not 180, so a dial with an even symmetry cannot hide it.
ON_DEMAND_BANKS = """() => {
  const machine = viewer.machine();
  machine.reset();
  machine.move('operand', { to: 4 });
  const origin = machine.snapshot();
  const mid = { identity: origin.identity,
                bank: { ...origin.bank, crank: origin.bank.crank + 190 } };
  window.origin = origin;
  window.mid = mid;
  return { origin, mid };
}"""


@needs_bundle
@needs_playwright
@needs_pil
class OnDemandClockedTest(TestCase):
    """OpenSpec `on-demand-clocked`: a film host mounts a CLOCKED machine
    on demand, poses each frame by request and captures it, with no
    frame loop running; the two verbs that draw over wall seconds are
    refused by name."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        root = Path(self.tempdir.name) / 'root'
        root.mkdir()
        shutil.copytree(CALCULATOR, root / 'calculator')
        shutil.copytree(REGULATOR, root / 'regulator')
        shutil.copytree(PASCALINE, root / 'pascaline')
        shutil.copy2(bundle_path(), root / 'machinome-viewer.js')
        (root / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(root)
        base = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.harness_url = f'{base}/harness.html'

    @contextmanager
    def harness(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.set_default_timeout(120_000)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(self.harness_url)
                page.wait_for_function('typeof MachinomeViewer !== "undefined"')
                yield page
                self.assertEqual(errors, [], f'uncaught page errors: {errors}')
            finally:
                browser.close()

    def mount(self, page, document, options=FILM_MOUNT):
        """Mount `document` and keep the handle as `window.viewer`; return
        the refusal's message, or None when the mount succeeded."""
        return page.evaluate("""async () => {
          const host = document.getElementById('host');
          try {
            window.viewer = await MachinomeViewer.mount(host, 'DOCUMENT', OPTIONS);
            return null;
          } catch (error) {
            return String(error.message);
          }
        }""".replace('DOCUMENT', document).replace('OPTIONS', options))

    def mount_calculator(self, page):
        refused = self.mount(page, 'calculator/viewer.json')
        self.assertIsNone(refused, 'the on-demand mount refused the clocked machine')

    def shot(self, page):
        return page.locator('#host').screenshot()

    def test_a_clocked_machine_mounts_on_demand_and_poses_by_restore(self):
        with self.harness() as page:
            self.mount_calculator(page)
            banks = page.evaluate(ON_DEMAND_BANKS)
            page.evaluate('() => { viewer.machine().restore(origin); viewer.setView(viewer.view()); }')
            at_origin = self.shot(page)
            # Restore alone: the request draws itself.
            mid_state = page.evaluate('() => { viewer.machine().restore(mid); return viewer.machine().state(); }')
            restored = self.shot(page)
            # Then the explicit render a host already has: the same view.
            page.evaluate('() => viewer.setView(viewer.view())')
            mid_frame = self.shot(page)
            # Away and back: posing the same bank draws the same frame.
            page.evaluate('() => { viewer.machine().restore(origin); viewer.setView(viewer.view()); }')
            back = self.shot(page)
            page.evaluate('() => { viewer.machine().restore(mid); viewer.setView(viewer.view()); }')
            again = self.shot(page)
            loop = page.evaluate('() => viewer.machine().clockPlaying()')
        self.assertEqual(mid_state, banks['mid']['bank'], 'restore did not take the bank given')
        self.assertNotEqual(at_origin, mid_frame, 'the restored crank did not reach the frame')
        self.assertEqual(back, at_origin, 'returning to the origin did not redraw it')
        self.assertEqual(again, mid_frame, 'the same bank drew a different frame')
        self.assertFalse(loop)

        # Restore ALONE already draws the new pose: against the origin it
        # differs as much as the setView frame does, and from the setView
        # frame only where `setView` re-fits the near and far planes to
        # the posed bounds (design D3; evidence.md). A frame that depends
        # on the bank and the view alone is the one after `setView`.
        def changed(a, b):
            difference = ImageChops.difference(
                Image.open(io.BytesIO(a)).convert('L'),
                Image.open(io.BytesIO(b)).convert('L'))
            return difference.width * difference.height - difference.histogram()[0]
        moved, refit = changed(at_origin, restored), changed(restored, mid_frame)
        print(f'\nrestore alone: {moved} pixels from the origin, {refit} from the setView frame')
        self.assertGreater(moved, 0.9 * changed(at_origin, mid_frame))
        self.assertLess(refit * 20, moved, 'restore alone left a stale frame')

    def test_on_demand_requests_answer_as_continuous(self):
        script = """() => {
          const machine = viewer.machine();
          machine.reset();
          const answers = [
            machine.move('operand', { to: 4 }),
            machine.move('crank', { by: 1100 }),
            machine.move('setting', { by: 1 }),
            machine.move('crank', { by: -30 }),
            machine.move('ring', { by: 500 }),
          ];
          return { answers: JSON.parse(JSON.stringify(answers)),
                   bank: machine.state() };
        }"""
        with self.harness() as page:
            self.mount_calculator(page)
            on_demand = page.evaluate(script)
            page.evaluate('() => viewer.dispose()')
            self.assertIsNone(self.mount(page, 'calculator/viewer.json', '{}'))
            continuous = page.evaluate(script)
        self.assertEqual(on_demand, continuous)
        # And the requests did something: the stroke committed.
        self.assertGreater(len(on_demand['answers'][1]['commits']), 0)

    def test_trigger_is_refused_on_demand(self):
        with self.harness() as page:
            self.mount_calculator(page)
            page.evaluate(ON_DEMAND_BANKS)
            page.evaluate('() => { viewer.machine().restore(origin); viewer.setView(viewer.view()); }')
            before_frame = self.shot(page)
            result = page.evaluate("""() => {
              const machine = viewer.machine();
              const before = machine.state();
              let refused = null;
              try { machine.trigger('Stroke'); } catch (error) { refused = String(error.message); }
              return { refused, before, after: machine.state() };
            }""")
            after_frame = self.shot(page)
        self.assertIsNotNone(result['refused'], 'trigger was accepted on demand')
        self.assertIn("machine().trigger('Stroke')", result['refused'])
        self.assertIn("renderMode 'on-demand'", result['refused'])
        self.assertIn('restore', result['refused'])
        self.assertEqual(result['after'], result['before'])
        self.assertEqual(after_frame, before_frame)

    def test_a_clock_does_not_play_on_demand(self):
        with self.harness() as page:
            refused = self.mount(page, 'regulator/viewer.json')
            self.assertIsNone(refused, 'the on-demand mount refused the regulator')
            result = page.evaluate("""() => {
              const machine = viewer.machine();
              const clock = machine.clock();
              let refused = null;
              try { machine.setClockPlaying(true); } catch (error) { refused = String(error.message); }
              const playing = machine.clockPlaying();
              machine.setClockPlaying(false);
              const answered = machine.move(clock, { by: 0.5 });
              return { clock, refused, playing, admitted: answered.admitted,
                       elapsed: machine.state()[clock] };
            }""")
        self.assertIsNotNone(result['refused'], 'the clock was started on demand')
        self.assertIn('setClockPlaying(true)', result['refused'])
        self.assertIn("renderMode 'on-demand'", result['refused'])
        self.assertFalse(result['playing'])
        self.assertEqual(result['admitted'], 0.5)
        self.assertEqual(result['elapsed'], 0.5)

    def test_an_on_demand_clocked_mount_shows_no_control(self):
        with self.harness() as page:
            self.mount_calculator(page)
            found = page.evaluate("""() => {
              const host = document.getElementById('host');
              return {
                canvases: host.querySelectorAll('canvas').length,
                controls: Array.from(host.querySelectorAll(
                  'button, input, select, textarea, .clocked-controls, '
                  + '.machinome-fullscreen, .animation-controls, .run-transport'))
                  .map((element) => element.outerHTML.slice(0, 80)),
                fullscreen: document.querySelectorAll('.machinome-fullscreen').length,
              };
            }""")
        self.assertEqual(found['canvases'], 1)
        self.assertEqual(found['controls'], [])
        self.assertEqual(found['fullscreen'], 0)

    def test_a_program_is_still_refused_on_demand(self):
        with self.harness() as page:
            refused = self.mount(page, 'pascaline/viewer.json')
        self.assertIsNotNone(refused, 'a running program mounted on demand')
        self.assertIn('on-demand rendering cannot run a program', refused)
        self.assertIn("renderMode 'continuous'", refused)
