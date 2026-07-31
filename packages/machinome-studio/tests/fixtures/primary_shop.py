"""An isolated ordinary-Git primary shop checkout for subprocess fixtures.

Production ``primary_shop_root`` resolves the shop checkout that owns a
subprocess's working directory through ``git rev-parse --git-common-dir``.
This worktree's own common directory names the pilot's primary checkout,
which does not carry this change's unintegrated ``profiles/`` and
``shop-skills/`` packages -- and must not be modified to add them.

Tests that launch ``python -m floor``/``python -m floor.orchestrator`` as a
real subprocess instead give that subprocess a throwaway ordinary Git
checkout as its own primary root, seeded with copies of this worktree's
``profiles/`` and ``shop-skills/``. Production resolution then finds them
exactly the way it would in a real checkout, unmodified.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


WORKTREE_ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def isolated_primary_shop() -> Iterator[Path]:
    """Yield a throwaway primary shop checkout carrying this worktree's profiles."""
    with tempfile.TemporaryDirectory() as temporary:
        shop = Path(temporary)
        subprocess.run(["git", "init", "-q", str(shop)], check=True)
        shutil.copytree(WORKTREE_ROOT / "profiles", shop / "profiles", symlinks=True)
        shutil.copytree(WORKTREE_ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
        yield shop


def subprocess_environment(base: dict[str, str] | None = None) -> dict[str, str]:
    """Environment for a subprocess run from an isolated primary shop.

    ``python -m floor``/``python -m floor.orchestrator`` are launched with
    the isolated checkout as the process working directory, so this
    worktree's ``floor`` package -- and every test fixture that imports it
    -- must reach the interpreter through ``PYTHONPATH`` instead.
    """
    environment = dict(base if base is not None else os.environ)
    existing = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(WORKTREE_ROOT), existing) if item
    )
    return environment
