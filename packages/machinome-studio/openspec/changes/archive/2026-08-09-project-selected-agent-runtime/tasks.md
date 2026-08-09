## 1. Verify the one unverified assumption

- [x] 1.1 Confirm against current OpenCode documentation how a model is named on
      `POST /session/{id}/prompt_async` — field name, and whether provider and
      model are two fields or one delimited string. Record the finding in the
      change's evidence before writing `_prompt()`.
- [x] 1.2 Confirm whether OpenCode exposes an enforceable reasoning-level control
      on that call. If it does, record its field and accepted values; if it does
      not, record that and reject the four-segment OpenCode form in 2.1.

## 2. Project runtime selection (red first)

- [x] 2.1 Write failing tests for the grammar: two or three segments for Codex and
      Claude, three or four for OpenCode, the backend in segment one fixing how
      the rest are read, and rejection of unknown backend, wrong segment count,
      empty segment, and an unsupported concrete Codex/Claude model.
- [x] 2.2 Write failing tests for the reasoning level: a trailing segment
      overrides profile effort, an omitted one inherits it, Codex accepts the full
      effort set while Claude accepts only low/medium/high, and a level named for
      a backend that cannot enforce one is rejected.
- [x] 2.3 Write failing tests for defaults: an unnamed agent, an absent
      `[tool.solid-node-studio]` table, an absent `pyproject.toml`, and a project
      that does not exist yet all resolve to Codex with the profile model and
      effort.
- [x] 2.4 Write failing tests for roster resolution: keys outside the active
      roster are ignored and reported, malformed agent keys are rejected, and
      unknown table keys are rejected, including a separate `effort` key.
- [x] 2.5 Implement the reader in `floor/preparation.py`: resolve and
      containment-check the project path, parse `[tool.solid-node-studio]`, and
      return the parsed selections without creating anything. Turn 2.1–2.4 green.

## 3. Profile loader split (red first)

- [x] 3.1 Write failing tests that `load_profile()` validates every declared
      backend table regardless of which backends a run will open, and that an
      OpenCode table in a profile is rejected.
- [x] 3.2 Remove the `backend=` parameter and `RuntimeProfile.backend`; keep
      per-agent tables instead of collapsing to one `BackendRuntime`; delete the
      OpenCode special case at `floor/profiles.py:149-153`. Add `provider` to
      `BackendRuntime`.
- [x] 3.3 Rewrite `tests/test_runtime_profiles.py`, including the TOML mutation
      tests at lines 93-113, against the new loader signature.
- [x] 3.4 Write failing tests for the merge step: a project model overrides the
      profile model, a project reasoning level overrides the profile effort, an
      omitted level inherits it, and tools and permission always come from the
      profile. Implement the merge and turn them green.

## 4. Multi-backend orchestration (red first)

- [x] 4.1 Write a failing test that a profile whose agents select two different
      backends opens each backend exactly once, sends `open_role()` only for the
      agents it owns, and closes each exactly once.
- [x] 4.2 Write a failing test that both backends' event streams are consumed
      concurrently and both roles' messages reach the broker.
- [x] 4.3 Change `ShopOrchestrator` to hold an agent-to-backend mapping; update
      all fourteen `self.backend` call sites in `open`, `deliver`,
      `_recover_and_deliver`, `interrupt`, `close_role`, and `close`.
- [x] 4.4 Call `start()` once per distinct backend and close each distinct
      backend exactly once in `close()`.
- [x] 4.5 Build one `route_events` task per open backend in `_serve` and extend
      `_wait_for_runtime` to wait on the delivery task plus every event task.
- [x] 4.6 Make `--backend-command` a per-backend override in
      `floor/backends/__init__.py` and update the fixture at
      `tests/test_orchestrator.py:584`.
- [x] 4.7 Confirm `backend_failed` still ends the run exactly as it does today;
      add a test pinning that deferred behaviour so a later change to it is
      deliberate.

## 5. OpenCode provider and model

- [x] 5.1 Write a failing test against the fake OpenCode server that a
      project-selected provider and model reach `prompt_async`, and that no model
      is sent when the project selects none.
- [x] 5.2 Implement it in `floor/backends/opencode.py::_prompt()` using the
      format confirmed in 1.1, carrying the reasoning level too if 1.2 found an
      enforceable control.
- [x] 5.3 Amend the supplemental-guidance precedence contract at
      `floor/backends/opencode.py:560-565` to distinguish pilot-authored
      configuration from project guidance text, and assert the new wording in
      `tests/test_opencode_backend.py`.

## 6. Remove the flag

- [x] 6.1 Convert the remaining backend-selecting tests and e2e fixtures
      (`tests/test_orchestrator.py:529,551`, `tests/test_shop_lifecycle_e2e.py`,
      `tests/test_broker.py`, `tests/test_role_contracts.py`,
      `tests/test_opencode_backend.py:217`) to project-declared selection.
- [x] 6.2 Delete `--backend` from `floor/orchestrator.py` and resolve selection
      the same way in `floor/__main__.py:33` and `floor/app.py:119`.
- [x] 6.3 Grep the tree to confirm no `--backend` reference survives in code,
      tests, scripts, or documentation.

## 7. Architecture records

- [x] 7.1 Write an ADR for project-owned per-agent runtime selection: the
      grammar, why selection lives in the project and defaults in the profile,
      why model and reasoning level cross that line while tools and permission do
      not, and the trusted-configuration versus untrusted-guidance boundary.
- [x] 7.2 Write an ADR for multi-backend orchestration: per-agent ownership, one
      instance per distinct backend, event fan-in, and the deferred whole-backend
      failure question.
- [x] 7.3 Amend ADR 0012 to record that OpenCode's compatibility defaults now
      apply only when the project selects no provider and model. Narrow it; do
      not supersede it.
- [x] 7.4 Add both new ADRs to `docs/adrs/README.md` in chronological order with
      correct status fields.

## 8. Documentation

- [x] 8.1 Update `docs/architecture-overview.md`, including the topology diagram
      at line 37 and the backend-configuration text at lines 119 and 126.
- [x] 8.2 Update `README.md:12-14` and `skills/running-the-shop/SKILL.md`
      (lines 24, 40, 46 and the skill description) to describe project-declared
      selection and the removed flag.
- [x] 8.3 Document the `[tool.solid-node-studio]` table where a maker will look
      for it, with a worked mixed-backend example.

## 9. Completion

- [x] 9.1 Run the full suite; report any structural blind spot or environmental
      failure honestly rather than reporting a clean pass.
- [x] 9.2 Open a floor for a real project with a mixed-backend selection and
      confirm both backends open, deliver, and close cleanly.
- [x] 9.3 Sync baseline specs, archive the change, and commit the completed
      implementation record.
