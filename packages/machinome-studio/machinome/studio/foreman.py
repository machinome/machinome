"""Direct conversation commands for the active foreman agent."""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib.request import Request, urlopen


def _request(server: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        f"{server.rstrip('/')}{path}",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=None) as response:  # nosec: explicit local shop-floor server
        return json.loads(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(prog="shop-floor-foreman")
    parser.add_argument("--server", default="http://127.0.0.1:9000")
    parser.add_argument("--run", default="shop-floor")
    commands = parser.add_subparsers(dest="command", required=True)

    receive = commands.add_parser("receive")
    receive.add_argument("--after", type=int, default=0)

    publish = commands.add_parser("publish")
    publish.add_argument("--text", required=True)

    arguments = parser.parse_args()
    if arguments.command == "receive":
        result = _request(arguments.server, f"/api/runs/{arguments.run}/foreman/receive", {"after": arguments.after})
    else:
        result = _request(arguments.server, f"/api/runs/{arguments.run}/foreman/publish", {"text": arguments.text})
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
