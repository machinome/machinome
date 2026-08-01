# SPRINT-002 brief: one model viewer

Planning record for `current.md`. It carries the findings the sprint rests on,
the decisions the pilot settled with their alternatives, the viewer interface
its consumers require, and the intent of each cycle.

Each cycle's requirements, spec deltas, tasks, and proof belong to that cycle's
own OpenSpec proposal. This document is the shared context those proposals start
from, not a substitute for them. Where it states a fact about the code, it names
where to re-verify it; treat a finding that no longer reproduces as a change in
the world, not as licence to drop the cycle.

All paths are relative to the repository named in the heading of each section.
Framework paths are in `solid-node`; shop paths are in `solid-node-shop`.

## 1. The problem

The same 3D model renderer exists three times, and a capability added to one
does not reach the others.

| | Development-loop viewer | Export widget | Shop floor viewer |
|---|---|---|---|
| Source | `solid_node/viewers/web/app/src/` | `solid_node/viewers/widget/src/` | `floor/frontend/src/viewer.ts` |
| Served by | `solid develop` (`viewers/web/viewer.py`) | `solid export` output and `solid_node/sphinx.py` | `floor/app.py` at `/artifacts/` |
| Input | live per-node HTTP `GET /node/<path>` | `manifest.json` | `viewer.json` |
| Build | CRA `react-scripts`, React 18, three 0.156 | esbuild IIFE, no framework | vite, React 19, three 0.185 |
| Tests | jest: `node.test.ts`, `composeOperations.test.ts`, `evaluator.test.ts`, `reloader.test.ts`, `reload.test.ts` | vitest: `evaluator.test.ts`, `tree.test.ts`; plus `tests/test_widget_e2e.py` | none; `npm test` is `tsc -b` |

The Python that serializes the node tree for those renderers exists three times
as well. That is the same duplication one layer down, and it has already
drifted (finding F-3).

## 2. Findings

Each was verified against the checkout at the sprint's base commits
(shop `ceddcd5`, framework `6f8a5ae`).

**F-1 — The shop floor viewer is a reimplementation of the export widget.**
`floor/frontend/src/viewer.ts:22-105` reproduces `solid_node/viewers/widget/src/evaluator.ts`
and `tree.ts` almost token for token: the same `powify` rewrite of OpenSCAD `^`
into `pow()`, the same degree-based trigonometry table, the same token cache,
the same `premultiply` composition loop, the same normal-versus-standard
material split, the same hemisphere and directional lights, and the same
camera fit (direction `(1, -1, 0.8)`, padding `1.2`). Floor adds exactly three
behaviors: restoring a preserved camera view across a remount, a `dispose()`
for React unmount, and a `Timeline` toggle that hides the animation bar until
requested, with the CSS class `functional-model` and `role="img"` /
`aria-label="Functional model"` on the canvas.

**F-2 — The development-loop viewer is a different architecture, not a variant.**
It fetches one node per HTTP request and builds the tree lazily
(`solid_node/viewers/web/app/src/node.ts:283`; server side `viewers/web/viewer.py:160,210`).
It flattens every mesh into one scene and composes an absolute world matrix per
mesh (`node.ts:59`) instead of nesting `THREE.Group`s. It carries a global
generation counter so that an in-flight STL callback cannot resurrect a mesh
into a scene a reload has replaced (`node.ts:50-130`). It reloads over a
websocket with an offline banner and a build-error pane (`reloader.ts`,
`App.tsx:96`). It has no colours (`node.ts:195` is `MeshNormalMaterial`, with a
`TODO use this.color`), no lights, no camera fit, and no animation controls; a
separate `Animator` drives time (`animator.ts`). It also carries dead weight: a
stubbed `NavigationTree.tsx`, a commented-out `ControlCube`, and `react-ace` /
`re-resizable` dependencies.

