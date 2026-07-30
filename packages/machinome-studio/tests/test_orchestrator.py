from __future__ import annotations

import asyncio
import unittest
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

from floor.app import Broker
from floor.backends.codex import CodexBackend as CodexAppServer, InactiveTurn
from floor.backends.base import BackendEvent, DeliveryReceipt, RoleContext, RoleHandle
from floor.backends.hermes import HermesBackend
from floor.orchestrator import (
    LocalBrokerControl,
    ShopOrchestrator,
    _serve,
    _shutdown_runtime,
    _wait_for_runtime,
)
from floor.preparation import PreparationError


ROOT = Path(__file__).resolve().parents[1]
FAKE_APP_SERVER = ROOT / "tests" / "fixtures" / "fake_codex_app_server.py"
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"


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

    # ── AgentBackend protocol shim ──────────────────────────────────────

    async def start(self) -> None:
        pass

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        thread_id = await self.start_thread(role)
        return RoleHandle(backend_id=thread_id, role=role)

    async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        turn_id = await self.start_turn(handle.backend_id, message)
        return DeliveryReceipt(delivery_id=turn_id, accepted=True)

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        await self.steer_turn(handle.backend_id, expected_delivery_id, message)
        return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)

    async def interrupt(self, handle: RoleHandle) -> None:
        await self.interrupt_turn(handle.backend_id, handle.backend_id)

    async def close_role(self, handle: RoleHandle) -> None:
        self.closed.append(handle.backend_id)

    # Events — FakeCodex doesn't emit events; tests call handle_notification
    # directly.  Provide a dummy async iterator for the protocol.
    async def _empty_events(self):
        while True:
            await __import__("asyncio").sleep(3600)
            yield  # type: ignore[misc]

    events = property(lambda self: self._empty_events())


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
        self.assertEqual(runtime.active_delivery_id, "turn-1")

        await self.orchestrator.deliver({"sequence": 11, "recipient": "designer", "body": "Second"})
        self.assertEqual(self.codex.steered_turns[0][0:2], ("thread-designer", "turn-1"))
        self.assertIn("instruction:\nSecond", self.codex.steered_turns[0][2])
        self.assertEqual(self.broker.delivered, [10, 11])

    def test_assignment_delivery_makes_acknowledgement_the_first_tool_call(self) -> None:
        message = self.orchestrator._message(
            {
                "sequence": 10,
                "kind": "assignment",
                "recipient": "machinist",
                "assignment_id": "build-1",
                "body": "Build the released drawing.",
            }
        )

        self.assertIn("FIRST TOOL CALL", message)
        self.assertIn(
            "python -m floor.agent acknowledge --role machinist --assignment build-1",
            message,
        )
        self.assertIn("Do not read files or investigate", message)

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
        self.assertEqual(self.codex.interrupted, [("thread-foreman", "thread-foreman")])
        self.assertEqual(self.codex.closed, ["thread-machinist", "thread-designer", "thread-foreman"])

    async def test_completed_foreman_message_is_published_to_the_maker_conversation(self) -> None:
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="foreman", text="Hello from Foreman.")
        )
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="designer", text="Internal specialist output.")
        )
        self.assertEqual(self.broker.conversation, [("foreman", "Hello from Foreman.")])


