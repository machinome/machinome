## Context

Every page that shows a model goes through `mount()` (`src/viewer.ts` 383): the export page auto-mounts the inspector layout (`index.html`, `data-machinome-layout="inspector"`; `src/widget.ts` 49-53), the development page calls `mountDevelopment` → `mountInspector` → `mount` (`src/develop.ts` 74-81, `src/inspector.ts` 220), the Studio calls `window.MachinomeViewer.mount(target, '<prefix>viewer.json', { baseUrl: prefix, animation: 'toggle', … })` over its own artifact route (`packages/machinome-studio/machinome/studio/frontend/src/main.tsx` 240-248; `app.py` 859-867 serves any file under the build directory), and the Enigma's public page calls `mountInspector('#machine', 'model/manifest.json', { sidebar: 'open', … })` over an export it copies whole (`projects/enigma-i/tools/machine/page/index.html` 389; `tools/machine/build_page.py` 49-54). A model's app therefore has one place to live: inside `mount()`.

What `mount()` builds today, all in the host's container: the canvas (appended at 438, `container.style.position = 'relative'` at 427), the panels (`rebuildDriverChrome` 2205, `rebuildRunChrome` 2274, `rebuildClockedChrome` 1886, each gated by `showsDriverChrome`/`showsRunControls` on `driverControls`, `options.ts` 237-262), the animation bar (`refreshControls` 2129-2166), the corner full-screen control (`fullscreen.ts` 350-352 appends it to the container), the part outcome label (801) and a `ResizeObserver` on the container sizing the renderer from the container's client size (2373-2396). The handle is built last, as the literal returned at 2478.

The clocked machine as a page sees it: `machine()` returns a fresh wrapper over the machine standing at that call (2686-2742): the pure `ClockedMachine` (`src/clocked/machine.ts` 99-126: `state`, `move`, `trigger`, `snapshot`, `restore`, `reset`, …) plus `clockPlaying`/`setClockPlaying`. There is no subscription on it. The running handle has `onCommit` and `onOutcome` (199-200, 2765-2766); the posed driver table `onDriverChange` (319); navigation `onAssemblyChange` (306, ADR-049). A request that will be drawn commits the bank at once and draws the transition over the declared duration (`clockedPlay` 1537-1592, `drawingFrame` 1632-1643; ADR-064, ADR-065, ADR-073), so "the bank changed" and "the picture caught up" are two different moments, and a page can learn neither.

The viewer is React-free since ADR-052 (which superseded ADR-013). The repository's precedent for bundling a project's React sources with a tool-owned toolchain is the movie's stage (`packages/machinome-movie/machinome/movie/js/src/stage-build.mjs`: esbuild, the tool's own React through `nodePaths`, an alias for the tool's module, an IIFE, names not paths, content-keyed reuse). The viewer's own JavaScript is the npm workspace member `widget/` with esbuild 0.24.2 as a dev dependency (`package.json`, `build.mjs`); `currency.py` keeps `dist/machinome-viewer.js` current with `src/`, `package.json`, `build.mjs` and `tsconfig.json` and never installs (`currency.py` 46-63); a wheel ships the built bundle without `src/` or `build.mjs` (`pyproject.toml` 61-67).

React is not installed at the workspace root: `node_modules/react` is absent there; copies exist only nested, under `packages/machinome-movie/machinome/movie/js/node_modules/` (19.3.0, pinned) and `packages/machinome-studio/machinome/studio/frontend/node_modules/` (`^19.1.1`) (verified on the bench, `package-lock.json` entries at 3865, 3875, 5822, 5832). The widget declares no React.

## Goals / Non-Goals

**Goals:**

- A document naming its model's app is shown with that app in place of the automatic panel, in every page that mounts through `mount()` with the panel presented, and nowhere else.
- The viewer bundle stays free of React; the viewer-app contract is a script, an event and a function.
- The Enigma keyboard can be written: it reads the committed bank and whether a drawing runs, and is told when either changes, whoever changed it.
- Every way an app can fail leaves the model visible and names the failure.
- The viewer bundles an app with its own toolchain from a source checkout, and refuses by name elsewhere.

