#!/usr/bin/env python3
"""Finite solid CLI fixture for launcher acceptance tests."""

from __future__ import annotations

import json
import os
import shutil
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
    # A watcher runs this repeatedly inside one floor, so the
    # environment cannot steer an individual build. A state file in the
    # project directory can: a test writes it between polls to make the
    # next build fail, publish a different snapshot, or -- by writing
    # nothing -- leave the snapshot identical.
    state = {}
    state_file = cwd / ".fake-solid-state.json"
    if state_file.is_file():
        state = json.loads(state_file.read_text())

    failure = state.get("fail") or os.environ.get("FAKE_SOLID_FAIL_BUILD")
    if failure:
        message = failure if isinstance(failure, str) else "forced initial build failure"
        print(message, file=sys.stderr)
        raise SystemExit(17)

    # Publish the way the framework does: write a fresh versioned
    # directory, repoint the _build symlink at it, and drop the old one.
    # A fixture that wrote in place would hide every bug that only appears
    # when the build directory a consumer is holding stops existing.
    build = cwd / f"_build.{os.urandom(4).hex()}"
    build.mkdir()
    model = state.get("model") or os.environ.get("FAKE_SOLID_MODEL", "part.stl")
    content = state.get("model_content") or os.environ.get("FAKE_SOLID_MODEL_CONTENT", "solid part")
    (build / model).write_text(content)
    viewer = state.get("viewer")
    if viewer is not None:
        viewer = json.dumps(viewer)
    else:
        viewer = os.environ.get("FAKE_SOLID_VIEWER")
    if viewer is None:
        viewer = json.dumps({"version": 1, "root": {"name": "part", "model": model}})
    (build / "viewer.json").write_text(viewer)

    link = cwd / "_build"
    previous = link.resolve() if link.is_symlink() else None
    if previous is None and link.is_dir():
        # A project built before symlink publication has a real directory
        # here; the first new-style build replaces it.
        shutil.rmtree(link)
    staging = cwd / f".{build.name}.link"
    staging.symlink_to(build.name)
    os.replace(staging, link)
    if previous is not None and previous != build and previous.is_dir():
        shutil.rmtree(previous, ignore_errors=True)
else:
    raise SystemExit(2)
