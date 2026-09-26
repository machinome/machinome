# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".css", ".html", ".js", ".py", ".sh", ".ts", ".tsx"}
COPYRIGHT = "Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes"
SPDX = "SPDX-License-Identifier: AGPL-3.0-or-later"


def tracked_source_files() -> list[Path]:
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
        if path.suffix in SOURCE_SUFFIXES or path.parts[:1] == ("scripts",)
    )


class LicenseHeaderTest(unittest.TestCase):
    def test_every_tracked_source_file_has_agpl_header(self) -> None:
        missing: list[str] = []

        for path in tracked_source_files():
            header = "\n".join((ROOT / path).read_text().splitlines()[:5])
            if COPYRIGHT not in header or SPDX not in header:
                missing.append(str(path))

        self.assertEqual([], missing, f"source files missing AGPL headers: {missing}")


if __name__ == "__main__":
    unittest.main()
