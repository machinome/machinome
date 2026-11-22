# How an open development page learns of a publication (observed 22 November 2026)

## Method

On the bench `machinome/WTs/model-apps` at `50bdffdf`, with the viewer bundle
built from the bench's source (`npm run build` in the widget directory, no
install), a scratch copy of the suite's `tests/flat_project/` with a manifest
naming `flat_project.simple_cylinder:SimpleCylinder` was served by

    env -C <scratch>/proj MACHINOME_PORT=8028 .venv/bin/machinome develop

(port 8028 from the bench's `.env`; nothing under `projects/`; no port 9010).
`develop-reload-probe.py` (beside this file) opened `http://localhost:8028/`
in headless Chromium, logged every frame received on the page's reload
socket, every response to `/_build_error` and `/build/viewer.json` with the
model path the document named, and, from a thread polling the file, every
rewrite of `_build/viewer.json` on disk with the model path it then named.
After 8 s it edited the model's Python (`radius=1` to `radius=3`), waited
25 s, edited it again (`height=10` to `height=20`), and waited 25 s. The
session was then stopped and its processes ended.

## Output (seconds since the probe started)

```
   1.66  PAGE fetch doc     flat_project/simple_cylinder-SimpleCylinder,1,10-1bb09a1c7131.stl
   1.78  WS open            ws://localhost:8028/ws/reload
   1.79  WS recv            reload
   1.83  PAGE build_error   {}
   1.87  PAGE fetch doc     flat_project/simple_cylinder-SimpleCylinder,1,10-1bb09a1c7131.stl
   9.45  --- EDIT 1         radius 1 -> 3
   9.57  WS recv            reload
   9.58  PAGE build_error   {}
   9.61  PAGE fetch doc     flat_project/simple_cylinder-SimpleCylinder,1,10-1bb09a1c7131.stl
  10.56  DISK viewer.json   flat_project/simple_cylinder-SimpleCylinder,3,10-c2cbc7ae5bfb.stl
  34.45  --- EDIT 2         height 10 -> 20
  34.54  WS recv            reload
  34.55  PAGE build_error   {}
  34.59  PAGE fetch doc     flat_project/simple_cylinder-SimpleCylinder,3,10-c2cbc7ae5bfb.stl
  35.50  DISK viewer.json   flat_project/simple_cylinder-SimpleCylinder,3,20-b5b953fd84c2.stl
  59.46  --- END
```

The develop log shows, for each edit, `… changed, reloading`, then
`manager.develop - Reloading the viewer`, then the page's two requests, then
`core.builder - START` of the next builder.

## What it shows

The mechanism, by reading and by observation: the open page learns of a
build only through `reload` on its socket (`widget/src/reloader.ts`
`onmessage` → `checkBuild`: `/_build_error`, then, with no new error,
`manifestChanged()` through `develop.ts`'s callback). The server sends
`reload` once when the socket opens (`server.py` `websocket_endpoint`) and
otherwise only when the session's `reload()` is called, which
`manager/develop.py` does at the top of its loop, after a builder process
has exited and before the next one starts (158-170). A watching builder
exits only when a source changes after it has published (`builder.py`
514-518, 636-641). So each edit's `reload` reaches the page about 0.1 s
after the edit, the page fetches the document still on disk (the previous
build's), and the new document is published about 1 s later with nothing
telling the page. The page shows each edit only at the next edit: one edit
behind, every time (radius 3 appeared at the second edit, height 20 never).
The page itself does not watch the document.

This is real, and it stands in the way of the brief's point (f): an app edit
that rode the same path would also show only at the following edit.
