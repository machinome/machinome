# SPRINT-003: The model changes as it is made

## Goal

The maker watches a model take shape: a part that finishes rebuilding appears,
the rest of the model and the camera stay put, nothing reloads or goes stale,
and the view never wedges — whoever caused the change.

## Source

`docs/product/sprints/PRD.md` is the source for this sprint. Every story,
cycle, OpenSpec proposal, architecture record, and acceptance test derives from
it. Read it before opening any cycle. This record carries execution identity and
evidence only; product content, decisions, and their rejected alternatives live
in the PRD.

## Stories

- [ ] STORY-007 - See the model change as it is made
  - Source: `docs/product/stories/STORY-007-see-the-model-change-as-it-is-made.md`
  - Derived from: `docs/product/sprints/PRD.md`

## Ratified scope

- Included: build mutual exclusion in the framework; per-artifact atomic
  publication into a single build directory with manifest-last ordering, orphan
  sweeping, and error-file clearing; a viewer interface for targeted artifact
  and manifest updates; the floor watching source as a build trigger and build
  output as its event source; the floor forwarding content events only; the
  shop browser updating the model in place.
- Excluded: content-addressed artifact filenames; any change to what the viewer
  can render; remote or multi-client floors; retiring `solid develop`; the shop
  workspace redesign already on `main`.

## Repositories

- `solid-node-shop`
  - Source: `main` @ `7397c71`
  - Sprint branch: `sprint-003`
  - Content: `7397c71`
  - Worktree: `WTs/sprint-003`
- `solid-node`
  - Source: `main` @ `acf4292`
  - Sprint branch: `sprint-003`
  - Content: `582da89`
  - Worktree: `solid-node/WTs/sprint-003`
  - Shop link: `WTs/sprint-003/solid-node`

## Cycles

- `solid-node` / `build-mutual-exclusion`
  - Intent: one builder at a time per project, with a dedup rule that lets a
    builder trust a publication already covering its change; PRD D2, ADR plan
    section 5
  - Story: `STORY-007`
  - Requires: none
  - Branch: `sprint-003-build-mutual-exclusion` from `acf4292`
  - Worktree: removed after integration
  - Commits: `7fb9e68` planning, `a89cc56` implementation and archive
  - Archive: `openspec/changes/archive/2026-08-02-build-mutual-exclusion`
  - Integrated: `sprint-003` @ `a89cc56`
- `solid-node` / `per-file-build-publication`
  - Intent: a single `_build` directory written one artifact at a time by
    atomic rename, manifest last, orphans swept, error file cleared; PRD D1,
    D7, section 3.2
  - Story: `STORY-007`
  - Requires: `solid-node` / `build-mutual-exclusion`
  - Branch: `sprint-003-per-file-build-publication`, rebased from `a89cc56`
    onto `f34ddc6` after F3 integrated first
  - Worktree: torn down
  - Commits: `b994c4a`, `582da89`
  - Archive: `openspec/changes/archive/2026-08-02-per-file-build-publication/`
  - Integrated: `sprint-003` @ `582da89`
- `solid-node` / `viewer-targeted-update`
  - Intent: the viewer handle accepts an artifact change and a manifest change
    and updates only what they name; consumed by the development loop as well;
    PRD D5, D6
  - Story: `STORY-007`
  - Requires: none
  - Branch: `sprint-003-viewer-targeted-update` from `a89cc56`
  - Worktree: torn down
  - Commits: `57521bf`, `f34ddc6`
  - Archive: `openspec/changes/archive/2026-08-02-viewer-targeted-update/`
  - Integrated: `sprint-003` @ `f34ddc6`
- `solid-node-shop` / `floor-artifact-event-pipeline`
  - Intent: two watchers with distinct jobs, an artifact route with no symlink
    to re-resolve, and SSE carrying the artifact path and nothing else; PRD
    D3, D4, section 3.3
  - Story: `STORY-007`
  - Requires: `solid-node` / `per-file-build-publication`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `floor-in-place-model-updates`
  - Intent: the browser updates the model in place through the framework
    viewer, answering PRD defects A and B by construction; PRD section 6
  - Story: `STORY-007`
  - Requires: `solid-node` / `viewer-targeted-update`,
    `solid-node-shop` / `floor-artifact-event-pipeline`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending

## Paired validation

- Setup verified 2026-08-02. Shop worktree `WTs/sprint-003` on `sprint-003` at
  the ratification commit, clean. Framework worktree
  `solid-node/WTs/sprint-003` created by `scripts/dev-env sprint-003 setup` on
  `sprint-003` at base `acf4292`, slot 1, backend 8001 / frontend 3001, clean
  apart from ignored bench links. `WTs/sprint-003/solid-node` resolves to the
  registered framework sprint worktree.
- Combined validation passed 2026-08-02 for shop content `7397c71` and
  framework content `a89cc56`, run from `WTs/sprint-003` against its linked
  `solid-node` checkout: shop `pytest tests` 144 passed with 25 subtests,
  `tests/dev-env-test.sh` all passed, framework `pytest tests` 394 passed with
  5 subtests, `openspec validate --all --strict` 13 specs.
