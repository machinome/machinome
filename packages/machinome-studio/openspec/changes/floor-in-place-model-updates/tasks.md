## 1. Make the suite able to express the defect

- [ ] 1.1 Upgrade the fake widget in `tests/fixtures/fake_solid.py` to the
  interface F3 published: report `apiVersion` 2, fetch every model path the
  snapshot names against `options.baseUrl` on mount, and expose
  `artifactChanged(path)`, `manifestChanged()` and `reload()` that fetch what
  their contract says they fetch and nothing else. Default the reported
  `viewer_api_version` to 2.
- [ ] 1.2 Have the fake widget record its own history on the page — mount
  count, every URL it fetched, and every update call with its argument — so a
  test can assert what the browser asked for rather than what it rendered.
- [ ] 1.3 Give the fake widget a way to fail a fetch on demand (state-file or
  query-driven), so an induced artifact failure is reproducible without racing
  a real one.
- [ ] 1.4 Confirm the upgraded fixture is honest: with today's `main.tsx` the
  new fixture must show a fresh mount per change. If it does not, the fixture
  is not observing the defect and 1.1-1.3 are not done.

## 2. Prove the defects red

- [ ] 2.1 Add an e2e test asserting the model canvas keeps its DOM identity
  across a rebuild that republishes one artifact. Confirm it is red against
  the current remount-per-generation code. (PRD acceptance 2)
- [ ] 2.2 Add an e2e test asserting that a one-artifact change produces exactly
  one artifact fetch — the artifact named — and no document refetch of the
  parts it did not name. Confirm red. (PRD acceptance 1)
- [ ] 2.3 Add an e2e test that induces an artifact fetch failure, then
  publishes again, and asserts the model is still displayed throughout and the
  second publication is applied with no page reload. Confirm it is red for the
  right reason — the current code drops the second event because its host is
  unmounted, so assert the *second* update, not just the error text. (PRD
  acceptance 3, Defect A)
- [ ] 2.4 Add an e2e test asserting a document-only change — placement or
  colour, no model bytes moved — updates the display with no model fetch.
  Confirm red. (PRD acceptance 6)
- [ ] 2.5 Add an e2e test asserting that removing a node from the document
  updates the model with no request for the removed artifact. Confirm red or
  record why it already passes. (PRD acceptance 7)

## 3. Update in place

- [ ] 3.1 Rewrite `FunctionalModel` in `floor/frontend/src/main.tsx` to mount
  once: an effect with no dependencies, the handle in a ref beside the existing
  `view` ref, disposal only on unmount, and the `disposed`/`cleanup` race guard
  kept as it is. (design D1)
- [ ] 3.2 Render the host `<div>` unconditionally and the error paragraph
  beside it, never instead of it. (design D2)
- [ ] 3.3 Route each `model_artifact_changed` event to one of three actions —
  `viewer.json` to `manifestChanged()`, `errors.json` to the existing banner
  fetch, anything else to `artifactChanged(path)` with the path verbatim.
  (design D3)
- [ ] 3.4 Report a rejected update in the error paragraph and clear it on the
  next update that succeeds; leave `model_build_unavailable` and the
  `errors.json` banner exactly as S1 left them. (design D4)
- [ ] 3.5 Replace the lifecycle-reconnect generation bump with
  `manifestChanged()` on the mounted handle. (design D5)
- [ ] 3.6 Delete `modelGeneration`, the `generation` prop, and the
  `?generation=N` query now that nothing consumes them.
- [ ] 3.7 Adjust `floor/frontend/src/styles.css` so the error paragraph and a
  live model coexist in the viewport without the model losing its space.

## 4. Serve what the browser now refetches

- [ ] 4.1 Add a test that a republished artifact is served with revalidation
  required — the artifact route sets `Cache-Control: no-cache` — and confirm
  it is red. (design D7)
- [ ] 4.2 Set that header on the artifact route in `floor/app.py`, leaving the
  fixed-build-root resolution S1 introduced untouched.

## 5. Require a viewer that can do this

- [ ] 5.1 Add a test that preparation fails, with the existing message naming
  both versions, when the installed viewer reports API 1. Confirm red.
- [ ] 5.2 Raise `REQUIRED_VIEWER_API` to 2 in `floor/preparation.py`.
- [ ] 5.3 Bring `floor/frontend/src/solid-node-widget.d.ts` level with the
  framework surface: `artifactChanged`, `manifestChanged`, `reload`, and
  `SOLID_NODE_VIEWER_API_VERSION: 2`. Verify with
  `npm --prefix floor/frontend test`, which typechecks the frontend.

## 6. Verify against the real thing

- [ ] 6.1 Run the shop suite green: `pytest tests` and
  `npm --prefix floor/frontend run build`.
- [ ] 6.2 Live check against the linked framework `sprint-003` checkout, not
  installed `solid_node` — the S1 record shows that distinction mattering.
  Open a shop on a scaffolded multi-part project, edit one leaf, and confirm
  from the browser that the canvas element is identical before and after, one
  artifact was fetched, and the camera did not move.
- [ ] 6.3 Live check the failure path: break the model source, confirm the
  banner appears while the previously published parts stay rendered, fix the
  source, and confirm the model updates and the banner clears with no reload.
- [ ] 6.4 Live check that a publication from outside the shop — `solid build`
  in a terminal — reaches the browser as an in-place update, which is the
  behaviour S1's event source exists to make possible.
- [ ] 6.5 Live check on `projects/v8-engine` that repeated one-leaf edits do
  not grow the page's memory across updates, the risk a long-lived handle
  carries.
- [ ] 6.6 Confirm the floor still imports, executes and serves no project
  Python. (PRD acceptance 8)

## 7. Records

- [ ] 7.1 Amend `docs/adrs/0013-observe-atomic-build-publications.md`: replace
  its recorded S1 bridge paragraph with the targeted update that discharges it,
  and record the artifact-path mapping and the cache-revalidation consequence.
  (design D8)
- [ ] 7.2 Sync the delta spec into
  `openspec/specs/functional-model-inspection/spec.md`, carrying every ADDED
  and MODIFIED requirement whole.
- [ ] 7.3 Run `openspec validate --all --strict`.
- [ ] 7.4 Archive the change through OpenSpec and record the cycle's
  integration evidence in `docs/product/sprints/current.md`.
