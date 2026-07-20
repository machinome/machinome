"""Real-browser acceptance test for the compiled shop-floor command."""

import shutil
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


class ShopLifecycleE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = Path(tempfile.mkdtemp(prefix="shop-floor-e2e-"))
        cls.binary = cls.temporary_directory / "shop-floor"
        cls.state_file = cls.temporary_directory / "shop-floor.pid"
        cls.port = free_port()
        cls.location = f"http://127.0.0.1:{cls.port}"
        subprocess.run(
            ["go", "build", "-o", str(cls.binary), "./cmd/shop-floor"],
            cwd=ROOT,
            check=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.ask_agent("close")
        finally:
            shutil.rmtree(cls.temporary_directory, ignore_errors=True)

    @classmethod
    def ask_agent(cls, command: str) -> None:
        subprocess.run(
            [
                str(cls.binary), command, "--port", str(cls.port),
                "--state-file", str(cls.state_file),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )

    def test_an_already_open_page_shows_closed_on_shutdown_and_open_after_restart(self) -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context()
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()
            try:
                self.ask_agent("open")
                page.goto(self.location)
                status = page.locator("#shop-status")
                expect(status).to_have_text("Shop is open")

                self.ask_agent("close")
                expect(status).to_have_text("Shop is closed")

                self.ask_agent("open")
                expect(status).to_have_text("Shop is open")
            except Exception:
                Path("test-results").mkdir(exist_ok=True)
                page.screenshot(path="test-results/shop-lifecycle-failure.png")
                raise
            finally:
                Path("test-results").mkdir(exist_ok=True)
                context.tracing.stop(path="test-results/shop-lifecycle-trace.zip")
                context.close()
                browser.close()
