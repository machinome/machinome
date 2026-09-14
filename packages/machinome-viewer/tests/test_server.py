# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""HTTP coverage for the development server."""

import json
import socket
import tempfile
import threading
from pathlib import Path
from subprocess import run
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
import uvicorn

from solid_node_viewer import server as server_module
from solid_node_viewer.server import WebViewer

from .support import (
    CHROME, HAS_PIL, HAS_PLAYWRIGHT, needs_bundle, needs_chrome, needs_pil,
    needs_playwright, published_build,
)

if HAS_PIL:
    from PIL import Image
if HAS_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright


class PublishedBuildTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.build_dir = Path(self.tempdir.name) / 'published-build'
        self.build_dir.mkdir()
        (self.build_dir / 'models').mkdir()
        (self.build_dir / 'models' / 'part.stl').write_text('solid part')
        (self.build_dir / 'viewer.json').write_text(json.dumps({
            'format': 'solid-node-export',
            'version': 1,
            'animation': {'fps': 30, 'frames': 360},
            'root': {'name': 'part', 'model': 'models/part.stl'},
        }))

    def viewer(self):
        return WebViewer(self.build_dir, dev=True)

    def test_serves_the_published_snapshot_and_models(self):
        client = TestClient(self.viewer().app)
        snapshot = client.get('/build/viewer.json')
        model = client.get('/build/models/part.stl')
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()['root']['model'], 'models/part.stl')
        self.assertEqual(model.status_code, 200)
        self.assertEqual(model.text, 'solid part')

    def test_a_request_cannot_escape_the_build_directory(self):
        outside = Path(self.tempdir.name) / 'secret.stl'
        outside.write_text('solid secret')
        (self.build_dir / 'models' / 'escape.stl').symlink_to(outside)
        client = TestClient(self.viewer().app)
        self.assertEqual(client.get('/build/models/escape.stl').status_code, 404)

    def test_reports_an_absent_snapshot_without_failing_the_server(self):
        (self.build_dir / 'viewer.json').unlink()
        client = TestClient(self.viewer().app)
        self.assertEqual(client.get('/build/viewer.json').status_code, 404)
        self.assertEqual(client.get('/_build_error').status_code, 200)
        self.assertEqual(client.get('/_build_error').json(), {})

    def test_reports_a_recorded_build_error(self):
        (self.build_dir / 'errors.json').write_text(
            json.dumps({'error': 'boom', 'tstamp': 1.0}))
        client = TestClient(self.viewer().app)
        self.assertEqual(client.get('/_build_error').json(),
                         {'error': 'boom', 'tstamp': 1.0})

    def test_the_reload_channel_greets_with_reload(self):
        client = TestClient(self.viewer().app)
        with client.websocket_connect('/ws/reload') as socket_:
            self.assertEqual(socket_.receive_text(), 'reload')

    def test_ports_default_from_the_environment(self):
        with patch.dict('os.environ', {'SOLID_NODE_PORT': '8123',
                                       'SOLID_NODE_FRONTEND_PORT': '3123'}):
            viewer = self.viewer()
        self.assertEqual(viewer.port, 8123)
        self.assertEqual(viewer.frontend, 3123)
        self.assertEqual(WebViewer(self.build_dir, port=9000, frontend=9001).port, 9000)