**Non-Goals:**

- An app per sub-assembly, types generated from the model, a theming or component library, a control widget kit, new declared-control kinds.
- Anything for running (worker) programs or posed documents beyond what falls out: the helper's machine hooks read a clocked machine and refuse by name otherwise (an app may still use `useViewer()` and the existing handle on any document).
- A toolchain in an installed copy; a type check of an app's sources; an app in a widget-less export (framework change, design Decision 8 there).

## Decisions

### 1. Where an app runs, and which mounts show it

The app is loaded inside `mount()` when, and only when, the loaded document names one, `driverControls` resolves to `'inline'`, and the render mode is `'continuous'`. The switch is the one that already gates every automatic panel (`showsDriverChrome`, `showsRunControls`), because the app is the model's own panel: a host that builds its own instrument panel (`driverControls: 'none'`) gets neither. Every on-demand mount already must pass `'none'` (`options.ts` 145-147): `machinome snapshot --viewer web` (`capture.py` 144, 179) and a movie's take (`machinome-movie/…/stage/runtime.tsx` 288). The framework's capture staging publishes no app in any case (companion change, Decision 6 there). No new option: none of the hosts needs to separate the two, and the Studio, which wants the app, mounts with the default.

Alternative rejected: an option of its own (`app: 'inline' | 'none'`). No host asks for the app without the panel switch or the reverse.

Under `'none'` the `app` record is validated with the document and its script is never fetched. The handle is whole either way.

### 2. The contract between the viewer and an app

An app is a classic script (an IIFE: it runs on `file:`, on any static host and inside the Studio, with no module loader or CORS). The viewer:

1. creates a `<script>` element with `src = baseUrl + app.script` (the base every model path resolves against, `resolveBaseUrl`), listens on **that element** for the event `machinome:app`, and appends it to the container's document `head`; a `<link rel="stylesheet">` for `app.stylesheet` is appended first and awaited;
2. the script, as it runs, dispatches `new CustomEvent('machinome:app', { detail: { contract: 1, start } })` on `document.currentScript`; the viewer takes `start` synchronously from the event;
3. on the script's `load`, the viewer calls `start(host)` with `host = { contract: 1, element, viewport, viewer, refuse }`: `element` is a fresh `div` filling the container that the app renders into; `viewport` the picture's element (Decision 4); `viewer` the mount's `ViewerHandle`; `refuse(reason)` the app's way to say it cannot go on (Decision 8). `start` returns a disposer function. The script element is then removed from `head`; the stylesheet stays until the app is disposed.

No global name is claimed (two viewers on one page may show two apps, each with its own React), the event is on the script that sent it, and nothing of React crosses the boundary. `contract` lets either side refuse the other by name later; this change knows only 1. Mounting awaits the app's start (or its refusal), so the handle a host receives is a handle on a page that shows the app or names why not. `mount()` does not reject for an app's failure: the model is mounted.

The handle object is built before the app starts: the literal returned at 2478 becomes a `const handle` that the app is given, then returned.

Alternatives rejected: an ES module with `import()` (fails on `file:` and needs CORS on another origin); a global registry keyed by URL (a global name for a contract that needs none); handing React elements across (makes the viewer import React).

### 3. The document's `app` record

