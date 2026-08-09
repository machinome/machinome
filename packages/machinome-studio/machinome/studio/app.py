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

from .profiles import RuntimeProfile, load_profile
from .watcher import ArtifactWatcher, ModelWatcher


RUN_ID = "shop-floor"
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

    def browser_value(self) -> dict[str, str]:
        return {
            "role": self.role,
            "label": self.label,
            "state": self.state,
            "failure": self.failure,
        }


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


class Broker:
    """One in-memory run's portable coordination state."""

    def __init__(self, profile: RuntimeProfile | None = None, *, event_history_limit: int = 20) -> None:
        self.profile = profile or load_profile(None, shop_root=Path(__file__).resolve().parents[1], backend="codex")
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

    def run(self) -> dict[str, object]:
        return {
            "id": RUN_ID,
            "status": "running",
            "profile_id": self.profile.id,
            "user_label": self.profile.user_label,
            "user_agent": {"id": self.profile.user_agent.id, "label": self.profile.user_agent.label},
            "roster": [{"id": agent.id, "label": agent.label} for agent in self.profile.agents],
            "agents": [agent.browser_value() for agent in self.agents.values()],
            "events": [event.browser_value() for event in self.events],
            "latest_event_sequence": self.latest_event_sequence,
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
        agent = Agent(role=role, label=label, state="waiting")
        self.agents[role] = agent
        self.publish("agent_manifested", agent)
        return agent

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


def create_app(
    project_root: Path | None = None,
    *,
    artifact_root: Path | None = None,
    viewer_bundle: Path | None = None,
    broker: Broker | None = None,
    profile: RuntimeProfile | None = None,
    solid_command: Sequence[str] | None = None,
    build_environment: Mapping[str, str] | None = None,
    settle_delay: float = 0.5,
) -> FastAPI:
    # The watcher belongs to the application, not the orchestrator: the
    # thing it refreshes is this app's own artifact route, and this app is what
    # publishes filesystem events. Both entry points get identical wiring.
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        observer: Observer | None = None
        source_watcher: ModelWatcher | None = None
        artifact_watcher: ArtifactWatcher | None = None
        if build_root is not None and build_root.is_dir():
            loop = asyncio.get_running_loop()
            observer = Observer()
            artifact_watcher = ArtifactWatcher(build_root, loop, app.state.broker.publish)
            observer.schedule(artifact_watcher, str(build_root), recursive=True)
            if solid_command is not None and project_root is not None:
                source_watcher = ModelWatcher(
                project_root,
                solid_command,
                app.state.broker.publish,
                loop=loop,
                extra_environment=build_environment,
                settle_delay=settle_delay,
                )
                observer.schedule(source_watcher, str(project_root), recursive=True)
            app.state.model_watcher = source_watcher
            app.state.artifact_watcher = artifact_watcher
            app.state.observer = observer
            observer.start()
        try:
            yield
        finally:
            if source_watcher is not None:
                source_watcher.close()
            if observer is not None:
                observer.stop()
                await asyncio.to_thread(observer.join)

    app = FastAPI(title="shop-floor", lifespan=lifespan)
    broker = broker or Broker(profile=profile)
    app.state.broker = broker
    app.state.model_watcher = None
    app.state.artifact_watcher = None
    app.state.observer = None
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")
    supplied_build_root = artifact_root or (project_root / "_build" if project_root is not None else None)
    build_root = supplied_build_root.resolve() if supplied_build_root is not None else None

    @app.get("/viewer/solid-widget.js")
    async def viewer() -> FileResponse:
        if viewer_bundle is None or not viewer_bundle.is_file():
            raise HTTPException(status_code=404, detail="no framework viewer is available")
        return FileResponse(viewer_bundle, media_type="text/javascript")

    @app.get("/artifacts/{artifact_path:path}")
    async def artifact(artifact_path: str) -> FileResponse:
        if build_root is None:
            raise HTTPException(status_code=404, detail="no project build is available")
        candidate = (build_root / artifact_path).resolve()
        if build_root not in candidate.parents and candidate != build_root:
            raise HTTPException(status_code=404, detail="unknown artifact")
        if not candidate.is_file():
            raise HTTPException(status_code=404, detail="unknown artifact")
        return FileResponse(candidate, headers={"Cache-Control": "no-cache"})

    @app.get("/")
    async def browser_page() -> FileResponse:
        return FileResponse(STATIC_ROOT / "index.html", media_type="text/html")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "open"}

    @app.get("/api/runs/latest")
    async def latest_run() -> dict[str, object]:
        return broker.run()

    @app.get("/api/runs/{run_id}")
    async def run(run_id: str) -> dict[str, object]:
        _require_run(run_id)
        return broker.run()

    @app.get("/api/runs/{run_id}/conversation")
    async def conversation(run_id: str) -> dict[str, object]:
        _require_run(run_id)
        return {"entries": [entry.browser_value() for entry in broker.conversation]}

    @app.post("/api/runs/{run_id}/conversation")
    async def submit_user_message(run_id: str, input: ConversationInput) -> JSONResponse:
        _require_run(run_id)
        return JSONResponse((await _conversation_or_400(broker, "user", input.text)).browser_value())

    @app.post("/api/runs/{run_id}/agents")
    async def manifest(run_id: str, input: ManifestInput) -> JSONResponse:
        _require_run(run_id)
        try:
            return JSONResponse(broker.manifest(input.role, input.label).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/runs/{run_id}/envelopes")
    async def send_envelope(run_id: str, input: EnvelopeInput) -> JSONResponse:
        _require_run(run_id)
        try:
            envelope = broker.send(
                input.kind,
                input.sender,
                input.recipient,
                input.body,
                input.assignment_id,
            )
        except ValueError as error:
            raise _broker_http_error(error) from error
        return JSONResponse(envelope.delivery_value())

    @app.post("/api/runs/{run_id}/envelopes/{sequence}/delivered")
    async def mark_delivered(run_id: str, sequence: int) -> JSONResponse:
        _require_run(run_id)
        try:
            return JSONResponse(broker.mark_delivered(sequence).delivery_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/runs/{run_id}/agents/{role}/assignments")
    async def assign(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        _require_run(run_id)
        try:
            broker.assign(role, input.assignment_id)
            return JSONResponse(broker.agents[role].browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/runs/{run_id}/agents/{role}/acknowledgments")
    async def acknowledge(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        _require_run(run_id)
        try:
            return JSONResponse(broker.acknowledge(role, input.assignment_id).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.post("/api/runs/{run_id}/agents/{role}/completions")
    async def complete(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        _require_run(run_id)
        try:
            return JSONResponse(broker.complete(role, input.assignment_id).browser_value())
        except ValueError as error:
            raise _broker_http_error(error) from error

    @app.delete("/api/runs/{run_id}/agents/{role}")
    async def stop(run_id: str, role: str) -> Response:
        _require_run(run_id)
        try:
            broker.stop(role)
        except ValueError as error:
            raise _broker_http_error(error) from error
        return Response(status_code=204)

    @app.get("/api/runs/{run_id}/orchestrator/stream")
    async def orchestrator_stream(run_id: str) -> StreamingResponse:
        _require_run(run_id)

        async def events() -> AsyncIterator[str]:
            async for envelope in broker.deliveries():
                yield f"event: envelope\ndata: {json.dumps(envelope.delivery_value())}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    def live_state_stream(request: Request) -> StreamingResponse:
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

    @app.get("/api/stream")
    async def stream(request: Request) -> StreamingResponse:
        return live_state_stream(request)

    @app.get("/api/runs/{run_id}/stream")
    async def run_stream(run_id: str, request: Request) -> StreamingResponse:
        _require_run(run_id)
        return live_state_stream(request)

    return app


async def _conversation_or_400(broker: Broker, author: str, text: str) -> ConversationEntry:
    try:
        return await broker.record_conversation(author, text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _require_run(run_id: str) -> None:
    if run_id != RUN_ID:
        raise HTTPException(status_code=404, detail="unknown shop run")


def _broker_http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "unknown" in detail:
        return HTTPException(status_code=404, detail=detail)
    if "required" in detail:
        return HTTPException(status_code=400, detail=detail)
    return HTTPException(status_code=409, detail=detail)
