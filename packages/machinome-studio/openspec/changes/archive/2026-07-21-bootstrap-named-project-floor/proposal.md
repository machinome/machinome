## Why

Opening the shop currently accepts an arbitrary optional project path and can
start the browser and agent team before any inspectable model exists, leaving
the maker with a 404 and agents without a guaranteed project repository. A
named-project startup convention must create or validate the project and prove
its initial model usable before any part of the floor becomes open.

## What Changes

- **BREAKING**: Require every shop-open request to provide a project name; the
  floor no longer opens without a project or accepts an arbitrary project path
  as the maker-facing project identity.
- Resolve that name only as `projects/<name>` in the shop workspace and reject
  names that could escape or ambiguously address that directory.
- If the named project does not exist, create the standard solid-node scaffold
  with `solid new`, establish it as its own Git repository, and make its
  default `root` model the first project state.
- Reuse an existing named project without overwriting it, after verifying that
  the directory is the exact project repository root expected by the shop.
- Gate the HTTP service, Codex app-server, and all role threads on a successful
  one-shot initial build whose complete viewer snapshot is available.
- If discovery, creation, repository validation, or initial build fails, start
  no floor, clean up any partial runtime, and report the concrete failure and
  project location instead of exposing a broken browser interface.

## Capabilities

### New Capabilities

- `named-project-bootstrap`: Required project-name selection, safe workspace
  resolution, creation of a missing solid-node project, and validation of an
  existing project repository before the floor can open.

### Modified Capabilities

- `shop-floor-lifecycle`: Opening becomes conditional on named-project
  readiness and a completed initial model, with the service and agents kept
  stopped on any preparation failure.
- `functional-model-inspection`: A successful open guarantees that the initial
  completed viewer snapshot is already available, so the first browser model
  request cannot be the current no-build 404 state.

## Impact

- The Codex shop launcher and orchestrator command-line contract, startup
  ordering, error handling, and cleanup.
- Project-name validation, `projects/` workspace resolution, solid-node command
  invocation, Git repository initialization and verification, and initial
  artifact validation.
- Floor lifecycle and artifact-route acceptance tests, including first-run,
  existing-project, invalid-name, scaffold failure, and build failure paths.
- Shop startup documentation and Codex operating guidance.
- Uses the existing solid-node `build` publication boundary from this
  workspace's `./solid-node` framework checkout; startup tests pin command
  discovery to that checkout rather than an unrelated sibling installation.
