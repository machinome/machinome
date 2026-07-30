"""Spike: what does `hermes acp` actually do with a mid-turn correction?

Design evidence only. Speaks raw ACP JSON-RPC to a `hermes acp` subprocess and
logs both directions. Deliberately does not import `floor.*` — the question is
about Hermes' behaviour, not about our adapter.

Scenarios
  S0  initialize handshake at protocolVersion 2, then 1 (no model call)
  S1  second session/prompt while a 60s tool call is in flight  <- decisive
  S2  session/cancel while a 60s tool call is in flight
  S3  reprompt after cancellation, to test session-context survival
  S4  teardown: stdin close -> SIGTERM -> SIGKILL, recording which one works

The agent is confined to a fresh temp cwd and prompted only to append
timestamps to probe.log. That side effect is the real instrument: a tool that
was truly aborted stops growing the file, one that was merely abandoned keeps
growing (an orphan).

Usage:  python acp_turn_control.py [--outdir DIR]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import signal
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

LONG_TOOL_PROMPT = (
    "Run exactly this shell command in the current directory and nothing else:\n"
    "  for i in $(seq 1 60); do date +%s.%N >> probe.log; sleep 1; done\n"
    "Run it in the foreground and wait for it to finish. "
    "Do not explain, summarise, or run any other command."
)

CORRECTION_PROMPT = (
    "STOP. Do not continue appending to probe.log. "
    "Immediately write the single word REDIRECTED into result.txt, then stop."
)

RECALL_PROMPT = (
    "In one short sentence: what were you doing immediately before this "
    "message, and did you finish it?"
)


class Probe:
    """Minimal ACP client that logs every frame in both directions."""

    def __init__(self, log_path: Path, cwd: Path) -> None:
        self.log_path = log_path
        self.cwd = cwd
        self.proc: asyncio.subprocess.Process | None = None
        self._next_id = 0
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._reader: asyncio.Task[None] | None = None
        self._stderr: asyncio.Task[None] | None = None
        self._t0 = time.monotonic()
        self._log = log_path.open("a", encoding="utf-8")
        # Every session/update notification, in arrival order.
        self.updates: list[dict[str, Any]] = []

    # ── logging ────────────────────────────────────────────────────────

    def record(self, direction: str, payload: Any, **extra: Any) -> None:
        entry = {
            "t": round(time.monotonic() - self._t0, 4),
            "dir": direction,
            "payload": payload,
            **extra,
        }
        self._log.write(json.dumps(entry, default=str) + "\n")
        self._log.flush()

    def note(self, message: str, **extra: Any) -> None:
        self.record("note", message, **extra)
        print(f"  [{time.monotonic() - self._t0:7.2f}s] {message}", flush=True)

    # ── lifecycle ──────────────────────────────────────────────────────

    async def start(self) -> None:
        self.proc = await asyncio.create_subprocess_exec(
            "hermes",
            "acp",
            "--accept-hooks",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
            env={**os.environ, "HERMES_ACP_SKIP_CONFIGURED_MCP": "1"},
            start_new_session=True,
        )
        self.note(f"spawned hermes acp pid={self.proc.pid} cwd={self.cwd}")
        self._reader = asyncio.create_task(self._read_stdout())
        self._stderr = asyncio.create_task(self._read_stderr())

    async def _read_stdout(self) -> None:
        assert self.proc is not None and self.proc.stdout is not None
        while line := await self.proc.stdout.readline():
            text = line.decode(errors="replace").strip()
            if not text:
                continue
            try:
                message = json.loads(text)
            except json.JSONDecodeError:
                self.record("in-raw", text)
                continue
            self.record("in", message)
            await self._dispatch(message)

    async def _read_stderr(self) -> None:
        assert self.proc is not None and self.proc.stderr is not None
        while line := await self.proc.stderr.readline():
            self.record("stderr", line.decode(errors="replace").rstrip())

    async def _dispatch(self, message: dict[str, Any]) -> None:
        request_id = message.get("id")
        method = message.get("method")

        # Response to something we sent.
        if request_id is not None and method is None:
            future = self._pending.pop(request_id, None)
            if future is not None and not future.done():
                future.set_result(message)
            return

        # Agent -> client request: must answer or the agent stalls.
        if request_id is not None and method is not None:
            await self._answer_agent_request(request_id, method, message)
            return

        # Notification.
        if method == "session/update":
            self.updates.append(message)

    async def _answer_agent_request(
        self, request_id: Any, method: str, message: dict[str, Any]
    ) -> None:
        params = message.get("params", {})
        if method == "session/request_permission":
            # Auto-allow so the shell tool can run unattended.
            options = params.get("options", []) or []
            chosen = next(
                (
                    option.get("optionId")
                    for option in options
                    if option.get("kind") in ("allow_once", "allow_always")
                ),
                options[0].get("optionId") if options else "allow",
            )
            self.note(f"auto-allowing permission request -> {chosen}")
            await self._respond(
                request_id,
                {"outcome": {"outcome": "selected", "optionId": chosen}},
            )
            return
        if method in ("fs/read_text_file", "fs/write_text_file"):
            # We declared no fs capability; answer defensively if asked anyway.
            await self._respond(request_id, {})
            return
        self.note(f"unhandled agent request {method!r}; replying method-not-found")
        await self._respond_error(request_id, -32601, f"unhandled: {method}")

    # ── sending ────────────────────────────────────────────────────────

    async def _write(self, payload: dict[str, Any]) -> None:
        assert self.proc is not None and self.proc.stdin is not None
        self.record("out", payload)
        self.proc.stdin.write((json.dumps(payload) + "\n").encode())
        await self.proc.stdin.drain()

    async def _respond(self, request_id: Any, result: dict[str, Any]) -> None:
        await self._write({"jsonrpc": "2.0", "id": request_id, "result": result})

    async def _respond_error(self, request_id: Any, code: int, msg: str) -> None:
        await self._write(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": code, "message": msg},
            }
        )

    def send_request_nowait(self, method: str, params: dict[str, Any]) -> tuple[int, asyncio.Task[dict[str, Any]]]:
        """Dispatch a request and return (id, task awaiting its response)."""
        self._next_id += 1
        request_id = self._next_id
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future

        async def send_and_wait() -> dict[str, Any]:
            await self._write(
                {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
            )
            return await future

        return request_id, asyncio.create_task(send_and_wait())

    async def request(
        self, method: str, params: dict[str, Any], timeout: float = 120
    ) -> dict[str, Any]:
        _, task = self.send_request_nowait(method, params)
        return await asyncio.wait_for(task, timeout=timeout)

    async def notify(self, method: str, params: dict[str, Any]) -> None:
        await self._write({"jsonrpc": "2.0", "method": method, "params": params})

    # ── teardown (this is S4) ──────────────────────────────────────────

    async def teardown(self) -> dict[str, Any]:
        """Close stdin, escalate to SIGTERM then SIGKILL, report what worked."""
        assert self.proc is not None
        result: dict[str, Any] = {}
        if self.proc.returncode is not None:
            result["ended_by"] = "already_exited"
            result["returncode"] = self.proc.returncode
            self.note(f"S4: process already exited rc={self.proc.returncode}")
            return result

        self.note("S4: closing stdin, waiting up to 5s")
        if self.proc.stdin is not None:
            self.proc.stdin.close()
        try:
            await asyncio.wait_for(self.proc.wait(), timeout=5)
            result["ended_by"] = "stdin_close"
        except asyncio.TimeoutError:
            self.note("S4: survived stdin close; sending SIGTERM, waiting up to 5s")
            self.proc.terminate()
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=5)
                result["ended_by"] = "sigterm"
            except asyncio.TimeoutError:
                self.note("S4: survived SIGTERM; sending SIGKILL")
                self.proc.kill()
                await asyncio.wait_for(self.proc.wait(), timeout=10)
                result["ended_by"] = "sigkill"
        result["returncode"] = self.proc.returncode
        self.note(f"S4: ended by {result['ended_by']} rc={result['returncode']}")

        for task in (self._reader, self._stderr):
            if task is not None:
                task.cancel()
        self._log.close()
        return result


# ── helpers ────────────────────────────────────────────────────────────


def probe_lines(cwd: Path) -> int:
    path = cwd / "probe.log"
    if not path.exists():
        return 0
    return len([ln for ln in path.read_text(errors="replace").splitlines() if ln.strip()])


async def wait_for_tool_running(probe: Probe, timeout: float = 60) -> bool:
    """Wait until probe.log shows the shell tool is actually executing."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if probe_lines(probe.cwd) >= 2:
            probe.note(f"tool confirmed running (probe.log has {probe_lines(probe.cwd)} lines)")
            return True
        await asyncio.sleep(0.5)
    probe.note("tool never started writing probe.log")
    return False


