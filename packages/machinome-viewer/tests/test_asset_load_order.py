# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""A loaded viewer image must not depend on the order its STLs arrive."""

import hashlib
import io
import json
import shutil
import tempfile
import threading
import time
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from machinome_viewer.bundle import bundle_path
from tests.support import QuietHandler, needs_bundle, needs_pil, needs_playwright

try:
    from PIL import Image
except ImportError:  # pragma: no cover - guarded by needs_pil
    Image = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None


def plate_stl(back=-0.02, front=0.02):
    """The same closed solid at two URLs; only its declared colour differs."""
    lo, hi = -1, 1
    faces = [
        ((lo, lo, front), (hi, lo, front), (hi, hi, front)),
        ((lo, lo, front), (hi, hi, front), (lo, hi, front)),
        ((hi, lo, back), (lo, lo, back), (lo, hi, back)),
        ((hi, lo, back), (lo, hi, back), (hi, hi, back)),
        ((lo, lo, back), (lo, lo, front), (lo, hi, front)),
        ((lo, lo, back), (lo, hi, front), (lo, hi, back)),
        ((hi, lo, front), (hi, lo, back), (hi, hi, back)),
        ((hi, lo, front), (hi, hi, back), (hi, hi, front)),
        ((lo, hi, front), (hi, hi, front), (hi, hi, back)),
        ((lo, hi, front), (hi, hi, back), (lo, hi, back)),
        ((lo, lo, back), (hi, lo, back), (hi, lo, front)),
        ((lo, lo, back), (hi, lo, front), (lo, lo, front)),
    ]
    lines = ['solid coincident_plate']
    for face in faces:
        lines.extend(['facet normal 0 0 0', ' outer loop'])
        lines.extend(f'  vertex {x} {y} {z}' for x, y, z in face)
        lines.extend([' endloop', 'endfacet'])
    lines.append('endsolid coincident_plate')
    return ('\n'.join(lines) + '\n').encode()


def document():
    def part(name, colour):
        return {'name': name, 'type': 'LeafNode', 'color': colour,
                'mtime': 0, 'operations': [], 'model': f'{name}.stl',
                'piece': name}

    return {
        'format': 'machinome-export', 'version': 2,
        'animation': {'fps': 30, 'frames': 30},
        'drivers': {}, 'instructions': {},
        'root': {'name': 'Load order plates', 'type': 'AssemblyNode',
                 'color': None, 'mtime': 0, 'operations': [],
                 'children': [part('red', '#ff0000'), part('blue', '#0000ff')]},
        'pieces': [
            {'id': name, 'name': name, 'sources': [],
             'models': [f'{name}.stl'], 'count': 1, 'size': [2, 2, 0.04],
             'volume': 0.16, 'watertight': True}
            for name in ('red', 'blue')
        ],
    }


