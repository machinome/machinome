from __future__ import annotations

import json
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class ShopLifecycleE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self._start_floor()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def _start_floor(self, project: Path | None = None) -> None:
        command = ["python", "-m", "floor", "--port", str(self.port)]
        if project is not None:
            command += ["--project", str(project), "--solid-command", "true"]
        self.floor = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        _wait_for_health(self.url("/health"))

    def tearDown(self) -> None:
        self.browser.close()
        self.playwright.stop()
        self._stop_floor()

    def test_roster_updates_without_reloading(self) -> None:
        self.page.goto(self.url("/"))
        self.page.get_by_text("Shop is open").wait_for()
        self.page.get_by_role("complementary", name="Shop menu").wait_for()
        self.page.get_by_role("region", name="Artifact view").get_by_text("No artifact selected.").wait_for()
        self.page.get_by_role("region", name="Chat").get_by_role("textbox", name="Message").wait_for()
        self._stop_floor()
        self.page.get_by_text("Shop is closed").wait_for(timeout=5_000)
        self._start_floor()
        self.page.get_by_text("Shop is open").wait_for(timeout=5_000)
        self.page.get_by_text("No agents are currently manifested.").wait_for()
        self.page.wait_for_timeout(100)
        _request(self.url("/api/runs/shop-floor/agents"), "POST", {"role": "machinist", "label": "Machinist"})
        row = self.page.locator('[data-agent-role="machinist"]')
        row.get_by_text("waiting").wait_for(timeout=500)
        _request(self.url("/api/runs/shop-floor/agents/machinist/assignments"), "POST", {"assignment_id": "work-1"})
        _request(self.url("/api/runs/shop-floor/agents/machinist/acknowledgments"), "POST", {"assignment_id": "work-1"})
        row.get_by_text("active").wait_for(timeout=500)
        _request(self.url("/api/runs/shop-floor/agents/machinist/completions"), "POST", {"assignment_id": "work-1"})
        row.get_by_text("waiting").wait_for(timeout=500)
        _request(self.url("/api/runs/shop-floor/agents/machinist"), "DELETE")
        self.page.get_by_text("No agents are currently manifested.").wait_for(timeout=500)

    def test_maker_can_direct_the_foreman_and_reload_the_conversation(self) -> None:
        self.page.goto(self.url("/"))
        conversation = self.page.get_by_role("region", name="Chat")
        composer = conversation.get_by_role("textbox", name="Message")
        composer.fill("Please begin with the housing.")
        conversation.get_by_role("button", name="Send").click()
        conversation.get_by_text("Please begin with the housing.").wait_for()
        self.assertEqual(self.page.get_by_text("Foreman conversation", exact=True).count(), 0)
        self.assertEqual(self.page.get_by_text("Message to foreman", exact=True).count(), 0)

        for index in range(20):
            _request(
                self.url("/api/runs/shop-floor/foreman/publish"),
                "POST",
                {"text": f"Progress update {index}: reviewing the drawing details."},
            )
        transcript = conversation.get_by_role("list", name="Conversation transcript")
        transcript.get_by_text("Progress update 19: reviewing the drawing details.").wait_for(timeout=1_000)
        transcript.evaluate("element => { element.scrollTop = 0; }")

        _request(
            self.url("/api/runs/shop-floor/foreman/publish"),
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
        self.assertEqual(messages[-1], "ForemanI will review the drawing and report back.")

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
        message = conversation.locator('[data-conversation-author="maker"]')
        message.wait_for()
        self.assertEqual(message.text_content(), "MakerFirst line\nSecond line")

    def test_workspace_has_no_horizontal_overflow_on_a_narrow_viewport(self) -> None:
        self.page.set_viewport_size({"width": 375, "height": 800})
        self.page.goto(self.url("/"))
        self.page.get_by_role("complementary", name="Shop menu").wait_for()
        self.assertTrue(
            self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),
            "workspace must not require horizontal page scrolling",
        )

    def test_desktop_workspace_keeps_the_menu_and_both_content_areas_visible(self) -> None:
        self.page.set_viewport_size({"width": 1440, "height": 900})
        self.page.goto(self.url("/"))
        menu = self.page.get_by_role("complementary", name="Shop menu").bounding_box()
        view = self.page.get_by_role("region", name="Artifact view").bounding_box()
        chat = self.page.get_by_role("region", name="Chat").bounding_box()
        self.assertIsNotNone(menu)
        self.assertIsNotNone(view)
        self.assertIsNotNone(chat)
        assert menu is not None and view is not None and chat is not None
        self.assertAlmostEqual(menu["y"], 0, delta=1)
        self.assertAlmostEqual(menu["height"], 900, delta=1)
        self.assertGreaterEqual(view["x"], menu["x"] + menu["width"] - 1)
        self.assertAlmostEqual(view["y"], 0, delta=1)
        self.assertAlmostEqual(chat["y"], view["y"] + view["height"], delta=1)
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
        canvas = self.page.get_by_role("region", name="Artifact view").get_by_role("img", name="Functional model")
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


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=5) as response:  # nosec: local floor service
        data = response.read()
        return json.loads(data) if data else {}


def _wait_for_health(url: str) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            if _request(url, "GET") == {"status": "open"}:
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"floor did not become ready at {url}")
