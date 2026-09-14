# ADR-052: The development page is a static page over the bundle

**Status:** Proposed

**Date:** 2026-09-14

**Change:** `ship-the-inspector-layout`

**Supersedes:**
- [ADR-013: React as frontend framework for the web viewer](ADR-013-react-frontend-framework.md)

**Amends:**
- [ADR-036: Snapshot-served shared viewer shell](ADR-036-snapshot-served-shared-viewer-shell.md)

**Depends on:**
- [ADR-051: The bundle ships an inspector layout](../EXPORT/ADR-051-the-bundle-ships-an-inspector-layout.md)
- [ADR-037: Targeted in-place viewer updates](ADR-037-targeted-in-place-viewer-updates.md)

## Context

ADR-013 chose React and Create React App when the development page owned a
renderer, a navigation tree, an animation clock and a per-node REST client.
ADR-036 took all of that away and left React "only as a lifecycle and
error/reload shell", recording the CRA migration debt explicitly rather
than folding it into that change. Its own rejected alternatives include,
verbatim, "Replace the shell with a static page" — rejected then because
it would have expanded a change about viewer sharing into a CRA,
packaging and `--web-dev` migration.

That migration is now small. What the shell does is: load the bundle,
mount it with inline animation and autoplay, name the tab, and run a
websocket reloader (`app/src/App.tsx`, `viewerShell.ts`, `reloader.ts` —
about 250 lines, of which the reloader is 150). ADR-051 supplies the
layout it should mount. What React and CRA cost, meanwhile, is a second
npm project with a 688 kB lockfile, a second frontend build in
`packaging.py`, an httpx proxy and a second dev-server process in
`server.py`, a `--dev`/`--start-frontend`/`--frontend-port` surface on
`serve`, and a test that skips itself in every environment that did not
run `npm run build` in a second directory.

One constraint is not negotiable. solid-node 0.6.0 is released on PyPI,
and its `solid develop --web-dev` runs

```
solid-node-viewer serve --build-dir <dir> --start-frontend
```

(`solid_node/manager/develop.py:49-51`). A viewer that rejected that flag
would turn a working framework command into an argparse error on a flag
the maker never typed.

## Decision

**The development page becomes a static page this package carries and the
server answers `/` with; the reload client moves into the bundle; React and
Create React App leave the package; and the three frontend flags stay
accepted as no-ops.**

1. **The page is a file, not an application.**
   `solid_node_viewer/widget/develop.html`, beside the export page and the
   bundle. It checks `/_viewer`, injects `/_viewer/bundle.js`, and calls
   `SolidNodeWidget.mountDevelopment('#root')`. Those first two steps must
   stay in the page, because they are what runs when the bundle is
   missing, and code inside a bundle cannot report that the bundle is not
   there. Everything after them is in the bundle, where the widget's own
   test runner can reach it.

2. **`mountDevelopment` is published.** It mounts the **inspector** on
   `/build/viewer.json` with `animation: 'inline'` and `autoplay: true` —
   the same two options `viewerShell.ts` passed — names the tab from the
   model's root name, and starts the reloader. It is exported so a host
   serving its own page over this server does not reproduce those steps,
   and it is the second capability behind the API version bump.

3. **The reload client lives in the bundle, behaviour unchanged.**
   `widget/src/reloader.ts` is `app/src/reloader.ts` with its React
   `setError` type replaced by a plain callback. The socket URL, the 2 s
   retry, the two-attempt grace before the first banner, the immediate
   banner when a live connection drops, the banner's id, class and text,
   the `/_build_error` poll and its `tstamp` dedupe are identical, and its
   nine jest tests become nine vitest tests. Its banner rule moves from
   `App.css` into its own injected stylesheet, the third component here to
   follow ADR-050's pattern.

4. **Partial reload is untouched.** The reload path ends, as it always
   did, in the handle's `manifestChanged()` — the targeted update of
   ADR-037. Nothing about it is reimplemented, and a Playwright test
   against the served page proves a republished `viewer.json` changes the
   model with no page load.

