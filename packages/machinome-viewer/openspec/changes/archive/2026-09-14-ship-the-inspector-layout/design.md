# Design — ship the inspector layout

## Context

Cycle 3 of the pilot's 2026-09-14 decision. Cycle 1 published the
navigation state (ADR-049), cycle 2 the navigator component (ADR-050),
and neither is mounted anywhere in this repository. This cycle composes
them into a layout, puts that layout on the export page behind an opt-in
attribute, and makes the development page a static file over the same
layout — which is what finally lets Create React App and React leave the
package.

What exists here:

- `mount(target, sourceUrl, options) -> Promise<ViewerHandle>`
  (`viewer.ts:197-202`). It takes the container over: sets
  `position: relative` on it (`:214`), appends the canvas (`:225`),
  appends the driver and run chrome into it (`:1233`, `:1767`, `:1778`),
  observes it with a `ResizeObserver` (`:768`), and empties it on
  `dispose()` (`:821`).
- `mountNavigator(target, viewer, options) -> NavigatorHandle`
  (`navigator.ts:213`), synchronous, options `label` / `fullAssembly` /
  `className` / `styles`, handle `{ dispose() }`.
- `widget.ts:20-42`: the auto-mount. It reads `?t=` and `?autoplay=0`
  into `ViewerOptions`, then `mount()`s every `[data-solid-widget]`
  element, writing `solid-widget: <message>` into the element on failure
  (`:37`).
- `widget/index.html:22`: one `<div id="solid-widget"
  data-solid-widget="manifest.json">`, sized `100%/100%` by the page's
  own `<style>`.
- `server.py`: `/ws/reload` greeting with `"reload"` (`:121-130`),
  `/_build_error` (`:132-139`), `/build/{path}` (`:141-153`), `/_viewer`
  and `/_viewer/bundle.js` (`:155-171`), then either the built CRA app or
  a 503 remedy at `/` (`:173-192`), or an httpx proxy to the npm dev
  server (`:194-208`).
- `app/`: `App.tsx` (a ref, a `ViewerShell`, a `Reloader`, and an error
  string that replaces the viewer), `viewerShell.ts` (fetch `/_viewer`,
  inject `/_viewer/bundle.js`, `mount('/build/viewer.json', {animation:
  'inline', autoplay: true})`, title from `root.name`), `reloader.ts`
  (the socket, the retry, the banner, `/_build_error`).
- `capture.py:70-90` builds `mount_options` with `driverControls: 'none'`
  and `capture.py:151-174` writes a page that calls
  `SolidNodeWidget.mount`. Neither is touched by anything below.

What the framework does, verified by reading it (it is another
repository and this change must not need one in it):

- `solid develop` runs `viewer_command() + ['serve', '--build-dir', DIR]`
  and appends `--start-frontend` **only** under its own `--web-dev`
  (`solid_node/manager/develop.py:42-52`, `:70-71`).
- `solid export` copies `viewer_bundle.bundle_path()` and
  `viewer_bundle.index_path()` into the export directory
  (`solid_node/core/export.py:176-178`).
- The Sphinx directive completes an export from `WIDGET_FILES =
  ('index.html', 'solid-widget.js')` (`solid_node/sphinx.py:50`,
  `:208-225`) and builds a query string of `t=` and `autoplay=0` only
  (`:131-135`).

So: two files, the same two names, and a query-string channel that
carries whatever the page's script chooses to read.

## 1. The layout's interface

### D1. `mountInspector`: async, one target, one source, options that extend the viewer's

```ts
export interface InspectorOptions extends ViewerOptions {
  /** Whether the assembly sidebar starts open; default 'collapsed'. */
  sidebar?: 'collapsed' | 'open';
  /** The navigator's own options, passed through untouched. */
  navigator?: NavigatorOptions;
  /** Inject the layout's stylesheet; default 'inject'. Also the default
   * for `navigator.styles`. */
  styles?: 'inject' | 'none';
}

export interface InspectorHandle {
  /** The mounted viewer. The whole ViewerHandle, not a copy of part of it. */
  viewer: ViewerHandle;
  /** The mounted navigator. */
  navigator: NavigatorHandle;
  /** Whether the sidebar is open right now. */
  sidebarOpen(): boolean;
  /** Open or close the sidebar, as the toggle does. */
  setSidebar(open: boolean): void;
  /** Dispose navigator then viewer, and empty the target. Idempotent. */
  dispose(): void;
}

export function mountInspector(
  target: HTMLElement | string,
  sourceUrl: string,
  options?: InspectorOptions,
): Promise<InspectorHandle>;
```

