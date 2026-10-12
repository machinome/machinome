## Why

The maker's live view of the functional model depends on an agent remembering
to run a process. The machinist's role card instructs it to start
`solid develop root --callback <url>` at the beginning of an assignment and keep
it running; the orchestrator mints a token, hands that exact command to the
machinist alone, and the broker turns the resulting POST into `model_changed`.

That makes a maker-facing guarantee conditional on model behaviour. If the
machinist forgets the command, substitutes a finite `solid build`, lets the
process die, or is not the role doing the editing, the browser silently shows a
stale model with no indication that it is stale. The designer and the pilot can
change project files too, and neither of them refreshes anything. Nothing
detects any of these; the failure mode is indistinguishable from "nothing
changed".

The shop already runs `solid build root` itself during preparation and already
owns the `_build` directory it serves. Detecting a change and rebuilding is
shop work, not agent work.

## What Changes

- The shop gains a deterministic model watcher that observes the active
  project's Python sources, rebuilds through the solid-node CLI when they
  change, and refreshes the maker's view when the rebuild publishes new
  artifacts. It runs for the whole life of the floor, independent of which
  role — or the pilot — changed the file.
- A failed rebuild becomes visible. Today a failure is silence; the maker keeps
  the last good model with no signal. The shop publishes a distinct build-failure
  event carrying the failure text, and the browser shows it without discarding
  the last inspectable model.
- **BREAKING** (internal seam only): the callback path is removed — the
  orchestrator's token and callback URL, the broker's
  `POST /api/runs/{run_id}/model/ready/{token}` route, `--callback-token`,
  `RoleContext.model_callback_url`, and the three backend prompt blocks that
  render the develop command.
- The machinist's role card loses its process-management paragraph. The role
  stops owning a long-running framework process on the maker's behalf, which
  restores the foreman/orchestrator boundary the architecture already states:
  agents manage work, the deterministic layer manages processes.
- ADR 0010 records the decision and supersedes the callback mechanism in
  ADR 0004. The artifact boundary ADR 0004 established is unchanged and
  reaffirmed: floor still never imports, executes, or serves project Python,
  and the completed `_build` directory remains the only functional-model input.

## Capabilities

### New Capabilities

None. This changes how an already-specified outcome is achieved and adds one
requirement to the capability that owns it.

### Modified Capabilities

- `functional-model-inspection`: the refresh requirement is currently written in
  mechanism terms — "SHALL start the machinist's solid-node development process
  with a floor callback location". Restate it as the outcome the maker needs: a
  change to the project's model becomes visible without the maker or any agent
  taking an action to make it so. Add a requirement that a rebuild failure is
  reported to the maker while the last complete model remains inspectable.

## Impact

Shop code:

- `floor/` gains the watcher and its wiring; `floor/app.py` loses the callback
  route and gains the failure event; `floor/orchestrator.py` loses token
  minting and callback injection; `floor/__main__.py` loses `--callback-token`.
- `floor/backends/base.py`, `codex.py`, `hermes.py`, `claude.py` lose
  `model_callback_url` and its three prompt blocks.
- `floor/frontend/src/main.tsx` handles the failure event; `floor/static/` is
  rebuilt from it.
- `agents/machinist.md` loses the develop-command paragraph.
- `tests/test_floor_api.py`, `test_floor_entrypoint.py`, `test_orchestrator.py`,
  `test_role_contracts.py` lose their callback coverage and gain watcher
  coverage.

Documentation:

- New `docs/adrs/0010-*`; ADR 0004 marked as amended; `docs/adrs/README.md`
  index extended.
- `docs/architecture-overview.md`: the functional-model boundary section is
  rewritten, and its decision table — currently stopping at 0006 while 0007,
  0008, and 0009 are accepted — is brought current.

Dependencies: the watcher needs a change-detection mechanism. Whether that adds
a dependency to the shop's two (`fastapi`, `uvicorn`) is settled in `design.md`.

Not in scope: the shop cannot yet learn the exact file set backing a model, so
the watcher observes the project's Python sources broadly. Narrowing that needs
a framework capability (`solid sources root`) and is deliberately left to a
later framework change. Framework ADR-033 has since made that set correct
inside the framework and made a rebuild cheap, so a broad watch now costs a few
seconds of background work that publishes nothing — the narrowing is an
optimisation to schedule on evidence, not a gap this cycle leaves open.
