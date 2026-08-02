#!/usr/bin/env python3
"""Finite solid CLI fixture for launcher acceptance tests."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


command = sys.argv[1]
argument = sys.argv[2] if len(sys.argv) > 2 else ""
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

    build = cwd / "_build"
    build.mkdir(exist_ok=True)

    def publish(path: Path, content: str) -> None:
        if path.is_file() and path.read_text() == content:
            return
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)

    failure = state.get("fail") or os.environ.get("FAKE_SOLID_FAIL_BUILD")
    if failure:
        message = failure if isinstance(failure, str) else "forced initial build failure"
        publish(build / "errors.json", message)
        print(message, file=sys.stderr)
        raise SystemExit(17)

    model = state.get("model") or os.environ.get("FAKE_SOLID_MODEL", "part.stl")
    content = state.get("model_content") or os.environ.get("FAKE_SOLID_MODEL_CONTENT", "solid part")
    publish(build / model, content)
    viewer = state.get("viewer")
    if viewer is not None:
        viewer = json.dumps(viewer)
    else:
        viewer = os.environ.get("FAKE_SOLID_VIEWER")
    if viewer is None:
        viewer = json.dumps({"version": 1, "root": {"name": "part", "model": model}})
    errors = build / "errors.json"
    if errors.exists():
        errors.unlink()
    publish(build / "viewer.json", viewer)
elif command == "viewer":
    state = {}
    state_file = cwd / ".fake-solid-state.json"
    if state_file.is_file():
        state = json.loads(state_file.read_text())
    if state.get("viewer_missing"):
        print("build the solid-node viewer bundle", file=sys.stderr)
        raise SystemExit(18)
    bundle = Path(tempfile.gettempdir()) / f"fake-solid-widget-{os.getpid()}.js"
    bundle.write_text('''globalThis.SolidNodeWidget={apiVersion:1,async mount(target,url,options){const snapshot=await fetch(url).then(r=>r.json());const canvas=document.createElement("canvas");canvas.width=640;canvas.height=360;canvas.className=options.className||"";canvas.setAttribute("role",options.role||"");canvas.setAttribute("aria-label",options.ariaLabel||"");const draw=(offset=0)=>{const ctx=canvas.getContext("2d");ctx.fillStyle=`hsl(${(JSON.stringify(snapshot).length+offset)%360} 60% 45%)`;ctx.fillRect(0,0,640,360)};draw();canvas.addEventListener("pointermove",event=>draw(event.offsetX));target.append(canvas);if(JSON.stringify(snapshot).includes("$t")&&options.animation==="toggle"){const toggle=document.createElement("button");toggle.textContent="Timeline";toggle.className="timeline-toggle";toggle.setAttribute("aria-expanded","false");const controls=document.createElement("div");controls.className="animation-controls";controls.hidden=true;toggle.onclick=()=>{controls.hidden=!controls.hidden;toggle.setAttribute("aria-expanded",String(!controls.hidden))};target.append(toggle,controls)}return{apiVersion:1,view(){return{}},dispose(){target.replaceChildren()}}}};''')
    print(json.dumps({"path": str(bundle), "apiVersion": state.get("viewer_api_version", 1)}))
else:
    raise SystemExit(2)
