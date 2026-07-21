from __future__ import annotations

import unittest
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from floor.app import Broker
from floor.orchestrator import CodexAppServer, InactiveTurn, LocalBrokerControl, ShopOrchestrator


ROOT = Path(__file__).resolve().parents[1]
FAKE_APP_SERVER = ROOT / "tests" / "fixtures" / "fake_codex_app_server.py"


class FakeBroker:
    def __init__(self) -> None:
        self.manifested: list[tuple[str, str]] = []
        self.delivered: list[int] = []
        self.conversation: list[tuple[str, str]] = []

    async def manifest(self, role: str, label: str) -> None:
        self.manifested.append((role, label))

    async def mark_delivered(self, sequence: int) -> None:
        self.delivered.append(sequence)

    async def record_conversation(self, author: str, text: str) -> None:
        self.conversation.append((author, text))


class FakeCodex:
    def __init__(self) -> None:
        self.started_threads: list[str] = []
        self.started_turns: list[tuple[str, str]] = []
        self.steered_turns: list[tuple[str, str, str]] = []
        self.interrupted: list[tuple[str, str]] = []
        self.closed: list[str] = []
        self.fail_next_steer = False

    async def start_thread(self, role: str) -> str:
        self.started_threads.append(role)
        return f"thread-{role}"

    async def start_turn(self, thread_id: str, message: str) -> str:
        self.started_turns.append((thread_id, message))
        return f"turn-{len(self.started_turns)}"

    async def steer_turn(self, thread_id: str, turn_id: str, message: str) -> None:
        if self.fail_next_steer:
            self.fail_next_steer = False
            raise InactiveTurn
        self.steered_turns.append((thread_id, turn_id, message))

    async def interrupt_turn(self, thread_id: str, turn_id: str) -> None:
        self.interrupted.append((thread_id, turn_id))

    async def close_thread(self, thread_id: str) -> None:
        self.closed.append(thread_id)

    async def close(self) -> None:
        pass


class ShopOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.codex = FakeCodex()
        self.broker = FakeBroker()
        self.orchestrator = ShopOrchestrator(self.codex, self.broker)
        await self.orchestrator.open()

    async def test_open_owns_exactly_the_three_role_threads(self) -> None:
        self.assertEqual(self.codex.started_threads, ["foreman", "designer", "machinist"])
        self.assertEqual([role for role, _ in self.broker.manifested], self.codex.started_threads)

    async def test_idle_delivery_starts_and_active_delivery_steers_the_same_owner(self) -> None:
        await self.orchestrator.deliver({"sequence": 10, "recipient": "designer", "body": "First"})
        runtime = self.orchestrator.roles["designer"]
        self.assertIn("instruction:\nFirst", self.codex.started_turns[0][1])
        self.assertEqual(runtime.active_turn_id, "turn-1")

        await self.orchestrator.deliver({"sequence": 11, "recipient": "designer", "body": "Second"})
        self.assertEqual(self.codex.steered_turns[0][0:2], ("thread-designer", "turn-1"))
        self.assertIn("instruction:\nSecond", self.codex.steered_turns[0][2])
        self.assertEqual(self.broker.delivered, [10, 11])

    async def test_completion_race_restarts_the_still_unacknowledged_envelope(self) -> None:
        await self.orchestrator.deliver({"sequence": 12, "recipient": "machinist", "body": "Build"})
        self.codex.fail_next_steer = True
        await self.orchestrator.deliver({"sequence": 13, "recipient": "machinist", "body": "Correction"})
        self.assertEqual(self.codex.started_turns[-1][0], "thread-machinist")
        self.assertIn("instruction:\nCorrection", self.codex.started_turns[-1][1])
        self.assertEqual(self.broker.delivered[-1], 13)

    async def test_standby_does_not_start_or_steer_a_turn_and_close_interrupts_active_work(self) -> None:
        self.assertEqual(self.codex.started_turns, [])
        self.assertEqual(self.codex.steered_turns, [])
        await self.orchestrator.deliver({"sequence": 14, "recipient": "foreman", "body": "Work"})
        await self.orchestrator.close()
        self.assertEqual(self.codex.interrupted, [("thread-foreman", "turn-1")])
        self.assertEqual(self.codex.closed, ["thread-machinist", "thread-designer", "thread-foreman"])

    async def test_completed_foreman_message_is_published_to_the_maker_conversation(self) -> None:
        await self.orchestrator.handle_notification(
            {
                "method": "item/completed",
                "params": {
                    "threadId": "thread-foreman",
                    "turnId": "turn-1",
                    "completedAtMs": 1,
                    "item": {"id": "item-1", "type": "agentMessage", "text": "Hello from Foreman."},
                },
            }
        )
        await self.orchestrator.handle_notification(
            {
                "method": "item/completed",
                "params": {
                    "threadId": "thread-designer",
                    "turnId": "turn-2",
                    "completedAtMs": 2,
                    "item": {"id": "item-2", "type": "agentMessage", "text": "Internal specialist output."},
                },
            }
        )

        self.assertEqual(self.broker.conversation, [("foreman", "Hello from Foreman.")])


