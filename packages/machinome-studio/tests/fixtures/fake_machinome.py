#!/usr/bin/env python3
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Finite Machinome CLI fixture for launcher acceptance tests."""

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
# One shop runs this fixture for several projects, so a test that asks how
# often the shop reached for the framework needs one log outside them all.
if call_log := os.environ.get("MACHINOME_CALL_LOG"):
    with Path(call_log).open("a") as calls:
        calls.write(f"{command}:{argument}\n")


def project_state(project: Path) -> dict:
    state_file = project / ".fake-machinome-state.json"
    return json.loads(state_file.read_text()) if state_file.is_file() else {}


def declared_models(state: dict) -> list[str]:
    """The names a [tool.machinome.models] table would declare, if any."""
    names = state.get("models")
    if isinstance(names, list) and names:
        return [str(name) for name in names]
    name = state.get("model_name")
    return [str(name)] if name else []


def model_build_dir(project: Path, state: dict, name: str | None = None) -> Path:
    """Where one model publishes. A project declaring named models builds each
    into `_build/<name>`, as the framework does for a [tool.machinome.models]
    table; an unnamed one owns `_build` itself."""
    if name is None:
        declared = declared_models(state)
        name = declared[0] if declared else None
    return project / "_build" / name if name else project / "_build"


if command == "new":
    if delay := os.environ.get("FAKE_MACHINOME_NEW_DELAY"):
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
    state_file = cwd / ".fake-machinome-state.json"
    if state_file.is_file():
        state = json.loads(state_file.read_text())
    if build_delay := state.get("build_delay"):
        time.sleep(float(build_delay))
    # A test that watches what the shop shows *while* a build runs cannot bound
    # that build with a sleep without racing it. A gate outside the project --
    # so no watcher sees it -- lets the test hold the build open and release it.
    if gate := state.get("build_gate"):
        deadline = time.monotonic() + 60
        while not Path(gate).exists() and time.monotonic() < deadline:
            time.sleep(0.02)

    # A real build imports the project's sources, so it opens every one of
    # them.  The fixture reads them for the same reason a watcher must not
    # treat a read as a change.
    for source in sorted(cwd.rglob("*.py")):
        if "_build" in source.relative_to(cwd).parts:
            continue
        source.read_text()
    with (cwd / ".fake-machinome-builds").open("a") as log:
        log.write("build\n")

    selected = argument if argument and not argument.startswith("-") else None
    build = model_build_dir(cwd, state, selected)
    build.mkdir(exist_ok=True, parents=True)

    def publish(path: Path, content: str) -> None:
        if path.is_file() and path.read_text() == content:
            return
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)

    failure = state.get("fail") or os.environ.get("FAKE_MACHINOME_FAIL_BUILD")
    if failure:
        message = failure if isinstance(failure, str) else "forced initial build failure"
        publish(build / "errors.json", message)
        print(message, file=sys.stderr)
        raise SystemExit(17)

    model = state.get("model") or os.environ.get("FAKE_MACHINOME_MODEL", "part.stl")
    content = state.get("model_content") or os.environ.get("FAKE_MACHINOME_MODEL_CONTENT", "solid part")
    publish(build / model, content)
    for extra_model, extra_content in sorted(state.get("extra_models", {}).items()):
        publish(build / extra_model, extra_content)
    viewer = state.get("viewer")
    if viewer is not None:
        viewer = json.dumps(viewer)
    else:
        viewer = os.environ.get("FAKE_MACHINOME_VIEWER")
    if viewer is None:
        viewer = json.dumps({"version": 1, "root": {"name": "part", "model": model}})
    errors = build / "errors.json"
    if errors.exists():
        errors.unlink()
    publish(build / "viewer.json", viewer)
elif command == "models":
    state = project_state(cwd)
    names = declared_models(state) or [None]
    print(json.dumps({
        "root": str(cwd),
        "build_root": str(cwd / "_build"),
        "default": names[0],
        "models": [{
            "name": name,
            "reference": "root:Root",
            "default": index == 0,
            "build_dir": str(model_build_dir(cwd, state, name)),
            "state": "unbuilt",
        } for index, name in enumerate(names)],
    }))
elif command == "viewer":
    state = {}
    state_file = cwd / ".fake-machinome-state.json"
    if state_file.is_file():
        state = json.loads(state_file.read_text())
    if state.get("viewer_missing"):
        print('The browser viewer is not installed. It is the separate machinome-viewer package; install it with: pip install "machinome[viewer]"', file=sys.stderr)
        raise SystemExit(18)
    bundle = Path(tempfile.gettempdir()) / f"fake-machinome-viewer-{os.getpid()}.js"
    bundle.write_text('''globalThis.MachinomeViewer={apiVersion:20,async mount(target,url,options){const history=window.__machinomeViewerHistory??={mounts:0,fetches:[],updates:[],navigators:[]};history.mounts+=1;const fetchJson=async(path)=>{history.fetches.push(path);const response=await fetch(path);if(!response.ok)throw new Error(`Failed to load ${path}`);return response.json()};const fetchArtifact=async(path)=>{const url=`${options.baseUrl}${path}`;history.fetches.push(url);const response=await fetch(url);if(!response.ok)throw new Error(`Failed to load ${url}`);return response.text()};const models=(value,found=[])=>{if(Array.isArray(value))value.forEach(child=>models(child,found));else if(value&&typeof value==="object"){if(typeof value.model==="string")found.push(value.model);Object.entries(value).forEach(([key,child])=>{if(key!=="model")models(child,found)})}return found};const assembly=(node,path=[],inherited=null)=>{const color=node.color??inherited;return{name:node.name??"root",path,color,model:typeof node.model==="string",children:(node.children??[]).map(child=>assembly(child,[...path,child.name],color))}};let snapshot=await fetchJson(url);let known=new Set(models(snapshot));await Promise.all([...known].map(fetchArtifact));const canvas=document.createElement("canvas");canvas.width=640;canvas.height=360;canvas.className=options.className||"";canvas.setAttribute("role",options.role||"");canvas.setAttribute("aria-label",options.ariaLabel||"");const draw=(offset=0)=>{const ctx=canvas.getContext("2d");ctx.fillStyle=`hsl(${(JSON.stringify(snapshot).length+offset)%360} 60% 45%)`;ctx.fillRect(0,0,640,360)};draw();canvas.addEventListener("pointermove",event=>draw(event.offsetX));target.append(canvas);if(JSON.stringify(snapshot).includes("$t")&&options.animation==="toggle"){const toggle=document.createElement("button");toggle.textContent="Timeline";toggle.className="timeline-toggle";toggle.setAttribute("aria-expanded","false");const controls=document.createElement("div");controls.className="animation-controls";controls.hidden=true;toggle.onclick=()=>{controls.hidden=!controls.hidden;toggle.setAttribute("aria-expanded",String(!controls.hidden))};target.append(toggle,controls)}return{apiVersion:20,artifactChanged:async(path)=>{history.updates.push(["artifactChanged",path]);await fetchArtifact(path);draw()},manifestChanged:async()=>{history.updates.push(["manifestChanged"]);const next=await fetchJson(url);const nextModels=new Set(models(next));await Promise.all([...nextModels].filter(path=>!known.has(path)).map(fetchArtifact));snapshot=next;known=nextModels;draw()},reload:async()=>{history.updates.push(["reload"]);snapshot=await fetchJson(url);known=new Set(models(snapshot));await Promise.all([...known].map(fetchArtifact));draw()},assembly:()=>assembly(snapshot.root),setRoot:(path)=>history.updates.push(["setRoot",path]),setVisible:(path,visible)=>history.updates.push(["setVisible",path,visible]),view(){return{}},dispose(){target.replaceChildren()}}},mountNavigator(target,viewer,options){const history=window.__machinomeViewerHistory??={mounts:0,fetches:[],updates:[],navigators:[]};const record={label:(options&&options.label)||'Assembly',disposed:false};history.navigators.push(record);const tree=document.createElement('div');tree.className='machinome-nav';const inner=document.createElement('div');inner.className='machinome-nav-tree';inner.setAttribute('role','tree');inner.setAttribute('aria-label',record.label);tree.append(inner);target.append(tree);return{dispose(){record.disposed=true;target.replaceChildren()}}}};''')
    if supplied_bundle := os.environ.get("FAKE_MACHINOME_BUNDLE"):
        bundle = Path(supplied_bundle)
    print(json.dumps({"path": str(bundle), "index": str(bundle.with_name("index.html")), "apiVersion": state.get("viewer_api_version", int(os.environ.get("FAKE_MACHINOME_VIEWER_API", "20"))), "version": "0.1.0"}))
elif command == "snapshot":
    output = Path(sys.argv[sys.argv.index("-o") + 1])
    output.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8/+8dAwMDEwMDAwMDAwAjPwLvkz8BYAAAAABJRU5ErkJggg=="))
else:
    raise SystemExit(2)