@needs_bundle
@needs_playwright
@needs_pil
class AssetLoadOrderTest(unittest.TestCase):
    def test_coincident_parts_have_identical_pngs_when_response_order_reverses(self):
        with tempfile.TemporaryDirectory(prefix='viewer-load-order-') as temp:
            stage = Path(temp)
            shutil.copy2(bundle_path(), stage / 'viewer.js')
            (stage / 'manifest.json').write_text(json.dumps(document()))
            stl = plate_stl()
            (stage / 'red.stl').write_bytes(stl)
            (stage / 'blue.stl').write_bytes(stl)
            (stage / 'index.html').write_text(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<style>html,body,#host{margin:0;width:100%;height:100%;'
                'overflow:hidden}canvas{display:block}</style></head><body>'
                '<div id="host"></div><script src="/viewer.js"></script>'
                '</body></html>')

            mode = {'delay': None}
            completions = []
            lock = threading.Lock()

            class DelayedHandler(QuietHandler):
                def do_GET(self):
                    path = urlsplit(self.path).path
                    if path not in ('/red.stl', '/blue.stl'):
                        return super().do_GET()
                    name = path[1:-4]
                    if name == mode['delay']:
                        time.sleep(0.2)
                    super().do_GET()
                    with lock:
                        completions.append(name)

            server = ThreadingHTTPServer(
                ('127.0.0.1', 0), partial(DelayedHandler, directory=str(stage)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_address[1]}/'
                first_frames = []
                orders = []
                centres = []
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(args=[
                        '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                    try:
                        for delayed in ('blue', 'red', 'red', 'blue'):
                            mode['delay'] = delayed
                            with lock:
                                completions.clear()
                            context = browser.new_context(
                                viewport={'width': 640, 'height': 480},
                                device_scale_factor=1)
                            try:
                                page = context.new_page()
                                page.goto(url, wait_until='load')
                                mounted = page.evaluate('''async () => {
                                  if (MachinomeViewer.apiVersion !== 29)
                                    throw Error('Expected Viewer API 29');
                                  window.viewer = await MachinomeViewer.mount(
                                    '#host', '/manifest.json', {
                                      renderMode: 'on-demand', animation: 'external',
                                      autoplay: false, driverControls: 'none',
                                      partControls: 'none', time: 0.25,
                                      up: [0, 1, 0], fov: 50,
                                      view: {camera: [0, 0, 5], target: [0, 0, 0]}
                                    });
                                  window.viewer.setView({camera: [0, 0, 5],
                                    target: [0, 0, 0]});
                                  window.viewer.setTime(0.25);
                                  return window.viewer.apiVersion;
                                }''')
                                self.assertEqual(mounted, 29)
                                with lock:
                                    order = tuple(completions)
                                expected = ('red', 'blue') if delayed == 'blue' else ('blue', 'red')
                                self.assertEqual(order, expected,
                                                 f'delay did not reverse completed STL responses: {order}')
                                orders.append(order)
                                captures = []
                                for _ in range(5):
                                    page.evaluate('window.viewer.setTime(0.25)')
                                    captures.append(page.screenshot())
                                self.assertTrue(all(frame == captures[0] for frame in captures),
                                                'repeated poses within one mount changed pixels')
                                first_frames.append(captures[0])
                                centre = Image.open(io.BytesIO(captures[0])).convert('RGB').getpixel((320, 240))
                                self.assertTrue((centre[0] > 1.5 * max(centre[1], centre[2]))
                                                or (centre[2] > 1.5 * max(centre[0], centre[1])),
                                                f'coincident plates were not visible: {centre}')
                                centres.append(centre)
                            finally:
                                context.close()
                    finally:
                        browser.close()
                self.assertEqual(orders, [
                    ('red', 'blue'), ('blue', 'red'),
                    ('blue', 'red'), ('red', 'blue')])
                digests = [hashlib.sha256(frame).hexdigest() for frame in first_frames]
                self.assertEqual(len(set(first_frames)), 1,
                                 f'identical loaded parts changed PNG bytes with STL completion order: '
                                 f'orders={orders}, hashes={digests}, centres={centres}')
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

    def test_a_physically_nearer_surface_occludes_in_either_response_order(self):
        with tempfile.TemporaryDirectory(prefix='viewer-real-depth-') as temp:
            stage = Path(temp)
            shutil.copy2(bundle_path(), stage / 'viewer.js')
            manifest = document()
            near = manifest['root']['children'][1]
            near.update({'name': 'green', 'color': '#00ff00', 'model': 'green.stl',
                         'piece': 'green'})
            manifest['pieces'][1].update({'id': 'green', 'name': 'green',
                                          'models': ['green.stl']})
            (stage / 'manifest.json').write_text(json.dumps(manifest))
            (stage / 'red.stl').write_bytes(plate_stl())
            (stage / 'green.stl').write_bytes(plate_stl(back=0.15, front=0.19))
            (stage / 'index.html').write_text(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<style>html,body,#host{margin:0;width:100%;height:100%;'
                'overflow:hidden}canvas{display:block}</style></head><body>'
                '<div id="host"></div><script src="/viewer.js"></script>'
                '</body></html>')
            mode = {'delay': None}
            completions = []
            lock = threading.Lock()

            class DelayedHandler(QuietHandler):
                def do_GET(self):
                    path = urlsplit(self.path).path
                    if path not in ('/red.stl', '/green.stl'):
                        return super().do_GET()
                    name = path[1:-4]
                    if name == mode['delay']:
                        time.sleep(0.2)
                    super().do_GET()
                    with lock:
                        completions.append(name)

            server = ThreadingHTTPServer(
                ('127.0.0.1', 0), partial(DelayedHandler, directory=str(stage)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_address[1]}/'
                frames = []
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(args=[
                        '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                    try:
                        for delayed in ('green', 'red'):
                            mode['delay'] = delayed
                            with lock:
                                completions.clear()
                            context = browser.new_context(
                                viewport={'width': 640, 'height': 480},
                                device_scale_factor=1)
                            try:
                                page = context.new_page()
                                page.goto(url, wait_until='load')
                                page.evaluate('''async () => {
                                  window.viewer = await MachinomeViewer.mount(
                                    '#host', '/manifest.json', {
                                      renderMode: 'on-demand', animation: 'external',
                                      autoplay: false, driverControls: 'none',
                                      partControls: 'none', time: 0.25,
                                      up: [0, 1, 0], fov: 50,
                                      view: {camera: [0, 0, 5], target: [0, 0, 0]}
                                    });
                                  window.viewer.setView({camera: [0, 0, 5],
                                    target: [0, 0, 0]});
                                  window.viewer.setTime(0.25);
                                }''')
                                with lock:
                                    order = tuple(completions)
                                self.assertEqual(order, ('red', 'green') if delayed == 'green'
                                                 else ('green', 'red'))
                                frame = page.screenshot()
                                r, g, b = Image.open(io.BytesIO(frame)).convert('RGB').getpixel((320, 240))
                                self.assertGreater(g, 1.5 * max(r, b),
                                                   'the physically nearer green plate must win')
                                frames.append(frame)
                            finally:
                                context.close()
                    finally:
                        browser.close()
                self.assertEqual(frames[0], frames[1],
                                 'real depth changed with STL completion order')
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
