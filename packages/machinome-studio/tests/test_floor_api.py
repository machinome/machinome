from __future__ import annotations

import json
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


class FloorAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.process = subprocess.Popen(
            ["python", "-m", "floor", "--port", str(self.port)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self._stop_floor)
        _wait_for_health(self.url("/health"))

    def test_default_and_configured_server_surface_tracks_agent_work(self) -> None:
        self.assertEqual(_request(self.url("/health"), "GET"), {"status": "open"})
        self.assertEqual(_request(self.url("/api/runs/latest"), "GET")["agents"], [])
        manifested = _request(
            self.url("/api/runs/shop-floor/agents"),
            "POST",
            {"role": "designer", "label": "Designer"},
        )
        self.assertEqual(manifested["state"], "waiting")
        _request(
            self.url("/api/runs/shop-floor/agents/designer/assignments"),
            "POST",
            {"assignment_id": "drawing-1"},
        )
        self.assertEqual(_request(self.url("/api/runs/latest"), "GET")["agents"][0]["state"], "waiting")
        acknowledged = _request(
            self.url("/api/runs/shop-floor/agents/designer/acknowledgments"),
            "POST",
            {"assignment_id": "drawing-1"},
        )
        self.assertEqual(acknowledged["state"], "active")
        completed = _request(
            self.url("/api/runs/shop-floor/agents/designer/completions"),
            "POST",
            {"assignment_id": "drawing-1"},
        )
        self.assertEqual(completed["state"], "waiting")
        self.assertEqual(_status(self.url("/api/runs/shop-floor/agents/unknown/acknowledgments"), "POST", {"assignment_id": "x"}), 404)
        self.assertEqual(_status(self.url("/api/runs/shop-floor/agents/designer/completions"), "POST", {"assignment_id": "x"}), 409)
        self.assertEqual(_status(self.url("/api/runs/shop-floor/agents/designer"), "DELETE"), 204)
        self.assertEqual(_request(self.url("/api/runs/latest"), "GET")["agents"], [])

    def test_foreman_conversation_is_ordered_and_survives_a_browser_snapshot(self) -> None:
        first = _request(
            self.url("/api/runs/shop-floor/conversation/maker"),
            "POST",
            {"text": "Build the bracket."},
        )
        foreman = _request(
            self.url("/api/runs/shop-floor/foreman/publish"),
            "POST",
            {"text": "I will inspect the drawing first."},
        )
        second = _request(
            self.url("/api/runs/shop-floor/conversation/maker"),
            "POST",
            {"text": "Use the thinner stock."},
        )

        conversation = _request(self.url("/api/runs/shop-floor/conversation"), "GET")
        self.assertEqual(
            conversation["entries"],
            [first, foreman, second],
            "a freshly loaded browser snapshot must retain the recorded order",
        )
        self.assertEqual(_status(self.url("/api/runs/shop-floor/conversation/maker"), "POST", {"text": "   "}), 400)

    def test_orchestrator_stream_blocks_then_emits_ordered_maker_direction(self) -> None:
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
            self.url("/api/runs/shop-floor/conversation/maker"),
            "POST",
            {"text": "Start with the frame."},
        )
        _request(
            self.url("/api/runs/shop-floor/conversation/maker"),
            "POST",
            {"text": "Add gussets."},
        )
        _request(
            self.url("/api/runs/shop-floor/conversation/maker"),
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

    def test_valid_callback_publishes_model_changed_event(self) -> None:
        self._restart_floor(Path(tempfile.mkdtemp()), callback_token="opaque")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.project, ignore_errors=True))
        self.assertEqual(_status(self.url("/api/runs/shop-floor/model/ready/wrong"), "POST"), 404)
        self.assertEqual(_status(self.url("/api/runs/shop-floor/model/ready/opaque"), "POST"), 204)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _restart_floor(self, project: Path, callback_token: str | None = None) -> None:
        self._stop_floor()
        self.project = project
        command = ["python", "-m", "floor", "--port", str(self.port), "--project", str(project), "--solid-command", "true"]
        if callback_token:
            command += ["--callback-token", callback_token]
        self.process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        _wait_for_health(self.url("/health"))

    def _stop_floor(self) -> None:
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
