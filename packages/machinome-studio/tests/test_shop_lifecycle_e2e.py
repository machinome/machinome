# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

from tests.fixtures.shop_process import isolated_launch_directory, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
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
        self.port = _free_port()
        self.process = subprocess.Popen(
            [
                "python", "-m", "floor", "--port", str(self.port),
                "--projects-dir", str(self.project_home),
                "--solid-command", str(FAKE_SOLID),
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
                "FAKE_SOLID_NEW_DELAY": "0.5",
            }),
        )
        self.addCleanup(self._stop)
        _wait_for(lambda: _request(self.url("/health"), "GET") == {"status": "open"})
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 900})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()

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
        self.page.get_by_text("LibreSolid Studio / new_bracket").wait_for()
        self.page.get_by_role("button", name="Close project").click()
        self.page.wait_for_url(self.url("/"), timeout=5_000)
        self.page.get_by_role("heading", name="Projects").wait_for()

    def test_the_hub_says_a_presented_model_is_being_brought_up_to_date(self) -> None:
        project = self._make_project("kept-warm")
        # A publication from an earlier run is what the session opens on. The
        # build behind it is held open so the browser can be read while it runs.
        subprocess.run(
            [sys.executable, str(FAKE_SOLID), "build"],
            cwd=project, check=True, capture_output=True,
        )
        gate = Path(self.temporary.name) / "release-build"
        (project / ".fake-solid-state.json").write_text(json.dumps({"build_gate": str(gate)}))

        self.page.goto(self.url("/"))
        self.page.get_by_text("closed · builder", exact=False).wait_for()
        rebuilding = self.page.get_by_text("Bringing the model up to date", exact=False)
        self.assertEqual(rebuilding.count(), 0)

        _request(self.url("/api/projects/kept-warm/session"), "POST")

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
            [sys.executable, str(FAKE_SOLID), "build"],
            cwd=project, check=True, capture_output=True,
        )
        gate = Path(self.temporary.name) / "release-build"
        (project / ".fake-solid-state.json").write_text(json.dumps({"build_gate": str(gate)}))
        self._open("warm-workspace")

        # The maker who clicks the card never sees it; they land here.
        self.page.goto(self.url("/projects/warm-workspace"))
        self.page.get_by_text("LibreSolid Studio / warm-workspace").wait_for()
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
        (project / ".fake-solid-state.json").write_text(json.dumps({"fail": "broken model evidence"}))
        session_id = self._open("broken-model")
        self.page.goto(self.url("/projects/broken-model"))
        self.page.get_by_text("broken model evidence", exact=False).wait_for(timeout=10_000)
        self.page.get_by_role("textbox", name="Message", exact=True).fill("Please repair the model")
        self.page.get_by_role("button", name="Send").click()
        _wait_for(lambda: _request(self.url(f"/api/sessions/{session_id}/conversation"), "GET")["entries"] != [])

    def test_workspace_mounts_the_project_scoped_viewer(self) -> None:
        self._make_project("viewer-project")
        self._open("viewer-project")
        self.page.goto(self.url("/projects/viewer-project"))
        self.page.get_by_role("img", name="Functional model").wait_for(timeout=10_000)
        history = self.page.evaluate("() => window.__solidNodeWidgetHistory")
        self.assertEqual(history["mounts"], 1)
        self.assertIn("/projects/viewer-project/artifacts/viewer.json", history["fetches"])

    def test_build_inspects_one_piece_at_scale_and_downloads_explicit_quantities(self) -> None:
        triangle = (
            "solid part\nfacet normal 0 0 1\nouter loop\n"
            "vertex 0 0 0\nvertex 24 0 0\nvertex 0 18 6\n"
            "endloop\nendfacet\nendsolid part\n"
        )
        project = self._make_project("print-job")
        viewer = {
            "format": "solid-node-export", "version": 1,
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
        (project / ".fake-solid-state.json").write_text(json.dumps({
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
        self.page.get_by_role("button", name="Expand root").click()
        self.page.get_by_title("root/__init__.py").click()
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
        _wait_for(lambda: (project / ".fake-solid-builds").read_text().count("build\n") >= 2)
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
        self.assertEqual(self.page.evaluate("() => window.__solidNodeWidgetHistory.mounts"), 1)

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
        folder = self.page.get_by_role("button", name="Expand root")
        folder.wait_for()
        self.assertEqual(self.page.get_by_title("root/__init__.py").count(), 0)
        self.assertEqual(self.page.locator(".source-chip").count(), 0)
        for kind in ("folder", "markdown", "image", "python", "file"):
            with self.subTest(kind=kind):
                self.assertGreaterEqual(self.page.locator(f'[data-source-icon="{kind}"]').count(), 1)
        icon_colors = self.page.locator(".source-icon").evaluate_all(
            "icons => [...new Set(icons.map(icon => getComputedStyle(icon).color))]"
        )
        self.assertEqual(len(icon_colors), 1)

        folder.click()
        self.page.get_by_title("root/__init__.py").wait_for()
        self.assertIsNotNone(self.page.get_by_role("button", name="Collapse root"))
        self.page.get_by_role("button", name="Collapse root").click()
        self.assertEqual(self.page.get_by_title("root/__init__.py").count(), 0)

        self.page.get_by_title("preview.png").click()
        preview = self.page.get_by_role("img", name="Preview preview.png")
        preview.wait_for()
        self.assertEqual(preview.evaluate("image => image.naturalWidth"), 1)
        self.assertEqual(self.page.locator(".monaco-editor").count(), 0)

        self.page.get_by_title("model.py").click()
        self.page.locator(".monaco-editor").wait_for()
        self.page.get_by_text("model = True", exact=False).wait_for()

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
                "state": "completed", "name": "solid_test", "summary": "tests/test_model.py",
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
        self.page.get_by_role("button", name="solid_test", exact=False).click()
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

    def test_model_panel_navigates_the_viewer_assembly(self) -> None:
        project = self._make_project("assembly-project")
        (project / ".fake-solid-state.json").write_text(json.dumps({
            "viewer": {
                "version": 1,
                "root": {
                    "name": "engine", "color": None, "children": [
                        {
                            "name": "housing", "color": "#cc4444",
                            "children": [{"name": "pin", "color": None}],
                        },
                        {"name": "unpainted", "color": None},
                    ],
                },
            },
        }))
        self._open("assembly-project")
        self.page.goto(self.url("/projects/assembly-project"))

        tree = self.page.get_by_role("tree", name="Assembly")
        tree.wait_for(timeout=10_000)
        self.page.get_by_role("heading", name="MODEL", exact=True).wait_for()
        engine_row = tree.get_by_role("treeitem").filter(has_text="engine")
        self.assertIn("focused-root", engine_row.get_attribute("class") or "")
        self.assertEqual(engine_row.get_by_text("root", exact=True).count(), 1)
        self.assertEqual(engine_row.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(28, 33, 40)")
        self.assertEqual(tree.locator(".assembly-row.selected").count(), 0)
        self.assertEqual(self.page.get_by_role("button", name="Show full assembly").count(), 0)
        self.assertEqual(engine_row.get_attribute("aria-expanded"), "true")
        housing_row = tree.get_by_role("treeitem").filter(has_text="housing")
        self.assertEqual(housing_row.get_attribute("aria-expanded"), "false")
        self.assertEqual(self.page.get_by_role("checkbox", name="Visibility for pin").count(), 0)
        housing_row.get_by_role("button", name="Expand housing").click()
        pin_visibility = self.page.get_by_role("checkbox", name="Visibility for pin")
        plain_visibility = self.page.get_by_role("checkbox", name="Visibility for unpainted")
        self.assertTrue(pin_visibility.is_checked())
        self.assertTrue(plain_visibility.is_checked())
        self.assertEqual(pin_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(204, 68, 68)")
        self.assertEqual(plain_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(107, 114, 128)")

        self.page.get_by_role("button", name="Code", exact=True).click()
        self.page.get_by_role("button", name="Model", exact=True).click()
        tree.wait_for()
        self.assertEqual(self.page.evaluate("() => window.__solidNodeWidgetHistory.mounts"), 1)

        housing_row.get_by_text("housing", exact=True).click()
        self.assertIn("focused-root", engine_row.get_attribute("class") or "")
        self.assertNotIn("focused-root", housing_row.get_attribute("class") or "")
        self.assertEqual(tree.locator(".assembly-row.selected").count(), 0)

        plain_row = tree.get_by_role("treeitem").filter(has_text="unpainted")
        plain_focus = plain_row.get_by_role("button", name="Focus unpainted")
        plain_row.hover()
        self.assertEqual(plain_focus.evaluate("element => getComputedStyle(element).opacity"), "1")
        plain_visibility.click()
        self.page.get_by_role("img", name="Functional model").hover()
        self.assertEqual(plain_focus.evaluate("element => getComputedStyle(element).opacity"), "0")

        pin_row = tree.get_by_role("treeitem").filter(has_text="pin")
        pin_focus = pin_row.get_by_role("button", name="Focus pin")
        self.assertEqual(pin_focus.text_content(), "Focus")
        self.assertEqual(pin_focus.evaluate("element => getComputedStyle(element).opacity"), "0")
        pin_row.hover()
        self.assertEqual(pin_focus.evaluate("element => getComputedStyle(element).opacity"), "1")
        pin_focus.click()
        self.assertEqual(pin_row.get_by_text("root", exact=True).count(), 1)
        self.assertEqual(pin_row.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(28, 33, 40)")
        self.assertEqual(pin_row.get_attribute("aria-selected"), "true")
        self.assertEqual(engine_row.get_attribute("aria-selected"), "false")
        self.page.get_by_role("button", name="Show full assembly").click()
        self.assertEqual(engine_row.get_by_text("root", exact=True).count(), 1)
        self.assertEqual(engine_row.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(28, 33, 40)")

        self.page.get_by_text("engine", exact=True).click()
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("ArrowRight")
        self.page.keyboard.press("Space")
        self.assertFalse(pin_visibility.is_checked())
        self.assertEqual(pin_visibility.evaluate("element => getComputedStyle(element).backgroundColor"), "rgba(0, 0, 0, 0)")
        desktop_tree = self.page.get_by_role("tree", name="Assembly").bounding_box()
        desktop_viewer = self.page.get_by_role("img", name="Functional model").bounding_box()
        self.assertIsNotNone(desktop_tree)
        self.assertIsNotNone(desktop_viewer)

        self.page.set_viewport_size({"width": 760, "height": 900})
        pin_visibility.wait_for()
        self.assertFalse(self.page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth"))
        housing_row.hover()
        housing_row.get_by_role("button", name="Focus housing").click()

        (project / ".fake-solid-state.json").write_text(json.dumps({
            "viewer": {
                "version": 1,
                "root": {
                    "name": "engine", "color": None,
                    "children": [{"name": "unpainted", "color": None}],
                },
            },
        }))
        (project / "root" / "__init__.py").write_text("# changed model\n")
        _wait_for(lambda: self.page.get_by_text("pin", exact=True).count() == 0)
        self.assertEqual(self.page.get_by_role("button", name="Show full assembly").count(), 0)

        history = self.page.evaluate("() => window.__solidNodeWidgetHistory")
        self.assertIn(["setVisible", ["housing", "pin"], False], history["updates"])
        self.assertIn(["setRoot", ["housing", "pin"]], history["updates"])
        self.assertIn(["setRoot", None], history["updates"])
        self.assertIn(["manifestChanged"], history["updates"])

    def test_model_panel_controls_the_supplied_framework_viewer(self) -> None:
        project = self._make_project("real-assembly-viewer")
        (project / ".fake-solid-state.json").write_text(json.dumps({
            "viewer": {
                "format": "solid-node-export", "version": 1,
                "animation": {"fps": 24, "frames": 24},
                "root": {
                    "name": "engine", "type": "assembly", "color": None,
                    "operations": [], "children": [
                        {
                            "name": "housing", "type": "assembly",
                            "color": "#cc4444", "operations": [],
                            "children": [{
                                "name": "pin", "type": "assembly",
                                "color": None, "operations": [], "children": [],
                            }],
                        },
                    ],
                },
            },
        }))
        self._open("real-assembly-viewer")
        self.page.goto(self.url("/projects/real-assembly-viewer"))

        tree = self.page.get_by_role("tree", name="Assembly")
        tree.get_by_role("button", name="Expand housing").click()
        checkbox = self.page.get_by_role("checkbox", name="Visibility for pin")
        checkbox.wait_for(timeout=10_000)
        self.assertTrue(checkbox.is_checked())
        checkbox.click()
        self.assertFalse(checkbox.is_checked())
        pin_row = self.page.get_by_role("treeitem").filter(has_text="pin")
        pin_row.hover()
        pin_row.get_by_role("button", name="Focus pin").click()
        self.page.get_by_role("button", name="Show full assembly").click()

    def _make_project(self, name: str) -> Path:
        project = self.project_home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text("_build/\n.fake-solid-builds\n.fake-solid-state.json\n")
        (project / "pyproject.toml").write_text('[tool.libresolid-studio]\nprofile = "builder"\n')
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "--all"], check=True)
        subprocess.run([
            "git", "-C", str(project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "fixture",
        ], check=True)
        return project

    def _open(self, name: str) -> str:
        _request(self.url(f"/api/projects/{name}/session"), "POST")
        _wait_for(lambda: self._project(name)["state"] in {"open", "failed"})
        project = self._project(name)
        self.assertEqual(project["state"], "open", project.get("failure"))
        return str(project["session_id"])

    def _project(self, name: str) -> dict[str, object]:
        return next(item for item in _request(self.url("/api/projects"), "GET")["projects"] if item["name"] == name)

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