def agent_texts(probe: Probe) -> str:
    """Concatenate streamed agent text, tolerating list- or dict-shaped content."""
    parts: list[str] = []
    for message in probe.updates:
        update = message.get("params", {}).get("update", {})
        if not isinstance(update, dict):
            continue
        content = update.get("content")
        if isinstance(content, dict) and isinstance(content.get("text"), str):
            parts.append(content["text"])
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "".join(parts)


def stop_reasons(probe: Probe) -> list[str]:
    """Every stopReason seen in notifications, wherever ACP put it."""
    found = []
    for message in probe.updates:
        update = message.get("params", {}).get("update", {})
        if "stopReason" in update:
            found.append(update["stopReason"])
        if update.get("sessionUpdate") in ("state_update", "idle"):
            found.append(f"state={update.get('state')}/{update.get('stopReason')}")
    return found


# ── scenarios ──────────────────────────────────────────────────────────


async def s0_handshake(outdir: Path) -> dict[str, Any]:
    """Which protocol version does hermes 0.19.0 negotiate? No model call."""
    print("\n=== S0: initialize handshake ===", flush=True)
    results: dict[str, Any] = {}
    for version in (2, 1):
        cwd = Path(tempfile.mkdtemp(prefix=f"acp-s0-v{version}-"))
        probe = Probe(outdir / f"s0-v{version}.jsonl", cwd)
        try:
            await probe.start()
            response = await probe.request(
                "initialize",
                {
                    "protocolVersion": version,
                    "clientCapabilities": {},
                    "clientInfo": {
                        "name": "acp-turn-control-spike",
                        "version": "0.1.0",
                    },
                },
                timeout=60,
            )
            results[f"v{version}"] = response
            probe.note(f"initialize(protocolVersion={version}) -> {json.dumps(response)[:400]}")
        except Exception as error:  # noqa: BLE001 - spike: record and continue
            results[f"v{version}"] = {"spike_error": repr(error)}
            probe.note(f"initialize(protocolVersion={version}) FAILED: {error!r}")
        finally:
            results[f"v{version}_teardown"] = await probe.teardown()
            shutil.rmtree(cwd, ignore_errors=True)
    return results


