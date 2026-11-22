# ADR-086: The viewer bundles a model's app with its own toolchain, and refuses where it has none

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [show-a-models-own-app](../../../openspec/changes/archive/2026-11-22-show-a-models-own-app/) (design Decisions 7, 11 and 12)

**Builds on:** [ADR-059: The viewer keeps its own bundle current, and refuses what it cannot repair](ADR-059-the-viewer-keeps-its-own-bundle-current.md)
(a build never installs), [ADR-084](ADR-084-a-models-app-is-a-script-the-viewer-starts-inside-mount.md)

## Context

An app's author writes React components and no `package.json`. The
framework asks a viewer, through its seam, for every browser-side operation.
React is not installed at the workspace root; the movie's stage is the
precedent for bundling a project's React sources with a tool-owned
toolchain.

## Decision

**The web provider offers the seam's operation `bundle`
(`bundle_app(entry, root, output_dir)`), which runs the widget's
`app-build.mjs` with Node: the app's own `.tsx/.ts/.jsx/.js` and
`.css`, the viewer's own esbuild, its own React and React DOM (19.3.0,
pinned exactly as widget dependencies) and the helper
`@machinome/viewer/app`, into one minified classic script and at most one
stylesheet, named by the first 16 hex digits of their SHA-256.**

1. **The helper.** `<Viewport/>`, `useMachine()` (`{bank, drawing}`
   through `useSyncExternalStore` over one store per host), `usePlay()`,
   `useViewer()`, and an error boundary that refuses the app. It lives in
   `widget/app/`, outside `src/`, so the viewer's bundle and its currency
   never read it.
2. **One React, by the import plugin.** As decided in the implementation,
   the single copy is enforced by the bundler's import plugin, not esbuild's
   `alias` option: `react`, `react/jsx-runtime`, `react-dom`,
   `react-dom/client` and the helper resolve to the files the widget
   resolves them to, and every other bare import is refused by name.
3. **The project's files only.** Every input esbuild read that is not the
   widget's must lie inside the project's root; one outside is refused
   naming it.
4. **The same sources, the same bytes.** The bundler compiles under a
   tsconfig of its own. **The bundle is path-free only because it is
   minified**: unminified, esbuild names modules by their paths and two
   copies of a project bundle to different names (the `minify` mutation
   turns U7 red). Minifying is therefore part of this decision.
5. **Notices.** The script opens with a banner naming the viewer, React's
   MIT notice and the helper's grant and source; React's legal comments
   follow at its end.
6. **Writes.** Through a temporary name and a rename; a file already holding
   the same bytes is left untouched, so an unchanged app publishes nothing.
7. **The limit of this release.** The app toolchain exists only in a source
   checkout of the repository with its JavaScript dependencies installed. A
   wheel excludes `widget/app/`, `widget/app-build.mjs` and
   `widget/tsconfig.app.json`, and **an installed viewer refuses** to
   bundle, naming that limit; a checkout without its dependencies refuses
   naming them and `npm ci` at the workspace root; no Node.js is refused by
   name. Nothing installs anything. Putting the toolchain into an installed
   copy is a later step this decision does not shape.

## Alternatives

- **esbuild's `alias`:** the same effect; the plugin is needed anyway to
  refuse other imports, so it carries the resolution too.
- **A project-owned `package.json` and React:** a toolchain per project,
  and two Reacts on a page that mixes them.
- **React in the viewer's bundle:** contradicts [ADR-052](../VIEWER-WEB/ADR-052-the-development-page-is-static.md), which made the viewer React-free.

## Consequences

- An app bundle is about 227 kB, most of it React; bundling takes a median
  0.18 s on the bench.
- The viewer's own bundle carries no React (U9).
- A mutation that removes the `react` entry turns nothing red in this
  checkout, which holds no second React an app could reach (recorded in the
  change's `evidence.md`).

## Proof

`tests/test_app_bundle.py` (U1 to U10), `app/app.test.tsx` (H1 to H6),
the wheel listing of task 5.4.
