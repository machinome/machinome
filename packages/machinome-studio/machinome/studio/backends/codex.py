# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Scoped Codex adapter borrowing the hub's independently authenticated owner."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field, replace
import json
from pathlib import Path
import shlex
from typing import Any
import uuid

from .base import (AgentActivity, BackendEvent, ContextUnrecoverable, DeliveryReceipt, InactiveTurn,
                   RoleContext, RoleHandle, RuntimeCatalogue, RuntimeChoice, skill_catalogue)
from .codex_policy import EFFORTS, MODEL_FINGERPRINTS, check_policy
from .codex_service import CodexService, CodexThread, ServiceReference, role_registry
from .codex_tools import FloorWorker, dynamic_result, validate_arguments
from .codex_wire import CodexProtocolError
from .claude import TRUST_FRAMING
from ..mcp_server import SKILL_TOOL
from ..profiles import BackendRuntime


@dataclass
class RoleState:
    handle: RoleHandle
    thread: CodexThread
    worker: FloorWorker
    runtime: BackendRuntime
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    active: str | None = None
    native_turn: str | None = None
    reader: asyncio.Task | None = None
    calls: dict[tuple[int, str, str, str], tuple[str, asyncio.Task]] = field(default_factory=dict)
    callbacks: set[asyncio.Task] = field(default_factory=set)
    worker_stopped: bool = False
    messages: set[tuple[str, str]] = field(default_factory=set)
    deliveries: dict[str, str] = field(default_factory=dict)
    closing: bool = False
    close_task: asyncio.Task | None = None
    stop_task: asyncio.Task | None = None
    failed_notice: bool = False
    latest_delivery: str | None = None


