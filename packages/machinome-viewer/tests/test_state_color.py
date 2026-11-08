# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Standard-produced documents, ordinary controls, and the real shipped bundle."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from unittest import TestCase

from machinome.viewer.web.bundle import bundle_path
from machinome.viewer.web.capture import Capture, carries_clocked, carries_program, mount_options
from .support import needs_bundle, needs_playwright, needs_pil, serve_directory
from .test_widget_e2e import HARNESS_PAGE

FIXTURE = Path(__file__).parent / 'fixtures' / 'state-color'
SHOTS = Path(__file__).parent / '_shots' / 'state-color'
RECEIPT = json.loads((FIXTURE / 'receipt.json').read_text())
OFF, ON = (RECEIPT['expected'][name] for name in ('off', 'on'))


class ColorFixtureTest(TestCase):
    def test_standard_exports_and_models_match_the_producer_receipt(self):
        for name, expected in RECEIPT['documents'].items():
            with self.subTest(name=name):
                root = FIXTURE / name
                raw = (root / 'manifest.json').read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), expected['sha256'])
                document = json.loads(raw)
                self.assertEqual(document['version'], 14)
                for model, digest in expected['models'].items():
                    self.assertEqual(sha256((root / model).read_bytes()).hexdigest(), digest)

    def test_execution_kind_is_selected_by_payload_for_version_fourteen(self):
        for name in RECEIPT['documents']:
            document = json.loads((FIXTURE / name / 'manifest.json').read_text())
            self.assertEqual(carries_clocked(document), name in (
                'clocked', 'invalid-clocked', 'clocked-state', 'publication-safe', 'publication-unsafe'))
            self.assertEqual(carries_program(document), name == 'running')


