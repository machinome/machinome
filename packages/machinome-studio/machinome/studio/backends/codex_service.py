# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Registry-injected shared auth owner; projects borrow isolated thread handles."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import uuid
from collections.abc import Awaitable, Callable

from ..codex_auth import AuthLease, CodexAuthError, LOGIN_COMMAND, child_environment, codex_binary, studio_home, validate_home, cleanup_journal_temporaries
from .codex_policy import check_policy, command, controlled_catalogue, digest, settings
from .codex_qualification import CodexQualifier, _bounded_read
from .codex_wire import CodexConnection, CodexProtocolError


def role_registry(agent: Any) -> list[dict[str, Any]]:
    """Derive descriptions/schemas from the authoritative floor definitions."""
    from .base import session_tool_names
    from ..mcp_server import ProjectTools, TOOL_SCHEMAS
    return [{"type": "function", "name": name if name.startswith("floor_") else f"floor_{name}",
             "description": getattr(ProjectTools, name).__doc__ or name.replace("_", " "),
             "inputSchema": TOOL_SCHEMAS[name]}
            for name in session_tool_names(agent.skills, agent.runtime.tools)]


@dataclass(eq=False)
class CodexThread:
    reference: ServiceReference
    thread_id: str
    role: str
    generation: int
    registry: list[dict[str, Any]]
    path: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    used: bool = False
    identity: str = field(default_factory=lambda: uuid.uuid4().hex)
    events: asyncio.Queue[dict[str, Any]] = field(default_factory=asyncio.Queue)
    closing: bool = False
    _close_task: asyncio.Task[None] | None = None
    quiesce: Callable[[], Awaitable[None]] | None = None

    async def close(self) -> None:
        if self._close_task is None:
            self.closing = True
            self._close_task = asyncio.create_task(self.reference.service._close_thread(self))
        await asyncio.shield(self._close_task)


class ServiceReference:
    """Pending project open transfers this exact reference to its adapter."""
    def __init__(self, service: CodexService, session_id: str):
        self.service = service
        self.session_id = session_id
        self.identity = uuid.uuid4().hex
        self.threads: set[CodexThread] = set()
        self.closing = False
        self._close_task: asyncio.Task[None] | None = None

    async def open_thread(self, role: str, parameters: dict[str, Any], registry: list[dict[str, Any]]) -> CodexThread:
        if self.closing:
            raise CodexProtocolError("Studio Codex project is closing")
        task = asyncio.create_task(self.service._open_thread(self, role, parameters, registry))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            # Native thread creation may already have succeeded. Await its
            # correlation before cleanup rather than leaving an unowned thread.
            try:
                handle = await task
                await handle.close()
            finally:
                raise

    async def _close(self) -> None:
        errors = []
        for thread in tuple(self.threads):
            try:
                await thread.close()
            except Exception as error:
                errors.append(error)
        await self.service._release(self)
        if errors:
            raise errors[0]

    async def close(self) -> None:
        if self._close_task is None:
            self.closing = True
            self._close_task = asyncio.create_task(self._close())
        await asyncio.shield(self._close_task)


