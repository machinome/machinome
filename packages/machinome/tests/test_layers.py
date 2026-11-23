# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A part's layers (OpenSpec change `declare-a-parts-layers`, capability
`layers`, design Decision 9).

The originating project is `projects/enigma-i`: its maker is to define the
electrical path and the parts that move the rotors once each, declare them
on whole subsystems, and have its page show one layer at a time. The
fixture is `tests/layers_project/`, a small clocked machine.

F1-F3 the layer and the declaration; P1-P4 the published document; P5 an
untagged model is byte-identical to the one published before layers
existed; P6 a tagged model differs from its untagged twin only by what
layers add; P7 every producer publishes the same layers; X1 the exported
page, in a real browser, shows one layer through its own app.

Tests that build do so in a temporary copy of the fixture project, never in
the committed tree; the document tests go through `serialize_node` and
`document_body` as `test_state_color.py` does.
"""

import asyncio
import dataclasses
import hashlib
import http.server
import json
import os
import re
import shutil
import tempfile
import threading
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from unittest import TestCase, skipIf, skipUnless

TESTS = Path(__file__).resolve().parent
FIXTURE = TESTS / 'layers_project'

#: The SHA-256 of `untagged.py:Layered`'s `viewer.json` as the base
#: `cc2e661a` published it, each `"mtime": <seconds>` written `"mtime": 0`: a
#: source file's modification time is a property of the checkout, not of the
#: document. Recorded before any source change, in `evidence.md`.
UNTAGGED_SHA256 = (
    'c9ea090d4ecf846a1cabd862b867a2dab3b81913bef624db435da4cc32cec267')

ELECTRICAL = {'key': 'electrical', 'label': 'Electrical path'}
MECHANICAL = {'key': 'mechanical', 'label': 'Rotor stepping'}

#: `machinome.viewer.web.capture.Capture.launch`'s arguments.
CHROMIUM_ARGS = ['--use-gl=angle', '--use-angle=swiftshader',
                 '--enable-unsafe-swiftshader']

#: How long a page may take to draw.
BOUND = 90.0


def document(node):
    """The document a producer publishes for `node`, as `test_state_color`
    builds it: `serialize_node`, then `document_body`."""
    from machinome.core.serializer import (
        compiled_clocked, compiled_controls, compiled_program, document_body,
        drivers_table, instructions_table, serialize_node, symbolic_document,
    )

    program, initial = compiled_program(node)
    clocked, clocked_initial = compiled_clocked(node)
    if clocked is not None:
        initial = clocked_initial
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda leaf: leaf.local_stl,
                              graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(
            instructions,
            version_five_or_above=program is not None or clocked is not None)
    result = document_body(node, root, drivers, events, program, initial,
                           controls=compiled_controls(program, initial),
                           clocked=clocked)
    result['root'] = root
    return result


def entries(root, prefix=''):
    """`{path: entry}` for every node entry under `root`, the root's own
    path being its name."""
    path = f'{prefix}{root["name"]}'
    found = {path: root}
    for child in root.get('children', ()):
        found.update(entries(child, f'{path}/'))
    return found


def keys_by_path(root):
    return {path: entry['layers'] for path, entry in entries(root).items()
            if 'layers' in entry}


def without_layers(value):
    """`value` with every `layers` key, at the top and on every node, taken
    out."""
    if isinstance(value, dict):
        return {key: without_layers(item) for key, item in value.items()
                if key != 'layers'}
    if isinstance(value, list):
        return [without_layers(item) for item in value]
    return value


def mentions_layers(value):
    if isinstance(value, dict):
        return any(key == 'layers' or mentions_layers(item)
                   for key, item in value.items())
    if isinstance(value, list):
        return any(mentions_layers(item) for item in value)
    return False


def normalized_sha256(data):
    return hashlib.sha256(
        re.sub(rb'"mtime": [0-9.e+-]+', b'"mtime": 0', data)).hexdigest()


needs_openscad = skipUnless(
    shutil.which('openscad'),
    "the fixture's parts are Solid2Node leaves, rendered by OpenSCAD, and "
    'no openscad is on the PATH')


def _toolchain_refusal():
    """Why the web viewer cannot bundle an app here, or None."""
    try:
        from machinome.viewer.web.app import refusal
    except ImportError as error:
        return f'the web viewer is not importable ({error})'
    return refusal()


TOOLCHAIN = _toolchain_refusal()
needs_toolchain = skipIf(
    TOOLCHAIN is not None,
    f"bundling an app needs the web viewer's toolchain: {TOOLCHAIN}")


def _playwright_refusal():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return 'playwright is not installed'
    try:
        with sync_playwright() as playwright:
            if not os.path.exists(playwright.chromium.executable_path):
                return "playwright's Chromium is not installed"
    except Exception as error:  # pragma: no cover - environment
        return f'Chromium cannot be found ({error})'
    return None


# -- F: the layer and the declaration ------------------------------------------


class LayerTest(TestCase):

    def test_f1_a_layer_reads_its_key_and_label_and_never_changes(self):
        from machinome.layers import Layer

        layer = Layer('electrical', label='Electrical path')
        self.assertEqual((layer.key, layer.label),
                         ('electrical', 'Electrical path'))
        self.assertEqual(repr(layer),
                         "Layer('electrical', label='Electrical path')")
        for name in ('key', 'label'):
            with self.subTest(assign=name):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(layer, name, 'x')

    def test_f1_a_layer_is_equal_only_to_itself(self):
        from machinome.layers import Layer

        layer = Layer('electrical', label='Electrical path')
        twin = Layer('electrical', label='Electrical path')
        self.assertEqual(layer, layer)
        self.assertNotEqual(layer, twin)
        self.assertEqual(len({layer, twin, layer}), 2)

    def test_f1_an_argument_that_is_not_a_non_empty_string_is_refused(self):
        from machinome.layers import Layer

        for call, argument in [
                (lambda: Layer('', label='x'), 'key'),
                (lambda: Layer(3, label='x'), 'key'),
                (lambda: Layer(None, label='x'), 'key'),
                (lambda: Layer('e', label=''), 'label'),
                (lambda: Layer('e', label=3), 'label'),
                (lambda: Layer('e'), 'label'),
                (lambda: Layer('e', 'x'), 'positional'),
                (lambda: Layer(label='x'), 'key')]:
            with self.subTest(argument=argument):
                with self.assertRaisesRegex(TypeError, argument):
                    call()

    def test_f1_the_refusal_says_what_was_given(self):
        from machinome.layers import Layer

        with self.assertRaisesRegex(
                TypeError, r"Layer key must be a non-empty string, not 3"):
            Layer(3, label='x')


class DeclarationTest(TestCase):

    def refuse(self, value):
        from machinome.node.solid2 import Solid2Node

        with self.assertRaises(TypeError) as raised:
            class Contact(Solid2Node):
                layers = value
        return str(raised.exception)

    def test_f2_a_value_that_is_not_one_layer_or_a_tuple_of_them(self):
        from machinome.node.solid2 import Solid2Node
        from tests.layers_project.layers import ELECTRICAL as LAYER

        class Leaf(Solid2Node):
            pass

        for value in ('electrical', [LAYER], (), (LAYER, 'x'), 3, None,
                      {LAYER}, Leaf()):
            with self.subTest(value=value):
                message = self.refuse(value)
                self.assertIn('Contact.layers', message)
                self.assertIn('Layer', message)
                self.assertIn('reserved', message)

    def test_f2_the_refusal_quotes_the_value_written(self):
        self.assertIn("Contact.layers is 'electrical'",
                      self.refuse('electrical'))

    def test_f2_a_repeated_layer_is_refused_naming_it(self):
        from tests.layers_project.layers import ELECTRICAL as LAYER

        message = self.refuse((LAYER, LAYER))
        self.assertIn('Contact.layers', message)
        self.assertIn(repr(LAYER), message)
        self.assertIn('twice', message)

    def test_f2_a_parameter_named_layers_is_refused(self):
        from machinome.node.solid2 import Solid2Node
        from machinome.parameters import Length

        with self.assertRaisesRegex(TypeError, 'Contact.layers'):
            class Contact(Solid2Node):
                layers = Length(3.0, min=0)

    def test_f2_the_accepted_forms(self):
        from machinome.node.solid2 import Solid2Node
        from tests.layers_project.layers import ELECTRICAL, MECHANICAL

        class One(Solid2Node):
            layers = ELECTRICAL

        class Two(Solid2Node):
            layers = (ELECTRICAL, MECHANICAL)

        self.assertEqual(One._declared_layers, (ELECTRICAL,))
        self.assertEqual(Two._declared_layers, (ELECTRICAL, MECHANICAL))

    def test_f3_a_class_that_declares_none_declares_none(self):
        from machinome.node.base import AbstractBaseNode
        from machinome.node.solid2 import Solid2Node
        from tests.layers_project.machine import Case

        self.assertEqual(AbstractBaseNode._declared_layers, ())
        self.assertEqual(Solid2Node._declared_layers, ())
        self.assertEqual(Case._declared_layers, ())

    def test_f3_a_subclass_and_a_mixin_add_to_what_they_inherit(self):
        from tests.layers_project import inherit
        from tests.layers_project.layers import ELECTRICAL, MECHANICAL

        self.assertEqual(inherit.Base._declared_layers, (ELECTRICAL,))
        self.assertEqual(inherit.Derived._declared_layers,
                         (ELECTRICAL, MECHANICAL))
        # A plain mixin that is not a node.
        self.assertEqual(inherit.Plain._declared_layers, (ELECTRICAL,))
        self.assertEqual(inherit.Mixed._declared_layers,
                         (ELECTRICAL, MECHANICAL))

    def test_f3_a_layer_declared_again_below_is_on_the_list_once(self):
        from tests.layers_project import inherit
        from tests.layers_project.layers import ELECTRICAL

        class Again(inherit.Base):
            layers = ELECTRICAL

        self.assertEqual(Again._declared_layers, (ELECTRICAL,))

    def test_f3_a_mixin_whose_layers_are_not_layers_is_refused_naming_both(self):
        from machinome.node.solid2 import Solid2Node

        class Copper:
            layers = 'x'

        with self.assertRaises(TypeError) as raised:
            class Contact(Copper, Solid2Node):
                pass
        message = str(raised.exception)
        self.assertIn('Contact', message)
        self.assertIn('Copper', message)
        self.assertIn("'x'", message)

    def test_f3_a_subclass_of_a_declared_class_is_still_checked(self):
        from tests.layers_project import inherit

        with self.assertRaisesRegex(TypeError, 'Worse.layers'):
            class Worse(inherit.Base):
                layers = 'x'


# -- P: the published document ----------------------------------------------


class PublicationTest(TestCase):

    def test_p1_the_table_and_each_node_s_declared_keys(self):
        from tests.layers_project.machine import Layered

        published = document(Layered())
        self.assertEqual(published['layers'], [ELECTRICAL, MECHANICAL])
        self.assertEqual(keys_by_path(published['root']), {
            'Layered/circuit': ['electrical'],
            'Layered/circuit/lamp': ['mechanical'],
            'Layered/lever': ['mechanical'],
            'Layered/key': ['electrical', 'mechanical'],
        })
        found = entries(published['root'])
        for path in ('Layered', 'Layered/case', 'Layered/circuit/wire'):
            self.assertNotIn('layers', found[path], path)

    def test_p1_the_table_is_in_the_order_a_walk_first_meets_a_layer(self):
        from tests.layers_project import machine

        # `lever` first, then `key`: mechanical is met before electrical.
        class Swapped(machine.Bare):
            def render(self):
                self.circuit.omit()
                self.spare.omit()

        published = document(Swapped())
        self.assertEqual(published['layers'], [MECHANICAL, ELECTRICAL])

    def test_p1_the_table_sits_between_the_instructions_and_the_bindings(self):
        from tests.layers_project.machine import Layered

        keys = list(document(Layered()))
        self.assertEqual(keys.index('layers'), keys.index('instructions') + 1)

    def test_p1_a_layer_declared_by_a_subclass_is_on_the_node(self):
        from tests.layers_project import inherit
        from machinome.node.assembly import AssemblyNode

        class Holder(AssemblyNode):
            derived = inherit.Derived()
            plain = inherit.Plain()

        published = document(Holder())
        self.assertEqual(keys_by_path(published['root']), {
            'Holder/derived': ['electrical', 'mechanical'],
            'Holder/plain': ['electrical'],
        })
        self.assertEqual(published['layers'], [ELECTRICAL, MECHANICAL])

    def test_p1_a_node_s_keys_are_in_the_order_its_classes_declare_them(self):
        from tests.layers_project import order
        from machinome.node.assembly import AssemblyNode

        class Holder(AssemblyNode):
            pair = order.Pair()
            topped = order.Topped()

        published = document(Holder())
        # Not alphabetical: written (mechanical, electrical) on one class,
        # and mechanical on the base before electrical on the subclass.
        self.assertEqual(keys_by_path(published['root']), {
            'Holder/pair': ['mechanical', 'electrical'],
            'Holder/topped': ['mechanical', 'electrical'],
        })

    def test_p2_a_part_fused_into_another_contributes_nothing(self):
        from tests.layers_project.machine import Layered

        published = document(Layered())
        found = entries(published['root'])
        self.assertIn('Layered/cover', found)
        self.assertNotIn('layers', found['Layered/cover'])
        self.assertFalse([path for path in found if '/cover/' in path])
        # The only entries on the electrical layer are the circuit and the
        # key, never the fused part.
        self.assertEqual(
            sorted(path for path, keys in keys_by_path(
                published['root']).items() if 'electrical' in keys),
            ['Layered/circuit', 'Layered/key'])

    def test_p2_an_omitted_child_s_layer_is_not_in_the_table(self):
        from tests.layers_project.machine import Layered

        published = document(Layered())
        self.assertNotIn('spare', [one['key'] for one in published['layers']])
        self.assertNotIn('Layered/spare', entries(published['root']))

    def test_p3_two_layers_of_one_key_are_refused_naming_both_paths(self):
        from tests.layers_project.conflict import Conflicted

        with self.assertRaises(ValueError) as raised:
            document(Conflicted())
        self.assertEqual(
            str(raised.exception),
            "two different layers share the key 'electrical': "
            "Layer('electrical', label='Electrical path') on "
            "Conflicted/first and Layer('electrical', label='Wires') on "
            "Conflicted/second; define a layer once and import it where it "
            "is declared")

    def test_p3_a_second_layer_with_an_equal_label_is_still_a_second_layer(
            self):
        from tests.layers_project.conflict import Twinned

        with self.assertRaisesRegex(
                ValueError, r"share the key 'electrical'.*Twinned/first.*"
                            r"Twinned/twin"):
            document(Twinned())

    def test_p3_the_same_layer_in_two_places_is_one_layer(self):
        from machinome.node.assembly import AssemblyNode
        from tests.layers_project.conflict import First

        class Both(AssemblyNode):
            first = First()
            second = First()

        published = document(Both())
        self.assertEqual(published['layers'], [ELECTRICAL])

    def test_p3_two_machines_may_each_define_a_layer_of_one_key(self):
        from tests.layers_project.conflict import Elsewhere, Separate

        self.assertEqual(document(Separate())['layers'], [ELECTRICAL])
        self.assertEqual(document(Elsewhere())['layers'],
                         [{'key': 'electrical', 'label': 'Wires'}])

    def test_p4_a_layer_assigned_on_an_instance_is_refused_naming_the_node(
            self):
        from tests.layers_project.instance import Assigned

        with self.assertRaises(TypeError) as raised:
            document(Assigned())
        self.assertEqual(
            str(raised.exception),
            "Assigned/contact (Assigning) assigns layers on the instance; "
            "a node's layers are declared in its class body")

    def test_p6_a_tagged_model_differs_from_its_twin_only_by_layers(self):
        from tests.layers_project.machine import Layered
        from tests.layers_project.untagged import Layered as Untagged

        tagged = document(Layered())
        untagged = document(Untagged())
        self.assertEqual(tagged['version'], untagged['version'])
        self.assertTrue(mentions_layers(tagged))
        self.assertFalse(mentions_layers(untagged))

        def shape(published):
            # What names the module that wrote the classes, or the file's
            # modification time, is no part of the machine.
            text = json.dumps(without_layers(published))
            text = re.sub(r'"(?:machine|untagged)-', '"m-', text)
            text = re.sub(r'"mtime": [0-9.e+-]+', '"mtime": 0', text)
            text = re.sub(r'"identity": "[0-9a-f]{64}"', '"identity": "x"',
                          text)
            return json.loads(text)

        self.assertEqual(shape(tagged), shape(untagged))


# -- P5, P7: the producers -----------------------------------------------------


class _Scratch(TestCase):
    """A temporary copy of the fixture project, `<base>/proj/layers_project/`,
    with its manifest."""

    def setUp(self):
        super().setUp()
        temporary = tempfile.mkdtemp(prefix='layers-')
        self.addCleanup(shutil.rmtree, temporary, ignore_errors=True)
        self.base = Path(os.path.realpath(temporary))
        self.project = self.base / 'proj'
        shutil.copytree(FIXTURE, self.project / 'layers_project',
                        ignore=shutil.ignore_patterns('__pycache__'))
        (self.project / 'pyproject.toml').write_text(
            '[tool.machinome]\n'
            'model = "layers_project.machine:Bare"\n')
        self.build_dir = self.project / '_build'
        present = 'SOLID_BUILD_DIR' in os.environ
        previous = os.environ.get('SOLID_BUILD_DIR')

        def restore():
            if present:
                os.environ['SOLID_BUILD_DIR'] = previous
            else:
                os.environ.pop('SOLID_BUILD_DIR', None)
        self.addCleanup(restore)

    def reference(self, module, name):
        return f'{self.project}/layers_project/{module}.py:{name}'

    def build(self, module, name):
        from machinome.core.builder import Builder
        builder = Builder(self.reference(module, name),
                          build_dir=str(self.build_dir), watch=False)
        return asyncio.run(builder._start())

    def published(self):
        return (self.build_dir / 'viewer.json').read_bytes()

    def load(self, module, name):
        from machinome.core.loader import load_node
        os.environ['SOLID_BUILD_DIR'] = str(self.build_dir)
        return load_node(self.reference(module, name))


@needs_openscad
class UntaggedTest(_Scratch):

    def test_p5_an_untagged_model_s_document_is_the_one_the_base_published(
            self):
        from machinome.core.builder import BuildOutcome

        self.assertEqual(self.build('untagged', 'Layered'),
                         BuildOutcome.CURRENT)
        published = self.published()
        self.assertFalse(mentions_layers(json.loads(published)))
        self.assertEqual(normalized_sha256(published), UNTAGGED_SHA256)


@needs_openscad
class ProducersTest(_Scratch):

    def test_p7_the_build_and_the_export_publish_the_same_layers(self):
        from machinome.core.builder import BuildOutcome
        from machinome.core.export import export_node

        self.assertEqual(self.build('machine', 'Bare'), BuildOutcome.CURRENT)
        built = json.loads(self.published())
        output = self.base / 'export'
        node = self.load('machine', 'Bare')
        export_node(node, str(output), widget=False)
        exported = json.loads((output / 'manifest.json').read_text())

        self.assertEqual(built['layers'], [ELECTRICAL, MECHANICAL])
        self.assertEqual(exported['layers'], built['layers'])
        self.assertEqual(keys_by_path(exported['root']),
                         keys_by_path(built['root']))
        self.assertEqual(keys_by_path(built['root'])['Bare/key'],
                         ['electrical', 'mechanical'])

    def test_p7_the_capture_staging_publishes_them_too(self):
        try:
            from machinome.viewer.web.stage import remove_stage, stage
            from machinome.viewer.web import bundle
        except ImportError as error:
            self.skipTest(f'the web viewer is not importable ({error})')
        if not bundle.has_bundle():
            self.skipTest("the web viewer's bundle is not built")

        self.build('machine', 'Bare')
        built = json.loads(self.published())
        node = self.load('machine', 'Bare')
        staging = stage(node, str(self.build_dir))
        try:
            staged = json.loads(
                (Path(staging) / 'viewer.json').read_text())
        finally:
            remove_stage(staging)
        self.assertEqual(staged['layers'], built['layers'])
        self.assertEqual(keys_by_path(staged['root']),
                         keys_by_path(built['root']))


# -- X1: the page in a real browser ---------------------------------------------


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *arguments):
        pass


@contextmanager
def serving(directory):
    server = http.server.ThreadingHTTPServer(
        ('127.0.0.1', 0), partial(_Quiet, directory=str(directory)))
    assert server.server_address[1] != 9010
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


#: The export directory's own page does not keep the handle; this one
#: mounts the manifest through the viewer's bundle (which starts the model's
#: app) and keeps the handle, as the viewer's own browser tests do.
HARNESS_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>layers harness</title>
    <style>
      html, body { margin: 0; height: 100%; background: #101418; }
      #host { width: 800px; height: 600px; }
    </style>
  </head>
  <body>
    <div id="host"></div>
    <script src="machinome-viewer.js"></script>
    <script>
      MachinomeViewer.mount(document.getElementById('host'), 'manifest.json',
                            {}).then((viewer) => { window.viewer = viewer; });
    </script>
  </body>
</html>
"""


