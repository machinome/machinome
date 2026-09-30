## 0. Preconditions

- [x] 0.1 Base: branch `pose-repaints` from `fix-warts` at `e30b05f`.
- [x] 0.2 Measure before any change (proposal, `evidence.md`): the fixture
  tour's capture loop at its output size, a pose's phases in the page
  (`flushSync` commit, views, picture decodes, repaint, measure) and in
  Node (`pose()`, screenshot), the compositions' repaints, and a probe of
  the rule's decision in the unchanged page. The instrumentation lives in a
  scratch harness and temporary lines of `stage/runtime.tsx`, removed before
  every commit.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the rule (D1), where it is decided (D2), how it is
  observed (D3).

## 1. The rule (red first)

- [x] 1.1 Red: in `test/browser/stage.test.mjs`, a test counting the
  animation frames a pose requests (a wrapped `requestAnimationFrame`): the
  same frame posed again requests none; a frame of `holds` (the view alone)
  posed at another instant requests none; a frame of `rise` whose title
  changes its words requests some; posing that frame A, then B with the
  other words, then A gives identical pixels for A, and B differs. Run it
  cold and record the failure.
- [x] 1.2 `stage/runtime.tsx`: `poseViews` reports whether a view was
  mounted, placed again or resized; `repaint` records the page's content;
  `setFrame` repaints only when D1 says so. The runtime's comments and the
  comment of `show()` in `src/render.mjs` say the rule.
- [x] 1.3 Show the pixel half of the new test is not vacuous, or record that
  it is: run it against a mutation that never repaints a pose, and record
  what fails.

## 2. Proof

- [x] 2.1 The browser and pipeline projects cold, five times, on the final
  content (`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow`); every
  summary quoted; one failure in five is a failure of the rule.
- [x] 2.2 The whole Node suite (`npm test`) and the Python suite on the
  final content, summaries quoted.
- [x] 2.3 Measure after, by the same harness on the same machine: frames a
  second, the loop's time, the repaints, and the command line's render of
  the tour at its output size.

## 3. Records

- [x] 3.1 ADR-004 amended in place with a dated section: a pose waits for
  what can change the picture, and for nothing else.
- [x] 3.2 `docs/stage.md` where it says the stage repaints;
  `docs/movie-document.md` left as it is (it does not say every pose
  repaints); `docs/architecture-overview.md` left as it is (it does not
  describe the repaint).
- [x] 3.3 `CHANGELOG.md` under `Unreleased`, with the measured numbers.
- [x] 3.4 Sync the baseline specs and archive the change with the CLI;
  `evidence.md` in the archived change.

Implementation note (30 September 2026): 0.3 is left open: the planning
commit was made for the orchestrator's review before implementation, and
that review, the campaign's gate, is not claimed here. 1.3 found the pixel
half of the new test vacuous against a stage that never repaints a pose
(`evidence.md`, finding 1); the frame count is what pins the rule. 4.1 is
owed.

## 4. Owed, not claimed by automation

- [ ] 4.1 After the merge, the orchestrator re-renders *Cut and Advance*
  with the real viewer and compares its 638 s.
