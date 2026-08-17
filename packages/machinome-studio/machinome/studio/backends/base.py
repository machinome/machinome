# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Portable agent-backend protocol and shared types.

Every agent backend implements ``AgentBackend``.  The orchestrator depends
only on this protocol — never on backend-native session/turn identifiers or
vendor-specific configuration.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from ..profiles import BackendRuntime, ProfileAgent


# ── delivery races ────────────────────────────────────────────────────────


class InactiveTurn(RuntimeError):
    """The expected delivery completed before steering was accepted.

    Part of the portable contract, not one backend's detail: each backend
    learns of the race from its own native response or outstanding-delivery
    record, and a backend whose runtime provides no such signal never raises it
    (see ADR 0008).
    """


# ── role context & handles ────────────────────────────────────────────────


@dataclass(frozen=True)
class RoleContext:
    """Runtime context injected into a role session at open time."""

    shop_root: str
    """Absolute root of the loaded shop package resources."""

    active_project: str
    """Absolute path to the active mechanical-project repository root."""

    agent: ProfileAgent
    """The validated, profile-owned contract for this session."""

    profile_id: str
    user_label: str
    user_agent_label: str


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


# ── runtime catalogues and activity ────────────────────────────────────────


@dataclass(frozen=True)
class RuntimeChoice:
    """One backend-owned model choice and its supported reasoning values."""

    model: str
    efforts: tuple[str, ...]
    backend: str = ""
    provider: str | None = None


@dataclass(frozen=True)
class RuntimeCatalogue:
    """Whether and how one existing role session can change runtime."""

    supported: bool
    choices: tuple[RuntimeChoice, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class AgentActivity:
    """Portable, browser-safe activity emitted by one role session."""

    id: str
    role: str
    category: Literal["tool", "file", "message", "error"]
    state: Literal["running", "completed", "failed"]
    name: str
    summary: str
    detail: str = ""
    path: str = ""
    diff: str = ""
    timestamp: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None


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
    activity: AgentActivity | None = None


# ── AgentBackend protocol ──────────────────────────────────────────────────


class AgentBackend(Protocol):
    """Protocol for a pluggable agent-runtime backend.

    A backend owns every external process it starts — one for all roles
    (``opencode serve``) or one per role (``claude``) —
    and releases all of them on ``close()``. It translates between its native
    protocol and the portable operations and events defined here. Cardinality
    is a backend's own business; ownership is not (ADR 0008).

    The orchestrator never sees native session/turn IDs or provider
    configuration — only the abstractions below.
    """

    events: AsyncIterator[BackendEvent]
    """Async iterator of portable backend events consumed by the orchestrator."""

    async def start(self) -> None:
        """Launch the backend process (idempotent)."""
        ...

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Create a persistent role session and return its handle."""
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

        Raises ``InactiveTurn`` when *expected_delivery_id* no longer
        matches — i.e. a completion race was lost.  The orchestrator
        catches this and retries with ``deliver_start``.  A backend whose
        runtime cannot report the race never raises it and resolves the
        ambiguity internally instead (ADR 0008).
        """
        ...

    async def deliver_notice(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> bool:
        """Steer an informational notice only if the expected delivery is active.

        Returns ``False`` after a completion race and MUST NOT start a turn.
        """
        ...

    async def interrupt(self, handle: RoleHandle) -> None:
        """Interrupt an active role session (best-effort on close/shutdown)."""
        ...

    async def close_role(self, handle: RoleHandle) -> None:
        """Release a role session (best-effort, graceful)."""
        ...

    async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
        """Describe choices for an existing role, or a fresh role when handle is None."""
        ...

    async def update_runtime(self, handle: RoleHandle, runtime: BackendRuntime) -> None:
        """Apply model and effort to the same persistent role session."""
        ...

    async def close(self) -> None:
        """Stop the backend process and release owned OS resources."""
        ...
