# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owned stdio JSON-RPC transport. Native frames never become diagnostics."""
from __future__ import annotations
import asyncio
import json
import os
import signal
from collections.abc import Awaitable, Callable
from typing import Any


class CodexProtocolError(RuntimeError):
    pass


async def stop_process(process: asyncio.subprocess.Process) -> None:
    """Reap the process and stop its process group, including surviving children."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        await asyncio.wait_for(process.wait(), 0.5)
    except TimeoutError:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await process.wait()


class CodexConnection:
    def __init__(self, process: asyncio.subprocess.Process):
        self.process = process
        self.pending: dict[int, asyncio.Future[Any]] = {}
        self.sequence = 0
        self.notifications: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.reader = asyncio.create_task(self._read())
        self._closing: asyncio.Task[None] | None = None
        self.dead = asyncio.Event()

    @classmethod
    async def start(cls, command: list[str], *, cwd: str, env: dict[str, str], pass_fds: tuple[int, ...] = ()) -> CodexConnection:
        process = await asyncio.create_subprocess_exec(
            *command, cwd=cwd, env=env, pass_fds=pass_fds, start_new_session=True,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL, limit=8 * 1024 * 1024,
        )
        connection = cls(process)
        try:
            await connection.rpc("initialize", {"clientInfo": {"name": "machinome_studio", "version": "0.1.0"},
                                                "capabilities": {"experimentalApi": True}})
            await connection.send({"method": "initialized"})
        except BaseException:
            await connection.close()
            raise
        return connection

    async def send(self, frame: dict[str, Any]) -> None:
        if self.process.stdin is None or self.dead.is_set():
            raise CodexProtocolError("Studio Codex transport is unavailable")
        self.process.stdin.write(json.dumps(frame, separators=(",", ":")).encode() + b"\n")
        await self.process.stdin.drain()

    async def rpc(self, method: str, params: dict[str, Any], *, timeout: float = 10) -> Any:
        self.sequence += 1
        identity = self.sequence
        future = asyncio.get_running_loop().create_future()
        self.pending[identity] = future
        try:
            await self.send({"id": identity, "method": method, "params": params})
            return await asyncio.wait_for(future, timeout)
        finally:
            self.pending.pop(identity, None)

    async def _read(self) -> None:
        try:
            assert self.process.stdout is not None
            while line := await self.process.stdout.readline():
                frame = json.loads(line)
                if not isinstance(frame, dict):
                    raise CodexProtocolError("Invalid Studio Codex protocol frame")
                if "method" in frame:
                    await self.notifications.put(frame)
                else:
                    identity = frame.get("id")
                    future = self.pending.get(identity) if type(identity) is int else None
                    if future is not None and not future.done():
                        if "error" in frame:
                            # Never include vendor request/response text; it may
                            # contain credentials, URLs or private tool content.
                            future.set_exception(CodexProtocolError("Studio Codex rejected an operation; check runtime policy and dedicated login"))
                        elif "result" in frame:
                            future.set_result(frame["result"])
                        else:
                            future.set_exception(CodexProtocolError("Invalid Studio Codex response"))
        except (ValueError, OSError, RuntimeError):
            pass
        finally:
            self.dead.set()
            for future in self.pending.values():
                if not future.done():
                    future.set_exception(CodexProtocolError("Studio Codex transport ended"))

    async def _close(self) -> None:
        await stop_process(self.process)
        await self.reader

    async def close(self) -> None:
        if self._closing is None:
            self._closing = asyncio.create_task(self._close())
        await asyncio.shield(self._closing)