class CodexOwnershipAcceptanceTest(unittest.IsolatedAsyncioTestCase):
    async def test_native_turn_identity_survives_events_steering_and_interrupt(self) -> None:
        codex = CodexAppServer(
            ROOT,
            command=(sys.executable, str(FAKE_APP_SERVER)),
        )
        await codex.start()
        self.addAsyncCleanup(codex.close)
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        handle = await codex.open_role("designer", context)

        receipt = await codex.deliver_start(handle, "Begin")
        started = await asyncio.wait_for(anext(codex.events), timeout=1)
        self.assertEqual(started.kind, "turn_started")
        self.assertEqual(started.delivery_id, receipt.delivery_id)

        steered = await codex.deliver_steer(
            handle, started.delivery_id or "", "Adjust"
        )
        self.assertEqual(steered.delivery_id, receipt.delivery_id)
        await codex.interrupt(handle)
        completed = await asyncio.wait_for(anext(codex.events), timeout=1)
        self.assertEqual(completed.kind, "turn_completed")
        self.assertEqual(completed.delivery_id, receipt.delivery_id)

    async def test_unexpected_process_exit_emits_backend_failure(self) -> None:
        codex = CodexAppServer(
            ROOT,
            command=(sys.executable, str(FAKE_APP_SERVER)),
        )
        await codex.start()
        self.addAsyncCleanup(codex.close)
        assert codex.process is not None
        codex.process.terminate()

        event = await asyncio.wait_for(anext(codex.events), timeout=1)
        self.assertEqual(event.kind, "backend_failed")
        self.assertIn("exited unexpectedly", event.error or "")

    async def test_role_threads_work_in_the_active_project_with_explicit_shop_context(self) -> None:
        project = ROOT / "projects" / "snowman"
        callback = "http://127.0.0.1:9000/api/runs/shop-floor/model/ready/capability"
        codex = CodexAppServer(
            ROOT,
            project=project,
            command=(sys.executable, str(FAKE_APP_SERVER)),
            solid_command=("/work/.venv/bin/solid",),
            model_callback_url=callback,
        )
        await codex.start()
        self.addAsyncCleanup(codex.close)

        await codex.start_thread("foreman")
        notification = await codex.notifications.get()
        thread = notification["params"]["thread"]

        self.assertEqual(thread["cwd"], str(project.resolve()))
        self.assertEqual(thread["sandbox"], "workspace-write")
        self.assertIsNone(thread["approvalPolicy"])
        self.assertIn(f"Shop checkout: {ROOT.resolve()}", thread["developerInstructions"])
        self.assertIn(f"Active project: {project.resolve()}", thread["developerInstructions"])

        await codex.start_thread("designer")
        designer = (await codex.notifications.get())["params"]["thread"]
        self.assertEqual(designer["cwd"], str(project.resolve()))
        self.assertEqual(designer["sandbox"], "workspace-write")
        self.assertIsNone(designer["approvalPolicy"])

        await codex.start_thread("machinist")
        machinist = (await codex.notifications.get())["params"]["thread"]
        self.assertEqual(machinist["cwd"], str(project.resolve()))
        self.assertEqual(machinist["sandbox"], "workspace-write")
        self.assertIsNone(machinist["approvalPolicy"])
        self.assertIn("/work/.venv/bin/solid develop root --callback", machinist["developerInstructions"])
        self.assertIn(callback, machinist["developerInstructions"])

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
        self.assertIsNotNone(orchestrator.roles["designer"].active_delivery_id)

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
        self.assertIsNotNone(orchestrator.roles["foreman"].active_delivery_id)

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

        self.assertIsNotNone(orchestrator.roles["designer"].active_delivery_id)
        self.assertIsNotNone(orchestrator.roles["machinist"].active_delivery_id)
        self.assertEqual(broker.agents["machinist"].assignment_id, "build-1")


class OrchestratorShutdownAcceptanceTest(unittest.TestCase):
    def test_preparation_failure_constructs_no_runtime_and_reports_no_url(self) -> None:
        arguments = SimpleNamespace(
            project_name="broken",
            project_home=Path("/work/projects"),
            solid_command="solid",
            cwd=ROOT,
            port=9000,
            backend="codex",
            backend_command="codex",
        )
        failure = PreparationError("build", "broken", Path("/work/projects/broken"), "failed")
        with (
            patch("floor.orchestrator.prepare_project", side_effect=failure),
            patch("floor.orchestrator.Broker") as broker,
            patch("floor.orchestrator.create_app") as create_app,
            self.assertRaises(PreparationError),
        ):
            __import__("asyncio").run(_serve(arguments))
        broker.assert_not_called()
        create_app.assert_not_called()

    def test_one_sigint_closes_with_a_live_sse_client(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project_home = Path(temporary.name) / "projects"
        project_home.mkdir()
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "floor.orchestrator",
                "shutdown-test",
                "--port",
                str(port),
                "--cwd",
                str(ROOT),
                "--backend-command",
                str(FAKE_APP_SERVER),
                "--project-home",
                str(project_home),
                "--solid-command",
                str(FAKE_SOLID),
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "Shop Test",
                "GIT_AUTHOR_EMAIL": "shop@example.invalid",
                "GIT_COMMITTER_NAME": "Shop Test",
                "GIT_COMMITTER_EMAIL": "shop@example.invalid",
            },
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


