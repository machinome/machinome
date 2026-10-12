## Context

This is cycle S2 of SPRINT-002 (`docs/product/sprints/current.md`, brief section
5). Its findings and the sprint decisions it implements are recorded there; this
document settles what the brief left to the owning proposal.

Current state in the shop:

- `floor/frontend/src/viewer.ts` is a 173-line reimplementation of the
  framework's export widget, mounted by `FunctionalModel` in
  `floor/frontend/src/main.tsx:55-86`. It remounts whenever the watcher's
  `generation` advances and carries the maker's camera across that remount in a
  ref.
- `floor/app.py:519` serves `_build` through `/artifacts/{path}`; the frontend
  fetches `/artifacts/viewer.json?generation=N` and hardcodes `/artifacts/` as
  the base for model paths.
- `floor/preparation.py` is a fail-closed sequence of subprocess stages that
  ends in a validated snapshot and returns a frozen `PreparedProject`;
  `floor/orchestrator.py:284` and `floor/__main__.py:50` pass its fields into
  `create_app`.
- The shop reaches solid-node only by invoking a configured command
  (`PreparedProject.solid_command`), and `tests/fixtures/fake_solid.py` is a fake
  of that whole interface.

Current state in the framework, at `solid-node` `sprint-002` @ `5c14acf`:

- `solid viewer` prints `{"path": ..., "apiVersion": N}` and exits 0, or writes
  `missing_bundle_remedy()` to stderr and exits 1
  (`solid_node/manager/viewer.py`).
- The bundle is `solid-widget.js`, an IIFE exposing the global
  `SolidNodeWidget`, built into the wheel and sdist by F3.
- `mount(target, sourceUrl, options)` returns a handle with `dispose()`,
  `view()`, `reload()`, `setTime()`, and `apiVersion`. Options are `baseUrl`,
  `animation` (`inline | toggle | none | external`), `time`, `autoplay`, `view`,
  `className`, `role`, `ariaLabel` (`viewers/widget/src/viewer.ts`,
  `src/options.ts`).
- `animation: 'toggle'` produces exactly the floor's behavior today: a
  persistent `Timeline` button with `aria-expanded`, and a hidden
  `animation-controls` bar.

## Goals / Non-Goals

**Goals:**

- The shop floor renders through the framework's viewer, and the shop keeps no
  renderer of its own.
- The shop reaches the bundle only through the solid-node CLI, so
  `fake_solid.py` can still stand in for the framework in tests.
- An unusable viewer stops the shop from opening, with the remedy in the message.
- The maker sees no behavior change: same materials, same camera fit, same
  preserved camera across a rebuild, same Timeline toggle, same ARIA.

**Non-Goals:**

- Any viewer capability beyond parity. New capabilities are why the sprint
  exists, but they follow the convergence.
- A degraded in-browser state for a missing or mismatched viewer (brief D-5).
- Making floor import `solid_node` (brief D-2).
- Changing `viewer.json`, its name, or its path rooting (brief D-3).
- Moving the floor's build toolchain or its watcher/SSE design.

## Decisions

### D1 — Preparation runs `solid viewer` and carries its result on `PreparedProject`

A new stage in `prepare_project`, using the same `_run` helper, the same
`solid_command`, and the same `PreparationError` shape as the build stage. It
runs before the build: the cheapest fail-closed check should reject the
workspace before the expensive one. Its parsed `path` and `apiVersion` become
frozen fields on `PreparedProject`, which already carries what the app needs.

*Alternatives.* Probing the bundle from `floor/app.py` at request time — moves a
fail-closed condition into a browser request, which D-5 rules out. Locating the
bundle by filesystem convention — reintroduces knowledge of the framework's
layout that the accessor exists to remove.

### D2 — The floor requires a minimum viewer API version, expressed as one integer compared with `>=`

`floor/preparation.py` carries `REQUIRED_VIEWER_API = 1` beside the stage that
checks it, and preparation fails when the reported `apiVersion` is below it.
`solidNodeViewerApi` is a compatibility integer the framework increments when
the viewer interface it exposes stops satisfying an existing consumer, so a
floor written against version *n* works with any bundle at *n* or above. The
constant is the single place a future floor change records that it now needs
more than the viewer once offered.

*Alternatives.* A version range or semver expression — the framework publishes
one integer, so a range has no second bound to express. A capability probe on
the mounted handle — moves the check into the browser, which D-5 rules out, and
would have to run before the failure it prevents.

### D3 — Floor serves the bundle from its own route, reading the framework's file; it does not copy or commit it

`floor/app.py` gains `GET /viewer/solid-widget.js`, a `FileResponse` for the
exact path preparation reported, wired through `create_app(viewer_bundle=...)`
the way `artifact_root` already is. The floor serves one named file, not a
mounted directory: the framework's widget directory also holds sources, and
`StaticFiles` there would publish them.

The bundle is not copied into `floor/static/`. It belongs to the installed
framework and a copy is exactly the staleness this sprint removes; committing
one would replace the second three.js this change deletes (F-6) with another.

*Alternatives.* Serving it from the existing `/artifacts` route — that route's
containment check is anchored at `_build`, and the viewer is not a project
artifact. Copying the bundle into `floor/static/` at preparation time — a
per-open filesystem write into a committed directory, and a second source of
truth for which viewer is running.

### D4 — The browser loads the bundle at runtime as a classic script and uses the `SolidNodeWidget` global

