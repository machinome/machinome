"""Start and stop the local shop-floor service for Codex."""

import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


class ShopOpenError(RuntimeError):
    """The shop-floor server did not become available."""


class ShopCloseError(RuntimeError):
    """The shop-floor server did not stop after being asked to close."""


class ShopRunner:
    def __init__(self, port: int = 9000, state_file: Path | None = None) -> None:
        self.port = port
        self.location = f"http://127.0.0.1:{port}"
        self.state_file = state_file or Path(tempfile.gettempdir()) / "solid-node-shop-floor.pid"

    def open(self) -> str:
        if self._is_running():
            return self.location
        self.state_file.unlink(missing_ok=True)

        source_root = str(Path(__file__).resolve().parents[1])
        environment = os.environ | {"PYTHONPATH": self._python_path(source_root)}
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "shop_floor.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--timeout-graceful-shutdown",
                "1",
            ],
            env=environment,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.state_file.write_text(str(process.pid))
        if wait_until_available(f"{self.location}/health"):
            return self.location

        process.terminate()
        process.wait(timeout=5)
        self.state_file.unlink(missing_ok=True)
        raise ShopOpenError("Shop-floor could not be opened.")

    def close(self) -> bool:
        if not self.state_file.exists():
            return False
        pid = int(self.state_file.read_text())
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        if not wait_until_unavailable(f"{self.location}/health"):
            raise ShopCloseError("Shop-floor could not be closed.")
        self.state_file.unlink(missing_ok=True)
        return True

    def _is_running(self) -> bool:
        if not self.state_file.exists():
            return False
        try:
            os.kill(int(self.state_file.read_text()), 0)
        except (ProcessLookupError, ValueError):
            return False
        return True

    @staticmethod
    def _python_path(source_root: str) -> str:
        current_path = os.environ.get("PYTHONPATH")
        return source_root if not current_path else f"{source_root}{os.pathsep}{current_path}"


def wait_until_available(location: str, timeout: float = 5) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(location, timeout=0.25) as response:
                if response.status == 200:
                    return True
        except urllib.error.URLError:
            time.sleep(0.05)
    return False


def wait_until_unavailable(location: str, timeout: float = 5) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(location, timeout=0.25):
                time.sleep(0.05)
        except urllib.error.URLError:
            return True
    return False
