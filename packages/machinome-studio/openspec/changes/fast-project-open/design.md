## Context

`SessionRegistry._open` (`floor/sessions.py`) awaits `prepare_project` in a
thread, then registers the session, starts the orchestrator, and starts the
watchers. `prepare_project` (`floor/preparation.py`) does, in order: resolve and
verify the project repository, scaffold and `git init` when creating,
`_viewer_info` (`solid viewer`), `solid build`, `_validate_snapshot`, and
`refresh_project_screenshot` (`solid snapshot --renderer web`).

Nothing about that order is wrong for a project being created. All of it is
wrong for reopening a project that is already built, which is the common case
and the one the maker feels.

The pieces needed to fix it already exist. `artifact_root_for` and
`_validate_snapshot` decide whether a publication is complete and valid.
`ArtifactWatcher` already forwards each completed publication and calls
`on_viewer_published`, which already triggers `Session._request_screenshot_refresh`.
`PreparedProject.build_invocation()` already exists so that the open path and
the watcher build the same way. `screenshot_revision()` already answers "is
there a valid screenshot" cheaply. This change is mostly re-sequencing around
those, not new machinery.

## Goals / Non-Goals

**Goals:**

- A reopen of an already-built project presents the model immediately.
- No screenshot render when the open published nothing.
- One `solid viewer` per running shop.
- Build failures, the repository boundary gate, and screenshot subordination
  are exactly as strict as today.

**Non-Goals:**

- Making the build itself faster. That is `fast-source-closure` and
  `fast-cli-startup`, in the framework.
- Making the screenshot render faster. On Metamaquina2 roughly 26 s of it is
  the browser drawing 115 MB of STL; this change avoids the render rather than
  accelerating it.
- Changing the live-state stream or the model watcher — that is the in-flight
  `make-shop-floor-event-driven` change.
- Caching anything across shop restarts. The viewer bundle is resolved once per
  running shop, not persisted.

## Decisions

### Split `prepare_project` into verify-and-prepare, and build

The repository work (resolve, boundary-verify, scaffold, `git init`, profile
declaration, initial commit) stays synchronous and stays before the session
exists — the boundary gate must hold before any agent starts, and a project
being created has nothing to present anyway.

The build, snapshot validation, and screenshot become a separate operation the
caller may run before registering the session or after. Both callers use
`PreparedProject.build_invocation()` so there is still one definition of how
this project builds.

*Alternative — a flag on `prepare_project`.* Rejected: a boolean that silently
reorders half a function's effects is how this kind of code becomes untestable.
Two named operations state what happens.

### Decide "did this open publish anything" from `viewer.json`'s content

Capture a digest of `_build/viewer.json` before the build and after it. The
framework only rewrites that file when the document actually differs
(`_write_viewer_snapshot` returns early on identical bytes), and the document
records each node's mtime, so a re-rendered artifact does change it.

Use the content digest rather than the mtime: `atomic_write` sets a fresh mtime
whenever it writes, and reading one small JSON file is cheap next to a 46 s
render. A missing file before and a present file after is a publication.

*Alternative — ask the framework whether it published.* Better, but it is a
framework interface change and this change is shop-scoped. The digest is
decided from the artifact the framework already publishes atomically.

### Present an existing publication, then build behind it

When `_build/viewer.json` exists and passes `_validate_snapshot`, register the
session, start the orchestrator and the watchers, then start the build as a
task tracked on the session. The watchers are started *before* the build so the
`ArtifactWatcher` cannot miss the publication it produces.

The maker is told the model is being brought up to date, and told again when it
completes, on **both** surfaces — because clicking a card navigates straight to
`/projects/<name>`, so in the common flow the maker never looks at the hub card
at all:

- the hub card, from `model_building` on the hub `open` event and in
  `/api/projects`;
- the workspace, from `model_building` in the session snapshot, cleared by a
  `model_build_settled` event on the session broker.

That settle event is required, not decorative. The case this whole change
exists for — reopening a project nothing has changed — publishes nothing: the
framework does not rewrite an identical `viewer.json`, so no artifact moves and
`ArtifactWatcher` stays silent. With no settle event the workspace notice would
stick on forever, which is a worse lie than saying nothing. It therefore fires
in a `finally`, for every outcome: published new work, published nothing, or
failed.

The flag lives on the broker rather than on the session, so the hub listing and
the session stream cannot disagree about it, and `Broker.subscribe_snapshot()`
registers the subscriber and serialises the snapshot with no `await` between
them. A browser therefore either reads `model_building: true` and then receives
the settle event, or reads `false` because it already settled — there is no
window in which the settle is missed. Reading the initial state from the session
snapshot rather than from `/api/projects` is what closes that window: the REST
fetch and the later stream open are two round trips with a gap between them.

A failure additionally publishes `model_build_unavailable` on the session
broker, the channel the watcher rebuild path already uses, before the settle.

The background build task is registered with the session's existing task
tracking so `Session.close()` cancels and awaits it like any other, and a
session cannot outlive a build or a build outlive its session.

### The screenshot decision lives with the build result

`refresh_project_screenshot` is called only when the build changed the
publication, or when `screenshot_revision()` reports no valid screenshot. The
byte comparison inside `refresh_project_screenshot` stays — it is still the
guard that prevents an identical PNG being rewritten — but it is no longer the
only thing preventing a pointless render.

## Risks / Trade-offs

- **A stale model is presented as current.** The whole point is to show a
  publication that may be out of date → the hub says so until the build
  finishes, and the spec forbids presenting a not-yet-current publication as
  settled. This is the one behaviour the pilot must be comfortable with, and it
  is why the "brought up to date" state is a requirement and not a nicety.
- **A background build outliving its session**, leaking a subprocess into a
  closed project → tracked on the session and cancelled in `close()`, like the
  existing event tasks.
- **Watcher started before the build could publish a partial state** → it
  cannot: publication is an atomic rename into `_build`, which is exactly what
  `ArtifactWatcher` listens for (ADR-013).
- **A project whose publication is valid but whose artifacts were deleted
  behind the shop's back** → `_validate_snapshot` already checks every
  referenced artifact is a real file inside `_build`, so it fails the
  present-early test and the open waits, as for an unbuilt project.
- **Digest says "unchanged" but the model did change** → would skip a needed
  screenshot; mitigated because the document records per-node mtimes, and
  bounded because the next real rebuild republishes and the watcher refreshes
  the screenshot then.
- **One `solid viewer` per shop hides a framework upgraded underneath a running
  shop** → accepted: replacing the framework under a running shop already
  invalidates far more than the bundle path, and the shop is restarted for it.