**F-3 — The node-tree walk exists three times in Python, and has drifted.**
`solid_node/core/export.py:97` (`_serialize_tree`), `solid_node/core/builder.py:95`
(`_viewer_state`), and `solid_node/viewers/web/viewer.py:160` (`NodeAPI.__init__`)
are the same recursion: same `node.rigid` short-circuit, same `render()`
list/tuple check, same `[op.serialized for op in node.operations]`. Two of them
call `node._link_child(child)` before recursing — the fix that makes viewer
names agree with STL and test names — and `_serialize_tree` does not. An
exported manifest can therefore name nodes differently from the build snapshot
of the same tree.

**F-4 — A built viewer bundle is absent exactly where development happens.**
`solid_node/viewers/widget/dist/solid-widget.js` is gitignored and built only by
npm; `MANIFEST.in` says so explicitly. Inspecting the locally built wheel
`dist/solid_node-0.4.0-py3-none-any.whl` shows `solid_node/viewers/widget/`
sources (`.gitignore`, `build.mjs`, `index.html`, `package.json`,
`package-lock.json`) and **no** `dist/solid-widget.js`. So a fresh tier-2
development workspace, any locally built wheel, and every framework worktree
have no viewer bundle at all. `solid_node/packaging.py` already solves this
problem for the CRA app — it runs `npm ci && npm run build` during sdist, and
during wheel build when `build/index.html` is missing — and does nothing for the
widget.

**F-5 — Framework benches could not build a bundle.** `scripts/dev-env` symlinked
the heavy gitignored directories for the CRA app only (`APP_DIR` at line 40, the
loop near line 168), while the framework's own OpenSpec conventions forbid
running `npm install` inside a worktree. A framework worktree therefore had no
way to build the widget. This is cycle S1's reason to exist.

**F-6 — The shop keeps a second copy of three.js in Git.**
`floor/static/assets/index-C51JVwFy.js` is 757534 bytes committed; the widget's
own bundle is 494541 bytes. Floor's `package.json` depends on `three`,
`@types/three` and `jokenizer` solely for its copy of the renderer.

**F-7 — Floor is currently forbidden from reusing the widget.**
`openspec/specs/functional-model-inspection/spec.md` requires floor to render
with "the established solid-node viewer semantics" and ends the requirement with
"It SHALL NOT use the separate export widget." `docs/adrs/0004-static-build-artifact-boundary-for-functional-model-inspection.md`
scopes `solid export` and its widget out of that decision. The archived change
`openspec/changes/archive/2026-07-21-inspect-functional-model/design.md` records
the intent: floor was to reimplement using the widget as a reference
implementation. Cycle S2 must amend both. Note that the `SHALL NOT` clause is a
mechanism inside a behavioral spec, which the operating contract says specs
should not carry; the amendment should state the outcome and leave the mechanism
to design and ADR.

**F-8 — Renaming the published export names is affordable but not free, and was
declined.** The names appear in: `solid_node/sphinx.py:49` (`WIDGET_FILES`),
`:57` (`WIDGET_BUNDLE`), `:189` (the copy mapping); `core/export.py:29`;
`manager/export.py:45`; `viewers/widget/build.mjs:28-29` (`globalName`,
`outfile`); `viewers/widget/index.html:22-23`; `viewers/widget/src/widget.ts:116,193,211,213,216`;
the ratified specs `openspec/specs/export/spec.md:19,59` and
`openspec/specs/sphinx-embedding/spec.md:64`; `docs/adrs/EXPORT/ADR-020-static-export-and-embeddable-viewer-widget.md`;
`docs/embedding.rst:23,26`; `docs/architecture.md:228`; and the tests
`tests/test_export.py`, `tests/test_sphinx_ext.py`, `tests/test_widget_e2e.py`.
Committed exports would *not* break: every `docs/_exports/*` directory is
`manifest.json` plus `models/` only and is completed at docs-build time from the
installed package, and a full export directory carries its own bundle and keeps
working. The only real breakage is a hand-written host page that follows
`docs/embedding.rst` and references the filename, the `data-solid-widget`
attribute, or the `SolidNodeWidget` global.