class CodexOwnershipAcceptanceTest(unittest.IsolatedAsyncioTestCase):
    async def test_role_threads_work_in_the_active_project_with_explicit_shop_context(self) -> None:
        project = ROOT / "projects" / "snowman"
        codex = CodexAppServer(ROOT, project=project, command=(sys.executable, str(FAKE_APP_SERVER)))
        await codex.start()
        self.addAsyncCleanup(codex.close)

        await codex.start_thread("foreman")
        notification = await codex.notifications.get()
        thread = notification["params"]["thread"]

        self.assertEqual(thread["cwd"], str(project.resolve()))
        self.assertEqual(thread["sandbox"], "danger-full-access")
        self.assertIn(f"Shop checkout: {ROOT.resolve()}", thread["developerInstructions"])
        self.assertIn(f"Active project: {project.resolve()}", thread["developerInstructions"])

    async def test_closing_never_used_role_threads_is_clean(self) -> None:
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(Broker()))
        await orchestrator.open()

        await orchestrator.close()

        self.assertIsNone(codex.process)

    async def test_one_owner_starts_steers_idles_and_closes_all_role_threads(self) -> None:
        broker = Broker()
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker))
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)

        self.assertEqual(sorted(broker.agents), ["designer", "foreman", "machinist"])
        request_count_at_standby = codex._next_id
        await __import__("asyncio").sleep(0.01)
        self.assertEqual(codex._next_id, request_count_at_standby, "standby must not create turns or tool calls")

        first = broker.send("direction", "foreman", "designer", "Begin")
        await orchestrator.deliver(first)
        second = broker.send("direction", "foreman", "designer", "Adjust")
        await orchestrator.deliver(second)
        self.assertEqual(broker.delivered, {first.sequence, second.sequence})
        self.assertIsNotNone(orchestrator.roles["designer"].active_turn_id)

    async def test_independent_app_server_cannot_steer_the_owners_thread(self) -> None:
        owner = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        inspector = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        await owner.start()
        await inspector.start()
        self.addAsyncCleanup(owner.close)
        self.addAsyncCleanup(inspector.close)
        thread_id = await owner.start_thread("foreman")
        turn_id = await owner.start_turn(thread_id, "Work")
        with self.assertRaises(InactiveTurn):
            await inspector.steer_turn(thread_id, turn_id, "Cross-process direction")

    async def test_broker_routes_maker_specialist_and_parallel_pipeline_messages(self) -> None:
        broker = Broker()
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker))
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)

        await broker.record_conversation("maker", "Open with the housing.")
        maker_direction = broker.pending_for("foreman")[0]
        await orchestrator.deliver(maker_direction)
        self.assertIsNotNone(orchestrator.roles["foreman"].active_turn_id)

        drawing = broker.assign("designer", "drawing-1", body="Release the first drawing.")
        await orchestrator.deliver(drawing)
        broker.acknowledge("designer", "drawing-1")
        report = broker.send("report", "designer", "foreman", "Released drawing commit abc123.", "drawing-1")
        await orchestrator.deliver(report)

        machining = broker.assign("machinist", "build-1", body="Build released drawing abc123.")
        await orchestrator.deliver(machining)
        broker.acknowledge("machinist", "build-1")
        ahead = broker.assign("designer", "drawing-2", body="Prepare one next draft.")
        self.assertNotIn(ahead.sequence, {item.sequence for item in broker.pending_for("designer")})
        broker.complete("designer", "drawing-1")
        self.assertIn(ahead.sequence, {item.sequence for item in broker.pending_for("designer")})
        await orchestrator.deliver(ahead)

        self.assertIsNotNone(orchestrator.roles["designer"].active_turn_id)
        self.assertIsNotNone(orchestrator.roles["machinist"].active_turn_id)
        self.assertEqual(broker.agents["machinist"].assignment_id, "build-1")


class OrchestratorShutdownAcceptanceTest(unittest.TestCase):
    def test_one_sigint_closes_with_a_live_sse_client(self) -> None:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "floor.orchestrator",
                "--port",
                str(port),
                "--cwd",
                str(ROOT),
                "--codex-command",
                str(FAKE_APP_SERVER),
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
            env={**os.environ},
        )
        self.addCleanup(self._terminate, process)
        assert process.stdout is not None
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if "shop-floor open" in process.stdout.readline():
                break
        else:
            self.fail("orchestrator did not open")

        stream = urlopen(f"http://127.0.0.1:{port}/events/lifecycle", timeout=2)  # nosec: local test server
        self.addCleanup(stream.close)
        self.assertIn(b"event: lifecycle", stream.readline())
        process.send_signal(signal.SIGINT)

        self.assertEqual(process.wait(timeout=5), 0)

    @staticmethod
    def _terminate(process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


if __name__ == "__main__":
    unittest.main()
