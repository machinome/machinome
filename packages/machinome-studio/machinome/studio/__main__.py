"""Run the local shop-floor service."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

from .app import create_app
from .preparation import default_project_home, default_solid_command, primary_shop_root
from .sessions import SessionRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local shop-floor service")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FLOOR_PORT", "9000")),
        help="local browser port (default: 9000 or FLOOR_PORT)",
    )
    parser.add_argument("--project-home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    checkout = Path.cwd()
    project_home = arguments.project_home or default_project_home(checkout)
    shop_root = primary_shop_root(checkout)
    solid_command = arguments.solid_command or default_solid_command(checkout)
    registry = SessionRegistry(
        project_home,
        shop_root=shop_root,
        solid_command=solid_command,
        start_agents=False,
    )
    uvicorn.run(
        create_app(project_home, registry=registry),
        host="127.0.0.1",
        port=arguments.port,
    )


if __name__ == "__main__":
    main()
