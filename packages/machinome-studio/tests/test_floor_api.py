from __future__ import annotations

import json
import socket
import subprocess
import tempfile
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

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

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


def _status(url: str, method: str, body: dict[str, str] | None = None) -> int:
    try:
        request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:  # nosec: local floor service
            return response.status
    except HTTPError as error:
        return error.code
