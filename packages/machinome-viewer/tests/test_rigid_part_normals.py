# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A part read from a model file is drawn from its positions alone, in a
real browser.

OpenSpec `draw-rigid-parts-without-stored-normals`, design Decision 9, R1
to R3: the WebGL buffers a mount creates, counted by
`test_share_one_geometry.py`'s init script; the bytes a document's
markings add; and the picture, judged by what must hold within one run
(each facet flat, lit on the side facing the viewer, never black, in
every look). No picture is stored: the few numbers R2 and R3 compare
with were recorded once, from the bundle built from the base, and are
written below. The model files are written here, as
`test_share_one_geometry.py` writes its tetrahedron; served by
`QuietHandler`, in Chromium with SwiftShader, in a host of 321 by 241
pixels.
"""

import io
import json
import math
import shutil
import struct
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from machinome.viewer.web.bundle import bundle_path
from tests.support import (
    MARKED, QuietHandler, needs_bundle, needs_pil, needs_playwright, strip_markings,
)
from tests.test_share_one_geometry import COUNT_BUFFERS

try:
    from PIL import Image
except ImportError:  # pragma: no cover - guarded by needs_pil
    Image = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - guarded by needs_playwright
    sync_playwright = None


# ---------------------------------------------------------------------
# Model files.

def binary(facets):
    """A binary STL whose facet normals all say +z, whatever the facet:
    what is drawn is never what the file says."""
    out = bytearray(80) + struct.pack('<I', len(facets))
    for facet in facets:
        out += struct.pack('<3f', 0, 0, 1)
        for vertex in facet:
            out += struct.pack('<3f', *vertex)
        out += b'\0\0'
    return bytes(out)


def _sub(a, b):
    return [a[k] - b[k] for k in range(3)]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def outward(facets):
    """Each triangle of a solid about the origin wound so that its normal
    points away from the origin."""
    wound = []
    for a, b, c in facets:
        centre = [(a[k] + b[k] + c[k]) / 3 for k in range(3)]
        n = _cross(_sub(b, a), _sub(c, a))
        wound.append((a, b, c) if _dot(n, centre) >= 0 else (a, c, b))
    return wound


def cube(s=20.0, inside_out=False):
    """A cube of side ``2 * s`` about the origin, wound outward, or every
    triangle wound inside out."""
    corner = [(x, y, z) for x in (-s, s) for y in (-s, s) for z in (-s, s)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    facets = []
    for a, b, c, d in quads:
        facets += [(corner[a], corner[b], corner[c]), (corner[a], corner[c], corner[d])]
    facets = outward(facets)
    return [(a, c, b) for a, b, c in facets] if inside_out else facets


def sphere(r=20.0, around=64, down=32):
    def point(i, j):
        return (r * math.sin(math.pi * j / down) * math.cos(2 * math.pi * i / around),
                r * math.sin(math.pi * j / down) * math.sin(2 * math.pi * i / around),
                r * math.cos(math.pi * j / down))
    facets = []
    for j in range(down):
        for i in range(around):
            a, b, c, d = point(i, j), point(i + 1, j), point(i + 1, j + 1), point(i, j + 1)
            if j > 0:
                facets.append((a, b, c))
            if j < down - 1:
                facets.append((a, c, d))
    return outward(facets)


def cylinder(r=4.0, length=80.0, sides=512):
    facets = []
    lo, hi = -length / 2, length / 2
    for i in range(sides):
        a0, a1 = 2 * math.pi * i / sides, 2 * math.pi * (i + 1) / sides
        p0 = (r * math.cos(a0), r * math.sin(a0))
        p1 = (r * math.cos(a1), r * math.sin(a1))
        facets += [((*p0, lo), (*p1, lo), (*p1, hi)), ((*p0, lo), (*p1, hi), (*p0, hi)),
                   ((0, 0, hi), (*p0, hi), (*p1, hi)), ((0, 0, lo), (*p1, lo), (*p0, lo))]
    return outward(facets)


FACETS = {
    'cube.stl': cube(),
    'inside-out.stl': cube(inside_out=True),
    'small.stl': cube(s=4.0),
    'sphere.stl': sphere(),
    'cylinder.stl': cylinder(),
}


def leaf(name, model, colour, x=0.0, y=0.0):
    return {'name': name, 'type': 'LeafNode', 'color': colour, 'mtime': 1,
            'operations': [['t', [str(x), str(y), '0']]], 'model': model}


def document(children):
    return {'format': 'machinome-export', 'version': 2,
            'animation': {'fps': 30, 'frames': 30},
            'drivers': {}, 'instructions': {},
            'root': {'name': 'root', 'type': 'AssemblyNode', 'color': None,
                     'mtime': 1, 'operations': [], 'children': children}}


DOCUMENTS = {
    # R1: three files, one part colourless.
    'three.json': document([leaf('cube', 'cube.stl', '#c08040', -60),
                            leaf('sphere', 'sphere.stl', None, 0),
                            leaf('cylinder', 'cylinder.stl', '#40c080', 60)]),
    # R3: a part, and another to light while it is among the others.
    'coloured.json': document([leaf('cube', 'cube.stl', '#c08040'),
                               leaf('other', 'small.stl', '#4080c0', 0, 80)]),
    'colourless.json': document([leaf('cube', 'cube.stl', None),
                                 leaf('other', 'small.stl', '#4080c0', 0, 80)]),
    'inside-out.json': document([leaf('cube', 'inside-out.stl', '#c08040')]),
}

OPTIONS = {'renderMode': 'on-demand', 'animation': 'external', 'autoplay': False,
           'driverControls': 'none', 'partControls': 'none'}

WIDTH, HEIGHT = 321, 241

#: R1's view frames all three parts: three.js uploads a geometry when it
#: first draws it.
THREE_VIEW = {'camera': [0, -260, 140], 'target': [0, 0, 0], 'up': [0, 0, 1], 'fov': 35}
#: The cube seen from +x, -y and +z: three of its faces.
CUBE_VIEW = {'camera': [95, -70, 60], 'target': [0, 0, 0], 'up': [0, 0, 1], 'fov': 35}
#: `test_widget_e2e.py`'s whole marked bench.
BENCH_VIEW = {'camera': [-55.1, 55.1, 55.0], 'target': [0.0, 0.0, 10.0], 'up': [0, 0, 1], 'fov': 35}

#: The faces R3 samples, by their outward normal: the three the cube
#: shows, and the three whose inner sides the inside-out cube shows.
NEAR_FACES = [(1, 0, 0), (0, -1, 0), (0, 0, 1)]
FAR_FACES = [(-1, 0, 0), (0, 1, 0), (0, 0, -1)]

#: The looks R3 puts the cube in, each with the script that makes it and
#: the script that puts it back.
LOOKS = [
    ('plain', '', ''),
    ('lit, the others kept', "window.clear = viewer.highlight([['cube']], {others: 'keep'})", 'clear()'),
    ('lit, the others dimmed', "window.clear = viewer.highlight([['cube']], {others: 'dim'})", 'clear()'),
    ('lit, the others ghosted', "window.clear = viewer.highlight([['cube']], {others: 'ghost'})", 'clear()'),
    ('among the others, kept', "window.clear = viewer.highlight([['other']], {others: 'keep'})", 'clear()'),
    ('among the others, dimmed', "window.clear = viewer.highlight([['other']], {others: 'dim'})", 'clear()'),
    ('among the others, ghosted', "window.clear = viewer.highlight([['other']], {others: 'ghost'})", 'clear()'),
    ('hidden and shown', "viewer.setVisible(['cube'], false); viewer.setVisible(['cube'], true)", ''),
]


def project(view, point):
    """The pixel a point falls on, as three.js's perspective camera of
    ``view`` projects it into the host."""
    eye, target, up = view['camera'], view['target'], view['up']
    z = _sub(eye, target)
    z = [c / math.sqrt(_dot(z, z)) for c in z]
    x = _cross(up, z)
    x = [c / math.sqrt(_dot(x, x)) for c in x]
    y = _cross(z, x)
    d = _sub(point, eye)
    vx, vy, vz = _dot(d, x), _dot(d, y), _dot(d, z)
    f = 1 / math.tan(math.radians(view['fov']) / 2)
    ndc_x = f / (WIDTH / HEIGHT) * vx / -vz
    ndc_y = f * vy / -vz
    return int((ndc_x + 1) / 2 * WIDTH), int((1 - ndc_y) / 2 * HEIGHT)


def face_samples(normal, s=20.0, inset=0.6):
    """Points over the interior of a cube face: a 5 by 5 grid over the
    middle ``inset`` of it."""
    axis = [k for k in range(3) if normal[k]][0]
    others = [k for k in range(3) if k != axis]
    steps = [inset * s * t for t in (-1, -0.5, 0, 0.5, 1)]
    points = []
    for u in steps:
        for v in steps:
            point = [0.0, 0.0, 0.0]
            point[axis] = normal[axis] * s
            point[others[0]], point[others[1]] = u, v
            points.append(point)
    return points


def faces(image, view, normals):
    """Each face's sampled pixels: the mean of each channel, the
    brightness (the sum of the means) and the spread (the widest range of
    one channel over the samples)."""
    measured = []
    for normal in normals:
        pixels = [image.getpixel(project(view, point)) for point in face_samples(normal)]
        means = [sum(pixel[k] for pixel in pixels) / len(pixels) for k in range(3)]
        spread = max(max(pixel[k] for pixel in pixels) - min(pixel[k] for pixel in pixels)
                     for k in range(3))
        measured.append({'means': means, 'brightness': sum(means), 'spread': spread})
    return measured


def ranked(measured):
    """The faces' order from the brightest, and the gaps between them."""
    order = sorted(range(len(measured)), key=lambda i: -measured[i]['brightness'])
    gaps = [measured[order[i]]['brightness'] - measured[order[i + 1]]['brightness']
            for i in range(len(order) - 1)]
    return order, gaps


