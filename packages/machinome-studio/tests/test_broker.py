from __future__ import annotations

import asyncio
from datetime import datetime
import unittest

from floor.app import Broker
from floor.backends.base import AgentActivity
from floor.profiles import load_profile


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


class BrokerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.broker = Broker(load_profile("fordesmac", shop_root=ROOT), event_history_limit=20)
        for agent in self.broker.profile.agents:
            self.broker.manifest(agent.id, agent.label)

    async def test_direction_and_reports_are_ordered_and_delivery_is_explicit(self) -> None:
        first = self.broker.send("direction", "foreman", "designer", "Start the first drawing.")
        second = self.broker.send("direction", "foreman", "designer", "Use a 6 mm wall.")
        report = self.broker.send("report", "designer", "foreman", "Drawing released.")

        self.assertEqual([item.sequence for item in self.broker.pending_for("designer")], [first.sequence, second.sequence])
        self.assertEqual([item.sequence for item in self.broker.pending_for("foreman")], [report.sequence])
        self.broker.mark_delivered(first.sequence)
        self.assertEqual([item.sequence for item in self.broker.pending_for("designer")], [second.sequence])
        self.assertEqual(self.broker.agents["designer"].state, "waiting", "direction must not mutate work state")

    async def test_unknown_and_retired_roles_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown agent"):
            self.broker.send("direction", "foreman", "drawing-office", "legacy")
        with self.assertRaisesRegex(ValueError, "unknown agent"):
            self.broker.manifest("drawing-office", "Drawing office")

    async def test_one_assignment_is_current_and_later_work_waits(self) -> None:
        first = self.broker.assign("designer", "drawing-1")
        second = self.broker.assign("designer", "drawing-2")
        agent = self.broker.agents["designer"]

        self.assertEqual(agent.assignment_id, "drawing-1")
        self.assertEqual(agent.pending_assignments, ["drawing-2"])
        self.assertEqual([item.sequence for item in self.broker.pending_for("designer")], [first.sequence])

        self.broker.acknowledge("designer", "drawing-1")
        self.assertEqual(agent.state, "active")
        self.broker.complete("designer", "drawing-1")
        self.assertEqual(agent.state, "waiting")
        self.assertEqual(agent.assignment_id, "drawing-2")
        self.assertEqual(agent.pending_assignments, [])
        self.assertEqual([item.sequence for item in self.broker.pending_for("designer")], [first.sequence, second.sequence])

    async def test_subscriber_queue_is_signal_driven_and_history_is_bounded(self) -> None:
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self.broker.subscribers.add(subscriber)
        try:
            envelope = self.broker.send("direction", "foreman", "machinist", "Hold position.")
            live = await asyncio.wait_for(subscriber.get(), timeout=0.1)
        finally:
            self.broker.subscribers.discard(subscriber)
        self.assertEqual(live["event"]["envelope_sequence"], envelope.sequence)

        for index in range(25):
            self.broker.publish("test_event", {"role": "foreman", "body": f"private-{index}"})
        snapshot = self.broker.run()
        self.assertEqual(len(snapshot["events"]), 20)
        self.assertNotIn("private-24", str(snapshot["events"]), "display history must exclude message bodies")

    async def test_event_snapshots_and_live_events_include_utc_publication_timestamps(self) -> None:
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self.broker.subscribers.add(subscriber)
        self.broker.publish("test_event", {"role": "foreman"})
        live_event = await asyncio.wait_for(subscriber.get(), timeout=0.1)
        self.broker.subscribers.discard(subscriber)
        snapshot_event = self.broker.run()["events"][-1]

        self.assertEqual(snapshot_event["timestamp"], live_event["event"]["timestamp"])
        recorded = datetime.fromisoformat(str(snapshot_event["timestamp"]).replace("Z", "+00:00"))
        self.assertIsNotNone(recorded.tzinfo)
        self.assertEqual(recorded.utcoffset().total_seconds(), 0)

    async def test_activity_updates_replace_by_role_and_id_and_history_is_bounded(self) -> None:
        first = AgentActivity(
            "tool-1", "designer", "tool", "running", "solid_test", "tests/test_plate.py"
        )
        self.broker.record_activity(first)
        completed = AgentActivity(
            "tool-1", "designer", "tool", "completed", "solid_test", "8 passed"
        )
        self.broker.record_activity(completed)

        matching = [item for item in self.broker.run()["activity"] if item["id"] == "tool-1"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["state"], "completed")
        self.assertRegex(str(matching[0]["timestamp"]), r"Z$")

        for index in range(405):
            self.broker.record_activity(AgentActivity(
                f"message-{index}", "foreman", "message", "completed", "message", str(index)
            ))
        self.assertEqual(len(self.broker.run()["activity"]), 400)

    async def test_role_failure_and_recovery_are_live_snapshot_state_without_completing_work(self) -> None:
        self.broker.assign("designer", "drawing-1")
        self.broker.acknowledge("designer", "drawing-1")
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self.broker.subscribers.add(subscriber)

        failed = self.broker.role_failed("designer", "session limit resets at 13:00 UTC")
        failure_event = await asyncio.wait_for(subscriber.get(), timeout=0.1)

        self.assertEqual(failed.state, "active")
        self.assertEqual(failed.failure, "session limit resets at 13:00 UTC")
        self.assertEqual(failure_event["kind"], "agent_failed")
        self.assertEqual(failure_event["payload"], failed.browser_value())
        snapshot_agent = next(agent for agent in self.broker.run()["agents"] if agent["role"] == "designer")
        self.assertEqual(snapshot_agent["failure"], "session limit resets at 13:00 UTC")

        recovered = self.broker.role_recovered("designer")
        recovery_event = await asyncio.wait_for(subscriber.get(), timeout=0.1)
        self.broker.subscribers.discard(subscriber)

        self.assertEqual(recovered.state, "active")
        self.assertEqual(recovered.failure, "")
        self.assertEqual(recovery_event["kind"], "agent_recovered")
        self.assertEqual(recovery_event["payload"], recovered.browser_value())

    async def test_maker_file_notices_snapshot_active_roles_and_coalesce_by_path(self) -> None:
        self.broker.assign("designer", "drawing-1")
        self.broker.acknowledge("designer", "drawing-1")
        conversation_before = list(self.broker.conversation)

        first = self.broker.queue_user_file_changed("root/plate.py", "revision-1")
        second = self.broker.queue_user_file_changed("root/plate.py", "revision-2")

        self.assertEqual([notice.recipient for notice in first], ["designer"])
        self.assertEqual([notice.recipient for notice in second], ["designer"])
        pending = self.broker.pending_system_notices("designer")
        self.assertEqual(len(pending), 1)
        self.assertEqual((pending[0].path, pending[0].revision), ("root/plate.py", "revision-2"))
        self.assertEqual(self.broker.pending_system_notices("foreman"), [])
        self.assertEqual(self.broker.conversation, conversation_before)
        self.assertEqual(self.broker.agents["designer"].state, "active")

        self.broker.mark_system_notices_delivered("designer", [pending[0].sequence])
        self.assertEqual(self.broker.pending_system_notices("designer"), [])

    async def test_maker_file_notice_keeps_a_newer_revision_queued_during_delivery(self) -> None:
        self.broker.assign("designer", "drawing-1")
        self.broker.acknowledge("designer", "drawing-1")
        self.broker.queue_user_file_changed("root/plate.py", "revision-1")
        delivering = self.broker.pending_system_notices("designer")[0]

        self.broker.queue_user_file_changed("root/plate.py", "revision-2")
        self.broker.mark_system_notices_delivered("designer", [delivering.sequence])

        pending = self.broker.pending_system_notices("designer")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].revision, "revision-2")
        self.assertNotEqual(pending[0].sequence, delivering.sequence)

    async def test_maker_file_notice_queues_nothing_when_every_role_is_waiting(self) -> None:
        self.assertEqual(self.broker.queue_user_file_changed("root/plate.py", "revision"), [])
        self.assertTrue(all(not self.broker.pending_system_notices(role) for role in self.broker.agents))


