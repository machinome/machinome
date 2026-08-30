## Why

Opening an already-built project takes over a minute, and almost none of that
time produces anything the maker did not already have.

Measured on Metamaquina2 — 567 nodes, 96 published artifacts, every artifact
already current, so the build renders nothing and its own log says
"Published artifacts are already current":

| what `prepare_project` runs, in order, before the session exists | measured |
| --- | ---: |
| `solid viewer` | 3.8 s |
| `solid build` | 23.5 s |
| `solid snapshot --renderer web` | 46.0 s |
| **total, synchronous, before the session registers or any agent starts** | **73 s** |

Each of the three is avoidable work on a reopen:

- **`solid viewer`** reports the *installed framework's* bundle path and API
  version. That is a property of the shop's own installation, identical for
  every project and every open, and it is re-resolved on each one.
- **The screenshot** is rendered unconditionally
  (`floor/preparation.py:376`), and only *after* rendering are its bytes
  compared against the existing file (`floor/screenshots.py:104`). When the
  model has not changed, the full 46 s is spent to discover that the PNG is
  identical and must not be written. The shop already holds the opposite
  principle for commits — "A commit carrying no model content does not
  render" — but the open path does not apply it.
- **The build** is awaited before the session is registered, so the hub shows
  `opening` and the profile's agents do not start until it finishes, even
  when a complete, valid publication is already on disk and could be shown
  immediately.

Two framework cycles reduce the middle row (`fast-source-closure`,
`fast-cli-startup`), but they cannot address any of the three points above:
those are the shop's own sequencing.

## What Changes

- The shop resolves the framework viewer bundle **once per running shop**
  instead of once per project open, and reuses it for every session.
- The shop renders a project screenshot on open only when the open actually
  changed the publication, or when the project has no valid screenshot yet.
  An open that published nothing renders nothing — the same rule floor-mediated
  commits already follow.
- When a project already has a complete, valid publication, opening **presents
  it immediately**: the session registers, the agents start, and the model is
  shown from that publication while the build runs behind it. The maker is told
  the model is being brought up to date, and the completed build reaches the
  browser over the live-state stream the watchers already publish.
- When a project has no valid publication — a project being created, or one
  never built — opening waits for the build exactly as it does today. There is
  nothing to show, so there is nothing to show early.
- Build failure reporting is unchanged: a failure still reaches the maker
  through the existing `model_build_unavailable` channel rather than being
  swallowed because the session opened first.

## Capabilities

### Modified Capabilities

- `shop-project-sessions`: opening a project may present an existing complete
  publication before its build finishes, rather than always awaiting the build.
- `project-model-screenshot`: the existing "content that cannot change the
  model does not render" rule extends from floor-mediated commits to opening,
  so an open that publishes nothing renders nothing.

### New Capabilities

- `project-open-cost`: what opening a project is permitted to re-do — work
  whose result the shop already holds is not repeated per project or per open.

## Impact

- `floor/preparation.py` — `_viewer_info` becomes shop-scoped;
  `prepare_project` gains publication-change detection around the build and
  stops rendering unconditionally.
- `floor/sessions.py` — `_open` registers the session on an existing valid
  publication and runs the build as a tracked background task; a hub state for
  "open, model rebuilding".
- `floor/app.py` — the hub event carrying that state.
- Reuses existing helpers rather than adding parallel ones:
  `artifact_root_for`, `_validate_snapshot`, `PreparedProject.build_invocation`,
  `screenshot_revision`, `ArtifactWatcher.on_viewer_published`, and
  `Session._request_screenshot_refresh`.
- No change to the launcher, to `--projects-dir`, to project-owned runtime
  selection, or to the repository boundary gate: the boundary is still verified
  before any agent starts.
- Independent of the in-flight `make-shop-floor-event-driven` change, which
  touches the live-state stream and the model watcher rather than the open path.