def strongest(measured):
    return [max(range(3), key=lambda k: face['means'][k]) for face in measured]


#: A face is black when its brightest channel's mean is below this.
BLACK = 24
#: Two faces are of two colours when a channel's means differ by more.
DISTINCT = 8


def pixels(image):
    data = image.tobytes()
    return [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]

# ---------------------------------------------------------------------
# Recorded once, on the bundle built from the base
# (6aee67ef9dc5453ea6ff731f3f692b0f7473fdf0, SHA256
# 0ecadb1e8523bc46d9c289e17367a185d41261096be5fa86df200c7807c4caad),
# before any source change, and never recorded again.

#: R2: the bytes the marked fixture's three markings add at mount (on
#: the base, 49,788 marked against 36,864 unmarked: thirteen buffers
#: against four).
MARKINGS_BYTES = 12924

#: R3: per look of the coloured cube, the faces' order from the
#: brightest (indices into NEAR_FACES), the gaps between them and each
#: face's spread.
_PLAIN = {'order': [2, 0, 1], 'gaps': [52.0, 55.0], 'spread': [0, 0, 0]}
_LIT = {'order': [2, 0, 1], 'gaps': [17.0, 14.0], 'spread': [0, 0, 0]}
COLOURED = {
    'plain': _PLAIN,
    'lit, the others kept': _LIT,
    'lit, the others dimmed': _LIT,
    'lit, the others ghosted': _LIT,
    'among the others, kept': _PLAIN,
    'among the others, dimmed': {'order': [2, 0, 1], 'gaps': [37.0, 32.24], 'spread': [0, 1, 0]},
    'among the others, ghosted': {'order': [2, 0, 1], 'gaps': [8.08, 7.96], 'spread': [0, 1, 1]},
    'hidden and shown': _PLAIN,
}