class ProfileBrokerTest(unittest.IsolatedAsyncioTestCase):
    async def test_direct_profile_routes_user_and_turn_state_without_assignment_ceremony(self) -> None:
        broker = Broker(profile=load_profile("builder", shop_root=ROOT))
        builder = broker.manifest("builder", "Builder")
        entry = await broker.record_conversation("user", "Build a bracket.")
        direction = broker.pending_for("builder")[0]

        self.assertEqual(entry.author, "user")
        self.assertEqual((direction.sender, direction.recipient, direction.assignment_id), ("user", "builder", ""))
        with self.assertRaisesRegex(ValueError, "assignment ID.*direct"):
            broker.send("direction", "user", "builder", "smuggle an assignment", "not-allowed")
        broker.register_direct_delivery("builder", "turn-1")
        broker.turn_started("builder", "turn-1")
        self.assertEqual(builder.state, "active")
        broker.turn_completed("builder", "turn-1")
        self.assertEqual(builder.state, "waiting")
        for operation in (
            lambda: broker.assign("builder", "bad"),
            lambda: broker.acknowledge("builder", "bad"),
            lambda: broker.complete("builder", "bad"),
            lambda: broker.send("report", "builder", "builder", "bad"),
        ):
            with self.assertRaisesRegex(ValueError, "direct|unavailable"):
                operation()

    async def test_direct_role_failure_ends_only_the_failed_turn(self) -> None:
        broker = Broker(profile=load_profile("builder", shop_root=ROOT))
        builder = broker.manifest("builder", "Builder")
        broker.register_direct_delivery("builder", "turn-1")
        broker.turn_started("builder", "turn-1")

        broker.role_failed("builder", "quota exhausted")

        self.assertEqual(builder.state, "waiting")
        self.assertEqual(builder.direct_delivery_id, "")
        self.assertEqual(builder.failure, "quota exhausted")

    async def test_delegated_profile_enforces_declared_edges_and_keeps_completion_assignment_based(self) -> None:
        broker = Broker(profile=load_profile("fordesmac", shop_root=ROOT))
        for agent in broker.profile.agents:
            broker.manifest(agent.id, agent.label)
        with self.assertRaisesRegex(ValueError, "assignment edge"):
            broker.send("assignment", "designer", "machinist", "skip foreman", "bad")
        with self.assertRaisesRegex(ValueError, "reporting parent"):
            broker.send("report", "designer", "machinist", "wrong parent")
        assignment = broker.send("assignment", "foreman", "librarian", "Research ACP", "research-1")
        self.assertEqual(assignment.recipient, "librarian")
        broker.acknowledge("librarian", "research-1")
        broker.turn_completed("librarian", "backend-turn")
        self.assertEqual(broker.agents["librarian"].state, "active")
        broker.complete("librarian", "research-1")
        self.assertEqual(broker.agents["librarian"].state, "waiting")

    async def test_only_declared_user_agent_output_reaches_the_conversation(self) -> None:
        broker = Broker(profile=load_profile("fordesmac", shop_root=ROOT))
        await broker.record_conversation("foreman", "Public update")
        self.assertEqual(broker.conversation[-1].author, "foreman")
        with self.assertRaisesRegex(ValueError, "user-facing"):
            await broker.record_conversation("designer", "Internal update")


if __name__ == "__main__":
    unittest.main()
