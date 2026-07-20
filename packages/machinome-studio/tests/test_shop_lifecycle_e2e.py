from __future__ import annotations

import json
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class ShopLifecycleE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        temporary = Path(self.temporary.name)
        self.binary = temporary / "shop-floor"
        self.state_file = temporary / "shop-floor.pid"
        self.port = _free_port()
        subprocess.run(["go", "build", "-o", str(self.binary), "./cmd/shop-floor"], cwd=ROOT, check=True)
        subprocess.run(
            [str(self.binary), "open", "--port", str(self.port), "--state-file", str(self.state_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def tearDown(self) -> None:
        self.browser.close()
        self.playwright.stop()
        subprocess.run([str(self.binary), "close", "--port", str(self.port), "--state-file", str(self.state_file)], check=False)
        self.temporary.cleanup()

    def test_roster_updates_without_reloading(self) -> None:
        self.page.goto(self.url("/"))
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


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=5) as response:  # nosec: local Go broker
        data = response.read()
        return json.loads(data) if data else {}