`floor/frontend/index.html` gains `<script src="/viewer/solid-widget.js">`
before its module entry, and `main.tsx` calls
`window.SolidNodeWidget.mount(...)`. The floor declares the handle's and
options' types in a small local `.d.ts`, because the package is not a build-time
dependency of the floor's Vite build. Auto-mount does not interfere: the bundle
mounts automatically only into elements carrying `data-solid-widget`, and the
floor's container has none.

The alternative — making `@solid-node/widget` a build-time npm dependency of
`floor/frontend` — would bundle three.js back into `floor/static` (undoing F-6),
pin the committed shop assets to whichever framework checkout built them, and
make a framework viewer improvement require a shop rebuild and commit. Loading
the installed framework's own bundle at runtime is what makes "improve it once,
see it everywhere" true for the shop.

The cost is a runtime coupling the TypeScript build cannot check. It is bounded
by D-1/D-2: the version the floor requires is asserted before the browser
starts, and the local `.d.ts` is what a version bump would have to update.

### D5 — Option mapping, chosen to preserve today's behavior exactly

```
mount(container, `/artifacts/viewer.json?generation=${generation}`, {
  baseUrl: "/artifacts/",
  animation: "toggle",
  view: preservedView,
  className: "functional-model",
  role: "img",
  ariaLabel: "Functional model",
})
```

`baseUrl` is passed explicitly even though `resolveBaseUrl` would derive the
same value from the source URL, because the floor's rooting at `/artifacts/` is
a floor decision and should not rest on how a query string is stripped.
`autoplay` keeps its default of `true`, matching `playing = tree.animated`
today.

### D6 — The rebuild path keeps remount-per-generation rather than moving to `handle.reload()`

`FunctionalModel`'s effect stays keyed on `generation`: it captures `view()`
before `dispose()` and passes it as `view` on the next mount, which is what the
framework's handle consumes. `reload()` re-fetches the same source URL, so
adopting it would require moving the floor's cache-busting `generation` out of
the query string and into the framework's fetch — a change to the framework
interface, in the cycle that is supposed to consume it.

*Trade-off.* Remounting rebuilds the WebGL context on every model change where
`reload()` would not. The maker-visible result is identical because the camera
is carried across, and this is the behavior the shop has today; if remount cost
becomes visible, adopting `reload()` is a later, isolated change.

### D7 — `fake_solid.py` gains a `viewer` subcommand and writes a stub bundle

The fixture writes a small JavaScript file into a temporary location and reports
its path with an `apiVersion`, so preparation's happy path exercises the real
parsing. Its argument parsing changes: `solid viewer` takes no argument, so
`command, argument = sys.argv[1:3]` becomes a form that tolerates a bare
subcommand. Its existing state-file mechanism gains the cases the new tests
need: report no viewer (non-zero exit with a remedy on stderr) and report an
`apiVersion` below what the floor requires.

### D8 — ADR-0004 is amended, not superseded

ADR-0004's decision — the completed `_build` directory is floor's only
functional-model input, and floor never imports or executes project Python —
is untouched by this change and remains true. Only its final scoping sentence
("`solid export` and its separate export widget are not part of this decision")
and the sentence stating that floor owns a browser-side renderer are wrong
after this cycle. They are amended in place with a dated note recording that
SPRINT-002 replaced floor's renderer with the framework's viewer, obtained
through the CLI, which does not weaken the artifact boundary: the bundle is
static JavaScript served to the browser, and no project Python enters the floor.

`docs/architecture-overview.md` describes no renderer boundary today, so the
amendment adds no overview change beyond the ADR index entry staying accurate.

## Risks / Trade-offs

- **A shop opened against a framework older than the bundle delivery cycle now
  refuses to open where it previously worked.** → This is D-5, ratified: the
  shop and the framework are not versioned independently, and the message names
  the remedy (`npm ci && npm run build` in the widget directory, which the
  framework's own `missing_bundle_remedy()` already spells out). Preparation
  reports the framework's own text rather than paraphrasing it.
- **The runtime coupling between `main.tsx` and the bundle's global is not
  type-checked.** → D-2's version gate fails the open before the browser loads,
  and the browser mount failure path already surfaces an error beside the model
  (`main.tsx:70`, `83`). A new test asserts the floor's declared required version
  matches the framework interface the local `.d.ts` describes.
- **The first build after upgrading the framework can publish a `viewer.json`
  that differs only by F1's additive `format` field, which the watcher reports as
  a model change.** → One ordinary refresh, recorded in
  `shop-skills/solid-node-api/SKILL.md` so it is not later diagnosed as a bug.
- **Regenerating the committed `floor/static` produces a large diff with new
  content-hashed asset names.** → Expected and desirable: it is where the
  duplicated three.js (F-6) leaves the repository. The build is reproducible from
  `npm --prefix floor/frontend run build`.
- **`solid viewer` adds a subprocess to every shop open.** → It is a JSON read
  with `needs_node = False`, ordered before the build it guards, so it costs less
  than the failure it prevents.

## Migration Plan

No data or on-disk migration. The sequence within the cycle is: preparation and
route first (red on the absent and incompatible cases), then the frontend swap
and dependency removal, then the regenerated `floor/static`, then the spec, ADR,
and skill amendments. Rollback is reverting the cycle commit; nothing outside the
repository changes state.

## Open Questions

None. The three items brief section 8 left to this cycle are settled above: the
accessor is `solid viewer` as F3 shipped it (D-1), the floor expresses its
minimum as one integer in `floor/preparation.py` (D-2), and the floor declares
the viewer's types locally rather than consuming published declarations (D-4).
