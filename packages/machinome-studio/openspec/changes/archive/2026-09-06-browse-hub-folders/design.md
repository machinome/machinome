## Context

The hub's unit of work is a direct child of the working folder, named by one
path segment. `floor/preparation.list_projects` iterates the working folder's
directories; `floor/sessions.SessionRegistry` keys sessions by that name;
`floor/app.py` exposes `/api/projects/{name}/session`,
`/projects/{name}/screenshot.png`, `/projects/{name}/viewer/solid-widget.js`
and `/projects/{name}/artifacts/{path}`; the React client routes on
`^/projects/([^/]+)$`. Preparation resolves the artifact root by asking
`solid models --json` for the *default* model's build directory, builds with a
bare `solid build`, and renders one screenshot at `<project>/screenshot.png`.

Two shapes of catalogue break against that. A grouping directory such as
`projects/sandbox/` — twenty-one project repositories inside — fails the
repository check and is listed as unopenable, hiding everything in it. A
repository declaring several models, such as `projects/3DPrintedClocks/` with
`wall_clock_01` and `wall_clock_02`, opens only its default model.

The framework already supports the multi-model half: `solid models --json`
reports every declared model with its own `build_dir` under `_build/<model>`,
`solid build <model>` builds one by name, and the build lock is
`<build_dir>.lock`, so two models of one repository build concurrently without
contending. What is missing is entirely on the shop side.

The pilot decided that each declared model is an independently openable project
with its own session and agents, sharing the repository — not a model switcher
inside one session.

## Goals / Non-Goals

**Goals:**

- One hub listing per folder, with a breadcrumb, reachable to any depth.
- A grouping directory and a multi-model project both present as folder cards.
- An entry path — `sandbox/windmill`, `3DPrintedClocks/wall_clock_01` — as the
  single identity for listing, opening, live state, and browser location.
- A session that builds, watches, serves, screenshots and tests its own model.
- No change to how a plain single-model project at the top level behaves.

**Non-Goals:**

- Creating folders from the hub. Folders are directories on disk, or the models
  a manifest declares.
- A model switcher inside an open workspace; the folder listing replaces it.
- Coordinating two sessions that share a repository's Git working tree beyond
  what the shop already does for one session.
- Changing the framework. Everything needed is already in `solid models`,
  `solid build <model>`, `solid test` and `solid snapshot`.

## Decisions

### Entry paths, resolved once, in the shop

A `HubEntry` carries `path` (POSIX, relative to the working folder), a `kind`
of `folder`, `project` or `unopenable`, and for a project its `project_root`
and `model` (the declared model name, or `None` for a single-model project).
`resolve_entry(path, project_home)` is the single gate: it splits the path,
refuses empty, dot and absolute components, walks only inside the working
folder, and stops at the first directory that is a Git repository root — every
remaining segment is then a model name checked against `solid models --json`.

Stopping at the repository root is what makes the two folder kinds
unambiguous: inside a project repository the hub never lists directories, only
declared models, so `3DPrintedClocks/wall_clock_01` cannot collide with a
subdirectory of the same name.

*Alternative rejected:* an opaque per-entry id assigned by the shop. It keeps
URLs single-segment but makes browser locations unshareable across restarts and
hides the path the maker is actually looking at.

### Listing one folder

`list_folder(project_home, path)` returns the entries of one directory. For each
child directory it decides, in order: is it a Git repository root (then a
project — a folder if its manifest declares more than one model, otherwise an
openable project); else does any Git repository root exist below it (then a
folder); else unopenable with its reason. The "holds a project below it" search
is a bounded walk that stops descending into a directory once it finds a
repository root, and skips `.git` and `_build`.

`solid models --json` is run once per repository per listing, at ~40 ms. A
listing of the working folder therefore costs one subprocess per project, as it
already costs three `git` subprocesses per project today.

*Alternative rejected:* a recursive listing of the whole catalogue delivered at
once, filtered in the browser. It makes the deep-nesting cost unbounded and
gives the folder card nothing cheap to count.

### Route re-keying