The companion change publishes, at the document's top level, either `app: { script: "<file>", stylesheet?: "<file>" }` or `app: { refusal: "<sentence>" }`. The viewer validates it with the document (in `assertRenderable`'s pass): an object carrying exactly one of `script` and `refusal`; `script` and `stylesheet` strings that are relative paths with no `..` segment, no leading `/` and no scheme; `refusal` a non-empty string. Anything else refuses the document by name ("the document's `app` …"), as a malformed `markings` list does (3386-3440), because it is a producer error, not a model to show half of. The record is additive and gated on no document version, as `markings` is; an older viewer, which validates no unknown top-level key (no such check exists in `assertRenderable` or `loadDocument`, 3454-3694), ignores it and shows the automatic panel. That is a truthful, operable rendering of the declared machine, so the record does not raise the document version (the framework's rule: the lowest version the content needs).

### 4. The picture: `viewport`

Only when an app is shown, `mount()` creates the **viewport**, a `div` (`machinome-viewport`) styled `position:relative; overflow:hidden; width:100%; height:100%; min-width:0; min-height:0`, moves the canvas into it with the canvas absolutely placed at its top left (so a canvas sized in pixels never holds its parent open when the place shrinks), moves the observer from the container to the viewport, and sizes the renderer from the viewport's client size. The corner full-screen control is anchored on the viewport (`FullscreenController.place` gains an optional corner element; `fullscreen.ts` 336-354). The full-screen root does not change: the container, or the inspector's composed root (`registerFullscreenRoot`, `inspector.ts` 212), so the whole app goes full screen with its picture. The part outcome label stays in the container, positioned against it as today.

The helper's `<Viewport/>` renders a `div` and, in a layout effect, appends `host.viewport` to it; it does not size it. When no app is shown (none named, refused, between two apps) the viewport, if it exists, is placed back in the container filling it, so the picture is always somewhere. A document with no app never creates a viewport: its DOM, styles, observer and corner control are exactly today's.

### 5. What an app replaces and what stays

While an app is shown the viewer builds no posed, running or clocked panel and no animation bar (`rebuildDriverChrome`, `rebuildRunChrome`, `rebuildClockedChrome` and the bar of `refreshControls` return early on one predicate, `showsApp()`). Kept: the canvas and orbit, the full-screen control (moved, Decision 4), the part affordance (its own switch, `partControls`; clocked documents carry no controls table today), the outcome label, the inspector's rail, sidebar and navigator (they belong to the layout around the viewer's pane, not to the viewer), `$t` playback as the options say (autoplay continues with no bar; an app may call `setTime`/`setSpeed`). The handle is unchanged and whole.

The inspector is kept because the app's area is the area the host gave `mount()`, which in the inspector is its viewer pane (`inspector.ts` 199-221). The reviewer ruled that the rail and sidebar stay ("Rulings").

### 6. The notification: `onMachineChange` and `drawing()`

Verified gap: `MachineHandle` (222-229) has no subscription; `machine()` (2686-2742) wraps the machine standing at the call, so a subscription on it would be lost to a republish that rebuilds the machine (`startMachine` 1307-1364). Added, the smallest pair that serves the keyboard:

- `ViewerHandle.onMachineChange(listener: () => void): () => void`. The listener is called with no argument, once, **after** every accepted operation that changes the clocked machine's committed bank or starts or ends a drawn transition, whatever made it: a request from the panel, the host's `machine().move/trigger/restore/reset`, the clock's transport (one per played frame, inside `clockFrame` 1653) and its step, a followed position of a dragged slider, a drawing's last frame (`drawingFrame` 1638-1642) or its landing by a later gesture, and a load or republish that builds, rebuilds or keeps the machine (`replaceTree`, `manifestChanged` 2611-2614). Not for a refused request, which changes nothing. One accepted operation that both commits and starts a drawing notifies once. It follows ADR-049's doctrine and `AssemblyChangeNotifier`'s shape (`assembly.ts` 102-128): it means "what you last read may be stale", a listener that throws is logged and the others still run, a listener cancelled during a dispatch is skipped, and a listener must not drive the viewer from inside the notification. A document with no clocked machine never notifies. `dispose()` drops every listener and notifies nobody.
- `MachineHandle.drawing(): boolean`: whether a drawn transition is running now (`clockedDrawing !== null`). True from the request that starts it until its last frame or its landing.

The listener carries no value, so no snapshot is copied per frame for a page that is not listening, and the reads a listener makes are the ones a host already has (`machine().state()`, `drawing()`).

Alternatives rejected: a listener receiving the bank (a copy per notification whether wanted or not); per-frame notification of the *shown* bank during a drawing (60 React renders a second the keyboard does not need); `onChange` on `MachineHandle` (lost on republish).

### 7. The helper, `@machinome/viewer/app`

