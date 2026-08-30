# ADR 0028: Open on the published model, and build behind it

**Status:** Accepted

**Date:** 2026-08-30

**Origin:** `fast-project-open`

## Context

Opening a project ran three solid-node subprocesses to completion before the
session existed. Measured on Metamaquina2 — 567 nodes, 96 published artifacts,
every artifact already current, so the build rendered nothing and logged
"Published artifacts are already current":

| step | measured |
| --- | ---: |
| `solid viewer` | 3.8 s |
| `solid build` | 23.8 s |
| `solid snapshot --renderer web` | 43.6 s |
| total before the session registered or any agent started | **~71 s** |

Every one of the three was avoidable on a reopen.

`solid viewer` reports the *installed framework's* bundle path and API version.
That is a property of the shop's own installation — the same answer for every
project and every open — yet it was asked again each time.

The screenshot was rendered unconditionally and only *then* compared, byte for
byte, against the existing file. When the model had not changed, the entire
43.6 s bought the discovery that the PNG was identical and must not be written.
The shop already held the opposite rule for the other path that triggers a
render: a floor-mediated commit carrying no model content does not render. The
open path simply did not apply it.

And the build was awaited before the session was registered, so the hub showed
`opening` and the profile's agents did not start, even when a complete, valid
publication was already on disk and could have been shown at once.

Two framework cycles (ADR-058, ADR-059 in solid-node) cut the middle row, but
none of the three problems above is the framework's; they are the shop's own
sequencing.

## Decision

**Resolve the viewer bundle once per running shop.** The required-API check and
the no-usable-bundle failure are unchanged; only when the question is asked
moves.

**Render on open only when the open changed what is published.** The decision is
taken from a sha256 of `_build/viewer.json` captured before and after the build
— not from its mtime, since `atomic_write` refreshes that whenever it writes,
and not by rendering and comparing afterwards, which still pays the whole cost.
A project with no valid screenshot still gets one, so a never-rendered project
does not stay without a preview.

**Present an existing complete publication immediately.** When
`_build/viewer.json` exists and passes the snapshot validation the shop already
performs, the session registers, the orchestrator and watchers start, and the
build then runs as a task owned by the session. Watchers start *before* the
build, so the atomic publication cannot be missed. A project with nothing
published — one being created, or never built — still waits, because there is
nothing to present.

Preparation splits into named operations rather than gaining a flag: repository
work (resolve, boundary-verify, scaffold, `git init`, profile declaration), the
build, and the initial commit for a created project. The repository boundary is
verified before any agent starts on both paths.

**Tell the maker on both surfaces, and clear it from a settle event.** Opening a
project navigates straight to `/projects/<name>`, so a maker in the common flow
never sees the hub card. The state therefore appears on the hub card and in the
workspace, and a `model_build_settled` event on the session broker clears it.

That event is load-bearing. The case this whole change exists for — reopening a
project nothing has changed — publishes nothing: the framework does not rewrite
an identical `viewer.json`, no artifact moves, and the artifact watcher stays
silent. Without a settle event the workspace notice would stick on forever,
which is a worse lie than saying nothing. It fires in a `finally`, for every
outcome.

The flag lives on the broker, so the hub listing and the session stream cannot
disagree, and the snapshot is serialised in the same breath as the subscriber is
registered — so a browser either sees `model_building` and then the settle, or
sees it already false. Initial state comes from the session snapshot rather than
a REST fetch precisely to close that window.

## Consequences

- A warm reopen no longer blocks on work whose result the shop already holds.
  The ~71 s of blocking subprocesses becomes roughly nothing, with an ~8 s
  build behind an already-usable session.
- **`open` now means "shown, and being checked" rather than "nothing is shown
  until it is correct".** This is the real cost of the decision: a maker can be
  looking at a model one edit stale. It is why telling them is a ratified
  requirement rather than a nicety, and why the settle event exists.
- Build failure reporting is unchanged — `model_build_unavailable` still
  reaches the maker, and the previous publication remains available rather than
  the session failing to open.
- Closing a project mid-build is not instant: `asyncio.to_thread` cannot
  interrupt a running `solid build`, so `close()` waits for that subprocess.
  The build never outlives its session; it just bounds shutdown.
- Neither notice is recorded in `docs/design/README.md`. The reference design
  has no "open but rebuilding" card state, so the appearance was chosen to match
  the design's existing informational amber and its extra-line slot. If the
  reference design is updated, that is where it belongs.

## References

- `floor/preparation.py` — `resolve_viewer_bundle`, `build_project`,
  `commit_new_project`, `has_complete_publication`, `_publication_digest`
- `floor/sessions.py` — `_build_behind`, `Broker.model_building`,
  `model_build_settled`
- `floor/frontend/src/main.tsx` — hub card and workspace notices
- OpenSpec change `fast-project-open`; capabilities `project-open-cost`,
  `shop-project-sessions`, `project-model-screenshot`