@needs_bundle
@needs_playwright
@needs_pil
class ModelColorBrowserTest(TestCase):
    def setUp(self):
        from playwright.sync_api import sync_playwright
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        shutil.copytree(FIXTURE, root / 'fixture')
        shutil.copy2(bundle_path(), root / 'machinome-viewer.js')
        (root / 'harness.html').write_text(HARNESS_PAGE)
        server = serve_directory(root)
        self.url = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        pw = sync_playwright().start()
        self.addCleanup(pw.stop)
        self.browser = pw.chromium.launch(args=['--no-sandbox', '--use-angle=swiftshader'])
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page(viewport={'width': 800, 'height': 600})
        self.errors, self.assets = [], []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('request', lambda r: self.assets.append(r.url) if '.stl' in r.url else None)
        self.page.goto(self.url + '/harness.html')
        SHOTS.mkdir(parents=True, exist_ok=True)

    def mount(self, name, controls=False):
        self.page.evaluate("""async ({name,controls}) => {
          if (window.viewer) viewer.dispose();
          window.viewer = await MachinomeViewer.mount('#host', `fixture/${name}/manifest.json`, {
            animation:'external', autoplay:false, partControls:'none',
            driverControls:controls ? 'inline' : 'none',
            ...(name==='running' ? {run:{autostart:false,dt:0.1}} : controls ? {} : {renderMode:'on-demand'}) });
          viewer.setView({camera:[30,-50,40],target:[0,0,0]});
          window.colors = () => viewer.assembly().children.map(node=>node.color);
        }""", {'name': name, 'controls': controls})

    def shot(self, name=None):
        return self.page.locator('canvas').screenshot(
            path=str(SHOTS / f'{name}.png') if name else None,
            style='.driver-controls,.clocked-controls,.run-controls { visibility:hidden !important; }')

    def assert_changed(self, before, after):
        import io
        from PIL import Image, ImageChops
        a, b = (Image.open(io.BytesIO(raw)).convert('RGB') for raw in (before, after))
        diff = ImageChops.difference(a, b)
        self.assertIsNotNone(diff.getbbox(), 'declared color changed but no canvas pixels changed')
        self.assertGreater(sum(max(pixel) > 4 for pixel in diff.getdata()), 100)

    def test_ordinary_slider_default_overlay_and_reload_use_the_same_glass(self):
        page = self.page
        self.mount('posed', controls=True)
        self.assertIsNone(page.evaluate('viewer.run()'))
        self.assertIsNone(page.evaluate('viewer.machine()'))
        before_requests = len(self.assets)
        self.assertEqual(page.evaluate('colors()'), [OFF])
        dark = self.shot('posed-dark')
        slider = page.get_by_role('slider', name='powered', exact=True)
        slider.fill('1'); slider.dispatch_event('input')
        self.assertEqual(page.evaluate('colors()'), [ON])
        lit = self.shot('posed-lit'); self.assert_changed(dark, lit)
        page.evaluate("window.clearHighlight=viewer.highlight([['glass']],{color:'#00ff00'})")
        slider.fill('0'); slider.dispatch_event('input')
        page.evaluate('clearHighlight()')
        self.assertEqual(page.evaluate('colors()'), [OFF])
        self.assertEqual(self.shot('posed-released'), dark)
        self.assertEqual(len(self.assets), before_requests)
        page.evaluate("window.clearHighlight=viewer.highlight([['glass']],{color:'#00ff00'})")
        slider.fill('1'); slider.dispatch_event('input')
        page.evaluate('clearHighlight()')
        self.assertEqual(self.shot(), lit)
        page.evaluate('viewer.reload()')
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(self.shot(), lit)
        model = json.loads((FIXTURE / 'posed/manifest.json').read_text())['root']['children'][0]['model']
        page.evaluate('path=>viewer.artifactChanged(path)', model)
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(self.shot(), lit)
        self.mount('powered', controls=True)
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(self.shot('powered-first-frame'), lit)
        self.assertEqual(self.errors, [])


    def test_clocked_snapshot_reset_restore_replay_and_event_parity(self):
        self.mount('clocked')
        page = self.page
        dark = self.shot('clocked-dark')
        before_requests = len(self.assets)
        answer = page.evaluate("""() => {
          window.machine=viewer.machine(); window.origin=machine.snapshot();
          const answer=machine.move('powered',{to:1}); window.saved=machine.snapshot();
          return {answer,bank:machine.state(),colors:colors()};
        }""")
        self.assertEqual(answer['colors'], [ON]); self.assertEqual(answer['bank']['count'], 1)
        lit = self.shot('clocked-lit'); self.assert_changed(dark, lit)
        page.evaluate("machine.move('powered',{to:0})")
        self.assertEqual(self.shot(), dark)
        page.evaluate('machine.restore(saved)')
        self.assertEqual(self.shot(), lit)
        page.evaluate('machine.reset()')
        self.assertEqual(page.evaluate('colors()'), [OFF]); self.assertEqual(self.shot(), dark)
        page.evaluate("machine.restore(origin);machine.move('powered',{to:1})")
        self.assertEqual(self.shot('clocked-replayed'), lit)
        self.assertEqual(page.evaluate('machine.state().count'), 1)
        self.assertEqual(len(self.assets), before_requests); self.assertEqual(self.errors, [])

    def test_invalid_clocked_color_keeps_bank_events_and_pixels_then_recovers(self):
        self.mount('invalid-clocked')
        page = self.page
        origin = page.evaluate('window.machine=viewer.machine(); machine.snapshot()')
        colors = page.evaluate('colors()'); dark = self.shot('invalid-standing')
        for operation in ["machine.move('powered',{to:3})",
                          "machine.restore({...machine.snapshot(),bank:{...machine.state(),powered:3,count:9}})"]:
            answer = page.evaluate("""operation=>{
              let error=null;try{eval(operation)}catch(e){error=e.message}
              viewer.setView(viewer.view());
              return {error,snapshot:machine.snapshot(),colors:colors()};
            }""", operation)
            self.assertRegex(answer['error'], 'later.*color')
            self.assertEqual(answer['snapshot'], origin); self.assertEqual(answer['colors'], colors)
            self.assertEqual(self.shot(), dark)
        page.evaluate("machine.move('independent',{to:4})")
        self.assertEqual(page.evaluate('machine.state()'), {'powered': 0, 'independent': 4, 'count': 0})
        page.evaluate("machine.move('powered',{to:1})")
        self.assertEqual(page.evaluate('machine.state().count'), 1)
        self.assertEqual(page.evaluate('colors()[0]'), ON)
        self.shot('invalid-recovered'); self.assertEqual(self.errors, [])

    def test_running_committed_frames_restore_reset_and_replay(self):
        self.mount('running')
        page = self.page
        self.assertIsNone(page.evaluate('viewer.machine()'))
        dark = self.shot('running-dark'); before_requests = len(self.assets)
        page.evaluate("""async()=>{
          window.run=viewer.run(); window.origin=await run.snapshot();
          const settled=run.move('powered',{to:1,duration:0.1});
          await run.step(1); await settled; window.saved=await run.snapshot();
        }""")
        self.assertEqual(page.evaluate('colors()'), [ON])
        lit = self.shot('running-lit'); self.assert_changed(dark, lit)
        page.evaluate('run.reset()')
        self.assertEqual(page.evaluate('colors()'), [OFF]); self.assertEqual(self.shot(), dark)
        page.evaluate('run.restore(saved)')
        self.assertEqual(self.shot(), lit)
        page.evaluate("""async()=>{
          await run.restore(origin); const settled=run.move('powered',{to:1,duration:0.1});
          await run.step(1); await settled;
        }""")
        self.assertEqual(self.shot('running-replayed'), lit)
        self.assertEqual(len(self.assets), before_requests); self.assertEqual(self.errors, [])

    def test_invalid_standard_republish_keeps_the_standing_color_and_highlight(self):
        self.mount('publication-safe')
        page = self.page
        page.evaluate("""()=>{
          window.machine=viewer.machine();machine.move('powered',{to:3});
          window.clearHighlight=viewer.highlight([['glass']],{color:'#00ff00'});
        }""")
        before = self.shot('republish-standing')
        snapshot = page.evaluate('machine.snapshot()')
        # Serve another unchanged standard-produced document as a new publication.
        page.route('**/fixture/publication-safe/manifest.json', lambda route: route.fulfill(
            path=FIXTURE / 'publication-unsafe' / 'manifest.json', content_type='application/json'))
        error = page.evaluate("""async()=>{
          try{await viewer.manifestChanged();return null}catch(e){return e.message}
        }""")
        self.assertRegex(error, 'glass.*color')
        self.assertEqual(page.evaluate('machine.snapshot()'), snapshot)
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(self.shot('republish-refused'), before)
        page.evaluate('clearHighlight()')
        self.assertEqual(page.evaluate('colors()'), [ON])
        page.evaluate("machine.move('powered',{to:0})")
        self.assertEqual(page.evaluate('colors()'), [OFF])
        self.assertEqual(self.errors, [])

    def test_new_clocked_identity_uses_its_incoming_initial_bank(self):
        self.mount('clocked')
        page = self.page
        page.evaluate("viewer.machine().move('powered',{to:3})")
        page.route('**/fixture/clocked/manifest.json', lambda route: route.fulfill(
            path=FIXTURE / 'invalid-clocked' / 'manifest.json', content_type='application/json'))
        page.evaluate('viewer.manifestChanged()')
        self.assertEqual(page.evaluate('viewer.machine().state()'),
                         {'powered': 0, 'independent': 0, 'count': 0})
        self.assertEqual(page.evaluate('colors()'), [OFF, ON])
        self.assertEqual(self.errors, [])

    def test_posed_publication_can_admit_an_incoming_clocked_machine(self):
        self.mount('posed')
        page = self.page
        page.route('**/fixture/posed/manifest.json', lambda route: route.fulfill(
            path=FIXTURE / 'clocked-state' / 'manifest.json', content_type='application/json'))
        page.evaluate('viewer.manifestChanged()')
        self.assertIsNotNone(page.evaluate('viewer.machine()'))
        page.evaluate("viewer.machine().move('powered',{to:1})")
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(page.evaluate('viewer.machine().state().count'), 1)
        self.assertEqual(self.errors, [])

    def test_same_clocked_identity_keeps_the_state_selected_color(self):
        self.mount('clocked-state')
        page = self.page
        page.evaluate("viewer.machine().move('powered',{to:1})")
        snapshot = page.evaluate('viewer.machine().snapshot()')
        lit = self.shot('state-clocked-lit')
        self.assertEqual(page.evaluate('colors()'), [ON])
        page.evaluate('viewer.manifestChanged()')
        self.assertEqual(page.evaluate('viewer.machine().snapshot()'), snapshot)
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(self.shot(), lit)
        page.evaluate("viewer.machine().move('powered',{to:0})")
        self.assertEqual(page.evaluate('colors()'), [ON])
        self.assertEqual(page.evaluate('viewer.machine().state().count'), 1)
        self.assertEqual(self.errors, [])

    def test_settled_relation_property_reaches_the_ordinary_viewer(self):
        self.mount('relation-property')
        page = self.page
        before = self.shot('relation-dark')
        page.evaluate("viewer.setDriver('powered',1)")
        self.assertEqual(page.evaluate('viewer.assembly().children[1].children[0].color'), ON)
        self.assert_changed(before, self.shot('relation-lit'))
        page.evaluate("viewer.setDriver('powered',0)")
        self.assertEqual(self.shot('relation-released'), before)
        self.assertEqual(self.errors, [])


@needs_bundle
@needs_playwright
@needs_pil
class ModelColorCaptureTest(TestCase):
    def test_standard_produced_modes_capture_their_native_default_color(self):
        import io
        from PIL import Image, ImageChops
        with tempfile.TemporaryDirectory() as directory:
            images = {}
            for name in ('posed', 'powered', 'clocked', 'running'):
                root = Path(directory) / name
                shutil.copytree(FIXTURE / name, root)
                # Capture's standard staging name aliases identical producer bytes.
                shutil.copy2(root / 'manifest.json', root / 'viewer.json')
                output = Path(directory) / f'{name}.png'
                Capture(str(root)).render(str(output), (320, 240), mount_options())
                images[name] = Image.open(io.BytesIO(output.read_bytes())).convert('RGBA')
                self.assertIn(255, images[name].getchannel('A').getdata())
            self.assertIsNone(ImageChops.difference(images['posed'], images['clocked']).getbbox())
            self.assertIsNone(ImageChops.difference(images['posed'], images['running']).getbbox())
            self.assertIsNotNone(ImageChops.difference(images['posed'].convert('RGB'), images['powered'].convert('RGB')).getbbox())
