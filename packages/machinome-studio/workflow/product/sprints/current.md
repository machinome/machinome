# SPRINT-002: One model viewer

## Goal

Every surface that shows a solid-node model — the shop floor, an exported
directory, the documentation, and the live development loop — renders it with
the same viewer, so an improvement to how models are seen is made once and
appears everywhere.

## Stories

- [ ] STORY-006 - See one model viewer everywhere
  - Source: `docs/product/stories/STORY-006-one-model-viewer.md`
  - Brief: `docs/product/sprints/SPRINT-002-brief.md` - findings, decisions with
    their rejected alternatives, the viewer interface consumers require, and the
    intent of every cycle. Read it before opening any cycle in this sprint.
  - Validation: `docs/product/sprints/SPRINT-002-validation.md` - binding
    cross-cycle proof matrix and final paired-validation procedure. Read it
    before proposing or implementing any cycle in this sprint.

## Ratified scope

- Included: one reusable viewer inside solid-node with the options its
  consumers need; one node-tree serializer behind both published documents;
  delivery of the built viewer inside the framework's Python distribution;
  the shop floor showing models through that viewer instead of its own; the
  development loop showing models through it as well.
- Excluded: publishing the viewer to a package registry; renaming the
  published export bundle, its auto-mount attribute, or its browser global;
  renaming either published document; making build publications portable and
  self-contained; viewer capabilities beyond parity and the options existing
  consumers require.

## Repositories

- `solid-node-shop`
  - Source: `main` @ `595eb00`
  - Sprint branch: `sprint-002`
  - Content: `f42cfe9`
  - Worktree: `WTs/sprint-002`
- `solid-node`
  - Source: `main` @ `6f8a5ae`
  - Sprint branch: `sprint-002`
  - Content: `6f8a5ae`
  - Worktree: `solid-node/WTs/sprint-002`
  - Shop link: `WTs/sprint-002/solid-node`

## Cycles

- `solid-node` / `unified-node-serializer`
  - Intent: one node-tree walk behind both published documents, converged
    additively; brief section 5 (F1)
  - Story: `STORY-006`
  - Requires: none
  - Branch: `sprint-002-unified-node-serializer` from `6f8a5ae`
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `viewer-bench-symlinks`
  - Intent: a framework bench can build any viewer package without installing
    inside a worktree; brief section 5 (S1)
  - Story: `STORY-006`
  - Requires: none
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node` / `viewer-package`
  - Intent: the single reusable viewer with the interface in brief section 4,
    consumed by export and Sphinx embedding; brief section 5 (F2)
  - Story: `STORY-006`
  - Requires: `solid-node` / `unified-node-serializer`, `solid-node-shop` / `viewer-bench-symlinks`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node` / `viewer-bundle-delivery`
  - Intent: the built viewer ships inside the Python distribution and a CLI
    accessor reports it; brief section 5 (F3)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-package`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `floor-uses-framework-viewer`
  - Intent: the shop floor shows models through the framework's viewer instead
    of its own copy; brief section 5 (S2)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-bundle-delivery`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node` / `dev-viewer-on-shared-package`
  - Intent: the development loop shows models through the same viewer and the
    last per-node walk retires; brief section 5 (F4)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-bundle-delivery`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `adjust-ignore-framework-link`
  - Story: none - sprint machinery
  - Requires: none
  - Branch: `sprint-002-adjust-ignore-framework-link` from `a0d74d3`
  - Commits: `f42cfe9`
  - Archive: not applicable - direct adjustment
  - Integrated: `sprint-002` @ `f42cfe9`

## Paired validation

- `python -m pytest tests/` (128 passed) and `bash tests/dev-env-test.sh`
  (all tests passed) passed from `WTs/sprint-002` after the rebase for shop
  content `f42cfe9` and framework content `6f8a5ae`.

## Decisions and scope changes

- 2026-08-01 - Stage the work as separate cycles rather than one change,
  because the development-loop viewer rests on a different architecture than
  the other two and carries the sprint's largest risk.
- 2026-08-01 - Include the development-loop viewer in this sprint; the goal is
  not met while one surface still carries its own implementation.
- 2026-08-01 - Unify the node-tree serializer behind both published documents
  and keep both document names, because the two names distinguish a portable
  directory from a build publication.
- 2026-08-01 - Keep the published export bundle name, auto-mount attribute,
  browser global, and current package directory unchanged. A package-directory
  rename may return during F2 only with a proven dependency-source/refresh path
  for framework benches and explicit pilot ratification.
- 2026-08-01 - Report an absent or incompatible viewer as one shop preparation
  failure rather than a degraded browser state, because no user exists today
  for whom the shop and the framework are versioned independently.
- 2026-08-01 - Do not publish the viewer to a package registry; deliver it
  inside the framework's Python distribution, deferring public release surface
  until an external consumer exists.
- 2026-08-01 - Correct the shop ignore rule so the framework sprint link is
  ignored as required, as a direct adjustment on the sprint branch: a commit on
  shop `main` would move it off the recorded base and prevent fast-forward
  integration when the sprint is archived.
- 2026-08-01 - Rebase shop `sprint-002` onto `main` @ `595eb00` before opening
  any feature cycle, incorporating the unrelated running-the-shop documentation
  change while histories are uncontested and preserving fast-forward archive
  integration.
- 2026-08-01 - Serialize the framework viewer build cycles as F2, then F3,
  then F4 by making F4 depend on F3. Their benches share heavy frontend
  directories through the shop's development environment, so the sprint graph,
  rather than transient orchestrator state, prevents overlapping writers.
- 2026-08-01 - Prove final distribution provenance from a disposable full
  checkout of the exact integrated framework content commit, outside every
  worktree; shared bench outputs remain development conveniences rather than
  release evidence.
- 2026-08-01 - Ratify `SPRINT-002-validation.md` as the binding cross-cycle
  proof matrix before opening F1 or S1.
- 2026-08-01 - Reconcile F1 proposal review by retaining document-level name
  parity, proving the real re-created-and-rebound child failure through both
  producers, recording schema identity versus portability in an ADR, accepting
  additive `mtime` churn, and assigning the shop API/watcher consequences to S2.
- 2026-08-01 - Preserve npm-less Python benches while making viewer benches
  explicit through `scripts/dev-env <name> setup --frontend`. Frontend mode
  validates the selected base's declared top-level dependency requirements
  against the primary installed tree rather than requiring whole-lockfile
  equality, creates and links missing generated-output roots, verifies only
  exact managed links as cleanliness exceptions, and rolls back failed setup.
  F2, F3, and F4 use frontend mode; ports and the six-field manifest remain
  unchanged.

## Outcome

Completed when the sprint is archived.
