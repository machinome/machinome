# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
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
import threading
import time
from dataclasses import replace
from contextlib import redirect_stderr
from types import SimpleNamespace
from pathlib import Path
from typing import cast
from unittest.mock import patch
from urllib.request import urlopen

from floor.app import Broker
from floor.backends.base import (
    AgentActivity,
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    InactiveTurn,
    RoleContext,
    RoleHandle,
    RuntimeCatalogue,
    RuntimeChoice,
)
from floor.orchestrator import (
    LocalBrokerControl,
    ShopOrchestrator,
    _route_backend_events,
    _serve,
    _shutdown_runtime,
    _wait_for_runtime,
)
from floor.preparation import PreparationError, ProjectAgentRuntime, ProjectRuntimeSelection, prepare_project
from floor.profiles import load_profile, resolve_profile_runtime

ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
def _resolved_profile(profile_id: str, backend: str = "claude"):
    profile = load_profile(profile_id, shop_root=ROOT)
    agents = {}
    if backend != "claude":
        for agent in profile.agents:
            source = "opencode:openai:gpt-5.4"
            agents[agent.id] = ProjectAgentRuntime("opencode", "openai", "gpt-5.4", None, source)
    selection = ProjectRuntimeSelection(ROOT, ROOT / "pyproject.toml", agents)
    return resolve_profile_runtime(profile, selection)


FORDESMAC = _resolved_profile("fordesmac")


