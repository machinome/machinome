from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from floor.backends.probe import probe_backend


class BackendProbeTest(unittest.TestCase):
    def test_missing_executable_is_reported_without_invoking_it(self) -> None:
        with patch("floor.backends.probe.shutil.which", return_value=None), patch("floor.backends.probe.subprocess.run") as run:
            value = probe_backend("codex", ("gpt-5.6-terra",))
        self.assertEqual(value["found"], False)
        self.assertIsNone(value["executable"])
        self.assertEqual(value["model"], "gpt-5.6-terra")
        run.assert_not_called()

    def test_present_executable_reports_path_version_and_configured_model(self) -> None:
        completed = subprocess.CompletedProcess(["/tools/codex", "--version"], 0, "codex-cli 1.2.3\n", "")
        with patch("floor.backends.probe.shutil.which", return_value="/tools/codex"), patch("floor.backends.probe.subprocess.run", return_value=completed):
            value = probe_backend("codex", ("gpt-5.6-sol",))
        self.assertEqual(
            value,
            {
                "id": "codex",
                "found": True,
                "executable": "/tools/codex",
                "version": "codex-cli 1.2.3",
                "model": "gpt-5.6-sol",
            },
        )


if __name__ == "__main__":
    unittest.main()
