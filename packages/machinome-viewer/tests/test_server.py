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
    CHROME, HAS_PIL, needs_bundle, needs_chrome, needs_pil, published_build,
)

if HAS_PIL:
    from PIL import Image


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

    def test_an_unbuilt_app_is_reported_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.object(server_module, 'app_build_path',
                          return_value=Path(tmpdir) / 'no-build'):
            client = TestClient(WebViewer(tmpdir).app)
            page = client.get('/')
            error = client.get('/_build_error')
        self.assertEqual(page.status_code, 503)
        self.assertIn('npm run build', page.json()['remedy'])
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
        if not server_module.app_build_path().is_dir():
            self.skipTest('development app not built (npm run build)')

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
        result = run([
            CHROME, '--headless', '--no-sandbox', '--disable-gpu',
            '--use-angle=swiftshader', '--window-size=800,600',
            '--virtual-time-budget=4000', f'--screenshot={image_path}', self.url,
        ], capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr.decode()[-500:])
        image = Image.open(image_path).convert('RGB')
        red = sum(1 for r, g, b in image.getdata()
                  if r > 100 and r > 1.4 * g and r > 1.4 * b)
        blue = sum(1 for r, g, b in image.getdata()
                   if b > 100 and b > 1.4 * r and b > 1.4 * g)
        self.assertGreater(red, 500, 'red hub not visible')
        self.assertGreater(blue, 2000, 'blue blades not visible')