Multi-segment names cannot be a single FastAPI path parameter without `%2F`
ambiguity, so project-scoped routes are re-keyed rather than made to hold a
path:

- open becomes `POST /api/sessions` with `{"path": …}`;
- create becomes `POST /api/projects` with `{"folder": …, "name": …,
  "profile": …}`;
- listing becomes `GET /api/entries?folder=<path>`, and the hub stream
  `GET /api/stream?folder=<path>`;
- artifacts and the viewer bundle move under the session that already
  identifies them: `/api/sessions/{id}/artifacts/{path}` and
  `/api/sessions/{id}/viewer/solid-widget.js`;
- the hub screenshot, which must work for a closed entry, becomes
  `GET /api/screenshot?path=<entry path>&revision=<hash>`.

Client routes stay readable — `/folders/<path>` and `/projects/<path>` — because
the SPA catch-all serves `index.html` for any depth and the client parses the
location itself.

*Alternative rejected:* percent-encoding the path into one segment. Starlette
decodes `%2F` before matching, so `sandbox%2Fwindmill` would not match
`{name}` reliably.

### The model travels with the session

`PreparedProject` gains `model: str | None`. Preparation asks `solid models
--json` once and takes the named model's `build_dir` instead of the default's;
`build_command` becomes `(solid, "build", model)` when a model is named;
`refresh_screenshot` renders that model into `screenshots/<model>.png`; the
watcher's rebuild uses the same invocation it always did, which now carries the
model. The scoped `solid_build`, `solid_test` and `solid_snapshot` tools default
their reference to the session's model rather than to nothing, so an agent that
passes no reference builds its own model and not its sibling's.

The session id remains the workspace's identity, so nothing downstream of
opening needs to learn about paths.

### Screenshots for named models

A single-model project keeps `screenshot.png` untouched. A named model uses
`screenshots/<model>.png`, a shop-managed convention parallel to the existing
one, kept out of `_build` because it is committed evidence. `screenshot_path`,
`screenshot_revision` and `is_safe_screenshot` take the entry rather than the
project root; the commit-staging path stages whichever of the two the session
owns.

*Alternative rejected:* `_build/<model>/screenshot.png`. It is where the render
already lands, but it is not committed, so a fresh clone would show no previews
until every model is built.

## Risks / Trade-offs

- **Two agent rosters commit to one Git working tree.** The pilot chose this
  deliberately. Nothing in the shop serialises them, so two machinists on
  `3DPrintedClocks` can stage each other's in-progress edits: `git_add` takes
  named paths, but `git_commit` commits the index, and the index is shared by
  the whole working tree. → Each session's agents are told which model they
  own, so they stage their own model's sources; the shop does not otherwise
  serialise them. The residual hazard is recorded here rather than papered
  over — it is the hazard two people sharing one checkout already have — and
  narrowing `git_commit` to the paths its session staged is the follow-up if it
  bites.
- **A shared source change rebuilds both models.** The watcher of each session
  watches the whole repository, so editing a shared library rebuilds both
  models. → This is correct behaviour, not a defect: both models did change.
  The cost is bounded by the per-model build lock, which lets them run
  concurrently.
- **Listing cost grows with catalogue depth.** The "holds a project" walk could
  be expensive on a pathological tree. → It stops at the first repository root
  on each branch, skips `.git` and `_build`, and only runs for directories that
  are not themselves repositories.
- **Route re-keying breaks any bookmarked workspace URL.** → The shop is
  private and experimental; the client routes it emits are all updated in this
  change.
- **A manifest that declares one named model.** It is a project, not a folder,
  so its screenshot path would flip between conventions if it later declared a
  second. → The rule is stated on the count of declared models, and the
  screenshot for a single-model project is always `screenshot.png`; gaining a
  second model re-renders both under `screenshots/`.

## Migration Plan

No data migration. Existing projects keep `screenshot.png`; a multi-model
project renders into `screenshots/` on its next open. `3DPrintedClocks` needs
no manifest change — it already declares both clocks.

## Open Questions

- Whether a folder card should preview the models or projects it holds rather
  than a folder mark. Left as a folder mark here; it is a card-design change
  that needs no spec change to revisit.