#: R3: the inside-out cube, plain, over FAR_FACES.
INSIDE_OUT = {'order': [2, 0, 1], 'gaps': [52.0, 55.0], 'spread': [0, 0, 0]}

#: R3: per look of the colourless cube, each face's strongest channel and
#: spread.
_COLOURLESS = {'strongest': [2, 2, 1], 'spread': [0, 0, 0]}
COLOURLESS = {name: _COLOURLESS for name, _, _ in LOOKS}

#: R3: on the marked bench, how many pixels the markings change against
#: the unmarked twin, and what share of them show a marking's own colour
#: (1,165 of 1,309).
MARKED_PIXELS = {'changed': 1309, 'share': 0.89}

#: How far from neutral a pixel may be and still read as a marking's own
#: colour (`#FFFFFF` and `#C0C0C0` are neutral), and how dark before it
#: is a decal drawn black or unlit rather than its colour.
NEUTRAL_SPREAD = 20
MARKING_FLOOR = 60
#: A pixel the markings changed differs from the twin by more than this.
CHANGED = 24


@needs_bundle
@needs_playwright
@needs_pil
class RigidPartNormalsTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='viewer-rigid-normals-')
        self.addCleanup(temp.cleanup)
        stage = Path(temp.name)
        shutil.copy2(bundle_path(), stage / 'viewer.js')
        for name, facets in FACETS.items():
            (stage / name).write_bytes(binary(facets))
        for name, content in DOCUMENTS.items():
            (stage / name).write_text(json.dumps(content))
        shutil.copytree(MARKED, stage / 'marked')
        strip_markings(stage / 'marked' / 'manifest.json', stage / 'marked' / 'unmarked.json')
        (stage / 'index.html').write_text(
            '<html><style>html,body{margin:0}'
            f'#a{{width:{WIDTH}px;height:{HEIGHT}px}}canvas{{display:block}}'
            '.machinome-fullscreen{display:none}</style>'
            '<body><div id="a"></div><script src="viewer.js"></script></body></html>')
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

    # -- the page -----------------------------------------------------

    def page(self):
        page = self.browser.new_page(viewport={'width': 400, 'height': 300})
        self.addCleanup(page.close)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        self.addCleanup(lambda: self.assertEqual(errors, []))
        page.add_init_script(COUNT_BUFFERS)
        page.goto(self.url)
        return page

    def mount(self, page, source, view):
        page.evaluate("""async ([source, options, view]) => {
          if (window.viewer) { window.viewer.dispose(); window.viewer = undefined; }
          window.viewer = await MachinomeViewer.mount('#a', source, options);
          viewer.setView(view);
        }""", [source, {**OPTIONS, 'view': {'camera': view['camera'], 'target': view['target']}}, view])

    def shot(self, page):
        image = Image.open(io.BytesIO(page.locator('#a').screenshot())).convert('RGB')
        self.assertEqual(image.size, (WIDTH, HEIGHT))
        return image

    def looks(self, page, source, view):
        """A picture of the cube in each of R3's looks."""
        self.mount(page, source, view)
        pictures = []
        for name, make, put_back in LOOKS:
            # Statements, never an expression: `evaluate` would call a
            # highlight's returned function and put it back at once.
            page.evaluate(f'(view) => {{ {make}; viewer.setView(view); }}', view)
            pictures.append((name, self.shot(page)))
            page.evaluate(f'(view) => {{ {put_back}; viewer.setView(view); }}', view)
        return pictures

    # -- what is measured ---------------------------------------------

    def measure_buffers(self, page):
        self.mount(page, '/three.json', THREE_VIEW)
        return page.evaluate("buffers('a')")

    def measure_markings_bytes(self):
        """The buffers the marked fixture and its unmarked twin create at
        mount, each in a page of its own."""
        counted = {}
        for name in ('manifest', 'unmarked'):
            page = self.page()
            self.mount(page, f'/marked/{name}.json', BENCH_VIEW)
            counted[name] = page.evaluate("buffers('a')")
        return counted

    def measure_coloured(self, page):
        return [(name, faces(image, CUBE_VIEW, NEAR_FACES))
                for name, image in self.looks(page, '/coloured.json', CUBE_VIEW)]

    def measure_colourless(self, page):
        return [(name, faces(image, CUBE_VIEW, NEAR_FACES))
                for name, image in self.looks(page, '/colourless.json', CUBE_VIEW)]

    def measure_inside_out(self, page):
        self.mount(page, '/inside-out.json', CUBE_VIEW)
        return faces(self.shot(page), CUBE_VIEW, FAR_FACES)

    def measure_marked(self, page, floor):
        """The pixels the markings change against the unmarked twin, and
        how many of them are neutral and at least ``floor`` in their
        darkest channel."""
        images = {}
        for name in ('manifest', 'unmarked'):
            self.mount(page, f'/marked/{name}.json', BENCH_VIEW)
            images[name] = self.shot(page)
        marked, twin = (pixels(images[name]) for name in ('manifest', 'unmarked'))
        changed = [one for one, other in zip(marked, twin)
                   if max(abs(one[k] - other[k]) for k in range(3)) > CHANGED]
        coloured = [pixel for pixel in changed
                    if max(pixel) - min(pixel) <= NEUTRAL_SPREAD and min(pixel) >= floor]
        return {'changed': len(changed), 'coloured': len(coloured),
                'darkest': sorted(min(pixel) for pixel in changed)}

    # -- R1 to R3 -----------------------------------------------------

    def test_r1_a_file_geometry_is_one_buffer_of_positions(self):
        counted = self.measure_buffers(self.page())
        print('R1 mount', counted, flush=True)
        vertices = 3 * sum(len(FACETS[name]) for name in ('cube.stl', 'sphere.stl', 'cylinder.stl'))
        # The stated reason on the base: two buffers a geometry, the
        # positions' and the normals', twice the bytes.
        self.assertEqual(counted['created'], 3)
        self.assertEqual(counted['bytes'], 12 * vertices)
        self.assertEqual(counted['deleted'], 0)

    def test_r2_the_markings_add_the_bytes_they_added(self):
        counted = self.measure_markings_bytes()
        print('R2', counted, flush=True)
        self.assertEqual(counted['manifest']['bytes'] - counted['unmarked']['bytes'], MARKINGS_BYTES)

    def test_r3_a_coloured_part_is_lit_flat_in_every_look(self):
        for name, measured in self.measure_coloured(self.page()):
            recorded = COLOURED[name]
            order, gaps = ranked(measured)
            with self.subTest(look=name):
                print('R3 coloured', name, measured, flush=True)
                self.assert_lit_flat(measured, order, gaps, recorded)

    def test_r3_a_part_wound_inside_out_is_lit_on_its_inner_faces(self):
        measured = self.measure_inside_out(self.page())
        print('R3 inside out', measured, flush=True)
        order, gaps = ranked(measured)
        self.assert_lit_flat(measured, order, gaps, INSIDE_OUT)

    def test_r3_a_colourless_part_shows_three_flat_faces_of_three_colours(self):
        for name, measured in self.measure_colourless(self.page()):
            recorded = COLOURLESS[name]
            with self.subTest(look=name):
                print('R3 colourless', name, measured, flush=True)
                self.assertEqual(strongest(measured), recorded['strongest'])
                for one in range(3):
                    for other in range(one + 1, 3):
                        self.assertGreater(
                            max(abs(a - b) for a, b in zip(measured[one]['means'],
                                                           measured[other]['means'])),
                            DISTINCT, 'two faces of one colour')
                for face, spread in zip(measured, recorded['spread']):
                    self.assertGreaterEqual(max(face['means']), BLACK, 'a face drawn black')
                    self.assertLessEqual(face['spread'], spread + 1, 'a face not flat')

    def test_r3_a_marking_shows_its_own_colour_over_its_part(self):
        measured = self.measure_marked(self.page(), MARKING_FLOOR)
        print('R3 marked', {key: value for key, value in measured.items() if key != 'darkest'},
              flush=True)
        self.assertGreaterEqual(measured['changed'], MARKED_PIXELS['changed'] // 2,
                                'the markings were not drawn')
        self.assertGreaterEqual(measured['coloured'] / measured['changed'],
                                MARKED_PIXELS['share'] - 0.05,
                                'the markings are not drawn in their own colours')

    def assert_lit_flat(self, measured, order, gaps, recorded):
        for face, spread in zip(measured, recorded['spread']):
            self.assertGreaterEqual(max(face['means']), BLACK, 'a face drawn black')
            self.assertLessEqual(face['spread'], spread + 1, 'a face not flat')
        self.assertEqual(order, recorded['order'], 'the faces lit in another order')
        for gap, was in zip(gaps, recorded['gaps']):
            self.assertGreaterEqual(gap, was / 2, 'two faces lit nearly alike')


if __name__ == '__main__':
    unittest.main()
