from __future__ import annotations

import asyncio
import unittest

from floor.app import Broker


class BrokerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.broker = Broker(event_history_limit=20)
        for role, label in (
            ("foreman", "Foreman"),
            ("designer", "Designer"),
            ("machinist", "Machinist"),
        ):
            self.broker.manifest(role, label)

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

    async def test_event_wait_is_signal_driven_and_history_is_bounded(self) -> None:
        cursor = self.broker.latest_event_sequence
        waiting = asyncio.create_task(self.broker.wait_for_events(cursor))
        await asyncio.sleep(0)
        self.assertFalse(waiting.done())

        envelope = self.broker.send("direction", "foreman", "machinist", "Hold position.")
        events = await asyncio.wait_for(waiting, timeout=0.1)
        self.assertEqual(events[-1].envelope_sequence, envelope.sequence)

        for index in range(25):
            self.broker.publish("test_event", {"role": "foreman", "body": f"private-{index}"})
        snapshot = self.broker.run()
        self.assertEqual(len(snapshot["events"]), 20)
        self.assertNotIn("private-24", str(snapshot["events"]), "display history must exclude message bodies")


if __name__ == "__main__":
    unittest.main()
