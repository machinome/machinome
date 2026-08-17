# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import sys
import unittest
from unittest.mock import patch
import os

from floor import agent


class AgentCLITest(unittest.TestCase):
    def test_direction_and_report_use_the_role_neutral_envelope_surface(self) -> None:
        with (
            patch.dict(os.environ, {"FLOOR_SESSION": "session-a"}),
            patch.object(sys, "argv", ["agent", "direction", "--sender", "foreman", "--recipient", "designer", "--text", "Draw it"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(
            request.call_args.args,
            (
                "http://127.0.0.1:9000",
                "/api/sessions/session-a/envelopes",
                "POST",
                {"kind": "direction", "sender": "foreman", "recipient": "designer", "body": "Draw it"},
            ),
        )

        with (
            patch.dict(os.environ, {"FLOOR_SESSION": "session-a"}),
            patch.object(sys, "argv", ["agent", "report", "--sender", "machinist", "--recipient", "foreman", "--text", "Built", "--assignment", "build-1"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[3]["recipient"], "foreman")
        self.assertEqual(request.call_args.args[3]["assignment_id"], "build-1")

    def test_assignment_caller_supplies_the_profile_edge(self) -> None:
        with (
            patch.dict(os.environ, {"FLOOR_SESSION": "session-a"}),
            patch.object(sys, "argv", ["agent", "assign", "--sender", "foreman", "--recipient", "librarian", "--assignment", "research", "--text", "Research ACP"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[3]["sender"], "foreman")
        self.assertEqual(request.call_args.args[3]["recipient"], "librarian")

    def test_session_defaults_from_environment_and_is_required(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(sys, "argv", ["agent", "stop", "--role", "builder"]),
            patch.object(agent, "_request") as request,
            self.assertRaises(SystemExit) as raised,
        ):
            agent.main()
        self.assertEqual(raised.exception.code, 2)
        request.assert_not_called()

        with (
            patch.dict(os.environ, {"FLOOR_SESSION": "from-environment"}),
            patch.object(sys, "argv", ["agent", "--session", "explicit", "stop", "--role", "builder"]),
            patch.object(agent, "_request", return_value={}) as request,
        ):
            agent.main()
        self.assertEqual(request.call_args.args[1], "/api/sessions/explicit/agents/builder")


if __name__ == "__main__":
    unittest.main()
