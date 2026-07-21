"""Single-owner Codex app-server orchestration for a live shop run."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import shlex
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Protocol

import uvicorn

from .app import Broker, Envelope, ROLE_LABELS, create_app
from .preparation import PreparationError, default_project_home, default_solid_command, prepare_project


SHOP_ROLES = tuple(ROLE_LABELS)


class InactiveTurn(RuntimeError):
    """The expected turn completed before steering was accepted."""


class CodexControl(Protocol):
    async def start_thread(self, role: str) -> str: ...
    async def start_turn(self, thread_id: str, message: str) -> str: ...
    async def steer_turn(self, thread_id: str, turn_id: str, message: str) -> None: ...
    async def interrupt_turn(self, thread_id: str, turn_id: str) -> None: ...
    async def close_thread(self, thread_id: str) -> None: ...
    async def close(self) -> None: ...


class BrokerControl(Protocol):
    async def manifest(self, role: str, label: str) -> None: ...
    async def mark_delivered(self, sequence: int) -> None: ...
    async def record_conversation(self, author: str, text: str) -> None: ...


@dataclass
class RoleRuntime:
    thread_id: str
    active_turn_id: str | None = None


class LocalBrokerControl:
    def __init__(self, broker: Broker) -> None:
        self.broker = broker

    async def manifest(self, role: str, label: str) -> None:
        self.broker.manifest(role, label)

    async def mark_delivered(self, sequence: int) -> None:
        self.broker.mark_delivered(sequence)

    async def record_conversation(self, author: str, text: str) -> None:
        await self.broker.record_conversation(author, text)


class ShopOrchestrator:
    """Own role threads and perform only deterministic lifecycle and routing."""

    def __init__(self, codex: CodexControl, broker: BrokerControl) -> None:
        self.codex = codex
        self.broker = broker
        self.roles: dict[str, RoleRuntime] = {}
        self._delivery_locks = {role: asyncio.Lock() for role in SHOP_ROLES}
        self._completed_turns: set[str] = set()

    async def open(self) -> None:
        start = getattr(self.codex, "start", None)
        if start is not None:
            await start()
        try:
            for role in SHOP_ROLES:
                thread_id = await self.codex.start_thread(role)
                self.roles[role] = RoleRuntime(thread_id=thread_id)
                await self.broker.manifest(role, ROLE_LABELS[role])
        except BaseException:
            await self.close()
            raise

    async def deliver(self, envelope: Envelope | dict[str, Any]) -> None:
        value = envelope.delivery_value() if isinstance(envelope, Envelope) else envelope
        sequence = int(value["sequence"])
        role = str(value["recipient"])
        message = self._message(value)
        runtime = self.roles.get(role)
        if runtime is None:
            raise ValueError(f"unknown orchestrated role: {role}")
        async with self._delivery_locks[role]:
            if runtime.active_turn_id is None:
                turn_id = await self.codex.start_turn(runtime.thread_id, message)
                runtime.active_turn_id = None if turn_id in self._completed_turns else turn_id
            else:
                try:
                    await self.codex.steer_turn(runtime.thread_id, runtime.active_turn_id, message)
                except InactiveTurn:
                    turn_id = await self.codex.start_turn(runtime.thread_id, message)
                    runtime.active_turn_id = None if turn_id in self._completed_turns else turn_id
            await self.broker.mark_delivered(sequence)

    async def handle_notification(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        params = message.get("params", {})
        if method == "item/completed":
            item = params.get("item", {})
            runtime = self.roles.get("foreman")
            if (
                runtime is not None
                and params.get("threadId") == runtime.thread_id
                and item.get("type") == "agentMessage"
                and str(item.get("text", "")).strip()
            ):
                await self.broker.record_conversation("foreman", str(item["text"]).strip())
            return
        if method not in {"turn/completed", "turn/started"}:
            return
        thread_id = params.get("threadId")
        turn = params.get("turn", {})
        turn_id = turn.get("id")
        runtime = next((item for item in self.roles.values() if item.thread_id == thread_id), None)
        if runtime is None:
            return
        if method == "turn/started":
            runtime.active_turn_id = turn_id
        else:
            self._completed_turns.add(turn_id)
            if runtime.active_turn_id == turn_id:
                runtime.active_turn_id = None

    @staticmethod
    def _message(value: dict[str, Any]) -> str:
        lines = [
            "Shop broker message:",
            f"kind: {value.get('kind', 'direction')}",
            f"sender: {value.get('sender', 'unknown')}",
            f"recipient: {value['recipient']}",
        ]
        assignment_id = value.get("assignment_id")
        if assignment_id:
            lines.append(f"assignment: {assignment_id}")
        if value.get("kind") == "assignment" and assignment_id:
            lines.extend(
                (
                    "ASSIGNMENT LIFECYCLE GATE:",
                    "Before anything else, your FIRST TOOL CALL must be:",
                    f"python -m floor.agent acknowledge --role {value['recipient']} --assignment {assignment_id}",
                    "Do not read files or investigate, load a role card or skill, start a development process, "
                    "or make any other tool call until that command succeeds.",
                )
            )
        lines.extend(("instruction:", str(value["body"])))
        return "\n".join(lines)

    async def close(self) -> None:
        for runtime in reversed(tuple(self.roles.values())):
            if runtime.active_turn_id is not None:
                await self.codex.interrupt_turn(runtime.thread_id, runtime.active_turn_id)
        for runtime in reversed(tuple(self.roles.values())):
            await self.codex.close_thread(runtime.thread_id)
        self.roles.clear()
        await self.codex.close()


class CodexAppServer:
    """Minimal newline-delimited JSON-RPC client owning one app-server process."""

    def __init__(
        self,
        cwd: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "codex",
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
        self.process: asyncio.subprocess.Process | None = None
        self.notifications: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._next_id = 0
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self.process is not None:
            return
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            "app-server",
            "--stdio",
            cwd=self.cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                **os.environ,
                "FLOOR_URL": self.broker_url,
                "PYTHONPATH": os.pathsep.join(
                    item for item in (str(self.cwd), os.environ.get("PYTHONPATH", "")) if item
                ),
            },
            start_new_session=True,
        )
        self._reader_task = asyncio.create_task(self._read_stdout())
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        await self._request(
            "initialize",
            {
                "clientInfo": {
                    "name": "solid-node-shop-orchestrator",
                    "title": "solid-node shop orchestrator",
                    "version": "0.1.0",
                },
                "capabilities": {"experimentalApi": True},
            },
        )
        await self._notify("initialized", {})

    async def start_thread(self, role: str) -> str:
        config_path = self.cwd / ".codex" / "agents" / f"{role}.toml"
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
        role_instructions = str(config.get("developer_instructions", ""))
        runtime_instructions = (
            f"Shop checkout: {self.cwd}\n"
            f"Active project: {self.project}\n"
            "Treat the active project as the sole mechanical-project repository for this shop run. "
            "Shop role cards and skills come from the shop checkout named above.\n\n"
        )
        if role == "machinist" and self.model_callback_url is not None:
            runtime_instructions += (
                "Live model development command (run it from the active project and keep it running "
                "throughout an active machining assignment):\n"
                f"{shlex.join(self.solid_command)} develop root --callback {shlex.quote(self.model_callback_url)}\n\n"
            )
        result = await self._request(
            "thread/start",
            {
                "cwd": str(self.project),
                "model": config.get("model"),
                "developerInstructions": runtime_instructions + role_instructions,
                "sandbox": "workspace-write",
                "serviceName": f"solid-node-shop-{role}",
            },
        )
        return str(result["thread"]["id"])

    async def start_turn(self, thread_id: str, message: str) -> str:
        result = await self._request(
            "turn/start",
            {"threadId": thread_id, "input": [{"type": "text", "text": message}]},
        )
        return str(result["turn"]["id"])

    async def steer_turn(self, thread_id: str, turn_id: str, message: str) -> None:
        try:
            await self._request(
                "turn/steer",
                {
                    "threadId": thread_id,
                    "expectedTurnId": turn_id,
                    "input": [{"type": "text", "text": message}],
                },
            )
        except RuntimeError as error:
            if "active turn" in str(error).lower() or "thread not found" in str(error).lower():
                raise InactiveTurn from error
            raise

    async def interrupt_turn(self, thread_id: str, turn_id: str) -> None:
        await self._request("turn/interrupt", {"threadId": thread_id, "turnId": turn_id})

    async def close_thread(self, thread_id: str) -> None:
        try:
            await self._request("thread/archive", {"threadId": thread_id})
        except RuntimeError as error:
            if "no rollout found for thread id" not in str(error).lower():
                raise

    async def close(self) -> None:
        if self.process is None:
            return
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=5)
        except asyncio.TimeoutError:
            self.process.terminate()
            await self.process.wait()
        if self._reader_task is not None:
            await self._reader_task
        if self._stderr_task is not None:
            await self._stderr_task
        self.process = None

    async def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("app-server is not running")
        self._next_id += 1
        request_id = self._next_id
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        self.process.stdin.write((json.dumps({"id": request_id, "method": method, "params": params}) + "\n").encode())
        await self.process.stdin.drain()
        return await asyncio.wait_for(future, timeout=30)

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("app-server is not running")
        self.process.stdin.write((json.dumps({"method": method, "params": params}) + "\n").encode())
        await self.process.stdin.drain()

    async def _read_stdout(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        while line := await self.process.stdout.readline():
            message = json.loads(line)
            request_id = message.get("id")
            if request_id is not None and ("result" in message or "error" in message):
                future = self._pending.pop(request_id, None)
                if future is None:
                    continue
                if "error" in message:
                    future.set_exception(RuntimeError(json.dumps(message["error"])))
                else:
                    future.set_result(message["result"])
            elif "method" in message:
                await self.notifications.put(message)

    async def _drain_stderr(self) -> None:
        assert self.process is not None and self.process.stderr is not None
        while await self.process.stderr.readline():
            pass


async def _serve(arguments: argparse.Namespace) -> None:
    project_home = arguments.project_home or default_project_home(arguments.cwd)
    solid_command = arguments.solid_command or default_solid_command(arguments.cwd)
    prepared = prepare_project(arguments.project_name, project_home=project_home, solid_command=solid_command)
    broker = Broker()
    callback_token = secrets.token_urlsafe(24)
    callback_url = f"http://127.0.0.1:{arguments.port}/api/runs/shop-floor/model/ready/{callback_token}"
    app = create_app(
        prepared.project_root,
        artifact_root=prepared.artifact_root,
        callback_token=callback_token,
        broker=broker,
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=arguments.port,
            log_level="info",
            timeout_graceful_shutdown=1,
        )
    )
    server_task = asyncio.create_task(server.serve())
    orchestrator: ShopOrchestrator | None = None
    delivery_task: asyncio.Task[None] | None = None
    notification_task: asyncio.Task[None] | None = None
    try:
        while not server.started and not server_task.done():
            await asyncio.sleep(0.01)
        if server_task.done():
            await server_task
            raise RuntimeError("shop-floor server stopped before opening")
        codex = CodexAppServer(
            arguments.cwd,
            project=prepared.project_root,
            command=arguments.codex_command,
            broker_url=f"http://127.0.0.1:{arguments.port}",
            solid_command=solid_command,
            model_callback_url=callback_url,
        )
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker))
        await orchestrator.open()
        print(f"shop-floor open at http://127.0.0.1:{arguments.port}", flush=True)

        async def route_deliveries() -> None:
            assert orchestrator is not None
            async for envelope in broker.deliveries():
                await orchestrator.deliver(envelope)

        async def route_notifications() -> None:
            assert orchestrator is not None
            while True:
                await orchestrator.handle_notification(await codex.notifications.get())

        delivery_task = asyncio.create_task(route_deliveries())
        notification_task = asyncio.create_task(route_notifications())
        await server_task
    except asyncio.CancelledError:
        pass
    finally:
        broker.shutdown()
        route_tasks = tuple(task for task in (delivery_task, notification_task) if task is not None)
        for task in route_tasks:
            task.cancel()
        if route_tasks:
            await asyncio.gather(*route_tasks, return_exceptions=True)
        if orchestrator is not None:
            await orchestrator.close()
        if not server_task.done():
            server.should_exit = True
            await server_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the event-driven Codex shop")
    parser.add_argument("project_name", help="lowercase kebab-case project name below projects/")
    parser.add_argument("--port", type=int, default=int(os.environ.get("FLOOR_PORT", "9000")))
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="shop checkout containing .codex role adapters")
    parser.add_argument("--project-home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    parser.add_argument("--codex-command", default="codex", help=argparse.SUPPRESS)
    try:
        asyncio.run(_serve(parser.parse_args()))
    except PreparationError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