- F1 opened 2026-08-02. `scripts/dev-env sprint-003-build-mutual-exclusion
  setup --base sprint-003` created branch `sprint-003-build-mutual-exclusion`
  at base `acf4292`, equal to the framework `sprint-003` head, slot 3, backend
  8003 / frontend 3003, clean apart from ignored bench links.
- F2 integrated 2026-08-02 by fast-forwarding framework `sprint-003` from
  `f34ddc6` to `582da89`. The cycle was not ready as first handed over and was
  repaired before integration: it was rebased onto the advanced sprint head;
  its ADR renumbered to ADR-038 because F3's ADR-037 landed first; its spec
  sync completed, which had dropped both REMOVED requirements and all three
  ADDED ones and paraphrased the MODIFIED ones; its 20 tasks verified and
  checked off; and the change archived, restoring the two-commit shape.
  Eleven lifecycle tests it had deleted -- including F1's guards against the
  develop-loop respawn and against a superseded build publishing -- were
  restored and adapted, each confirmed red by removing the behaviour it
  guards. Three tasks had no test at all; those were written.
  One further defect was found only by exercising a real project: with the
  candidate directory gone, a render lands at the artifact's final path, so
  the following pass found every artifact current and never rewrote
  `viewer.json`. Artifacts advanced while the document naming them stayed a
  build behind, which would have silently defeated F3 and S2. The builder now
  republishes the manifest when it no longer matches the model, guarded by a
  unit test and by an assertion added to the real-OpenSCAD end-to-end test.
  Evidence: framework `pytest tests` 395 passed with 5 subtests, `openspec
  validate --all --strict` 13 specs. Live on a scaffolded three-file project:
  a one-leaf edit rewrote only that leaf's artifact, the untouched leaf kept
  its inode and mtime, and the document followed the edit; `solid test`,
  `solid build` and `solid develop` interleaved under the F1 lock with exit 0
  throughout, no leftover temporaries or locks. Combined validation passed for
  shop content `7397c71` and framework content `582da89`: shop `pytest tests`
  144 passed with 25 subtests, `tests/dev-env-test.sh` all passed. Cycle
  worktree torn down; the branch is retained.
- F3 integrated 2026-08-02 by fast-forwarding framework `sprint-003` from
  `a89cc56` to `f34ddc6`, after verifying the cycle still descended from that
  head. Evidence: framework `pytest tests` 395 passed with 5 subtests, widget
  vitest 29 passed, `npm run typecheck` clean, web app `react-scripts test` 12
  passed, `openspec validate --all --strict` 13 specs, ADR-037 accepted. Live
  check on a scaffolded three-file project: editing one leaf source refetched
  only that leaf's artifact, left the unedited hub artifact alone, and kept the
  canvas element identical. Combined validation passed for shop content
  `7397c71` and framework content `f34ddc6`: shop `pytest tests` 144 passed
  with 25 subtests, `tests/dev-env-test.sh` all passed. Cycle worktree torn
  down with `scripts/dev-env sprint-003-viewer-targeted-update teardown`; the
  branch is retained. F2 branches from `a89cc56` and must be rechecked against
  `f34ddc6` before its fast-forward.
- F1 integrated 2026-08-02 by fast-forwarding framework `sprint-003` from
  `acf4292` to `a89cc56`. Cycle worktree torn down with `scripts/dev-env
  sprint-003-build-mutual-exclusion teardown`; the branch is retained. No shop
  content changed, so shop content remains `7397c71`.
- F2 opened 2026-08-02. `scripts/dev-env sprint-003-per-file-build-publication
  setup --base sprint-003` created branch `sprint-003-per-file-build-publication`
  at base `a89cc56`, equal to the framework `sprint-003` head after F1, slot 3.
  Its recorded dependency on F1 is satisfied.
- F3 opened 2026-08-02. `scripts/dev-env sprint-003-viewer-targeted-update setup
  --base sprint-003` created branch `sprint-003-viewer-targeted-update` at base
  `a89cc56`, slot 4. It has no dependencies and runs in parallel with F2; both
  branch from the same framework head, so whichever integrates second must be
  rechecked against the advanced sprint branch before its fast-forward.

## Decisions and scope changes

- 2026-08-02 - Adopt a PRD as this sprint's source document, replacing the
  brief used by SPRINT-002. Everything in the sprint derives from it, and this
  record carries execution identity and evidence only.
- 2026-08-02 - Supersede the `make-shop-floor-event-driven` worktree rather
  than rewrite it. Its specs describe a source-watching, floor-building,
  full-reload design this sprint rejects, and all three of its fix commits
  edited `floor/watcher.py`, where neither measured defect lives. Its diagnosis
  is preserved in PRD section 2; its branch and worktree are retained until the
  pilot directs otherwise.
- 2026-08-02 - Order `build-mutual-exclusion` before
  `per-file-build-publication`. Under set-atomic publication a build race
  caused a lost update; under a single directory two builders write the same
  files and interleave, so the race becomes corrupting rather than merely
  wasteful.
- 2026-08-02 - File three architecture records rather than two: one per
  framework subsystem the work decides (BUILD, VIEWER-WEB) and one for the
  shop. The framework files ADRs by subsystem, the viewer interface serves the
  development loop independently of the shop, and a shop record cannot decide a
  framework interface.

## Outcome

Completed when the sprint is archived.