# ── AgentBackend protocol acceptance tests ─────────────────────────────────
# These tests use the portable AgentBackend protocol and a FakeBackend
# fixture.  They are RED until Phase 4 switches ShopOrchestrator from
# CodexControl to AgentBackend.


class FakeBackendOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    """Orchestrator acceptance through the portable AgentBackend protocol."""

    async def asyncSetUp(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend as FB

        self.backend = FB()
        self.broker = FakeBroker()
        self.orchestrator = ShopOrchestrator(self.backend, self.broker)
        await self.orchestrator.open()

    async def test_open_owns_exactly_the_three_role_sessions(self) -> None:
        self.assertEqual(
            [r for r, _ in self.backend.opened_roles],
            ["foreman", "designer", "machinist"],
        )
        self.assertEqual(
            [role for role, _ in self.broker.manifested],
            [r for r, _ in self.backend.opened_roles],
        )

    async def test_direction_envelope_reaches_backend_deliver_with_body(self) -> None:
        await self.orchestrator.deliver(
            {"sequence": 10, "recipient": "designer", "body": "Design the housing."}
        )
        self.assertEqual(len(self.backend.deliveries), 1)
        handle, message = self.backend.deliveries[0]
        self.assertEqual(handle.role, "designer")
        self.assertIn("Design the housing.", message)

    async def test_role_message_event_records_foreman_conversation(self) -> None:
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="foreman", text="Progress update.")
        )
        self.assertEqual(self.broker.conversation, [("foreman", "Progress update.")])

    async def test_steer_receipt_replaces_the_active_delivery_identity(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class NewIdentityBackend(FakeBackend):
            async def deliver_steer(
                self,
                handle: RoleHandle,
                expected_delivery_id: str,
                message: str,
            ) -> DeliveryReceipt:
                self.deliveries.append((handle, message))
                return DeliveryReceipt(
                    delivery_id="replacement-delivery", accepted=True
                )

        backend = NewIdentityBackend()
        orchestrator = ShopOrchestrator(backend, FakeBroker())
        await orchestrator.open()
        await orchestrator.deliver(
            {"sequence": 30, "recipient": "designer", "body": "Begin"}
        )
        await orchestrator.deliver(
            {"sequence": 31, "recipient": "designer", "body": "Correct"}
        )

        self.assertEqual(
            orchestrator.roles["designer"].active_delivery_id,
            "replacement-delivery",
        )
        await orchestrator.close()

    async def test_backend_and_role_failures_fail_closed(self) -> None:
        for event in (
            BackendEvent(kind="backend_failed", error="process exited"),
            BackendEvent(kind="role_failed", role="designer", error="prompt failed"),
        ):
            with self.subTest(kind=event.kind), self.assertRaisesRegex(
                RuntimeError, event.error or ""
            ):
                await self.orchestrator.handle_event(event)

    async def test_close_interrupts_active_roles_in_reverse_then_closes_backend(self) -> None:
        await self.orchestrator.deliver(
            {"sequence": 14, "recipient": "foreman", "body": "Work"}
        )
        await self.orchestrator.close()
        # At least one interrupted handle for the active foreman
        self.assertGreater(len(self.backend.interrupted), 0)
        self.assertEqual(self.backend.interrupted[0].role, "foreman")
        self.assertTrue(self.backend.closed)

    async def test_close_releases_every_resource_after_individual_failures(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class FailingBackend(FakeBackend):
            async def interrupt(self, handle: RoleHandle) -> None:
                await super().interrupt(handle)
                if handle.role == "designer":
                    raise RuntimeError("interrupt failed")

            async def close_role(self, handle: RoleHandle) -> None:
                await super().close_role(handle)
                if handle.role == "machinist":
                    raise RuntimeError("role close failed")

        backend = FailingBackend()
        orchestrator = ShopOrchestrator(backend, FakeBroker())
        await orchestrator.open()
        await orchestrator.deliver(
            {"sequence": 20, "recipient": "foreman", "body": "Work"}
        )
        await orchestrator.deliver(
            {"sequence": 21, "recipient": "designer", "body": "Work"}
        )

        with self.assertRaisesRegex(RuntimeError, "interrupt failed"):
            await orchestrator.close()
        self.assertEqual(
            [handle.role for handle in backend.interrupted],
            ["designer", "foreman"],
        )
        self.assertEqual(
            [handle.role for handle in backend.closed_roles],
            ["machinist", "designer", "foreman"],
        )
        self.assertTrue(backend.closed)

    async def test_open_preserves_primary_failure_after_cleanup_failure(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class FailingOpenBackend(FakeBackend):
            async def open_role(
                self, role: str, context: RoleContext
            ) -> RoleHandle:
                if role == "designer":
                    raise RuntimeError("designer open failed")
                return await super().open_role(role, context)

            async def close_role(self, handle: RoleHandle) -> None:
                await super().close_role(handle)
                raise RuntimeError("cleanup failed")

        backend = FailingOpenBackend()
        orchestrator = ShopOrchestrator(backend, FakeBroker())
        with self.assertRaisesRegex(RuntimeError, "designer open failed"):
            await orchestrator.open()
        self.assertEqual(
            [handle.role for handle in backend.closed_roles], ["foreman"]
        )
        self.assertTrue(backend.closed)

    async def test_route_failure_ends_runtime_wait(self) -> None:
        async def serve_forever() -> None:
            await asyncio.Future()

        async def fail_route() -> None:
            raise RuntimeError("delivery routing failed")

        server_task = asyncio.create_task(serve_forever())
        route_task = asyncio.create_task(fail_route())
        self.addCleanup(server_task.cancel)
        with self.assertRaisesRegex(RuntimeError, "delivery routing failed"):
            await _wait_for_runtime(server_task, (route_task,))

    async def test_runtime_shutdown_stops_server_when_backend_close_fails(
        self,
    ) -> None:
        class FailingOrchestrator:
            async def close(self) -> None:
                raise RuntimeError("backend close failed")

        class FakeServer:
            should_exit = False

        server = FakeServer()

        async def serve_until_stopped() -> None:
            while not server.should_exit:
                await asyncio.sleep(0)

        server_task = asyncio.create_task(serve_until_stopped())
        with self.assertRaisesRegex(RuntimeError, "backend close failed"):
            await _shutdown_runtime(
                FailingOrchestrator(), server, server_task
            )
        self.assertTrue(server.should_exit)
        self.assertTrue(server_task.done())


class BackendFlagAcceptanceTest(unittest.TestCase):
    def test_unknown_backend_rejected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend

        with self.assertRaises(ValueError) as cm:
            create_backend("unknown", cwd=Path("/tmp"))
        self.assertIn("unknown", str(cm.exception))

    def test_codex_backend_selected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend
        from floor.backends.codex import CodexBackend

        backend = create_backend("codex", cwd=Path("/tmp"))
        self.assertIsInstance(backend, CodexBackend)

    def test_hermes_backend_selected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend
        from floor.backends.hermes import HermesBackend

        backend = create_backend("hermes", cwd=Path("/tmp"))
        self.assertIsInstance(backend, HermesBackend)


class ACPFixtureTest(unittest.TestCase):
    def test_fake_acp_server_starts_and_accepts_session_new(self) -> None:
        """Smoke test: the fake ACP server accepts session/new over stdio."""
        import subprocess

        proc = subprocess.Popen(
            [sys.executable, str(ROOT / "tests" / "fixtures" / "fake_acp_server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: proc.kill())
        assert proc.stdin is not None and proc.stdout is not None

        proc.stdin.write(
            json.dumps(
                {
                    "id": 1,
                    "method": "session/new",
                    "params": {"cwd": "/tmp", "mcpServers": []},
                }
            )
            + "\n"
        )
        proc.stdin.flush()
        response = json.loads(proc.stdout.readline())
        self.assertEqual(response["id"], 1)
        self.assertIn("sessionId", response["result"])
        self.assertIn("session-1", response["result"]["sessionId"])

        proc.stdin.close()
        proc.wait(timeout=5)


# ── HermesBackend acceptance tests against fake ACP fixture ────────────────
# RED until HermesBackend methods are implemented (currently all raise
# NotImplementedError).

FAKE_ACP_SERVER = ROOT / "tests" / "fixtures" / "fake_acp_server.py"


class HermesBackendAcceptanceTest(unittest.IsolatedAsyncioTestCase):
    """HermesBackend exercising all AgentBackend operations through fake ACP."""

    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.capture = Path(self.temporary.name) / "acp.jsonl"
        self.environment = patch.dict(
            os.environ, {"FAKE_ACP_CAPTURE": str(self.capture)}
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.hermes = HermesBackend(
            ROOT,
            project=ROOT / "projects" / "snowman",
            command=(sys.executable, str(FAKE_ACP_SERVER)),
            solid_command=("/work/.venv/bin/solid",),
        )

    def captured(self) -> list[dict]:
        return [json.loads(line) for line in self.capture.read_text().splitlines()]

    async def test_role_bootstrap_and_environment_are_operational(self) -> None:
        await self.hermes.start()
        callback = "http://127.0.0.1:9000/model-ready"
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
            model_callback_url=callback,
        )
        await self.hermes.open_role("machinist", context)

        captured = self.captured()
        environment = next(item for item in captured if item["kind"] == "environment")
        self.assertTrue(environment["floorImportable"])
        self.assertIn(str(ROOT), environment["pythonpath"].split(os.pathsep))
        prompts = [
            item["value"]
            for item in captured
            if item["kind"] == "message"
            and item["value"].get("method") == "session/prompt"
        ]
        self.assertEqual(len(prompts), 1)
        self.assertIn("id", prompts[0], "session/prompt must be an ACP request")
        text = prompts[0]["params"]["prompt"][0]["text"]
        self.assertIn(str(ROOT / "agents" / "machinist.md"), text)
        self.assertIn(str(ROOT / "skills" / "solid-node-api" / "SKILL.md"), text)
        self.assertIn(str(ROOT / "skills" / "solid-node" / "SKILL.md"), text)
        self.assertIn("/work/.venv/bin/solid develop root --callback", text)
        self.assertIn(callback, text)
        await self.hermes.close()

    async def test_prompt_events_preserve_request_identity(self) -> None:
        await self.hermes.start()
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        handle = await self.hermes.open_role("foreman", context)
        receipt = await self.hermes.deliver_start(handle, "Begin")

        started = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        message = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        completed = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(
            (started.kind, started.delivery_id),
            ("turn_started", receipt.delivery_id),
        )
        self.assertEqual(
            (message.kind, message.role, message.text),
            ("role_message", "foreman", "FAKE_REPLY"),
        )
        self.assertEqual(
            (completed.kind, completed.delivery_id),
            ("turn_completed", receipt.delivery_id),
        )
        await self.hermes.close()

    async def test_unexpected_process_exit_emits_backend_failure(self) -> None:
        await self.hermes.start()
        assert self.hermes.process is not None
        self.hermes.process.terminate()
        event = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(event.kind, "backend_failed")
        self.assertIn("hermes acp exited", event.error or "")
        await self.hermes.close()

    async def test_full_role_lifecycle_through_fake_acp(self) -> None:
        """start -> open_role x 3 -> deliver -> close through fake ACP."""
        await self.hermes.start()
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        foreman = await self.hermes.open_role("foreman", context)
        designer = await self.hermes.open_role("designer", context)
        machinist = await self.hermes.open_role("machinist", context)

        self.assertEqual(foreman.role, "foreman")
        self.assertEqual(designer.role, "designer")
        self.assertEqual(machinist.role, "machinist")

        receipt = await self.hermes.deliver_start(
            foreman, "Begin the design."
        )
        self.assertTrue(receipt.accepted)
        self.assertIsNotNone(receipt.delivery_id)

        await self.hermes.close_role(designer)
        await self.hermes.close_role(machinist)
        await self.hermes.close_role(foreman)
        await self.hermes.close()

    async def test_deliver_and_interrupt_through_fake_acp(self) -> None:
        """deliver_start then interrupt cancels the active session."""
        await self.hermes.start()
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        handle = await self.hermes.open_role("foreman", context)
        await self.hermes.deliver_start(handle, "Work")
        await self.hermes.interrupt(handle)
        await self.hermes.close_role(handle)
        await self.hermes.close()

    async def test_active_prompt_is_steered_without_replacing_its_identity(
        self,
    ) -> None:
        await self.hermes.start()
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        handle = await self.hermes.open_role("foreman", context)
        first = await self.hermes.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(started.delivery_id, first.delivery_id)

        second = await self.hermes.deliver_steer(
            handle, first.delivery_id, "Corrected"
        )
        self.assertEqual(second.delivery_id, first.delivery_id)

        # The redirect acknowledgement is control-plane text, not a second turn
        # or a role message for the maker conversation.
        await asyncio.sleep(0.05)
        self.assertTrue(self.hermes.notifications.empty())
        await self.hermes.close()

    async def test_deliver_steer_handles_inactive_turn_through_fake_acp(self) -> None:
        """deliver_steer on a completed turn raises InactiveTurn."""
        await self.hermes.start()
        context = RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(ROOT / "projects" / "snowman"),
        )
        handle = await self.hermes.open_role("foreman", context)
        receipt = await self.hermes.deliver_start(handle, "First")
        # Let _read_stdout process the fake ACP server's response
        # (the fake server returns end_turn immediately).
        await asyncio.sleep(0.05)
        # Now the turn is complete; steering should raise InactiveTurn.
        with self.assertRaises(InactiveTurn):
            await self.hermes.deliver_steer(
                handle, receipt.delivery_id, "Correction"
            )
        await self.hermes.close_role(handle)
        await self.hermes.close()

    async def test_idempotent_start_through_fake_acp(self) -> None:
        """Calling start() twice does not launch a second process."""
        await self.hermes.start()
        process = self.hermes.process
        await self.hermes.start()
        self.assertIs(self.hermes.process, process)
        await self.hermes.close()

    async def _foreman(self) -> RoleHandle:
        await self.hermes.start()
        return await self.hermes.open_role(
            "foreman",
            RoleContext(
                shop_checkout=str(ROOT),
                active_project=str(ROOT / "projects" / "snowman"),
            ),
        )

    def _methods(self) -> list[str]:
        return [
            item["value"]["method"]
            for item in self.captured()
            if item["kind"] == "message" and "method" in item["value"]
        ]

    async def test_steering_never_cancels_the_active_turn(self) -> None:
        """ADR 0007: a correction is an extra prompt, never a cancellation."""
        handle = await self._foreman()
        first = await self.hermes.deliver_start(handle, "HOLD")

        steered = await self.hermes.deliver_steer(
            handle, first.delivery_id, "Corrected"
        )

        self.assertEqual(steered.delivery_id, first.delivery_id)
        self.assertNotIn("session/cancel", self._methods())
        await self.hermes.close()

    async def test_steer_acknowledgement_is_not_a_turn_completion(self) -> None:
        """The instant bare stop reason must not complete either delivery."""
        handle = await self._foreman()
        first = await self.hermes.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(started.delivery_id, first.delivery_id)

        await self.hermes.deliver_steer(handle, first.delivery_id, "Corrected")
        await asyncio.sleep(0.1)

        # No turn_completed for either identity, and the original is still
        # the session's active prompt.
        self.assertTrue(self.hermes.notifications.empty())
        self.assertEqual(
            self.hermes._active_prompts.get(handle.backend_id),
            int(first.delivery_id),
        )
        await self.hermes.close()

    async def test_text_streamed_before_a_correction_is_retained(self) -> None:
        """Steering preserves the turn, so its earlier output must survive.

        Deliberately does not sleep before steering. `turn_started` is queued
        before the write is drained, so the correction is sent while the turn's
        first chunk is still unread — the case where suppressing chunks by
        session would silently eat real output. The assembled message must
        still contain the pre-correction text and not the acknowledgement.
        """
        handle = await self._foreman()
        first = await self.hermes.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(started.kind, "turn_started")

        # "FINISH" makes the fixture apply the correction inside the held turn.
        await self.hermes.deliver_steer(handle, first.delivery_id, "FINISH now")

        message = await asyncio.wait_for(anext(self.hermes.events), timeout=2)
        completed = await asyncio.wait_for(anext(self.hermes.events), timeout=2)
        self.assertEqual((message.kind, message.role), ("role_message", "foreman"))
        self.assertEqual(message.text, "PREPOST")
        self.assertEqual(
            (completed.kind, completed.delivery_id),
            ("turn_completed", first.delivery_id),
        )
        await self.hermes.close()

    async def test_cancelled_turn_completes_and_is_not_a_role_failure(self) -> None:
        """hermes 0.19.0 fails a cancelled prompt; that must not kill the run."""
        handle = await self._foreman()
        receipt = await self.hermes.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.hermes.events), timeout=1)
        self.assertEqual(started.kind, "turn_started")

        await self.hermes.interrupt(handle)

        event = await asyncio.wait_for(anext(self.hermes.events), timeout=2)
        self.assertEqual(
            (event.kind, event.delivery_id),
            ("turn_completed", receipt.delivery_id),
            "a cancelled turn must complete, not fail the role",
        )
        await self.hermes.close()

    async def test_slow_role_bootstrap_still_opens_the_shop(self) -> None:
        """A bootstrap slower than the control budget is not a protocol stall."""
        hermes = HermesBackend(
            ROOT,
            project=ROOT / "projects" / "snowman",
            command=(sys.executable, str(FAKE_ACP_SERVER)),
            solid_command=("/work/.venv/bin/solid",),
            control_timeout=0.3,
            prompt_timeout=20,
        )
        with patch.dict(os.environ, {"FAKE_ACP_PROMPT_DELAY": "1.5"}):
            await hermes.start()
            handle = await hermes.open_role(
                "foreman",
                RoleContext(
                    shop_checkout=str(ROOT),
                    active_project=str(ROOT / "projects" / "snowman"),
                ),
            )
        self.assertEqual(handle.role, "foreman")
        await hermes.close()

    async def test_close_is_bounded_against_a_subprocess_that_ignores_signals(
        self,
    ) -> None:
        """close() must escalate to SIGKILL rather than wait forever."""
        with patch.dict(os.environ, {"FAKE_ACP_IGNORE_SIGNALS": "1"}):
            hermes = HermesBackend(
                ROOT,
                project=ROOT / "projects" / "snowman",
                command=(sys.executable, str(FAKE_ACP_SERVER)),
                solid_command=("/work/.venv/bin/solid",),
            )
            await hermes.start()
            process = hermes.process
            assert process is not None
            started = time.monotonic()
            await asyncio.wait_for(hermes.close(), timeout=20)
            elapsed = time.monotonic() - started
        self.assertIsNotNone(process.returncode)
        self.assertLess(elapsed, 15, "close() must be bounded")


if __name__ == "__main__":
    unittest.main()
