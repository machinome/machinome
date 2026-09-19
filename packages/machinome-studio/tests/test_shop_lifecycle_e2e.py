# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

from floor.preparation import REQUIRED_VIEWER_API
from tests.fixtures.shop_process import isolated_launch_directory, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_MACHINOME = ROOT / "tests" / "fixtures" / "fake_machinome.py"
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class ShopLifecycleE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:  # pragma: no cover - optional local browser dependency
            raise unittest.SkipTest(f"Playwright is unavailable: {error}") from error
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception as error:  # pragma: no cover - browser install is environmental
            cls.playwright.stop()
            raise unittest.SkipTest(f"Chromium is unavailable: {error}") from error

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project_home = Path(self.temporary.name) / "projects"
        self.project_home.mkdir()
        self.shop = self.enterContext(isolated_launch_directory())
        self._launch()
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 900})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()

    def _launch(self, extra_env: dict[str, str] | None = None) -> None:
        """Start the shop subprocess. `setUp` calls this with no extra
        environment; a test that needs the real viewer bundle stops the
        default process and relaunches through this same method with
        FAKE_MACHINOME_BUNDLE / FAKE_MACHINOME_VIEWER_API set, so the framework
        viewer command the floor process itself later runs inherits them
        (`resolve_viewer_bundle` runs with no `extra_env` of its own -- it
        inherits the floor process's own environment)."""
        self.port = _free_port()
        self.process = subprocess.Popen(
            [
                "python", "-m", "floor", "--port", str(self.port),
                "--projects-dir", str(self.project_home),
                "--machinome-command", str(FAKE_MACHINOME),
            ],
            cwd=self.shop,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            env=subprocess_environment({
                **os.environ,
                "GIT_AUTHOR_NAME": "Shop Test",
                "GIT_AUTHOR_EMAIL": "shop@example.invalid",
                "GIT_COMMITTER_NAME": "Shop Test",
                "GIT_COMMITTER_EMAIL": "shop@example.invalid",
                "FAKE_MACHINOME_NEW_DELAY": "0.5",
                **(extra_env or {}),
            }),
        )
        self.addCleanup(self._stop)
        _wait_for(lambda: _request(self.url("/health"), "GET") == {"status": "open"})

    def _discover_real_viewer_bundle(self) -> tuple[Path, int]:
        """The real viewer bundle a behavioural test proves the navigator
        against (design D4). `SHOP_E2E_VIEWER_BUNDLE` first -- a value
        naming no file is a hard failure, not a skip, because the pilot
        asked for that exact bundle -- then the installed
        `machinome_viewer` package if it is new enough, else a named skip.
        A skipped run is not evidence; the caller must actually be run with
        the environment variable exported to prove anything red or green."""
        supplied = os.environ.get("SHOP_E2E_VIEWER_BUNDLE")
        if supplied:
            path = Path(supplied)
            if not path.is_file():
                raise AssertionError(f"SHOP_E2E_VIEWER_BUNDLE names no file: {path}")
            banner = path.read_bytes()[:512]
            match = re.search(rb"\bviewer API (\d+)", banner)
            if not match:
                raise AssertionError(f"SHOP_E2E_VIEWER_BUNDLE has no 'viewer API N' banner: {path}")
            return path, int(match.group(1))
        installed_version: int | None = None
        try:
            from machinome_viewer import bundle as installed_bundle
        except ImportError:
            installed_bundle = None
        if installed_bundle is not None and installed_bundle.has_bundle():
            installed_version = installed_bundle.api_version()
            if installed_version >= REQUIRED_VIEWER_API:
                return installed_bundle.bundle_path(), installed_version
        self.skipTest(
            f"no viewer bundle at API {REQUIRED_VIEWER_API} or newer is available: "
            "export SHOP_E2E_VIEWER_BUNDLE to name one, or install a newer "
            "machinome-viewer (installed viewer API: "
            f"{installed_version if installed_version is not None else 'no bundle installed'})"
        )

    def test_hub_lists_projects_unopenable_entries_and_opens_the_creation_sheet(self) -> None:
        self._make_project("bracket")
        (self.project_home / "not-a-repository").mkdir()
        self.page.goto(self.url("/"))

        self.page.get_by_role("heading", name="Projects").wait_for()
        self.page.get_by_text(str(self.project_home), exact=True).wait_for()
        self.page.get_by_text("bracket", exact=True).wait_for()
        self.page.get_by_text("not-a-repository", exact=True).wait_for()
        self.page.get_by_text("not a git repository", exact=False).wait_for()
        self.page.get_by_role("button", name="New project").first.click()
        self.page.get_by_role("heading", name="New project").wait_for()
        self.page.get_by_text("stored in the working folder").wait_for()

    def test_project_creation_opens_a_workspace_and_close_returns_to_the_hub(self) -> None:
        self.page.goto(self.url("/"))
        self.page.get_by_role("button", name="New project").first.click()
        self.page.get_by_label("Project name").fill("new_bracket")
        self.page.get_by_role("button", name="Builder").click()
        self.page.get_by_role("button", name="Create and open").click()
        self.page.get_by_text("creating · builder", exact=False).wait_for(timeout=2_000)
        self.page.wait_for_url("**/projects/new_bracket", timeout=10_000)
        self.page.get_by_text("Machinome Studio / new_bracket").wait_for()
        self.page.get_by_role("button", name="Close project").click()
        self.page.wait_for_url(self.url("/"), timeout=5_000)
        self.page.get_by_role("heading", name="Projects").wait_for()

    def test_the_hub_says_a_presented_model_is_being_brought_up_to_date(self) -> None:
        project = self._make_project("kept-warm")
        # A publication from an earlier run is what the session opens on. The
        # build behind it is held open so the browser can be read while it runs.
        subprocess.run(
            [sys.executable, str(FAKE_MACHINOME), "build"],
            cwd=project, check=True, capture_output=True,
        )
        gate = Path(self.temporary.name) / "release-build"
        (project / ".fake-machinome-state.json").write_text(json.dumps({"build_gate": str(gate)}))

        self.page.goto(self.url("/"))
        self.page.get_by_text("closed · builder", exact=False).wait_for()
        rebuilding = self.page.get_by_text("Bringing the model up to date", exact=False)
        self.assertEqual(rebuilding.count(), 0)

        _request(self.url("/api/sessions"), "POST", {"path": "kept-warm"})

        # The live event has to carry the state through to the card,
        rebuilding.wait_for(timeout=10_000)
        # a browser arriving mid-build has to read it from the hub snapshot,
        self.page.reload()
        rebuilding.wait_for(timeout=10_000)
        # and the maker has to be told when the model is current again.
        gate.write_text("go\n")
        rebuilding.wait_for(state="detached", timeout=20_000)
        self.page.get_by_text("open · builder", exact=False).wait_for()

    def test_the_workspace_says_a_presented_model_is_being_brought_up_to_date(self) -> None:
        project = self._make_project("warm-workspace")
        # As in the hub case: a publication from an earlier run, and a build
        # held open behind the session that opens on it.
        subprocess.run(
            [sys.executable, str(FAKE_MACHINOME), "build"],
            cwd=project, check=True, capture_output=True,
        )
        gate = Path(self.temporary.name) / "release-build"
        (project / ".fake-machinome-state.json").write_text(json.dumps({"build_gate": str(gate)}))
        self._open("warm-workspace")

        # The maker who clicks the card never sees it; they land here.
        self.page.goto(self.url("/projects/warm-workspace"))
        self.page.get_by_text("Machinome Studio / warm-workspace").wait_for()
        rebuilding = self.page.get_by_text("Bringing the model up to date", exact=False)
        rebuilding.wait_for(timeout=10_000)

        # This build publishes nothing, so only the settled event can clear it.
        gate.write_text("go\n")
        rebuilding.wait_for(state="detached", timeout=20_000)

    def test_two_workspace_pages_show_only_their_own_conversation(self) -> None:
        self._make_project("alpha")
        self._make_project("bravo")
        alpha = self._open("alpha")
        bravo = self._open("bravo")
        for session_id in (alpha, bravo):
            _request(
                self.url(f"/api/sessions/{session_id}/agents"), "POST",
                {"role": "builder", "label": "Builder"},
            )
        _request(self.url(f"/api/sessions/{alpha}/conversation"), "POST", {"text": "Alpha message"})
        _request(self.url(f"/api/sessions/{bravo}/conversation"), "POST", {"text": "Bravo message"})

        alpha_page = self.context.new_page()
        bravo_page = self.context.new_page()
        alpha_page.goto(self.url("/projects/alpha"))
        bravo_page.goto(self.url("/projects/bravo"))
        alpha_page.get_by_text("Alpha message").wait_for()
        bravo_page.get_by_text("Bravo message").wait_for()
        self.assertEqual(alpha_page.get_by_text("Bravo message").count(), 0)
        self.assertEqual(bravo_page.get_by_text("Alpha message").count(), 0)

    def test_overflowing_transcript_ends_above_the_message_composer(self) -> None:
        self._make_project("long-chat")
        session_id = self._open("long-chat")
        _request(
            self.url(f"/api/sessions/{session_id}/agents"), "POST",
            {"role": "builder", "label": "Builder"},
        )
        for index in range(30):
            _request(
                self.url(f"/api/sessions/{session_id}/conversation"),
                "POST",
                {"text": f"Conversation message {index:02d}"},
            )
        self.page.goto(self.url("/projects/long-chat"))
        self.page.get_by_text("Conversation message 29").wait_for()

        transcript = self.page.get_by_role("list", name="Conversation transcript").bounding_box()
        composer = self.page.get_by_role("form", name="Message composer").bounding_box()
        assert transcript is not None and composer is not None
        self.assertLessEqual(transcript["y"] + transcript["height"], composer["y"])

    def test_failed_initial_model_build_keeps_chat_available_and_states_the_reason(self) -> None:
        project = self._make_project("broken-model")
        (project / ".fake-machinome-state.json").write_text(json.dumps({"fail": "broken model evidence"}))
        session_id = self._open("broken-model")
        self.page.goto(self.url("/projects/broken-model"))
        self.page.get_by_text("broken model evidence", exact=False).wait_for(timeout=10_000)
        self.page.get_by_role("textbox", name="Message", exact=True).fill("Please repair the model")
        self.page.get_by_role("button", name="Send").click()
        _wait_for(lambda: _request(self.url(f"/api/sessions/{session_id}/conversation"), "GET")["entries"] != [])

    def test_workspace_mounts_the_project_scoped_viewer(self) -> None:
        self._make_project("viewer-project")
        session_id = self._open("viewer-project")
        self.page.goto(self.url("/projects/viewer-project"))
        self.page.get_by_role("img", name="Functional model").wait_for(timeout=10_000)
        history = self.page.evaluate("() => window.__machinomeViewerHistory")
        self.assertEqual(history["mounts"], 1)
        self.assertIn(f"/api/sessions/{session_id}/artifacts/viewer.json", history["fetches"])

    def test_build_inspects_one_piece_at_scale_and_downloads_explicit_quantities(self) -> None:
        triangle = (
            "solid part\nfacet normal 0 0 1\nouter loop\n"
            "vertex 0 0 0\nvertex 24 0 0\nvertex 0 18 6\n"
            "endloop\nendfacet\nendsolid part\n"
        )
        project = self._make_project("print-job")
        viewer = {
            "format": "machinome-export", "version": 1,
            "root": {"name": "assembly", "children": [
                {"name": "gear", "model": "gear.stl", "piece": "111111111111"},
                {"name": "pin", "model": "pin.stl", "piece": "222222222222"},
            ]},
            "pieces": [
                {
                    "id": "111111111111", "name": "Planet Gear", "count": 3,
                    "models": ["gear.stl"], "sources": ["root/gear.py"],
                    "size": [24, 18, 6], "volume": 1296, "watertight": True,
                },
                {
                    "id": "222222222222", "name": "Pin", "count": 1,
                    "models": ["pin.stl"], "sources": ["root/pin.py"],
                    "size": [6, 6, 30], "volume": 500, "watertight": False,
                },
            ],
        }
        (project / ".fake-machinome-state.json").write_text(json.dumps({
            "model": "gear.stl", "model_content": triangle,
            "extra_models": {"pin.stl": triangle}, "viewer": viewer,
        }))
        self._open("print-job")
        self.page.goto(self.url("/projects/print-job"))
        composer = self.page.get_by_role("textbox", name="Message", exact=True)
        composer.fill("keep this Build draft")

        self.page.get_by_role("button", name="Build", exact=True).click()
        self.page.get_by_role("region", name="Build inspection").wait_for()
        self.page.get_by_role("img", name="Planet Gear, one representative piece on a 250 by 210 millimetre build plate").wait_for(timeout=10_000)
        self.assertEqual(self.page.locator(".build-piece-canvas").count(), 1)
        self.page.get_by_text("Print 3 copies", exact=True).wait_for()
        self.page.get_by_text("one representative shown", exact=True).wait_for()
        self.page.get_by_text("fits 250 × 210 × 220 mm", exact=True).wait_for()
        self.page.get_by_role("button", name="Pin", exact=False).click()
        self.page.get_by_text("Print 1 copy", exact=True).wait_for()
        self.page.get_by_text("not watertight", exact=True).wait_for()

        self.page.get_by_role("button", name="Model", exact=True).click()
        self.page.get_by_role("button", name="Build", exact=True).click()
        self.assertEqual(self.page.get_by_role("button", name="Pin", exact=False).get_attribute("aria-current"), "true")
        self.assertEqual(composer.input_value(), "keep this Build draft")

        with self.page.expect_download() as pending:
            self.page.get_by_role("link", name="Download package").click()
        download = pending.value
        self.assertEqual(download.suggested_filename, "print-job-print-package.zip")
        archive_path = download.path()
        assert archive_path is not None
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(
                archive.namelist(),
                ["README.md", "planet-gear-111111111111.stl", "pin-222222222222.stl"],
            )
            readme = archive.read("README.md").decode()
            self.assertIn("| `planet-gear-111111111111.stl` | 3 |", readme)
            self.assertIn("| `pin-222222222222.stl` | 1 |", readme)

        self.page.set_viewport_size({"width": 760, "height": 900})
        self.assertFalse(self.page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth"))

    def test_code_workspace_saves_and_reconciles_agent_file_changes(self) -> None:
        project = self._make_project("code-project")
        (project / ".gitignore").write_text(
            (project / ".gitignore").read_text() + "ignored.py\n"
        )
        (project / "ignored.py").write_text("# ignored\n")
        self._open("code-project")
        self.page.goto(self.url("/projects/code-project"))

        self.page.get_by_role("button", name="Code", exact=True).click()
        self.assertEqual(self.page.get_by_text("Files", exact=True).count(), 0)
        self.assertEqual(self.page.get_by_title("ignored.py").count(), 0)
        # The model's own file is open already; nothing had to be found first.
        self.page.locator(".source-tree").get_by_title("root/__init__.py").wait_for()
        editor = self.page.locator(".monaco-editor").first
        editor.wait_for(timeout=10_000)
        editor_box = editor.bounding_box()
        assert editor_box is not None
        self.assertGreater(editor_box["height"], 500)
        editor_input = editor.locator(".native-edit-context, textarea.inputarea")
        self.page.get_by_role("textbox", name="Message", exact=True).wait_for()

        editor_input.focus()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.type("# saved in Code\n")
        self.page.keyboard.press("Control+S")
        _wait_for(lambda: (project / "root" / "__init__.py").read_text() == "# saved in Code\n")
        _wait_for(lambda: (project / ".fake-machinome-builds").read_text().count("build\n") >= 2)
        self.page.get_by_text("saved", exact=True).wait_for()

        (project / "agent_created.py").write_text("# made by an agent\n")
        self.page.get_by_title("agent_created.py").wait_for(timeout=10_000)
        self.page.get_by_title("agent_created.py").click()
        self.page.get_by_text("made by an agent", exact=False).wait_for(timeout=10_000)

        (project / "agent_created.py").write_text("# clean agent revision\n")
        self.page.get_by_text("clean agent revision", exact=False).wait_for(timeout=10_000)

        composer = self.page.get_by_role("textbox", name="Message", exact=True)
        composer.fill("persistent draft")
        self.page.get_by_role("button", name="Model", exact=True).click()
        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_title("agent_created.py").last.wait_for()
        self.assertEqual(composer.input_value(), "persistent draft")
        self.assertEqual(self.page.evaluate("() => window.__machinomeViewerHistory.mounts"), 1)

        editor_input.focus()
        self.page.keyboard.press("End")
        self.page.keyboard.type("# unsaved maker text")
        self.page.get_by_text("unsaved", exact=True).wait_for()
        (project / "agent_created.py").write_text("# changed by an agent\n")
        self.page.get_by_text("external changes", exact=True).wait_for(timeout=10_000)
        self.page.get_by_text("Your unsaved text is preserved.", exact=False).wait_for()
        editor_input.focus()
        self.page.keyboard.press("Control+S")
        self.assertEqual((project / "agent_created.py").read_text(), "# changed by an agent\n")
        self.page.get_by_role("button", name="Reload external version").click()
        self.page.get_by_text("changed by an agent", exact=False).wait_for(timeout=10_000)

    def test_code_navigator_collapses_folders_uses_file_icons_and_previews_png(self) -> None:
        project = self._make_project("code-browser")
        (project / "README.md").write_text("# Drawing\n")
        (project / "preview.png").write_bytes(PNG_1X1)
        (project / "model.py").write_text("model = True\n")
        (project / "settings.toml").write_text("enabled = true\n")
        self._open("code-browser")
        self.page.goto(self.url("/projects/code-browser"))

        self.page.get_by_role("button", name="Code", exact=True).click()
        # The model's file is open, so the folder holding it stands open too.
        tree = self.page.locator(".source-tree")
        folder = self.page.get_by_role("button", name="Collapse root")
        folder.wait_for()
        tree.get_by_title("root/__init__.py").wait_for()
        for kind in ("folder", "markdown", "image", "python", "file"):
            with self.subTest(kind=kind):
                self.assertGreaterEqual(self.page.locator(f'[data-source-icon="{kind}"]').count(), 1)
        icon_colors = self.page.locator(".source-icon").evaluate_all(
            "icons => [...new Set(icons.map(icon => getComputedStyle(icon).color))]"
        )
        self.assertEqual(len(icon_colors), 1)

        folder.click()
        self.assertEqual(tree.get_by_title("root/__init__.py").count(), 0)
        self.page.get_by_role("button", name="Expand root").click()
        tree.get_by_title("root/__init__.py").wait_for()

        self.page.get_by_title("preview.png").click()
        preview = self.page.get_by_role("img", name="Preview preview.png")
        preview.wait_for()
        self.assertEqual(preview.evaluate("image => image.naturalWidth"), 1)
        self.assertEqual(self.page.locator(".monaco-editor").count(), 0)

        self.page.get_by_title("model.py").click()
        self.page.locator(".monaco-editor").wait_for()
        self.page.get_by_text("model = True", exact=False).wait_for()

    def test_code_opens_on_the_file_the_presented_assembly_is_written_in(self) -> None:
        project = self._make_project("already-open")
        (project / "root" / "__init__.py").write_text("# the root assembly\n")
        self._open("already-open")
        self.page.goto(self.url("/projects/already-open"))

        # First visit to Code: the model on show is already the file in hand.
        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_text("the root assembly", exact=False).wait_for(timeout=10_000)
        tab = self.page.locator(".code-tabs button.active")
        self.assertEqual(tab.get_attribute("title"), "root/__init__.py")

        # Closed on purpose, it stays closed -- reopening Code is not a reason
        # to hand a maker back the file they just put away.
        self.page.get_by_label("Close root/__init__.py").click()
        self.page.get_by_text("Open a file from the project root").wait_for()
        self.page.get_by_role("button", name="Model", exact=True).click()
        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_text("Open a file from the project root").wait_for()

    def test_code_editor_colours_a_short_file_while_the_model_keeps_rendering(self) -> None:
        project = self._make_project("code-colour")
        (project / "short.py").write_text("import os\n\n\ndef bead(count):\n    # one heaven bead\n    return count\n")
        self._open("code-colour")
        # A model rendering every frame leaves the browser no idle time, and
        # idle time is the only time Monaco colours lines on its own.
        self.page.add_init_script("window.requestIdleCallback = () => 0;")
        self.page.goto(self.url("/projects/code-colour"))

        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_title("short.py").click()
        self.page.locator(".monaco-editor").wait_for(timeout=10_000)
        self.page.get_by_text("one heaven bead", exact=False).wait_for(timeout=10_000)

        # The file is short enough to fit, so no scroll can rescue the colours.
        _wait_for(lambda: len(self._token_classes()) > 1)

    def test_agents_workspace_is_interactive_mounted_and_reachable_at_narrow_width(self) -> None:
        self._make_project("agents-workspace")
        session_id = self._open("agents-workspace")
        _request(
            self.url(f"/api/sessions/{session_id}/agents"), "POST",
            {"role": "builder", "label": "Builder"},
        )
        run = _request(self.url(f"/api/sessions/{session_id}"), "GET")
        agent = run["agents"][0]
        agent.update({
            "backend": "claude", "provider": None, "model": "sonnet",
            "effort": "high", "runtime_idle": True, "runtime_pristine": True, "backend_idle": True,
        })
        run["activity"] = [
            {
                "id": "tool-1", "sequence": 1, "role": "builder", "category": "tool",
                "state": "completed", "name": "machinome_test", "summary": "tests/test_model.py",
                "detail": "8 passed", "path": "", "diff": "", "timestamp": "2026-08-12T08:42:20Z",
                "input_tokens": 120, "output_tokens": 30,
            },
            {
                "id": "file-1", "sequence": 2, "role": "builder", "category": "file",
                "state": "completed", "name": "edit_file", "summary": "root/__init__.py",
                "detail": "", "path": "root/__init__.py",
                "diff": "@@ -1 +1 @@\n-# model\n+# revised model", "timestamp": "2026-08-12T08:42:44Z",
                "input_tokens": None, "output_tokens": None,
            },
        ]
        snapshot = {"run": run, "conversation": []}
        self.page.route(
            f"**/api/sessions/{session_id}/stream",
            lambda route: route.fulfill(
                status=200,
                content_type="text/event-stream",
                body=f"event: snapshot\ndata: {json.dumps(snapshot)}\n\n",
            ),
        )
        revision = "a" * 64
        runtime_requests: list[dict[str, object]] = []
        stale = {"enabled": False}
        pristine = {"value": True}

        def runtime_route(route) -> None:
            if route.request.method == "PATCH":
                runtime_requests.append(route.request.post_data_json)
                if stale["enabled"]:
                    stale["enabled"] = False
                    route.fulfill(status=409, content_type="application/json", body=json.dumps({"detail": "pyproject.toml changed since the controls were loaded"}))
                    return
                body = route.request.post_data_json
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "config_revision": revision, "persisted": body["persist"],
                }))
                return
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "role": "builder",
                "runtime": {"backend": "claude", "provider": None, "model": "sonnet", "effort": "high"},
                "supported": True,
                "reason": None,
                "choices": [
                    {"backend": "claude", "provider": None, "model": "sonnet", "efforts": ["medium", "high"]},
                    {"backend": "claude", "provider": None, "model": "opus", "efforts": ["medium", "high"]},
                    {"backend": "opencode", "provider": "anthropic", "model": "claude-sonnet-4-5", "efforts": ["medium", "high"]},
                    {"backend": "opencode", "provider": "openai-codex", "model": "gpt-5.6-sol", "efforts": ["high"]},
                ],
                "config_revision": revision,
                "runtime_idle": True,
                "runtime_pristine": pristine["value"],
            }))

        self.page.route(f"**/api/sessions/{session_id}/agents/builder/runtime", runtime_route)
        self.page.goto(self.url("/projects/agents-workspace"))
        composer = self.page.get_by_role("textbox", name="Message", exact=True)
        composer.fill("keep this draft")

        self.page.get_by_role("button", name="Agents", exact=True).click()
        self.page.locator(".agents-area").wait_for()
        self.page.get_by_text("Replace this unused session immediately.").wait_for()
        controls = self.page.locator(".agent-controls")
        provider_select = controls.get_by_label("Provider", exact=True)
        model_select = controls.get_by_label("Model", exact=True)
        self.assertEqual(provider_select.input_value(), "anthropic")
        self.assertTrue(provider_select.is_disabled())
        self.assertEqual(self.page.get_by_text("Tools", exact=True).count(), 0)
        self.assertEqual(self.page.get_by_role("button", name="codex", exact=True).count(), 0)
        self.assertFalse(self.page.get_by_role("button", name="claude", exact=True).is_disabled())
        self.page.get_by_role("button", name="opencode", exact=True).click()
        self.assertFalse(provider_select.is_disabled())
        self.assertEqual(provider_select.locator("option").all_text_contents(), ["anthropic", "openai-codex"])
        provider_select.select_option("openai-codex")
        self.assertEqual(model_select.locator("option").all_text_contents(), ["gpt-5.6-sol"])
        self.page.get_by_role("button", name="Apply", exact=True).click()
        self.page.get_by_text("applied · written to pyproject.toml", exact=True).wait_for()
        self.assertEqual(runtime_requests[-1]["provider"], "openai-codex")
        self.assertEqual(runtime_requests[-1]["model"], "gpt-5.6-sol")
        self.page.get_by_role("button", name="claude", exact=True).click()
        self.assertEqual(provider_select.input_value(), "anthropic")
        self.assertTrue(provider_select.is_disabled())
        self.assertTrue(self.page.get_by_label("write to pyproject.toml").is_checked())
        self.assertTrue(self.page.get_by_role("button", name="Apply", exact=True).is_disabled())
        self.assertEqual(self.page.locator('[data-agent-role="builder"].selected').count(), 1)

        self.page.get_by_role("button", name="tools 1", exact=True).click()
        self.page.get_by_role("button", name="machinome_test", exact=False).click()
        self.page.get_by_text("8 passed", exact=True).wait_for()
        self.page.get_by_role("button", name="files 1", exact=True).click()
        self.page.get_by_text("# revised model", exact=True).wait_for()
        self.page.get_by_role("button", name="Open in Code", exact=True).click()
        self.page.locator(".monaco-editor").wait_for(timeout=10_000)

        self.page.get_by_role("button", name="Agents", exact=True).click()
        self.assertEqual(composer.input_value(), "keep this draft")
        self.assertEqual(self.page.get_by_role("button", name="files 1", exact=True).get_attribute("class"), "selected")

        model_select.select_option("opus")
        self.page.get_by_role("button", name="medium", exact=True).click()
        self.page.get_by_role("button", name="Apply", exact=True).click()
        self.page.get_by_text("applied · written to pyproject.toml", exact=True).wait_for()
        self.assertTrue(runtime_requests[-1]["persist"])

        self.page.get_by_label("write to pyproject.toml").uncheck()
        self.page.get_by_role("button", name="high", exact=True).click()
        self.page.get_by_role("button", name="Apply", exact=True).click()
        self.page.get_by_text("applied · this session only", exact=True).wait_for()
        self.assertFalse(runtime_requests[-1]["persist"])

        stale["enabled"] = True
        self.page.get_by_role("button", name="Apply", exact=True).click()
        self.page.get_by_text("pyproject.toml changed since the controls were loaded", exact=True).wait_for()
        self.page.set_viewport_size({"width": 760, "height": 900})
        self.assertFalse(self.page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth"))

        agent["runtime_pristine"] = False
        pristine["value"] = False
        self.page.reload()
        self.page.get_by_role("button", name="Agents", exact=True).click()
        self.page.get_by_text("Locked after this agent's first use.").wait_for()
        self.assertTrue(self.page.get_by_role("button", name="opencode", exact=True).is_disabled())

    def test_model_panel_mounts_and_disposes_the_viewer_navigator(self) -> None:
        self._make_project("navigator-project")
        self._open("navigator-project")
        self.page.goto(self.url("/projects/navigator-project"))

        self.page.get_by_role("heading", name="MODEL", exact=True).wait_for()
        # The fake widget's navigator is deliberately an EMPTY tree (design
        # D5: no rows, so nothing gives it a non-zero height) -- it is
        # attached, not necessarily "visible" by Playwright's box-size
        # heuristic.
        tree = self.page.get_by_role("tree", name="Assembly")
        tree.wait_for(state="attached", timeout=10_000)
        history = self.page.evaluate("() => window.__machinomeViewerHistory")
        self.assertEqual(len(history["navigators"]), 1)
        self.assertEqual(history["navigators"][0]["label"], "Assembly")

        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_role("button", name="Model", exact=True).click()
        tree.wait_for(state="attached")
        history = self.page.evaluate("() => window.__machinomeViewerHistory")
        self.assertEqual(len(history["navigators"]), 1)
        self.assertEqual(history["mounts"], 1)

        self.page.get_by_role("button", name="Close project").click()
        self.page.get_by_role("heading", name="Projects").wait_for()
        history = self.page.evaluate("() => window.__machinomeViewerHistory")
        self.assertEqual(len(history["navigators"]), 1)
        self.assertTrue(history["navigators"][0]["disposed"])

    def test_model_panel_presents_the_viewer_navigator(self) -> None:
        """The one behavioural test that runs against a REAL viewer bundle
        (design D4): the panel's look is proved against the navigator's
        published class contract and the studio's own `--machinome-nav-*`
        overrides, not against the e2e fake's hand-written tree. A skipped
        run is not evidence -- see `_discover_real_viewer_bundle`."""
        bundle, api_version = self._discover_real_viewer_bundle()
        self._stop()
        self._launch({"FAKE_MACHINOME_BUNDLE": str(bundle), "FAKE_MACHINOME_VIEWER_API": str(api_version)})

        project = self._make_project("navigator-look")
        viewer_document = {
            "format": "machinome-export", "version": 1,
            "animation": {"fps": 24, "frames": 1},
            "root": {
                "name": "engine", "type": "assembly", "color": None, "operations": [],
                "children": [
                    {
                        "name": "housing", "type": "assembly", "color": "#cc4444", "operations": [],
                        "children": [
                            {"name": "pin", "type": "assembly", "color": None, "operations": [], "children": []},
                        ],
                    },
                    {"name": "unpainted", "type": "assembly", "color": None, "operations": [], "children": []},
                ],
            },
        }
        (project / ".fake-machinome-state.json").write_text(json.dumps({"viewer": viewer_document}))
        self._open("navigator-look")
        self.page.goto(self.url("/projects/navigator-look"))

        tree = self.page.get_by_role("tree", name="Assembly")
        tree.wait_for(timeout=10_000)
        self.page.get_by_role("heading", name="MODEL", exact=True).wait_for()

        engine_row = tree.get_by_role("treeitem").filter(has_text="engine")
        self.assertIn("machinome-nav-row--root", engine_row.get_attribute("class") or "")
        self.assertEqual(engine_row.get_attribute("aria-selected"), "true")
        self.assertEqual(engine_row.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(28, 33, 40)")
        self.assertIn("rgb(79, 182, 184)", engine_row.evaluate("element => getComputedStyle(element).boxShadow"))
        self.assertEqual(
            engine_row.evaluate("element => getComputedStyle(element).getPropertyValue('--machinome-nav-focus-ring')").strip(),
            "#e0a350",
        )
        self.assertEqual(self.page.get_by_role("button", name="Show full assembly").count(), 0)

        self.assertEqual(self.page.get_by_role("checkbox", name="Visibility for pin").count(), 0)
        housing_row = tree.get_by_role("treeitem").filter(has_text="housing")
        housing_row.get_by_role("button", name="Expand housing").click()
        pin_visibility = self.page.get_by_role("checkbox", name="Visibility for pin")
        plain_visibility = self.page.get_by_role("checkbox", name="Visibility for unpainted")
        pin_visibility.wait_for(timeout=10_000)
        self.assertTrue(pin_visibility.is_checked())
        self.assertTrue(plain_visibility.is_checked())
        self.assertEqual(pin_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(204, 68, 68)")
        self.assertEqual(plain_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(107, 114, 128)")

        # Keyboard contract: Down (engine -> housing), Right (housing is
        # already expanded, so this MOVES to its first child, pin), Enter
        # (pin becomes the focused root -- the navigator redraws which row
        # carries `machinome-nav-row--root`), Space (toggles the active row's --
        # pin's -- own visibility, emptying its chip).
        self.page.get_by_text("engine", exact=True).click()
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("ArrowRight")
        self.page.keyboard.press("Enter")
        pin_row = tree.get_by_role("treeitem").filter(has_text="pin")
        self.assertIn("machinome-nav-row--root", pin_row.get_attribute("class") or "")
        self.assertNotIn("machinome-nav-row--root", engine_row.get_attribute("class") or "")
        self.page.keyboard.press(" ")
        self.assertFalse(pin_visibility.is_checked())
        self.assertEqual(pin_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgba(0, 0, 0, 0)")

        self.page.get_by_role("button", name="Show full assembly").click()
        self.assertIn("machinome-nav-row--root", engine_row.get_attribute("class") or "")
        self.assertEqual(self.page.get_by_role("button", name="Show full assembly").count(), 0)

        viewer_document["root"]["children"][0]["children"] = []
        (project / ".fake-machinome-state.json").write_text(json.dumps({"viewer": viewer_document}))
        (project / "root" / "__init__.py").write_text("# changed model\n")
        _wait_for(lambda: self.page.get_by_text("pin", exact=True).count() == 0)
        tree.wait_for(state="attached")
        self.page.get_by_role("heading", name="MODEL", exact=True).wait_for()

    def test_a_multi_model_card_shows_its_models_side_by_side(self) -> None:
        project = self._make_project("clocks", models=("wall_clock_01", "wall_clock_02", "wall_clock_03", "wall_clock_04"))
        (project / "screenshots").mkdir()
        for model in ("wall_clock_01", "wall_clock_03"):
            (project / "screenshots" / f"{model}.png").write_bytes(PNG_1X1)
        self._make_project("sandbox/windmill")

        self.page.goto(self.url("/"))
        card = self.page.get_by_role("link").filter(has_text="clocks").first
        card.wait_for(timeout=10_000)

        # The first three declared models, in manifest order, and the one
        # without a picture still holding its place.
        previews = card.get_by_role("img")
        self.assertEqual(previews.count(), 2)
        self.assertEqual(previews.nth(0).get_attribute("alt"), "wall_clock_01 model preview")
        self.assertEqual(previews.nth(1).get_attribute("alt"), "wall_clock_03 model preview")
        self.assertEqual(card.locator(".model-tile").count(), 3)

        # A directory of unrelated projects stands on the projects it holds.
        grouping = self.page.get_by_role("link").filter(has_text="sandbox").first
        self.assertEqual(grouping.locator(".model-tile").count(), 1)

    def test_hub_cards_are_links_a_maker_can_open_in_another_tab(self) -> None:
        self._make_project("sandbox/windmill")

        self.page.goto(self.url("/"))
        folder = self.page.get_by_role("link").filter(has_text="sandbox").first
        folder.wait_for(timeout=10_000)
        self.assertEqual(folder.get_attribute("href"), "/folders/sandbox")

        folder.click()
        self.page.wait_for_url(self.url("/folders/sandbox"), timeout=5_000)
        project = self.page.get_by_role("link").filter(has_text="windmill").first
        self.assertEqual(project.get_attribute("href"), "/projects/sandbox/windmill")

    def test_a_project_url_opened_in_a_new_tab_opens_the_project(self) -> None:
        self._make_project("sandbox/windmill")

        # What a middle click or "Open link in a new tab" on the card does:
        # a fresh page that lands on a closed project opens it here.
        page = self.context.new_page()
        self.addCleanup(page.close)
        page.goto(self.url("/projects/sandbox/windmill"))
        page.get_by_text("builder · open", exact=True).wait_for(timeout=30_000)
        self.assertEqual(page.url, self.url("/projects/sandbox/windmill"))
        self.assertEqual(self._project("sandbox/windmill")["state"], "open")

    def test_the_studio_title_returns_to_the_projects_home(self) -> None:
        self._make_project("sandbox/windmill")
        self._open("sandbox/windmill")

        self.page.goto(self.url("/projects/sandbox/windmill"))
        home = self.page.get_by_role("link", name="Machinome Studio")
        home.wait_for(timeout=10_000)
        self.assertEqual(home.get_attribute("href"), "/")
        home.click()
        self.page.wait_for_url(self.url("/"), timeout=5_000)
        self.page.get_by_role("heading", name="Projects").wait_for()

        # And from a folder, without closing anything.
        self.page.goto(self.url("/folders/sandbox"))
        self.page.get_by_role("link", name="Machinome Studio").click()
        self.page.wait_for_url(self.url("/"), timeout=5_000)
        self.page.get_by_role("heading", name="Projects").wait_for()

    def test_closing_a_project_returns_to_the_folder_that_lists_it(self) -> None:
        self._make_project("sandbox/windmill")
        self._open("sandbox/windmill")

        self.page.goto(self.url("/projects/sandbox/windmill"))
        self.page.get_by_text("Machinome Studio / sandbox/windmill").wait_for(timeout=10_000)
        self.page.get_by_role("button", name="Close project").click()

        self.page.wait_for_url(self.url("/folders/sandbox"), timeout=5_000)
        self.page.get_by_role("heading", name="sandbox").wait_for()

    def _make_project(self, name: str, models: tuple[str, ...] = ()) -> Path:
        project = self.project_home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text("_build/\n.fake-machinome-builds\n.fake-machinome-state.json\n")
        declared = "".join(f'{model} = "root:Root"\n' for model in models)
        (project / "pyproject.toml").write_text(
            '[tool.machinome-studio]\nprofile = "builder"\n'
            + (f"\n[tool.machinome.models]\n{declared}" if models else "")
        )
        if models:
            (project / ".fake-machinome-state.json").write_text(json.dumps({"models": list(models)}))
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "--all"], check=True)
        subprocess.run([
            "git", "-C", str(project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "fixture",
        ], check=True)
        return project

    def _open(self, path: str) -> str:
        _request(self.url("/api/sessions"), "POST", {"path": path})
        _wait_for(lambda: self._project(path)["state"] in {"open", "failed"})
        project = self._project(path)
        self.assertEqual(project["state"], "open", project.get("failure"))
        return str(project["session_id"])

    def _token_classes(self) -> set[str]:
        markup = self.page.inner_html(".view-lines")
        return set(re.findall(r"mtk\d+", markup))

    def _project(self, path: str) -> dict[str, object]:
        folder, _, _ = path.rpartition("/")
        entries = _request(self.url(f"/api/entries?folder={folder}"), "GET")["entries"]
        return next(item for item in entries if item["path"] == path)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stderr is not None:
            self.process.stderr.close()


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=5) as response:  # nosec: local test service
        data = response.read()
        return json.loads(data) if data else {}


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_for(predicate, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if predicate():
                return
        except (OSError, StopIteration):
            pass
        time.sleep(.05)
    raise AssertionError("condition did not become true")


if __name__ == "__main__":
    unittest.main()
