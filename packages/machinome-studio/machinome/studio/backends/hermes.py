"""Hermes agent backend — wraps ``hermes acp`` over stdio.

Structural outline: defines the ``HermesBackend`` class implementing
``AgentBackend`` so the factory can register and import it.  Full ACP
integration is a follow-on change.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import Any

from .base import (
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    RoleContext,
    RoleHandle,
)


class HermesBackend:
    """AgentBackend backed by a ``hermes acp`` subprocess.

    Each role gets one persistent ACP session.  The orchestrator routes
    envelopes via ``deliver()`` (which uses ``session/prompt`` when idle,
    active-turn redirect when busy).  Events translate from ACP
    ``session/update`` notifications.

    Not yet wired to a real ``hermes acp`` process — this is a structural
    outline for the factory and test fixture.
    """

    events: AsyncIterator[BackendEvent]

    def __init__(
        self,
        cwd: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "hermes",
        broker_url: str = "http://127.0.0.1:9000",
        solid_command: str | Sequence[str] = "solid",
        model_callback_url: str | None = None,
    ) -> None:
        self.cwd = cwd.resolve()
        self.project = (project or cwd).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.solid_command = (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        self.model_callback_url = model_callback_url

    async def start(self) -> None:
        raise NotImplementedError("HermesBackend.start — ACP integration not yet implemented")

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        raise NotImplementedError("HermesBackend.open_role — ACP integration not yet implemented")

    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        raise NotImplementedError("HermesBackend.deliver — ACP integration not yet implemented")

    async def interrupt(self, handle: RoleHandle) -> None:
        raise NotImplementedError("HermesBackend.interrupt — ACP integration not yet implemented")

    async def close_role(self, handle: RoleHandle) -> None:
        raise NotImplementedError("HermesBackend.close_role — ACP integration not yet implemented")

    async def close(self) -> None:
        raise NotImplementedError("HermesBackend.close — ACP integration not yet implemented")


# ── registration ───────────────────────────────────────────────────────────

from . import _register  # noqa: E402

_register("hermes", HermesBackend)