class BundleRoutesTest(TestCase):
    def test_reports_available_bundle_and_api_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle = Path(tmpdir) / 'solid-widget.js'
            bundle.write_text('window.SolidNodeWidget = {};')
            with patch.object(server_module, 'bundle_path', return_value=bundle), \
                 patch.object(server_module, 'has_bundle', return_value=True), \
                 patch.object(server_module, 'api_version', return_value=1):
                client = TestClient(WebViewer(tmpdir, dev=True).app)
                status = client.get('/_viewer')
                script = client.get('/_viewer/bundle.js')
        self.assertEqual(status.json(), {
            'available': True, 'apiVersion': 1, 'remedy': None,
        })
        self.assertEqual(script.status_code, 200)
        self.assertIn('SolidNodeWidget', script.text)

    def test_reports_the_remedy_when_the_bundle_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.object(server_module, 'has_bundle', return_value=False), \
             patch.object(server_module, 'api_version', return_value=1), \
             patch.object(server_module, 'missing_bundle_remedy',
                          return_value='run npm run build'):
            client = TestClient(WebViewer(tmpdir, dev=True).app)
            status = client.get('/_viewer')
            script = client.get('/_viewer/bundle.js')
        self.assertEqual(status.json(), {
            'available': False, 'apiVersion': 1, 'remedy': 'run npm run build',
        })
        self.assertEqual(script.status_code, 503)
        self.assertEqual(script.json()['remedy'], 'run npm run build')

    def test_a_build_artifact_is_never_cached(self):
        # A republished `viewer.json` must reach the widget's plain
        # `fetch()` on the next reload; a browser's heuristic freshness
        # would otherwise serve the previous document for a while.
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'viewer.json').write_text('{}')
            client = TestClient(WebViewer(tmpdir).app)
            artifact = client.get('/build/viewer.json')
        self.assertEqual(artifact.status_code, 200)
        self.assertEqual(artifact.headers.get('cache-control'), 'no-store')

    def test_the_development_page_is_served_from_the_package(self):
        # The page is a package file this server answers `/` with
        # (design D13) -- not a build output, so it is present whether
        # or not the widget bundle itself has been built.
        with tempfile.TemporaryDirectory() as tmpdir:
            client = TestClient(WebViewer(tmpdir).app)
            page = client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn('/_viewer/bundle.js', page.text)
        self.assertIn('mountDevelopment', page.text)

    def test_a_missing_development_page_is_reported_not_fatal(self):
        # Can only mean a broken installation (design D13), but the
        # build, bundle and error routes stay available regardless --
        # the same shape the old unbuilt-app route had.
        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.object(server_module, 'develop_page_path',
                          return_value=Path(tmpdir) / 'no-such-file.html'):
            client = TestClient(WebViewer(tmpdir).app)
            page = client.get('/')
            error = client.get('/_build_error')
        self.assertEqual(page.status_code, 503)
        self.assertIn('no-such-file.html', page.json()['remedy'])
        self.assertEqual(error.status_code, 200)


