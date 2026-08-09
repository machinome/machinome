from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

from tests.fixtures.primary_shop import isolated_primary_shop, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
FAKE_CODEX_ECHO = ROOT / "tests" / "fixtures" / "fake_codex_echo_server.py"
FAKE_CLAUDE = ROOT / "tests" / "fixtures" / "fake_claude_cli.py"


class ShopLifecycleE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.temporary = tempfile.TemporaryDirectory()
        self.project_home = Path(self.temporary.name) / "projects"
        self.project_home.mkdir()
        self._project_number = 0
        self.shop = self.enterContext(isolated_primary_shop())
        self._start_floor()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def _start_floor(
        self,
        project: Path | None = None,
        *,
        profile: str = "fordesmac",
        orchestrated: bool = False,
        static_root: Path | None = None,
        backend: str = "codex",
        backend_command: Path | None = None,
    ) -> None:
        self._project_number += 1
        name = f"browser-{self._project_number}"
        environment = subprocess_environment({
            **os.environ,
            "GIT_AUTHOR_NAME": "Shop Test",
            "GIT_AUTHOR_EMAIL": "shop@example.invalid",
            "GIT_COMMITTER_NAME": "Shop Test",
            "GIT_COMMITTER_EMAIL": "shop@example.invalid",
        })
        if static_root is not None:
            environment["SHOP_FLOOR_STATIC_ROOT"] = str(static_root)
        if project is not None:
            target = self.project_home / name
            shutil.copytree(project, target)
            (target / ".gitignore").write_text("_build/\n")
            subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
            subprocess.run(["git", "-C", str(target), "add", "--all"], check=True)
            subprocess.run(["git", "-C", str(target), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid", "commit", "-q", "-m", "fixture"], check=True)
            viewer = target / "_build" / "viewer.json"
            environment["FAKE_SOLID_VIEWER"] = viewer.read_text()
            value = json.loads(viewer.read_text())
            model = value["root"]["model"]
            environment["FAKE_SOLID_MODEL"] = model
            environment["FAKE_SOLID_MODEL_CONTENT"] = (target / "_build" / model).read_text()
        self.project = target if project is not None else self.project_home / name
        if backend != "codex":
            if not self.project.exists():
                (self.project / "root").mkdir(parents=True)
                (self.project / "root" / "__init__.py").write_text("# project runtime fixture\n")
                (self.project / ".gitignore").write_text("_build/\n")
                subprocess.run(["git", "init", "-q", "-b", "main", str(self.project)], check=True)
            agents = ["builder"] if profile == "builder" else ["foreman", "designer", "machinist", "librarian"]
            runtime = "claude:sonnet" if backend == "claude" else "opencode:openai:gpt-5.4"
            with (self.project / "pyproject.toml").open("a") as manifest:
                manifest.write("\n[tool.solid-node-studio.agents]\n")
                for agent in agents:
                    manifest.write(f'{agent} = "{runtime}"\n')
            subprocess.run(["git", "-C", str(self.project), "add", "--all"], check=True)
            subprocess.run(
                ["git", "-C", str(self.project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid", "commit", "-q", "-m", "runtime fixture"],
                check=True,
            )
        module = "floor.orchestrator" if orchestrated else "floor"
        command = [
            "python",
            "-m",
            module,
            name,
            "--profile",
            profile,
            "--port",
            str(self.port),
            "--project-home",
            str(self.project_home),
            "--solid-command",
            str(FAKE_SOLID),
        ]
        if orchestrated:
            command.extend(
                (
                    "--cwd",
                    str(self.shop),
                    "--backend-command",
                    f"{backend}={backend_command or FAKE_CODEX_ECHO}",
                )
            )
        self.floor = subprocess.Popen(
            command,
            cwd=self.shop,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        _wait_for_health(self.url("/health"))

    def tearDown(self) -> None:
        self.browser.close()
        self.playwright.stop()
        self._stop_floor()
        self.temporary.cleanup()


    def test_initial_floor_build_renders_without_a_lifecycle_reload_race(self) -> None:
        self.page.goto(self.url("/"))
        self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model").wait_for(timeout=5_000)

    def test_workspace_presents_the_solidnode_studio_brand(self) -> None:
        self.page.goto(self.url("/"))
        self.assertEqual(self.page.title(), "SolidNode Studio")
        self.assertEqual(self.page.get_by_text("SolidNode Studio", exact=True).count(), 1)

    def test_agent_panel_updates_live_and_deferred_rail_items_do_not_navigate(self) -> None:
        for role, label in (("foreman", "Foreman"), ("designer", "Designer"), ("machinist", "Machinist"), ("librarian", "Librarian")):
            _request(self.url("/api/runs/shop-floor/agents"), "POST", {"role": role, "label": label})
        self.page.goto(self.url("/"))
        panel = self.page.get_by_role("complementary", name="Agent context")
        panel.get_by_role("heading", name="Agents").wait_for()
        for role in ("foreman", "designer", "machinist", "librarian"):
            self.assertEqual(panel.locator(f'[data-agent-role="{role}"][data-agent-state="waiting"]').count(), 1)

        _request(self.url("/api/runs/shop-floor/agents/designer/assignments"), "POST", {"assignment_id": "drawing-1"})
        _request(self.url("/api/runs/shop-floor/agents/designer/acknowledgments"), "POST", {"assignment_id": "drawing-1"})
        panel.locator('[data-agent-role="designer"][data-agent-state="active"]').wait_for()
        self.assertEqual(self.page.get_by_role("log", name="Broker events").count(), 0)

        files = self.page.locator('[data-workspace-area="files"]')
        before = self.page.url
        files.hover()
        self.assertEqual(self.page.url, before)
        self.assertEqual(self.page.locator('[data-workspace-area="model"][aria-current="page"]').count(), 1)

    def test_maker_can_direct_the_foreman_and_reload_the_conversation(self) -> None:
        self.page.goto(self.url("/"))
        conversation = self.page.get_by_role("region", name="Chat")
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("Please begin with the housing.")
        conversation.get_by_role("button", name="Send").click()
        conversation.locator(
            '[data-conversation-author="user"]',
            has_text="Please begin with the housing.",
        ).wait_for()
        self.assertEqual(self.page.get_by_text("Foreman conversation", exact=True).count(), 0)
        self.assertEqual(self.page.get_by_text("Message to foreman", exact=True).count(), 0)

        for index in range(20):
            _request(
                self.url("/api/runs/shop-floor/conversation"),
                "POST",
                {"text": f"Progress update {index}: reviewing the drawing details."},
            )
        transcript = conversation.get_by_role("list", name="Conversation transcript")
        transcript.get_by_text("Progress update 19: reviewing the drawing details.").wait_for(timeout=1_000)
        transcript.evaluate("element => { element.scrollTop = 0; }")

        _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "I will review the drawing and report back."},
        )
        conversation.get_by_text("I will review the drawing and report back.").wait_for(timeout=1_000)
        self.assertGreater(transcript.evaluate("element => element.scrollTop"), 0)
        self.page.reload()
        transcript = self.page.get_by_role("region", name="Chat").get_by_role("list", name="Conversation transcript")
        transcript.get_by_text("Please begin with the housing.").wait_for()
        transcript.get_by_text("I will review the drawing and report back.").wait_for()
        messages = transcript.locator("[data-conversation-author]").all_text_contents()
        self.assertEqual(messages[0], "MakerPlease begin with the housing.")
        self.assertEqual(messages[-1], "MakerI will review the drawing and report back.")

    def test_role_limit_failure_is_visible_across_reload_and_foreman_can_resume(self) -> None:
        claude_command = Path(self.temporary.name) / "fake-claude"
        shutil.copy2(FAKE_CLAUDE, claude_command)
        claude_command.chmod(0o755)
        self._stop_floor()
        self._start_floor(
            profile="fordesmac",
            orchestrated=True,
            backend="claude",
            backend_command=claude_command,
        )
        self.page.goto(self.url("/"))
        self.page.locator('[data-agent-role="foreman"]').wait_for(timeout=5_000)
        conversation = self.page.get_by_role("region", name="Chat")
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("SESSION_LIMIT")
        composer.press("Enter")

        notice = conversation.get_by_role("alert")
        notice.get_by_text("Foreman session failed", exact=False).wait_for(timeout=5_000)
        notice.get_by_text("You've hit your session limit · resets 1pm (UTC)", exact=True).wait_for()
        self.assertTrue(composer.is_enabled())

        self.page.reload()
        conversation = self.page.get_by_role("region", name="Chat")
        conversation.get_by_role("alert").get_by_text("Foreman session failed", exact=False).wait_for()
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("Resume the shop now.")
        composer.press("Enter")
        conversation.locator(".role-failure-notice").wait_for(state="detached", timeout=5_000)
        conversation.locator('[data-conversation-author="foreman"]', has_text="FAKE_REPLY").wait_for()

    def test_reconnect_restores_a_conversation_entry_without_legacy_recovery_requests(self) -> None:
        self.page.goto(self.url("/"))
        transcript = self.page.get_by_role("region", name="Chat").get_by_role("list", name="Conversation transcript")
        self.page.context.set_offline(True)
        self.page.route("**/api/runs/latest", lambda route: route.abort())
        self.page.route("**/api/runs/*/stream*", lambda route: route.abort())
        try:
            _request(
                self.url("/api/runs/shop-floor/conversation"),
                "POST",
                {"text": "Recorded while disconnected."},
            )
            self.page.context.set_offline(False)
            restored = transcript.locator(
                '[data-conversation-author="user"]',
                has_text="Recorded while disconnected.",
            )
            restored.wait_for(timeout=5_000)
            self.assertEqual(restored.count(), 1)
        finally:
            self.page.context.set_offline(False)

    def test_reconnect_restores_current_agent_work_without_legacy_recovery_requests(self) -> None:
        self.page.goto(self.url("/"))
        panel = self.page.get_by_role("complementary", name="Agent context")
        self.page.context.set_offline(True)
        self.page.route("**/api/runs/latest", lambda route: route.abort())
        self.page.route("**/api/runs/*/stream*", lambda route: route.abort())
        try:
            _request(self.url("/api/runs/shop-floor/agents"), "POST", {"role": "designer", "label": "Designer"})
            _request(
                self.url("/api/runs/shop-floor/agents/designer/assignments"),
                "POST",
                {"assignment_id": "offline-drawing"},
            )
            _request(
                self.url("/api/runs/shop-floor/agents/designer/acknowledgments"),
                "POST",
                {"assignment_id": "offline-drawing"},
            )
            self.page.context.set_offline(False)
            active = panel.locator('[data-agent-role="designer"][data-agent-state="active"]')
            active.wait_for(timeout=5_000)
            self.assertEqual(active.count(), 1)
        finally:
            self.page.context.set_offline(False)

    def test_open_page_recovers_current_and_subsequent_state_after_floor_restart(self) -> None:
        self.page.goto(self.url("/"))
        self.page.get_by_role("complementary", name="Agent context").wait_for()
        for index in range(5):
            _request(self.url("/api/runs/shop-floor/conversation"), "POST", {"text": f"Old process {index}"})
        self.page.get_by_text("Old process 4").wait_for()
        self.page.route("**/api/runs/latest", lambda route: route.abort())

        self._stop_floor()
        self._start_floor()
        self.page.wait_for_function(
            "() => !document.body.innerText.includes('Old process 4')",
            timeout=10_000,
        )
        _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "New process conversation."},
        )
        _request(self.url("/api/runs/shop-floor/agents"), "POST", {"role": "designer", "label": "Designer"})
        _request(
            self.url("/api/runs/shop-floor/agents/designer/assignments"),
            "POST",
            {"assignment_id": "restart-drawing"},
        )
        _request(
            self.url("/api/runs/shop-floor/agents/designer/acknowledgments"),
            "POST",
            {"assignment_id": "restart-drawing"},
        )

        self.page.get_by_text("New process conversation.").wait_for(timeout=5_000)
        self.page.locator('[data-agent-role="designer"][data-agent-state="active"]').wait_for(timeout=5_000)

    def test_idle_page_does_not_repeat_run_state_or_conversation_requests(self) -> None:
        requests: list[str] = []
        self.page.on("request", lambda request: requests.append(request.url))
        self.page.goto(self.url("/"))
        self.page.get_by_role("complementary", name="Agent context").wait_for()
        requests.clear()

        self.page.wait_for_timeout(2_200)

        repeated = [
            url for url in requests
            if url.endswith("/api/runs/latest") or ("/api/runs/" in url and url.endswith("/conversation"))
        ]
        self.assertEqual(repeated, [])

    def test_chat_composer_sends_with_enter_and_adds_lines_with_control_enter(self) -> None:
        self.page.goto(self.url("/"))
        conversation = self.page.get_by_role("region", name="Chat")
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("First line")
        composer.press("Control+Enter")
        composer.type("Second line")
        self.assertEqual(composer.input_value(), "First line\nSecond line")
        self.assertEqual(conversation.get_by_role("list").locator("[data-conversation-author]").count(), 0)
        composer.press("Enter")
        message = conversation.locator('[data-conversation-author="user"]')
        message.wait_for()
        self.assertEqual(message.text_content(), "MakerFirst line\nSecond line")

    def test_builder_profile_is_direct_and_uses_the_profile_neutral_browser_contract(self) -> None:
        self._stop_floor()
        self._start_floor(profile="builder", orchestrated=True)
        self.page.goto(self.url("/"))

        panel = self.page.get_by_role("complementary", name="Agent context")
        waiting = panel.locator('[data-agent-role="builder"][data-agent-state="waiting"]')
        waiting.wait_for()
        self.assertEqual(waiting.count(), 1)
        self.assertEqual(panel.get_by_text("Foreman", exact=True).count(), 0)
        self.assertEqual(
            _status(
                self.url("/api/runs/shop-floor/agents/builder/assignments"),
                "POST",
                {"assignment_id": "forbidden"},
            ),
            409,
        )

        conversation = self.page.get_by_role("region", name="Chat")
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("First line")
        composer.press("Control+Enter")
        composer.type("Second line")
        self.assertEqual(composer.input_value(), "First line\nSecond line")
        composer.press("Enter")
        transcript = conversation.get_by_role("list", name="Conversation transcript")
        transcript.locator('[data-conversation-author="user"]', has_text="First line").wait_for()
        first_echo = transcript.locator('[data-conversation-author="builder"]', has_text="First line")
        first_echo.wait_for()
        active = panel.locator('[data-agent-role="builder"][data-agent-state="active"]')
        active.wait_for()

        composer.fill("Steer direct work")
        composer.press("Enter")
        transcript.locator('[data-conversation-author="builder"]', has_text="Steer direct work").wait_for()
        self.assertEqual(active.count(), 1)

        composer.fill("SETTLE_TURN")
        composer.press("Enter")
        transcript.locator('[data-conversation-author="builder"]', has_text="SETTLE_TURN").wait_for()
        waiting.wait_for()

        for index in range(20):
            _request(self.url("/api/runs/shop-floor/conversation"), "POST", {"text": f"Builder update {index}"})
        transcript.locator('[data-conversation-author="user"]', has_text="Builder update 19").wait_for()
        transcript.evaluate("element => { element.scrollTop = 0; }")
        _request(self.url("/api/runs/shop-floor/conversation"), "POST", {"text": "Newest Builder direction"})
        transcript.locator('[data-conversation-author="user"]', has_text="Newest Builder direction").wait_for()
        self.assertGreater(transcript.evaluate("element => element.scrollTop"), 0)

    def test_workspace_has_no_horizontal_overflow_on_a_narrow_viewport(self) -> None:
        self.page.set_viewport_size({"width": 375, "height": 800})
        self.page.goto(self.url("/"))
        self.page.get_by_role("complementary", name="Agent context").wait_for()
        self.assertTrue(
            self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),
            "workspace must not require horizontal page scrolling",
        )

    def test_desktop_workspace_keeps_the_rail_panel_viewport_and_chat_visible(self) -> None:
        self.page.set_viewport_size({"width": 1440, "height": 900})
        self.page.goto(self.url("/"))
        rail = self.page.get_by_role("navigation", name="Workspace areas").bounding_box()
        panel = self.page.get_by_role("complementary", name="Agent context").bounding_box()
        view = self.page.get_by_role("region", name="Model").bounding_box()
        chat = self.page.get_by_role("region", name="Chat").bounding_box()
        self.assertIsNotNone(rail)
        self.assertIsNotNone(panel)
        self.assertIsNotNone(view)
        self.assertIsNotNone(chat)
        assert rail is not None and panel is not None and view is not None and chat is not None
        self.assertAlmostEqual(rail["y"], 38, delta=1)
        self.assertGreaterEqual(panel["x"], rail["x"] + rail["width"] - 1)
        self.assertGreaterEqual(view["x"], panel["x"] + panel["width"] - 1)
        self.assertGreaterEqual(chat["x"], view["x"] + view["width"] - 1)
        self.assertGreater(view["height"], 0)
        self.assertGreater(chat["height"], 0)

    def test_built_model_is_rendered_from_static_build_artifacts(self) -> None:
        project = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(project, ignore_errors=True))
        build = project / "_build"
        build.mkdir()
        (project / "__init__.py").write_text("this source must not be imported")
        (build / "viewer.json").write_text(
            '{"version": 1, "animation": {"fps": 30, "frames": 360}, '
            '"root": {"name": "part", "color": "#22c55e", '
            '"operations": [["t", ["10 * cos(360 * $t)", "0", "0"]]], "model": "part.stl"}}'
        )
        (build / "part.stl").write_text("solid part\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 10 0 0\nvertex 0 10 0\nendloop\nendfacet\nendsolid part\n")
        self._stop_floor()
        self._start_floor(project)
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        self.page.wait_for_timeout(250)
        timeline = self.page.get_by_role("button", name="Timeline")
        controls = self.page.locator(".animation-controls")
        self.assertTrue(controls.is_hidden(), "timeline controls must not obscure the initial model view")
        timeline.click()
        self.assertTrue(controls.is_visible())
        timeline.click()
        self.assertTrue(controls.is_hidden())
        before_orbit = canvas.screenshot()
        box = canvas.bounding_box()
        assert box is not None
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        self.page.mouse.down()
        self.page.mouse.move(box["x"] + box["width"] * 0.7, box["y"] + box["height"] * 0.6)
        self.page.mouse.up()
        self.page.wait_for_timeout(100)
        self.assertNotEqual(before_orbit, canvas.screenshot(), "orbiting the functional model must redraw the canvas")

    def test_a_republished_artifact_updates_the_existing_canvas_only(self) -> None:
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        self.page.wait_for_timeout(1_100)
        canvas.evaluate("element => { window.__testCanvas = element; }")
        history = self.page.evaluate("window.__solidNodeWidgetHistory")
        self._publish_artifact("part.stl", "solid changed")
        self.page.wait_for_function("() => window.__solidNodeWidgetHistory.updates.some(([kind, path]) => kind === 'artifactChanged' && path === 'part.stl')", timeout=5_000)
        self.assertTrue(canvas.evaluate("element => element === window.__testCanvas"))
        current = self.page.evaluate("window.__solidNodeWidgetHistory")
        self.assertEqual(current["mounts"], 1)
        self.assertEqual(current["fetches"][len(history["fetches"]):], ["/artifacts/part.stl"])

    def test_a_manifest_published_between_snapshot_and_stream_updates_without_reload(self) -> None:
        """A Snowman-style assembly-to-fusion update cannot be lost at startup."""
        fusion = self.project / "_build" / "fusion.stl"
        fusion.write_text("solid fused snowman")
        published = False

        def publish_after_snapshot(response):
            nonlocal published
            if response.url.endswith("/api/stream") and not published:
                published = True
                self._publish_artifact(
                    "viewer.json",
                    json.dumps({"version": 2, "root": {"name": "snowman", "model": "fusion.stl"}}),
                )

        self.page.on("response", publish_after_snapshot)
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        canvas.evaluate("element => { window.__testCanvas = element; }")
        self.page.wait_for_function(
            "() => window.__solidNodeWidgetHistory.updates.some(([kind]) => kind === 'manifestChanged')",
            timeout=5_000,
        )
        self.assertTrue(canvas.evaluate("element => element === window.__testCanvas"))
        self.assertEqual(self.page.evaluate("window.__solidNodeWidgetHistory.mounts"), 1)

    def test_a_failed_targeted_update_keeps_the_model_and_recovers(self) -> None:
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        self.page.wait_for_timeout(1_100)
        canvas.evaluate("element => { window.__testCanvas = element; }")
        self._publish_artifact("viewer.json", json.dumps({"version": 2, "root": {"name": "missing", "model": "missing.stl"}}))
        self.page.get_by_text("Failed to load /artifacts/missing.stl").wait_for(timeout=5_000)
        self.assertTrue(canvas.evaluate("element => element === window.__testCanvas"))
        self._publish_artifact("viewer.json", json.dumps({"version": 3, "root": {"name": "part", "model": "part.stl"}}))
        self.page.wait_for_function("() => !document.body.innerText.includes('Failed to load /artifacts/missing.stl')", timeout=5_000)
        self.assertTrue(canvas.evaluate("element => element === window.__testCanvas"))

    def test_document_only_and_node_removal_updates_do_not_fetch_geometry(self) -> None:
        self.page.goto(self.url("/"))
        self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model").wait_for()
        self.page.wait_for_timeout(1_100)
        history = self.page.evaluate("window.__solidNodeWidgetHistory")
        self._publish_artifact("viewer.json", json.dumps({"version": 2, "root": {"name": "part", "color": "#22c55e", "model": "part.stl"}}))
        self.page.wait_for_function("() => window.__solidNodeWidgetHistory.updates.some(([kind]) => kind === 'manifestChanged')", timeout=5_000)
        current = self.page.evaluate("window.__solidNodeWidgetHistory")
        self.assertEqual(current["fetches"][len(history["fetches"]):], ["/artifacts/viewer.json"])
        history = current
        self._publish_artifact("viewer.json", json.dumps({"version": 3, "root": {"name": "empty"}}))
        self.page.wait_for_function("() => window.__solidNodeWidgetHistory.updates.filter(([kind]) => kind === 'manifestChanged').length === 2", timeout=5_000)
        current = self.page.evaluate("window.__solidNodeWidgetHistory")
        self.assertEqual(current["fetches"][len(history["fetches"]):], ["/artifacts/viewer.json"])

    def test_a_development_build_mounts_the_viewer_exactly_once(self) -> None:
        # The shipped bundle is a production build, where React runs each effect
        # once. A mount effect that cannot survive being torn down and re-run --
        # which StrictMode does on every development mount -- leaves no trace in
        # any other test here, so the maker meets it before the suite does.
        bundle = Path(self.temporary.name) / "development-static"
        _build_frontend(bundle)
        self._stop_floor()
        self._start_floor(static_root=bundle)
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for(timeout=5_000)
        canvas.evaluate("element => { window.__testCanvas = element; }")
        self.assertEqual(self.page.evaluate("window.__solidNodeWidgetHistory.mounts"), 1)
        self._publish_artifact("part.stl", "solid changed")
        self.page.wait_for_function("() => window.__solidNodeWidgetHistory.updates.some(([kind, path]) => kind === 'artifactChanged' && path === 'part.stl')", timeout=5_000)
        self.assertTrue(canvas.evaluate("element => element === window.__testCanvas"))
        history = self.page.evaluate("window.__solidNodeWidgetHistory")
        self.assertEqual(history["mounts"], 1)
        self.assertEqual([update for update in history["updates"] if update[0] == "artifactChanged"], [["artifactChanged", "part.stl"]])

    def _publish_artifact(self, name: str, content: str) -> None:
        target = self.project / "_build" / name
        temporary = target.with_name(f".{name}.test")
        temporary.write_text(content)
        os.replace(temporary, target)

    def test_reloads_the_initial_build_when_a_new_project_floor_reopens(self) -> None:
        first = Path(tempfile.mkdtemp())
        second = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(first, ignore_errors=True))
        self.addCleanup(lambda: __import__("shutil").rmtree(second, ignore_errors=True))
        _fixture_project(first, "first", "first.stl", "0 0 0\n10 0 0\n0 10 0")
        _fixture_project(second, "second", "second.stl", "0 0 0\n40 0 0\n0 40 0")

        self._stop_floor()
        self._start_floor(first)
        self.page.goto(self.url("/"))
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        first_render = canvas.screenshot()

        self._stop_floor()
        self._start_floor(second)
        self.page.wait_for_timeout(250)
        canvas = self.page.get_by_role("region", name="Model").get_by_role("img", name="Functional model")
        canvas.wait_for()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and canvas.screenshot() == first_render:
            self.page.wait_for_timeout(100)
        self.assertNotEqual(first_render, canvas.screenshot(), "reopening on a new project must replace the previous project render")

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _stop_floor(self) -> None:
        self.floor.terminate()
        try:
            self.floor.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.floor.kill()
            self.floor.wait(timeout=5)
        if self.floor.stderr is not None:
            self.floor.stderr.close()


