"""Conversation publishing command for the active foreman agent."""

from __future__ import annotations

import argparse
import json
import os
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
    parser.add_argument("--server", default=os.environ.get("FLOOR_URL", "http://127.0.0.1:9000"))
    parser.add_argument("--run", default="shop-floor")
    parser.add_argument("--text", required=True)

    arguments = parser.parse_args()
    result = _request(arguments.server, f"/api/runs/{arguments.run}/foreman/publish", {"text": arguments.text})
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
