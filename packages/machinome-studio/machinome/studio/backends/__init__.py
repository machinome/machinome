"""Pluggable agent backends for the shop orchestrator.

The ``create_backend`` factory selects a concrete ``AgentBackend``
implementation by name.  Each backend owns one external agent-runtime
process and exposes only role-level operations — no Codex thread or turn
identifiers, no Hermes ACP session identifiers, and no provider
configuration escape above this seam.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def create_backend(
    name: str,
    *,
    cwd: Path,
    project: Path | None = None,
    broker_url: str = "http://127.0.0.1:9000",
    command: str | None = None,
    solid_command: str = "solid",
    model_callback_url: str | None = None,
    **_kwargs: Any,
) -> "AgentBackend":
    """Return the AgentBackend for *name* ("codex", "hermes", or "claude").

    Raises ``ValueError`` for unknown names.
    """
    if name not in _BACKENDS:
        raise ValueError(f"unknown backend: {name!r} (choose from: {', '.join(sorted(_BACKENDS))})")
    backend_command = command or name  # default: backend name as the command
    return _BACKENDS[name](
        cwd=cwd,
        project=project,
        broker_url=broker_url,
        command=backend_command,
        solid_command=solid_command,
        model_callback_url=model_callback_url,
    )


# ---------------------------------------------------------------------------
# Lazily-registered factory map — backends register themselves at import time
# ---------------------------------------------------------------------------

_BACKENDS: dict[str, type[AgentBackend]] = {}


def _register(name: str, cls: type[AgentBackend]) -> None:
    if name in _BACKENDS:
        raise RuntimeError(f"backend {name!r} already registered")
    _BACKENDS[name] = cls


# Import order is deliberate: base → codex → hermes → claude so the factory
# map is populated before ``create_backend`` is first called.
from .base import AgentBackend  # noqa: E402
from . import codex as _codex  # noqa: E402
from . import hermes as _hermes  # noqa: E402
from . import claude as _claude  # noqa: E402
