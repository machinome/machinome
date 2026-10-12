## Why

The shop opens for exactly one project, named on the command line before the
service starts, and that project is fixed for the life of the process. A maker
who wants a second project stops the shop and starts another one; a maker who
wants a new project creates it by naming one that does not exist yet and
learning the naming rules from an error message. Every choice the shop needs —
which project, which profile — has to be made in a terminal before anything is
visible.

The reference design replaces that with a project hub: the shop opens on a
landing screen listing the projects it can see, projects are created from a
sheet in the browser, and several projects can be open at once in one service.

## What Changes

- The launcher takes no project name and no profile. **BREAKING**: the
  `project_name` positional argument and the `--profile` option are removed, and
  the shop no longer opens directly into a project from the command line.
- The service starts bound to a working folder rather than a project, and serves
  the project hub (design screen 1a) at `/`.
- Opening a project creates a **session**: one prepared repository, one model
  build, one watcher, one broker, and the profile's standing agents. A project
  has at most one session, so a second browser reaching the same project joins
  the existing one. There is no limit on how many sessions are open at once.
- Each session carries an opaque identifier. The launcher places it in every
  agent process's environment and the agent command defaults to it, so an agent
  addresses its own session without stating one and cannot reach another.
- A session ends when the maker closes it from the workspace. Sessions are
  **ephemeral**: nothing survives closing the session or stopping the service.
  Durable sessions are deliberately out of scope and left to a later change.
- Projects are created from the new-project sheet (design screen 3c), which
  takes a safe direct-child directory name without imposing a naming style and
  a profile. **BREAKING**: creation now writes the chosen
  profile into the project's `pyproject.toml`, which scaffolding previously was
  required not to do.
- The hub lists every directory in the working folder. A directory that cannot
  be opened — for example, one that is not its own Git repository — is
  listed as unopenable with the reason, instead of being a fatal error that
  prevented the shop from starting at all.
- Failure to prepare a project or to start its agents leaves the maker on the
  hub with the reason and no partial session. A failed *model build* still opens
  the session, so the workspace can show the build error over a project that
  cannot currently build.
- The hub reports which agent backends are present, read-only: each known
  backend's executable, version and configured model, and whether it was found.
  Detection happens automatically when the hub loads; there is no manual
  detection control. Enabling, disabling and locating backends stay with the
  unimplemented setup screens.
- The project grid uses four columns on full-HD displays, three on ordinary
  desktop widths, two at compact widths and one on narrow screens. Cards are at
  least 252 pixels tall with 158-pixel model previews.
- The workspace is unchanged except that it is served at `/projects/<name>` and
  gains a close control in its title bar.

## Capabilities

### New Capabilities
- `shop-project-hub`: the landing screen — what the maker sees before choosing a
  project, which entries in the working folder are listed and which are
  openable, how a project is created, and what backend availability is reported.
- `shop-project-sessions`: several concurrent project sessions in one service —
  session identity, one session per project, what opening and closing guarantee,
  and how an agent is confined to its own session.

### Modified Capabilities
- `shop-floor-lifecycle`: opening and closing become per-session operations
  requested from the browser rather than process startup and shutdown; the
  service starts and stays running with no project open; the initial model build
  no longer gates the floor's availability.
- `named-project-bootstrap`: the project name arrives from the hub rather than
  the command line; a working-folder entry that fails validation is listed as
  unopenable rather than refusing the whole shop.
- `project-runtime-selection`: creating a project writes its `profile` key,
  reversing the requirement that scaffolding not write one; with `--profile`
  removed there is no override, so a project's declaration — or the shop default
  — always decides.
- `shop-runtime-profile`: profile selection loses the `--profile` source and
  resolves from the project's declaration or the shop default alone.
- `shop-agent-lifecycle`: a shop is opened for a project rather than by a
  profile option, so the roster follows the project's declared profile.
- `shop-browser-workspace`: the browser has more than one location; the
  workspace is one project's view at `/projects/<name>` and offers closing.
- `shop-live-state-stream`: the live stream is per session, and the hub has its
  own stream for project and session state.

## Impact

- `floor/__main__.py` — loses project and profile arguments and the
  prepare-then-serve sequence.
- `floor/app.py` — one broker per session instead of one per process; run,
  conversation, stream and artifact routes become session-scoped; new hub,
  project and session routes.
- `floor/preparation.py`, `floor/watcher.py`, `floor/profiles.py` — preparation,
  watching and profile resolution become per-session and move behind a request.
- `floor/agent.py` — session identifier from the environment.
- `floor/backends/` — a read-only presence and version probe per backend.
- `floor/frontend/` — the hub and the new-project sheet, routing, and the close
  control; the existing workspace presentation is otherwise untouched.
- `tests/` — end-to-end tests open projects through the API instead of the
  command line.
- `AGENTS.md`, `skills/running-the-shop/SKILL.md`, `README.md`,
  `docs/architecture-overview.md` — the launcher no longer takes a project or a
  profile.