@needs_openscad
@needs_toolchain
class PageTest(_Scratch):

    def setUp(self):
        super().setUp()
        refusal = _playwright_refusal()
        if refusal is not None:
            self.skipTest(refusal)
        self.errors = []

    @contextmanager
    def browsing(self):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=CHROMIUM_ARGS)
            try:
                page = browser.new_page(viewport={'width': 1000,
                                                  'height': 700})
                page.set_default_timeout(int(BOUND * 1000))
                page.on('pageerror',
                        lambda error: self.errors.append(str(error)))
                page.on('console', lambda message: self.errors.append(
                    message.text) if message.type == 'error' else None)
                yield page
            finally:
                browser.close()

    def test_x1_the_exported_page_shows_one_layer_through_its_own_app(self):
        from machinome.core.export import export_node

        output = self.base / 'export'
        node = self.load('machine', 'Layered')
        manifest = export_node(node, str(output))
        self.assertEqual(manifest['layers'], [ELECTRICAL, MECHANICAL])
        self.assertIn('app', manifest)
        (output / 'harness.html').write_text(HARNESS_PAGE)

        def on_screen(page, path):
            return page.evaluate(
                '(path) => window.viewer.partOnScreen(path) !== null', path)

        with serving(output) as base, self.browsing() as page:
            page.goto(f'{base}/harness.html')
            page.wait_for_selector('.layers-app .layers-app-button')
            page.wait_for_function('() => window.viewer !== undefined')
            # One button per layer, then the whole machine's.
            self.assertEqual(page.evaluate("""() => [...document
              .querySelectorAll('.layers-app-button')].map(
                (button) => button.textContent)"""),
                ['Whole machine', 'Electrical path', 'Rotor stepping'])
            page.wait_for_function(
                '() => window.viewer.partOnScreen(["case"]) !== null')
            for path in (['case'], ['lever'], ['circuit', 'wire'], ['key']):
                self.assertTrue(on_screen(page, path), path)

            page.click('.layers-app-button[data-layer="electrical"]')
            self.assertFalse(on_screen(page, ['case']))
            self.assertFalse(on_screen(page, ['lever']))
            self.assertTrue(on_screen(page, ['circuit', 'wire']))
            self.assertTrue(on_screen(page, ['key']))
            self.assertEqual(page.evaluate(
                'window.viewer.navigation().layer'), ELECTRICAL)

            page.click('.layers-app-button[data-layer=""]')
            self.assertTrue(on_screen(page, ['case']))
            self.assertTrue(on_screen(page, ['lever']))
            self.assertIsNone(page.evaluate(
                'window.viewer.navigation().layer'))
        self.assertEqual(self.errors, [])
