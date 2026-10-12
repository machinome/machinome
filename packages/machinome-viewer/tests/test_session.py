# machinome-viewer - the browser viewer for Machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The development server in the framework's process (change `viewer-seam`).

`machinome.viewer.web.serve` starts the server in a thread the provider owns
and returns its session once the server listens. The session tells every
open page that a build was published by sending `reload` on its reload
socket, which stays open, and its `stop` returns when the server has
stopped. A port another listener holds is refused by `serve` at once. Once
the server listens, the session prints its address on standard output, the
one line a maker running `machinome viewer serve` or `machinome develop`
reads it from (change `viewer-command`).
"""

import io
import json
import os
import socket
import tempfile
import threading
import time
import urllib.request
from contextlib import redirect_stdout
from unittest import TestCase

from websockets.sync.client import connect

import machinome.viewer as viewers
import machinome.viewer.web as web


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


class LiveSessionTest(TestCase):

    def setUp(self):
        self.build = tempfile.TemporaryDirectory(prefix='viewer-session-')
        self.addCleanup(self.build.cleanup)
        with open(os.path.join(self.build.name, 'viewer.json'), 'w') as out:
            json.dump({'format': 'machinome-document', 'version': 1}, out)
        self.port = free_port()
        self.session = web.serve(self.build.name, port=self.port)
        self.addCleanup(self.session.stop)

    def get(self, path):
        with urllib.request.urlopen(
                f'http://127.0.0.1:{self.port}{path}', timeout=5) as answer:
            return answer.read()

    def test_the_server_listens_when_serve_returns(self):
        self.assertEqual(json.loads(self.get('/build/viewer.json'))['version'],
                         1)

    def test_a_reload_reaches_every_open_page_without_closing_it(self):
        url = f'ws://127.0.0.1:{self.port}/ws/reload'
        with connect(url) as first, connect(url) as second:
            self.assertEqual(first.recv(timeout=5), 'reload')
            self.assertEqual(second.recv(timeout=5), 'reload')
            for _ in range(2):
                self.session.reload()
                self.assertEqual(first.recv(timeout=5), 'reload')
                self.assertEqual(second.recv(timeout=5), 'reload')
            first.ping().wait(timeout=5)

    def test_a_reload_with_no_page_open_is_nothing(self):
        self.session.reload()
        self.assertEqual(json.loads(self.get('/build/viewer.json'))['version'],
                         1)

    def test_stop_returns_when_the_server_has_stopped(self):
        named = [thread for thread in threading.enumerate()
                 if thread.name == 'machinome-viewer-web']
        self.assertEqual(len(named), 1)
        self.session.stop()
        self.assertFalse(named[0].is_alive())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as again:
            again.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            again.bind(('0.0.0.0', self.port))
        self.session.stop()


class TheAddressIsPrintedTest(TestCase):

    def test_one_line_names_the_address_once_the_server_listens(self):
        port = free_port()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as build, redirect_stdout(output):
            session = web.serve(build, port=port)
            try:
                printed = output.getvalue()
                with urllib.request.urlopen(
                        f'http://127.0.0.1:{port}/_viewer', timeout=5):
                    pass
            finally:
                session.stop()
        self.assertEqual(printed,
                         f'Serving at http://0.0.0.0:{port} (Ctrl+C to stop)\n')
        self.assertEqual(output.getvalue(), printed)

    def test_a_server_that_cannot_listen_prints_no_address(self):
        held = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(held.close)
        held.bind(('0.0.0.0', 0))
        held.listen()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as build, redirect_stdout(output), \
                self.assertRaises(viewers.ViewerError):
            web.serve(build, port=held.getsockname()[1])
        self.assertEqual(output.getvalue(), '')


class TakenPortTest(TestCase):

    def test_serve_raises_within_a_second(self):
        held = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(held.close)
        held.bind(('0.0.0.0', 0))
        held.listen()
        port = held.getsockname()[1]
        with tempfile.TemporaryDirectory() as build:
            started = time.monotonic()
            with self.assertRaises(viewers.ViewerError) as raised:
                web.serve(build, port=port)
            elapsed = time.monotonic() - started
        self.assertLess(elapsed, 1.0)
        self.assertEqual(str(raised.exception),
                         f'the web viewer cannot serve on port {port}: '
                         'Address already in use')
        self.assertEqual([thread for thread in threading.enumerate()
                          if thread.name == 'machinome-viewer-web'], [])
