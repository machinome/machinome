## 1. Canonical screenshot pipeline

- [ ] 1.1 Add red-first unit tests for the fixed 640x360 rendering invocation,
  first creation, byte-identical no-op, atomic changed-image replacement,
  renderer/output failure, preservation of a prior image, and refusal to follow
  a project-root `screenshot.png` symlink; record the expected red failures.
- [x] 1.2 Implement the shared project screenshot helper using the selected
  Machinome executable, an outside-project temporary output, PNG validation,
  byte comparison, and atomic replacement, with screenshot errors represented
  separately from build or Git errors.
- [ ] 1.3 Add serialization/coalescing coverage for overlapping requests and
  implement per-project ordering so an older render cannot replace the result
  of a newer refresh request.

## 2. Build and bootstrap integration

- [x] 2.1 Add red-first preparation tests that a successful initial build and
  screenshot put `screenshot.png` in the initial commit, while screenshot
  failure alone still permits the scaffold commit and session preparation.
- [ ] 2.2 Add red-first watcher and scoped-build tests that successful
  source-triggered builds, successful `solid_build` calls, and externally
  published `viewer.json` request screenshot refreshes, while failed builds do
  not replace the prior image or change their existing result semantics.
- [x] 2.3 Wire the shared helper into project preparation, source-triggered
  build completion, the scoped `solid_build` tool, and external successful
  publication observation; keep every screenshot failure best-effort and
  supplemental.

## 3. Best-effort Git injection

- [ ] 3.1 Add red-first scoped-tool tests that `git_commit` refreshes and stages
  a changed regular `screenshot.png`, manufactures no diff for identical bytes,
  and still invokes and returns the Git commit result after rendering,
  publication, unsafe-path, or staging failure.
- [x] 3.2 Implement commit-time best-effort refresh and exact-path staging
  without unstaging, deleting, restoring, or substituting another path, and
  expose any screenshot problem only as supplemental warning information.
- [ ] 3.3 Update Builder, Designer, and Machinist runtime contracts and their
  contract tests so the root `screenshot.png` is recognized as a shop-managed
  injected commit artifact while arbitrary engineering snapshots remain
  uncommitted scratch.

## 4. Hub inventory, serving, and live refresh

- [x] 4.1 Add red-first inventory and API tests for screenshot
  availability/content revision, an exact closed-project image route,
  missing/unreadable fallback, repository-boundary enforcement, and symlink
  refusal.
- [ ] 4.2 Add red-first hub-stream tests that changed screenshot bytes publish
  one project-metadata revision update, identical bytes publish none, no
  conversation or agent state leaks into the hub, and reconnect snapshots carry
  the current revision.
- [x] 4.3 Implement screenshot metadata, the exact screenshot route, and
  hub-scoped revision publication without weakening project repository checks
  or the `_build` artifact boundary.
- [ ] 4.4 Add browser acceptance coverage and implement accessible,
  contain-fitted, revision-cache-busted project-card images with the existing
  striped placeholder on absent or failed images; rebuild the checked-in
  frontend bundle.

## 5. Architecture and reference documentation

- [x] 5.1 Draft and accept an ADR recording the root `screenshot.png`
  convention, fixed best-effort rendering, floor-mediated commit injection,
  closed-project serving boundary, and explicit priority of builds and commits
  over image success.
- [x] 5.2 Update the architecture overview and ADR index to reflect the
  accepted boundary and the hub's screenshot metadata changes.
- [x] 5.3 Update the reference design to replace its pending-thumbnail note
  with the canonical screenshot, sizing, accessibility, and placeholder
  behavior.

## 6. Validation and completion

- [x] 6.1 Run focused screenshot, preparation, watcher, scoped-tool, API,
  stream, role-contract, and browser tests; preserve red-first evidence and
  report structural blind spots or environmental renderer failures honestly.
- [ ] 6.2 Run the complete shop test suite, frontend build, browser acceptance
  suite, and strict OpenSpec validation.
- [ ] 6.3 Manually build and commit a scratch project through the floor, verify
  its root `screenshot.png` is committed and shown on the hub, then force a
  screenshot failure and verify the next important commit still succeeds.
- [ ] 6.4 Sync the completed delta specifications into the baseline specs,
  archive the change, and commit the completed implementation record.
