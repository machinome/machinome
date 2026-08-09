"""Read-only discovery of supported agent backend executables."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..profiles import load_profile, resolve_profile_runtime


BACKENDS = ("codex", "claude", "opencode")


def probe_backends(shop_root: Path) -> list[dict[str, object]]:
    models = _configured_models(shop_root)
    return [probe_backend(name, models.get(name, ())) for name in BACKENDS]


def probe_backend(name: str, configured_models: tuple[str, ...] = ()) -> dict[str, object]:
    executable = shutil.which(name)
    if executable is None:
        return {
            "id": name,
            "found": False,
            "executable": None,
            "version": None,
            "model": ", ".join(configured_models) or None,
        }
    try:
        result = subprocess.run(
            (executable, "--version"),
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        version = (result.stdout or result.stderr).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        version = "version unavailable"
    return {
        "id": name,
        "found": True,
        "executable": executable,
        "version": version,
        "model": ", ".join(configured_models) or None,
    }


def _configured_models(shop_root: Path) -> dict[str, tuple[str, ...]]:
    models: dict[str, set[str]] = {name: set() for name in BACKENDS}
    for profile_id in ("builder", "fordesmac"):
        try:
            profile = resolve_profile_runtime(load_profile(profile_id, shop_root=shop_root))
        except ValueError:
            continue
        for agent in profile.agents:
            if agent.runtime is not None:
                models.setdefault(agent.runtime.backend, set()).add(agent.runtime.model)
            for backend, runtime in agent.backends.items():
                models.setdefault(backend, set()).add(runtime.model)
    return {name: tuple(sorted(values)) for name, values in models.items()}
