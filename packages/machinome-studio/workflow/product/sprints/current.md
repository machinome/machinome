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
  - Content: `5e2c56a`
  - Worktree: `WTs/sprint-003`
- `solid-node`
  - Source: `main` @ `acf4292`
  - Sprint branch: `sprint-003`
  - Content: `b9279ea`
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
- `solid-node-shop` / `reliable-live-model-event-delivery`
  - Intent: an already-open browser receives every published model manifest
    after its initial run snapshot, so an assembly-to-fusion change appears
    without a manual reload; regression from the Snowman floor validation.
  - Story: `STORY-007`
  - Requires: `solid-node-shop` / `floor-artifact-event-pipeline`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `floor-artifact-event-pipeline`
  - Intent: two watchers with distinct jobs, an artifact route with no symlink
    to re-resolve, and SSE carrying the artifact path and nothing else; PRD
    D3, D4, section 3.3
  - Story: `STORY-007`
  - Requires: `solid-node` / `per-file-build-publication`
  - Branch: `sprint-003-floor-artifact-event-pipeline` from `30ac154`
  - Worktree: `WTs/sprint-003-floor-artifact-event-pipeline`
  - Commits: `534b50b` planning, `6817520` implementation and archive
  - Archive: `openspec/changes/archive/2026-08-02-floor-artifact-event-pipeline/`
  - Integrated: `sprint-003` @ `6817520`
- `solid-node-shop` / `floor-in-place-model-updates`
  - Intent: the browser updates the model in place through the framework
    viewer, answering PRD defects A and B by construction; PRD section 6
  - Story: `STORY-007`
  - Requires: `solid-node` / `viewer-targeted-update`,
    `solid-node-shop` / `floor-artifact-event-pipeline`
  - Branch: `sprint-003-floor-in-place-model-updates` from `659f5fa`
  - Worktree: `WTs/sprint-003-floor-in-place-model-updates`
  - Commits: `c06cc78` planning, `5e2c56a` implementation and archive
  - Archive: `openspec/changes/archive/2026-08-03-floor-in-place-model-updates/`
  - Integrated: `sprint-003` @ `5e2c56a`

## Paired validation

- The double-fetch finding S2 recorded is fixed 2026-08-03, on explicit pilot
  direction, as a direct framework commit rather than a full F-cycle --
  `db59935` on `main` is the precedent for a bounded framework fix committed
  without a proposal cycle. Framework `sprint-003` advances from `582da89` to
  `b9279ea`: a `WidgetTree` node now remembers that `artifactChanged()`
  supplied its current geometry, and the `manifestChanged()` that immediately
  follows trusts it instead of comparing `mtime`, consuming the memory either
  way so a later genuine change is still detected. Added as a scenario to
  `viewer-package`'s geometry-identity requirement rather than a proposal
  directory. Reproduced red with a `tree.test.ts` case before the fix and
  green after; framework `pytest tests` 395 passed with 5 subtests;
  `openspec validate --all --strict` 13 specs. ADR 0013's recorded finding is
  updated to record the fix rather than the open question.
  Re-verified live against the rebuilt widget bundle on the same scaffolded
  project: one edit now produces exactly one geometry fetch, where it
  previously produced two. Combined validation re-run from `WTs/sprint-003`
  against the advanced framework content: shop `pytest tests` 151 passed, 1
  skipped, 24 subtests; `tests/dev-env-test.sh` all passed; `openspec validate
  --all --strict` 13 specs. The cycle worktree `WTs/sprint-003-floor-in-place-model-updates`,
  whose framework link tracks the same branch, was re-run in full against the
  fixed bundle: 13/13 `test_shop_lifecycle_e2e.py` passed, including the
  development-bundle guard that needs `node_modules`.
- S2 integrated 2026-08-03 by fast-forwarding shop `sprint-003` from
  `659f5fa` to `5e2c56a`, after rechecking that the cycle still descended from
  that head. Combined validation passed from `WTs/sprint-003` against its
  linked framework checkout at content `582da89`: shop `pytest tests` 151
  passed, 1 skipped, 24 subtests; `tests/dev-env-test.sh` all passed;
  `openspec validate --all --strict` 13 specs; framework `pytest tests` 395
  passed with 5 subtests. The one skip is
  `test_a_development_build_mounts_the_viewer_exactly_once`, which needs
  `floor/frontend/node_modules` to build the development bundle and is absent
  from an integration worktree by design; it ran and passed in the cycle
  worktree, where the same commit is under test with those dependencies
  present. Every cycle in this sprint is now integrated.

