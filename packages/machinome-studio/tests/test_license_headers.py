# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Every source file of the studio states the set's licence.

The studio is a package of the machinome repository, under the licence of
every package there, stated once at the repository's root (change
``join-studio``): each tracked source file carries the copyright line and the
SPDX line of that expression, read from the framework's manifest, and no
SPDX line of the package's current files names another. The records of their
day (archived changes, the design reference, the spikes, the archive) keep
what they said.
"""

from __future__ import annotations

import subprocess
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
SOURCE_SUFFIXES = {".css", ".html", ".js", ".py", ".sh", ".ts", ".tsx"}
# The Machinome identity release and the interface fonts are copied intact
# from their own sources and carry their own notices; they are served as
# static assets and are not this repository's source.
VENDORED = ("machinome", "studio", "frontend", "public", "assets")
# Records of their day, kept as they were written.
RECORDS = (
    ("openspec", "changes", "archive"),
    ("workflow", "design"),
    ("workflow", "spikes"),
    ("workflow", "archive"),
)
COPYRIGHT = "Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes"
LICENCE = tomllib.loads((REPOSITORY / "packages" / "machinome" / "pyproject.toml").read_text())["project"]["license"]
MARKER = "SPDX-License-" "Identifier:"


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = (Path(value.decode()) for value in result.stdout.split(b"\0") if value)
    return sorted(
        path
        for path in paths
        if not any(path.parts[: len(record)] == record for record in RECORDS)
    )


def tracked_source_files() -> list[Path]:
    return [
        path
        for path in tracked_files()
        if (path.suffix in SOURCE_SUFFIXES or path.parts[:1] == ("scripts",))
        and path.parts[: len(VENDORED)] != VENDORED
    ]


class LicenseHeaderTest(unittest.TestCase):
    def test_every_tracked_source_file_states_the_set_s_licence(self) -> None:
        missing: list[str] = []

        for path in tracked_source_files():
            header = "\n".join((ROOT / path).read_text().splitlines()[:5])
            if COPYRIGHT not in header or f"{MARKER} {LICENCE}" not in header:
                missing.append(str(path))

        self.assertEqual([], missing, f"source files missing the set's licence header: {missing}")

    def test_no_current_file_names_another_licence(self) -> None:
        other: list[str] = []

        for path in tracked_files():
            if (ROOT / path).is_symlink() or not (ROOT / path).is_file():
                continue
            try:
                text = (ROOT / path).read_text()
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if MARKER in line and f"{MARKER} {LICENCE}" not in line:
                    other.append(f"{path}:{number}")

        self.assertEqual([], other, f"SPDX lines naming another licence: {other}")


if __name__ == "__main__":
    unittest.main()