5. **A build error is shown over a viewer that stays mounted.** The React
   shell swapped the viewer for a `<pre>`, which discarded the camera and
   any live run for an error the next save would fix. The static page
   shows the error in a pane above the layout. This is a behaviour change,
   made deliberately and ratified in the change's spec rather than
   discovered: the requirement asks that errors be shown "in its error
   pane", and the same spec's run requirements ask that a cosmetic edit
   leave the machine exactly where it was — which a teardown on the
   previous failed save makes impossible.

6. **React, Create React App and `solid_node_viewer/app/` are deleted**,
   and with them the second frontend in `packaging.py`, the two `app/*`
   lines in `MANIFEST.in`, `APP_DIR` and `app_build_path()` in
   `bundle.py`, and `WebDevServer` and the httpx proxy in `server.py`. A
   wheel now needs one npm build; `httpx` moves to the `dev` extra with
   the proxy it served.

7. **`--dev`, `--start-frontend` and `--frontend-port` keep being
   accepted**, do nothing, and log one notice each;
   `SOLID_NODE_FRONTEND_PORT` and `DEFAULT_FRONTEND_PORT` keep resolving
   harmlessly. This is written into the `development-server` spec, not
   left as a kindness in the code, so a later cycle tidying "unused flags"
   cannot break a released framework and pass its own tests.

## Consequences

- The development page shows the assembly tree, because it mounts the
  inspector. That is the user-visible point of the whole cycle.
- The package's only frontend build is the widget's esbuild pass.
  `tests/test_server.py`'s skip disappears: the page is a package file, so
  "not built" is no longer a state it can be in, and the browser test that
  had been skipping itself now runs everywhere Chromium is available.
- ADR-013 is superseded. React is not a dependency of this package in any
  form. ADR-036's "React remains only as a lifecycle and error/reload
  shell, CRA migration debt remains explicit" is discharged; the rest of
  ADR-036 — the server serving `/build/` and `/_viewer/bundle.js`, the
  page mounting the shared bundle against the published snapshot, the
  retirement of the recursive NodeAPI — stands unchanged.
- `solid develop --web-dev` still works and now does exactly what
  `--web` does. Its help text is the framework's to correct; the viewer's
  log line says what happened.
- Two accepted-but-inert flags and one inert environment variable are
  carried indefinitely. That is the price of a framework released against
  them, and the spec says so out loud.

## Alternatives considered

**Change the framework instead, and drop the flags.** The framework
worktree exists for it. Rejected: it would make a viewer release depend on
a framework release for three lines of argparse, and would leave every
already-installed solid-node 0.6.0 broken against a new viewer.

**Migrate the app from CRA to Vite and keep React.** It would answer
ADR-013's own "CRA deprecated" consequence and change nothing else: a
second npm project, a second build at packaging time, a second lockfile,
and a shell whose whole content is four calls into a bundle.

**Keep the app and mount the inspector inside it.** The cheapest possible
change, and it leaves every cost above in place for a page that would then
be a React wrapper around a layout the bundle already composes.

**Inline the whole page, reloader included, in `develop.html`.** It would
put the one piece with a real state machine and an existing test suite in
a file no test runner loads.

**A second bundle entry (`develop.js`).** It would be a second published
artifact, against `viewer-distribution`'s "exactly the page and the one
bundle".

## References

- `solid_node_viewer/widget/develop.html` — the page
- `solid_node_viewer/widget/src/develop.ts` — `mountDevelopment`
- `solid_node_viewer/widget/src/reloader.ts` — the ported reload client
- `solid_node_viewer/server.py`, `solid_node_viewer/cli.py`,
  `solid_node_viewer/packaging.py`, `solid_node_viewer/bundle.py`
- `openspec/changes/ship-the-inspector-layout/`
- [ADR-035: Reusable viewer core and declared API](../EXPORT/ADR-035-reusable-viewer-core-and-declared-api.md)
