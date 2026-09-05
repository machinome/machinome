## Context

The shop is a workspace whose ignored subdirectories are independent
repositories. Today `scripts/setup dev` clones the framework and runs npm
inside `solid-node/solid_node/viewers/{web/app,widget}`; `scripts/dev-env`
symlinks those packages' `node_modules` and build output into each framework
worktree; and the floor asks `solid viewer` for the bundle it serves at
`/projects/<name>/viewer/solid-widget.js`. After the split the framework has
no frontends, and `solid viewer` answers from the installed
`solid-node-viewer` package or fails naming `pip install "solid-node[viewer]"`.

## Goals / Non-Goals

**Goals:** a workspace that installs and develops the viewer as the
independent repository it now is; a bench script that does not describe a
layout that no longer exists; an agent contract and skills that tell agents
where the viewer lives and what the framework does without it; a floor whose
failure message names the real remedy.

**Non-Goals:** changing how the floor mounts or serves the bundle; asking the
viewer package directly (the pilot chose to keep going through the framework);
running viewer development through shop worktrees or sprints.

## Decisions

- **The viewer is a lane, not a framework detail.** AGENTS.md gets a section
  parallel to molejo's: independent repository, its own OpenSpec and ADRs,
  never staged in the shop, honest status. The framework-work lane says the
  viewer is not framework source. `.gitignore` gains `/solid-node-viewer`.
- **Setup follows the licence boundary.** Tier 1 is one pip line with the
  extra. Tier 2 clones `SOLID_NODE_VIEWER_REPO` (default
  `https://github.com/LibreSolid/solid-node-viewer.git`) to
  `./solid-node-viewer`, installs it editable into the workspace venv, and
  builds its widget and app there; a missing npm leaves the viewer unbuilt and
  says so, as before. The framework clone is installed editable as today with
  no npm step.
- **dev-env stops linking frontends.** The discovery loop would find nothing
  and skip silently, but code and tests describing `solid_node/viewers/*`
  packages would mislead the next reader. The step, its comments and its two
  tests go; the port allocation stays because the viewer still reads
  `SOLID_NODE_PORT` and `SOLID_NODE_FRONTEND_PORT` from the worktree's `.env`.
- **The floor is unchanged in code.** `solid viewer` keeps `path` and
  `apiVersion` and adds fields the floor ignores. The floor already surfaces
  the framework's stderr for a failed `viewer` stage, so the remedy the maker
  reads is the framework's — now the extra. The spec is restated; the fake
  `solid` fixture's message follows so tests read like reality.

## Risks / Trade-offs

- [Tier 2 needs a viewer remote that may not exist yet] → setup names the URL
  it tried and stops; `SOLID_NODE_VIEWER_REPO` overrides it, as
  `SOLID_NODE_REPO` already does for the framework.
- [Agents keep suggesting npm inside the framework] → the API skill and the
  machining skill say the viewer is installed, not built, from a project's
  point of view.