async def open_session(probe: Probe, version: int) -> str:
    await probe.request(
        "initialize",
        {
            "protocolVersion": version,
            "clientCapabilities": {},
            "clientInfo": {"name": "acp-turn-control-spike", "version": "0.1.0"},
        },
        timeout=60,
    )
    result = await probe.request(
        "session/new", {"cwd": str(probe.cwd), "mcpServers": []}, timeout=120
    )
    session_id = str(result.get("result", {}).get("sessionId") or result.get("sessionId"))
    probe.note(f"session opened: {session_id}")
    return session_id


async def s1_concurrent_prompt(outdir: Path, version: int) -> dict[str, Any]:
    """THE decisive scenario: second prompt while a tool call is in flight."""
    print("\n=== S1: second session/prompt during an active turn ===", flush=True)
    cwd = Path(tempfile.mkdtemp(prefix="acp-s1-"))
    probe = Probe(outdir / "s1.jsonl", cwd)
    findings: dict[str, Any] = {"cwd": str(cwd)}
    try:
        await probe.start()
        session_id = await open_session(probe, version)

        first_id, first_task = probe.send_request_nowait(
            "session/prompt",
            {"sessionId": session_id, "prompt": [{"type": "text", "text": LONG_TOOL_PROMPT}]},
        )
        findings["first_prompt_id"] = first_id
        probe.note(f"sent long-turn prompt id={first_id}")

        if not await wait_for_tool_running(probe):
            findings["outcome"] = "tool_never_started"
            return findings

        lines_at_send = probe_lines(cwd)
        findings["probe_lines_when_correction_sent"] = lines_at_send
        probe.note(f"sending CORRECTION while tool runs (probe.log={lines_at_send} lines)")

        send_time = time.monotonic()
        second_id, second_task = probe.send_request_nowait(
            "session/prompt",
            {"sessionId": session_id, "prompt": [{"type": "text", "text": CORRECTION_PROMPT}]},
        )
        findings["second_prompt_id"] = second_id

        # Which response lands first, and how fast?
        done, pending = await asyncio.wait(
            {first_task, second_task},
            timeout=150,
            return_when=asyncio.FIRST_COMPLETED,
        )
        findings["second_prompt_latency_s"] = None
        if second_task in done:
            findings["second_prompt_latency_s"] = round(time.monotonic() - send_time, 2)
            findings["second_response"] = second_task.result()
            findings["which_returned_first"] = "second(correction)"
        elif first_task in done:
            findings["first_response"] = first_task.result()
            findings["which_returned_first"] = "first(long turn)"

        # Let the rest settle.
        remaining = [t for t in (first_task, second_task) if not t.done()]
        if remaining:
            settled, still_pending = await asyncio.wait(remaining, timeout=150)
            for task in settled:
                key = "first_response" if task is first_task else "second_response"
                try:
                    findings[key] = task.result()
                except Exception as error:  # noqa: BLE001
                    findings[key] = {"spike_error": repr(error)}
            for task in still_pending:
                task.cancel()
                findings["still_pending"] = (
                    "first" if task is first_task else "second"
                )

        await asyncio.sleep(3)
        findings["probe_lines_final"] = probe_lines(cwd)
        findings["probe_lines_added_after_correction"] = (
            findings["probe_lines_final"] - lines_at_send
        )
        findings["result_txt"] = (
            (cwd / "result.txt").read_text(errors="replace").strip()
            if (cwd / "result.txt").exists()
            else None
        )
        findings["stop_reasons"] = stop_reasons(probe)
        findings["update_kinds"] = sorted(
            {
                m.get("params", {}).get("update", {}).get("sessionUpdate", "?")
                for m in probe.updates
            }
        )
        probe.note(f"S1 findings: {json.dumps({k: v for k, v in findings.items() if k not in ('first_response','second_response')}, default=str)}")
        return findings
    finally:
        findings["teardown"] = await probe.teardown()
        findings["cwd_kept"] = str(cwd)


