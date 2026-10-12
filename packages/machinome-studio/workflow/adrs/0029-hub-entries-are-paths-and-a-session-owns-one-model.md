# ADR 0029: Hub entries are paths, and a session owns one model

**Status:** Accepted

**Date:** 2026-09-06

**Origin:** `browse-hub-folders`

## Context

The hub's unit of work was a direct child of the working folder named by one
path segment. `list_projects` iterated that folder's directories; sessions were
keyed by that name; `/api/projects/{name}/session`,
`/projects/{name}/screenshot.png` and `/projects/{name}/artifacts/{path}` were
keyed by it; the React client routed on `^/projects/([^/]+)$`.

Two shapes of real catalogue broke against that:

- `projects/sandbox/` groups twenty-one project repositories. It is not a
  repository itself, so it failed the boundary check and was listed as one card
  reading "not a project repository", with everything inside unreachable.
- `projects/3DPrintedClocks/` is one repository whose manifest declares
  `wall_clock_01` and `wall_clock_02`. Opening it opened the default model, and
  the other clock had no way in.

Both are the same missing idea: a hub entry the maker can enter.

The framework already supports the second half. `solid models --json` reports
each declared model with its own `build_dir` under `_build/<model>`,
`solid build <model>` builds one by name, and the build lock is
`<build_dir>.lock`, so two models of one repository build concurrently without
contending. What was missing was entirely on the shop's side.

## Decision

**A hub entry is a path relative to the working folder.** `sandbox/windmill`
for a nested project, `3DPrintedClocks/wall_clock_01` for one model. That path
is the browser location, the open request, the hub-state identity, and the
session key. `resolve_entry` is the single gate: it refuses empty, dot and
absolute segments, walks only inside the working folder, and **stops at the
first directory that is a repository root** — every remaining segment is a
model name checked against the manifest.

Stopping at the repository root is what makes the two kinds of folder
unambiguous. Inside a project the hub lists declared models and nothing else,
so a model name can never collide with a directory of the same name.

**A folder is either a directory holding projects, or a project holding
models.** A directory that is not a repository and holds a repository anywhere
below it is a folder; a repository declaring more than one model is a folder of
those models; a repository declaring one, or none, stays a single project card;
a directory that is neither remains unopenable with its reason. Model names are
read straight from `pyproject.toml`, not through `solid models`, so listing a
folder of twenty projects costs no subprocess.

**A session belongs to one entry — a repository and the model it names.** This
was the pilot's choice over a model switcher inside one session: each model has
its own session, agents, conversation, build, watch and screenshot, and two
models of one repository can be open at once. `PreparedProject` carries the
model; the artifact root is resolved for that model rather than the project
default; `build_command` names it; the scoped `solid_build`, `solid_test` and
`solid_snapshot` default their reference to it; and both backends state it in
the role contract.

**Project-scoped routes are re-keyed rather than made to hold a path.**
Starlette decodes `%2F` before matching, so a multi-segment name cannot be one
path parameter. Opening becomes `POST /api/sessions` with the entry path;
listing becomes `GET /api/entries?folder=`; the hub stream takes the same
query; artifacts and the viewer bundle move under the session that already
identifies them; and the hub screenshot, which must work for a closed entry,
becomes `GET /api/screenshot?path=`. Client routes stay readable —
`/folders/<path>` and `/projects/<path>` — because the SPA catch-all serves
`index.html` at any depth.

**A named model's preview lives at `screenshots/<model>.png`.** A single-model
project keeps the root `screenshot.png` exactly as it was. The per-model path is
committed evidence like its predecessor, rather than living in `_build`, so a
fresh clone shows previews before anything is built.

## Consequences

- The hub lists one folder at a time, with a breadcrumb; a catalogue can nest to
  any depth.
- Two agent rosters can now commit to one Git working tree. `git_add` takes
  named paths but `git_commit` commits the index, and the index is shared. Each
  session's agents are told which model they own; nothing else serialises them.
  This is the deliberate cost of the pilot's choice, and narrowing `git_commit`
  to the paths its own session staged is the follow-up if it bites.
- A change to source both models share rebuilds both. That is correct — both
  models did change — and the per-model build lock lets the two builds run at
  the same time.
- Bookmarked workspace URLs from before this change no longer resolve. The shop
  is private and experimental, and every client route it emits is updated here.
- Creating a folder from the hub is deliberately not offered: folders are
  directories the maker makes on disk, or the models a manifest declares.

## References

- `floor/preparation.py` — `HubEntry`, `resolve_entry`, `resolve_folder`,
  `new_entry`, `list_folder`, `declared_models`, `resolve_artifact_root`
- `floor/sessions.py` — `_by_entry`, `entries`, `lists_models`, `publish_hub`
- `floor/app.py` — `/api/entries`, `/api/sessions`, `/api/screenshot`,
  session-scoped artifacts and viewer
- `floor/screenshots.py` — `screenshot_path(project_root, model)`
- `floor/frontend/src/main.tsx` — `Hub`, `Breadcrumb`, folder cards, routing
- OpenSpec change `browse-hub-folders`; capabilities `hub-folder-navigation`,
  `shop-project-hub`, `shop-project-sessions`, `functional-model-inspection`,
  `project-model-screenshot`, `shop-live-state-stream`,
  `named-project-bootstrap`