def _context(role: str, *, backend: str = "claude", project: Path | None = None) -> RoleContext:
    profile = _resolved_profile("fordesmac", backend)
    return RoleContext(
        shop_root=str(ROOT),
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
        self.system_notices: dict[str, list[dict[str, object]]] = {}
        self.delivered_system_notices: list[tuple[str, list[int]]] = []
        self.activity: list[AgentActivity] = []
        self.runtime: dict[str, object] = {}
        self.backend_idle: dict[str, bool] = {}
        self.pristine: dict[str, bool] = {agent.id: True for agent in FORDESMAC.agents}

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

    async def pending_system_notices(self, role: str) -> list[dict[str, object]]:
        return list(self.system_notices.get(role, ()))

    async def mark_system_notices_delivered(self, role: str, sequences: list[int]) -> None:
        self.delivered_system_notices.append((role, sequences))
        delivered = set(sequences)
        self.system_notices[role] = [
            notice for notice in self.system_notices.get(role, ())
            if int(notice["sequence"]) not in delivered
        ]

    async def record_activity(self, activity: AgentActivity) -> None:
        self.activity.append(activity)

    async def runtime_changed(self, role: str, runtime: object) -> None:
        self.runtime[role] = runtime

    async def backend_idle_changed(self, role: str, idle: bool) -> None:
        self.backend_idle[role] = idle

    async def runtime_idle(self, role: str) -> bool:
        return True

    async def runtime_pristine(self, role: str) -> bool:
        return self.pristine.get(role, True)

    async def mark_runtime_used(self, role: str) -> None:
        self.pristine[role] = False


class FakeMultiplexBackend:
    def __init__(self, backend_name: str = "claude") -> None:
        self.backend_name = backend_name
        self.started_threads: list[str] = []
        self.started_turns: list[tuple[str, str]] = []
        self.steered_turns: list[tuple[str, str, str]] = []
        self.interrupted: list[tuple[str, str]] = []
        self.closed: list[str] = []
        self.fail_next_steer = False
        self.accept_notices = True
        self.notice_deliveries: list[tuple[str, str, str]] = []
        self.runtime_updates: list[tuple[RoleHandle, object]] = []

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

    async def deliver_notice(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> bool:
        self.notice_deliveries.append((handle.backend_id, expected_delivery_id, message))
        return self.accept_notices

    async def interrupt(self, handle: RoleHandle) -> None:
        await self.interrupt_turn(handle.backend_id, handle.backend_id)

    async def close_role(self, handle: RoleHandle) -> None:
        self.closed.append(handle.backend_id)

    async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
        claude = self.backend_name == "claude"
        model = "opus" if claude else "gpt-5.4"
        provider = None if claude else "openai"
        return RuntimeCatalogue(
            supported=True,
            choices=(RuntimeChoice(model, ("medium", "high"), self.backend_name, provider),),
        )

    async def update_runtime(self, handle: RoleHandle, runtime: object) -> None:
        self.runtime_updates.append((handle, runtime))

    # Events — the fake doesn't emit events; tests call handle_notification
    # directly.  Provide a dummy async iterator for the protocol.
    async def _empty_events(self):
        while True:
            await __import__("asyncio").sleep(3600)
            yield  # type: ignore[misc]

    events = property(lambda self: self._empty_events())


class ShopOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.backend = FakeMultiplexBackend()
        self.broker = FakeBroker()
        self.orchestrator = ShopOrchestrator(self.backend, self.broker, profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
        await self.orchestrator.open()

    async def test_open_owns_exactly_the_three_role_threads(self) -> None:
        self.assertEqual(self.backend.started_threads, ["foreman", "designer", "machinist", "librarian"])
        self.assertEqual([role for role, _ in self.broker.manifested], self.backend.started_threads)

    async def test_idle_delivery_starts_and_active_delivery_steers_the_same_owner(self) -> None:
        await self.orchestrator.deliver({"sequence": 10, "recipient": "designer", "body": "First"})
        runtime = self.orchestrator.roles["designer"]
        self.assertIn("instruction:\nFirst", self.backend.started_turns[0][1])
        self.assertEqual(runtime.active_delivery_id, "turn-1")

        await self.orchestrator.deliver({"sequence": 11, "recipient": "designer", "body": "Second"})
        self.assertEqual(self.backend.steered_turns[0][0:2], ("thread-designer", "turn-1"))
        self.assertIn("instruction:\nSecond", self.backend.steered_turns[0][2])
        self.assertEqual(self.broker.delivered, [10, 11])

    def test_assignment_delivery_makes_the_floor_acknowledgement_tool_the_first_call(self) -> None:
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
        self.assertIn('floor_acknowledge(role="machinist", assignment="build-1")', message)
        self.assertNotIn("python -m floor.agent acknowledge", message)
        self.assertIn("Do not read files or investigate", message)

    def test_every_selectable_backend_acknowledges_through_the_floor_tool(self) -> None:
        for backend in ("claude", "opencode"):
            with self.subTest(backend=backend):
                orchestrator = ShopOrchestrator(
                    self.backend,
                    self.broker,
                    profile=_resolved_profile("fordesmac", backend),
                    shop_root=ROOT,
                    active_project=ROOT,
                )
                message = orchestrator._message(
                    {
                        "sequence": 10,
                        "kind": "assignment",
                        "recipient": "machinist",
                        "assignment_id": "build-1",
                        "body": "Build the released drawing.",
                    }
                )

                self.assertIn(
                    'floor_acknowledge(role="machinist", assignment="build-1")',
                    message,
                )
                self.assertNotIn("python -m floor.agent acknowledge", message)

    async def test_completion_race_restarts_the_still_unacknowledged_envelope(self) -> None:
        await self.orchestrator.deliver({"sequence": 12, "recipient": "machinist", "body": "Build"})
        self.backend.fail_next_steer = True
        await self.orchestrator.deliver({"sequence": 13, "recipient": "machinist", "body": "Correction"})
        self.assertEqual(self.backend.started_turns[-1][0], "thread-machinist")
        self.assertIn("instruction:\nCorrection", self.backend.started_turns[-1][1])
        self.assertEqual(self.broker.delivered[-1], 13)

    async def test_notice_steers_a_continuing_turn_without_starting_or_changing_work(self) -> None:
        await self.orchestrator.deliver({"sequence": 20, "recipient": "designer", "body": "First"})
        self.broker.system_notices["designer"] = [
            {"sequence": 1, "kind": "user_file_changed", "path": "root/plate.py", "revision": "new"}
        ]
        started = len(self.backend.started_turns)

        await self.orchestrator.deliver_pending_notices("designer")

        self.assertEqual(len(self.backend.started_turns), started)
        self.assertIn("kind: user_file_changed", self.backend.notice_deliveries[-1][2])
        self.assertEqual(self.broker.delivered_system_notices, [("designer", [1])])

    async def test_unaccepted_notice_waits_for_the_next_ordinary_delivery(self) -> None:
        await self.orchestrator.deliver({"sequence": 21, "recipient": "designer", "body": "First"})
        self.broker.system_notices["designer"] = [
            {"sequence": 2, "kind": "user_file_changed", "path": "root/plate.py", "revision": "new"}
        ]
        self.backend.accept_notices = False
        started = len(self.backend.started_turns)

        await self.orchestrator.deliver_pending_notices("designer")
        self.assertEqual(len(self.backend.started_turns), started)
        self.assertEqual(self.broker.delivered_system_notices, [])

        await self.orchestrator.handle_event(
            BackendEvent(kind="turn_completed", role="designer", delivery_id="turn-1")
        )
        await self.orchestrator.deliver({"sequence": 22, "recipient": "designer", "body": "Continue"})

        self.assertEqual(len(self.backend.started_turns), started + 1)
        self.assertIn("kind: user_file_changed", self.backend.started_turns[-1][1])
        self.assertIn("instruction:\nContinue", self.backend.started_turns[-1][1])
        self.assertEqual(self.broker.delivered_system_notices, [("designer", [2])])

    async def test_standby_does_not_start_or_steer_a_turn_and_close_interrupts_active_work(self) -> None:
        self.assertEqual(self.backend.started_turns, [])
        self.assertEqual(self.backend.steered_turns, [])
        await self.orchestrator.deliver({"sequence": 14, "recipient": "foreman", "body": "Work"})
        await self.orchestrator.close()
        self.assertEqual(self.backend.interrupted, [("thread-foreman", "thread-foreman")])
        self.assertEqual(self.backend.closed, ["thread-librarian", "thread-machinist", "thread-designer", "thread-foreman"])

    async def test_completed_foreman_message_is_published_to_the_maker_conversation(self) -> None:
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="foreman", text="Hello from Foreman.")
        )
        await self.orchestrator.handle_event(
            BackendEvent(kind="role_message", role="designer", text="Internal specialist output.")
        )
        self.assertEqual(self.broker.conversation, [("foreman", "Hello from Foreman.")])

    async def test_idle_runtime_update_preserves_backend_and_changes_model_and_reasoning_together(self) -> None:
        current = self.orchestrator.current_runtime("designer")
        changed = replace(current, model="opus", effort="high")

        catalogue = await self.orchestrator.runtime_catalog("designer")
        applied = await self.orchestrator.update_runtime("designer", changed)

        self.assertTrue(catalogue.supported)
        self.assertEqual(applied, changed)
        self.assertEqual(self.orchestrator.roles["designer"].handle.backend_id, "thread-designer")
        self.assertEqual(self.backend.runtime_updates[-1][1], changed)

    async def test_active_native_delivery_rejects_runtime_update(self) -> None:
        await self.orchestrator.deliver({"sequence": 44, "recipient": "designer", "body": "work"})
        changed = replace(self.orchestrator.current_runtime("designer"), model="opus")

        with self.assertRaisesRegex(RuntimeError, "not idle"):
            await self.orchestrator.update_runtime("designer", changed)

        self.assertEqual(self.backend.runtime_updates, [])

    async def test_failed_persistence_commit_rolls_back_before_runtime_is_published(self) -> None:
        current = self.orchestrator.current_runtime("designer")
        changed = replace(current, model="opus", effort="high")

        with self.assertRaisesRegex(RuntimeError, "stale project config"):
            await self.orchestrator.update_runtime(
                "designer",
                changed,
                commit=lambda: (_ for _ in ()).throw(RuntimeError("stale project config")),
            )

        self.assertEqual(self.orchestrator.current_runtime("designer"), current)
        self.assertEqual([item[1] for item in self.backend.runtime_updates], [changed, current])
        self.assertEqual(self.broker.runtime["designer"], current)

    async def test_pristine_backend_change_replaces_unused_handle_without_migration(self) -> None:
        opencode = FakeMultiplexBackend("opencode")
        async def resolve_backend(name: str) -> AgentBackend:
            self.assertEqual(name, "opencode")
            return cast(AgentBackend, opencode)
        self.orchestrator.backend_resolver = resolve_backend
        current = self.orchestrator.current_runtime("designer")
        requested = replace(
            FORDESMAC.agent("designer").backends["claude"],
            model="gpt-5.4",
            effort="high",
            backend="opencode",
            provider="openai",
        )

        applied = await self.orchestrator.update_runtime("designer", requested)

        self.assertEqual(applied, requested)
        self.assertEqual(self.orchestrator.current_runtime("designer"), requested)
        self.assertEqual(opencode.started_threads, ["designer"])
        self.assertIn("thread-designer", self.backend.closed)
        self.assertIs(self.orchestrator.backends_by_agent["designer"], opencode)
        self.assertEqual(current.backend, "claude")

    async def test_used_role_rejects_backend_change_even_after_it_is_idle(self) -> None:
        self.broker.pristine["designer"] = False
        requested = replace(
            FORDESMAC.agent("designer").backends["claude"],
            model="gpt-5.4",
            backend="opencode",
            provider="openai",
        )

        with self.assertRaisesRegex(ValueError, "first use"):
            await self.orchestrator.update_runtime("designer", requested)

    async def test_failed_pristine_replacement_commit_keeps_old_owner_and_handle(self) -> None:
        opencode = FakeMultiplexBackend("opencode")
        async def resolve_backend(_name: str) -> AgentBackend:
            return cast(AgentBackend, opencode)
        self.orchestrator.backend_resolver = resolve_backend
        current = self.orchestrator.current_runtime("designer")
        old_handle = self.orchestrator.roles["designer"].handle
        requested = replace(
            FORDESMAC.agent("designer").backends["claude"],
            model="gpt-5.4",
            effort="high",
            backend="opencode",
            provider="openai",
        )

        with self.assertRaisesRegex(RuntimeError, "stale project config"):
            await self.orchestrator.update_runtime(
                "designer", requested,
                commit=lambda: (_ for _ in ()).throw(RuntimeError("stale project config")),
            )

        self.assertEqual(self.orchestrator.current_runtime("designer"), current)
        self.assertIs(self.orchestrator.roles["designer"].handle, old_handle)
        self.assertIs(self.orchestrator.backends_by_agent["designer"], self.backend)
        self.assertEqual(opencode.closed, ["thread-designer"])
        self.assertNotIn("thread-designer", self.backend.closed)

    async def test_backend_activity_is_forwarded_without_native_protocol_data(self) -> None:
        activity = AgentActivity(
            id="activity-1", role="designer", category="tool", state="completed",
            name="read_file", summary="parts/bracket.py", detail="168 lines",
        )

        await self.orchestrator.handle_event(BackendEvent(kind="activity", role="designer", activity=activity))

        self.assertEqual(self.broker.activity, [activity])


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
        primary, claude = CountingBackend(), CountingBackend()
        orchestrator = ShopOrchestrator(
            {
                "foreman": primary,
                "designer": claude,
                "machinist": primary,
                "librarian": primary,
            },
            FakeBroker(),
            profile=profile,
            shop_root=ROOT,
            active_project=ROOT,
        )

        await orchestrator.open()
        self.assertTrue(primary.started)
        self.assertTrue(claude.started)
        self.assertEqual([role for role, _ in primary.opened_roles], ["foreman", "machinist", "librarian"])
        self.assertEqual([role for role, _ in claude.opened_roles], ["designer"])
        await orchestrator.close()
        self.assertEqual([handle.role for handle in primary.closed_roles], ["librarian", "machinist", "foreman"])
        self.assertEqual([handle.role for handle in claude.closed_roles], ["designer"])
        self.assertTrue(primary.closed)
        self.assertTrue(claude.closed)
        self.assertEqual((primary.start_count, claude.start_count), (1, 1))
        self.assertEqual((primary.close_count, claude.close_count), (1, 1))

    async def test_later_backend_start_failure_closes_every_backend(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend

        class FailingStartBackend(FakeBackend):
            async def start(self) -> None:
                raise RuntimeError("second backend failed")

        first, second = FakeBackend(), FailingStartBackend()
        orchestrator = ShopOrchestrator(
            {agent.id: (second if agent.id == "designer" else first) for agent in FORDESMAC.agents},
            FakeBroker(), profile=FORDESMAC, shop_root=ROOT, active_project=ROOT,
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

        opencode, claude = QueueBackend(), QueueBackend()
        profile = FORDESMAC
        orchestrator = RecordingOrchestrator(
            {agent.id: (claude if agent.id == "designer" else opencode) for agent in profile.agents},
            FakeBroker(), profile=profile, shop_root=ROOT, active_project=ROOT,
        )
        tasks = [
            asyncio.create_task(_route_backend_events(orchestrator, backend))
            for backend in (opencode, claude)
        ]
        self.addAsyncCleanup(lambda: [task.cancel() for task in tasks])
        await opencode.queue.put(BackendEvent(kind="role_message", role="foreman", text="from opencode"))
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

        class RacingBackend(FakeMultiplexBackend):
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

        racing = RacingBackend()
        orchestrator = ShopOrchestrator(
            cast(AgentBackend, racing),
            LocalBrokerControl(broker),
            profile=profile,
            shop_root=ROOT,
            active_project=ROOT,
        )
        racing.orchestrator = orchestrator
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

        class RacingBackend(FakeMultiplexBackend):
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

        racing = RacingBackend()
        orchestrator = ShopOrchestrator(
            cast(AgentBackend, racing),
            LocalBrokerControl(broker),
            profile=profile,
            shop_root=ROOT,
            active_project=ROOT,
        )
        racing.orchestrator = orchestrator
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
            shop_root=ROOT,
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
        backend = FakeMultiplexBackend()
        broker = FakeBroker()
        orchestrator = ShopOrchestrator(backend, broker, profile=profile, shop_root=ROOT, active_project=ROOT)
        await orchestrator.open()
        self.addAsyncCleanup(orchestrator.close)
        self.assertEqual(backend.started_threads, ["foreman", "designer", "machinist", "librarian"])
        await orchestrator.handle_event(BackendEvent(kind="role_message", role="designer", text="Internal"))
        await orchestrator.handle_event(BackendEvent(kind="role_message", role="foreman", text="Public"))
        self.assertEqual(broker.conversation, [("foreman", "Public")])

    async def test_direct_turn_events_update_the_builder_broker_without_assignment_ids(self) -> None:
        profile = _resolved_profile("builder")
        broker = Broker(profile=profile)
        backend = FakeMultiplexBackend()
        orchestrator = ShopOrchestrator(backend, LocalBrokerControl(broker), profile=profile, shop_root=ROOT, active_project=ROOT)
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
        backend = FakeMultiplexBackend()
        orchestrator = ShopOrchestrator(backend, LocalBrokerControl(broker), profile=profile, shop_root=ROOT, active_project=ROOT)
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


class BrokerPipelineRoutingTest(unittest.IsolatedAsyncioTestCase):
    async def test_broker_routes_maker_specialist_and_parallel_pipeline_messages(self) -> None:
        broker = Broker(FORDESMAC)
        backend = FakeMultiplexBackend()
        orchestrator = ShopOrchestrator(backend, LocalBrokerControl(broker), profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
    def test_one_sigint_closes_with_a_live_sse_client(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project_home = Path(temporary.name) / "projects"
        project_home.mkdir()
        launch_directory = Path(temporary.name) / "not-a-git-repository"
        launch_directory.mkdir()
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
                "--projects-dir",
                str(project_home),
                "--solid-command",
                str(FAKE_SOLID),
            ],
            cwd=launch_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
            env={
                **os.environ,
                "PYTHONPATH": str(ROOT),
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


class SessionOpeningTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        from floor.sessions import SessionRegistry
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "projects"
        self.home.mkdir()
        self.project = self.home / "engine"
        (self.project / "root").mkdir(parents=True)
        (self.project / "root" / "__init__.py").write_text("# model\n")
        (self.project / ".gitignore").write_text("_build/\n.fake-solid-builds\n")
        (self.project / "pyproject.toml").write_text('[tool.libresolid-studio]\nprofile = "builder"\n')
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.project)], check=True)
        subprocess.run(["git", "-C", str(self.project), "add", "--all"], check=True)
        subprocess.run([
            "git", "-C", str(self.project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "fixture",
        ], check=True)
        self.backends = []

        def factory(*_args, **_kwargs):
            from tests.fixtures.fake_backend import FakeBackend
            backend = FakeBackend()
            self.backends.append((_kwargs, backend))
            return backend

        self.registry = SessionRegistry(
            self.home,
            shop_root=ROOT,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            backend_factory=factory,
        )
        self.addAsyncCleanup(self.registry.close_all)

    async def test_open_resolves_prepares_builds_and_starts_agents_inside_one_session(self) -> None:
        await self.registry.request_open("engine")
        session = await self.registry.wait_until_settled("engine")
        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(session.profile.id, "builder")
        self.assertEqual(list(session.broker.agents), ["builder"])
        self.assertNotEqual(session.id, session.name)
        self.assertEqual(self.backends[0][0]["session_id"], session.id)

    async def test_a_backend_is_built_with_every_skill_its_profile_allowlists(self) -> None:
        await self.registry.request_open("engine")
        session = await self.registry.wait_until_settled("engine")
        assert session is not None
        expected = {
            skill.name: skill.path
            for agent in session.profile.agents
            for skill in agent.skills
        }
        self.assertTrue(expected, "the builder profile allowlists skills")
        self.assertEqual(
            {skill.name: skill.path for skill in self.backends[0][0]["skills"]},
            expected,
        )

    async def test_pristine_catalogue_lazily_registers_optional_backend_owners(self) -> None:
        await self.registry.request_open("engine")
        session = await self.registry.wait_until_settled("engine")
        assert session is not None
        self.assertEqual(len(self.backends), 1)

        catalogue = await session.runtime_catalog("builder")

        self.assertTrue(catalogue["runtime_pristine"])
        self.assertEqual(len(self.backends), 2)
        self.assertEqual(len(session.orchestrator.backends), 2)
        self.assertEqual(len(session.event_tasks), 2)

    async def test_creation_is_visible_as_a_provisional_project_until_its_directory_exists(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def slow_prepare(*args, **kwargs):
            started.set()
            if not release.wait(timeout=5):
                raise TimeoutError("test did not release project preparation")
            return prepare_project(*args, **kwargs)

        subscriber, _snapshot = await self.registry.subscribe_hub()
        try:
            with patch("floor.sessions.prepare_project", side_effect=slow_prepare):
                response = await self.registry.create("new_project", "builder")
                self.assertEqual(response, {"state": "opening"})
                self.assertTrue(await asyncio.to_thread(started.wait, 2))

                event = await asyncio.wait_for(subscriber.get(), timeout=2)
                self.assertEqual(event, {"kind": "creating", "project": "new_project", "profile": "builder"})
                projects = {item["name"]: item for item in await self.registry.projects()}
                self.assertEqual(projects["new_project"]["state"], "creating")
                self.assertEqual(projects["new_project"]["profile"], "builder")
                self.assertFalse((self.home / "new_project").exists())

                release.set()
                self.assertIsNotNone(await self.registry.wait_until_settled("new_project"))
        finally:
            release.set()
            self.registry.unsubscribe_hub(subscriber)

    async def test_profile_failure_is_fatal_before_preparation_and_leaves_no_session(self) -> None:
        (self.project / "pyproject.toml").write_text('[tool.libresolid-studio]\nprofile = "missing-profile"\n')
        with patch("floor.sessions.prepare_project") as prepare:
            await self.registry.request_open("engine")
            self.assertIsNone(await self.registry.wait_until_settled("engine"))
        prepare.assert_not_called()
        self.assertIsNone(self.registry.by_project("engine"))
        self.assertIn("cannot be loaded", self.registry._failures["engine"])

    async def test_preparation_and_agent_start_failures_leave_no_partial_session(self) -> None:
        failure = PreparationError("repository", "engine", self.project, "broken")
        with patch("floor.sessions.prepare_project", side_effect=failure):
            await self.registry.request_open("engine")
            self.assertIsNone(await self.registry.wait_until_settled("engine"))
        self.assertIsNone(self.registry.by_project("engine"))

        class BrokenBackend:
            events = _empty_events()

            async def start(self):
                raise RuntimeError("backend start failed")

            async def close(self):
                return None

        self.registry.backend_factory = lambda *_args, **_kwargs: BrokenBackend()
        await self.registry.request_open("engine")
        self.assertIsNone(await self.registry.wait_until_settled("engine"))
        self.assertIsNone(self.registry.by_project("engine"))
        self.assertIn("backend start failed", self.registry._failures["engine"])


async def _empty_events():
    if False:
        yield None


# ── AgentBackend protocol acceptance tests ─────────────────────────────────
# These tests use the portable AgentBackend protocol and a FakeBackend
# fixture, independently of any concrete backend adapter.


class FakeBackendOrchestratorTest(unittest.IsolatedAsyncioTestCase):
    """Orchestrator acceptance through the portable AgentBackend protocol."""

    async def asyncSetUp(self) -> None:
        from tests.fixtures.fake_backend import FakeBackend as FB

        self.backend = FB()
        self.broker = FakeBroker()
        self.orchestrator = ShopOrchestrator(self.backend, self.broker, profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
        orchestrator = ShopOrchestrator(backend, broker, profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
        orchestrator = ShopOrchestrator(backend, broker, profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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
        orchestrator = ShopOrchestrator(backend, FakeBroker(), profile=FORDESMAC, shop_root=ROOT, active_project=ROOT)
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

        overrides = parse_backend_command_overrides(("opencode=/tmp/fake-opencode", "claude=/tmp/fake-claude"))
        opencode = create_backend("opencode", shop_root=Path("/tmp"), command_overrides=overrides)
        claude = create_backend("claude", shop_root=Path("/tmp"), command_overrides=overrides)
        self.assertEqual(opencode.command, ("/tmp/fake-opencode",))
        self.assertEqual(claude.command, ("/tmp/fake-claude",))

    def test_a_shared_tool_server_is_built_with_the_profiles_skills(self) -> None:
        from floor.backends import create_backend

        skills = FORDESMAC.agent("machinist").skills
        self.assertTrue(skills)
        opencode = create_backend("opencode", shop_root=ROOT, skills=skills)
        self.assertEqual(opencode.skills, {skill.name: skill.path for skill in skills})
        # Claude configures a tool server per role, so it registers each
        # agent's own skills from its role context instead.
        create_backend("claude", shop_root=ROOT, skills=skills)

    def test_unknown_backend_rejected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend

        with self.assertRaises(ValueError) as cm:
            create_backend("unknown", shop_root=Path("/tmp"))
        self.assertIn("unknown", str(cm.exception))

    def test_retired_backends_rejected(self) -> None:
        from pathlib import Path
        from floor.backends import create_backend

        for retired in ("hermes", "codex"):
            with self.subTest(backend=retired):
                with self.assertRaisesRegex(ValueError, f"unknown backend.*{retired}"):
                    create_backend(retired, shop_root=Path("/tmp"))


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
            session_id="opaque-session",
        )
    def context(self, role: str) -> RoleContext:
        return _context(role, backend="claude", project=self.project)

    def captured(self) -> list[dict]:
        return [json.loads(line) for line in self.capture.read_text().splitlines()]

    async def test_runtime_control_is_read_only_because_context_cannot_be_preserved(self) -> None:
        catalogue = await self.claude.runtime_catalog(RoleHandle("not-opened", "designer"))
        self.assertFalse(catalogue.supported)
        self.assertIn("cannot preserve", catalogue.reason)
        with self.assertRaisesRegex(RuntimeError, "cannot preserve"):
            await self.claude.update_runtime(
                RoleHandle("not-opened", "designer"),
                self.context("designer").agent.runtime,
            )

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
            self.assertEqual(environment["floor_session"], "opaque-session")
        await self.claude.close()

    async def test_role_contract_is_session_level_not_a_turn(self) -> None:
        """The first user message must be a broker envelope (ADR 0009)."""
        await self.claude.start()
        await self.claude.open_role("machinist", self.context("machinist"))
        captured = self.captured()

        argv = next(i for i in captured if i["kind"] == "environment")["argv"]
        contract = argv[argv.index("--append-system-prompt") + 1]
        self.assertIn(str(ROOT / "profiles" / "fordesmac" / "machinist.md"), contract)
        self.assertIn("trusted control plane", contract)

        user_messages = [
            i for i in captured
            if i["kind"] == "message" and i["value"].get("type") == "user"
        ]
        self.assertEqual(user_messages, [], "open_role must not send a user turn")
        await self.claude.close()

    async def test_role_card_supplies_model_and_scoped_mcp_tools(self) -> None:
        await self.claude.start()
        await self.claude.open_role("machinist", self.context("machinist"))
        argv = next(i for i in self.captured() if i["kind"] == "environment")["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "sonnet")
        tools = argv[argv.index("--tools") + 1]
        self.assertIn("mcp__floor__read_file", tools)
        self.assertIn("mcp__floor__solid_build", tools)
        self.assertNotIn("Bash", tools)
        self.assertNotIn("--safe-mode", argv)
        self.assertIn("--strict-mcp-config", argv)
        config = json.loads(Path(argv[argv.index("--mcp-config") + 1]).read_text())
        server = config["mcpServers"]["floor"]
        self.assertEqual(server["command"], sys.executable)
        self.assertIn(str(self.project), server["args"])
        self.assertEqual(
            server["args"][server["args"].index("--floor-session") + 1],
            "opaque-session",
        )
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "bypassPermissions")
        await self.claude.close()

    async def test_a_role_is_announced_its_own_skills_and_can_load_them(self) -> None:
        await self.claude.start()
        await self.claude.open_role("machinist", self.context("machinist"))
        environment = next(i for i in self.captured() if i["kind"] == "environment")
        argv = environment["argv"]
        contract = argv[argv.index("--append-system-prompt") + 1]

        machinist = FORDESMAC.agent("machinist")
        for skill in machinist.skills:
            self.assertIn(skill.name, contract)
            self.assertIn(skill.description, contract)
            self.assertNotIn(str(skill.path), contract)
            self.assertNotIn((skill.path / "SKILL.md").read_text(), contract)
        self.assertIn("load_skill", contract)

        self.assertIn("mcp__floor__load_skill", argv[argv.index("--tools") + 1])
        server = json.loads(Path(argv[argv.index("--mcp-config") + 1]).read_text())["mcpServers"]["floor"]
        registry = json.loads(server["args"][server["args"].index("--skills-json") + 1])
        self.assertEqual(
            registry,
            {skill.name: str(skill.path.resolve()) for skill in machinist.skills},
        )
        await self.claude.close()

    async def test_a_role_holding_no_skill_is_offered_no_skill_loading(self) -> None:
        await self.claude.start()
        await self.claude.open_role("foreman", self.context("foreman"))
        argv = next(i for i in self.captured() if i["kind"] == "environment")["argv"]
        self.assertEqual(FORDESMAC.agent("foreman").skills, ())
        self.assertNotIn("load_skill", argv[argv.index("--append-system-prompt") + 1])
        self.assertNotIn("load_skill", argv[argv.index("--tools") + 1])
        server = json.loads(Path(argv[argv.index("--mcp-config") + 1]).read_text())["mcpServers"]["floor"]
        self.assertNotIn("--skills-json", server["args"])
        await self.claude.close()

    async def test_first_delivery_waits_through_pending_mcp_until_connected(self) -> None:
        from floor.backends.claude import ClaudeBackend

        await self.claude.close()
        self.claude = ClaudeBackend(
            ROOT,
            project=self.project,
            command=(sys.executable, str(FAKE_CLAUDE_CLI)),
            solid_command=("/work/.venv/bin/solid",),
            session_id="opaque-session",
            startup_grace=0.05,
            mcp_readiness_timeout=0.5,
        )
        with patch.dict(os.environ, {"FAKE_CLAUDE_MCP_PENDING_DELAY": "0.15"}):
            await self.claude.start()
            handle = await self.claude.open_role("foreman", self.context("foreman"))
            receipt = await self.claude.deliver_start(handle, "Begin")

        self.assertEqual(handle.role, "foreman")
        self.assertIn(handle.backend_id, self.claude.processes)
        started = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        message = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        completed = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual((started.kind, started.delivery_id), ("turn_started", receipt.delivery_id))
        self.assertEqual((message.kind, message.text), ("role_message", "FAKE_REPLY"))
        self.assertEqual((completed.kind, completed.delivery_id), ("turn_completed", receipt.delivery_id))
        await self.claude.close()

    async def test_first_delivery_reports_last_pending_status_on_readiness_timeout(self) -> None:
        from floor.backends.claude import ClaudeBackend

        await self.claude.close()
        self.claude = ClaudeBackend(
            ROOT,
            project=self.project,
            command=(sys.executable, str(FAKE_CLAUDE_CLI)),
            session_id="opaque-session",
            startup_grace=0.01,
            mcp_readiness_timeout=0.05,
        )
        with patch.dict(os.environ, {"FAKE_CLAUDE_MCP_PENDING_DELAY": "0.2"}):
            await self.claude.start()
            handle = await self.claude.open_role("foreman", self.context("foreman"))
            with self.assertRaisesRegex(RuntimeError, "last status: pending"):
                await self.claude.deliver_start(handle, "Begin")
        self.assertEqual(self.claude.processes, {})

    async def test_first_delivery_fails_immediately_on_terminal_mcp_status(self) -> None:
        with patch.dict(os.environ, {"FAKE_CLAUDE_MCP_FINAL_STATUS": "failed"}):
            await self.claude.start()
            handle = await self.claude.open_role("foreman", self.context("foreman"))
            with self.assertRaisesRegex(RuntimeError, "status is 'failed'"):
                await self.claude.deliver_start(handle, "Begin")
        self.assertEqual(self.claude.processes, {})

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
        activity = await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertEqual(
            (activity.kind, activity.activity.category, activity.activity.state),
            ("activity", "tool", "completed"),
        )
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(anext(self.claude.events), timeout=0.5)

    async def test_notice_never_starts_a_completed_claude_delivery(self) -> None:
        await self.claude.start()
        handle = await self.claude.open_role("machinist", self.context("machinist"))
        receipt = await self.claude.deliver_start(handle, "HOLD")
        await asyncio.wait_for(anext(self.claude.events), timeout=5)
        self.assertTrue(await self.claude.deliver_notice(handle, receipt.delivery_id, "Notice"))
        await asyncio.wait_for(anext(self.claude.events), timeout=5)
        await asyncio.wait_for(anext(self.claude.events), timeout=5)
        messages = len([item for item in self.captured() if item["kind"] == "message"])

        self.assertFalse(await self.claude.deliver_notice(handle, receipt.delivery_id, "Too late"))
        self.assertEqual(len([item for item in self.captured() if item["kind"] == "message"]), messages)
        await self.claude.close()
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

        backend = create_backend("claude", shop_root=Path("/tmp"))
        self.assertIsInstance(backend, ClaudeBackend)
