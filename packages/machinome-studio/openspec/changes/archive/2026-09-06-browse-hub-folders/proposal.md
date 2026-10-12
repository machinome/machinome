## Why

The hub lists only the direct children of the working folder, and only as
projects. A maker who groups projects in a subdirectory — `sandbox/`, holding
twenty of them — sees one card saying "not a project repository", and the
projects inside are unreachable. A repository that declares several models —
`3DPrintedClocks`, whose manifest names `wall_clock_01` and `wall_clock_02` —
shows one card that opens the default model, and the other clock has no way in.
Both cases are the same missing idea: a hub entry the maker can enter, with a
way back out.

## What Changes

- The hub lists one folder at a time. It opens on the working folder and shows
  a breadcrumb naming the folders above the one being listed, each of which
  returns the maker to it.
- A directory that is not a project repository but holds project repositories
  below it is listed as a **folder card**. Entering it lists its contents. A
  directory that is neither a project nor holds one anywhere below it remains
  an unopenable card with its reason.
- A project repository that declares more than one named model is also listed
  as a folder card. Entering it lists one project card per declared model.
- Every hub entry is identified by its path relative to the working folder:
  `sandbox/windmill` for a nested project, `3DPrintedClocks/wall_clock_01` for
  one model of a multi-model repository.
- **BREAKING** A session belongs to an openable entry rather than to a project
  directory: each declared model has its own session, agents, conversation,
  build, watch and screenshot, and two models of one repository can be open at
  the same time. The shop's project-scoped HTTP routes are re-keyed from a
  single project-name segment to a session or an entry path.
- The session builds, watches and serves the model its entry names, rather than
  the project's default model.
- A multi-model project's screenshots live one per model at
  `<project>/screenshots/<model>.png`. A single-model project keeps
  `<project>/screenshot.png` exactly as it is today.
- Creating a project from the hub creates it inside the folder the maker is
  currently listing. Creation is not offered while listing a multi-model
  project, whose entries are models rather than directories.
- Creating a folder from the hub is out of scope: folders are directories the
  maker makes on disk, or that a project's manifest declares as models.

## Capabilities

### New Capabilities
- `hub-folder-navigation`: what a folder is, how the hub lists one folder at a
  time, how the maker enters a folder and returns from it, and how every entry
  is named by its path under the working folder.

### Modified Capabilities
- `shop-project-hub`: the hub lists the entries of one folder rather than every
  direct child of the working folder; folder cards join project cards; a project
  is identified by path; creation targets the listed folder.
- `shop-project-sessions`: a session belongs to one openable entry — a project
  and the model it names — so several sessions may share one repository, and
  the at-most-one-session rule is per entry.
- `functional-model-inspection`: a session prepares, builds, watches and serves
  the model its entry names rather than the project's default model.
- `project-model-screenshot`: a multi-model project keeps one screenshot per
  model under a per-model path; a single-model project is unchanged.
- `shop-live-state-stream`: hub snapshots and hub events identify entries by
  their path under the working folder and say which folder they belong to.
- `named-project-bootstrap`: a created project's name is a safe direct-child
  name of the folder being listed, and the shop verifies the repository
  boundary of the entry's project root wherever it sits under the catalogue.

## Impact

- `floor/preparation.py`: listing becomes folder-scoped and entry-typed, model
  selection joins preparation, and the artifact root is resolved for a named
  model rather than the default.
- `floor/sessions.py`: the session registry is keyed by entry path; hub events
  carry the entry path and its folder.
- `floor/app.py`: project-scoped routes (`viewer`, `screenshot`, `artifacts`,
  open, create) are re-keyed; the artifacts and viewer routes move under the
  session, and the hub screenshot route takes an entry path.
- `floor/watcher.py`, `floor/screenshots.py`, `floor/build_package.py`,
  `floor/mcp_server.py`: build, watch, snapshot and the scoped `solid build`
  tool name the session's model.
- `floor/frontend/src/main.tsx` and `styles.css`: folder cards, breadcrumb,
  folder-scoped grid, and path-based client routes.
- Runtime role prompts under `profiles/`: an agent's project root may hold a
  sibling model's session; its instructions name the model it works on.
- `tests/`: hub listing, session identity, and route tests.
- Multi-model project repositories gain the `screenshots/` convention.
- An ADR records that hub entries are paths and that a session belongs to a
  model, with the architecture overview updated to match.
