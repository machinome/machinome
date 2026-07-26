"""Portable agent-backend protocol and shared types.

Every agent backend implements ``AgentBackend``.  The orchestrator depends
only on this protocol — never on Codex thread/turn identifiers, Hermes ACP
session handles, or vendor-specific configuration.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


# ── role context & handles ────────────────────────────────────────────────


@dataclass(frozen=True)
class RoleContext:
    """Runtime context injected into a role session at open time."""

    shop_checkout: str
    """Absolute path to the shop checkout (role cards, skills live here)."""

    active_project: str
    """Absolute path to the active mechanical-project repository root."""

    model_callback_url: str | None = None
    """Callback URL the machinist uses to signal model rebuilds."""


@dataclass(frozen=True)
class RoleHandle:
    """Opaque handle the orchestrator uses to address a role session.

    The ``backend_id`` is meaningful only to the backend that created it.
    """

    backend_id: str
    role: str


# ── delivery receipts ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class DeliveryReceipt:
    """Result of delivering a message to a role session."""

    delivery_id: str
    """Opaque identifier used to correlate turn_started / turn_completed."""

    accepted: bool
    """True if the backend accepted the input; False if a completion race lost."""


# ── backend events ─────────────────────────────────────────────────────────


@dataclass
class BackendEvent:
    """A portable event emitted by a backend and consumed by the orchestrator."""

    kind: str  # role_message | turn_started | turn_completed |
    # role_failed | backend_failed

    role: str | None = None
    text: str | None = None
    delivery_id: str | None = None
    error: str | None = None


# ── AgentBackend protocol ──────────────────────────────────────────────────


class AgentBackend(Protocol):
    """Protocol for a pluggable agent-runtime backend.

    Every backend owns one external process (``codex app-server``, ``hermes
    acp``, …) and translates between its native protocol and the portable
    operations and events defined here.

    The orchestrator never sees thread/turn IDs, ACP session handles, or
    provider configuration — only the abstractions below.
    """

    events: AsyncIterator[BackendEvent]
    """Async iterator of portable backend events consumed by the orchestrator."""

    async def start(self) -> None:
        """Launch the backend process (idempotent)."""
        ...

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Create a persistent role session and return its handle."""
        ...

    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        """Route a broker envelope to a role session.

        The orchestrator calls ``deliver_start`` when the role is idle and
        ``deliver_steer`` when the role is active.  The default
        ``deliver()`` implementation dispatches to the appropriate method
        based on whether *expected_delivery_id* is passed.
        """
        ...

    async def deliver_start(
        self, handle: RoleHandle, message: str
    ) -> DeliveryReceipt:
        """Start a new delivery on an idle role session.

        Returns a receipt with an opaque delivery_id for correlation.
        """
        ...

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        """Steer an active delivery (turn redirect).

        Raises ``InactiveTurn`` (imported from the backend module) when
        *expected_delivery_id* no longer matches — i.e. a completion race
        was lost.  The orchestrator catches this and retries with
        ``deliver_start``.
        """
        ...

    async def interrupt(self, handle: RoleHandle) -> None:
        """Interrupt an active role session (best-effort on close/shutdown)."""
        ...

    async def close_role(self, handle: RoleHandle) -> None:
        """Release a role session (best-effort, graceful)."""
        ...

    async def close(self) -> None:
        """Stop the backend process and release owned OS resources."""
        ...
