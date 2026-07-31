"""HTTP, SSE, and static browser surface for the local shop floor."""

from __future__ import annotations

import asyncio
import json
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

from .watcher import ModelWatcher


RUN_ID = "shop-floor"
STATIC_ROOT = Path(__file__).parent / "static"
ROLE_LABELS = {"foreman": "Foreman", "designer": "Designer", "machinist": "Machinist"}
MESSAGE_KINDS = {"direction", "assignment", "report"}


@dataclass
class Agent:
    role: str
    label: str
    state: str
    assignment_id: str = ""
    pending_assignments: list[str] = field(default_factory=list)

    def browser_value(self) -> dict[str, str]:
        return {"role": self.role, "label": self.label, "state": self.state}


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

    def browser_value(self) -> dict[str, object]:
        return {key: value for key, value in asdict(self).items() if value not in ("", None)}


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

    def __init__(self, *, event_history_limit: int = 20) -> None:
        self.agents: dict[str, Agent] = {}
        self.subscribers: set[asyncio.Queue[dict[str, object]]] = set()
        self.delivery_subscribers: set[asyncio.Queue[Envelope | None]] = set()
        self.conversation: list[ConversationEntry] = []
        self.envelopes: list[Envelope] = []
        self.delivered: set[int] = set()
        self.available: set[int] = set()
        self.assignment_envelopes: dict[tuple[str, str], int] = {}
        self.events: deque[BrokerEvent] = deque(maxlen=event_history_limit)
        self.latest_event_sequence = 0
        self._next_envelope_sequence = 0
        self._event_changed = asyncio.Event()

    def run(self) -> dict[str, object]:
        return {
            "id": RUN_ID,
            "status": "running",
            "agents": [agent.browser_value() for agent in sorted(self.agents.values(), key=lambda item: item.role)],
            "events": [event.browser_value() for event in self.events],
        }

    def manifest(self, role: str, label: str) -> Agent:
        if role not in ROLE_LABELS:
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
        if sender != "maker" and sender not in ROLE_LABELS:
            raise ValueError("unknown agent sender")
        if recipient not in ROLE_LABELS:
            raise ValueError("unknown agent recipient")
        body = body.strip()
        if not body:
            raise ValueError("body is required")
        if kind == "assignment":
            if sender != "foreman":
                raise ValueError("only foreman assigns work")
            return self.assign(recipient, assignment_id, body=body)
        if kind == "report" and recipient != "foreman":
            raise ValueError("reports must be addressed to foreman")
        envelope = self._new_envelope(kind, sender, recipient, body, assignment_id)
        self._make_available(envelope)
        return envelope

    def assign(self, role: str, assignment_id: str, *, body: str | None = None) -> Envelope:
        agent = self._agent(role)
        if not assignment_id:
            raise ValueError("assignment_id is required")
        if (role, assignment_id) in self.assignment_envelopes:
            raise ValueError("assignment already exists")
        envelope = self._new_envelope(
            "assignment",
            "foreman",
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
        agent = self._agent(role)
        if agent.state != "waiting" or agent.assignment_id != assignment_id:
            raise ValueError("invalid lifecycle report")
        agent.state = "active"
        self.publish("work_acknowledged", agent, role=role, assignment_id=assignment_id)
        return agent

    def complete(self, role: str, assignment_id: str) -> Agent:
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
        if role not in ROLE_LABELS:
            raise ValueError("unknown agent")
        return [
            envelope
            for envelope in self.envelopes
            if envelope.recipient == role
            and envelope.sequence in self.available
            and envelope.sequence not in self.delivered
        ]

    def mark_delivered(self, sequence: int) -> Envelope:
        envelope = self._envelope(sequence)
        if sequence not in self.available:
            raise ValueError("envelope is not available")
        if sequence in self.delivered:
            raise ValueError("envelope already delivered")
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

    async def record_conversation(self, author: str, text: str) -> ConversationEntry:
        text = text.strip()
        if not text:
            raise ValueError("text is required")
        entry = ConversationEntry(sequence=len(self.conversation) + 1, author=author, text=text)
        self.conversation.append(entry)
        self.publish("conversation_entry", entry)
        if author == "maker":
            self.send("direction", "maker", "foreman", text)
        return entry

    async def wait_for_events(self, after: int) -> list[BrokerEvent]:
        while True:
            events = [event for event in self.events if event.sequence > after]
            if events:
                return events
            self._event_changed.clear()
            if any(event.sequence > after for event in self.events):
                continue
            await self._event_changed.wait()

    async def deliveries(self) -> AsyncIterator[Envelope]:
        queue: asyncio.Queue[Envelope | None] = asyncio.Queue()
        self.delivery_subscribers.add(queue)
        try:
            for role in ROLE_LABELS:
                for envelope in self.pending_for(role):
                    await queue.put(envelope)
            while True:
                envelope = await queue.get()
                if envelope is None:
                    return
                if envelope.sequence not in self.delivered:
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
            summary=_event_summary(kind, role, sender, recipient, assignment_id),
            role=role,
            sender=sender,
            recipient=recipient,
            assignment_id=assignment_id,
            envelope_sequence=envelope_sequence,
        )
        self.events.append(event)
        self._event_changed.set()
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

    def _envelope(self, sequence: int) -> Envelope:
        try:
            return next(item for item in self.envelopes if item.sequence == sequence)
        except StopIteration as error:
            raise ValueError("unknown envelope") from error


