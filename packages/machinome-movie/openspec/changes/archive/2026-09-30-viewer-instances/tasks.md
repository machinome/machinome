## 0. Preconditions

- [x] 0.1 Base: branch `viewer-instances` from `fix-warts` at `8d6c842`,
  with `pose-repaints`, `narration-end-anchor`, `speech-key-lookup` and
  `fixture-hygiene` merged.
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the lease (D1), the state carried by the instance (D2),
  the lens rule below API 28 (D3), what `window.film` reports (D4).

## 1. The lease (red first)

- [x] 1.1 Red, layer 5: in `test/browser/stage.test.mjs`, with the
  late-canvas double, a view that leaves frees its instance and one that
  returns is drawn on it: the probe's instance serves `balance.mill` with a
  standing highlight and `ground` hidden, then `opening.wide` with no
  highlight and nothing hidden (the restore runs, `ground` is shown again,
  the canvas fills the new box), then `balance.mill` again; one instance
  mounts, `views()` lists one, A's pixels are identical before and after,
  and B's pixels equal B's in a session where B is posed first. Then the
  split: A-only, B-only and a frame placing A and B side by side, posed in
  each of the six orders in its own session: two instances mount in every
  order, and each frame's pixels are the same in all six. Run cold and
  record the failures.
- [x] 1.2 Red, layer 4: in `stage/stage.test.tsx`, `leaseViews` keeps a
  placed view's instance, leases the lowest free one, mounts only when none
  is free, never exceeds the largest frame's count over every sequence of
  five frames drawn from A, B, A and B, and none, and leases an instance
  with a recorded lens only to that lens. Record the failure.
- [x] 1.3 `stage/runtime.tsx`: `leaseViews`; `poseViews` releases, keeps and
  leases by it, mounting only for a view without one; the instance's key
  changes with the lease and its `hidden`, `applied`, `restore` and `size`
  stay; `views()`, `project()` and `clearComposition` read the instances.
  The existing tests that counted one mount per view element are updated to
  the lease (the probe's instance is leased on).
- [x] 1.4 Show the new browser tests are not vacuous: run them against a
  mutation that resets an instance's diffs at a lease without restoring
  (the standing highlight left on), and one that mounts per view element
  as before; record what fails.

## 2. Proof

- [x] 2.1 The slow project cold three times on the final content
  (`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow`): every preview
  proof (pixel replay, A-B-A, the transitions) and incremental rendering's
  "every incremental PNG equals a separately cold film" hold; summaries
  quoted.
- [x] 2.2 The whole Node suite (`npm test`) and the Python suite on the
  final content, summaries quoted.

## 3. Records

- [x] 3.1 ADR-007 (STAGE): viewer instances are leased to view elements per
  frame; indexed in `docs/adrs/README.md`; ADR-004's decision 3 points to
  it in a dated amendment.
- [x] 3.2 The three contract sentences: `docs/stage.md` (the `view` row),
  `docs/movie-document.md` (the stage section's last item, and `views()`
  where it lists the instances' keys), and the `react-stage` requirement
  through the spec delta; `docs/architecture-overview.md` where it states
  the rule; the runtime's comments.
- [x] 3.3 `CHANGELOG.md` under `Unreleased`.
- [x] 3.4 Sync the baseline specs and archive the change with the CLI;
  `evidence.md` in the archived change, with the count *Cut and Advance*
  will mount under the rule.

Implementation note (30 September 2026): 0.2 is left open: the planning
commit was made for the orchestrator's review before implementation, and
that review, the campaign's gate, is not claimed here. 1.4's second mutation
was run as a lease that never takes a free instance (a view mounts whenever
it held none at the frame before), which the unchanged runtime's red (one
mount per view element) already covers; a third mutation, the lens ignored,
was run at layer 4 (`evidence.md`). 4.1 is owed.

## 4. Owed, not claimed by automation

- [ ] 4.1 After the merge, the orchestrator measures the memory of
  *Cut and Advance* with the real viewer.
