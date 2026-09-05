# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""What the suites share: the committed export fixture and a way to see it.

The fixture under tests/fixtures/spinner is a widget-less
`solid export` of the framework's spinner test project -- a red hub and
three blue blades turning with `$t`. It is committed rather than produced
here because this repository does not depend on the framework: the viewer
reads documents, it does not make them.
"""

import glob
import os
import shutil
import threading
import unittest
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from solid_node_viewer.bundle import bundle_path, index_path

FIXTURES = Path(__file__).parent / 'fixtures'
SPINNER = FIXTURES / 'spinner'

try:
    from PIL import Image, ImageChops  # noqa: F401
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from playwright.sync_api import sync_playwright  # noqa: F401
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def find_headless_chrome():
    """A chromium able to take --headless --screenshot shots.
    Prefers an explicit $SOLID_HEADLESS_CHROME, then playwright's cached
    headless shell, then a browser on PATH."""
    explicit = os.environ.get('SOLID_HEADLESS_CHROME')
    if explicit:
        return explicit
    cached = sorted(glob.glob(os.path.expanduser(
        '~/.cache/ms-playwright/chromium_headless_shell-*/'
        'chrome-headless-shell-*/chrome-headless-shell'
    )))
    if cached:
        return cached[-1]
    for name in ('chromium', 'chromium-browser', 'google-chrome', 'chrome'):
        path = shutil.which(name)
        if path:
            return path
    return None


CHROME = find_headless_chrome()

needs_bundle = unittest.skipUnless(
    bundle_path().exists(), 'widget bundle not built (npm run build)')
needs_chrome = unittest.skipUnless(CHROME, 'no headless chromium available')
needs_pil = unittest.skipUnless(HAS_PIL, 'Pillow not installed')
needs_playwright = unittest.skipUnless(HAS_PLAYWRIGHT, 'playwright not installed')


def export_with_widget(target):
    """Copy the fixture export into ``target`` and complete it with the
    installed widget files, exactly as `solid export` would have."""
    shutil.copytree(SPINNER, target)
    shutil.copy2(bundle_path(), Path(target) / 'solid-widget.js')
    shutil.copy2(index_path(), Path(target) / 'index.html')
    return Path(target)


def published_build(target):
    """Copy the fixture export into ``target`` shaped as a normal build:
    the document is named ``viewer.json``."""
    shutil.copytree(SPINNER, target)
    (Path(target) / 'manifest.json').rename(Path(target) / 'viewer.json')
    return Path(target)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@contextmanager
def serve_directory(directory):
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