def create_app(
    project_root: Path | None = None,
    *,
    artifact_root: Path | None = None,
    broker: Broker | None = None,
    solid_command: Sequence[str] | None = None,
    build_environment: Mapping[str, str] | None = None,
    poll_interval: float = 0.5,
) -> FastAPI:
    # The watcher belongs to the application, not the orchestrator: the
    # thing it refreshes is this app's own artifact route, and this app
    # is what publishes model_changed. Both entry points -- the full
    # orchestrated floor and broker-only mode -- get it with no
    # duplicated wiring. An app built without a solid command runs no
    # watcher and spawns no subprocesses.
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        watcher_task: asyncio.Task[None] | None = None
        if solid_command is not None and project_root is not None and build_root is not None:
            watcher = ModelWatcher(
                project_root,
                build_root,
                solid_command,
                app.state.broker.publish,
                extra_environment=build_environment,
                poll_interval=poll_interval,
            )
            app.state.model_watcher = watcher
            watcher_task = asyncio.create_task(watcher.run())
        try:
            yield
        finally:
            if watcher_task is not None:
                watcher_task.cancel()
                await asyncio.gather(watcher_task, return_exceptions=True)

    app = FastAPI(title="shop-floor", lifespan=lifespan)
    broker = broker or Broker()
    app.state.broker = broker
    app.state.model_watcher = None
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")
    build_root = artifact_root or (project_root / "_build" if project_root is not None else None)

    @app.get("/artifacts/{artifact_path:path}")
    async def artifact(artifact_path: str) -> FileResponse:
        if build_root is None:
            raise HTTPException(status_code=404, detail="no project build is available")
        candidate = (build_root / artifact_path).resolve()
        if build_root.resolve() not in candidate.parents and candidate != build_root.resolve():
            raise HTTPException(status_code=404, detail="unknown artifact")
        if not candidate.is_file():
            raise HTTPException(status_code=404, detail="unknown artifact")
        return FileResponse(candidate)

    @app.get("/")
    async def browser_page() -> FileResponse:
        return FileResponse(STATIC_ROOT / "index.html", media_type="text/html")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "open"}

    @app.get("/events/lifecycle")
    async def lifecycle_events(request: Request) -> StreamingResponse:
        async def events() -> AsyncIterator[str]:
            yield "event: lifecycle\ndata: open\n\n"
            while not await request.is_disconnected():
                yield ": keepalive\n\n"
                await asyncio.sleep(15)

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

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

    @app.post("/api/runs/{run_id}/conversation/maker")
    async def submit_maker_message(run_id: str, input: ConversationInput) -> JSONResponse:
        _require_run(run_id)
        return JSONResponse((await _conversation_or_400(broker, "maker", input.text)).browser_value())

    @app.post("/api/runs/{run_id}/foreman/publish")
    async def publish_foreman_message(run_id: str, input: ConversationInput) -> JSONResponse:
        _require_run(run_id)
        return JSONResponse((await _conversation_or_400(broker, "foreman", input.text)).browser_value())

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

    @app.get("/api/runs/{run_id}/stream")
    async def stream(run_id: str, request: Request) -> StreamingResponse:
        _require_run(run_id)
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()

        async def events() -> AsyncIterator[str]:
            broker.subscribers.add(subscriber)
            try:
                while not await request.is_disconnected():
                    try:
                        event = await asyncio.wait_for(subscriber.get(), timeout=15)
                        yield f"event: shop-floor\ndata: {json.dumps(event)}\n\n"
                    except TimeoutError:
                        yield ": keepalive\n\n"
            finally:
                broker.subscribers.discard(subscriber)

        return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    return app


async def _conversation_or_400(broker: Broker, author: str, text: str) -> ConversationEntry:
    try:
        return await broker.record_conversation(author, text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _event_summary(kind: str, role: str, sender: str, recipient: str, assignment_id: str) -> str:
    labels = ROLE_LABELS
    if kind == "agent_manifested":
        return f"{labels.get(role, role.title())} manifested"
    if kind == "agent_stopped":
        return f"{labels.get(role, role.title())} stopped"
    if kind.endswith("_available"):
        name = kind.removesuffix("_available").replace("_", " ").title()
        return f"{name} · {labels.get(sender, sender.title())} → {labels.get(recipient, recipient.title())}"
    if kind == "assignment_queued":
        return f"Assignment queued · {labels.get(role, role.title())} · {assignment_id}"
    if kind == "work_acknowledged":
        return f"Work started · {labels.get(role, role.title())} · {assignment_id}"
    if kind == "work_completed":
        return f"Work completed · {labels.get(role, role.title())} · {assignment_id}"
    if kind == "envelope_delivered":
        return f"Delivered · {labels.get(recipient, recipient.title())}"
    if kind == "conversation_entry":
        return "Conversation updated"
    if kind == "model_changed":
        return "Model updated"
    if kind == "model_build_failed":
        return "Model rebuild failed"
    if kind == "model_build_succeeded":
        return "Model rebuilt"
    return kind.replace("_", " ").title()


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