class CodexService:
    def __init__(self, *, home: Path | None = None):
        self._home = home
        self._operator_environment = dict(os.environ)
        self._lease: AuthLease | None = None
        self.qualifier = CodexQualifier()
        self.references: set[ServiceReference] = set()
        self.threads: dict[str, CodexThread] = {}
        self.connection: CodexConnection | None = None
        self.generation = 0
        self.invalidated = False
        self._lock = asyncio.Lock()
        self._private: tempfile.TemporaryDirectory[str] | None = None
        self._router: asyncio.Task[None] | None = None
        self._journal: set[str] = set()
        self.native_group: str | None = None
        self._close_task: asyncio.Task[None] | None = None
        self._qualified: dict[str, Any] = {}
        self._policy: dict[str, Any] = {}

    @property
    def home(self) -> Path:
        if self._home is None:
            self._home = studio_home(self._operator_environment)
        return self._home

    @property
    def lease(self) -> AuthLease:
        if self._lease is None:
            self._lease = AuthLease(self.home)
        return self._lease

    async def acquire(self, session_id: str, registries: list[list[dict[str, Any]]]) -> ServiceReference:
        async with self._lock:
            if self._close_task is not None:
                raise CodexProtocolError("Studio Codex hub is closing")
            self.lease.acquire()
            try:
                cleanup_journal_temporaries(self.home)
                # Even later borrowers qualify their own actual role schemas.
                qualified = await self.qualifier.qualify(registries)
                if self.connection is not None and qualified.get("contract") != self._qualified.get("contract"):
                    raise CodexProtocolError("Codex installation or policy changed while the shared service was active; close Codex projects before reopening")
                if self.connection is None:
                    self._qualified = qualified
                if self._close_task is not None:
                    raise CodexProtocolError("Studio Codex hub is closing")
                validate_home(self.home)
                if self.connection is None:
                    self.connection = await self._launch()
                    self.generation += 1
                    await self._clean_orphans()
                    self._router = asyncio.create_task(self._route(self.connection, self.generation))
                elif self.connection.dead.is_set():
                    raise CodexProtocolError("Studio Codex transport failed; close its projects before reopening")
                reference = ServiceReference(self, session_id)
                self.references.add(reference)
                return reference
            except BaseException:
                if not self.references:
                    await self._stop()
                raise

    async def _launch(self) -> CodexConnection:
        binary = Path(self._qualified["binary"])
        if await _bounded_read(digest, binary) != self._qualified["binary_digest"]:
            raise CodexProtocolError("Codex executable changed after qualification")
        catalog = await _bounded_read(controlled_catalogue, binary)
        self._private = tempfile.TemporaryDirectory(prefix="studio-codex-service-")
        private = Path(self._private.name)
        catalogue = private / "catalogue.json"
        catalogue.write_text(json.dumps(catalog))
        policy = settings(catalogue)
        self._policy = policy
        connection = await CodexConnection.start(command(binary, policy), cwd=str(private),
                                                env=child_environment(self.home, private), pass_fds=(self.lease.descriptor,))
        try:
            await check_policy(connection, policy)
            validate_home(self.home, require_auth=True)
            # Ask native auth to refresh against its authoritative store. Never
            # export tokens, emulate refresh or copy another login.
            try:
                account = await connection.rpc("account/read", {"refreshToken": True})
            except CodexProtocolError:
                raise CodexAuthError(f"Studio Codex authentication could not refresh. Run {LOGIN_COMMAND} after closing the hub") from None
            if not isinstance(account.get("account"), dict) or account["account"].get("type") != "chatgpt":
                raise CodexAuthError(f"Studio Codex ChatGPT authentication is unavailable. Run {LOGIN_COMMAND}")
            validate_home(self.home, require_auth=True)
        except BaseException:
            await connection.close()
            raise
        return connection

    def _write_journal(self) -> None:
        path = self.home / "studio-threads.json"
        descriptor, name = tempfile.mkstemp(prefix=".studio-threads-", dir=self.home)
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump(sorted(self._journal), stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            Path(name).unlink(missing_ok=True)

    async def _clean_orphans(self) -> None:
        path = self.home / "studio-threads.json"
        if path.exists():
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
                raise CodexProtocolError("Invalid Studio Codex thread registry")
            try:
                recorded = json.loads(path.read_bytes())
                if not isinstance(recorded, list) or any(not isinstance(item, str) or not item or len(item) > 128 for item in recorded):
                    raise ValueError
                self._journal = set(recorded)
            except (ValueError, TypeError):
                raise CodexProtocolError("Invalid Studio Codex thread registry") from None
        assert self.connection is not None
        marker = str(uuid.uuid5(uuid.NAMESPACE_URL, f"machinome-studio:{self.home.absolute()}"))
        metadata = {"owner": "machinome-studio", "marker": marker}
        group = (await self.connection.rpc("project/create", {"idempotencyKey": marker,
                    "name": "Studio ephemeral floor sessions", "roots": [], "metadata": metadata}))["project"]
        if (not isinstance(group.get("id"), str) or group.get("metadata") != metadata or group.get("roots") != []
                or group.get("name") != "Studio ephemeral floor sessions"):
            raise CodexProtocolError("Codex native owner group does not match Studio's cleanup authority")
        self.native_group = group["id"]
        # Native grouping is atomic with thread/start. It closes the crash gap
        # between native persistence and recording our local thread journal.
        owned: set[str] = set()
        for archived in (False, True):
            cursor = None
            seen: set[str] = set()
            while True:
                result = await self.connection.rpc("thread/list", {"projectId": self.native_group, "limit": 100,
                    "archived": archived, "cursor": cursor, "sourceKinds": ["vscode", "appServer", "cli"]})
                if not isinstance(result.get("data"), list):
                    raise CodexProtocolError("Invalid Codex native thread inventory")
                for thread in result["data"]:
                    if not isinstance(thread, dict) or thread.get("projectId") != self.native_group or not isinstance(thread.get("id"), str):
                        raise CodexProtocolError("Codex orphan inventory crossed Studio's owner group")
                    owned.add(thread["id"])
                cursor = result.get("nextCursor")
                if cursor is None:
                    break
                if not isinstance(cursor, str) or cursor in seen:
                    raise CodexProtocolError("Invalid Codex native thread pagination")
                seen.add(cursor)
        # Journal-only ids have no persisted record in the exact owner group;
        # never delete an unmarked native record by trusting a local id alone.
        self._journal = owned
        self._write_journal()
        for thread in tuple(owned):
            await self.connection.rpc("thread/delete", {"threadId": thread})
            self._journal.remove(thread)
            self._write_journal()

    async def _open_thread(self, reference: ServiceReference, role: str, parameters: dict[str, Any], registry: list[dict[str, Any]]) -> CodexThread:
        async with self._lock:
            if reference not in self.references or reference.closing or self.connection is None:
                raise CodexProtocolError("Studio Codex project is not live")
            await check_policy(self.connection, self._policy)
            result = await self.connection.rpc("thread/start", {
                **parameters, "projectId": self.native_group, "dynamicTools": registry, "environments": [], "sandbox": "read-only", "approvalPolicy": "never",
            })
            identity = result["thread"]["id"]
            if not isinstance(identity, str) or identity in self.threads:
                raise CodexProtocolError("Invalid Studio Codex thread identity")
            self._journal.add(identity)
            self._write_journal()
            handle = CodexThread(reference, identity, role, self.generation, json.loads(json.dumps(registry)),
                                 result["thread"].get("path") or "", json.loads(json.dumps(parameters)))
            self.threads[identity] = handle
            reference.threads.add(handle)
            return handle

    async def _close_thread(self, handle: CodexThread) -> None:
        async with self._lock:
            if self.threads.get(handle.thread_id) is not handle:
                return
            self.threads.pop(handle.thread_id)
            try:
                if self.connection is not None and not self.connection.dead.is_set():
                    await self.connection.rpc("thread/delete", {"threadId": handle.thread_id})
                    self._journal.discard(handle.thread_id)
                    self._write_journal()
            finally:
                # History cleanup can fail independently of stopped routing and
                # worker ownership. Preserve its exact orphan id for next start.
                handle.reference.threads.discard(handle)

    async def _route(self, connection: CodexConnection, generation: int) -> None:
        while True:
            incoming = asyncio.create_task(connection.notifications.get())
            dead = asyncio.create_task(connection.dead.wait())
            try:
                await asyncio.wait((incoming, dead), return_when=asyncio.FIRST_COMPLETED)
                if dead.done():
                    for handle in tuple(self.threads.values()):
                        if handle.generation == generation and not handle.closing:
                            await handle.events.put({"studioGeneration": generation, "method": "studio/transportFailed", "params": {"threadId": handle.thread_id}})
                    return
                frame = incoming.result()
                parameters = frame.get("params", {})
                if not isinstance(parameters, dict):
                    await connection.close()
                    for handle in tuple(self.threads.values()):
                        if handle.generation == generation and not handle.closing:
                            await handle.events.put({"studioGeneration": generation, "method": "studio/transportFailed", "params": {"threadId": handle.thread_id}})
                    return
                identity = parameters.get("threadId")
                if identity is None and isinstance(parameters.get("thread"), dict):
                    identity = parameters["thread"].get("id")
                handle = self.threads.get(identity) if isinstance(identity, str) else None
                if handle is not None and handle.generation == generation and not handle.closing and not handle.reference.closing:
                    await handle.events.put({**frame, "studioGeneration": generation})
                elif "id" in frame:
                    if frame.get("method") == "item/tool/call":
                        await connection.send({"id": frame["id"], "result": {"success": False, "contentItems": [{"type": "inputText", "text": "Rejected stale or unknown Studio tool owner"}]}})
                    else:
                        await connection.send({"id": frame["id"], "error": {"code": -32601, "message": "Studio denies undeclared server requests"}})
            finally:
                for task in (incoming, dead):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(incoming, dead, return_exceptions=True)

    async def _release(self, reference: ServiceReference) -> None:
        async with self._lock:
            self.references.discard(reference)
            if not self.references:
                await self._stop()

    def _verify_record(self, handle: CodexThread) -> None:
        path = Path(handle.path)
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise CodexProtocolError("Codex retained thread has no verifiable native record")
        resolved = path.resolve()
        if not resolved.is_relative_to(self.home / "sessions") or any(parent.is_symlink() for parent in path.parents if parent != self.home.parent):
            raise CodexProtocolError("Codex retained thread record is outside Studio storage")
        try:
            with path.open("rb") as stream:
                line = stream.readline(1024 * 1024 + 1)
            if len(line) > 1024 * 1024:
                raise ValueError
            frame = json.loads(line)
            payload = frame["payload"]
            expected = [{"type": "function", **tool} for tool in handle.registry]
            if frame["type"] != "session_meta" or payload["id"] != handle.thread_id or payload.get("dynamic_tools", []) != expected:
                raise ValueError
        except (OSError, ValueError, KeyError, TypeError):
            raise CodexProtocolError("Codex retained dynamic registry differs from its immutable role contract") from None

    async def recover(self) -> None:
        """One generation transition resumes all retained sibling conversations."""
        async with self._lock:
            if self.invalidated:
                raise CodexProtocolError("Codex isolation contract was invalidated; close its projects before retrying")
            if self.connection is not None and not self.connection.dead.is_set():
                return
            if not self.references:
                raise CodexProtocolError("Studio Codex service has no live owner")
            handles = tuple(handle for handle in self.threads.values() if not handle.closing and not handle.reference.closing)
            for handle in handles:
                if handle.used:
                    self._verify_record(handle)
            # Stop the dead generation while preserving lease and native records.
            if self.connection is not None:
                await self.connection.close()
            if self._router is not None:
                self._router.cancel()
                await asyncio.gather(self._router, return_exceptions=True)
                self._router = None
            # Every old-generation tool worker must be stopped, including a
            # sibling whose failure notification has not yet been consumed.
            await asyncio.gather(*(handle.quiesce() for handle in handles if handle.quiesce is not None))
            if self._private is not None:
                self._private.cleanup()
                self._private = None
            self.connection = None
            connection = await self._launch()
            try:
                for handle in handles:
                    if handle.used:
                        result = await connection.rpc("thread/resume", {"threadId": handle.thread_id, "sandbox": "read-only", "approvalPolicy": "never"})
                        if result["thread"]["id"] != handle.thread_id:
                            raise CodexProtocolError("Codex resumed an unexpected thread")
                    else:
                        result = await connection.rpc("thread/start", {**handle.parameters, "projectId": self.native_group,
                            "dynamicTools": handle.registry, "environments": [], "sandbox": "read-only", "approvalPolicy": "never"})
                        old = handle.thread_id
                        self.threads.pop(old)
                        self._journal.discard(old)
                        handle.thread_id = result["thread"]["id"]
                        handle.path = result["thread"].get("path") or ""
                        self.threads[handle.thread_id] = handle
                        self._journal.add(handle.thread_id)
                        self._write_journal()
            except BaseException:
                await connection.close()
                raise
            self.connection = connection
            self.generation += 1
            for handle in handles:
                # The old router is joined above. Remove queued events as well
                # as tagging frames: consumers may already hold an old frame
                # and must compare its generation after acquiring delivery locks.
                while not handle.events.empty():
                    handle.events.get_nowait()
                handle.generation = self.generation
            self._router = asyncio.create_task(self._route(connection, self.generation))

    async def invalidate(self) -> None:
        """Native authority leakage invalidates every borrower, not its peers."""
        self.invalidated = True
        connection = self.connection
        if connection is not None:
            await connection.close()
        handles = tuple(self.threads.values())
        await asyncio.gather(*(handle.quiesce() for handle in handles if handle.quiesce is not None))
        for handle in handles:
            if not handle.closing:
                await handle.events.put({"studioGeneration": handle.generation, "method": "studio/transportFailed",
                                         "params": {"threadId": handle.thread_id}})

    async def _stop(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
        if self._router is not None:
            self._router.cancel()
            await asyncio.gather(self._router, return_exceptions=True)
            self._router = None
        if self._private is not None:
            self._private.cleanup()
            self._private = None
        if self._lease is not None:
            self._lease.release()
        self.invalidated = False

    async def _close(self) -> None:
        errors = []
        for reference in tuple(self.references):
            try:
                await reference.close()
            except Exception as error:
                errors.append(error)
        try:
            async with self._lock:
                await self._stop()
        finally:
            if errors:
                raise errors[0]

    async def close(self) -> None:
        if self._close_task is None:
            self._close_task = asyncio.create_task(self._close())
        await asyncio.shield(self._close_task)
