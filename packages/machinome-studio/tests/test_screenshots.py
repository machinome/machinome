from __future__ import annotations

import base64
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.screenshots import refresh_project_screenshot, screenshot_path


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEElEQVR42mNk+M/wHwAFAAH/9X2H7gAAAABJRU5ErkJggg=="
)


class WebScreenshotTest(unittest.TestCase):
    def test_uses_web_renderer_and_publishes_its_bytes_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            observed: list[str] = []

            def render(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
                observed.extend(command)
                Path(command[command.index("-o") + 1]).write_bytes(PNG)
                return subprocess.CompletedProcess(command, 0, "", "")

            with patch("floor.screenshots.subprocess.run", side_effect=render):
                result = refresh_project_screenshot(project, ("solid",))

            self.assertTrue(result.updated)
            self.assertEqual(observed[:4], ["solid", "snapshot", "--renderer", "web"])
            # The web renderer rejects the OpenSCAD-only presentation options.
            self.assertNotIn("--projection", observed)
            self.assertEqual(screenshot_path(project).read_bytes(), PNG)
