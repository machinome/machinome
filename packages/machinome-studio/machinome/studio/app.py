"""HTTP, SSE, and static browser surface for the local shop floor."""

from __future__ import annotations

import asyncio
import json
import os
from collections import deque
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from watchdog.observers import Observer

from .backends.base import AgentActivity
from .profiles import BackendRuntime, RuntimeProfile, load_profile, resolve_profile_runtime
from .preparation import PreparationError, verified_project_root
from .screenshots import is_safe_screenshot, screenshot_path
from .source_files import SourceConflict, SourceUnavailable
from .watcher import ArtifactWatcher, ModelWatcher


# The browser bundle the floor serves. Overridable so a test can run the
# maker's browser against a development build of the same source: React only
# double-invokes effects there, and the shipped bundle cannot exercise that.
STATIC_ROOT = Path(os.environ.get("SHOP_FLOOR_STATIC_ROOT") or Path(__file__).parent / "static")
MESSAGE_KINDS = {"direction", "assignment", "report"}


@dataclass
class Agent:
    role: str
    label: str
    state: str
    assignment_id: str = ""
    pending_assignments: list[str] = field(default_factory=list)
    direct_delivery_id: str = ""
    failure: str = ""
    backend: str = ""
    provider: str = ""
    model: str = ""
    effort: str = ""
    tools: str | list[str] = "inherit"
    backend_idle: bool = True

    def browser_value(self) -> dict[str, object]:
        return {
            "role": self.role,
            "label": self.label,
            "state": self.state,
            "failure": self.failure,
            "backend": self.backend,
            "provider": self.provider or None,
            "model": self.model,
            "effort": self.effort,
            "tools": self.tools,
            "backend_idle": self.backend_idle,
            "runtime_idle": self.runtime_idle,
            "assignment_id": self.assignment_id or None,
            "pending_assignments": list(self.pending_assignments),
        }

    @property
    def runtime_idle(self) -> bool:
        return (
            self.state == "waiting" and not self.failure and self.backend_idle
            and not self.assignment_id and not self.pending_assignments
        )


