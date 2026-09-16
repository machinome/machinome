## Why

A maker opened the studio to look at a machine and the viewer refused it:

> `/api/sessions/.../artifacts/viewer.json` declares document version 7,
> which this viewer does not render; it renders versions 1, 2, 3, 4, 5, 6.

Nothing was wrong with the document, the producer, or this repository's
source. `execute-the-selection` (`5a3e1d7`, API 16, document version 7)
and `mirror-the-gate-guard` (`98d0347`) were both integrated into `main`;
`package.json` declared `solidNodeViewerApi: 16` and
`solidNodeDocumentVersions: [1..7]`; `viewer.ts`'s `RENDERED_VERSIONS`
declared the same. The file actually being served — `widget/dist/solid-widget.js`
in the checkout the environment installs editable — had been built at
`Sep 15 17:42`, before that cycle landed, and carried `[1,2,3,4,5,6]` and
`viewer API 15`. **The bundle was stale, and nothing in this package
noticed or said so.**

It is worth being exact about which promise broke, because this package
already made it. `viewer-distribution`, "A framework finds the installed
viewer through one entry point":

> `apiVersion` and `documentVersions` SHALL come from the widget package's
> own single declaration of each, the same declaration the bundle is built
> from, so the answer a framework reads and the versions the bundle
> actually refuses can never disagree.

They disagreed. The requirement pins both numbers to ONE declaration, which
removes the drift between two *declarations* — and that much holds. What it
does not cover is the gap between the declaration and the **built artifact**:
`describe()` reads `package.json` at the moment it is asked, while
`dist/solid-widget.js` was built from whatever `package.json` and `src/`
said whenever someone last ran `npm run build`. In an installed wheel those
are the same instant by construction. In a source checkout — which is how
every developer, every worktree, and this whole workspace runs the viewer —
they are two different instants, and the entry point answers for a file it
never checked.

So the lookup told the truth about the declaration and a lie about the
bundle, and the maker got a message accusing the *document* of being
unreadable, when the document was correct and the renderer was old.

### Measured on the base

Base: worktree `solid-node-viewer/WTs/keep-the-bundle-current`, branch
`keep-the-bundle-current` at `98d0347` (`main`).

Deterministic reproduction, no editing: build the bundle from the sources
at `fff31e4` (API 15, versions 1-6), restore `main`'s sources, ask.

| | says |
| --- | --- |
| `describe()` / the entry point / `describe` command | `apiVersion: 16`, `documentVersions: [1,2,3,4,5,6,7]` |
| the bundle it hands out the path of | `viewer API 15`, refuses by `[1,2,3,4,5,6]` |

Every consumer inherits that: `solid export` copies the stale bundle beside
a version 7 document, `solid-node-viewer serve` serves it at
`/_viewer/bundle.js`, `capture` copies it into the staging directory and
photographs its refusal, and the shop floor serves the path the framework's
`solid viewer` report gave it. No surface reports anything wrong, because as
far as each one knows it is serving the bundle this installation has.

Detecting it is cheap and repairing it is nearly so, which is the other half
of the argument: over the widget's **77** build inputs, a newest-mtime scan
takes a **median 2.88 ms** (max 3.97 ms over 20 runs), and `npm run build`
takes **0.33-0.41 s** wall clock. A check on every answer costs
milliseconds; a repair costs a third of a second, and only when something
actually changed.

`packaging.py` carries the same hole one step further out. It builds a
frontend that is **missing**:

```python
def build_missing_frontends():
    for frontend in FRONTENDS:
        if not frontend.output_exists():
            build_frontend(frontend)
```

A wheel built from a checkout whose bundle is stale therefore *ships* the
stale bundle, and the spec says so in as many words: "creating a wheel SHALL
build it only when the checkout does not already contain its output, keeping
an existing one". That is a publishing hazard, not just a development
annoyance — `scripts/check-dist` would install and smoke a wheel whose
bundle is older than the source it was cut from.

## What Changes

- **A source checkout answers from a bundle built from its current sources.**
  Before the entry point answers, before the development server serves the
  bundle route, and before a capture copies the bundle into its staging
  directory, this package SHALL compare the built bundle against the inputs
  it is built from — everything under `widget/src/`, `package.json`,
  `build.mjs` and `tsconfig.json` — and rebuild it when it is older.
- **A rebuild builds; it never installs.** The automatic path runs the build
  only. It never runs `npm ci` or `npm install`, so a checkout whose
  `node_modules` is a symlink shared with another worktree is never
  reinstalled by something as innocent as asking a question. (This is not
  hypothetical: `npm ci` through such a symlink has emptied the primary
  checkout's `node_modules` in this workspace.)
- **What cannot be repaired is named, not served.** When the bundle is stale
  and the rebuild cannot run or fails — no `node_modules`, no `npm`, a
  TypeScript error — the lookup SHALL raise with the reason and the remedy
  and the command SHALL exit non-zero, rather than answering with a
  declaration the bundle does not honour. A stale bundle is a broken
  installation; it is now reported as one.
- **An installed distribution is untouched.** A wheel carries no `widget/src`
  and no `build.mjs`, so there is nothing to compare and nothing to rebuild:
  installing still needs no npm, and the check costs one `is_file()`.
- **A wheel is cut from a current bundle.** `build_missing_frontends`
  becomes a build of what is missing *or stale*, so a wheel built from this
  checkout can no longer carry a bundle older than the source beside it.
- **Concurrent processes do not tear the file.** A rebuild holds an
  exclusive lock; a second process waits and then finds the bundle current
  rather than writing it a second time.

## Impact

- Affected specs: `viewer-distribution` (the lookup, and what distributions
  carry), `development-server` (the bundle route).
- Affected code: `solid_node_viewer/bundle.py`, a new
  `solid_node_viewer/currency.py`, `solid_node_viewer/server.py`,
  `solid_node_viewer/capture.py`, `solid_node_viewer/packaging.py`.
- Affected decisions: ADR-059 (new).
- The widget's TypeScript is **not** touched: no `src/` file, no
  `package.json` number, no bundle content. This cycle changes when the
  bundle is built, never what it contains.

## Non-goals

- **The shop's own copy of the answer.** `libresolid-studio` resolves the
  bundle once through `solid viewer` and holds the path for the life of the
  running shop (`floor/sessions.py:521-531`). With this change, a shop
  *started* after a viewer change gets a rebuilt bundle; a shop already
  running when the viewer changes goes on serving the path it resolved,
  whose file is now rebuilt underneath it — correct on the next page load,
  because the route is a `FileResponse` read per request. Whether the shop
  should re-ask per session open is the shop's decision, in the shop's
  repository, and is recorded for the pilot rather than taken here.
- **Content hashing.** Currency is decided by modification time in integer
  nanoseconds, as the framework decided for its own artifacts. A source
  touched without being changed costs one 0.35 s rebuild; that is cheaper
  than hashing 77 files on every answer.
- **Watching.** Nothing polls or subscribes. The check happens when someone
  asks, which is exactly when a wrong answer would matter.
- **Rebuilding anything but the bundle.** The pages are carried as written
  and have no build step; the corpus fixture is a test input, not a
  published artifact.
