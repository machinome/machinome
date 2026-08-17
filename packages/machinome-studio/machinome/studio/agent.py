# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Outgoing role-neutral shop broker commands for managed agents."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen


def _request(server: str, path: str, method: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    request = Request(
        f"{server.rstrip('/')}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:  # nosec: explicit local shop-floor server
        data = response.read()
        return json.loads(data) if data else {}


@dataclass(frozen=True)
class FloorClient:
    """Bounded client for one already-selected shop-floor session."""

    server: str
    session: str

    @property
    def base(self) -> str:
        return f"/api/sessions/{self.session}"

    def manifest(self, role: str, label: str) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/agents",
            "POST",
            {"role": role, "label": label},
        )

    def direction(self, sender: str, recipient: str, text: str) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/envelopes",
            "POST",
            {"kind": "direction", "sender": sender, "recipient": recipient, "body": text},
        )

    def assign(
        self,
        sender: str,
        recipient: str,
        assignment: str,
        text: str,
    ) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/envelopes",
            "POST",
            {
                "kind": "assignment",
                "sender": sender,
                "recipient": recipient,
                "body": text,
                "assignment_id": assignment,
            },
        )

    def acknowledge(self, role: str, assignment: str) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/agents/{role}/acknowledgments",
            "POST",
            {"assignment_id": assignment},
        )

    def report(
        self,
        sender: str,
        recipient: str,
        text: str,
        assignment: str = "",
    ) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/envelopes",
            "POST",
            {
                "kind": "report",
                "sender": sender,
                "recipient": recipient,
                "body": text,
                "assignment_id": assignment,
            },
        )

    def complete(self, role: str, assignment: str) -> dict[str, Any]:
        return _request(
            self.server,
            f"{self.base}/agents/{role}/completions",
            "POST",
            {"assignment_id": assignment},
        )

    def stop(self, role: str) -> dict[str, Any]:
        return _request(self.server, f"{self.base}/agents/{role}", "DELETE")


def main() -> None:
    parser = argparse.ArgumentParser(prog="shop-floor-agent")
    parser.add_argument("--server", default=os.environ.get("FLOOR_URL", "http://127.0.0.1:9000"))
    parser.add_argument("--session", default=os.environ.get("FLOOR_SESSION"))
    commands = parser.add_subparsers(dest="command", required=True)

    manifest = commands.add_parser("manifest")
    manifest.add_argument("--role", required=True)
    manifest.add_argument("--label", required=True)

    direction = commands.add_parser("direction")
    direction.add_argument("--sender", required=True)
    direction.add_argument("--recipient", required=True)
    direction.add_argument("--text", required=True)

    assign = commands.add_parser("assign")
    assign.add_argument("--sender", required=True)
    assign.add_argument("--recipient", required=True)
    assign.add_argument("--assignment", required=True)
    assign.add_argument("--text", required=True)

    acknowledge = commands.add_parser("acknowledge")
    acknowledge.add_argument("--role", required=True)
    acknowledge.add_argument("--assignment", required=True)

    report = commands.add_parser("report")
    report.add_argument("--sender", required=True)
    report.add_argument("--recipient", required=True)
    report.add_argument("--text", required=True)
    report.add_argument("--assignment", default="")

    complete = commands.add_parser("complete")
    complete.add_argument("--role", required=True)
    complete.add_argument("--assignment", required=True)

    stop = commands.add_parser("stop")
    stop.add_argument("--role", required=True)

    arguments = parser.parse_args()
    if not arguments.session:
        parser.error("a session is required (set FLOOR_SESSION or pass --session)")
    client = FloorClient(arguments.server, arguments.session)
    if arguments.command == "manifest":
        result = client.manifest(arguments.role, arguments.label)
    elif arguments.command == "direction":
        result = client.direction(arguments.sender, arguments.recipient, arguments.text)
    elif arguments.command == "assign":
        result = client.assign(
            arguments.sender,
            arguments.recipient,
            arguments.assignment,
            arguments.text,
        )
    elif arguments.command == "acknowledge":
        result = client.acknowledge(arguments.role, arguments.assignment)
    elif arguments.command == "report":
        result = client.report(
            arguments.sender,
            arguments.recipient,
            arguments.text,
            arguments.assignment,
        )
    elif arguments.command == "complete":
        result = client.complete(arguments.role, arguments.assignment)
    else:
        result = client.stop(arguments.role)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
