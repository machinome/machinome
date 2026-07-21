from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from floor import agent, foreman


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
            patch.object(sys, "argv", ["agent", "report", "--role", "machinist", "--text", "Built", "--assignment", "build-1"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[3]["recipient"], "foreman")
        self.assertEqual(request.call_args.args[3]["assignment_id"], "build-1")

    def test_foreman_surface_publishes_only_and_has_no_receive_command(self) -> None:
        with (
            patch.object(sys, "argv", ["foreman", "--text", "Progress"]),
            patch.object(foreman, "_request", return_value={}) as request,
        ):
            foreman.main()
        self.assertEqual(request.call_args.args[1], "/api/runs/shop-floor/foreman/publish")


if __name__ == "__main__":
    unittest.main()
