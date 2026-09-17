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
import json
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
#: The Pascaline module's own published build: a version 5 document
#: carrying a compiled mechanical program, beside stand-in meshes.
PASCALINE = FIXTURES / 'pascaline'
#: The pin tumbler lock's own published build: a version 5 document
#: whose spans READ OTHER COORDINATES, beside stand-in meshes. See its
#: own README.
LOCK = FIXTURES / 'lock'
#: The same module's classes published with a `controls` table: a
#: version 5 document whose six controls make three dials touchable,
#: beside stand-in meshes. See its own README.
TOUCHED = FIXTURES / 'touched'
#: The framework's own marked bench, exported verbatim: a version 2
#: document whose two parts carry three markings between them, beside
#: REAL part meshes and their decal sheets. See its own README.
MARKED = FIXTURES / 'marked'
#: The Curta's own clearing interface, exported from the framework's own
#: test machine: a version 6 document whose six law edges each READ THE
#: COORDINATE THEY DRIVE, beside a stand-in mesh. See its own README.
CLEARING = FIXTURES / 'clearing'
#: The Curta-SHAPED fixture, exported from the framework's own
#: `tests/clocked_project/calculator.py:Calculator`: a version 8
#: document carrying a compiled CLOCKED machine -- four wheels of one
#: class, a stroke over four digits and an operand, a clearing relation
#: per wheel, a selector wired through a port, an anti-reversal ratchet
#: and an off-rest freeze -- beside the meshes it names. See its own
#: README.
CALCULATOR = FIXTURES / 'calculator'
#: The Curta's own CARRIAGE, exported from the framework's own test
#: machine: a version 7 document whose nine law edges hold ONE BLOCK of
#: seven -- four dials on the carriage and three levers on the frame,
#: a cycle every carriage position breaks -- beside the meshes it names.
#: See its own README.
CARRIAGE = FIXTURES / 'carriage'

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


def published_run(target):
    """Stage the running fixture: a version 5 document carrying a
    program, already named ``viewer.json``, beside the meshes it names."""
    shutil.copytree(PASCALINE, target)
    return Path(target)


def published_lock(target):
    """Stage the LOCK fixture: the lock's own published version 5
    document, whose bounds read other coordinates, beside the stand-in
    meshes it names."""
    shutil.copytree(LOCK, target)
    return Path(target)


def published_calculator(target):
    """Stage the CALCULATOR fixture: the Curta-shaped machine as a
    version 8 document -- a `states` table and a compiled `clocked`
    object with three bounds -- already named ``viewer.json``, beside
    the meshes it names."""
    shutil.copytree(CALCULATOR, target)
    return Path(target)


def published_carriage(target):
    """Stage the CARRIAGE fixture: the Curta's own carriage as a
    version 7 document -- nine law edges of which seven form one block --
    already named ``viewer.json``, beside the meshes it names."""
    shutil.copytree(CARRIAGE, target)
    return Path(target)


def published_touched(target):
    """Stage the TOUCHABLE running fixture: the same shape as
    :func:`published_run`, with a `controls` table beside the program."""
    shutil.copytree(TOUCHED, target)
    return Path(target)


def export_marked(target):
    """Copy the MARKED fixture into ``target`` and complete it with the
    installed widget files, exactly as `solid export` would have --
    :func:`export_with_widget`'s shape, over the marked bench."""
    shutil.copytree(MARKED, target)
    shutil.copy2(bundle_path(), Path(target) / 'solid-widget.js')
    shutil.copy2(index_path(), Path(target) / 'index.html')
    return Path(target)


def published_marked(target):
    """Stage the MARKED fixture shaped as a normal build: the document
    is named ``viewer.json``, beside the models and the decal sheets it
    names -- :func:`published_build`'s shape, over the marked bench."""
    shutil.copytree(MARKED, target)
    (Path(target) / 'manifest.json').rename(Path(target) / 'viewer.json')
    return Path(target)


def strip_markings(document_path, target_path=None):
    """Write ``document_path`` again with every `markings` key removed.

    The UNMARKED TWIN every "renders exactly as before" and "reads
    exactly as before" assertion compares against: the same document,
    the same models, the same everything else. Produced by the test that
    needs it and never committed -- the fixture is the marked one, and
    the twin is one `del` away from it.
    """
    document_path = Path(document_path)
    target_path = Path(target_path) if target_path else document_path
    document = json.loads(document_path.read_text())

    def strip(node):
        node.pop('markings', None)
        for child in node.get('children', []):
            strip(child)

    strip(document['root'])
    target_path.write_text(json.dumps(document))
    return target_path


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        # The suites rewrite a served document between two fetches of the
        # same URL -- a republish, which is what `solid develop` does --
        # and a browser answering the second from its cache would test
        # the bytes of the first.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


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
