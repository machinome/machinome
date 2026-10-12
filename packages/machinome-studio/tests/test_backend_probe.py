# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.backends.probe import BACKENDS, probe_backend, probe_backends


class BackendProbeTest(unittest.TestCase):
    def test_only_selectable_backends_are_probed(self) -> None:
        self.assertEqual(BACKENDS, ("claude", "opencode", "codex"))

    def test_codex_is_listed_even_when_missing(self) -> None:
        with patch("floor.backends.probe.shutil.which", return_value=None), patch("floor.backends.probe.subprocess.run") as run:
            values = probe_backends(Path(__file__).resolve().parents[1])
        self.assertEqual([item["id"] for item in values], ["claude", "opencode", "codex"])
        self.assertFalse(values[-1]["found"])
        run.assert_not_called()

    def test_codex_detection_only_requests_version(self) -> None:
        completed = subprocess.CompletedProcess(["/tools/codex", "--version"], 0, "codex-cli 0.157.1\n", "")
        with patch("floor.backends.probe.shutil.which", side_effect=lambda name: "/tools/codex" if name == "codex" else None), patch("floor.backends.probe.subprocess.run", return_value=completed) as run:
            values = probe_backends(Path(__file__).resolve().parents[1])
        codex = next(item for item in values if item["id"] == "codex")
        self.assertTrue(codex["found"])
        self.assertEqual(codex["version"], "codex-cli 0.157.1")
        self.assertIsNone(codex["model"])  # No profile default for explicit-only Codex.
        run.assert_called_once_with(("/tools/codex", "--version"), check=True, capture_output=True, text=True, timeout=5)

    def test_missing_executable_is_reported_without_invoking_it(self) -> None:
        with patch("floor.backends.probe.shutil.which", return_value=None), patch("floor.backends.probe.subprocess.run") as run:
            value = probe_backend("claude", ("sonnet",))
        self.assertEqual(value["found"], False)
        self.assertIsNone(value["executable"])
        self.assertEqual(value["model"], "sonnet")
        run.assert_not_called()

    def test_unreadable_codex_version_does_not_hide_the_backend(self) -> None:
        for error in (OSError("unavailable"), subprocess.TimeoutExpired("codex", 5), subprocess.CalledProcessError(1, "codex")):
            with self.subTest(error=error), patch("floor.backends.probe.shutil.which", return_value="/tools/codex"), patch("floor.backends.probe.subprocess.run", side_effect=error):
                value = probe_backend("codex")
            self.assertTrue(value["found"])
            self.assertEqual(value["version"], "version unavailable")

    def test_present_executable_reports_path_version_and_configured_model(self) -> None:
        completed = subprocess.CompletedProcess(["/tools/claude", "--version"], 0, "claude-cli 1.2.3\n", "")
        with patch("floor.backends.probe.shutil.which", return_value="/tools/claude"), patch("floor.backends.probe.subprocess.run", return_value=completed):
            value = probe_backend("claude", ("opus",))
        self.assertEqual(
            value,
            {
                "id": "claude",
                "found": True,
                "executable": "/tools/claude",
                "version": "claude-cli 1.2.3",
                "model": "opus",
            },
        )


if __name__ == "__main__":
    unittest.main()
