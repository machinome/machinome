"""Run the local shop-floor service."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn

from .app import create_app
from .preparation import (
    PreparationError,
    ProjectRuntimeError,
    default_project_home,
    default_solid_command,
    prepare_project,
    primary_shop_root,
    read_project_runtime,
)
from .profiles import ProfileError, load_profile, resolve_profile_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local shop-floor service")
    parser.add_argument("project_name", help="lowercase kebab-case project name below projects/")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FLOOR_PORT", "9000")),
        help="local browser port (default: 9000 or FLOOR_PORT)",
    )
    parser.add_argument("--project-home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    parser.add_argument("--profile", help="override the project-selected runtime profile")
    arguments = parser.parse_args()
    checkout = Path.cwd()
    project_home = arguments.project_home or default_project_home(checkout)
    try:
        shop_root = primary_shop_root(checkout)
        selection = read_project_runtime(arguments.project_name, project_home=project_home)
        profile = resolve_profile_runtime(
            load_profile(arguments.profile, shop_root=shop_root, selection=selection),
            selection,
        )
    except (PreparationError, ProfileError, ProjectRuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    solid_command = arguments.solid_command or default_solid_command(checkout)
    try:
        prepared = prepare_project(
            arguments.project_name,
            project_home=project_home,
            solid_command=solid_command,
            shop_root=shop_root,
        )
    except PreparationError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    uvicorn.run(
        create_app(
            prepared.project_root,
            artifact_root=prepared.artifact_root,
            viewer_bundle=prepared.viewer_bundle,
            solid_command=prepared.solid_command,
            build_environment=prepared.build_environment,
            profile=profile,
        ),
        host="127.0.0.1",
        port=arguments.port,
    )


if __name__ == "__main__":
    main()
