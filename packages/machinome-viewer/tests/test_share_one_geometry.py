# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Parts that name one model file share one geometry, in a real browser.

OpenSpec `share-one-geometry-per-model-file`, design Decision 11, B1 to
B3: the WebGL buffers each viewer's context creates and deletes, counted
by an init script that wraps `createBuffer`, `deleteBuffer` and
`bufferData` per context, and decoded pixels compared against the same
document in which every part names its own copy of the same bytes.
Served by `QuietHandler` (`Cache-Control: no-store`), in Chromium with
SwiftShader, as `test_asset_load_order.py` serves and launches.
"""

import io
import json
import shutil
import struct
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from machinome.viewer.web.bundle import bundle_path
from tests.support import QuietHandler, needs_bundle, needs_pil, needs_playwright

try:
    from PIL import Image
except ImportError:  # pragma: no cover - guarded by needs_pil
    Image = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None


def solid_stl(size=1.0):
    """A closed tetrahedron, binary, with the extent ``size``."""
    facets = [((0, 0, 0), (0, size, 0), (size, 0, 0)),
              ((0, 0, 0), (0, 0, size), (0, size, 0)),
              ((0, 0, 0), (size, 0, 0), (0, 0, size)),
              ((size, 0, 0), (0, size, 0), (0, 0, size))]
    out = bytearray(80) + struct.pack('<I', len(facets))
    for facet in facets:
        out += struct.pack('<3f', 0, 0, 0)
        for vertex in facet:
            out += struct.pack('<3f', *vertex)
        out += b'\0\0'
    return bytes(out)


def part(name, model, x, colour='#c08040'):
    return {'name': name, 'type': 'LeafNode', 'color': colour, 'mtime': 1,
            'operations': [['t', [str(x), '0', '0']]], 'model': model}


def document(models):
    colours = ['#c08040', '#4080c0', '#40c080', '#c04080']
    return {'format': 'machinome-export', 'version': 2,
            'animation': {'fps': 30, 'frames': 30},
            'drivers': {}, 'instructions': {},
            'root': {'name': 'root', 'type': 'AssemblyNode', 'color': None,
                     'mtime': 1, 'operations': [],
                     'children': [part(name, model, 2 * index, colours[index])
                                  for index, (name, model) in enumerate(zip('abcd', models))]}}


# Four parts, three naming one file; and the same parts, each naming its
# own copy of the same bytes.
SHARED = ['shared.stl', 'shared.stl', 'shared.stl', 'other.stl']
COPIES = ['shared.stl', 'copy1.stl', 'copy2.stl', 'other.stl']

COUNT_BUFFERS = """
(() => {
  // Per context, on its canvas, which outlives the context's viewer.
  const counts = (context) => {
    const canvas = context.canvas;
    if (!canvas.__buffers) canvas.__buffers = {created: 0, deleted: 0, bytes: 0};
    return canvas.__buffers;
  };
  for (const proto of [WebGL2RenderingContext.prototype, WebGLRenderingContext.prototype]) {
    const create = proto.createBuffer, remove = proto.deleteBuffer, data = proto.bufferData;
    proto.createBuffer = function () { counts(this).created++; return create.call(this); };
    proto.deleteBuffer = function (buffer) {
      if (buffer) counts(this).deleted++;
      return remove.call(this, buffer);
    };
    proto.bufferData = function (target, source, usage) {
      if (source && source.byteLength) counts(this).bytes += source.byteLength;
      return data.call(this, target, source, usage);
    };
  }
  // A host's canvas is found while it is mounted and kept after.
  window.canvases = {};
  window.buffers = (host) => {
    if (!window.canvases[host]) window.canvases[host] = document.querySelector(`#${host} canvas`);
    return {...(window.canvases[host].__buffers || {created: 0, deleted: 0, bytes: 0})};
  };
})();
"""

OPTIONS = ("{renderMode:'on-demand',animation:'external',autoplay:false,"
           "driverControls:'none',partControls:'none',"
           "view:{camera:[3,-10,6],target:[3,0,0]}}")


@needs_bundle
@needs_playwright
@needs_pil
class ShareOneGeometryTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='viewer-share-geometry-')
        self.addCleanup(temp.cleanup)
        stage = Path(temp.name)
        shutil.copy2(bundle_path(), stage / 'viewer.js')
        for name in ('shared', 'copy1', 'copy2', 'other'):
            (stage / f'{name}.stl').write_bytes(solid_stl())
        (stage / 'shared.json').write_text(json.dumps(document(SHARED)))
        (stage / 'copies.json').write_text(json.dumps(document(COPIES)))
        (stage / 'index.html').write_text(
            '<html><style>html,body{margin:0}.host{width:320px;height:240px;'
            'display:inline-block;vertical-align:top}canvas{display:block}</style>'
            '<body><div id="a" class="host"></div><div id="b" class="host"></div>'
            '<script src="viewer.js"></script></body></html>')
        server = ThreadingHTTPServer(('127.0.0.1', 0),
                                     partial(QuietHandler, directory=str(stage)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.url = f'http://127.0.0.1:{server.server_port}/'
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        self.browser = playwright.chromium.launch(args=[
            '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        self.addCleanup(self.browser.close)

    def page(self):
        page = self.browser.new_page(viewport={'width': 640, 'height': 240})
        self.addCleanup(page.close)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        self.addCleanup(lambda: self.assertEqual(errors, []))
        page.add_init_script(COUNT_BUFFERS)
        page.goto(self.url)
        return page

    def mount(self, page, host, name):
        page.evaluate(f"""async () => {{
          window.{host} = await MachinomeViewer.mount('#{host}', '/{name}.json', {OPTIONS});
          {host}.setView({host}.view());
        }}""")

    def pixels(self, page, host):
        return Image.open(io.BytesIO(page.locator(f'#{host}').screenshot())).convert('RGBA').tobytes()

    def test_b1_one_file_is_uploaded_once_and_every_buffer_is_deleted_at_disposal(self):
        page = self.page()
        self.mount(page, 'a', 'shared')
        mounted = page.evaluate("buffers('a')")
        print('B1 mount', mounted, flush=True)
        page.evaluate("async () => { await a.artifactChanged('shared.stl'); a.setView(a.view()); }")
        changed = page.evaluate("buffers('a')")
        print('B1 artifactChanged', changed, flush=True)
        page.evaluate('a.dispose()')
        disposed = page.evaluate("buffers('a')")
        print('B1 dispose', disposed, flush=True)
        # The stated reason on the base: 8 at mount (a geometry per part),
        # then 6 created and 6 deleted by the update.
        self.assertEqual(mounted['created'], 4)
        self.assertEqual(mounted['deleted'], 0)
        self.assertEqual((changed['created'] - mounted['created'],
                          changed['deleted'] - mounted['deleted']), (2, 2))
        self.assertEqual(disposed['deleted'], disposed['created'])

    def test_b2_pixels_equal_the_same_document_with_every_part_naming_its_own_copy(self):
        pictures = {}
        for name in ('shared', 'copies'):
            page = self.page()
            self.mount(page, 'a', name)
            states = [('mounted', self.pixels(page, 'a'))]
            for mode in ('keep', 'dim', 'ghost'):
                page.evaluate(f"window.clear = a.highlight([['b']], {{others: '{mode}'}}); a.setView(a.view())")
                states.append((f'highlight {mode}', self.pixels(page, 'a')))
                page.evaluate('clear(); a.setView(a.view())')
            page.evaluate("a.setVisible(['c'], false); a.setView(a.view())")
            states.append(('c hidden', self.pixels(page, 'a')))
            page.evaluate("a.setVisible(['c'], true); a.setView(a.view())")
            page.evaluate("async () => { await a.artifactChanged('shared.stl'); a.setView(a.view()); }")
            states.append(('after an artifact update', self.pixels(page, 'a')))
            pictures[name] = states
            page.evaluate('a.dispose()')
        for (state, shared), (_, copied) in zip(pictures['shared'], pictures['copies']):
            self.assertEqual(shared, copied, f'pixels differ {state}')
        self.assertNotEqual(pictures['shared'][0][1], pictures['shared'][3][1],
                            'the ghosting highlight drew nothing')

    def test_b3_disposing_one_of_two_viewers_deletes_its_buffers_and_leaves_the_other(self):
        page = self.page()
        page.evaluate(f"""async () => {{
          [window.a, window.b] = await Promise.all([
            MachinomeViewer.mount('#a', '/shared.json', {OPTIONS}),
            MachinomeViewer.mount('#b', '/shared.json', {OPTIONS})]);
          a.setView(a.view()); b.setView(b.view());
        }}""")
        before = self.pixels(page, 'b')
        page.evaluate("buffers('a'); buffers('b')")
        page.evaluate('a.dispose(); b.setView(b.view())')
        gone = page.evaluate("buffers('a')")
        print('B3 disposed viewer', gone, 'other', page.evaluate("buffers('b')"), flush=True)
        self.assertGreater(gone['created'], 0)
        self.assertEqual(gone['deleted'], gone['created'])
        self.assertEqual(self.pixels(page, 'b'), before)
        page.evaluate('b.dispose()')


if __name__ == '__main__':
    unittest.main()