**F-9 — Release mechanics.** `.github/workflows/python-app.yml` already installs
Node 22 and builds the widget bundle in three jobs (`widget`, `docs`, and the
tag-triggered `build`). `make dist` runs `python -m build`, which invokes
`solid_node/packaging.py`. The tag job creates a GitHub release; PyPI upload is
manual (`Makefile` `release: dist` → `twine upload dist/*`, per
`CONTRIBUTING.rst:123-128`, after `bump2version`). Adding a frontend to the
build is therefore nearly free; adding a registry publication is not.

**F-10 — The two published documents differ trivially.** `manifest.json`
(`core/export.py`) carries a `format` key and deduplicates meshes under
`models/`; `viewer.json` (`core/builder.py`) carries `mtime` per node and roots
model paths at the build directory. Node fields are otherwise identical. Path
rooting is not a schema difference: it is a consumer parameter, which is why
floor hardcodes `/artifacts/` (`floor/frontend/src/viewer.ts:116`) and the
widget derives its base from the manifest URL (`widget/src/widget.ts:37`).
`viewer.json` is named in 13 shop files and 8 framework files outside archives,
including two ratified specs, three ADRs, and both `shop-skills/` documents.

**F-11 — Floor reaches the framework only through the CLI.** `floor/` never
imports `solid_node`; it invokes a configured command
(`floor/preparation.py:49,98`). `tests/fixtures/fake_solid.py` is a fake `solid`
CLI that the shop's tests run against. Any new framework-supplied asset must
therefore be reachable through a CLI the fake can emulate, and the fake must be
able to supply a bundle for S2's tests.

## 3. Decisions

Recorded with the alternative that was rejected and why. The one-line forms in
`current.md` are authoritative for scope; this section carries the reasoning.

**D-1 — One viewer, delivered inside the framework's Python distribution; no
package registry in this sprint.** The viewer becomes a real package (its own
`package.json`, tests, build, types, documented options), but stays
`"private": true`. Rejected: publishing `@solid-node/viewer` to npm now. A
registry release adds a second credential, a publication ordering constraint
against the wheel, and a permanent public artifact per tag — while the option
surface is precisely what will churn as capabilities are added. Revisit when a
second consumer exists that cannot reach the Python distribution: an external
embedder, or the shop published on its own cadence. At that point the package
already exists and publishing is a CI job.

**D-2 — Floor obtains the bundle through a CLI accessor, not a Python import.**
Preserves the boundary in F-11 and keeps `fake_solid.py` able to emulate the
whole framework interface. Rejected: `import solid_node` in floor (breaks the
single-interface boundary and cannot be faked in tests), and vendoring a copy
into the shop (recreates the duplication this sprint removes).

**D-3 — Unify the serializer; keep both document names.** One walk,
parameterized by rooting and mesh copying, emitting one schema; `viewer.json`
gains `format` and `manifest.json` gains `mtime`, both additive. Rejected:
renaming `viewer.json` to `manifest.json`. The two names distinguish a portable,
self-contained directory from a snapshot beside a build — a distinction Sphinx
relies on when it recognizes an export directory by its `format` key. Unifying
the name would require reintroducing that distinction as a flag, and would touch
two ratified specs, three ADRs, both `shop-skills/` documents and 21 files. If
build publications ever become portable (deduplicated, self-contained, servable
as-is), the distinction disappears and one name becomes right; that is its own
change, not a side effect of this one.

**D-4 — Keep the published export names and current package directory.**
`solid-widget.js`, `data-solid-widget`, `SolidNodeWidget`, and
`solid_node/viewers/widget` stay. Rejected: renaming the published names, per
F-8 — the cost is not user breakage but dragging two ratified specs, an ADR, and
a deprecation alias into the cycle every other cycle depends on. A package
directory rename may return during F2 only with a proven dependency-source or
refresh path for framework benches and explicit pilot ratification.