- S2 reviewed and repaired 2026-08-03 before integration. The handover was
  green on 151 shop tests and still shipped a defect no test here could see.
  Its mount effect guarded re-entry with a ref shared across effect instances,
  so React's StrictMode remount -- which tears the effect down and re-runs it
  synchronously -- skipped the second mount while the first disposed itself and
  left no viewer at all. The shipped bundle is a production build, where each
  effect runs once, so every existing assertion passed. Reproduced by building
  the same source in development mode and rerunning the suite against it: four
  e2e tests failed on a canvas that never appeared, and the same experiment on
  `659f5fa` passed, establishing it as S2's regression rather than a
  pre-existing one. Mounts, updates and disposal now share one queue, so a
  torn-down mount resolves before the next attempt instead of blocking it.
  `STATIC_ROOT` honours `SHOP_FLOOR_STATIC_ROOT` so the new
  `test_a_development_build_mounts_the_viewer_exactly_once` can drive the
  maker's browser against a development bundle; it was confirmed red against
  the handed-over code.
- S2 live-checked 2026-08-03 against framework `sprint-003` content `582da89`,
  reached through `PYTHONPATH` and a `--solid-command` wrapper rather than the
  installed `solid_node`, which resolves to framework `main` -- the distinction
  the S1 record had to correct. On a scaffolded two-leaf project with the real
  `solid` CLI and the real widget bundle rebuilt from that worktree: editing
  one leaf preserved the canvas element and the orbited camera, fetched only
  that leaf's STL and never the untouched leaf's, and changed the render; a
  broken source showed the failure banner while the published model stayed
  rendered, and fixing it cleared the banner and updated the model with no
  reload; a `solid build` run from a terminal outside the shop reached the
  browser as an in-place update; and eight consecutive edits held the page heap
  at 4.56 MB -> 4.77 MB, flat after the third, with one canvas throughout,
  measured through CDP because `performance.memory` is quantised.
- S2 finding, measured not fixed: one edit costs two fetches of the changed
  artifact. The framework publishes the artifact and then the manifest, so the
  floor forwards two events as D3 decides; `artifactChanged()` replaces the
  mesh without recording the new `mtime`, so the following `manifestChanged()`
  finds the node stale and refetches the same bytes. The redundancy is F3's
  bookkeeping in `widget/src/tree.ts`. The shop cannot suppress either update
  without correlating or interpreting events, which D3 and D4 forbid, so this
  belongs to a framework cycle and is recorded in ADR 0013's consequences. The
  sprint's outcome still holds: only the changed artifact is fetched, and the
  untouched parts of the model are never requested.
- S2 opened 2026-08-03. Branch `sprint-003-floor-in-place-model-updates` and
  worktree `WTs/sprint-003-floor-in-place-model-updates` created from the shop
  `sprint-003` head `659f5fa`, which is also the shop content commit: the S1
  defect fix carried `floor/watcher.py`, ADR 0013 and a baseline spec, so the
  Content field above is corrected from `6817520` to `659f5fa`. Both recorded
  dependencies are satisfied: F3 `viewer-targeted-update` is integrated at
  framework `f34ddc6`, an ancestor of framework `sprint-003` head `582da89`,
  and S1 is integrated at `6817520`, an ancestor of `659f5fa`. The framework
  link `WTs/sprint-003/solid-node` resolves to the registered framework sprint
  worktree at `582da89`, whose widget package reports
  `solidNodeViewerApi: 2` — the interface this cycle consumes.
- S1 defect fixed 2026-08-03 on `sprint-003`. Review of the integrated S1 found
  the source handler dispatching on `on_any_event`, so inotify's `opened` and
  `closed_no_write` events from a build's own source reads triggered the next
  build, indefinitely. Measured live against framework `sprint-003` (`582da89`)
  with the real `solid build`: one edit produced 14 builds in 40 seconds before
  the fix and exactly 1 after, with no further build for the remaining 40
  seconds. The suite was blind to it because `tests/fixtures/fake_solid.py`
  never opened the project's sources; the fixture now reads them, and
  `test_a_build_reading_the_sources_does_not_trigger_another_build` is red
  without the fix. All 147 shop tests pass. ADR 0013 and the
  `functional-model-inspection` baseline spec record what the source handler
  listens for. Correcting the S1 record below: task 5.3's live check ran
  against installed `solid_node` (framework `main` @ `acf4292`), not the sprint
  worktree, and no SSE-level or external-build coverage was added to
  `tests/test_shop_lifecycle_e2e.py` under tasks 5.1 and 5.2.
- S1 integrated 2026-08-02 by fast-forwarding shop `sprint-003` from
  `30ac154` to `6817520`. Combined validation passed from `WTs/sprint-003`
  against linked framework content `582da89`: shop `pytest tests`,
  `tests/dev-env-test.sh`, and `openspec validate --all --strict` passed.
  The cycle remains in place until this evidence commit is verified.
- S1 opened 2026-08-02. Branch `sprint-003-floor-artifact-event-pipeline` and
  worktree `WTs/sprint-003-floor-artifact-event-pipeline` created from the shop
  `sprint-003` head `30ac154`, whose content commit is `7397c71`. Its recorded
  dependency on F2 is satisfied: framework `sprint-003` is at `582da89`. The
  ignored link `WTs/sprint-003-floor-artifact-event-pipeline/solid-node`
  resolves to the framework sprint worktree at that commit, so the cycle builds
  and tests against the framework content it depends on.
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
