"""Run the local shop-floor service."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

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
    parser.add_argument("--project", type=Path, help="project root to build and serve")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("__init__.py"),
        help="project-local model path passed to solid build (default: __init__.py)",
    )
    parser.add_argument("--callback-token", help="local token accepted from solid develop callbacks")
    parser.add_argument("--solid-command", default="solid", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.project is not None:
        subprocess.run([arguments.solid_command, "build", str(arguments.model)], cwd=arguments.project, check=True)
    uvicorn.run(
        create_app(arguments.project, callback_token=arguments.callback_token),
        host="127.0.0.1",
        port=arguments.port,
    )


if __name__ == "__main__":
    main()