@needs_bundle
@needs_chrome
@needs_pil
class DevelopmentAppBrowserTest(TestCase):
    """The development app renders a published build through the bundle."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.build_dir = published_build(Path(self.tempdir.name) / '_build')

        with socket.socket() as reserved:
            reserved.bind(('127.0.0.1', 0))
            port = reserved.getsockname()[1]
        self.server = uvicorn.Server(uvicorn.Config(
            WebViewer(self.build_dir, dev=False, port=port).app,
            host='127.0.0.1', port=port, log_level='error',
        ))
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f'http://127.0.0.1:{port}/'
        for _ in range(50):
            if self.server.started:
                break
            threading.Event().wait(0.1)
        self.assertTrue(self.server.started, 'development server did not start')

    def stop_server(self):
        self.server.should_exit = True
        self.thread.join(timeout=5)

    def test_the_spinner_renders_with_its_declared_colours(self):
        image_path = Path(self.tempdir.name) / 'development-viewer.png'
        # The development page now opens with its assembly sidebar open
        # (design D10) -- collapsed here by the query string so this
        # colour-pixel test keeps measuring the full-width canvas its
        # thresholds were tuned against; the sidebar itself is proved
        # separately (`develop.test.ts`, `InspectorLayoutE2ETest`).
        result = run([
            CHROME, '--headless', '--no-sandbox', '--disable-gpu',
            '--use-angle=swiftshader', '--window-size=800,600',
            '--virtual-time-budget=4000', f'--screenshot={image_path}',
            f'{self.url}?sidebar=collapsed',
        ], capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr.decode()[-500:])
        image = Image.open(image_path).convert('RGB')
        red = sum(1 for r, g, b in image.getdata()
                  if r > 100 and r > 1.4 * g and r > 1.4 * b)
        blue = sum(1 for r, g, b in image.getdata()
                   if b > 100 and b > 1.4 * r and b > 1.4 * g)
        self.assertGreater(red, 500, 'red hub not visible')
        self.assertGreater(blue, 2000, 'blue blades not visible')


@needs_bundle
@needs_playwright
class DevelopmentPageReloadTest(TestCase):
    """The claim this whole cycle turns on (design D12): a republished
    document updates the served development page in place, with no page
    load. Partial reload is `manifestChanged()` (ADR-037), untouched by
    this change; what moves is only the 150 lines that decide WHEN to
    call it, ported into the bundle in increment 3."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.build_dir = published_build(Path(self.tempdir.name) / '_build')

        with socket.socket() as reserved:
            reserved.bind(('127.0.0.1', 0))
            port = reserved.getsockname()[1]
        self.server = uvicorn.Server(uvicorn.Config(
            WebViewer(self.build_dir, port=port).app,
            host='127.0.0.1', port=port, log_level='error',
        ))
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f'http://127.0.0.1:{port}/'
        for _ in range(50):
            if self.server.started:
                break
            threading.Event().wait(0.1)
        self.assertTrue(self.server.started, 'development server did not start')

    def stop_server(self):
        self.server.should_exit = True
        self.thread.join(timeout=5)

    def test_a_republished_document_updates_the_page_in_place(self):
        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=[
                '--no-sandbox', '--disable-gpu', '--use-angle=swiftshader',
            ])
            try:
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.on('pageerror', lambda error: errors.append(str(error)))
                # Capture the reloader's own socket so the test can force
                # exactly the reconnect a `solid develop` server restart
                # drives (spec "Rebuild refreshes the browser"), without
                # actually killing and rebinding this test's own server.
                page.add_init_script("""
                    window.__sockets = [];
                    const Native = window.WebSocket;
                    window.WebSocket = function(url) {
                        const socket = new Native(url);
                        window.__sockets.push(socket);
                        return socket;
                    };
                    window.WebSocket.prototype = Native.prototype;
                """)
                page.goto(self.url)
                page.wait_for_selector('.solid-nav-row')
                # A property set on window survives an in-place update
                # and is lost by a page load (design D11/D12's claim).
                page.evaluate('window.__pageLoad = performance.now()')
                stamp_before = page.evaluate('window.__pageLoad')
                rows_before = page.locator('.solid-nav-row').count()

                # The file write lands BETWEEN two evaluations, as
                # `solid develop`'s own rebuild does
                # (`tests/test_widget_e2e.py`'s
                # `test_a_targeted_update_notifies_once_with_reconciled_state`
                # uses the same direct-`sync_playwright` shape).
                manifest = json.loads((self.build_dir / 'viewer.json').read_text())
                manifest['root']['children'] = manifest['root']['children'][:-1]
                (self.build_dir / 'viewer.json').write_text(json.dumps(manifest))

                page.evaluate('window.__sockets[window.__sockets.length - 1].close()')
                page.wait_for_function(
                    'document.querySelectorAll(".solid-nav-row").length < %d'
                    % rows_before, timeout=10000)

                stamp_after = page.evaluate('window.__pageLoad')
                rows_after = page.locator('.solid-nav-row').count()
            finally:
                browser.close()

        self.assertEqual(errors, [], f'uncaught page errors: {errors}')
        self.assertIsNotNone(stamp_after, 'the page reloaded: window.__pageLoad was lost')
        self.assertEqual(stamp_after, stamp_before,
                         'a page load happened between the two reads')
        self.assertLess(rows_after, rows_before,
                        'the tree did not shrink after the republish')