@dataclass(frozen=True)
class Envelope:
    sequence: int
    kind: str
    sender: str
    recipient: str
    body: str
    assignment_id: str = ""

    def delivery_value(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SystemNotice:
    sequence: int
    kind: str
    recipient: str
    path: str
    revision: str

    def delivery_value(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BrokerEvent:
    sequence: int
    timestamp: str
    kind: str
    summary: str
    role: str = ""
    sender: str = ""
    recipient: str = ""
    assignment_id: str = ""
    envelope_sequence: int | None = None
    payload: dict[str, object] = field(default_factory=dict, repr=False)

    def browser_value(self) -> dict[str, object]:
        value = asdict(self)
        value.pop("payload")
        return {key: item for key, item in value.items() if item not in ("", None)}


@dataclass(frozen=True)
class ConversationEntry:
    sequence: int
    author: str
    text: str

    def browser_value(self) -> dict[str, object]:
        return asdict(self)


class ManifestInput(BaseModel):
    role: str
    label: str


class AssignmentInput(BaseModel):
    assignment_id: str


class ConversationInput(BaseModel):
    text: str


class EnvelopeInput(BaseModel):
    kind: str
    sender: str
    recipient: str
    body: str
    assignment_id: str = ""


class ProjectInput(BaseModel):
    name: str
    profile: str | None = None


class SourceSaveInput(BaseModel):
    content: str
    expected_revision: str


class RuntimeUpdateInput(BaseModel):
    model: str
    effort: str
    persist: bool = True
    expected_revision: str | None = None


class Broker:
    """One in-memory run's portable coordination state."""

    def __init__(self, profile: RuntimeProfile | None = None, *, session_id: str = "unbound", event_history_limit: int = 20) -> None:
        self.profile = profile or resolve_profile_runtime(
            load_profile(None, shop_root=Path(__file__).resolve().parents[1])
        )
        self.session_id = session_id
        self.agents: dict[str, Agent] = {}
        self.subscribers: set[asyncio.Queue[dict[str, object]]] = set()
        self.delivery_subscribers: set[asyncio.Queue[Envelope | None]] = set()
        self.conversation: list[ConversationEntry] = []
        self.envelopes: list[Envelope] = []
        self.delivered: set[int] = set()
        self.failed_deliveries: set[int] = set()
        self.available: set[int] = set()
        self.assignment_envelopes: dict[tuple[str, str], int] = {}
        self.events: deque[BrokerEvent] = deque(maxlen=event_history_limit)
        self.latest_event_sequence = 0
        self._next_envelope_sequence = 0
        self._next_notice_sequence = 0
        self.system_notices: dict[str, list[SystemNotice]] = {}
        self.model_build_error: str | None = None
        self.activity: deque[dict[str, object]] = deque(maxlen=400)
        self._activity_sequence = 0

    def run(self) -> dict[str, object]:
        return {
            "id": self.session_id,
            "status": "running",
            "profile_id": self.profile.id,
            "user_label": self.profile.user_label,
            "user_agent": {"id": self.profile.user_agent.id, "label": self.profile.user_agent.label},
            "roster": [{"id": agent.id, "label": agent.label} for agent in self.profile.agents],
            "agents": [agent.browser_value() for agent in self.agents.values()],
            "events": [event.browser_value() for event in self.events],
            "latest_event_sequence": self.latest_event_sequence,
            "model_build_error": self.model_build_error,
            "activity": list(self.activity),
        }

    def snapshot(self) -> dict[str, object]:
        return {
            "run": self.run(),
            "conversation": [entry.browser_value() for entry in self.conversation],
        }

    def subscribe_snapshot(self) -> tuple[asyncio.Queue[dict[str, object]], dict[str, object]]:
        """Register a live subscriber before serialising its initial state."""
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self.subscribers.add(subscriber)
        return subscriber, self.snapshot()

    def manifest(self, role: str, label: str) -> Agent:
        declared = self._profile_agent(role)
        if label != declared.label:
            raise ValueError("agent label does not match active profile")
        if role not in self._agent_ids:
            raise ValueError("unknown agent role")
        if role in self.agents:
            raise ValueError("agent already manifested")
        runtime = declared.runtime
        agent = Agent(
            role=role,
            label=label,
            state="waiting",
            backend=runtime.backend if runtime is not None else "",
            provider=(runtime.provider or "") if runtime is not None else "",
            model=runtime.model if runtime is not None else "",
            effort=runtime.effort if runtime is not None else "",
            tools=(runtime.tools if isinstance(runtime.tools, str) else list(runtime.tools)) if runtime is not None else "inherit",
        )
        self.agents[role] = agent
        self.publish("agent_manifested", agent)
        return agent

    def runtime_changed(self, role: str, runtime: BackendRuntime) -> Agent:
        agent = self._agent(role)
        agent.backend = runtime.backend
        agent.provider = runtime.provider or ""
        agent.model = runtime.model
        agent.effort = runtime.effort
        agent.tools = runtime.tools if isinstance(runtime.tools, str) else list(runtime.tools)
        self.publish("agent_runtime_changed", agent, role=role)
        return agent

    def backend_idle_changed(self, role: str, idle: bool) -> Agent:
        agent = self._agent(role)
        if agent.backend_idle == idle:
            return agent
        agent.backend_idle = idle
        self.publish("agent_backend_idle_changed", agent, role=role)
        return agent

    def runtime_idle(self, role: str) -> bool:
        return self._agent(role).runtime_idle

    def record_activity(self, activity: AgentActivity) -> dict[str, object]:
        self._agent(activity.role)
        key = (activity.role, activity.id)
        previous = next(
            (item for item in self.activity if (item.get("role"), item.get("id")) == key),
            None,
        )
        self._activity_sequence += 1
        value = asdict(activity)
        value["sequence"] = self._activity_sequence
        value["timestamp"] = activity.timestamp or datetime.now(UTC).isoformat().replace("+00:00", "Z")
        value = {name: item for name, item in value.items() if item not in ("", None)}
        if previous is not None:
            items = list(self.activity)
            items[items.index(previous)] = value
            self.activity = deque(items, maxlen=self.activity.maxlen)
        else:
            self.activity.append(value)
        self.publish("agent_activity", value, role=activity.role)
        return value

    def stop(self, role: str) -> Agent:
        agent = self.agents.pop(role, None)
        if agent is None:
            raise ValueError("unknown agent")
        self.publish("agent_stopped", agent)
        return agent

    def send(
        self,
        kind: str,
        sender: str,
        recipient: str,
        body: str,
        assignment_id: str = "",
    ) -> Envelope:
        if kind not in MESSAGE_KINDS:
            raise ValueError("unknown envelope kind")
        if self.profile.work_mode == "direct" and assignment_id:
            raise ValueError("assignment ID is unavailable in direct mode")
        if sender != "user" and sender not in self._agent_ids:
            raise ValueError("unknown agent sender")
        if recipient not in self._agent_ids:
            raise ValueError("unknown agent recipient")
        body = body.strip()
        if not body:
            raise ValueError("body is required")
        if kind == "assignment":
            if self.profile.work_mode != "delegated":
                raise ValueError("assignment lifecycle is unavailable in direct mode")
            if recipient not in self._profile_agent(sender).assigns:
                raise ValueError("assignment edge is not declared by the active profile")
            return self.assign(recipient, assignment_id, body=body, sender=sender)
        if kind == "report":
            if self.profile.work_mode != "delegated":
                raise ValueError("assignment lifecycle is unavailable in direct mode")
            if self._profile_agent(sender).reports_to != recipient:
                raise ValueError("reporting parent is not declared by the active profile")
        if kind == "direction" and sender == "user" and recipient != self.profile.user_agent_id:
            raise ValueError("user direction must target the profile user-facing agent")
        envelope = self._new_envelope(kind, sender, recipient, body, assignment_id)
        self._make_available(envelope)
        return envelope

    def assign(self, role: str, assignment_id: str, *, body: str | None = None, sender: str | None = None) -> Envelope:
        if self.profile.work_mode != "delegated":
            raise ValueError("assignment lifecycle is unavailable in direct mode")
        agent = self._agent(role)
        sender = sender or (self._profile_agent(role).reports_to or "")
        if role not in self._profile_agent(sender).assigns:
            raise ValueError("assignment edge is not declared by the active profile")
        if not assignment_id:
            raise ValueError("assignment_id is required")
        if (role, assignment_id) in self.assignment_envelopes:
            raise ValueError("assignment already exists")
        envelope = self._new_envelope(
            "assignment",
            sender,
            role,
            body or f"Assignment {assignment_id}",
            assignment_id,
        )
        self.assignment_envelopes[(role, assignment_id)] = envelope.sequence
        if not agent.assignment_id:
            agent.assignment_id = assignment_id
            self._make_available(envelope)
        else:
            agent.pending_assignments.append(assignment_id)
            self.publish(
                "assignment_queued",
                {"role": role, "assignment_id": assignment_id},
                role=role,
                assignment_id=assignment_id,
                envelope_sequence=envelope.sequence,
            )
        return envelope

    def acknowledge(self, role: str, assignment_id: str) -> Agent:
        if self.profile.work_mode != "delegated":
            raise ValueError("assignment lifecycle is unavailable in direct mode")
        agent = self._agent(role)
        if agent.state != "waiting" or agent.assignment_id != assignment_id:
            raise ValueError("invalid lifecycle report")
        agent.state = "active"
        self.publish("work_acknowledged", agent, role=role, assignment_id=assignment_id)
        return agent

    def complete(self, role: str, assignment_id: str) -> Agent:
        if self.profile.work_mode != "delegated":
            raise ValueError("assignment lifecycle is unavailable in direct mode")
        agent = self._agent(role)
        if agent.state != "active" or agent.assignment_id != assignment_id:
            raise ValueError("invalid lifecycle report")
        agent.state = "waiting"
        agent.assignment_id = ""
        self.publish("work_completed", agent, role=role, assignment_id=assignment_id)
        if agent.pending_assignments:
            next_assignment = agent.pending_assignments.pop(0)
            agent.assignment_id = next_assignment
            sequence = self.assignment_envelopes[(role, next_assignment)]
            envelope = self._envelope(sequence)
            self._make_available(envelope)
        return agent

    def pending_for(self, role: str) -> list[Envelope]:
        if role not in self._agent_ids:
            raise ValueError("unknown agent")
        return [
            envelope
            for envelope in self.envelopes
            if envelope.recipient == role
            and envelope.sequence in self.available
            and envelope.sequence not in self.delivered
            and envelope.sequence not in self.failed_deliveries
        ]

    def queue_user_file_changed(self, path: str, revision: str) -> list[SystemNotice]:
        queued: list[SystemNotice] = []
        for role, agent in self.agents.items():
            if agent.state != "active":
                continue
            pending = self.system_notices.setdefault(role, [])
            notice = next(
                (
                    item
                    for item in pending
                    if item.kind == "user_file_changed" and item.path == path
                ),
                None,
            )
            if notice is None:
                self._next_notice_sequence += 1
                notice = SystemNotice(
                    self._next_notice_sequence,
                    "user_file_changed",
                    role,
                    path,
                    revision,
                )
                pending.append(notice)
            else:
                self._next_notice_sequence += 1
                notice = SystemNotice(
                    self._next_notice_sequence,
                    "user_file_changed",
                    role,
                    path,
                    revision,
                )
                pending[:] = [
                    notice if item.kind == "user_file_changed" and item.path == path else item
                    for item in pending
                ]
            queued.append(notice)
            self.publish(
                "system_notice_queued",
                {"role": role, "notice_kind": notice.kind},
                role=role,
            )
        return queued

    def pending_system_notices(self, role: str) -> list[SystemNotice]:
        if role not in self._agent_ids:
            raise ValueError("unknown agent")
        return list(self.system_notices.get(role, ()))

    def mark_system_notices_delivered(self, role: str, sequences: list[int]) -> None:
        if role not in self._agent_ids:
            raise ValueError("unknown agent")
        delivered = set(sequences)
        pending = self.system_notices.get(role, [])
        removed = [notice for notice in pending if notice.sequence in delivered]
        self.system_notices[role] = [
            notice for notice in pending if notice.sequence not in delivered
        ]
        for _notice in removed:
            self.publish("system_notice_delivered", {"role": role}, role=role)

    def mark_delivered(self, sequence: int) -> Envelope:
        envelope = self._envelope(sequence)
        if sequence not in self.available:
            raise ValueError("envelope is not available")
        if sequence in self.delivered:
            raise ValueError("envelope already delivered")
        if sequence in self.failed_deliveries:
            raise ValueError("envelope delivery already failed")
        self.delivered.add(sequence)
        self.publish(
            "envelope_delivered",
            {
                "role": envelope.recipient,
                "sender": envelope.sender,
                "recipient": envelope.recipient,
                "assignment_id": envelope.assignment_id,
            },
            role=envelope.recipient,
            sender=envelope.sender,
            recipient=envelope.recipient,
            assignment_id=envelope.assignment_id,
            envelope_sequence=envelope.sequence,
        )
        return envelope

    def mark_delivery_failed(self, sequence: int, error: str) -> Envelope:
        envelope = self._envelope(sequence)
        if sequence not in self.available:
            raise ValueError("envelope is not available")
        if sequence in self.delivered or sequence in self.failed_deliveries:
            raise ValueError("envelope delivery already finished")
        self.failed_deliveries.add(sequence)
        self.publish(
            "envelope_delivery_failed",
            {
                "role": envelope.recipient,
                "sender": envelope.sender,
                "recipient": envelope.recipient,
                "assignment_id": envelope.assignment_id,
                "error": error,
            },
            role=envelope.recipient,
            sender=envelope.sender,
            recipient=envelope.recipient,
            assignment_id=envelope.assignment_id,
            envelope_sequence=envelope.sequence,
        )
        return envelope

    async def record_conversation(self, author: str, text: str) -> ConversationEntry:
        if author not in {"user", self.profile.user_agent_id}:
            raise ValueError("only user and the profile user-facing agent can enter the conversation")
        text = text.strip()
        if not text:
            raise ValueError("text is required")
        entry = ConversationEntry(sequence=len(self.conversation) + 1, author=author, text=text)
        self.conversation.append(entry)
        self.publish("conversation_entry", entry)
        if author == "user":
            self.send("direction", "user", self.profile.user_agent_id, text)
        return entry

    async def deliveries(self) -> AsyncIterator[Envelope]:
        queue: asyncio.Queue[Envelope | None] = asyncio.Queue()
        self.delivery_subscribers.add(queue)
        try:
            for role in self._agent_ids:
                for envelope in self.pending_for(role):
                    await queue.put(envelope)
            while True:
                envelope = await queue.get()
                if envelope is None:
                    return
                if envelope.sequence not in self.delivered and envelope.sequence not in self.failed_deliveries:
                    yield envelope
        finally:
            self.delivery_subscribers.discard(queue)

    def shutdown(self) -> None:
        for subscriber in tuple(self.delivery_subscribers):
            subscriber.put_nowait(None)

    def publish(
        self,
        kind: str,
        payload: Agent | ConversationEntry | dict[str, object],
        *,
        role: str = "",
        sender: str = "",
        recipient: str = "",
        assignment_id: str = "",
        envelope_sequence: int | None = None,
    ) -> BrokerEvent:
        value = payload if isinstance(payload, dict) else payload.browser_value()
        if kind == "model_build_unavailable":
            self.model_build_error = str(value.get("reason") or "the shop could not start a model build")
        elif kind == "model_artifact_changed" and value.get("artifact") == "viewer.json":
            self.model_build_error = None
        role = role or str(value.get("role", ""))
        sender = sender or str(value.get("sender", ""))
        recipient = recipient or str(value.get("recipient", ""))
        assignment_id = assignment_id or str(value.get("assignment_id", ""))
        self.latest_event_sequence += 1
        event = BrokerEvent(
            sequence=self.latest_event_sequence,
            timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            kind=kind,
            summary=self._event_summary(kind, role, sender, recipient, assignment_id),
            role=role,
            sender=sender,
            recipient=recipient,
            assignment_id=assignment_id,
            envelope_sequence=envelope_sequence,
            payload=value,
        )
        self.events.append(event)
        live_event: dict[str, object] = {"kind": kind, "payload": value, "event": event.browser_value()}
        for subscriber in tuple(self.subscribers):
            subscriber.put_nowait(live_event)
        return event

    def _new_envelope(
        self,
        kind: str,
        sender: str,
        recipient: str,
        body: str,
        assignment_id: str,
    ) -> Envelope:
        self._next_envelope_sequence += 1
        envelope = Envelope(
            sequence=self._next_envelope_sequence,
            kind=kind,
            sender=sender,
            recipient=recipient,
            body=body,
            assignment_id=assignment_id,
        )
        self.envelopes.append(envelope)
        return envelope

    def _make_available(self, envelope: Envelope) -> None:
        self.available.add(envelope.sequence)
        self.publish(
            f"{envelope.kind}_available",
            {
                "role": envelope.recipient,
                "sender": envelope.sender,
                "recipient": envelope.recipient,
                "assignment_id": envelope.assignment_id,
            },
            role=envelope.recipient,
            sender=envelope.sender,
            recipient=envelope.recipient,
            assignment_id=envelope.assignment_id,
            envelope_sequence=envelope.sequence,
        )
        for subscriber in tuple(self.delivery_subscribers):
            subscriber.put_nowait(envelope)

    def _agent(self, role: str) -> Agent:
        agent = self.agents.get(role)
        if agent is None:
            raise ValueError("unknown agent")
        return agent

    @property
    def _agent_ids(self) -> tuple[str, ...]:
        return tuple(agent.id for agent in self.profile.agents)

    def _profile_agent(self, role: str):
        try:
            return self.profile.agent(role)
        except ValueError as error:
            raise ValueError("unknown agent") from error

    def turn_started(self, role: str, delivery_id: str) -> Agent:
        if self.profile.work_mode != "direct" or role != self.profile.user_agent_id:
            return self._agent(role)
        agent = self._agent(role)
        if agent.direct_delivery_id != delivery_id:
            return agent
        agent.state = "active"
        self.publish("direct_work_started", agent, role=role)
        return agent

    def turn_completed(self, role: str, delivery_id: str) -> Agent:
        if self.profile.work_mode != "direct" or role != self.profile.user_agent_id:
            return self._agent(role)
        agent = self._agent(role)
        if agent.direct_delivery_id != delivery_id:
            return agent
        agent.state = "waiting"
        agent.direct_delivery_id = ""
        self.publish("direct_work_completed", agent, role=role)
        return agent

    def register_direct_delivery(self, role: str, delivery_id: str) -> None:
        """Record the one backend delivery that may change direct work state."""
        if self.profile.work_mode != "direct" or role != self.profile.user_agent_id:
            return
        self._agent(role).direct_delivery_id = delivery_id

    def role_failed(self, role: str, error: str) -> Agent:
        agent = self._agent(role)
        agent.failure = error.strip() or "unknown error"
        if self.profile.work_mode == "direct" and role == self.profile.user_agent_id:
            agent.state = "waiting"
            agent.direct_delivery_id = ""
        self.publish("agent_failed", agent, role=role)
        return agent

    def role_recovered(self, role: str) -> Agent:
        agent = self._agent(role)
        agent.failure = ""
        self.publish("agent_recovered", agent, role=role)
        return agent

    def _event_summary(self, kind: str, role: str, sender: str, recipient: str, assignment_id: str) -> str:
        labels = {"user": self.profile.user_label, **{agent.id: agent.label for agent in self.profile.agents}}
        if kind == "agent_manifested":
            return f"{labels.get(role, role.title())} manifested"
        if kind == "agent_stopped":
            return f"{labels.get(role, role.title())} stopped"
        if kind == "agent_failed":
            return f"{labels.get(role, role.title())} failed"
        if kind == "agent_recovered":
            return f"{labels.get(role, role.title())} recovered"
        if kind == "agent_runtime_changed":
            return f"Runtime changed · {labels.get(role, role.title())}"
        if kind == "agent_activity":
            return f"Activity · {labels.get(role, role.title())}"
        if kind.endswith("_available"):
            name = kind.removesuffix("_available").replace("_", " ").title()
            return f"{name} · {labels.get(sender, sender.title())} → {labels.get(recipient, recipient.title())}"
        if kind == "assignment_queued":
            return f"Assignment queued · {labels.get(role, role.title())} · {assignment_id}"
        if kind in {"work_acknowledged", "direct_work_started"}:
            return f"Work started · {labels.get(role, role.title())}" + (f" · {assignment_id}" if assignment_id else "")
        if kind in {"work_completed", "direct_work_completed"}:
            return f"Work completed · {labels.get(role, role.title())}" + (f" · {assignment_id}" if assignment_id else "")
        if kind == "envelope_delivered":
            return f"Delivered · {labels.get(recipient, recipient.title())}"
        if kind == "envelope_delivery_failed":
            return f"Delivery failed · {labels.get(recipient, recipient.title())}"
        if kind == "conversation_entry":
            return "Conversation updated"
        if kind == "model_artifact_changed":
            return "Model artifact updated"
        if kind == "model_build_unavailable":
            return "Model build unavailable"
        return kind.replace("_", " ").title()

    def _envelope(self, sequence: int) -> Envelope:
        try:
            return next(item for item in self.envelopes if item.sequence == sequence)
        except StopIteration as error:
            raise ValueError("unknown envelope") from error


def create_app(working_folder: Path, *, registry: object) -> FastAPI:
    """Serve the project hub and all registry-owned session surfaces."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await registry.close_all()  # type: ignore[attr-defined]

    app = FastAPI(title="solid-node-studio", lifespan=lifespan)
    app.state.working_folder = working_folder.resolve()
    app.state.registry = registry
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")

    def session(session_id: str):
        try:
            return registry.require_id(session_id)  # type: ignore[attr-defined]
        except KeyError as error:
            raise HTTPException(status_code=404, detail="unknown session") from error

    def project_session(name: str):
        value = registry.by_project(name)  # type: ignore[attr-defined]
        if value is None:
            raise HTTPException(status_code=404, detail="project is not open")
        return value

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "open"}

    @app.get("/api/projects")
    async def projects() -> dict[str, object]:
        return {"working_folder": str(working_folder.resolve()), "projects": await registry.projects()}  # type: ignore[attr-defined]

    @app.post("/api/projects")
    async def create_project(input: ProjectInput) -> JSONResponse:
        try:
            value = await registry.create(input.name, input.profile)  # type: ignore[attr-defined]
        except (ValueError, RuntimeError) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return JSONResponse(value, status_code=202)

    @app.post("/api/projects/{name}/session")
    async def open_project(name: str) -> JSONResponse:
        try:
            value = await registry.request_open(name)  # type: ignore[attr-defined]
        except (ValueError, RuntimeError) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return JSONResponse(value, status_code=200 if value.get("state") == "open" else 202)

    @app.delete("/api/sessions/{session_id}")
    async def close_project(session_id: str) -> Response:
        session(session_id)
        asyncio.create_task(registry.request_close(session_id))  # type: ignore[attr-defined]
        return Response(status_code=202)

    @app.get("/api/backends")
    async def backends() -> dict[str, object]:
        from .backends.probe import probe_backends
        return {"backends": await asyncio.to_thread(probe_backends, registry.shop_root)}  # type: ignore[attr-defined]

    @app.post("/api/backends/detect")
    async def detect_backends() -> dict[str, object]:
        return await backends()

    @app.get("/projects/{name}/viewer/solid-widget.js")
    async def viewer(name: str) -> FileResponse:
        bundle = project_session(name).prepared.viewer_bundle
        if bundle is None or not bundle.is_file():
            raise HTTPException(status_code=404, detail="no framework viewer is available")
        return FileResponse(bundle, media_type="text/javascript")

    @app.get("/projects/{name}/screenshot.png")
    async def project_screenshot(name: str) -> FileResponse:
        try:
            root = await asyncio.to_thread(verified_project_root, name, working_folder)
        except (PreparationError, ValueError) as error:
            raise HTTPException(status_code=404, detail="unknown project screenshot") from error
        if not is_safe_screenshot(root):
            raise HTTPException(status_code=404, detail="unknown project screenshot")
        return FileResponse(screenshot_path(root), media_type="image/png", headers={"Cache-Control": "no-cache"})

    @app.get("/projects/{name}/artifacts/{artifact_path:path}")
    async def artifact(name: str, artifact_path: str) -> FileResponse:
        build_root = project_session(name).artifact_root.resolve()
        candidate = (build_root / artifact_path).resolve()
        if build_root not in candidate.parents and candidate != build_root:
            raise HTTPException(status_code=404, detail="unknown artifact")
        if not candidate.is_file():
            raise HTTPException(status_code=404, detail="unknown artifact")
        return FileResponse(candidate, headers={"Cache-Control": "no-cache"})

    @app.get("/api/sessions/{session_id}")
    async def run(session_id: str) -> dict[str, object]:
        return session(session_id).broker.run()

    @app.get("/api/sessions/{session_id}/agents/{role}/runtime")
    async def agent_runtime_catalog(session_id: str, role: str) -> JSONResponse:
        try:
            return JSONResponse(await session(session_id).runtime_catalog(role))
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.patch("/api/sessions/{session_id}/agents/{role}/runtime")
    async def update_agent_runtime(
        session_id: str,
        role: str,
        input: RuntimeUpdateInput,
    ) -> JSONResponse:
        from .runtime_config import RuntimeConfigConflict

        try:
            return JSONResponse(await session(session_id).update_runtime(
                role,
                input.model,
                input.effort,
                persist=input.persist,
                expected_revision=input.expected_revision,
            ))
        except RuntimeConfigConflict as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.get("/api/sessions/{session_id}/conversation")
    async def conversation(session_id: str) -> dict[str, object]:
        broker = session(session_id).broker
        return {"entries": [entry.browser_value() for entry in broker.conversation]}

    @app.get("/api/sessions/{session_id}/source")
    async def source_entries(session_id: str) -> dict[str, object]:
        workspace = session(session_id).source_workspace
        try:
            entries = await asyncio.to_thread(workspace.entries)
        except SourceUnavailable as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        return {"entries": [entry.browser_value() for entry in entries]}

    @app.get("/api/sessions/{session_id}/source/{source_path:path}")
    async def source_file(session_id: str, source_path: str) -> dict[str, str]:
        workspace = session(session_id).source_workspace
        try:
            document = await asyncio.to_thread(workspace.read, source_path)
        except SourceUnavailable as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return document.browser_value()

    @app.get("/api/sessions/{session_id}/source-preview/{source_path:path}")
    async def source_preview(session_id: str, source_path: str) -> Response:
        workspace = session(session_id).source_workspace
        try:
            content = await asyncio.to_thread(workspace.read_png, source_path)
        except SourceUnavailable as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return Response(
            content=content,
            media_type="image/png",
            headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"},
        )

    @app.put("/api/sessions/{session_id}/source/{source_path:path}")
    async def save_source_file(
        session_id: str,
        source_path: str,
        input: SourceSaveInput,
    ) -> JSONResponse:
        project = session(session_id)
        try:
            document = await project.save_source(
                source_path,
                input.content,
                input.expected_revision,
            )
        except SourceConflict as error:
            return JSONResponse(
                {
                    "detail": str(error),
                    "current": error.document.browser_value(),
                },
                status_code=409,
            )
        except SourceUnavailable as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return JSONResponse(document.browser_value())

    @app.post("/api/sessions/{session_id}/conversation")
    async def submit_user_message(session_id: str, input: ConversationInput) -> JSONResponse:
        return JSONResponse((await _conversation_or_400(session(session_id).broker, "user", input.text)).browser_value())

    @app.post("/api/sessions/{session_id}/agents")
    async def manifest(session_id: str, input: ManifestInput) -> JSONResponse:
        try:
            return JSONResponse(session(session_id).broker.manifest(input.role, input.label).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/sessions/{session_id}/envelopes")
    async def send_envelope(session_id: str, input: EnvelopeInput) -> JSONResponse:
        broker = session(session_id).broker
        try:
            envelope = broker.send(input.kind, input.sender, input.recipient, input.body, input.assignment_id)
        except ValueError as error:
            raise _broker_http_error(error) from error
        return JSONResponse(envelope.delivery_value())

    @app.post("/api/sessions/{session_id}/envelopes/{sequence}/delivered")
    async def mark_delivered(session_id: str, sequence: int) -> JSONResponse:
        try:
            return JSONResponse(session(session_id).broker.mark_delivered(sequence).delivery_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/sessions/{session_id}/agents/{role}/assignments")
    async def assign(session_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        broker = session(session_id).broker
        try:
            broker.assign(role, input.assignment_id)
            return JSONResponse(broker.agents[role].browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/sessions/{session_id}/agents/{role}/acknowledgments")
    async def acknowledge(session_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        try:
            return JSONResponse(session(session_id).broker.acknowledge(role, input.assignment_id).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/sessions/{session_id}/agents/{role}/completions")
    async def complete(session_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        try:
            return JSONResponse(session(session_id).broker.complete(role, input.assignment_id).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.delete("/api/sessions/{session_id}/agents/{role}")
    async def stop(session_id: str, role: str) -> Response:
        try:
            session(session_id).broker.stop(role)
        except ValueError as error:
            raise _broker_http_error(error) from error
        return Response(status_code=204)

    @app.get("/api/sessions/{session_id}/orchestrator/stream")
    async def orchestrator_stream(session_id: str) -> StreamingResponse:
        broker = session(session_id).broker

        async def events() -> AsyncIterator[str]:
            async for envelope in broker.deliveries():
                yield f"event: envelope\ndata: {json.dumps(envelope.delivery_value())}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    def live_state_stream(request: Request, broker: Broker) -> StreamingResponse:
        async def events() -> AsyncIterator[str]:
            subscriber, snapshot = broker.subscribe_snapshot()
            try:
                yield f"event: snapshot\ndata: {json.dumps(snapshot)}\n\n"
                while not await request.is_disconnected():
                    try:
                        event = await asyncio.wait_for(subscriber.get(), timeout=15)
                        yield f"event: shop-floor\ndata: {json.dumps(event)}\n\n"
                    except TimeoutError:
                        yield ": keepalive\n\n"
            finally:
                broker.subscribers.discard(subscriber)

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/api/sessions/{session_id}/stream")
    async def session_stream(session_id: str, request: Request) -> StreamingResponse:
        return live_state_stream(request, session(session_id).broker)

    @app.get("/api/stream")
    async def hub_stream(request: Request) -> StreamingResponse:
        async def events() -> AsyncIterator[str]:
            subscriber, snapshot = await registry.subscribe_hub()  # type: ignore[attr-defined]
            try:
                yield f"event: snapshot\ndata: {json.dumps(snapshot)}\n\n"
                while not await request.is_disconnected():
                    try:
                        event = await asyncio.wait_for(subscriber.get(), timeout=15)
                        yield f"event: project\ndata: {json.dumps(event)}\n\n"
                    except TimeoutError:
                        yield ": keepalive\n\n"
            finally:
                registry.unsubscribe_hub(subscriber)  # type: ignore[attr-defined]

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/{browser_path:path}")
    async def browser_page(browser_path: str) -> FileResponse:
        if browser_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="unknown API route")
        return FileResponse(STATIC_ROOT / "index.html", media_type="text/html")

    return app


async def _conversation_or_400(broker: Broker, author: str, text: str) -> ConversationEntry:
    try:
        return await broker.record_conversation(author, text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _broker_http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "unknown" in detail:
        return HTTPException(status_code=404, detail=detail)
    if "required" in detail:
        return HTTPException(status_code=400, detail=detail)
    return HTTPException(status_code=409, detail=detail)
