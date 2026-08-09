from __future__ import annotations

import asyncio
import io
import unittest
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import replace
from contextlib import redirect_stderr
from types import SimpleNamespace
from pathlib import Path
from typing import cast
from unittest.mock import patch
from urllib.request import urlopen

from floor.app import Broker
from floor.backends.codex import CodexBackend as CodexAppServer
from floor.backends.base import AgentBackend, BackendEvent, DeliveryReceipt, InactiveTurn, RoleContext, RoleHandle
from floor.orchestrator import (
    LocalBrokerControl,
    ShopOrchestrator,
    _route_backend_events,
    _serve,
    _shutdown_runtime,
    _wait_for_runtime,
)
from floor.preparation import PreparationError, ProjectAgentRuntime, ProjectRuntimeSelection
from floor.profiles import load_profile, resolve_profile_runtime

from tests.fixtures.primary_shop import isolated_primary_shop


ROOT = Path(__file__).resolve().parents[1]
FAKE_APP_SERVER = ROOT / "tests" / "fixtures" / "fake_codex_app_server.py"
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
def _resolved_profile(profile_id: str, backend: str = "codex"):
    profile = load_profile(profile_id, shop_root=ROOT)
    agents = {}
    if backend != "codex":
        for agent in profile.agents:
            if backend == "claude":
                default = agent.backends["claude"]
                source = f"claude:{default.model}"
                agents[agent.id] = ProjectAgentRuntime("claude", None, default.model, None, source)
            else:
                source = "opencode:openai:gpt-5.4"
                agents[agent.id] = ProjectAgentRuntime("opencode", "openai", "gpt-5.4", None, source)
    selection = ProjectRuntimeSelection(ROOT, ROOT / "pyproject.toml", agents)
    return resolve_profile_runtime(profile, selection)


FORDESMAC = _resolved_profile("fordesmac")


def _context(role: str, *, backend: str = "codex", project: Path | None = None) -> RoleContext:
    profile = _resolved_profile("fordesmac", backend)
    return RoleContext(
        shop_checkout=str(ROOT),
        active_project=str((project or ROOT / "projects" / "snowman").resolve()),
        agent=profile.agent(role),
        profile_id=profile.id,
        user_label=profile.user_label,
        user_agent_label=profile.user_agent.label,
    )


class FakeBroker:
    def __init__(self) -> None:
        self.manifested: list[tuple[str, str]] = []
        self.delivered: list[int] = []
        self.conversation: list[tuple[str, str]] = []
        self.failures: dict[str, str] = {}
        self.recoveries: list[str] = []
        self.failed_deliveries: list[tuple[int, str]] = []

    async def manifest(self, role: str, label: str) -> None:
        self.manifested.append((role, label))

    async def mark_delivered(self, sequence: int) -> None:
        self.delivered.append(sequence)

    async def record_conversation(self, author: str, text: str) -> None:
        self.conversation.append((author, text))

    async def role_failed(self, role: str, error: str) -> None:
        self.failures[role] = error

    async def role_recovered(self, role: str) -> None:
        self.failures.pop(role, None)
        self.recoveries.append(role)

    async def mark_delivery_failed(self, sequence: int, error: str) -> None:
        self.failed_deliveries.append((sequence, error))


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
        self.orchestrator = ShopOrchestrator(self.codex, self.broker, profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await self.orchestrator.open()

    async def test_open_owns_exactly_the_three_role_threads(self) -> None:
        self.assertEqual(self.codex.started_threads, ["foreman", "designer", "machinist", "librarian"])
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
        self.assertEqual(self.codex.closed, ["thread-librarian", "thread-machinist", "thread-designer", "thread-foreman"])

    async def test_completed_foreman_message_is_published_to_the_maker_conversation(self) -> None:
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="foreman", text="Hello from Foreman.")
        )
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="designer", text="Internal specialist output.")
        )
        self.assertEqual(self.broker.conversation, [("foreman", "Hello from Foreman.")])


class MultiBackendOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    async def test_each_distinct_backend_opens_and_closes_once_for_its_agents(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class CountingBackend(FakeBackend):
            def __init__(self) -> None:
                super().__init__()
                self.start_count = 0
                self.close_count = 0

            async def start(self) -> None:
                self.start_count += 1
                await super().start()

            async def close(self) -> None:
                self.close_count += 1
                await super().close()

        profile = load_profile("fordesmac", shop_root=ROOT)
        selection = ProjectRuntimeSelection(
            ROOT,
            ROOT / "pyproject.toml",
            {
                "designer": ProjectAgentRuntime("claude", None, "opus", None, "claude:opus"),
            },
        )
        profile = resolve_profile_runtime(profile, selection)
        codex, claude = CountingBackend(), CountingBackend()
        orchestrator = ShopOrchestrator(
            {
                "foreman": codex,
                "designer": claude,
                "machinist": codex,
                "librarian": codex,
            },
            FakeBroker(),
            profile=profile,
            shop_checkout=ROOT,
            active_project=ROOT,
        )

        await orchestrator.open()
        self.assertTrue(codex.started)
        self.assertTrue(claude.started)
        self.assertEqual([role for role, _ in codex.opened_roles], ["foreman", "machinist", "librarian"])
        self.assertEqual([role for role, _ in claude.opened_roles], ["designer"])
        await orchestrator.close()
        self.assertEqual([handle.role for handle in codex.closed_roles], ["librarian", "machinist", "foreman"])
        self.assertEqual([handle.role for handle in claude.closed_roles], ["designer"])
        self.assertTrue(codex.closed)
        self.assertTrue(claude.closed)
        self.assertEqual((codex.start_count, claude.start_count), (1, 1))
        self.assertEqual((codex.close_count, claude.close_count), (1, 1))

    async def test_later_backend_start_failure_closes_every_backend(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class FailingStartBackend(FakeBackend):
            async def start(self) -> None:
                raise RuntimeError("second backend failed")

        first, second = FakeBackend(), FailingStartBackend()
        orchestrator = ShopOrchestrator(
            {agent.id: (second if agent.id == "designer" else first) for agent in FORDESMAC.agents},
            FakeBroker(), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT,
        )
        with self.assertRaisesRegex(RuntimeError, "second backend failed"):
            await orchestrator.open()
        self.assertTrue(first.closed)
        self.assertTrue(second.closed)

    async def test_event_streams_from_both_backends_are_consumed(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class QueueBackend(FakeBackend):
            def __init__(self) -> None:
                super().__init__()
                self.queue: asyncio.Queue[BackendEvent] = asyncio.Queue()
                self.events = self._queue_events()

            async def _queue_events(self):
                while True:
                    yield await self.queue.get()

        class RecordingOrchestrator(ShopOrchestrator):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                self.seen: list[tuple[str, str | None]] = []

            async def handle_event(self, event: BackendEvent) -> None:
                self.seen.append((event.kind, event.role))
                await super().handle_event(event)

        codex, claude = QueueBackend(), QueueBackend()
        profile = FORDESMAC
        orchestrator = RecordingOrchestrator(
            {agent.id: (claude if agent.id == "designer" else codex) for agent in profile.agents},
            FakeBroker(), profile=profile, shop_checkout=ROOT, active_project=ROOT,
        )
        tasks = [
            asyncio.create_task(_route_backend_events(orchestrator, backend))
            for backend in (codex, claude)
        ]
        self.addAsyncCleanup(lambda: [task.cancel() for task in tasks])
        await codex.queue.put(BackendEvent(kind="role_message", role="foreman", text="from codex"))
        await claude.queue.put(BackendEvent(kind="role_message", role="designer", text="from claude"))
        for _ in range(20):
            if len(orchestrator.seen) == 2:
                break
            await asyncio.sleep(0)
        self.assertEqual(set(orchestrator.seen), {("role_message", "foreman"), ("role_message", "designer")})


class ProfileOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    async def test_direct_start_event_that_wins_the_receipt_race_is_adopted(self) -> None:
        profile = _resolved_profile("builder")
        broker = Broker(profile=profile)

        class RacingCodex(FakeCodex):
            orchestrator: ShopOrchestrator

            async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
                receipt = await super().deliver_start(handle, message)
                await self.orchestrator.handle_event(
                    BackendEvent(
                        kind="turn_started",
                        role=handle.role,
                        delivery_id=receipt.delivery_id,
                    )
                )
                return receipt

        codex = RacingCodex()
        orchestrator = ShopOrchestrator(
            cast(AgentBackend, codex),
            LocalBrokerControl(broker),
            profile=profile,
            shop_checkout=ROOT,
            active_project=ROOT,
        )
        codex.orchestrator = orchestrator
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        await broker.record_conversation("user", "Build")
        await orchestrator.deliver(broker.pending_for("builder")[0])

        self.assertEqual(broker.agents["builder"].state, "active")
        self.assertEqual(
            broker.agents["builder"].direct_delivery_id,
            orchestrator.roles["builder"].active_delivery_id,
        )

    async def test_direct_completion_that_wins_the_receipt_race_stays_waiting(self) -> None:
        profile = _resolved_profile("builder")
        broker = Broker(profile=profile)

        class RacingCodex(FakeCodex):
            orchestrator: ShopOrchestrator

            async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
                receipt = await super().deliver_start(handle, message)
                for kind in ("turn_started", "turn_completed"):
                    await self.orchestrator.handle_event(
                        BackendEvent(
                            kind=kind,
                            role=handle.role,
                            delivery_id=receipt.delivery_id,
                        )
                    )
                return receipt

        codex = RacingCodex()
        orchestrator = ShopOrchestrator(
            cast(AgentBackend, codex),
            LocalBrokerControl(broker),
            profile=profile,
            shop_checkout=ROOT,
            active_project=ROOT,
        )
        codex.orchestrator = orchestrator
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        await broker.record_conversation("user", "Quick answer")
        await orchestrator.deliver(broker.pending_for("builder")[0])

        self.assertEqual(broker.agents["builder"].state, "waiting")
        self.assertEqual(broker.agents["builder"].direct_delivery_id, "")
        self.assertIsNone(orchestrator.roles["builder"].active_delivery_id)

    async def test_every_declared_agent_gets_the_exact_verified_project_root(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        project = ROOT / "projects" / "verified-root"
        profile = _resolved_profile("fordesmac")
        backend = FakeBackend()
        orchestrator = ShopOrchestrator(
            backend,
            FakeBroker(),
            profile=profile,
            shop_checkout=ROOT,
            active_project=project,
        )
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        self.assertEqual(
            [context.active_project for _, context in backend.opened_roles],
            [str(project.resolve())] * len(profile.agents),
        )

    async def test_profile_order_contract_and_only_user_agent_output_are_generic(self) -> None:
        profile = _resolved_profile("fordesmac")
        codex = FakeCodex()
        broker = FakeBroker()
        orchestrator = ShopOrchestrator(codex, broker, profile=profile, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        self.assertEqual(codex.started_threads, ["foreman", "designer", "machinist", "librarian"])
        await orchestrator.handle_event(BackendEvent(kind="role_message", role="designer", text="Internal"))
        await orchestrator.handle_event(BackendEvent(kind="role_message", role="foreman", text="Public"))
        self.assertEqual(broker.conversation, [("foreman", "Public")])

    async def test_direct_turn_events_update_the_builder_broker_without_assignment_ids(self) -> None:
        profile = _resolved_profile("builder")
        broker = Broker(profile=profile)
        codex = FakeCodex()
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker), profile=profile, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        await broker.record_conversation("user", "Build")
        envelope = broker.pending_for("builder")[0]
        await orchestrator.deliver(envelope)
        delivery = orchestrator.roles["builder"].active_delivery_id
        await orchestrator.handle_event(BackendEvent(kind="turn_started", role="builder", delivery_id=delivery))
        self.assertEqual(broker.agents["builder"].state, "active")
        await orchestrator.handle_event(BackendEvent(kind="turn_completed", role="builder", delivery_id=delivery))
        self.assertEqual(broker.agents["builder"].state, "waiting")

    async def test_direct_lifecycle_ignores_stale_events_and_preserves_the_steered_delivery_identity(self) -> None:
        profile = _resolved_profile("builder")
        broker = Broker(profile=profile)
        codex = FakeCodex()
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker), profile=profile, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        await broker.record_conversation("user", "Build")
        first = broker.pending_for("builder")[0]
        await orchestrator.deliver(first)
        delivery = orchestrator.roles["builder"].active_delivery_id

        await orchestrator.handle_event(BackendEvent(kind="turn_started", role="builder", delivery_id="stale"))
        self.assertEqual(broker.agents["builder"].state, "waiting")
        self.assertEqual(orchestrator.roles["builder"].active_delivery_id, delivery)

        await orchestrator.handle_event(BackendEvent(kind="turn_started", role="builder", delivery_id=delivery))
        await broker.record_conversation("user", "Use aluminum")
        steer = broker.pending_for("builder")[0]
        await orchestrator.deliver(steer)
        self.assertEqual(orchestrator.roles["builder"].active_delivery_id, delivery)

        await orchestrator.handle_event(BackendEvent(kind="turn_completed", role="builder", delivery_id="stale"))
        self.assertEqual(broker.agents["builder"].state, "active")
        self.assertEqual(orchestrator.roles["builder"].active_delivery_id, delivery)

        await orchestrator.handle_event(BackendEvent(kind="turn_completed", role="builder", delivery_id=delivery))
        self.assertEqual(broker.agents["builder"].state, "waiting")


class CodexOwnershipAcceptanceTest(unittest.IsolatedAsyncioTestCase):
    async def test_native_turn_identity_survives_events_steering_and_interrupt(self) -> None:
        codex = CodexAppServer(
            ROOT,
            command=(sys.executable, str(FAKE_APP_SERVER)),
        )
        await codex.start()
        self.addAsyncCleanup(codex.close)
        context = _context("designer")
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
        codex = CodexAppServer(
            ROOT,
            project=project,
            command=(sys.executable, str(FAKE_APP_SERVER)),
            solid_command=("/work/.venv/bin/solid",),
        )
        await codex.start()
        self.addAsyncCleanup(codex.close)

        await codex.start_thread("foreman", _context("foreman", project=project))
        notification = await codex.notifications.get()
        thread = notification["params"]["thread"]

        self.assertEqual(thread["cwd"], str(project.resolve()))
        self.assertEqual(thread["sandbox"], "danger-full-access")
        self.assertEqual(thread["approvalPolicy"], "never")
        self.assertEqual(thread["runtimeWorkspaceRoots"], [str(project.resolve())])
        self.assertEqual(thread["config"], {"model_reasoning_effort": "medium"})
        self.assertIn(f"Shop checkout: {ROOT.resolve()}", thread["developerInstructions"])
        self.assertIn(f"Active project: {project.resolve()}", thread["developerInstructions"])

        await codex.start_thread("designer", _context("designer", project=project))
        designer = (await codex.notifications.get())["params"]["thread"]
        self.assertEqual(designer["cwd"], str(project.resolve()))
        self.assertEqual(designer["sandbox"], "danger-full-access")
        self.assertEqual(designer["approvalPolicy"], "never")
        self.assertEqual(designer["runtimeWorkspaceRoots"], [str(project.resolve())])
        self.assertEqual(designer["config"], {"model_reasoning_effort": "medium"})

        await codex.start_thread("machinist", _context("machinist", project=project))
        machinist = (await codex.notifications.get())["params"]["thread"]
        self.assertEqual(machinist["cwd"], str(project.resolve()))
        self.assertEqual(machinist["sandbox"], "danger-full-access")
        self.assertEqual(machinist["approvalPolicy"], "never")
        self.assertEqual(machinist["runtimeWorkspaceRoots"], [str(project.resolve())])
        self.assertEqual(machinist["config"], {"model_reasoning_effort": "medium"})
        self.assertNotIn("develop root", machinist["developerInstructions"])

    async def test_closing_never_used_role_threads_is_clean(self) -> None:
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(Broker(FORDESMAC)), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()

        await orchestrator.close()

        self.assertIsNone(codex.process)

    async def test_one_owner_starts_steers_idles_and_closes_all_role_threads(self) -> None:
        broker = Broker(FORDESMAC)
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)

        self.assertEqual(sorted(broker.agents), ["designer", "foreman", "librarian", "machinist"])
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
        thread_id = await owner.start_thread("foreman", _context("foreman"))
        turn_id = await owner.start_turn(thread_id, "Work")
        with self.assertRaises(InactiveTurn):
            await inspector.steer_turn(thread_id, turn_id, "Cross-process direction")

    async def test_broker_routes_maker_specialist_and_parallel_pipeline_messages(self) -> None:
        broker = Broker(FORDESMAC)
        codex = CodexAppServer(ROOT, command=(sys.executable, str(FAKE_APP_SERVER)))
        orchestrator = ShopOrchestrator(codex, LocalBrokerControl(broker), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)

        await broker.record_conversation("user", "Open with the housing.")
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
            backend_command=[],
        )
        failure = PreparationError("build", "broken", Path("/work/projects/broken"), "failed")
        with (
            patch("floor.orchestrator.primary_shop_root", return_value=ROOT),
            patch("floor.orchestrator.prepare_project", side_effect=failure),
            patch("floor.orchestrator.Broker") as broker,
            patch("floor.orchestrator.create_app") as create_app,
            self.assertRaises(PreparationError),
        ):
            __import__("asyncio").run(_serve(arguments))
        broker.assert_not_called()
        create_app.assert_not_called()

    def test_orchestrator_normalizes_to_the_primary_root_before_loading_a_profile(self) -> None:
        arguments = SimpleNamespace(
            project_name="broken",
            project_home=Path("/work/projects"),
            solid_command="solid",
            cwd=ROOT / "WTs" / "checkout",
            port=9000,
            backend_command=[],
        )
        primary = ROOT
        failure = PreparationError("build", "broken", Path("/work/projects/broken"), "failed")
        with (
            patch("floor.orchestrator.primary_shop_root", return_value=primary),
            patch("floor.orchestrator.load_profile", return_value=FORDESMAC) as load_profile,
            patch("floor.orchestrator.prepare_project", side_effect=failure),
            self.assertRaises(PreparationError),
        ):
            __import__("asyncio").run(_serve(arguments))
        self.assertEqual(load_profile.call_args.kwargs["shop_root"], primary)

    def test_project_profile_and_option_override_resolve_for_the_orchestrated_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_home = Path(temporary) / "projects"
            project = project_home / "engine"
            project.mkdir(parents=True)
            (project / "pyproject.toml").write_text(
                '[tool.solid-node-studio]\nprofile = "builder"\n'
            )
            failure = PreparationError("build", "engine", project, "failed")
            for option, expected in ((None, "builder"), ("fordesmac", "fordesmac")):
                arguments = SimpleNamespace(
                    project_name="engine",
                    project_home=project_home,
                    solid_command="solid",
                    cwd=ROOT,
                    profile=option,
                    port=9000,
                    backend_command=[],
                )
                with (
                    self.subTest(option=option),
                    patch("floor.orchestrator.primary_shop_root", return_value=ROOT),
                    patch("floor.orchestrator.resolve_profile_runtime", wraps=resolve_profile_runtime) as resolve,
                    patch("floor.orchestrator.prepare_project", side_effect=failure),
                    self.assertRaises(PreparationError),
                ):
                    asyncio.run(_serve(arguments))
                self.assertEqual(resolve.call_args.args[0].id, expected)

    def test_profile_override_ignores_and_reports_declared_roster_selections(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_home = Path(temporary) / "projects"
            project = project_home / "engine"
            project.mkdir(parents=True)
            (project / "pyproject.toml").write_text(
                '[tool.solid-node-studio]\n'
                'profile = "fordesmac"\n'
                '[tool.solid-node-studio.agents]\n'
                'designer = "claude:opus"\n'
                'machinist = "codex:gpt-5.6-sol"\n'
            )
            arguments = SimpleNamespace(
                project_name="engine",
                project_home=project_home,
                solid_command="solid",
                cwd=ROOT,
                profile="builder",
                port=9000,
                backend_command=[],
            )
            failure = PreparationError("build", "engine", project, "failed")
            errors = io.StringIO()
            with (
                patch("floor.orchestrator.primary_shop_root", return_value=ROOT),
                patch("floor.orchestrator.resolve_profile_runtime", wraps=resolve_profile_runtime) as resolve,
                patch("floor.orchestrator.prepare_project", side_effect=failure),
                redirect_stderr(errors),
                self.assertRaises(PreparationError),
            ):
                asyncio.run(_serve(arguments))

            profile = resolve_profile_runtime(*resolve.call_args.args)
            self.assertEqual(profile.id, "builder")
            self.assertEqual(profile.ignored_agent_ids, ("designer", "machinist"))
            self.assertIn("ignored runtime selection for agent 'designer'", errors.getvalue())
            self.assertIn("ignored runtime selection for agent 'machinist'", errors.getvalue())

    def test_one_sigint_closes_with_a_live_sse_client(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project_home = Path(temporary.name) / "projects"
        project_home.mkdir()
        shop = self.enterContext(isolated_primary_shop())
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
                str(shop),
                "--backend-command",
                f"codex={FAKE_APP_SERVER}",
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

        stream = urlopen(f"http://127.0.0.1:{port}/api/stream", timeout=2)  # nosec: local test server
        self.addCleanup(stream.close)
        self.assertIn(b"event: snapshot", stream.readline())
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
        self.orchestrator = ShopOrchestrator(self.backend, self.broker, profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await self.orchestrator.open()

    async def test_open_owns_exactly_the_three_role_sessions(self) -> None:
        self.assertEqual(
            [r for r, _ in self.backend.opened_roles],
            ["foreman", "designer", "machinist", "librarian"],
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

    async def test_steer_receipt_cannot_replace_the_active_delivery_identity(self) -> None:
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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        await orchestrator.deliver(
            {"sequence": 30, "recipient": "designer", "body": "Begin"}
        )
        with self.assertRaisesRegex(RuntimeError, "changed the active delivery identity"):
            await orchestrator.deliver(
                {"sequence": 31, "recipient": "designer", "body": "Correct"}
            )
        self.assertEqual(orchestrator.roles["designer"].active_delivery_id, "delivery-1")
        await orchestrator.close()

    async def test_role_failure_retains_the_session_and_the_next_delivery_recovers_it(self) -> None:
        await self.orchestrator.deliver(
            {"sequence": 30, "recipient": "designer", "body": "Begin"}
        )
        retained = self.orchestrator.roles["designer"].handle

        await self.orchestrator.handle_event(
            BackendEvent(kind="role_failed", role="designer", error="session limit")
        )

        self.assertEqual(self.broker.failures, {"designer": "session limit"})
        self.assertIsNone(self.orchestrator.roles["designer"].active_delivery_id)
        await self.orchestrator.deliver(
            {"sequence": 31, "recipient": "designer", "body": "Resume"}
        )
        self.assertEqual(self.backend.deliveries[-1][0], retained)
        self.assertEqual(self.broker.recoveries, ["designer"])
        self.assertNotIn("designer", self.broker.failures)

    async def test_dead_failed_session_is_replaced_once_for_the_recovery_delivery(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class DeadSessionBackend(FakeBackend):
            failed_handle: RoleHandle | None = None

            async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
                if handle == self.failed_handle:
                    raise RuntimeError("session pipe is closed")
                return await super().deliver_start(handle, message)

        backend = DeadSessionBackend()
        broker = FakeBroker()
        orchestrator = ShopOrchestrator(backend, broker, profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        backend.failed_handle = orchestrator.roles["machinist"].handle
        await orchestrator.handle_event(
            BackendEvent(kind="role_failed", role="machinist", error="process exited")
        )

        await orchestrator.deliver(
            {"sequence": 40, "recipient": "machinist", "body": "Resume machining"}
        )

        self.assertIn(backend.failed_handle, backend.closed_roles)
        self.assertEqual([role for role, _ in backend.opened_roles].count("machinist"), 2)
        self.assertNotEqual(orchestrator.roles["machinist"].handle, backend.failed_handle)
        self.assertEqual(broker.recoveries, ["machinist"])
        await orchestrator.close()

    async def test_failed_recovery_attempt_is_reported_without_ending_routing(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class UnavailableBackend(FakeBackend):
            unavailable = False

            async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
                if self.unavailable and role == "foreman":
                    raise RuntimeError("limit still exhausted")
                return await super().open_role(role, context)

            async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
                if self.unavailable and handle.role == "foreman":
                    raise RuntimeError("limit still exhausted")
                return await super().deliver_start(handle, message)

        backend = UnavailableBackend()
        broker = FakeBroker()
        orchestrator = ShopOrchestrator(backend, broker, profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
        await orchestrator.open()
        backend.unavailable = True
        await orchestrator.handle_event(
            BackendEvent(kind="role_failed", role="foreman", error="session limit")
        )

        await orchestrator.deliver(
            {"sequence": 50, "recipient": "foreman", "body": "Try again"}
        )

        self.assertEqual(broker.failures["foreman"], "limit still exhausted")
        self.assertEqual(broker.failed_deliveries, [(50, "limit still exhausted")])
        self.assertEqual(broker.recoveries, [])
        await orchestrator.close()

    async def test_backend_failure_remains_runtime_ending(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "process exited"):
            await self.orchestrator.handle_event(
                BackendEvent(kind="backend_failed", error="process exited")
            )

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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
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
            ["librarian", "machinist", "designer", "foreman"],
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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_checkout=ROOT, active_project=ROOT)
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
    def test_backend_command_overrides_are_keyed_per_backend(self) -> None:
        from floor.backends import create_backend, parse_backend_command_overrides

        overrides = parse_backend_command_overrides(("codex=/tmp/fake-codex", "claude=/tmp/fake-claude"))
        codex = create_backend("codex", cwd=Path("/tmp"), command_overrides=overrides)
        claude = create_backend("claude", cwd=Path("/tmp"), command_overrides=overrides)
        self.assertEqual(codex.command, ("/tmp/fake-codex",))
        self.assertEqual(claude.command, ("/tmp/fake-claude",))

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

    def test_retired_hermes_backend_rejected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend

        with self.assertRaisesRegex(ValueError, "unknown backend.*hermes"):
            create_backend("hermes", cwd=Path("/tmp"))


# ── ClaudeBackend acceptance tests against the fake Claude CLI fixture ─────
# The fixture proves the steer *transport* only. Whether a real model acts on
# a delivered correction is measured in the spike, not here (ADR 0009).

FAKE_CLAUDE_CLI = ROOT / "tests" / "fixtures" / "fake_claude_cli.py"


class ClaudeBackendAcceptanceTest(unittest.IsolatedAsyncioTestCase):
    """ClaudeBackend exercising AgentBackend operations through a fake CLI."""

    async def asyncSetUp(self) -> None:
        from floor.backends.claude import ClaudeBackend

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.capture = Path(self.temporary.name) / "claude.jsonl"
        self.environment = patch.dict(
            os.environ, {"FAKE_CLAUDE_CAPTURE": str(self.capture)}
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.claude = ClaudeBackend(
            ROOT,
            project=self.project,
            command=(sys.executable, str(FAKE_CLAUDE_CLI)),
            solid_command=("/work/.venv/bin/solid",),
        )
    def context(self, role: str) -> RoleContext:
        return _context(role, backend="claude", project=self.project)

    def captured(self) -> list[dict]:
        return [json.loads(line) for line in self.capture.read_text().splitlines()]

    async def test_open_role_starts_one_process_per_role(self) -> None:
        await self.claude.start()
        await self.claude.open_role("foreman", self.context("foreman"))
        await self.claude.open_role("designer", self.context("designer"))
        self.assertEqual(len(self.claude.processes), 2)
        environments = [i for i in self.captured() if i["kind"] == "environment"]
        self.assertEqual(len(environments), 2)
        for environment in environments:
            self.assertEqual(environment["cwd"], str(self.project))
            self.assertTrue(environment["floorImportable"])
        await self.claude.close()

    async def test_role_contract_is_session_level_not_a_turn(self) -> None:
        """The first user message must be a broker envelope (ADR 0009)."""
        await self.claude.start()
        await self.claude.open_role("machinist", self.context("machinist"))
        captured = self.captured()

        argv = next(i for i in captured if i["kind"] == "environment")["argv"]
        contract = argv[argv.index("--append-system-prompt") + 1]
        self.assertIn(str(ROOT / "profiles" / "fordesmac" / "machinist.md"), contract)
        self.assertIn(str(ROOT / "profiles" / "fordesmac" / "skills" / "solid-node-api" / "SKILL.md"), contract)
        self.assertIn("trusted control plane", contract)

        user_messages = [
            i for i in captured
            if i["kind"] == "message" and i["value"].get("type") == "user"
        ]
        self.assertEqual(user_messages, [], "open_role must not send a user turn")
        await self.claude.close()

    async def test_role_card_supplies_model_and_tools(self) -> None:
        await self.claude.start()
        await self.claude.open_role("machinist", self.context("machinist"))
        argv = next(i for i in self.captured() if i["kind"] == "environment")["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "sonnet")
        self.assertIn("Bash", argv[argv.index("--tools") + 1])
        self.assertIn("--safe-mode", argv)
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "bypassPermissions")
        await self.claude.close()

    async def test_manual_permission_policy_retains_confirmation_mode(self) -> None:
        context = self.context("machinist")
        context = replace(
            context,
            agent=replace(
                context.agent,
                runtime=replace(context.agent.runtime, permission="manual"),
            ),
        )
        await self.claude.start()
        await self.claude.open_role("machinist", context)
        argv = next(i for i in self.captured() if i["kind"] == "environment")["argv"]
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "manual")
        await self.claude.close()

    async def test_delivery_is_completed_under_the_minted_identifier(self) -> None:
        await self.claude.start()
        handle = await self.claude.open_role("foreman", self.context("foreman"))
        receipt = await self.claude.deliver_start(handle, "Begin")

        started = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        message = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        completed = await asyncio.wait_for(anext(self.claude.events), timeout=5)
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
        await self.claude.close()

    async def test_steering_preserves_identity_and_yields_one_completion(self) -> None:
        await self.claude.start()
        handle = await self.claude.open_role("machinist", self.context("machinist"))
        receipt = await self.claude.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual(started.kind, "turn_started")

        steered = await self.claude.deliver_steer(
            handle, receipt.delivery_id, "Also chamfer the edge."
        )
        self.assertEqual(steered.delivery_id, receipt.delivery_id)

        message = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual((message.kind, message.role), ("role_message", "machinist"))
        completed = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual(
            (completed.kind, completed.delivery_id),
            ("turn_completed", receipt.delivery_id),
        )
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(anext(self.claude.events), timeout=0.5)
        await self.claude.close()

    async def test_steer_after_completion_becomes_a_new_delivery(self) -> None:
        """No InactiveTurn: the CLI cannot report the race (ADR 0008)."""
        await self.claude.start()
        handle = await self.claude.open_role("foreman", self.context("foreman"))
        receipt = await self.claude.deliver_start(handle, "Begin")
        for _ in range(3):  # started, role_message, completed
            await asyncio.wait_for(anext(self.claude.events), timeout=5)

        steered = await self.claude.deliver_steer(
            handle, receipt.delivery_id, "A late correction."
        )
        self.assertNotEqual(steered.delivery_id, receipt.delivery_id)
        started = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual(
            (started.kind, started.delivery_id),
            ("turn_started", steered.delivery_id),
        )
        await self.claude.close()

    async def test_interrupted_turn_completes_and_does_not_fail_the_role(self) -> None:
        await self.claude.start()
        handle = await self.claude.open_role("machinist", self.context("machinist"))
        receipt = await self.claude.deliver_start(handle, "HOLD")
        await asyncio.wait_for(anext(self.claude.events), timeout=5)

        await self.claude.interrupt(handle)
        completed = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual(
            (completed.kind, completed.delivery_id),
            ("turn_completed", receipt.delivery_id),
        )
        await self.claude.close()

    async def test_one_role_process_exiting_is_a_role_failure(self) -> None:
        await self.claude.start()
        await self.claude.open_role("foreman", self.context("foreman"))
        handle = await self.claude.open_role("designer", self.context("designer"))
        self.claude.processes[handle.backend_id].terminate()

        event = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual((event.kind, event.role), ("role_failed", "designer"))
        await self.claude.close()

    async def test_partial_open_releases_already_started_processes(self) -> None:
        await self.claude.start()
        await self.claude.open_role("foreman", self.context("foreman"))
        with patch.object(
            self.claude, "_role_command", side_effect=RuntimeError("boom")
        ):
            with self.assertRaises(RuntimeError):
                await self.claude.open_role("designer", self.context("designer"))
        await self.claude.close()
        self.assertEqual(self.claude.processes, {})


class ClaudeBackendStartupFailureTest(unittest.IsolatedAsyncioTestCase):
    """A session that dies at startup must say why.

    Written after implementation, not red-first: the need surfaced only when
    the real CLI deadlocked a readiness gate and stderr had been discarded
    (design.md D8a).
    """

    async def test_startup_exit_reports_stderr(self) -> None:
        from floor.backends.claude import ClaudeBackend

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project = Path(temporary.name) / "project"
        project.mkdir()
        claude = ClaudeBackend(
            ROOT,
            project=project,
            command=(
                sys.executable,
                "-c",
                "import sys; sys.stderr.write('no such flag\\n'); sys.exit(2)",
            ),
        )
        context = _context("foreman", backend="claude", project=project)
        await claude.start()
        with self.assertRaises(RuntimeError) as caught:
            await claude.open_role("foreman", context)
        self.assertIn("exited at startup with status 2", str(caught.exception))
        self.assertIn("no such flag", str(caught.exception))
        self.assertEqual(claude.processes, {})
        await claude.close()


class ClaudeBackendShutdownTest(unittest.IsolatedAsyncioTestCase):
    """close() must release every owned process, bounded, even a stubborn one."""

    async def test_close_forces_a_process_that_ignores_sigterm(self) -> None:
        from floor.backends.claude import ClaudeBackend

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project = Path(temporary.name) / "project"
        project.mkdir()
        with patch.dict(os.environ, {"FAKE_CLAUDE_IGNORE_SIGNALS": "1"}):
            claude = ClaudeBackend(
                ROOT,
                project=project,
                command=(sys.executable, str(FAKE_CLAUDE_CLI)),
                stop_timeout=0.5,
            )
            context = _context("foreman", backend="claude", project=project)
            await claude.start()
            await claude.open_role("foreman", context)
            await claude.open_role("designer", context)
            processes = list(claude.processes.values())

            await asyncio.wait_for(claude.close(), timeout=10)
            for process in processes:
                self.assertIsNotNone(process.returncode)
            self.assertEqual(claude.processes, {})


class ClaudeBackendFlagTest(unittest.TestCase):
    def test_claude_backend_selected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend
        from floor.backends.claude import ClaudeBackend

        backend = create_backend("claude", cwd=Path("/tmp"))
        self.assertIsInstance(backend, ClaudeBackend)
