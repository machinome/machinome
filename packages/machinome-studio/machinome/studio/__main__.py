"""Run the local shop-floor service."""

from __future__ import annotations

import argparse
import os

import uvicorn

from .app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local shop-floor service")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FLOOR_PORT", "9000")),
        help="local browser port (default: 9000 or FLOOR_PORT)",
    )
    arguments = parser.parse_args()
    uvicorn.run(create_app(), host="127.0.0.1", port=arguments.port)


if __name__ == "__main__":
    main()