**D-5 — An absent or incompatible viewer is one shop preparation failure.**
Floor asks the installed framework for the bundle and its API version; if it is
missing or below what floor requires, the shop refuses to open with a message
naming the remedy, through the existing failure path in `floor/preparation.py`.
Rejected: a degraded in-browser state with an in-pane notice. The case it would
serve — floor newer than the installed framework — requires the shop and the
framework to be versioned and distributed independently, which they are not: the
shop is unpublished and will first ship alongside a framework release. Designing
a degraded path now means testing a half-working viewer in every model-related
path for a user who does not exist. Revisit if the shop is ever published on its
own cadence.

**D-6 — Staged cycles, with the development-loop viewer inside the sprint.**
The dev viewer rests on a different architecture (F-2) and carries the sprint's
largest risk, so it is not bundled into the cycle that unblocks the shop.
Rejected: deferring it to a later sprint — the goal is not met while one surface
still carries its own implementation.

**D-7 — The viewer core stays framework-agnostic and imperative.** `mount()`
returning a handle, no React inside the package. Floor keeps its own React
wrapper (`floor/frontend/src/main.tsx:52-83`), and the development-loop app
keeps its own shell. Rejected: shipping a React component, which would bind the
package to one React major across three consumers that today span React 18, 19
and none.

**D-8 — The bundle exposes an API version from the first cycle that ships it.**
Without it, an incompatible bundle produces a blank pane and a console error
instead of a sentence. It is roughly ten lines now and expensive to retrofit.

## 4. The viewer interface its consumers require

Derived from what the three renderers do today. A cycle proposal may name these
differently, but must cover the behavior.

Entry point: mount into a container against a snapshot URL plus a base URL for
the meshes; return a handle.

Options:

- **source** — snapshot URL, and the base URL model paths resolve against. One
  loader reads either published document (F-10, D-3).
- **animation** — none; an always-visible inline bar (what `solid export` shows
  today); a bar hidden behind a compact persistent `Timeline` toggle (what floor
  requires); or externally driven, with the host supplying time. Plus initial
  time (`0..1`) and autoplay, which the Sphinx directive sets from a query string
  (`?t=`, `?autoplay=0`).
- **camera** — fit to the loaded model bounds, Z-up as in OpenSCAD, and the
  option to restore a previously captured view instead of fitting.
- **materials** — inherited colour with `MeshStandardMaterial`, and
  `MeshNormalMaterial` when no colour is available anywhere up the tree.
- **chrome** — CSS class and ARIA attributes on the canvas; floor requires the
  class `functional-model`, `role="img"`, `aria-label="Functional model"`, and
  `aria-expanded` on its timeline toggle.

Handle: `dispose()` (floor unmount), `view()` (capture camera position and orbit
target for the next mount), `reload()` (rebuild the tree from the snapshot,
keeping the current view — what the development loop needs), and `apiVersion`.

Auto-mount from `data-solid-widget="<manifest url>"` stays, because it is the
published export contract (D-4).

## 5. Cycles

Dependencies and identities are in `current.md`; this section is the intent.

### F1 — `solid-node` / `unified-node-serializer`

Replace the three walks of F-3 with one, parameterized by how a rigid node's
model path is rooted and whether meshes are copied and deduplicated. Converge the
two documents additively: `format` into `viewer.json`, `mtime` into
`manifest.json`. Apply `_link_child` in the export path so all three consumers
name nodes identically.

Prove the drift red first: an export and a build snapshot of the same tree
disagree on node names today. Do not rename a document, change path rooting, or
make build publications portable.

### S1 — `solid-node-shop` / `viewer-bench-symlinks`

Generalize `scripts/dev-env` so it symlinks the heavy gitignored directories for
every frontend package under `solid_node/viewers/`, not only the CRA app (F-5),
so a framework worktree can build a bundle without `npm install` inside it.
Cover it in `tests/dev-env-test.sh`. Do not change port allocation or the
manifest format.

### F2 — `solid-node` / `viewer-package`

