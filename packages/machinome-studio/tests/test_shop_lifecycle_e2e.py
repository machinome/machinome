from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from tests.fixtures.primary_shop import isolated_primary_shop, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"


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
        self.shop = self.enterContext(isolated_primary_shop())
        self.port = _free_port()
        self.process = subprocess.Popen(
            [
                "python", "-m", "floor", "--port", str(self.port),
                "--project-home", str(self.project_home),
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
        self.page.get_by_text("SolidNode Studio / new_bracket").wait_for()
        self.page.get_by_role("button", name="Close project").click()
        self.page.wait_for_url(self.url("/"), timeout=5_000)
        self.page.get_by_role("heading", name="Projects").wait_for()

    def test_two_workspace_pages_show_only_their_own_conversation(self) -> None:
        self._make_project("alpha")
        self._make_project("bravo")
        alpha = self._open("alpha")
        bravo = self._open("bravo")
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

    def _make_project(self, name: str) -> Path:
        project = self.project_home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text("_build/\n.fake-solid-builds\n.fake-solid-state.json\n")
        (project / "pyproject.toml").write_text('[tool.solid-node-studio]\nprofile = "builder"\n')
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
