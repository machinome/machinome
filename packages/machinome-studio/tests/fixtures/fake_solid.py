#!/usr/bin/env python3
"""Finite solid CLI fixture for launcher acceptance tests."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


command, argument = sys.argv[1:3]
cwd = Path.cwd()
if command == "new":
    project = cwd / argument
    (project / "root").mkdir(parents=True)
    (project / "root" / "__init__.py").write_text("# test scaffold\n")
    (project / ".gitignore").write_text("_build/\n")
elif command == "build":
    if os.environ.get("FAKE_SOLID_FAIL_BUILD"):
        print("forced initial build failure", file=sys.stderr)
        raise SystemExit(17)
    build = cwd / "_build"
    build.mkdir(exist_ok=True)
    model = os.environ.get("FAKE_SOLID_MODEL", "part.stl")
    (build / model).write_text(os.environ.get("FAKE_SOLID_MODEL_CONTENT", "solid part"))
    viewer = os.environ.get("FAKE_SOLID_VIEWER")
    if viewer is None:
        viewer = json.dumps({"version": 1, "root": {"name": "part", "model": model}})
    (build / "viewer.json").write_text(viewer)
else:
    raise SystemExit(2)