Turn `solid_node/viewers/widget` into the single reusable viewer package with the
interface in section 4 and an exported API version (D-8). The directory may be
renamed only after the conditional gate in D-4 is ratified; otherwise retain it.
The published output names may not change. Make `solid export` and
`solid_node/sphinx.py` consume it, and fold floor's three behaviors (F-1) in as
options. Keep the package private (D-1).

Evidence: the widget's vitest suite extended to the new options, the framework's
export and Sphinx tests, `tests/test_widget_e2e.py`, and the documentation build
CI already runs with `-W` including the V8 example export. Add no capability
beyond parity plus the options consumers need.

### F3 — `solid-node` / `viewer-bundle-delivery`

Build the bundle into wheel and sdist the way `packaging.py` already does for the
CRA app, cover it in `MANIFEST.in`, and add the CLI accessor that reports the
built bundle's path and API version (D-2). F-4 is the red: today's wheel ships
sources and no bundle, and a fresh development workspace has no viewer.

Evidence: build a distribution and assert the bundle inside it; CLI tests. Do not
make floor import `solid_node`.

### S2 — `solid-node-shop` / `floor-uses-framework-viewer`

Delete `floor/frontend/src/viewer.ts`; obtain the bundle through the CLI accessor
and serve it from floor's static route; keep the React wrapper in `main.tsx`.
Implement D-5 in `floor/preparation.py`. Drop `three`, `@types/three` and
`jokenizer` from `floor/frontend/package.json` and rebuild the committed
`floor/static` (F-6). Teach `tests/fixtures/fake_solid.py` to supply a bundle
(F-11).

Amend `openspec/specs/functional-model-inspection/spec.md` so the requirement
states the outcome rather than forbidding the widget, and amend ADR-0004's
exclusion of the export widget (F-7).

Evidence: the shop suite, new preparation tests for the absent and incompatible
cases, and visual confirmation that a model still renders and that a rebuild
preserves the maker's camera.

### F4 — `solid-node` / `dev-viewer-on-shared-package`

Make `solid develop` serve the published snapshot plus a reload signal, and
rebuild its React app on the shared package. Retire `node.ts`, the per-node walk
in `NodeAPI`, and the unused `SnapshotNodeAPI` (`viewers/web/viewer.py:259`,
called by nothing but its test). The development viewer gains colours, lights and
a fitted camera as a consequence.

The jest tests that encode the flat-scene architecture (F-2) are replaced, not
ported. Reload behavior that must survive: rebuild after a successful build, the
offline banner when `solid develop` is down, and the build-error pane. Do not
change either document's name or rooting.

## 6. Sequencing

F1 and S1 have no dependencies and can run in parallel. F2 needs F1 (one schema
to load rather than dual-source branching that would be written and then deleted)
and S1 (a bench that can build a bundle). F3 needs F2. S2 needs F3 integrated
into the framework's `sprint-002`, because floor consumes the accessor. F4 needs
F3 so framework viewer build cycles remain serialized while their benches share
heavy frontend directories. F1 removes two of the three Python walks; F4 removes
the third.

## 7. Out of scope, with reasons

- Registry publication of the viewer (D-1).
- Renaming `solid-widget.js`, `data-solid-widget`, `SolidNodeWidget` (D-4).
- Renaming `viewer.json` or `manifest.json` (D-3).
- Making build publications portable and self-contained — the change that would
  make one document name correct; deliberately separate (D-3).
- Viewer capabilities beyond parity and the options in section 4. New
  capabilities are the reason the sprint exists, but they belong after the three
  surfaces share one implementation.
- A degraded in-browser state for viewer version mismatch (D-5).

## 8. Left to the cycles

Deliberately unsettled here, to be decided in the owning proposal with
implementation evidence: the exact spelling and shape of the CLI accessor;
whether F3 also ships TypeScript declarations for consumers that typecheck
against the package; how floor expresses the minimum API version it requires;
and whether F4 moves the development app off `react-scripts` to the toolchain the
rest of the workspace uses.
