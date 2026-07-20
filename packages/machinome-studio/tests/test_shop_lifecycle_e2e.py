from __future__ import annotations

import json
import socket
import subprocess
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

    def _start_floor(self) -> None:
        self.floor = subprocess.Popen(
            ["python", "-m", "floor", "--port", str(self.port)],
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