async def s2_cancel(outdir: Path, version: int) -> dict[str, Any]:
    """Does session/cancel actually abort the running tool, or orphan it?"""
    print("\n=== S2: session/cancel during an active turn ===", flush=True)
    cwd = Path(tempfile.mkdtemp(prefix="acp-s2-"))
    probe = Probe(outdir / "s2.jsonl", cwd)
    findings: dict[str, Any] = {"cwd": str(cwd)}
    try:
        await probe.start()
        session_id = await open_session(probe, version)

        first_id, first_task = probe.send_request_nowait(
            "session/prompt",
            {"sessionId": session_id, "prompt": [{"type": "text", "text": LONG_TOOL_PROMPT}]},
        )
        if not await wait_for_tool_running(probe):
            findings["outcome"] = "tool_never_started"
            return findings

        lines_at_cancel = probe_lines(cwd)
        findings["probe_lines_at_cancel"] = lines_at_cancel
        probe.note(f"sending session/cancel (probe.log={lines_at_cancel} lines)")
        cancel_time = time.monotonic()
        await probe.notify("session/cancel", {"sessionId": session_id})

        try:
            findings["first_response"] = await asyncio.wait_for(first_task, timeout=60)
            findings["cancel_to_response_s"] = round(time.monotonic() - cancel_time, 2)
        except asyncio.TimeoutError:
            findings["first_response"] = "TIMEOUT: no response within 60s of cancel"
            first_task.cancel()

        # The orphan test: does the shell keep writing after cancellation?
        probe.note("polling probe.log for 10s to detect an orphaned tool process")
        await asyncio.sleep(10)
        findings["probe_lines_10s_after_cancel"] = probe_lines(cwd)
        findings["lines_added_after_cancel"] = (
            findings["probe_lines_10s_after_cancel"] - lines_at_cancel
        )
        findings["tool_orphaned"] = findings["lines_added_after_cancel"] > 2
        findings["stop_reasons"] = stop_reasons(probe)
        probe.note(
            f"S2: {findings['lines_added_after_cancel']} lines added after cancel; "
            f"orphaned={findings['tool_orphaned']}; stop_reasons={findings['stop_reasons']}"
        )

        # S3 rides on this session.
        print("\n=== S3: reprompt after cancellation ===", flush=True)
        try:
            recall = await probe.request(
                "session/prompt",
                {"sessionId": session_id, "prompt": [{"type": "text", "text": RECALL_PROMPT}]},
                timeout=120,
            )
            findings["s3_reprompt_accepted"] = True
            findings["s3_response"] = recall
            findings["s3_agent_text"] = agent_texts(probe)[-600:]
            probe.note(f"S3 agent recall: {findings['s3_agent_text'][-300:]!r}")
        except Exception as error:  # noqa: BLE001
            findings["s3_reprompt_accepted"] = False
            findings["s3_error"] = repr(error)
            probe.note(f"S3 reprompt FAILED: {error!r}")
        return findings
    finally:
        findings["teardown"] = await probe.teardown()
        findings["cwd_kept"] = str(cwd)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).parent / "evidence")
    parser.add_argument(
        "--only",
        choices=("s0", "s1", "s2"),
        action="append",
        help="run only these scenarios (default: all)",
    )
    parser.add_argument(
        "--version",
        type=int,
        default=None,
        help="protocolVersion to advertise (default: whatever the agent declares in S0)",
    )
    arguments = parser.parse_args()
    outdir = arguments.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    only = set(arguments.only or ("s0", "s1", "s2"))

    summary: dict[str, Any] = {"hermes": shutil.which("hermes")}
    version = arguments.version
    if "s0" in only or version is None:
        summary["s0"] = await s0_handshake(outdir)
        # Use the version the AGENT declares, not the one we asked for: hermes
        # 0.19.0 accepts an advertisement of 2 and answers 1.
        if version is None:
            declared = {
                key: value.get("result", {}).get("protocolVersion")
                for key, value in summary["s0"].items()
                if isinstance(value, dict) and "result" in value
            }
            summary["agent_declared_versions"] = declared
            version = max((v for v in declared.values() if isinstance(v, int)), default=1)
    summary["version_used"] = version
    print(f"\n--> running behavioural scenarios at protocolVersion={version}", flush=True)

    if "s1" in only:
        try:
            summary["s1"] = await asyncio.wait_for(s1_concurrent_prompt(outdir, version), timeout=420)
        except Exception as error:  # noqa: BLE001
            summary["s1"] = {"spike_error": repr(error)}
    if "s2" in only:
        try:
            summary["s2_s3"] = await asyncio.wait_for(s2_cancel(outdir, version), timeout=420)
        except Exception as error:  # noqa: BLE001
            summary["s2_s3"] = {"spike_error": repr(error)}

    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nwrote {outdir / 'summary.json'}", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
