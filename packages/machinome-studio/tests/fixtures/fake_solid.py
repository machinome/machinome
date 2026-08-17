#!/usr/bin/env python3
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Finite solid CLI fixture for launcher acceptance tests."""

from __future__ import annotations

import json
import base64
import os
import sys
import tempfile
import time
from pathlib import Path


command = sys.argv[1]
argument = sys.argv[2] if len(sys.argv) > 2 else ""
cwd = Path.cwd()
if command == "new":
    if delay := os.environ.get("FAKE_SOLID_NEW_DELAY"):
        time.sleep(float(delay))
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

    # A real build imports the project's sources, so it opens every one of
    # them.  The fixture reads them for the same reason a watcher must not
    # treat a read as a change.
    for source in sorted(cwd.rglob("*.py")):
        if "_build" in source.relative_to(cwd).parts:
            continue
        source.read_text()
    with (cwd / ".fake-solid-builds").open("a") as log:
        log.write("build\n")

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
    for extra_model, extra_content in sorted(state.get("extra_models", {}).items()):
        publish(build / extra_model, extra_content)
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
    bundle.write_text('''globalThis.SolidNodeWidget={apiVersion:4,async mount(target,url,options){const history=window.__solidNodeWidgetHistory??={mounts:0,fetches:[],updates:[]};history.mounts+=1;const fetchJson=async(path)=>{history.fetches.push(path);const response=await fetch(path);if(!response.ok)throw new Error(`Failed to load ${path}`);return response.json()};const fetchArtifact=async(path)=>{const url=`${options.baseUrl}${path}`;history.fetches.push(url);const response=await fetch(url);if(!response.ok)throw new Error(`Failed to load ${url}`);return response.text()};const models=(value,found=[])=>{if(Array.isArray(value))value.forEach(child=>models(child,found));else if(value&&typeof value==="object"){if(typeof value.model==="string")found.push(value.model);Object.entries(value).forEach(([key,child])=>{if(key!=="model")models(child,found)})}return found};const assembly=(node,path=[],inherited=null)=>{const color=node.color??inherited;return{name:node.name??"root",path,color,model:typeof node.model==="string",children:(node.children??[]).map(child=>assembly(child,[...path,child.name],color))}};let snapshot=await fetchJson(url);let known=new Set(models(snapshot));await Promise.all([...known].map(fetchArtifact));const canvas=document.createElement("canvas");canvas.width=640;canvas.height=360;canvas.className=options.className||"";canvas.setAttribute("role",options.role||"");canvas.setAttribute("aria-label",options.ariaLabel||"");const draw=(offset=0)=>{const ctx=canvas.getContext("2d");ctx.fillStyle=`hsl(${(JSON.stringify(snapshot).length+offset)%360} 60% 45%)`;ctx.fillRect(0,0,640,360)};draw();canvas.addEventListener("pointermove",event=>draw(event.offsetX));target.append(canvas);if(JSON.stringify(snapshot).includes("$t")&&options.animation==="toggle"){const toggle=document.createElement("button");toggle.textContent="Timeline";toggle.className="timeline-toggle";toggle.setAttribute("aria-expanded","false");const controls=document.createElement("div");controls.className="animation-controls";controls.hidden=true;toggle.onclick=()=>{controls.hidden=!controls.hidden;toggle.setAttribute("aria-expanded",String(!controls.hidden))};target.append(toggle,controls)}return{apiVersion:4,artifactChanged:async(path)=>{history.updates.push(["artifactChanged",path]);await fetchArtifact(path);draw()},manifestChanged:async()=>{history.updates.push(["manifestChanged"]);const next=await fetchJson(url);const nextModels=new Set(models(next));await Promise.all([...nextModels].filter(path=>!known.has(path)).map(fetchArtifact));snapshot=next;known=nextModels;draw()},reload:async()=>{history.updates.push(["reload"]);snapshot=await fetchJson(url);known=new Set(models(snapshot));await Promise.all([...known].map(fetchArtifact));draw()},assembly:()=>assembly(snapshot.root),setRoot:(path)=>history.updates.push(["setRoot",path]),setVisible:(path,visible)=>history.updates.push(["setVisible",path,visible]),view(){return{}},dispose(){target.replaceChildren()}}}};''')
    if supplied_bundle := os.environ.get("FAKE_SOLID_BUNDLE"):
        bundle = Path(supplied_bundle)
    print(json.dumps({"path": str(bundle), "apiVersion": state.get("viewer_api_version", 4)}))
elif command == "snapshot":
    output = Path(sys.argv[sys.argv.index("-o") + 1])
    output.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8/+8dAwMDEwMDAwMDAwAjPwLvkz8BYAAAAABJRU5ErkJggg=="))
else:
    raise SystemExit(2)
