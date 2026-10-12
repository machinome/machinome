# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The package contributes ``machinome studio`` and declares no console script.

The studio is the distribution ``machinome-studio`` of the machinome
repository, numbered with the set (change ``join-studio``, framework
ADR-193): its command is the class ``Studio`` of ``machinome.studio.cli``,
read by ``machinome`` from the entry-point group ``machinome.commands``. This
reads ``pyproject.toml`` only; ``scripts/check-dist`` proves the installed
wheel.
"""

from __future__ import annotations

import ast
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]


def manifest(path: Path) -> dict:
    return tomllib.loads(path.read_text())


class CommandEntryPointTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = manifest(ROOT / "pyproject.toml")["project"]

    def test_the_command_is_contributed_through_machinome_commands(self) -> None:
        self.assertEqual(
            self.project["entry-points"],
            {"machinome.commands": {"studio": "machinome.studio.cli:Studio"}},
        )

    def test_no_console_script_is_declared(self) -> None:
        self.assertNotIn("scripts", self.project)
        self.assertNotIn("gui-scripts", self.project)

    def test_the_package_is_numbered_with_the_set_and_pins_it(self) -> None:
        core = manifest(REPOSITORY / "packages" / "machinome" / "pyproject.toml")["project"]
        version = core["version"]
        self.assertEqual(self.project["version"], version)
        self.assertIn(f"machinome~={version}", self.project["dependencies"])
        self.assertIn(f"machinome-viewer[snapshot]~={version}", self.project["dependencies"])
        self.assertEqual(core["optional-dependencies"]["studio"], [f"machinome-studio~={version}"])

    def test_the_package_ships_its_surface_profiles_and_skills(self) -> None:
        setuptools = manifest(ROOT / "pyproject.toml")["tool"]["setuptools"]
        self.assertEqual(
            setuptools["packages"]["find"],
            {"include": ["machinome.studio", "machinome.studio.backends"], "namespaces": True},
        )
        self.assertIs(setuptools["include-package-data"], False)
        self.assertEqual(
            setuptools["package-data"], {"machinome.studio": ["static/**", "profiles/**", "shop-skills/**"]}
        )
        self.assertFalse((ROOT / "machinome" / "__init__.py").exists())
        self.assertTrue((ROOT / "machinome" / "studio" / "__init__.py").is_file())


class FrameworkBoundaryTest(unittest.TestCase):
    def test_the_studio_imports_no_framework_module(self) -> None:
        # The studio runs the framework's command and reads the viewer's
        # report as processes; `machinome` loads only as its namespace's
        # parent (change `join-studio`).
        package = ROOT / "machinome" / "studio"
        found: list[str] = []
        for module in sorted(package.rglob("*.py")):
            if "frontend" in module.relative_to(package).parts:
                continue
            for node in ast.walk(ast.parse(module.read_text())):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module]
                else:
                    continue
                for name in names:
                    if name.split(".")[0] in ("machinome", "floor") and not (
                        name == "machinome.studio" or name.startswith("machinome.studio.")
                    ):
                        found.append(f"{module.relative_to(ROOT)}:{node.lineno} {name}")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
