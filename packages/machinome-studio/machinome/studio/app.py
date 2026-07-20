"""HTTP, SSE, and static browser surface for the local shop floor."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


RUN_ID = "shop-floor"
STATIC_ROOT = Path(__file__).parent / "static"


@dataclass
class Agent:
    role: str
    label: str
    state: str
    assignment_id: str = ""

    def browser_value(self) -> dict[str, str]:
        return {"role": self.role, "label": self.label, "state": self.state}


class ManifestInput(BaseModel):
    role: str
    label: str


class AssignmentInput(BaseModel):
    assignment_id: str


class Broker:
    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}
        self.subscribers: set[asyncio.Queue[dict[str, object]]] = set()

    def run(self) -> dict[str, object]:
        return {
            "id": RUN_ID,
            "status": "running",
            "agents": [agent.browser_value() for agent in sorted(self.agents.values(), key=lambda agent: agent.role)],
        }

    def publish(self, kind: str, agent: Agent) -> None:
        event: dict[str, object] = {"kind": kind, "payload": agent.browser_value()}
        for subscriber in self.subscribers:
            try:
                subscriber.put_nowait(event)
            except asyncio.QueueFull:
                pass


def create_app() -> FastAPI:
    app = FastAPI(title="shop-floor")
    broker = Broker()
    app.state.broker = broker
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")

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

    @app.post("/api/runs/{run_id}/agents")
    async def manifest(run_id: str, input: ManifestInput) -> JSONResponse:
        _require_run(run_id)
        if not input.role or not input.label:
            raise HTTPException(status_code=400, detail="role and label are required")
        if input.role in broker.agents:
            raise HTTPException(status_code=409, detail="agent already manifested")
        agent = Agent(role=input.role, label=input.label, state="waiting")
        broker.agents[agent.role] = agent
        broker.publish("agent_manifested", agent)
        return JSONResponse(agent.browser_value())

    @app.post("/api/runs/{run_id}/agents/{role}/assignments")
    async def assign(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        agent = _agent_for_transition(broker, run_id, role, input.assignment_id)
        if agent.state != "waiting":
            raise HTTPException(status_code=409, detail="invalid lifecycle report")
        agent.assignment_id = input.assignment_id
        broker.publish("assignment", agent)
        return JSONResponse(agent.browser_value())

    @app.post("/api/runs/{run_id}/agents/{role}/acknowledgments")
    async def acknowledge(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        agent = _agent_for_transition(broker, run_id, role, input.assignment_id)
        if agent.state != "waiting" or agent.assignment_id != input.assignment_id:
            raise HTTPException(status_code=409, detail="invalid lifecycle report")
        agent.state = "active"
        broker.publish("work_acknowledged", agent)
        return JSONResponse(agent.browser_value())

    @app.post("/api/runs/{run_id}/agents/{role}/completions")
    async def complete(run_id: str, role: str, input: AssignmentInput) -> JSONResponse:
        agent = _agent_for_transition(broker, run_id, role, input.assignment_id)
        if agent.state != "active" or agent.assignment_id != input.assignment_id:
            raise HTTPException(status_code=409, detail="invalid lifecycle report")
        agent.state = "waiting"
        agent.assignment_id = ""
        broker.publish("work_completed", agent)
        return JSONResponse(agent.browser_value())

    @app.delete("/api/runs/{run_id}/agents/{role}")
    async def stop(run_id: str, role: str) -> Response:
        _require_run(run_id)
        agent = broker.agents.pop(role, None)
        if agent is None:
            raise HTTPException(status_code=404, detail="unknown agent")
        broker.publish("agent_stopped", agent)
        return Response(status_code=204)

    @app.get("/api/runs/{run_id}/stream")
    async def stream(run_id: str, request: Request) -> StreamingResponse:
        _require_run(run_id)
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=8)

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


def _require_run(run_id: str) -> None:
    if run_id != RUN_ID:
        raise HTTPException(status_code=404, detail="unknown shop run")


def _agent_for_transition(broker: Broker, run_id: str, role: str, assignment_id: str) -> Agent:
    _require_run(run_id)
    if not assignment_id:
        raise HTTPException(status_code=400, detail="assignment_id is required")
    agent = broker.agents.get(role)
    if agent is None:
        raise HTTPException(status_code=404, detail="unknown agent")
    return agent
