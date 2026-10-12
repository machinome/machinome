# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Contract tests for deterministic Build inspection downloads."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from floor.build_package import BuildPackageError, build_package


class BuildPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.artifacts = Path(self.temporary.name)
        (self.artifacts / "models").mkdir()
        (self.artifacts / "models" / "gear.stl").write_bytes(b"solid gear\nendsolid gear\n")
        (self.artifacts / "models" / "pin.stl").write_bytes(b"solid pin\nendsolid pin\n")
        self._publish([
            {
                "id": "bbbbbbbbbbbb", "name": "Planet Gear", "count": 3,
                "models": ["models/gear.stl"], "sources": ["root/gear.py"],
                "size": [24.6, 24.6, 9.0], "volume": 18400, "watertight": True,
            },
            {
                "id": "aaaaaaaaaaaa", "name": "Pin", "count": 1,
                "models": ["models/pin.stl"], "sources": ["root/pin.py"],
                "size": [5, 5, 20], "volume": 300, "watertight": True,
            },
        ])

    def test_package_has_one_stl_per_piece_and_explicit_instructions(self) -> None:
        package = build_package(self.artifacts)
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            self.assertEqual(
                archive.namelist(),
                ["README.md", "pin-aaaaaaaaaaaa.stl", "planet-gear-bbbbbbbbbbbb.stl"],
            )
            self.assertEqual(archive.read("pin-aaaaaaaaaaaa.stl"), b"solid pin\nendsolid pin\n")
            self.assertEqual(archive.read("planet-gear-bbbbbbbbbbbb.stl"), b"solid gear\nendsolid gear\n")
            readme = archive.read("README.md").decode()
            self.assertIn("250 × 210 × 220 mm", readme)
            self.assertIn("| `pin-aaaaaaaaaaaa.stl` | 1 |", readme)
            self.assertIn("| `planet-gear-bbbbbbbbbbbb.stl` | 3 |", readme)
            self.assertNotIn("root/gear.py", readme)
            self.assertNotIn("slicer", readme.lower())
            self.assertNotIn("generated", readme.lower())

    def test_unchanged_publication_produces_identical_zip_bytes(self) -> None:
        self.assertEqual(build_package(self.artifacts), build_package(self.artifacts))

    def test_rejects_invalid_piece_documents_and_model_references(self) -> None:
        invalid = [
            [{"id": "aaaaaaaaaaaa", "name": "Pin", "count": 1, "models": ["../pin.stl"]}],
            [{"id": "aaaaaaaaaaaa", "name": "Pin", "count": 1, "models": ["models/pin.obj"]}],
            [{"id": "aaaaaaaaaaaa", "name": "Pin", "count": 1, "models": ["models/missing.stl"]}],
            [
                {"id": "same", "name": "One", "count": 1, "models": ["models/pin.stl"]},
                {"id": "same", "name": "Two", "count": 1, "models": ["models/gear.stl"]},
            ],
            [{"id": "aaaaaaaaaaaa", "name": "Pin", "count": 0, "models": ["models/pin.stl"]}],
        ]
        for pieces in invalid:
            with self.subTest(pieces=pieces):
                self._publish(pieces)
                with self.assertRaises(BuildPackageError):
                    build_package(self.artifacts)

    def _publish(self, pieces: list[dict[str, object]]) -> None:
        (self.artifacts / "viewer.json").write_text(json.dumps({
            "format": "machinome-export",
            "version": 1,
            "root": {"name": "root", "children": []},
            "pieces": pieces,
        }))


if __name__ == "__main__":
    unittest.main()
