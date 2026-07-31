from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from floor import agent


class AgentCLITest(unittest.TestCase):
    def test_direction_and_report_use_the_role_neutral_envelope_surface(self) -> None:
        with (
            patch.object(sys, "argv", ["agent", "direction", "--sender", "foreman", "--recipient", "designer", "--text", "Draw it"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(
            request.call_args.args,
            (
                "http://127.0.0.1:9000",
                "/api/runs/shop-floor/envelopes",
                "POST",
                {"kind": "direction", "sender": "foreman", "recipient": "designer", "body": "Draw it"},
            ),
        )

        with (
            patch.object(sys, "argv", ["agent", "report", "--sender", "machinist", "--recipient", "foreman", "--text", "Built", "--assignment", "build-1"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[3]["recipient"], "foreman")
        self.assertEqual(request.call_args.args[3]["assignment_id"], "build-1")

    def test_assignment_caller_supplies_the_profile_edge(self) -> None:
        with (
            patch.object(sys, "argv", ["agent", "assign", "--sender", "foreman", "--recipient", "librarian", "--assignment", "research", "--text", "Research ACP"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[3]["sender"], "foreman")
        self.assertEqual(request.call_args.args[3]["recipient"], "librarian")


if __name__ == "__main__":
    unittest.main()