class CodexBackend:
    def __init__(self, *, shop_root: Path, project: Path | None = None, model: str | None = None,
                 broker_url: str = "http://127.0.0.1:9000", command: str = "codex",
                 machinome_command: str = "machinome", session_id: str | None = None,
                 codex_service: CodexService | None = None, codex_reference: ServiceReference | None = None):
        if command != "codex":
            raise ValueError("Scoped Codex command overrides are unsupported; Studio uses only its qualified pinned native installation")
        if codex_service is None or codex_reference is None or codex_reference.service is not codex_service:
            raise CodexProtocolError("Codex requires the hub's qualified project reference")
        if session_id is not None and session_id != codex_reference.session_id:
            raise CodexProtocolError("Codex adapter session differs from its owned project reference")
        if project is None:
            raise CodexProtocolError("Codex requires an explicit owned project root")
        self.service = codex_service
        self.reference = codex_reference
        self.shop_root = shop_root
        self.project = project.resolve()
        self.model = model
        self.broker_url = broker_url
        self.session_id = session_id or codex_reference.session_id
        self.machinome_command = tuple(shlex.split(machinome_command))
        self.roles: dict[str, RoleState] = {}
        self.events_queue: asyncio.Queue[BackendEvent | None] = asyncio.Queue()
        self.closing: asyncio.Task | None = None

    @property
    def events(self):
        async def iterator():
            while (event := await self.events_queue.get()) is not None:
                if event.is_current is None or event.is_current():
                    yield event
        return iterator()

    async def start(self) -> None:
        if self.reference.closing or self.closing is not None:
            raise CodexProtocolError("Codex project adapter is closing")

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        await self.start()
        if (role != context.agent.id or Path(context.active_project).resolve() != self.project
            or Path(context.shop_root).resolve() != self.shop_root.resolve() or context.active_model != self.model):
            raise CodexProtocolError("Codex role context differs from its immutable project contract")
        runtime = context.agent.runtime
        if runtime is None:
            raise CodexProtocolError("Codex role has no runtime")
        self._validate_runtime(runtime)
        registry = role_registry(context.agent)
        instructions = "\n".join([f"Active project: {Path(context.active_project).resolve()}",
            *([f"Active model: {context.active_model}. Leave sibling models to their owning sessions."] if context.active_model else []),
            f"Role: {role}; profile: {context.profile_id}; human label: {context.user_label}",
            "The following profile prompt is authoritative:", context.agent.prompt_path.read_text(),
            *skill_catalogue(context.agent.skills, f"floor_{SKILL_TOOL}"), TRUST_FRAMING])
        worker = FloorWorker(context, machinome_command=self.machinome_command,
                             broker_url=self.broker_url, session_id=self.session_id)
        thread = None
        try:
            await worker.start()
            thread = await self.reference.open_thread(role, {"model": runtime.model,
                "developerInstructions": instructions, "persistExtendedHistory": True}, registry)
            handle = RoleHandle(thread.identity, role)
            state = RoleState(handle, thread, worker, runtime)
            thread.quiesce = lambda: self._stop_worker(state)
            self.roles[handle.backend_id] = state
            state.reader = asyncio.create_task(self._consume(state))
            return handle
        except BaseException:
            await worker.close()
            if thread is not None:
                await thread.close()
            raise

    def _state(self, handle: RoleHandle) -> RoleState:
        state = self.roles.get(handle.backend_id)
        if state is None or state.handle != handle or state.closing:
            raise CodexProtocolError("Unknown or closed Codex role handle")
        return state

    @staticmethod
    def _validate_runtime(runtime: BackendRuntime) -> None:
        if runtime.backend != "codex" or runtime.provider is not None or runtime.model not in MODEL_FINGERPRINTS or runtime.effort not in EFFORTS:
            raise CodexProtocolError("Unsupported scoped Codex model or reasoning level")

    def _emit(self, state: RoleState, kind: str, **fields) -> None:
        if state.closing and not (kind == "activity" and fields.get("activity") is not None and fields["activity"].state != "running"):
            return
        if kind == "role_failed":
            if state.failed_notice:
                return
            state.failed_notice = True
            fields.setdefault("delivery_id", state.latest_delivery)
        generation = state.thread.generation
        terminal_activity = kind == "activity" and fields.get("activity") is not None and fields["activity"].state != "running"
        self.events_queue.put_nowait(BackendEvent(kind=kind, role=state.handle.role,
            handle_id=state.handle.backend_id,
            # A cancellation terminal must settle its already-published running
            # activity even after shared recovery advances this same handle.
            is_current=lambda: terminal_activity or (state.thread.generation == generation and self.roles.get(state.handle.backend_id) is state),
            **fields))

    async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        state = self._state(handle)
        async with state.lock:
            try:
                await self.service.recover()
                if state.worker_stopped:
                    old = state.worker
                    state.worker = FloorWorker(old.context, machinome_command=self.machinome_command,
                        broker_url=self.broker_url, session_id=self.session_id)
                    await state.worker.start()
                    state.worker_stopped = False
                    state.stop_task = None
                if state.active is not None:
                    raise CodexProtocolError("Codex role already has an active delivery")
                connection = self.service.connection
                if connection is None:
                    raise CodexProtocolError("Codex transport is unavailable")
                await check_policy(connection, self.service._policy)
                # Set BEFORE attempted send: an ambiguous failure is used history.
                state.thread.used = True
                response = await connection.rpc("turn/start", {"threadId": state.thread.thread_id,
                    "input": [{"type": "text", "text": message}], "model": state.runtime.model,
                    "effort": state.runtime.effort, "environments": [], "approvalPolicy": "never",
                    "sandboxPolicy": {"type": "readOnly"}})
                native = response["turn"]["id"]
                if not isinstance(native, str) or not native:
                    raise CodexProtocolError("Codex returned an invalid turn identity")
                state.native_turn = native
                state.active = uuid.uuid4().hex
                state.latest_delivery = state.active
                state.failed_notice = False
                state.calls.clear()
                state.deliveries[native] = state.active
                if len(state.deliveries) > 64:
                    oldest = next(iter(state.deliveries))
                    state.deliveries.pop(oldest)
                    state.messages = {key for key in state.messages if key[0] != oldest}
                self._emit(state, "turn_started", delivery_id=state.active)
                return DeliveryReceipt(state.active, True)
            except Exception:
                await self._stop_worker(state)
                raise ContextUnrecoverable("Retained Codex role context is unavailable; no fresh replacement was started") from None

    async def _steer(self, state: RoleState, expected: str, message: str) -> DeliveryReceipt:
        async with state.lock:
            if state.active != expected or state.native_turn is None:
                raise InactiveTurn("Codex delivery already completed")
            connection = self.service.connection
            if connection is None or connection.dead.is_set():
                raise ContextUnrecoverable("Retained Codex transport is unavailable")
            try:
                await connection.rpc("turn/steer", {"threadId": state.thread.thread_id,
                    "expectedTurnId": state.native_turn, "input": [{"type": "text", "text": message}]})
            except CodexProtocolError:
                if connection.dead.is_set():
                    raise ContextUnrecoverable("Retained Codex transport is unavailable") from None
                try:
                    retained = (await connection.rpc("thread/read", {"threadId": state.thread.thread_id, "includeTurns": True}))["thread"]
                    expected_turn = next((turn for turn in retained["turns"] if turn["id"] == state.native_turn), None)
                    if retained["id"] == state.thread.thread_id and expected_turn is not None and expected_turn.get("status") in {"completed", "interrupted"}:
                        completed = state.active
                        if expected_turn["status"] == "interrupted":
                            await self._stop_worker(state)
                        state.active = state.native_turn = None
                        if completed is not None:
                            self._emit(state, "turn_completed", delivery_id=completed)
                        raise InactiveTurn("Codex delivery completed before steering")
                except InactiveTurn:
                    raise
                except Exception:
                    pass
                # Generic native rejections include policy/auth failures. They
                # are never interpreted as permission to start a fresh turn.
                raise ContextUnrecoverable("Codex steering was rejected; retained context was preserved") from None
            return DeliveryReceipt(expected, True)

    async def deliver_steer(self, handle: RoleHandle, expected_delivery_id: str, message: str) -> DeliveryReceipt:
        return await self._steer(self._state(handle), expected_delivery_id, message)

    async def deliver_notice(self, handle: RoleHandle, expected_delivery_id: str, message: str) -> bool:
        try:
            await self._steer(self._state(handle), expected_delivery_id, message)
            return True
        except InactiveTurn:
            return False

    async def _consume(self, state: RoleState) -> None:
        try:
            while True:
                frame = await state.thread.events.get()
                async with state.lock:
                    if state.closing or frame.get("studioGeneration") != state.thread.generation:
                        continue
                    method, params = frame.get("method"), frame.get("params", {})
                    item_type = params.get("item", {}).get("type") if isinstance(params.get("item"), dict) else None
                    if (item_type in {"commandExecution", "fileChange", "mcpToolCall", "webSearch", "imageView", "imageGeneration",
                                      "collabAgentToolCall", "toolSearch"}
                        or method == "model/rerouted" or "approval" in str(method).lower() or "requestUserInput" in str(method)):
                        await self.service.invalidate()
                        self._emit(state, "role_failed", error="Codex native authority violated the scoped role contract")
                        continue
                    if method == "studio/transportFailed":
                        await self._stop_worker(state)
                        if frame.get("studioGeneration") != state.thread.generation:
                            continue
                        state.active = state.native_turn = None
                        self._emit(state, "role_failed", error="Studio Codex transport stopped; retained context recovery is required")
                    elif method == "item/tool/call":
                        # Tasks permit native notices/completion to keep routing
                        # while a bounded floor worker runs a long build.
                        callback = asyncio.create_task(self._callback(state, frame))
                        state.callbacks.add(callback)
                        callback.add_done_callback(state.callbacks.discard)
                    elif method == "item/completed" and params.get("turnId") in state.deliveries:
                        item = params.get("item", {})
                        message_key = (params["turnId"], item.get("id"))
                        if (item.get("type") == "agentMessage" and isinstance(item.get("text"), str)
                            and isinstance(item.get("id"), str) and message_key not in state.messages):
                            state.messages.add(message_key)
                            self._emit(state, "role_message", text=item["text"], delivery_id=state.deliveries[params["turnId"]])
                    elif method == "thread/tokenUsage/updated" and params.get("turnId") in state.deliveries:
                        total = params.get("tokenUsage", {}).get("total", {})
                        if all(type(total.get(key)) is int and total[key] >= 0 for key in ("inputTokens", "outputTokens")):
                            self._emit(state, "activity", activity=AgentActivity(uuid.uuid4().hex, state.handle.role,
                                "message", "completed", "token usage", "Codex session tokens",
                                input_tokens=total["inputTokens"], output_tokens=total["outputTokens"]))
                    elif method == "turn/completed" and params.get("turn", {}).get("id") == state.native_turn:
                        turn = params["turn"]
                        delivery = state.active
                        if turn.get("status") in {"failed", "interrupted"}:
                            await self._stop_worker(state)
                        state.active = state.native_turn = None
                        if turn.get("status") == "failed":
                            self._emit(state, "role_failed", error="Codex delivery failed; retained context was preserved")
                        elif delivery is not None:
                            self._emit(state, "turn_completed", delivery_id=delivery)
                    elif "id" in frame:
                        connection = self.service.connection
                        if connection is not None:
                            await connection.send({"id": frame["id"], "error": {"code": -32601, "message": "Studio denies undeclared requests"}})
        except asyncio.CancelledError:
            raise
        except Exception:
            if not state.closing:
                await self._stop_worker(state)
                self._emit(state, "role_failed", error="Studio Codex role routing failed")

    async def _callback(self, state: RoleState, frame: dict[str, Any]) -> None:
        result = {"success": False, "contentItems": [{"type": "inputText", "text": "Rejected invalid or stale Studio tool call"}]}
        generation = frame.get("studioGeneration")
        connection = self.service.connection
        params = frame.get("params", {})
        fresh = False
        activity = None
        try:
            async with state.lock:
                if (state.closing or generation != state.thread.generation or params.get("threadId") != state.thread.thread_id
                    or params.get("turnId") != state.native_turn or state.active is None or params.get("namespace") not in (None, "functions")
                    or not isinstance(params.get("callId"), str) or not params["callId"]):
                    raise ValueError
                tool = next((item for item in state.thread.registry if item["name"] == params.get("tool")), None)
                if tool is None:
                    raise ValueError
                validate_arguments(params.get("arguments"), tool["inputSchema"])
                if any(params["arguments"].get(field, state.handle.role) != state.handle.role for field in ("sender", "role")):
                    raise ValueError
                if tool["name"] in {"floor_assign", "floor_direction"} and params["arguments"].get("recipient") not in state.worker.context.agent.assigns:
                    raise ValueError
                serialized = json.dumps({"tool": tool["name"], "arguments": params["arguments"]}, sort_keys=True, separators=(",", ":"))
                key = (generation, state.thread.thread_id, state.native_turn, params["callId"])
                cached = state.calls.get(key)
                if cached is not None and cached[0] != serialized:
                    raise ValueError
                if cached is None:
                    canonical = tool["name"] if tool["name"] in state.worker.names else tool["name"].removeprefix("floor_")
                    task = asyncio.create_task(state.worker.rpc("tools/call", {"name": canonical, "arguments": params["arguments"]}))
                    state.calls[key] = (serialized, task)
                    fresh = True
                    path = params["arguments"].get("path", "")
                    diff = params["arguments"].get("unified_diff", "")
                    if not path and diff:
                        path = next((line[4:].removeprefix("b/") for line in diff.splitlines() if line.startswith("+++ ") and line[4:] != "/dev/null"), "")
                    activity = AgentActivity(uuid.uuid4().hex, state.handle.role,
                        "file" if canonical in {"write_file", "edit_file", "apply_patch"} else "tool", "running", canonical,
                        f"{canonical}{' · ' + path if isinstance(path, str) and path else ''}",
                        path=path if isinstance(path, str) else "", diff=diff[:16000])
                    self._emit(state, "activity", activity=activity)
                else:
                    task = cached[1]
            result = dynamic_result(await asyncio.shield(task))
        except asyncio.CancelledError:
            result = {"success": False, "contentItems": [{"type": "inputText", "text": "Floor tool cancelled because its role worker stopped"}]}
            raise
        except Exception:
            pass
        finally:
            if fresh and activity is not None:
                image = any(item["type"] == "inputImage" for item in result["contentItems"])
                detail = "\n".join(item.get("text", "") for item in result["contentItems"] if item["type"] == "inputText")[:2000]
                if image:
                    detail = "Image result delivered to the model" + ("\n" + detail if detail else "")
                summary = activity.summary + (" · image result" if image else " · " + detail[:160] if detail else "")
                self._emit(state, "activity", activity=replace(activity, state="completed" if result["success"] else "failed", summary=summary, detail=detail))
        # Never answer an old connection's request on a new process generation.
        if connection is not None and connection is self.service.connection and generation == state.thread.generation and not connection.dead.is_set():
            try:
                await connection.send({"id": frame["id"], "result": result})
            except CodexProtocolError:
                pass

    async def interrupt(self, handle: RoleHandle) -> None:
        state = self._state(handle)
        async with state.lock:
            if state.native_turn is not None and self.service.connection is not None:
                await self.service.connection.rpc("turn/interrupt", {"threadId": state.thread.thread_id, "turnId": state.native_turn})

    async def _stop_worker(self, state: RoleState) -> None:
        if state.stop_task is None:
            state.stop_task = asyncio.create_task(self._quiesce_worker(state))
        await asyncio.shield(state.stop_task)

    async def _quiesce_worker(self, state: RoleState) -> None:
        # This barrier deliberately takes no state.lock: a delivery owns that
        # lock while requesting shared recovery, and all sibling workers must
        # stop before any native generation is restarted.
        state.worker_stopped = True
        state.active = state.native_turn = None
        await state.worker.close()
        pending = [task for task in state.callbacks if task is not asyncio.current_task()]
        for task in pending:
            task.cancel()
        for _, task in state.calls.values():
            if not task.done():
                task.cancel()
        await asyncio.gather(*pending, *(task for _, task in state.calls.values()), return_exceptions=True)

    async def _close_role(self, state: RoleState) -> None:
        state.closing = True
        # Stop project-mutating descendants before native history cleanup.
        try:
            await self._stop_worker(state)
        finally:
            for _, task in state.calls.values():
                if not task.done():
                    task.cancel()
            await asyncio.gather(*(task for _, task in state.calls.values()), return_exceptions=True)
            if state.reader is not None:
                state.reader.cancel()
                await asyncio.gather(state.reader, return_exceptions=True)
            try:
                await state.thread.close()
            finally:
                self.roles.pop(state.handle.backend_id, None)

    async def close_role(self, handle: RoleHandle) -> None:
        state = self.roles.get(handle.backend_id)
        if state is None:
            return
        if state.close_task is None:
            state.closing = True
            state.close_task = asyncio.create_task(self._close_role(state))
        await asyncio.shield(state.close_task)

    async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
        if self.service.invalidated:
            reason = "Codex isolation contract failed; close its projects before reopening"
            return RuntimeCatalogue(False, reason=reason, unavailable={"codex": reason})
        if self.service.connection is None or self.service.connection.dead.is_set() or self.reference.closing:
            reason = "Codex transport is unavailable; retained context recovery or dedicated Studio login is required"
            return RuntimeCatalogue(False, reason=reason, unavailable={"codex": reason})
        return RuntimeCatalogue(True, tuple(RuntimeChoice(model, tuple(EFFORTS), "codex") for model in MODEL_FINGERPRINTS))

    async def update_runtime(self, handle: RoleHandle, runtime: BackendRuntime) -> None:
        self._validate_runtime(runtime)
        state = self._state(handle)
        async with state.lock:
            if state.active is not None:
                raise CodexProtocolError("Codex runtime can change only while idle")
            state.runtime = runtime

    async def _close(self) -> None:
        try:
            await asyncio.gather(*(self.close_role(state.handle) for state in tuple(self.roles.values())), return_exceptions=True)
        finally:
            try:
                await self.reference.close()
            finally:
                self.events_queue.put_nowait(None)

    async def close(self) -> None:
        if self.closing is None:
            self.closing = asyncio.create_task(self._close())
        await asyncio.shield(self.closing)
