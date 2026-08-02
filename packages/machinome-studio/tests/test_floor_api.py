from __future__ import annotations

import json
import socket
import subprocess
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tests.fixtures.primary_shop import isolated_primary_shop, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"


class FloorAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project_home = Path(self.temporary.name) / "projects"
        self.project_home.mkdir()
        self._project_number = 0
        self.shop = self.enterContext(isolated_primary_shop())
        self._start_floor("floor-api")
        self.addCleanup(self._stop_floor)
        _wait_for_health(self.url("/health"))

    def test_default_profile_run_surface_exposes_profile_metadata(self) -> None:
        self.assertEqual(_request(self.url("/health"), "GET"), {"status": "open"})
        run = _request(self.url("/api/runs/latest"), "GET")
        self.assertEqual(run["profile_id"], "builder")
        self.assertEqual(run["user_label"], "Maker")
        self.assertEqual(run["user_agent"], {"id": "builder", "label": "Builder"})
        self.assertEqual(run["roster"], [{"id": "builder", "label": "Builder"}])
        manifested = _request(
            self.url("/api/runs/shop-floor/agents"),
            "POST",
            {"role": "builder", "label": "Builder"},
        )
        self.assertEqual(manifested["state"], "waiting")
        self.assertEqual(_status(self.url("/api/runs/shop-floor/agents/builder/assignments"), "POST", {"assignment_id": "x"}), 409)
        self.assertEqual(_status(self.url("/api/runs/shop-floor/agents/builder"), "DELETE"), 204)
        self.assertEqual(_request(self.url("/api/runs/latest"), "GET")["agents"], [])

    def test_profile_conversation_is_ordered_and_survives_a_browser_snapshot(self) -> None:
        first = _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "Build the bracket."},
        )
        second = _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "Use the thinner stock."},
        )

        conversation = _request(self.url("/api/runs/shop-floor/conversation"), "GET")
        self.assertEqual(
            conversation["entries"],
            [first, second],
            "a freshly loaded browser snapshot must retain the recorded order",
        )
        self.assertEqual(_status(self.url("/api/runs/shop-floor/conversation"), "POST", {"text": "   "}), 400)

    def test_orchestrator_stream_blocks_then_emits_ordered_user_direction(self) -> None:
        received: list[dict[str, object]] = []

        def wait_for_direction() -> None:
            with urlopen(self.url("/api/runs/shop-floor/orchestrator/stream"), timeout=5) as response:  # nosec: local floor
                for raw_line in response:
                    line = raw_line.decode().strip()
                    if line.startswith("data: "):
                        received.append(json.loads(line.removeprefix("data: ")))
                        if len(received) == 3:
                            return

        listener = threading.Thread(target=wait_for_direction)
        listener.start()
        time.sleep(0.1)
        self.assertTrue(listener.is_alive(), "the orchestrator stream must wait without polling")
        _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "Start with the frame."},
        )
        _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "Add gussets."},
        )
        _request(
            self.url("/api/runs/shop-floor/conversation"),
            "POST",
            {"text": "Keep the corners round."},
        )
        listener.join(timeout=2)
        self.assertFalse(listener.is_alive())
        self.assertEqual([item["body"] for item in received], ["Start with the frame.", "Add gussets.", "Keep the corners round."])
        self.assertEqual([item["sequence"] for item in received], sorted(item["sequence"] for item in received))
        self.assertEqual(_status(self.url("/api/runs/shop-floor/foreman/receive"), "POST", {"after": "0"}), 404)

    def test_serves_only_completed_build_artifacts_and_not_project_source(self) -> None:
        project = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(project, ignore_errors=True))
        build = project / "_build"
        build.mkdir()
        (build / "viewer.json").write_text('{"version": 1, "root": {"name": "part", "model": "part.stl"}}')
        (build / "part.stl").write_text("solid part")

        # A project source file must never be exposed through the artifact route.
        (project / "__init__.py").write_text("raise RuntimeError('must not import')")
        self._restart_floor(project)

        self.assertIn("part.stl", _raw(self.url("/artifacts/viewer.json")))
        self.assertEqual(_raw(self.url("/artifacts/part.stl")), "solid part")
        self.assertEqual(_status(self.url("/artifacts/../__init__.py"), "GET"), 404)

    def test_serves_the_framework_viewer_bundle(self) -> None:
        self.assertIn("SolidNodeWidget", _raw(self.url("/viewer/solid-widget.js")))

    def test_the_removed_model_callback_route_is_gone(self) -> None:
        # The floor refreshes the model itself now; nothing may post a
        # refresh into it. See tests/test_model_watcher.py.
        self.assertEqual(_status(self.url("/api/runs/shop-floor/model/ready/anything"), "POST"), 404)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _restart_floor(self, project: Path) -> None:
        self._stop_floor()
        self._project_number += 1
        name = f"restart-{self._project_number}"
        target = self.project_home / name
        shutil.copytree(project, target)
        (target / ".gitignore").write_text("_build/\n")
        subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "add", "--all"], check=True)
        subprocess.run(["git", "-C", str(target), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid", "commit", "-q", "-m", "fixture"], check=True)
        environment = self._environment()
        viewer = target / "_build" / "viewer.json"
        if viewer.is_file():
            environment["FAKE_SOLID_VIEWER"] = viewer.read_text()
            value = json.loads(viewer.read_text())
            model = value["root"]["model"]
            environment["FAKE_SOLID_MODEL"] = model
            environment["FAKE_SOLID_MODEL_CONTENT"] = (target / "_build" / model).read_text()
        self.project = target
        self._start_floor(name, environment=environment)

    def _start_floor(self, name: str, *, environment: dict[str, str] | None = None) -> None:
        command = ["python", "-m", "floor", name, "--port", str(self.port), "--project-home", str(self.project_home), "--solid-command", str(FAKE_SOLID)]
        self.process = subprocess.Popen(command, cwd=self.shop, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=environment or self._environment())
        _wait_for_health(self.url("/health"))

    @staticmethod
    def _environment() -> dict[str, str]:
        return subprocess_environment({
            **__import__("os").environ,
            "GIT_AUTHOR_NAME": "Shop Test",
            "GIT_AUTHOR_EMAIL": "shop@example.invalid",
            "GIT_COMMITTER_NAME": "Shop Test",
            "GIT_COMMITTER_EMAIL": "shop@example.invalid",
        })

    def _stop_floor(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        if self.process.stderr is not None:
            self.process.stderr.close()


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_for_health(url: str) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            if _request(url, "GET") == {"status": "open"}:
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"floor did not become ready at {url}")


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=5) as response:  # nosec: local floor service
        data = response.read()
        return json.loads(data) if data else {}


def _raw(url: str) -> str:
    with urlopen(url, timeout=5) as response:  # nosec: local floor service
        return response.read().decode()


def _status(url: str, method: str, body: dict[str, str] | None = None) -> int:
    try:
        request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:  # nosec: local floor service
            return response.status
    except HTTPError as error:
        return error.code
