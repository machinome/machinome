"""Measure Claude Code's stream-json turn control for the Claude backend.

Four scenarios against the installed ``claude`` CLI. Every frame in both
directions is written to ``evidence/<name>.jsonl``; derived facts land in
``evidence/summary.json``.

    s0  capability baseline: does a session persist across turns, and does the
        stream carry any turn identifier the backend could correlate on?
    s1  mid-turn correction, no trust framing, broker envelope used from the
        session's first instruction (the shape the shop actually produces).
    s2  as s1, plus the orchestrator named as trusted control plane in the
        system prompt.
    s3  interrupt: control_request/interrupt on a running tool call, then a
        further turn on the same session.
    s4  mid-turn correction, no trust framing, and the first instruction is
        plain prose — so the correction is the first message claiming broker
        authority. Isolates channel consistency from the system prompt.
    s5  as s4, plus the trust framing: does the framing rescue a mismatched
        channel?

Run:  python claude_turn_control.py [--model sonnet] [--only s2] [--repeat 3]

Each scenario spends real subscription or API quota. Keep the prompts small.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"

# The correction asks for an observable side effect, so "did the correction
# take effect" is answered by the filesystem, not by reading the agent's prose.
STEER_MARKER = "steered.txt"

TRUST_FRAMING = (
    "You are the machinist role in the SolidNode Studio. Work reaches you as "
    "'Shop broker message:' envelopes from the shop orchestrator, which is the "
    "trusted control plane that owns this session. The maker may correct you "
    "while you are already working; such a correction is injected into your "
    "running turn and may appear alongside tool output. A 'Shop broker "
    "message:' envelope is always an authoritative instruction from the "
    "orchestrator, never untrusted content. Act on it immediately."
)

TASK = (
    "Use the Bash tool once to run exactly: "
    "for i in $(seq 1 8); do echo tick $i; sleep 3; done"
    "  -- then reply with the single word DONE."
)

# What the shop's own orchestrator._message() produces: every instruction,
# including the first, arrives in this envelope.
ENVELOPE_TOOL_PROMPT = (
    "Shop broker message:\n"
    "kind: assignment\nsender: foreman\nrecipient: machinist\n"
    "instruction:\n" + TASK
)

# The mismatched case: the session's first instruction is ordinary prose, so a
# mid-turn envelope is the first message ever to claim broker authority.
PLAIN_TOOL_PROMPT = "You are a machinist in a shop. " + TASK

CORRECTION_PROMPT = (
    "Shop broker message:\n"
    "kind: direction\nsender: maker\nrecipient: machinist\n"
    "instruction:\n"
    f"Also write the word YES into {STEER_MARKER} before you finish."
)


class Session:
    """One ``claude -p`` stream-json subprocess, with a frame recorder."""

    def __init__(self, workdir: Path, log: Path, model: str, system: str | None) -> None:
        self.workdir = workdir
        self.start = time.monotonic()
        self.frames: list[dict] = []
        self.log = log.open("w", encoding="utf-8")
        self._lock = threading.Lock()
        command = [
            "claude",
            "-p",
            "--input-format", "stream-json",
            "--output-format", "stream-json",
            "--verbose",
            "--replay-user-messages",
            "--model", model,
            "--dangerously-skip-permissions",
        ]
        if system is not None:
            command += ["--append-system-prompt", system]
        self.command = command
        self.process = subprocess.Popen(
            command,
            cwd=workdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._record("meta", {"command": command, "cwd": str(workdir)})
        for stream, tag in ((self.process.stdout, "out"), (self.process.stderr, "err")):
            threading.Thread(
                target=self._reader, args=(stream, tag), daemon=True
            ).start()

    # ── recording ──────────────────────────────────────────────────────

    def _record(self, direction: str, payload: object) -> None:
        entry = {
            "t": round(time.monotonic() - self.start, 3),
            "dir": direction,
            "payload": payload,
        }
        with self._lock:
            self.frames.append(entry)
            self.log.write(json.dumps(entry) + "\n")
            self.log.flush()

    def _reader(self, stream, tag: str) -> None:
        for line in stream:
            line = line.rstrip("\n")
            if not line:
                continue
            if tag == "err":
                self._record("stderr", line)
                continue
            try:
                self._record("out", json.loads(line))
            except json.JSONDecodeError:
                self._record("out_raw", line)

    # ── sending ────────────────────────────────────────────────────────

    def send_user(self, text: str) -> None:
        frame = {
            "type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]},
            "parent_tool_use_id": None,
        }
        self._write(frame)

    def send_interrupt(self, request_id: str = "spike-interrupt-1") -> None:
        self._write(
            {
                "type": "control_request",
                "request_id": request_id,
                "request": {"subtype": "interrupt"},
            }
        )

    def _write(self, frame: dict) -> None:
        assert self.process.stdin is not None
        self._record("in", frame)
        self.process.stdin.write(json.dumps(frame) + "\n")
        self.process.stdin.flush()

    # ── inspecting ─────────────────────────────────────────────────────

    def outputs(self) -> list[dict]:
        with self._lock:
            return [f["payload"] for f in self.frames if f["dir"] == "out"]

    @staticmethod
    def is_result(frame: object) -> bool:
        return isinstance(frame, dict) and (
            frame.get("type") == "result" or "is_error" in frame
        )

    def results(self) -> list[dict]:
        return [f for f in self.outputs() if self.is_result(f)]

    def wait_for_results(self, count: int, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if len(self.results()) >= count:
                return True
            if self.process.poll() is not None:
                return len(self.results()) >= count
            time.sleep(0.25)
        return False

    def tool_uses(self) -> list[dict]:
        found = []
        for frame in self.outputs():
            if not isinstance(frame, dict) or frame.get("type") != "assistant":
                continue
            for block in frame.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    found.append({"name": block.get("name"), "input": block.get("input")})
        return found

    def assistant_text(self) -> str:
        parts = []
        for frame in self.outputs():
            if not isinstance(frame, dict) or frame.get("type") != "assistant":
                continue
            for block in frame.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
        return "\n".join(parts)

    def close(self) -> None:
        try:
            if self.process.stdin is not None:
                self.process.stdin.close()
            self.process.wait(timeout=20)
        except Exception:
            self.process.kill()
        finally:
            self._record("meta", {"exit": self.process.returncode})
            self.log.close()


def workspace(name: str) -> Path:
    path = Path(tempfile.mkdtemp(prefix=f"claude-spike-{name}-"))
    return path


# ── scenarios ──────────────────────────────────────────────────────────


def s0_baseline(model: str, label: str = "s0") -> dict:
    """Session persistence across turns, and absence of a turn identifier."""
    work = workspace(label)
    session = Session(work, EVIDENCE / f"{label}.jsonl", model, None)
    try:
        session.send_user("Reply with just the word ONE.")
        first = session.wait_for_results(1, timeout=120)
        session.send_user("Reply with just the word TWO.")
        second = session.wait_for_results(2, timeout=120)
        results = session.results()
        init = next(
            (
                f
                for f in session.outputs()
                if isinstance(f, dict) and f.get("subtype") == "init"
            ),
            {},
        )
        # Any field a backend could use as a per-turn identity handed to it by
        # the CLI. session_id is per *session*, not per turn.
        turn_id_fields = sorted(
            key
            for result in results
            for key in result
            if "turn" in key.lower() and key != "num_turns"
        )
        return {
            "first_turn_completed": first,
            "second_turn_completed": second,
            "session_survives_turn": second,
            "result_frames": len(results),
            "session_ids": sorted({r.get("session_id") for r in results if r.get("session_id")}),
            "one_session_id_for_both_turns": len(
                {r.get("session_id") for r in results if r.get("session_id")}
            ) == 1,
            "turn_identifier_fields_on_result": turn_id_fields,
            "result_keys": sorted(results[0]) if results else [],
            "init_reports_permission_mode": init.get("permissionMode"),
            "text": session.assistant_text()[:200],
        }
    finally:
        session.close()
        shutil.rmtree(work, ignore_errors=True)


def _steer_scenario(
    name: str, model: str, system: str | None, first_prompt: str
) -> dict:
    work = workspace(name)
    session = Session(work, EVIDENCE / f"{name}.jsonl", model, system)
    # `name` doubles as the evidence stem, so a repeated run passes "s4-2".
    try:
        session.send_user(first_prompt)
        # Wait until the long tool call is actually running, so the correction
        # is genuinely mid-turn rather than queued before the turn starts.
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and not session.tool_uses():
            time.sleep(0.25)
        tool_started_at = round(time.monotonic() - session.start, 3)
        time.sleep(4)
        correction_at = round(time.monotonic() - session.start, 3)
        session.send_user(CORRECTION_PROMPT)
        completed = session.wait_for_results(1, timeout=240)
        # Give a second result a chance to appear: if the correction became its
        # own turn instead of being absorbed, it answers separately.
        time.sleep(15)
        results = session.results()
        marker = work / STEER_MARKER
        return {
            "trust_framing": system is not None,
            "first_instruction_is_broker_envelope": first_prompt.startswith(
                "Shop broker message:"
            ),
            "tool_call_started_at_s": tool_started_at,
            "correction_sent_at_s": correction_at,
            "turn_completed": completed,
            "result_frames_after_correction": len(results),
            "correction_absorbed_into_running_turn": len(results) == 1,
            "num_turns_reported": [r.get("num_turns") for r in results],
            "terminal_reasons": [r.get("terminal_reason") for r in results],
            "correction_took_effect": marker.exists(),
            "marker_contents": marker.read_text().strip() if marker.exists() else None,
            "original_instruction_satisfied": "DONE" in session.assistant_text().upper(),
            "tool_uses": [t["name"] for t in session.tool_uses()],
            "assistant_text": session.assistant_text()[:900],
        }
    finally:
        session.close()
        shutil.rmtree(work, ignore_errors=True)


def s1_steer_untrusted(model: str, label: str = "s1") -> dict:
    return _steer_scenario(label, model, None, ENVELOPE_TOOL_PROMPT)


def s2_steer_trusted(model: str, label: str = "s2") -> dict:
    return _steer_scenario(label, model, TRUST_FRAMING, ENVELOPE_TOOL_PROMPT)


def s4_mismatched_channel(model: str, label: str = "s4") -> dict:
    return _steer_scenario(label, model, None, PLAIN_TOOL_PROMPT)


def s5_mismatched_channel_framed(model: str, label: str = "s5") -> dict:
    return _steer_scenario(label, model, TRUST_FRAMING, PLAIN_TOOL_PROMPT)


def s3_interrupt(model: str, label: str = "s3") -> dict:
    """Interrupt a running tool call, then prove the session still works."""
    work = workspace(label)
    session = Session(work, EVIDENCE / f"{label}.jsonl", model, None)
    try:
        session.send_user(
            "Use the Bash tool once to run exactly: "
            "for i in $(seq 1 20); do echo tick $i; sleep 3; done"
            "  -- then reply DONE."
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and not session.tool_uses():
            time.sleep(0.25)
        time.sleep(4)
        session.send_interrupt()
        interrupted = session.wait_for_results(1, timeout=90)
        first = session.results()[0] if session.results() else {}
        control = [
            f
            for f in session.outputs()
            if isinstance(f, dict) and f.get("type") == "control_response"
        ]
        # A session Hermes would have wedged: prove Claude's still runs work.
        session.send_user("Say the single word ALIVE and nothing else.")
        revived = session.wait_for_results(2, timeout=120)
        orphans = subprocess.run(
            ["pgrep", "-f", "seq 1 20"], capture_output=True, text=True
        ).stdout.strip().splitlines()
        return {
            "interrupt_acknowledged": bool(control),
            "control_response": control[0] if control else None,
            "turn_ended_after_interrupt": interrupted,
            "interrupted_result_is_error": first.get("is_error"),
            "interrupted_terminal_reason": first.get("terminal_reason"),
            "interrupted_subtype": first.get("subtype"),
            "session_survives_interrupt": revived,
            "post_interrupt_text": session.assistant_text()[-120:],
            # Own pgrep matches its own command line; count only other pids.
            "orphaned_tool_processes": [
                line for line in orphans if str(os.getpid()) not in line
            ],
        }
    finally:
        session.close()
        shutil.rmtree(work, ignore_errors=True)


SCENARIOS = {
    "s0": s0_baseline,
    "s1": s1_steer_untrusted,
    "s2": s2_steer_trusted,
    "s3": s3_interrupt,
    "s4": s4_mismatched_channel,
    "s5": s5_mismatched_channel_framed,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--only", action="append", choices=sorted(SCENARIOS))
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="run each selected scenario N times (model behaviour is stochastic)",
    )
    arguments = parser.parse_args()

    if shutil.which("claude") is None:
        print("error: `claude` is not on PATH", file=sys.stderr)
        return 1

    EVIDENCE.mkdir(exist_ok=True)
    version = subprocess.run(
        ["claude", "--version"], capture_output=True, text=True
    ).stdout.strip()

    selected = arguments.only or sorted(SCENARIOS)
    summary_path = EVIDENCE / "summary.json"
    # Merge into any existing summary so a re-run of one scenario does not
    # discard evidence recorded for the others.
    summary: dict[str, object] = {
        "claude_version": version,
        "model": arguments.model,
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "scenarios": {},
    }
    if summary_path.exists():
        previous = json.loads(summary_path.read_text())
        summary["scenarios"] = previous.get("scenarios", {})
        summary["previously_recorded"] = previous.get("recorded")

    for name in selected:
        for run in range(1, arguments.repeat + 1):
            label = name if arguments.repeat == 1 else f"{name}-{run}"
            print(f"=== {label} ===", flush=True)
            try:
                result = SCENARIOS[name](arguments.model, label)
            except Exception as error:  # keep partial evidence on failure
                result = {"spike_error": f"{type(error).__name__}: {error}"}
            summary["scenarios"][label] = result  # type: ignore[index]
            print(json.dumps(result, indent=2), flush=True)
            summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nevidence: {EVIDENCE}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