def _build_frontend(destination: Path) -> None:
    """Build the floor's browser bundle in development mode into ``destination``."""
    frontend = ROOT / "floor" / "frontend"
    if not (frontend / "node_modules").is_dir():
        raise unittest.SkipTest(f"{frontend}/node_modules is absent; run npm install to exercise the development bundle")
    subprocess.run(
        ["npx", "vite", "build", "--mode", "development", "--outDir", str(destination), "--emptyOutDir"],
        cwd=frontend,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "NODE_ENV": "development"},
    )


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=5) as response:  # nosec: local floor service
        data = response.read()
        return json.loads(data) if data else {}


def _status(url: str, method: str, body: dict[str, str]) -> int:
    request = Request(
        url,
        data=json.dumps(body).encode(),
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=5) as response:  # nosec: local floor service
            return response.status
    except HTTPError as error:
        error.close()
        return error.code


def _fixture_project(project: Path, name: str, model: str, triangle: str) -> None:
    build = project / "_build"
    build.mkdir(parents=True)
    (build / "viewer.json").write_text(json.dumps({"version": 1, "root": {"name": name, "model": model}}))
    vertices = "\n".join(f"vertex {point}" for point in triangle.splitlines())
    (build / model).write_text(
        f"solid {name}\nfacet normal 0 0 1\nouter loop\n{vertices}\nendloop\nendfacet\nendsolid {name}\n"
    )


def _wait_for_health(url: str) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            if _request(url, "GET") == {"status": "open"}:
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"floor did not become ready at {url}")