Source: `widget/app/index.tsx` (the public module) and `widget/app/start.tsx` (what the bundler's generated entry calls), outside `src/` so neither the viewer's bundle, nor `currency.py`'s inputs (`src/`, `package.json`, `build.mjs`, `tsconfig.json`), nor `tsconfig.json`'s `include: ["src"]` read them. An app imports it as `import { Viewport, useMachine, usePlay, useViewer } from '@machinome/viewer/app'`, a subpath of the widget's own npm name (`@machinome/viewer`), resolved by the bundler's alias; no new package name is claimed.

- `start(App)` (generated entry) creates a React root on `host.element` and renders, synchronously (`flushSync`), `<HostContext value={host}><Boundary><App/></Boundary></HostContext>`; returns `() => root.unmount()`. After the first commit it checks that `host.viewport` is inside `host.element`; if not, it calls `host.refuse('it places no <Viewport/>, so the model would not be seen')`.
- `<Viewport className? style?/>`: a `div` that adopts `host.viewport` in a layout effect (Decision 4). One per app; a second adopts it away from the first.
- `useViewer()`: `host.viewer`.
- `useMachine(): { bank: Readonly<Record<string, number>>; drawing: boolean }`: the committed bank and whether a transition is drawn, through `useSyncExternalStore` over one store per host. The store subscribes once to `viewer.onMachineChange`; on each notification it reads `viewer.machine()` and builds a new frozen snapshot; `getSnapshot` returns the cached snapshot, which therefore changes identity exactly when a notification arrived; on subscribe it re-reads, so a change between the first render and the subscription is not lost. No tearing: notifications are synchronous at the end of an operation, the snapshot is replaced inside the listener, and React re-renders synchronously from the store when a snapshot changes during a concurrent render. On a document with no clocked machine `useMachine()` throws `this model is not a clocked machine; useMachine() reads a clocked machine's bank`.
- `usePlay(): (name: string) => ClockedRequest`: plays a declared instruction through `viewer.machine().trigger(name)`; a refusal is thrown as the machine's own error (the app catches it where it wants to say so). Same refusal as `useMachine` for a model that is not clocked.
- `Boundary`: a React error boundary around the app; a render error calls `host.refuse(<message>)`.

The names differ from the brief's proposal in one place: one hook, `useMachine()`, returns the two facts the notification carries, where `useBank()` would have returned one of them; the reviewer ruled that it stands ("Rulings").

The helper is not shipped in this change's wheel (Decision 11) and its licence header is the set's, like every file of the package (`tests/test_licence.py`); see Open Questions.

### 8. Refusals: what the reader sees

In every case below the viewport fills the container, a notice `div.machinome-app-refusal` with `role="alert"` stands over the picture's top left reading `This model's app is not shown: <reason>`, the same sentence goes to `console.error`, no automatic panel is built (showing it would present an interface the author replaced as if it were the model's), orbit and the full-screen control work, and `mount()` resolves.

| Case | Reason |
| --- | --- |
| the document's record is a refusal | the producer's sentence verbatim |
| the stylesheet or script fails to load | `<file> could not be loaded (<status or error>)` |
| the script ran and sent no `machinome:app` event, or a contract other than 1 | `<file> is not an app this viewer can start (<what it sent>)` |
| `start` throws | `it failed as it started: <message>` |
| the app calls `host.refuse` (no `<Viewport/>`, a render error, the helper's not-clocked refusal) | the app's sentence |

A refusal after the app started disposes it (deferred to a microtask, since React cannot unmount from inside its own render) before the notice is shown. A malformed record refuses the document (Decision 3), which is the existing mount failure and not this table.

### 9. Republish and reload

`manifestChanged()` and `reload()` reconcile the app after the new document is installed: the same `script` and `stylesheet` → the running app is kept and is notified through `onMachineChange` like any other subscriber (its state survives); a different record → the old app is disposed, its stylesheet removed, the viewport put back in the container, and the new one started (awaited inside the update); a record removed → the app is disposed and the automatic panel built as for a document that never had one; a record added → the panel removed and the app started. A refusal record or a failed new app replaces the running one with the notice. `artifactChanged(path)` for an app file is a no-op already (`tree.ts` 371-393 matches only model and marking paths); the Studio forwards every file published into the build directory through it (`watcher.py` ArtifactWatcher), and then `viewer.json` through `manifestChanged`.

Because the companion change names an app's files by their content, a rebundled app is always a different record, and an unchanged one is the same record.

**On the development page.** The page learns of a build only through `reload` on its socket: `reloader.ts` `checkBuild` fetches `/_build_error` and then calls the callback `develop.ts` gives it, `inspector.viewer.manifestChanged()` (109-113); the page watches nothing else. Observed on the bench (companion `evidence/develop-reload-observation.md`), `reload` is sent today when a builder exits, before the next publishes, so a page shows each edit one edit late. The companion change makes `develop` call the session's `reload()` when `viewer.json` is replaced (its Decision 5b), and republishes an app edit from the builder that holds the model (its Decision 5a). After an app edit the page therefore receives `reload` once the document naming the new app is in place, calls `manifestChanged()`, finds the same root and a different `app` record, keeps every part's geometry (`Geometry is refetched only when its identity changes`), disposes the old app with the picture placed back in the container, and starts the new one, which adopts the same canvas. Nothing in this package's reload channel or server changes.

### 10. Disposal

`dispose()`: the full-screen controller first, as today (2488); then the app (its disposer, which unmounts its React root and so runs its effects' cleanups while the handle still answers), its stylesheet link, its element and the viewport; then `onMachineChange`'s listeners are dropped; then everything else in today's order; `container.replaceChildren()` last. A disposed mount never loads a script whose load was still pending: the pending load is abandoned and its start never called.

### 11. The bundler: the provider operation `bundle`

The framework asks, through its seam, `provider.bundle_app(entry, root, output_dir)` (the seam's Protocol is the companion change's Decision 2). This package answers it in `machinome/viewer/web/app.py`, importing only the standard library, and declares `bundle` in `OPERATIONS`.

`bundle_app` runs `node widget/app-build.mjs`, giving it `{entry, root, output}` as JSON on standard input and reading `{script, stylesheet, inputs}` or `{refusal}` from standard output; it raises `machinome.viewer.ViewerError` with the sentence on any refusal. It returns `{'script': 'app-<h>.js', 'stylesheet': 'app-<h>.css' | None, 'inputs': [<absolute paths of the project files read>]}`.

`app-build.mjs` (licence header; imports esbuild from the widget's own resolution):

- **Entry.** Writes, in a fresh temporary directory, `entry.tsx`: `import App from <entry>; import { start } from <widget>/app/start.tsx; document.currentScript.dispatchEvent(new CustomEvent('machinome:app', { detail: { contract: 1, start: (host) => start(App, host) } }));`. The entry must be inside `root` and exist; its default export is the app component.
- **esbuild options.** `bundle`, `format: 'iife'`, `platform: 'browser'`, `target: 'es2020'` (the widget's), `minify: true`, `jsx: 'automatic'`, `define: { 'process.env.NODE_ENV': '"production"' }`, `sourcemap: false`, `metafile: true`, `write: false`, `absWorkingDir` the temporary directory, loaders for `.ts .tsx .js .jsx .css`.
- **One React.** `alias` maps `react`, `react/jsx-runtime`, `react-dom`, `react-dom/client` and `@machinome/viewer/app` to the files the **widget** resolves them to (`createRequire(<widget>/package.json).resolve(...)`), so the app, the helper and React DOM share one copy wherever npm placed it (hoisted at the root or nested under the widget); `react-dom`'s own `scheduler` resolves from its own directory.
- **What may be imported.** A plugin `onResolve` refuses any bare specifier other than those five, naming it: `<importer>: imports 'three'; an app imports its own files, react, react-dom and @machinome/viewer/app`. After the build, every input in the metafile that is not the widget's (`app/`, the resolved React packages) must lie inside `root` (real paths); one outside is refused naming it and the root. Assets other than CSS (images, fonts) are not loaded: an import of one is refused by esbuild's own "no loader" error, reported as the refusal.
- **Names and bytes.** The script's bytes are the banner plus esbuild's output; the stylesheet exists only when the app imports CSS. `h` is the first 16 hex digits of the SHA-256 of the script's bytes (and of the stylesheet's, for its own name). Minified output carries no file path, so the same sources at two paths bundle to the same bytes; a test proves it (Decision 15, U7), and if it fails the bundler must rename esbuild's path keys as the movie's `renameOutput` does instead of relaxing the test.
- **Notices.** The banner: `machinome-viewer app bundle, built by machinome-viewer <version>`; `Bundles React and React DOM <version> - Copyright (c) Meta Platforms, Inc. and affiliates - MIT License - https://github.com/facebook/react/blob/main/LICENSE`; `Bundles @machinome/viewer/app - Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes - SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+ - Source: https://github.com/machinome/machinome`. esbuild's default `legalComments` (end of file) keeps React's own comments too.
- **Writes.** Each file is written to `output` through a temporary name and renamed (the Studio's `ArtifactWatcher` reads renames as publications), except that a file already holding the same bytes under the same name is left untouched, so an unchanged app publishes nothing; nothing else is written there; the temporary directory is removed.
- **Errors.** esbuild's messages become one refusal: `the app <entry relative to root> does not build:\n<file:line:column: text>…`.

`app.py`'s refusals, before Node runs:

- no `widget/app-build.mjs` or `widget/app/` (an installed wheel): `this machinome-viewer <version> was installed without the toolchain that bundles a model's app; in this release an app is bundled only from a source checkout of the machinome repository with its JavaScript dependencies installed`;
- `esbuild`, `react` or `react-dom` not found from the widget upward (the walk `currency._build_program_installed` makes, extended): `the viewer's JavaScript dependencies are not installed (<missing>); install them with npm ci in <workspace root>`, the root found by `packaging.workspace_root`;
- no `node` on `PATH`: `bundling a model's app needs Node.js, and none is on the PATH`.

Nothing installs a dependency, as `currency.py` promises (46-63). The wheel excludes `widget/app/*`, `widget/app-build.mjs` and `widget/tsconfig.app.json` beside the existing exclusions, so an installed copy answers the first refusal rather than a half toolchain. A later step that installs the toolchain into an installed copy changes only where these files and dependencies are found; nothing here fixes a shape for it.

### 12. Where React comes from, and the Studio

The widget's `package.json` gains `"react": "19.3.0"` and `"react-dom": "19.3.0"` under `dependencies` (they are what an app bundle carries at run time) and `"@types/react": "19.3.0"`, `"@types/react-dom": "19.3.0"` under `devDependencies`, pinned exactly, as the movie pins them, so an app's bytes do not move with a range. The root `package-lock.json` is updated by one `npm install` at the workspace root (`npm install --workspace packages/machinome-viewer/machinome/viewer/web/widget react@19.3.0 react-dom@19.3.0 && npm install --workspace … -D @types/react@19.3.0 @types/react-dom@19.3.0`), run once on the bench after confirming its `node_modules` is a directory and not a symbolic link (`packaging.build_frontend` 79-86 refuses the same case). npm may hoist the widget's React to the root or nest it under the widget; the bundler does not care (Decision 11, "One React"). `npm ci` at a workspace root then installs it for every checkout. The viewer's own bundle does not import React; a test asserts `dist/machinome-viewer.js` carries none (Decision 15, U9).

The Studio needs nothing for an app to be shown: it mounts with the panel presented and serves every file of the build directory (`app.py` 859-867), and the companion change bundles the app into that directory in `machinome build`, which the Studio runs (`preparation.py` 300). What it lacks is a rebuild when an app's file changes: its `ModelWatcher` rebuilds on `.py` events only (`watcher.py` 205). That is a follow-up in the Studio's own package (`packages/machinome-studio`), not made here.

### 13. API 31

`machinomeViewerApi` becomes 31: a host may require the app capability and `onMachineChange`/`drawing()`. Document versions stay 1 to 14. A new requirement states the gate, as the conditional-colour change did ("Conditional color has an explicit reader capability"); the baseline requirement "The viewer declares its API version", whose text still names 19, is not restated here.

### 14. The manual and the changelog

Under `skills/write-the-manual/SKILL.md` (workspace): a new how-to, `packages/machinome/docs/howto/give-a-model-its-app.rst` (`.. needs:: viewer`; the companion change writes the declaration half of it, this change the helper and what the page shows; one page, written once, owned by both changes' tasks); `docs/reference/viewer/viewer-handle.rst` (`onMachineChange`), `clocked.rst` (`drawing()`), `mount.rst` (`driverControls` also gates a model's app), `layouts.rst` (the inspector keeps its sidebar beside an app), `compatibility.rst` (API 31), `troubleshooting.rst` (the refusals of Decision 8 and 11); a new `docs/reference/viewer/app.rst` for the helper's four names; `howto/browser-viewer.rst` (a model with its own app shows it instead of the panel); `howto/embed-the-viewer.rst` (a host's `driverControls: 'none'` suppresses the app too). The changelog bullet is written in the same cycle under "Unreleased" in `packages/machinome-viewer/CHANGELOG.md`.

### 15. Tests, red first

Widget (vitest, jsdom), run singly from `widget/`:

- `src/machine-change.test.ts` (on the `draw-on-change`/`follow-the-slider` bench pattern: `vi.mock('three')` counting renderer, stubbed `ResizeObserver` and `fetch`, hand-written clocked documents): M1 a host `move` notifies once, after the bank changed; M2 `trigger` of a drawn instruction notifies at the request with `drawing()` true, and again at the last frame with `drawing()` false; M3 a refused request notifies nothing; M4 a played clock notifies once per frame; M5 a republish that rebuilds the machine notifies, and a listener registered before it still hears the new machine; M6 a throwing listener does not stop the next; M7 `dispose()` notifies nobody; M8 a posed document never notifies. Red on the base: `onMachineChange`/`drawing` do not exist (read through the namespace so the file loads).
- `src/app.test.ts` (the app loader against fake scripts that dispatch the event, through a seam `mountAppWith` as `inspector.ts` uses `mountInspectorWith`): A1 a document with an app builds no panel and no animation bar and the app's element fills the container; A2 the canvas is in the viewport and the observer observes the viewport; A3 the corner control is in the viewport; A4 each row of Decision 8's table shows its notice, resolves the mount and builds no panel; A5 a malformed record refuses the document naming `app`; A6 `driverControls: 'none'` fetches no script; A7 republish with the same record keeps the app (its disposer not called), with another record disposes and starts, with none rebuilds the panel; A8 `dispose()` calls the app's disposer before the handle is released and removes the stylesheet; A9 a document without an app has today's DOM (canvas a child of the container, no viewport).
- `app/app.test.tsx` (jsdom, real React): H1 `useMachine` re-renders on a notification with a new bank and stays identical without one; H2 a change between render and subscribe is caught; H3 `usePlay` calls `trigger` and rethrows its refusal; H4 `<Viewport/>` adopts the viewport; an app with none refuses; H5 a render error refuses with its message; H6 `useMachine` on a non-clocked handle refuses by name.

Python (`packages/machinome-viewer/tests`):

- `tests/test_app_bundle.py`: U1 the fixture app bundles to a script and a stylesheet with content names; U2 the script opens with the banner naming React's MIT licence and the helper's grant; U3 an import of `three` is refused naming it; U4 an import outside the root is refused naming the file; U5 a syntax error is refused with its file and line; U6 missing toolchain files and missing dependencies are refused with their sentences (a copy of the widget without `app-build.mjs`; a fake widget path with no `node_modules`); U7 the fixture copied to two different directories bundles to byte-identical files; U8 `inputs` lists the fixture's own files and nothing of the widget; U9 `dist/machinome-viewer.js` contains no React (`react.production`, `__SECRET_INTERNALS`, `ReactCurrentDispatcher` absent); U10 the provider declares `bundle` and its `CONTRACT` is unchanged. U1-U8 skip, saying why, where Node or the dependencies are absent.
- `tests/test_model_app.py` (Chromium, the `test_lock_document.py` and `test_calculator_document.py` pattern): the existing fixture `tests/fixtures/calculator/` (the framework's clocked `Calculator`, a version 8 build with the instructions `Set four` and `Stroke` and the states `w0.digit` to `w3.digit`, which stand for the Enigma's window numbers) is reused verbatim, and a new `tests/fixtures/calculator-app/` holds only the app's sources (`app/index.tsx`, `app/Readout.tsx`, `app/app.css`, and the refused `app/broken.tsx` and `app/imports-three.tsx`). The test copies the build to a temporary directory, bundles the app into it with `bundle_app`, writes the returned record into the copy's `viewer.json`, serves it, and in the export page and in `mountDevelopment` checks: B1 the app's buttons are drawn and no `.clocked-controls` panel; B2 clicking `Stroke` disables both buttons until the drawing lands, then the readouts show the committed digits; B3 the canvas resizes with the viewport; B4 a refusal record shows the notice and the model's canvas has drawn pixels; B5 a mount of the same document with `driverControls: 'none'` shows neither the app nor a panel and requests no app script; B6 the open development page shows the edited app, the picture standing: the copy is served by this package's own `Session` (`session.py`), the development page is opened, the fixture's `Readout.tsx` is edited and bundled again into the copy, the copy's `viewer.json` is replaced atomically with the new record, and `session.reload()` is called, as the companion's `develop` does; the page then shows the new text without a page load (a marker set on `window` survives), the canvas is the same element with drawn pixels, no model file is requested after the edit, and the previous app's stylesheet is gone. B1-B6 are red on the base (no app is loaded).

The end-to-end proof across both packages, a fixture model declaring an app built and exported by the framework and driven in Chromium, is the companion change's (its Decision 10).

## Risks / Trade-offs

- [An app's global CSS can restyle the host page, the Studio's included] → the manual says an app's stylesheet applies to the page it is shown in and should scope its selectors under its own root class; no scoping is imposed.
- [A slow app script delays `mount()`'s resolution] → the picture is drawn while it loads; the bundle is one minified file of about 150 kB, most of it React.
- [Bundling costs a Node start and an esbuild run per publication] → measured on the bench in tasks 5.3 and recorded; esbuild is not the cost (milliseconds), Node's start and React's parse are; the content name makes an unchanged app republish nothing.
- [Two apps on one page carry two Reacts] → each is self-contained by design; the cost is paid only by a page that mounts two models with apps.
- [The helper's grant travels into a project's bundle] → stated in the banner; the pilot's question below.
- [A notification per played clock frame] → it is one call per frame to a listener that reads the bank; a page with no listener pays a loop over an empty set.
- [The panel is not shown when an app fails] → deliberate (Decision 8); the notice names the failure and the model stays visible.

## Decision record

After the implementation confirms them, ADRs in `workflow/adrs/EXPORT/` (next free numbers after ADR-083): a model's app is a script the viewer starts inside `mount()` through a framework-neutral contract (Decisions 1-5, 8-10); the clocked machine notifies a page of a changed bank or drawing on the mount handle (Decision 6); the viewer bundles a model's app with its own toolchain and refuses where it has none (Decisions 11-12). None is written before the implementation.

## Rulings (reviewer, 22 November 2026, under the pilot's standing delegation)

- The inspector's rail and sidebar stay beside an app (Decision 5).
- `useMachine()` returning `{ bank, drawing }` stands (Decision 7).
- No type check of an app's sources in this change.

## Open Questions

- For the pilot: an app bundle combines the project's own code with the helper's code, which carries the set's grant, GPL-2.0-or-later OR CERN-OHL-S-2.0+ (Decision 7). Should the helper carry a permissive grant instead? Kept as designed until the pilot answers; it does not block.

## Found while proposing, out of scope

- The development page is told of a build before the build publishes, so it shows each edit one edit late. Observed on the bench and fixed in the framework for every published document, the app's path included (companion design Decision 5 and `evidence/develop-reload-observation.md`); nothing in this package changes for it.
