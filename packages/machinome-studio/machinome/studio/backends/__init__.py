"""Pluggable agent backends for the shop orchestrator.

The ``create_backend`` factory selects a concrete ``AgentBackend``
implementation by name.  Each backend owns one external agent-runtime
process and exposes only role-level operations — no backend-native session or
turn identifiers and no provider configuration escape above this seam.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def create_backend(
    name: str,
    *,
    shop_root: Path,
    project: Path | None = None,
    broker_url: str = "http://127.0.0.1:9000",
    command: str | None = None,
    command_overrides: Mapping[str, str] | None = None,
    solid_command: str = "solid",
    session_id: str | None = None,
    **_kwargs: Any,
) -> "AgentBackend":
    """Return the AgentBackend for *name*.

    Raises ``ValueError`` for unknown names.
    """
    if name not in _BACKENDS:
        raise ValueError(f"unknown backend: {name!r} (choose from: {', '.join(sorted(_BACKENDS))})")
    backend_command = (command_overrides or {}).get(name) or command or name
    return _BACKENDS[name](
        shop_root=shop_root,
        project=project,
        broker_url=broker_url,
        command=backend_command,
        solid_command=solid_command,
        session_id=session_id,
    )


def parse_backend_command_overrides(values: Sequence[str] | None) -> dict[str, str]:
    """Parse repeatable BACKEND=COMMAND fixture overrides."""
    parsed: dict[str, str] = {}
    for value in values or ():
        backend, separator, command = value.partition("=")
        if not separator or not backend or not command:
            raise ValueError("backend command override must be BACKEND=COMMAND")
        if backend not in _BACKENDS:
            raise ValueError(f"backend command override names unknown backend {backend!r}")
        if backend in parsed:
            raise ValueError(f"backend command override repeats {backend!r}")
        parsed[backend] = command
    return parsed


# ---------------------------------------------------------------------------
# Lazily-registered factory map — backends register themselves at import time
# ---------------------------------------------------------------------------

_BACKENDS: dict[str, type[AgentBackend]] = {}


def _register(name: str, cls: type[AgentBackend]) -> None:
    if name in _BACKENDS:
        raise RuntimeError(f"backend {name!r} already registered")
    _BACKENDS[name] = cls


# Import order is deliberate: base first, then concrete registration modules.
# map is populated before ``create_backend`` is first called.
from .base import AgentBackend  # noqa: E402
from . import codex as _codex  # noqa: E402
from . import claude as _claude  # noqa: E402
from . import opencode as _opencode  # noqa: E402
