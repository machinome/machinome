# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
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
                result = refresh_project_screenshot(project, ("machinome",))

            self.assertTrue(result.updated)
            self.assertEqual(observed[:4], ["machinome", "snapshot", "--renderer", "web"])
            # The web renderer rejects the OpenSCAD-only presentation options.
            self.assertNotIn("--projection", observed)
            self.assertEqual(screenshot_path(project).read_bytes(), PNG)


class ModelScreenshotTest(unittest.TestCase):
    """A project declaring several models keeps one preview per model."""

    def render(self, project: Path, model: str | None, payload: bytes = PNG):
        observed: list[str] = []

        def render(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            observed.extend(command)
            Path(command[command.index("-o") + 1]).write_bytes(payload)
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch("floor.screenshots.subprocess.run", side_effect=render):
            result = refresh_project_screenshot(project, ("machinome",), model=model)
        return result, observed

    def test_a_named_model_publishes_beside_its_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "clocks"
            project.mkdir()

            result, observed = self.render(project, "wall_clock_02")

            self.assertTrue(result.updated)
            self.assertEqual(observed[:3], ["machinome", "snapshot", "wall_clock_02"])
            self.assertEqual(screenshot_path(project, "wall_clock_02"),
                             project / "screenshots" / "wall_clock_02.png")
            self.assertEqual((project / "screenshots" / "wall_clock_02.png").read_bytes(), PNG)
            self.assertFalse((project / "screenshot.png").exists())

    def test_one_model_does_not_disturb_another(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "clocks"
            project.mkdir()
            self.render(project, "wall_clock_01")
            first = (project / "screenshots" / "wall_clock_01.png").read_bytes()

            self.render(project, "wall_clock_02", PNG + b"\n")

            self.assertEqual((project / "screenshots" / "wall_clock_01.png").read_bytes(), first)
            self.assertNotEqual((project / "screenshots" / "wall_clock_02.png").read_bytes(), first)

    def test_a_single_model_project_keeps_the_root_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "engine"
            project.mkdir()

            _result, observed = self.render(project, None)

            self.assertEqual(observed[:3], ["machinome", "snapshot", "--renderer"])
            self.assertEqual((project / "screenshot.png").read_bytes(), PNG)
            self.assertFalse((project / "screenshots").exists())