**Async, because `mount` is.** The layout builds its skeleton
synchronously, `await`s `mount()` on the viewer pane, then mounts the
navigator on the handle that came back and returns. A navigator cannot
exist before a viewer handle does, so there is no honest synchronous
version.

**If the viewer refuses, the layout leaves nothing behind.** `mount()`
rejects on an unreadable document, an unevaluable technology, an
undeclared driver id (`viewer.ts`'s `assertRenderable` surface). The
layout catches, empties the target, and rethrows the original error — so
a caller sees exactly the error `mount` would have given it and the page
does not keep a sidebar around a viewer that never existed. The
auto-mount path then writes it into the element as it already does
(`widget.ts:36-39`).

### D2. The handle exposes the two handles; it does not wrap them

`InspectorHandle` has `viewer` and `navigator` as fields.

*Alternative that lost:* `InspectorHandle extends ViewerHandle`, or a
handle that re-declares the viewer's operations and forwards them.
`ViewerHandle` is 25 members today (`viewer.ts:133-173`) and grows every
cycle; a forwarding layer would have to be extended by every future
viewer change, and a missed one is a capability a host silently cannot
reach through the layout. Exposing the handle keeps exactly one
declaration of the viewer's API and lets a host write
`inspector.viewer.run()` with the types it already has.

*Alternative that lost:* return `{ dispose() }` only, like
`NavigatorHandle`. A development page that has to name its tab from the
model, and a studio that may one day drive a run, both need the viewer.

**Disposal order is navigator, then viewer, then the target.** The
navigator cancels its subscription first so the viewer's own
`assemblyChanges.dispose()` has nothing left to release, then the viewer
tears down its renderer and empties *its* pane, then the layout empties
the target (`target.replaceChildren()`, the idiom at `viewer.ts:821`).
Idempotent, and safe if a host disposed either inner handle first — the
navigator's own `dispose()` is already idempotent, and the viewer's is
(`viewer.ts:797-801`).

### D3. `sidebar` is a two-value string, not a boolean

`'collapsed' | 'open'`, matching `animation`, `driverControls` and
`styles` — this package spells a presentation choice as a named mode, and
`sidebar: false` would not say whether false means "closed" or "absent".
There is no third value for "no sidebar at all": a host that wants the
plain viewer calls `mount`, which is the thing it already has.

Default `'collapsed'`, the pilot's decision. The reason it is the right
default beyond the instruction: the export page is often an `<iframe>` in
documentation at 480 px tall (`sphinx.py` `DEFAULT_HEIGHT`), where a
260 px sidebar would take most of the width from the model.

### D4. `navigator` is a nested block, not flattened options

`NavigatorOptions.className` and `ViewerOptions.className` mean different
things (the navigator's root element; the viewer's **canvas**,
`viewer.ts:219`), and `label` would be ambiguous between the tree and the
layout. Nesting keeps each option's meaning exactly the one its own
component published, and `InspectorOptions extends ViewerOptions` keeps
the promise that the layout takes everything `mount` takes.

The toggle's accessible name is `options.navigator?.label ?? 'Assembly'`
— one name for one thing, rather than a second option that can disagree
with the tree's own label.

`styles` is the layout's own; it also becomes the default for
`navigator.styles`, so one `styles: 'none'` covers a page under a
Content-Security-Policy that forbids inline style blocks, and a host that
wants finer control still has both.

## 2. What it builds

### D5. Four elements, and the viewer owns exactly one of them

```
<div class="solid-inspector">                     ← the target's only child
  <div class="solid-inspector-rail">              ← always present
    <button class="solid-inspector-toggle"
            aria-expanded="false"
            aria-controls="solid-inspector-sidebar-N">Assembly</button>
  </div>
  <div class="solid-inspector-sidebar"
       id="solid-inspector-sidebar-N" hidden>     ← the navigator's host
  </div>
  <div class="solid-inspector-viewer"></div>      ← mount()'s container
</div>
```

The viewer is given `.solid-inspector-viewer` and nothing else. It sets
`position: relative` on it, appends its canvas and its chrome into it,
and empties it on dispose — all of which now happen inside a pane the
layout owns, rather than on the host's element. That is the whole reason
the viewer gets a pane of its own instead of the layout decorating the
target: the viewer's `dispose()` calls `replaceChildren()` on its
container (`viewer.ts:821`), which would delete the sidebar if the two
shared an element.

**The rail is always in the DOM, in both states.** It carries the toggle
and nothing else. Consequences that matter:

1. The toggle element is never created or destroyed by a toggle, so
   keyboard focus stays on it across open and close. A disclosure that
   drops focus to `<body>` on every use is unusable from the keyboard.
2. The sidebar can be `hidden` — out of the layout and out of the
   accessibility tree — without hiding the only way to bring it back.

### D6. Collapsing removes the sidebar from layout; it does not overlay it

`.solid-inspector` is `display: flex`; the sidebar is a flex item with
`flex: 0 0 var(--solid-inspector-sidebar-width)`, and collapsing sets the
`hidden` property on it (`display: none` via the UA sheet, reinforced by
the stylesheet). The viewer pane is `flex: 1 1 auto; min-width: 0`, so it
grows into the space.

Two things follow, and both are the point:

- **The model is never covered.** An overlaid sidebar would sit on top of
  the canvas, over the very geometry a maker opened the tree to look at,
  and the driver chrome is already in that corner (`viewer.ts:1233`, the
  panel is `position: absolute; left: 0; top: 0`).
- **The viewer resizes with no code here.** `mount()` installs a
  `ResizeObserver` on its container and recomputes `renderer.setSize`,
  `camera.aspect` and the projection matrix on every box change
  (`viewer.ts:757-769`). Changing the pane's width *is* a box change, so
  the observer fires and the canvas follows. The layout writes no resize
  handler, listens to no `resize` event, and calls nothing on the handle.

*Alternative that lost:* animating the width with a CSS transition. It
would fire the observer dozens of times during the animation, each
resizing a WebGL renderer. Not worth it; the toggle is instant.

### D7. The sidebar remembers nothing

No `localStorage`, no `sessionStorage`, no cookie, no history entry, no
rewriting of the URL. The state a page loads with is exactly what its
options and its query string say. Two reasons: an export directory is a
static artifact that must look the same to the maker who publishes it and
the reader who opens it, and a remembered sidebar in one `<iframe>` on a
documentation page would silently change every other embed of the same
export on the same origin.

## 3. How a page asks for it

### D8. `data-solid-layout`, with `?layout=` as its twin

The auto-mount (`widget.ts:20-42`) grows one decision per element:

| source | value | effect |
| --- | --- | --- |
| no attribute, no query | — | `mount()` — **today's behaviour, unchanged** |
| `data-solid-layout="viewer"` | `viewer` | `mount()` |
| `data-solid-layout="inspector"` | `inspector` | `mountInspector()` |
| `?layout=inspector` / `?layout=viewer` | | overrides the attribute |
| `data-solid-sidebar="open"` \| `"collapsed"` | | the initial sidebar |
| `?sidebar=open` \| `?sidebar=collapsed` | | overrides the attribute |

**The default is the plain viewer.** Every page that exists — every
hand-written embed, every already-exported directory whose `index.html`
predates this change, the e2e harness, the capture page — carries no
`data-solid-layout` and gets exactly what it gets today. That is the
compatibility promise of ADR-035's published names, and it is worth more
than a nicer default.

**The query string wins over the attribute** because the attribute is
what the page ships with and the query string is what a particular link
asks for — the same relationship `?t=` already has with the document's
own animation. It is also the only channel a Sphinx directive or an
`<iframe src>` can reach, since the framework copies `index.html`
verbatim.

**An unrecognised value is refused by name**, not silently ignored:
`solid-widget: unknown layout "sidebar"` written into the element, the
shape the auto-mount already uses for a failed mount (`widget.ts:37`). A
typo that silently renders the old layout is a bug a maker cannot see.

`data-solid-widget` itself is untouched: same attribute, same meaning,
same element. `index.html` gains one attribute on line 22 and nothing
else, and the file keeps its name, so `WIDGET_FILES` and `export.py`
copy the same two files.

*Alternative that lost:* a second published page (`inspector.html`) beside
`index.html`. It would be a third file for the framework to copy — a
change to `WIDGET_FILES` and `export.py` in an Apache-2.0 repository for
an AGPL asset — to say what one attribute says.

*Alternative that lost:* making the inspector the default and letting a
page opt out. It would change what every existing export shows the moment
someone upgrades the viewer that completes it, which is precisely the
silent change the attribute exists to avoid.

## 4. The development page

### D9. Where the page lives: `solid_node_viewer/widget/develop.html`

Beside the export page, in the directory that already holds the bundle
and `index.html`.

- `MANIFEST.in:7` already does `recursive-include solid_node_viewer/widget *`,
  so the file ships with no packaging change at all.
- `bundle.py` gains `develop_page_path()` beside `index_path()`
  (`bundle.py:30-32`) — one accessor, the same shape.
- It is authored against the bundle it sits next to, and its version can
  never drift from it.

*Alternative that lost:* `solid_node_viewer/develop/index.html`. A new
directory, a new `MANIFEST.in` stanza and a new package-data path for one
file, whose only argument is that `widget/` is named for the module and
not for "the frontend". The directory already holds the export page,
which is not the widget module either.

**It is not a published name.** `index.html` and `solid-widget.js` are
compatibility contracts because the framework copies them by name;
`develop.html` is served by this package's own server at `/` and named
nowhere else.

### D10. The page is twenty lines; everything testable is in the bundle

```html
<div id="root"></div>
<script>
  fetch('/_viewer').then(r => r.json()).then(status => {
    if (!status.available) { showRemedy(status.remedy); return; }
    loadScript('/_viewer/bundle.js')
      .then(() => SolidNodeWidget.mountDevelopment('#root'))
      .catch(showRemedy);
  });
</script>
```

The availability check and the script injection **must** be in the page:
they are what runs when the bundle is absent, and code in the bundle
cannot report that the bundle is missing. Everything after it is in the
bundle, where vitest can reach it.

```ts
export interface DevelopmentOptions extends InspectorOptions {
  /** The document; default '/build/viewer.json'. */
  sourceUrl?: string;
}
export interface DevelopmentHandle {
  inspector: InspectorHandle;
  dispose(): void;
}
export function mountDevelopment(
  target: HTMLElement | string,
  options?: DevelopmentOptions,
): Promise<DevelopmentHandle>;
```

`mountDevelopment` does exactly what `App.tsx` + `viewerShell.ts` did,
minus the bundle loading:

1. `mountInspector(target, '/build/viewer.json', { animation: 'inline',
   autoplay: true, sidebar: 'open', ...options })` — the same two options
   `viewerShell.ts:46-48` passes, the inspector instead of the plain
   viewer, and the sidebar open: the development page is where a maker
   inspects the machine they are building, and nothing embeds it, so the
   export page's collapsed default (D3) does not apply. The page passes
   `?sidebar=collapsed` through to `options` for a link that wants the
   model alone (reviewer decision, 2026-09-14).
2. `document.title` from the document's `root.name`, split on capitals
   exactly as `viewerShell.ts:89-93` does. It refetches `/build/viewer.json`,
   as the shell did; the server sends `Cache-Control: no-store` for a
   republished document in the suite's own server and the browser's cache
   is not the concern here.
3. `new Reloader(showError, () => inspector.viewer.manifestChanged())` —
   the partial update, unchanged (D12).

`mountDevelopment` is published on the global because a host serving its
own page over this server (the shop floor is one) should not have to
reproduce those three steps. It is the second capability behind the
version bump.

*Alternative that lost:* a second esbuild entry point producing
`develop.js`. It would be a second published file, and
`viewer-distribution`'s "exactly the page and the one bundle" is a
requirement, not a habit. The brief's preference and the spec agree.

*Alternative that lost:* putting the whole page inline in `develop.html`.
It would put the reloader — the one piece with a real state machine and
an existing test suite — in an HTML file no test runner loads.

### D11. The build error is a pane over a viewer that stays mounted

`App.tsx:28` renders `{error ? <pre> : <div ref={host}>}` — a build error
unmounts the viewer, and clearing it mounts a new one that refetches
every model and loses the camera and any live run.

The static page shows `.solid-inspector-error` (a `<pre>` positioned over
the layout, scrollable, dismissed when the error clears) and leaves the
inspector mounted underneath.

This is a **deliberate behaviour change**, called out in the proposal and
given its own scenario so the pilot ratifies it rather than discovering
it. The ratified requirement says the page "SHALL … show build errors or
the missing-bundle remedy in its error pane" — it does — and the run
requirement in the same spec says a cosmetic edit must leave the machine
exactly where it was, which a teardown on the *previous* failed save
makes impossible. The old behaviour was a consequence of React state, not
a decision.

### D12. Partial reload is not ported, moved or rewritten

The reload path is: server greets `"reload"` on the socket → `checkBuild()`
fetches `/_build_error` → no error → `reload()` → `handle.manifestChanged()`.
`manifestChanged()` is the widget's targeted update (ADR-037), and it is
not touched by this change. What moves is the 150 lines that decide *when*
to call it.

`widget/src/reloader.ts` is `app/src/reloader.ts` with one type changed:
`setError: React.Dispatch<React.SetStateAction<string>>` becomes
`(message: string) => void`. Everything observable is held identical and
asserted so:

| thing | value | where it is today |
| --- | --- | --- |
| socket URL | `<ws>://<host>/ws/reload` | `reloader.ts:64-70` |
| retry interval | 2000 ms, indefinitely | `:16`, `:108` |
| initial grace | 2 failed attempts before the banner | `:22`, `:101-105` |
| drop after a live connection | banner immediately | `:96-100` |
| banner element | `id="solid-node-offline-banner"`, `class="reload-offline-banner"` | `:24`, `:119-121` |
| banner text | `solid develop is not running — model may be stale` | `:25` |
| reconnect | `checkBuild()` then hide the banner | `:77-84` |
| `"reload"` message | `checkBuild()` | `:87-91` |
| error surface | `/_build_error`, `tstamp` dedupe | `:135-145` |

`app/src/reloader.test.ts`'s nine cases move to
`widget/src/reloader.test.ts` unchanged in intent, jest → vitest
(`jest.useFakeTimers()` → `vi.useFakeTimers()`, `jest.fn` → `vi.fn`),
under the `@vitest-environment jsdom` pragma cycle 2 established.

**The banner injects its own stylesheet**, `<style
id="solid-node-reloader-style">` with `.reload-offline-banner` and
`--solid-reload-*` properties — the third component in this bundle to
follow the pattern ADR-050 set, and the reason `mountDevelopment` is
self-contained rather than needing rules from the page it is called from.
The rule is `App.css`'s, carried over verbatim in effect: a fixed red
strip across the top with `pointer-events: none`, so the stale model
underneath stays fully interactive.

### D13. What the server does now

```
GET /                 → FileResponse(develop_page_path())
GET /build/{path}     → unchanged
GET /_build_error     → unchanged
GET /_viewer          → unchanged
GET /_viewer/bundle.js→ unchanged
WS  /ws/reload        → unchanged
```

Gone: the `StaticFiles` mount at `/` (the page loads nothing but the
bundle route and the build routes), `WebDevServer` (`server.py:75-91`),
`_setup_proxy_server` and `_proxy` (`:194-208`), and with them the only
use of `httpx` in the package.

Kept, deliberately: `WebViewer(build_dir, dev=..., port=..., frontend=...)`
accepts the same four arguments, `frontend_port()`,
`DEFAULT_FRONTEND_PORT` and `SOLID_NODE_FRONTEND_PORT` still resolve.
`dev` is ignored. The reason is D14, and it also keeps
`test_server.py:83-89`'s environment test meaningful.

A defensive `/` remains for the file being absent — it can only mean a
broken installation, but the route answering 503 with the file's path is
cheaper than a `FileResponse` raising inside uvicorn, and it is the same
shape the unbuilt-app route had (`server.py:179-186`).

### D14. The three frontend flags stay, as no-ops, because a released framework passes one

solid-node 0.6.0 is on PyPI. Its `solid develop --web-dev` runs

```
solid-node-viewer serve --build-dir <dir> --start-frontend
```

(`solid_node/manager/develop.py:49-51`). A viewer that rejects that flag
turns a working framework command into an argparse error on a flag the
maker did not type. So `serve` keeps `--dev`, `--start-frontend` and
`--frontend-port`; they parse, they change nothing, and `run_serve` logs
one line naming the flag and saying the development page is now static
and there is no npm dev server to proxy.

This is written into the `development-server` spec rather than left as a
kindness in the code, because a later cycle tidying "unused" flags would
otherwise break a released framework and pass its own tests.

`--frontend-port` and `SOLID_NODE_FRONTEND_PORT` keep being *read* for
the same reason: a maker's shell, a `.env` or a script may set them, and
a viewer that fails on an environment variable it no longer needs is a
worse citizen than one that ignores it.

*Alternative that lost:* change the framework. The framework worktree
exists for it, but it would make a viewer release depend on a framework
release for a flag that costs three lines to accept, and it would leave
every already-installed 0.6.0 broken.

## 5. Packaging, after the app

- `packaging.py`: `FRONTENDS = (WIDGET,)`; `DEVELOPMENT_APP` deleted.
  `build_distribution_frontends()` and `build_missing_frontends()` keep
  their shape and iterate one frontend. An sdist builds the bundle; a
  wheel from a checkout that already has `dist/solid-widget.js` builds
  nothing. Installing still needs no npm, which is the requirement.
- `MANIFEST.in`: the two `solid_node_viewer/app` lines go.
- `pyproject.toml`: `httpx` moves from `dependencies` to the `dev`
  extra. It was there for `_proxy` alone; `fastapi.testclient` needs it,
  which is why it lands in `dev` rather than disappearing. *This one is
  separable:* it is its own task, and reverting it costs one line if the
  reviewer would rather not narrow a released dependency set.
- `bundle.py`: `APP_DIR` and `app_build_path()` deleted,
  `develop_page_path()` added. `describe()` is **unchanged** — the entry
  point's mapping is a contract with the framework and gains no key.

## 6. Where the logic lives so a test can reach it

Four surfaces, and the deletion is proved by a fifth:

1. **`inspector.test.ts` — jsdom, per file.** The layout against a stub:
   `mountInspector` cannot run `mount()` in jsdom (no WebGL), so the
   module takes its two collaborators through a seam — an internal
   `mountInspectorWith(mount, mountNavigator, …)` that the exported
   `mountInspector` calls with the real ones. The test asserts the
   element structure, the toggle's `aria-expanded`/`aria-controls`, the
   sidebar's `hidden` across toggles, focus staying on the toggle, the
   navigator being mounted into the sidebar with the passed options, the
   stylesheet injected once across two mounts and not at all under
   `styles: 'none'`, the handle exposing both inner handles, disposal
   order and idempotence, and a rejecting `mount` leaving the target
   empty and rethrowing.
2. **`reloader.test.ts` — jsdom, per file.** The nine ported cases, plus
   one the port adds: the injected stylesheet.
3. **`develop.test.ts` — jsdom, per file.** `mountDevelopment` against a
   stubbed inspector and a stubbed `fetch`: the source URL and the two
   options, the title from `root.name`, the reloader's reload calling
   `manifestChanged()` and not `reload()`, and the error pane appearing
   and clearing.
4. **`tests/test_widget_e2e.py` — Chromium, the real bundle.** The
   export page with `data-solid-layout="inspector"`: the sidebar
   collapsed, the toggle opening it, the tree present, the canvas wider
   after collapsing than before, `?sidebar=open` shipping it open, a page
   with no attribute still mounting a plain viewer with no
   `.solid-inspector` in it.
5. **`tests/test_server.py` — Chromium against the served page.** The
   skipped test becomes real: the development page renders the spinner's
   colours, and a **republished `viewer.json` updates the model with no
   page load** (asserted by stamping the page — e.g. a property set on
   `window` at first load — and finding it still there after the
   document changed). Plus `test_packaging.py` proving the wheel path
   builds one frontend, and `test_cli.py` proving the three flags parse
   and reach `WebViewer` without a `WebDevServer`.

### D15. Why a seam rather than a jsdom `mount()`

`mount()` constructs a `THREE.WebGLRenderer`, which jsdom cannot give a
context for, and pulling three.js into a jsdom test would make the
layout's test as slow and as fragile as the thing it is testing. The seam
is internal (not exported from `widget.ts`), the real wiring is one line,
and the real wiring is exactly what the Playwright tests exercise. It is
the same split cycle 2 used: a stub handle for the component test, the
real bundle for the browser test.

## 7. Risks

1. **The deletion is irreversible in the same commit as the page.** If
   the static page is wrong, the CRA app is gone. Mitigated by ordering:
   the page and its tests land *before* the app is deleted (tasks 3 and
   4), so the increment that deletes has a green served-page test behind
   it.
2. **A host that serves the old app's build directory.** Nothing outside
   this package ever pointed at `app/build`; `app_build_path()` is used
   only by `server.py:174` and `test_server.py`. Checked by grep, and the
   task says so.
3. **The framework's `--web-dev` becomes a lie.** It still works, and it
   now does exactly what `--web` does. Its help text is the framework's
   to fix, and the viewer's log line says what happened. Named here so
   the reviewer sees it was not missed.
4. **`data-solid-layout` is now a compatibility surface.** Another
   published name to keep, in a package whose distribution spec lists
   them. Listed in the README beside the others.
5. **The bundle grows again** — a layout, a reloader, a development
   entry and two stylesheets — for every host including the capture page,
   which mounts none of them. Same trade ADR-050 took, for the same
   reason: a second file costs a framework change.

## 8. Open questions

1. **Should the sidebar be resizable by dragging?** Not proposed. A
   custom property sets the width and a host overrides it; a drag handle
   is a stateful affordance that would want to remember, which D7 says it
   must not.
2. **Should `mountDevelopment` be published at all**, or should the page
   inline those three steps? Published, so the shop floor can serve its
   own page over this server without reproducing them — but it is the
   thinnest of the three new entries and the reviewer may reasonably want
   it unexported. It costs one line either way.
3. **Should the export page's `<title>` follow the model**, as the
   development page's does? Out of scope; `index.html` says `solid-node
   model` today and changing it is not this cycle's business.

## 9. The ADRs to extract

**Two, not one**, because they are filed in different subsystem
directories, amend different records, and answer different questions:

- **ADR-051 (EXPORT): The bundle ships an inspector layout, and the page
  selects it.** `mountInspector`, the sidebar as a disclosure that
  remembers nothing, the viewer resizing through its own observer, one
  themable stylesheet on the navigator's pattern, `data-solid-layout`
  with a query-string twin and the plain viewer as the default, and API
  10 → 11. Extends ADR-050 and ADR-035; consequence for ADR-020's
  auto-mount contract.
- **ADR-052 (VIEWER-WEB): The development page is a static page over the
  bundle.** The page the package carries, `mountDevelopment`, the
  reloader inside the bundle, the build-error pane over a viewer that
  stays mounted, the three frontend flags accepted as no-ops for the
  released framework, and React and CRA leaving the package.
  **Supersedes ADR-013** (React frontend) and **amends ADR-036**, whose
  own rejected alternative ("Replace the shell with a static page") this
  is.

*One combined ADR was considered* and rejected: a reader asking "why is
there no React in this package" would have to find the answer inside an
EXPORT record about a widget layout, and the index's own subsystem
split (`VIEWER-WEB — development server and app`) would put the
supersession of ADR-013 in the wrong section. The discipline in
`docs/adrs/README.md` is one decision per ADR.
