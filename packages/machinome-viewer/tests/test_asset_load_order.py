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
    def test_queued_models_and_markings_keep_pixels_and_duplicate_viewer_ownership(self):
        with tempfile.TemporaryDirectory(prefix='viewer-queued-order-') as temp:
            stage = Path(temp)
            shutil.copy2(bundle_path(), stage / 'viewer.js')
            payload = document()
            original = payload['root']['children']
            payload['root']['children'] = [
                {**original[index % 2], 'name': f'plate{index}',
                 'model': f'plate{index}.stl'} for index in range(8)
            ]
            payload['root']['children'][0]['markings'] = [
                {'name': 'first', 'model': 'mark0.stl', 'color': '#ffffff'},
                {'name': 'second', 'model': 'mark1.stl', 'color': '#333333'},
            ]
            (stage / 'manifest.json').write_text(json.dumps(payload))
            for name in [f'plate{i}' for i in range(8)] + ['mark0', 'mark1']:
                (stage / f'{name}.stl').write_bytes(plate_stl())
            (stage / 'index.html').write_text(
                '<html><style>html,body{margin:0}.host{width:320px;'
                'height:240px;display:inline-block;vertical-align:top}'
                'canvas{display:block}</style>'
                '<div id="a" class="host"></div><div id="b" class="host"></div>'
                '<script src="viewer.js"></script></html>')
            mode = {'reverse': False}

            class DelayedHandler(QuietHandler):
                protocol_version = 'HTTP/1.1'

                def do_GET(self):
                    path = urlsplit(self.path).path.rsplit('/', 1)[-1]
                    if path.endswith('.stl'):
                        index = int(path[5:-4]) if path.startswith('plate') else int(path[4:-4])
                        delay = index % 4 if mode['reverse'] else 3-index % 4
                        time.sleep(delay * .01)
                    super().do_GET()

            server = ThreadingHTTPServer(('127.0.0.1', 0),
                partial(DelayedHandler, directory=str(stage)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(thread.join, 2)
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            url = f'http://127.0.0.1:{server.server_port}/'
            with sync_playwright() as pw:
                browser = pw.chromium.launch(args=[
                    '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                try:
                    frames = []
                    for reverse in (False, True):
                        mode['reverse'] = reverse
                        page = browser.new_page(viewport={'width': 640, 'height': 240})
                        session = page.context.new_cdp_session(page)
                        session.send('Network.enable')
                        session.send('Network.setCacheDisabled', {'cacheDisabled': True})
                        network_events = []
                        session.on('Network.requestWillBeSent', lambda event, rows=network_events:
                            rows.append({'event':'request','id':event['requestId'],
                                'url':event['request']['url'],'at':time.time()}))
                        session.on('Network.loadingFailed', lambda event, rows=network_events:
                            rows.append({'event':'failed','at':time.time(),**event}))
                        errors = []
                        page.on('pageerror', lambda error, errors=errors: errors.append(str(error)))
                        page.on('requestfailed', lambda request, errors=errors: errors.append(
                            (request.url, request.failure)))
                        # The server delays real responses inside each group;
                        # the viewer owns all network and STL parsing work.
                        page.goto(url)
                        page.evaluate('''() => {
                          window.fetchFailures=[];const oldFetch=window.fetch;
                          window.phases=[];window.bodyDone=[];
                          window.fetch=(...args)=>oldFetch(...args).then(response=>{
                            if(response.body){const oldGet=response.body.getReader.bind(response.body);
                              response.body.getReader=()=>{const reader=oldGet();const oldRead=reader.read.bind(reader);let bytes=0;
                                reader.read=(...args)=>oldRead(...args).then(result=>{
                                  if(result.value)bytes+=result.value.byteLength;
                                  if(result.done)bodyDone.push({url:response.url,at:Date.now()/1000,bytes,status:response.status});return result});return reader};}
                            return response;
                          }).catch(error=>{fetchFailures.push(String(error));throw error});
                        }''')
                        result = page.evaluate('''async () => {
                          const options={renderMode:'on-demand',animation:'external',
                            autoplay:false,driverControls:'none',partControls:'none',
                            view:{camera:[0,0,5],target:[0,0,0]}};
                          phases.push({phase:'mount start',at:Date.now()/1000});
                          [window.first,window.second]=await Promise.all([
                            MachinomeViewer.mount('#a','/manifest.json',options),
                            MachinomeViewer.mount('#b','/manifest.json',options)]);
                          first.setView(first.view()); second.setView(second.view());
                          phases.push({phase:'mount done',at:Date.now()/1000});
                          return [first.assembly().children.length,second.assembly().children.length];
                        }''')
                        self.assertEqual(result, [8, 8])
                        def check_loads():
                            readings = page.evaluate('({phases,bodyDone,fetchFailures})')
                            self.assertEqual(readings['fetchFailures'], [])
                            expected = {url + name + '.stl' for name in
                                [f'plate{i}' for i in range(8)] + ['mark0', 'mark1']}
                            self.assertEqual({row['url'] for row in readings['bodyDone']}, expected)
                            for row in readings['bodyDone']:
                                self.assertEqual((row['status'], row['bytes']), (200, len(plate_stl())))
                            requests = {row['id']: row['url'] for row in network_events
                                        if row['event'] == 'request'}
                            completed = list(readings['bodyDone'])
                            failed = [row for row in network_events if row['event'] == 'failed']
                            if errors:
                                print('NETWORK_DIAGNOSIS', json.dumps({'events':network_events,
                                    'readbacks':readings}), flush=True)
                            # Chromium may report canceled ERR_ABORTED just AFTER
                            # a completely consumed body (also reproduced on the
                            # frozen base). Qualify only that exact observation;
                            # pre-completion or other failures remain red. Each
                            # failed request consumes its own completed-body fact.
                            for row in failed:
                                self.assertEqual((row.get('canceled'), row['errorText']),
                                                 (True, 'net::ERR_ABORTED'))
                                match = next((body for body in completed if
                                    body['url'] == requests[row['requestId']] and
                                    body['at'] <= row['at']), None)
                                self.assertIsNotNone(match, 'request failed before its body completed')
                                completed.remove(match)
                            self.assertEqual(len(errors), len(failed), 'page or unqualified request failure')

                        check_loads()
                        before = page.locator('#b').screenshot()
                        page.evaluate('first.dispose(); second.setView(second.view())')
                        self.assertEqual(before, page.locator('#b').screenshot(),
                                         'disposing a duplicate-URL viewer changed another owner')
                        frames.append(before)
                        check_loads()
                        page.evaluate('second.dispose()')
                        # Keep pages alive until both trials finish. Closing a
                        # page can abort Chromium's trailing network events,
                        # which are teardown rather than viewer readiness.
                    self.assertEqual(frames[0], frames[1], 'queued identities depend on completion order')
                finally:
                    browser.close()

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
