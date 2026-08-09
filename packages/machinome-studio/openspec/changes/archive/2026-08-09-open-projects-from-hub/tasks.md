## 1. Session ownership

- [x] 1.1 Add a failing test in `tests/test_floor_api.py` that two sessions for different projects hold independent brokers, rosters and conversations
- [x] 1.2 Extract a `Session` type owning project root, artifact root, build environment, resolved profile, `Broker`, watcher task and agent processes — everything `create_app` currently closes over
- [x] 1.3 Add a `SessionRegistry` keyed by project name, holding at most one session per project, with open, lookup, and close
- [x] 1.4 Give each session an opaque generated identifier distinct from the project name, and index the registry by it for agent lookup
- [x] 1.5 Rebuild `create_app` to take a working folder and an empty registry instead of one prepared project

## 2. Agent confinement

- [x] 2.1 Add failing tests in `tests/test_agent_cli.py` that the agent command reads its session from the environment, and in `tests/test_floor_api.py` that an unknown, missing, or foreign session identifier is refused rather than applied
- [x] 2.2 Move the agent-facing routes to `/api/sessions/{session_id}/...`, resolving through the registry and returning 404 for an unknown identifier
- [x] 2.3 Replace `--run` and its `shop-floor` default in `floor/agent.py` with `--session`, defaulting from `FLOOR_SESSION`
- [x] 2.4 Set `FLOOR_SESSION` alongside `FLOOR_URL` when a session spawns each agent process
- [x] 2.5 Add a test that an agent of a closed session cannot reach the later session of the same project

## 3. Opening and closing a project

- [x] 3.1 Add failing tests in `tests/test_orchestrator.py` for the open sequence: profile resolution, preparation and agent start are fatal and leave nothing behind, while a failed model build still opens the session
- [x] 3.2 Move preparation, profile resolution, build and agent start out of `floor/__main__.py` into a session-opening routine on the registry
- [x] 3.3 Run opening as a task, with the build and git work off the event loop so one project's opening cannot stall another's stream
- [x] 3.4 Implement teardown on fatal failure so no partial session survives, and report the failing stage
- [x] 3.5 Implement session close: end every agent, stop the watcher, drop the registry entry, bounded and forcing a process that will not exit
- [x] 3.6 Close every open session when the shop stops
- [x] 3.7 Add `POST /api/projects/{name}/session` and `DELETE /api/sessions/{id}`, returning immediately and reporting progress through the hub stream
- [x] 3.8 Add a test that a second open request for an already-open project joins the existing session rather than starting a second

## 4. Project inventory

- [x] 4.1 Add failing tests in `tests/test_project_preparation.py` for listing a working folder holding a valid project, a directory that is not a Git repository root, and a regular file that must not be listed
- [x] 4.2 Implement listing: every directory under the working folder with its name, openability and the reason when it cannot be opened; omit regular files
- [x] 4.3 Read each listed project's declared profile, defaulting to `fordesmac`, without failing the listing on a project whose declaration is unusable
- [x] 4.4 Read branch and last commit time per project through `git`, off the event loop
- [x] 4.5 Add `GET /api/projects` returning the list with open state from the registry
- [x] 4.6 Add a test that an unopenable entry does not prevent the listing or the opening of any other project

## 5. Project creation

- [x] 5.1 Add failing tests in `tests/test_project_runtime_selection.py` that creation writes the chosen `profile` key, and in `tests/test_project_preparation.py` that a name colliding with any existing entry is refused and creates nothing
- [x] 5.2 Reverse the scaffold rule in `floor/preparation.py` so creation writes `[tool.solid-node-studio] profile` from the maker's choice
- [x] 5.3 Validate a requested name as one safe direct-child directory name, without imposing a style convention, and unused by any entry of the working folder before any filesystem effect
- [x] 5.4 Add `POST /api/projects` taking name and profile, creating the project and opening it as one action
- [x] 5.5 Remove `--profile` from profile resolution in `floor/profiles.py`, leaving the project declaration and the shop default
- [x] 5.6 Keep an accepted creation as a provisional project in registry snapshots and events until its directory exists or creation fails

## 6. Backend reporting

- [x] 6.1 Add failing tests that a missing executable reports as missing and a present one reports its path, version and configured model
- [x] 6.2 Add a read-only probe per backend in `floor/backends/`: executable lookup, version invocation, configured model from the profile
- [x] 6.3 Add `GET /api/backends` and `POST /api/backends/detect`, with no enable, disable or locate operation

## 7. Streams

- [x] 7.1 Add failing tests that a project stream carries only its own project's changes, and that a hub stream carries project and open-state changes and no conversation
- [x] 7.2 Move today's `/api/stream` to `/api/sessions/{id}/stream`, bound to that session's broker, keeping the snapshot-then-events shape unchanged
- [x] 7.3 Implement the hub stream at `/api/stream`: snapshot of the project list on connect, then opening, open, failed and closed changes
- [x] 7.4 Scope `/artifacts/{path}` per session under the project's browser location, and update the viewer and S1 bridge URLs to match

## 8. Browser

- [x] 8.1 Add routing: hub at `/`, project workspace at `/projects/<name>`, with a project that has no session returning the maker to the hub
- [x] 8.2 Build the hub (screen 1a) at the fidelity stated in `docs/design/README.md`: working-folder card without disk size, backends group, project grid, dashed new-project tile, and the documented empty state
- [x] 8.3 Build the unopenable project card, carrying its reason, from the design's existing tokens
- [x] 8.4 Build the new-project sheet (screen 3c) with name and profile fields, its validation messages, and its blurred-hub presentation
- [x] 8.5 Show opening and failure state on the project card from the hub stream
- [x] 8.6 Point the workspace at the per-session stream and add the close control to the title bar, top right
- [x] 8.7 Warn before closing while an agent holds an assignment, and return every browser on that project to the hub when it closes
- [x] 8.8 Rebuild the frontend bundle into `floor/static/`
- [x] 8.9 Close the creation sheet immediately after acceptance and upsert a visible `creating` project card until the project opens or fails
- [x] 8.10 Remove the manual `Detect backends` control while retaining automatic read-only backend reporting
- [x] 8.11 Apply the ratified responsive 4/3/2/1 card columns and 252px card / 158px preview proportions

## 9. Launcher, tests and documentation

- [x] 9.1 Remove `project_name` and `--profile` from `floor/__main__.py`, keeping `--port` and the hidden test options
- [x] 9.2 Update `tests/test_floor_entrypoint.py` and `tests/test_shop_lifecycle_e2e.py` to open projects through the API rather than the command line
- [x] 9.3 Update `tests/test_runtime_profiles.py` and `tests/test_project_runtime_selection.py` for the removal of the `--profile` override
- [x] 9.4 Update `AGENTS.md` and `skills/running-the-shop/SKILL.md`: the launcher takes no project and no profile, and the pilot chooses the project in the browser
- [x] 9.5 Update `README.md` for the new launcher and the working folder
- [x] 9.6 Update `docs/architecture-overview.md` to describe one service over a working folder, per-project sessions, and agent confinement by session identifier
- [x] 9.7 Run the full test suite and confirm no path still assumes one project per process
- [x] 9.8 Sync the completed delta specifications into the baseline specifications and archive the change
