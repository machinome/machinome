# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Helpers for launching the loaded shop package outside any source checkout."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


WORKTREE_ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def isolated_launch_directory() -> Iterator[Path]:
    """Yield an ordinary non-Git cwd unrelated to shop and project resources."""
    with tempfile.TemporaryDirectory() as temporary:
        yield Path(temporary)


def subprocess_environment(base: dict[str, str] | None = None) -> dict[str, str]:
    """Load this worktree's shop package in a subprocess launched elsewhere."""
    environment = dict(base if base is not None else os.environ)
    existing = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(WORKTREE_ROOT), existing) if item
    )
    return environment
