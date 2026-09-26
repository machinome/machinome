# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""The package declares the ``machinome-studio`` console script.

This reads ``pyproject.toml`` only: the workspace venv's editable install is
generated from the primary checkout, so checking installed metadata would
fail in a worktree for a reason unrelated to this change (see design D1 and
the proposal's Migration Plan).
"""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConsoleScriptTest(unittest.TestCase):
    def test_machinome_studio_console_script_is_declared(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())
        scripts = project["project"]["scripts"]
        self.assertEqual(scripts, {"machinome-studio": "floor.orchestrator:main"})


if __name__ == "__main__":
    unittest.main()
