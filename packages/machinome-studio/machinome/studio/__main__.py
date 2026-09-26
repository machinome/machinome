# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Run the local shop-floor service."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn

from .app import create_app
from .launcher import LaunchError, resolve_launch
from .openspec import OpenSpecUnavailable, resolve_openspec_command
from .preparation import default_machinome_command, shop_resource_root
from .sessions import SessionRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local shop-floor service")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="local browser port (default: 9000 or FLOOR_PORT)",
    )
    parser.add_argument(
        "--projects-dir",
        type=Path,
        default=None,
        help="exact directory containing project repositories",
    )
    parser.add_argument("--machinome-command", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    try:
        arguments.projects_dir, arguments.port = resolve_launch(arguments, os.environ)
        resolve_openspec_command()
    except (LaunchError, OpenSpecUnavailable) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    project_home = arguments.projects_dir
    shop_root = shop_resource_root()
    machinome_command = arguments.machinome_command or default_machinome_command()
    registry = SessionRegistry(
        project_home,
        shop_root=shop_root,
        machinome_command=machinome_command,
        start_agents=False,
    )
    uvicorn.run(
        create_app(project_home, registry=registry),
        host="127.0.0.1",
        port=arguments.port,
    )


if __name__ == "__main__":
    main()
