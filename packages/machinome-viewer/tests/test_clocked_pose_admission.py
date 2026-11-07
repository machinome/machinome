# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Real bundled viewer: a refused final pose leaves bank AND pixels standing."""

from hashlib import sha256
import json
import math
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from machinome.viewer.web.bundle import bundle_path
from .support import needs_bundle, needs_playwright, serve_directory
from .test_widget_e2e import HARNESS_PAGE

FIXTURE = Path(__file__).parent / "fixtures" / "pose-admission"
SHOTS = Path(__file__).parent / "_shots" / "pose-admission"


@needs_bundle
@needs_playwright
class ClockedPoseAdmissionTest(TestCase):
    def setUp(self):
        from playwright.sync_api import sync_playwright

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        shutil.copytree(
            FIXTURE,
            root / "fixture",
            ignore=shutil.ignore_patterns("_build", "__pycache__"),
        )
        shutil.copy2(bundle_path(), root / "machinome-viewer.js")
        (root / "harness.html").write_text(HARNESS_PAGE)
        server = serve_directory(root)
        url = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        pw = sync_playwright().start()
        self.addCleanup(pw.stop)
        browser = pw.chromium.launch(args=["--no-sandbox", "--use-angle=swiftshader"])
        self.addCleanup(browser.close)
        self.page = browser.new_page(viewport={"width": 800, "height": 600})
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(url + "/harness.html")
        self.page.evaluate("""async () => {
          window.viewer = await MachinomeViewer.mount('#host', 'fixture/manifest.json', {
            renderMode:'on-demand', animation:'external', autoplay:false,
            driverControls:'none', partControls:'none' });
          viewer.setView({camera:[0,-60,90], target:[5,0,0]});
          window.machine = viewer.machine();
          window.visible = () => ['earlier','arm/body'].map(
            path => viewer.partOnScreen(path.split('/')));
        }""")

    def assert_finite(self, value):
        if isinstance(value, dict):
            for child in value.values():
                self.assert_finite(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_finite(child)
        elif isinstance(value, (int, float)):
            self.assertTrue(
                math.isfinite(value), f"nonfinite public screen value: {value}"
            )

    def assert_same_screen(self, actual, expected):
        # setView refits the camera's planes and may round a CSS coordinate
        # in its final decimal place. Tree matrices are pinned exactly in TS.
        if isinstance(expected, dict):
            self.assertEqual(actual.keys(), expected.keys())
            for key in expected:
                self.assert_same_screen(actual[key], expected[key])
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected))
            for a, b in zip(actual, expected):
                self.assert_same_screen(a, b)
        elif isinstance(expected, (float, int)):
            self.assertAlmostEqual(actual, expected, places=9)
        else:
            self.assertEqual(actual, expected)

    def test_invalid_move_instruction_restore_keep_bank_pixels_and_recovery(self):
        page = self.page
        origin = page.evaluate("machine.snapshot()")
        screens = page.evaluate("visible()")
        self.assertTrue(all(part is not None for part in screens))
        self.assert_finite(screens)
        SHOTS.mkdir(parents=True, exist_ok=True)
        before = page.locator("#host").screenshot(path=str(SHOTS / "before.png"))
        receipts = []
        # All requests use the real rendered descendant. The +3 request
        # crosses three commits, so a bank-only guard cannot fake rollback.
        for operation in [
            "machine.move('press',{to:2.000001})",
            "machine.move('press',{to:-0.000001})",
            "machine.move('press',{to:3})",
            "machine.restore({...machine.snapshot(),"
            "bank:{...machine.state(),press:3,count:7}})",
        ]:
            answer = page.evaluate(
                """operation => {
              let error = null, result = null;
              try { result = eval(operation); } catch (e) { error = String(e.message); }
              viewer.setView(viewer.view());
              return {error, result, snapshot:machine.snapshot(), screens:visible()};
            }""",
                operation,
            )
            receipts.append(answer)
            self.assertIsNotNone(
                answer["error"], operation + " accepted invalid final pose"
            )
            self.assertRegex(answer["error"], r"arm.*operation 0")
            self.assertIsNone(answer["result"])
            self.assertEqual(answer["snapshot"], origin)
            self.assert_same_screen(answer["screens"], screens)
            self.assert_finite(answer["screens"])
            self.assertEqual(page.locator("#host").screenshot(), before)
        page.locator("#host").screenshot(path=str(SHOTS / "after-refusal.png"))
        # Restore original bank, then repopulate a failed candidate cache.
        page.evaluate("machine.restore(machine.snapshot())")
        page.evaluate("() => { try { machine.move('press',{to:3}); } catch (_) {} }")
        independent = page.evaluate("""() => {
              const answer=machine.move('independent',{to:4});
              return {answer,bank:machine.state(),screens:visible()};
            }""")
        self.assertEqual(
            independent["bank"], {"press": 0, "independent": 4, "count": 0}
        )
        self.assertEqual(independent["answer"]["commits"], [])
        self.assert_same_screen(independent["screens"][1], screens[1])
        self.assertNotEqual(independent["screens"][0], screens[0])
        valid = page.evaluate("""() => {
              const answer=machine.move('press',{to:1.5});
              return {answer,bank:machine.state(),screens:visible()};
            }""")
        self.assertEqual(valid["bank"], {"press": 1.5, "independent": 4, "count": 1})
        self.assertEqual(len(valid["answer"]["commits"]), 1)
        self.assertEqual(valid["answer"]["end"], 1.5)
        self.assert_finite(valid["screens"])
        self.assertNotEqual(valid["screens"][1], screens[1])
        page.locator("#host").screenshot(path=str(SHOTS / "valid-recovery.png"))
        # Same complete bank from a clean reset gives the same explicit
        # standing-press/new-independent geometry, independently of caches.
        page.evaluate("machine.reset()")
        page.evaluate("machine.move('independent',{to:4})")
        self.assert_same_screen(page.evaluate("visible()"), independent["screens"])
        (SHOTS / "receipt.json").write_text(
            json.dumps(
                {"refusals": receipts, "independent": independent, "valid": valid},
                indent=2,
                allow_nan=False,
            )
            + "\n"
        )
        self.assertEqual(self.errors, [])

    def test_continuous_instruction_refuses_before_drawing_or_committing(self):
        page = self.page
        page.evaluate("""async () => {
          viewer.dispose();
          window.viewer = await MachinomeViewer.mount('#host', 'fixture/manifest.json', {
            renderMode:'continuous', animation:'external', autoplay:false,
            driverControls:'none', partControls:'none' });
          viewer.setView({camera:[0,-60,90], target:[5,0,0]});
          window.machine = viewer.machine();
        }""")
        before = page.evaluate("({bank:machine.snapshot(),screens:visible()})")
        pixels = page.locator("#host").screenshot()
        answer = page.evaluate("""() => {
          let error = null, result = null;
          try { result = machine.trigger('Invalid'); }
          catch(e) { error=String(e.message); }
          return {error,result,bank:machine.snapshot(),screens:visible()};
        }""")
        self.assertRegex(answer["error"], r"arm.*operation 0")
        self.assertIsNone(answer["result"])
        self.assertEqual(answer["bank"], before["bank"])
        self.assert_same_screen(answer["screens"], before["screens"])
        self.assertEqual(page.locator("#host").screenshot(), pixels)
        # A subsequent frame must still show the standing bank, with no
        # instruction drawing or asynchronous page error leaked by refusal.
        page.evaluate("""() => new Promise(resolve => requestAnimationFrame(
              () => requestAnimationFrame(resolve)))""")
        self.assertEqual(page.evaluate("machine.snapshot()"), before["bank"])
        self.assert_same_screen(page.evaluate("visible()"), before["screens"])
        self.assertEqual(self.errors, [])


class PoseAdmissionFixtureTest(TestCase):
    def test_retained_publication_matches_its_source_and_native_receipt(self):
        receipt = json.loads((FIXTURE / "receipt.json").read_text())
        for name, expected in receipt["sha256"].items():
            self.assertEqual(
                sha256((FIXTURE / name).read_bytes()).hexdigest(), expected
            )
        document = json.loads((FIXTURE / "manifest.json").read_text())
        self.assertEqual(document["version"], 8)
        self.assertEqual(
            document["bindings"], [{"name": "_b0", "expression": "(press * 10)"}]
        )
        self.assertFalse(receipt["document_edited"])
        self.assertFalse(receipt["native_cad"])
        self.assertEqual(len(receipt["refusals"]), 3)
        self.assertTrue(
            all(
                row["before"] == row["after"] and row["records_unchanged"]
                for row in receipt["refusals"]
            )
        )
