## 1. Prove the current gap red

- [x] 1.1 Add a test that a model source change refreshes the maker's view with no callback and no agent action, and observe it fail against the current code
- [x] 1.2 Add a test that a failed rebuild reports the failure while the previous model stays inspectable, and observe it fail
- [x] 1.3 Add a test that a rebuild leaving the published snapshot unchanged publishes no model change, and observe it fail
- [x] 1.4 Extend `tests/fixtures/fake_solid.py` so a build can be made to fail on demand, to change the published snapshot, and to leave it identical — the three states the tests above need

## 2. Build the watcher

- [x] 2.1 Add `floor/watcher.py`: poll `*.py` under the project root, excluding `.git`, `__pycache__`, `.venv`, and the whole `_build` family (symlink, `_build.*` versions, `.solid-node-build-*` staging)
- [x] 2.2 Require a fingerprint stable across two consecutive polls before rebuilding (D3), and coalesce changes arriving during a build into one follow-up rebuild (D5)
- [x] 2.3 Run `solid build root` through `asyncio.create_subprocess_exec` from the project directory with the same environment `floor/preparation.py` uses; extract that shared invocation rather than duplicating it
- [x] 2.4 Publish `model_changed` only when the `viewer.json` content hash differs from the last published one, seeded from the snapshot preparation validated (D4)
- [x] 2.5 Publish `model_build_failed` with bounded captured stderr on a non-zero build exit and `model_build_succeeded` on the next success, without conflating recovery with artifact change (D6)
- [x] 2.6 Log each rebuild with its trigger file and duration, so the wasted-rebuild rate and build latency are collectible evidence rather than anecdote

## 3. Wire it into the floor

- [x] 3.1 Give `create_app` the project root and solid command, and start/stop the watcher from the application lifespan; run it only when a solid command is supplied (D1)
- [x] 3.2 Pass the solid command from `floor/__main__.py` and `floor/orchestrator.py`
- [x] 3.3 Summarise `model_build_failed` in the broker's event log alongside `model_changed`
- [x] 3.4 Handle build outcome events in `floor/frontend/src/main.tsx`: show failure text while keeping the last model rendered, clear it on `model_build_succeeded`, and refresh artifacts only on `model_changed`; rebuild `floor/static/`

## 4. Remove the callback seam

- [x] 4.1 Delete the `POST /api/runs/{run_id}/model/ready/{token}` route and `create_app`'s `callback_token` parameter
- [x] 4.2 Delete `--callback-token` from `floor/__main__.py`
- [x] 4.3 Delete token minting and callback URL injection from `floor/orchestrator.py`
- [x] 4.4 Delete `model_callback_url` from `RoleContext` and from the codex, hermes, and claude backends, including all three develop-command prompt blocks
- [x] 4.5 Remove the machinist role card's process-management paragraph, leaving the acknowledge/report/complete lifecycle intact
- [x] 4.6 Remove callback coverage from `tests/test_floor_api.py`, `test_floor_entrypoint.py`, `test_orchestrator.py`, and `test_role_contracts.py`

## 5. Evidence

- [x] 5.1 Run the full Python suite green
- [x] 5.2 Run the frontend TypeScript check
- [x] 5.3 Run `scripts/test-e2e`
- [x] 5.4 Exercise a real floor by hand: edit a project model file, confirm the browser refreshes with no agent running; break it, confirm the failure is shown and the previous model still renders; fix it, confirm recovery
- [x] 5.5 Measure and report repeat incremental build latency and the rebuild count caused by non-model `.py` edits, against the figures `design.md` records from ADR-033 — and confirm that a non-model edit rebuilds without publishing `model_changed`, which is what makes the broad watch acceptable

## 6. Records

- [x] 6.1 Write ADR 0010 for the shop-owned watcher, superseding ADR 0004's callback mechanism while reaffirming its artifact boundary; mark ADR 0004 accordingly
- [x] 6.2 Add ADR 0010 to `docs/adrs/README.md`
- [x] 6.3 Rewrite the functional-model boundary section of `docs/architecture-overview.md`, and bring its decision table current — it stops at 0006 while 0007, 0008, and 0009 are accepted
- [x] 6.4 Sync the baseline spec and archive the change
