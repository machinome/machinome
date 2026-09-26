# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from floor.backends.probe import BACKENDS, probe_backend


class BackendProbeTest(unittest.TestCase):
    def test_only_selectable_backends_are_probed(self) -> None:
        self.assertEqual(BACKENDS, ("claude", "opencode"))

    def test_missing_executable_is_reported_without_invoking_it(self) -> None:
        with patch("floor.backends.probe.shutil.which", return_value=None), patch("floor.backends.probe.subprocess.run") as run:
            value = probe_backend("claude", ("sonnet",))
        self.assertEqual(value["found"], False)
        self.assertIsNone(value["executable"])
        self.assertEqual(value["model"], "sonnet")
        run.assert_not_called()

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
